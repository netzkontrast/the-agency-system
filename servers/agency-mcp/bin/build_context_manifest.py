import argparse
import sys
import os
import json
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agency_mcp.lib.codemode.context_indexer import extract_summary, extract_views, infer_tags, compute_sha256

def derive_id(rel_path: str) -> str:
    path = Path(rel_path)
    # Strip ext
    if path.suffix in ('.md', '.json', '.yaml', '.yml'):
        p_str = str(path.with_suffix(''))
    else:
        p_str = str(path)

    # Replace / with :
    res = p_str.replace(os.sep, ':').replace('/', ':').lower()

    import re
    res = re.sub(r"[^a-z0-9_\-:/]", "-", res)
    return res

def main():
    parser = argparse.ArgumentParser(description="Build Context Mode Manifest")
    parser.add_argument("--root", default=".", help="Repo root directory")
    parser.add_argument("--out", default="servers/agency-mcp/src/agency_mcp/codemode/context_manifest.json", help="Output file")
    parser.add_argument("--check", action="store_true", help="Check mode: compare on-disk vs fresh crawl")
    parser.add_argument("--no-include-vendor", action="store_true", help="Exclude vendor docs")

    from datetime import timezone
    args = parser.parse_args()

    root_path = Path(args.root).resolve()
    vendor_dir = Path.home() / "work" / "vendor"

    # Define directories to crawl and their allowed extensions
    # Fix 5
    CRAWL_CONFIG = {
        "Plan": {".md"},
        "overrides": {".md", ".yaml"},
        "reference": {".md", ".json"},
        "docs": {".md"},
        "genres": {".md"}
    }

    crawl_dirs = list(CRAWL_CONFIG.keys())

    if not args.no_include_vendor:
        sources_file = root_path / "Plan" / "SOURCES.md"
        vendor_targets = []
        if sources_file.exists():
            import re
            sources_content = sources_file.read_text()
            # Extract vendor repos from e.g. ~/work/vendor/bitwize-music
            for match in re.finditer(r"~/work/vendor/([a-zA-Z0-9_\-]+)", sources_content):
                vendor_targets.append(match.group(1))

        if vendor_targets and vendor_dir.exists():
             for target in vendor_targets:
                 target_dir = vendor_dir / target
                 if target_dir.exists():
                     crawl_dirs.append(str(target_dir))
                     CRAWL_CONFIG[str(target_dir)] = {".md"}

    entries = []
    seen_ids = set()

    for crawl_dir in crawl_dirs:
        dir_path = root_path / crawl_dir
        if dir_path.is_absolute():
             base_search = dir_path
        else:
             base_search = dir_path

        if not base_search.exists():
            continue

        allowed_exts = CRAWL_CONFIG.get(crawl_dir, {".md", ".json", ".yaml", ".yml"})

        for path in base_search.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix not in allowed_exts:
                continue

            # Fix 2: relative path helper
            try:
                rel_path = str(path.relative_to(root_path))
            except ValueError:
                try:
                    rel_path = "vendor/" + str(path.relative_to(vendor_dir))
                except ValueError:
                    print(f"Warning: File {path} is outside both root and vendor. Skipping.", file=sys.stderr)
                    continue

            id_str = derive_id(rel_path)
            if id_str in seen_ids:
                print(f"Error: Duplicate ID '{id_str}' for file '{rel_path}'", file=sys.stderr)
                sys.exit(1)
            seen_ids.add(id_str)

            body_bytes = path.read_bytes()
            body_str = body_bytes.decode('utf-8', errors='ignore')

            summary = extract_summary(str(path), body_str)
            tags = infer_tags(str(path), body_str)

            # Simple title extraction
            title = os.path.basename(path)
            if path.suffix == '.md':
                for line in body_str.splitlines():
                    if line.startswith("# "):
                        title = line[2:].strip()
                        break
            elif path.suffix in ('.json', '.yaml', '.yml'):
                try:
                    import yaml
                    data = yaml.safe_load(body_str)
                    if isinstance(data, dict) and 'title' in data:
                        title = data['title']
                except:
                    pass

            # Mime type
            mime_map = {'.md': 'text/markdown', '.json': 'application/json', '.yaml': 'text/yaml', '.yml': 'text/yaml'}
            mime = mime_map.get(path.suffix, 'text/plain')

            # Fix 6: Timezone
            mtime = path.stat().st_mtime
            iso_time = datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat().replace("+00:00", "Z")

            entry = {
                "id": id_str,
                "title": title[:120],
                "summary": summary,
                "tags": tags,
                "path": rel_path,
                "mime": mime,
                "size_bytes": len(body_bytes),
                "last_modified": iso_time,
                "sha256": compute_sha256(body_bytes),
                "views": extract_views(str(path), body_bytes)
            }
            entries.append(entry)

    # Sort entries by ID
    entries.sort(key=lambda x: x['id'])

    manifest_data = {"entries": entries}

    if args.check:
        out_path = Path(args.out)
        if not out_path.exists():
            print(f"Check mode failed: output file {out_path} does not exist.", file=sys.stderr)
            sys.exit(1)

        with open(out_path, "r") as f:
            old_data = json.load(f)

        old_entries = {e['id']: e for e in old_data.get('entries', [])}
        new_entries = {e['id']: e for e in entries}

        drift = False

        old_keys = set(old_entries.keys())
        new_keys = set(new_entries.keys())

        if old_keys != new_keys:
            print("Check mode failed: keys drift detected.", file=sys.stderr)
            added = new_keys - old_keys
            missing = old_keys - new_keys
            if added: print(f"Added IDs: {added}", file=sys.stderr)
            if missing: print(f"Missing IDs: {missing}", file=sys.stderr)
            drift = True

        for id_str, new_entry in new_entries.items():
            if id_str not in old_entries:
                continue
            old_entry = old_entries[id_str]
            for field in ['sha256', 'size_bytes', 'last_modified']:
                if str(old_entry[field]) != str(new_entry[field]):
                    print(f"Check mode failed: drift detected in {new_entry['path']} for field {field}", file=sys.stderr)
                    print(f"Expected: {old_entry[field]}, Actual: {new_entry[field]}", file=sys.stderr)
                    drift = True

        if drift:
            sys.exit(1)

        print("Check mode: ok")
        sys.exit(0)

    else:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w") as f:
            json.dump(manifest_data, f, indent=2, sort_keys=True)
            f.write("\n")
        print(f"Built manifest with {len(entries)} entries at {out_path}")

if __name__ == "__main__":
    main()
