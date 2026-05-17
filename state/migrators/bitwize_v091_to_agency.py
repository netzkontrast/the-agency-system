import argparse
import datetime
import json
import os
import shutil
import sys
from pathlib import Path

# Adjust path to find _hashing and _atomic
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from state.migrators._hashing import sha256_of_files
from state.migrators._atomic import atomic_write_json

try:
    import yaml
except ImportError:
    yaml = None


def merge_config(bitwize_config: dict, repo_root: Path = None) -> dict:
    """Merges bitwize config into the unified config shape per spec 018 references."""
    if repo_root is None:
        repo_root = Path(__file__).resolve().parent.parent.parent

    template_path = repo_root / "config" / "agency-system.config.template.yaml"

    if template_path.is_file() and yaml:
        try:
            with template_path.open("r", encoding="utf-8") as f:
                unified = yaml.safe_load(f)
        except Exception:
            unified = {"version": "1.0.0", "novel": {}, "jules": {}, "agentic": {}, "shared": {}}
    else:
        # Fallback if we cannot load the template or yaml is missing
        unified = {
            "version": "1.0.0",
            "novel": {},
            "jules": {},
            "agentic": {},
            "shared": {}
        }

    # Preserve verbatim under music:
    if "music" not in unified:
        unified["music"] = {}

    for k, v in bitwize_config.items():
        unified["music"][k] = v

    return unified


def main(args_list=None):
    parser = argparse.ArgumentParser(description="Migrate bitwize-music state to agency-system state.")
    parser.add_argument("--dry-run", action="store_true", help="Report what would happen without writing.")
    parser.add_argument("--source-dir", default=str(Path.home() / ".bitwize-music"), help="Source directory.")
    parser.add_argument("--dest-dir", default=str(Path.home() / ".agency-system"), help="Destination directory.")
    parser.add_argument("--no-backup", action="store_true", help="Skip backup creation.")
    # Allow overriding repo_root for tests
    parser.add_argument("--repo-root", default=None, help=argparse.SUPPRESS)

    args = parser.parse_args(args_list)

    source_dir = Path(args.source_dir)
    dest_dir = Path(args.dest_dir)
    repo_root = Path(args.repo_root) if args.repo_root else None

    source_state_file = source_dir / "cache" / "state.json"
    source_config_file = source_dir / "config.yaml"

    has_state = source_state_file.exists()
    has_config = source_config_file.exists()

    if not has_state and not has_config:
        print(json.dumps({"would_migrate": 0, "would_skip": 0, "input_hash": None, "reason": "no bitwize state found"}))
        return 0

    files_to_hash = []
    if has_state:
        files_to_hash.append(source_state_file)
    if has_config:
        files_to_hash.append(source_config_file)

    input_hash = sha256_of_files(files_to_hash)

    dest_state_file = dest_dir / "cache" / "state.json"
    dest_config_file = dest_dir / "config.yaml"

    if dest_state_file.exists():
        try:
            with dest_state_file.open("r", encoding="utf-8") as f:
                dest_data = json.load(f)
            existing_hash = dest_data.get("_migration", {}).get("input_hash")
            if existing_hash == input_hash:
                print(json.dumps({"reason": "already migrated", "input_hash": input_hash}))
                return 0
        except Exception:
            pass

    # Read Source State
    bitwize_state = {}
    if has_state:
        try:
            with source_state_file.open("r", encoding="utf-8") as f:
                bitwize_state = json.load(f)
        except Exception as e:
            sys.stderr.write(json.dumps({"error": "read", "msg": str(e)}) + "\n")
            return 2

        if not isinstance(bitwize_state, dict):
            sys.stderr.write(json.dumps({"error": "schema", "msg": "source state is not a JSON object"}) + "\n")
            return 2

    # Read Source Config
    bitwize_config = {}
    if has_config and yaml:
        try:
            with source_config_file.open("r", encoding="utf-8") as f:
                bitwize_config = yaml.safe_load(f) or {}
        except Exception as e:
            sys.stderr.write(json.dumps({"error": "read", "msg": str(e)}) + "\n")
            return 2

    artists_count = 0
    if "albums" in bitwize_state:
        for _ in bitwize_state["albums"]:
            artists_count += 1

    if args.dry_run:
        print(json.dumps({"would_migrate": artists_count, "would_skip": 0, "input_hash": input_hash}))
        return 0

    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

    # Backup
    if not args.no_backup:
        backup_dir = dest_dir / "backup" / now_iso
        backup_dir.mkdir(parents=True, exist_ok=True)
        if has_state:
            shutil.copy2(source_state_file, backup_dir / "bitwize-state.json")
        if has_config:
            shutil.copy2(source_config_file, backup_dir / "bitwize-config.yaml")

    # Unified Payload
    unified_state = {
        "music": bitwize_state,
        "novel": {},
        "jules": {},
        "agentic": {},
        "_version": "1.0.0",
        "_migration": {
            "input_hash": input_hash,
            "from": "bitwize-music v0.91.0",
            "at": now_iso
        }
    }

    # Atomic write state
    try:
        atomic_write_json(dest_state_file, unified_state)
    except Exception as e:
        sys.stderr.write(json.dumps({"error": "write", "msg": str(e)}) + "\n")
        return 2

    # Atomic write config
    unified_config = merge_config(bitwize_config, repo_root)

    if yaml:
        dest_config_file.parent.mkdir(parents=True, exist_ok=True)
        import tempfile
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(dir=dest_config_file.parent, delete=False, suffix='.tmp', mode='w', encoding='utf-8') as f:
                tmp_path = Path(f.name)
                yaml.safe_dump(unified_config, f, default_flow_style=False, sort_keys=False)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_path, dest_config_file)
        except Exception as e:
            if tmp_path and tmp_path.exists():
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass
            sys.stderr.write(json.dumps({"error": "write", "msg": str(e)}) + "\n")
            return 2

    # Write DEPRECATED.md
    dep_md = source_dir / "DEPRECATED.md"
    backup_path = dest_dir / "backup" / now_iso
    dep_md.write_text(
        f"# Deprecated\nMigrated at {now_iso}.\nNew state is at {dest_dir}.\nBackups at {backup_path}.\n",
        encoding="utf-8"
    )

    print(json.dumps({"artefacts_written": 2, "input_hash": input_hash}))
    return 0

if __name__ == "__main__":
    sys.exit(main())
