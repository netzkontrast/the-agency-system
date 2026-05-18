import json
import os
import shutil
import subprocess
from pathlib import Path
from unittest import mock

import pytest
import yaml

MIGRATOR_SCRIPT = Path("state/migrators/bitwize_v091_to_agency.py").resolve()

def setup_bitwize_source(tmp_path: Path, valid: bool = True) -> Path:
    source_dir = tmp_path / "source"
    source_dir.mkdir(parents=True)

    cache_dir = source_dir / "cache"
    cache_dir.mkdir(parents=True)
    state_file = cache_dir / "state.json"

    config_file = source_dir / "config.yaml"
    config_file.write_text("content:\n  root: '/tmp'\n  artist: 'Test'", encoding="utf-8")

    if valid:
        state_file.write_text(json.dumps({
            "albums": {"Test": {"album1": {"slug": "album1"}, "album2": {"slug": "album2"}, "album3": {"slug": "album3"}}}
        }), encoding="utf-8")
    else:
        # Invalid schema (top-level list)
        state_file.write_text("[]", encoding="utf-8")

    return source_dir

def run_migrator(source_dir: Path, dest_dir: Path, *args: str) -> subprocess.CompletedProcess:
    cmd = ["python", str(MIGRATOR_SCRIPT), "--source-dir", str(source_dir), "--dest-dir", str(dest_dir)] + list(args)
    return subprocess.run(cmd, capture_output=True, text=True)

def test_dry_run_writes_nothing(tmp_path: Path) -> None:
    source_dir = setup_bitwize_source(tmp_path)
    dest_dir = tmp_path / "dest"

    res = run_migrator(source_dir, dest_dir, "--dry-run")
    assert res.returncode == 0
    assert "would_migrate" in res.stdout
    assert "input_hash" in res.stdout

    assert not dest_dir.exists() or not any(dest_dir.iterdir())

def test_real_run_migrates_payload(tmp_path: Path) -> None:
    source_dir = setup_bitwize_source(tmp_path)
    dest_dir = tmp_path / "dest"

    res = run_migrator(source_dir, dest_dir, "--no-backup")
    assert res.returncode == 0

    dest_state = dest_dir / "cache" / "state.json"
    assert dest_state.exists()

    data = json.loads(dest_state.read_text(encoding="utf-8"))
    assert "music" in data
    assert "albums" in data["music"]
    assert "Test" in data["music"]["albums"]
    assert len(data["music"]["albums"]["Test"]) == 3
    assert data["_version"] == "1.0.0"
    assert "novel" in data
    assert "jules" in data
    assert "agentic" in data

def test_backup_snapshot_created(tmp_path: Path) -> None:
    source_dir = setup_bitwize_source(tmp_path)
    dest_dir = tmp_path / "dest"

    res = run_migrator(source_dir, dest_dir)
    assert res.returncode == 0

    backup_base = dest_dir / "backup"
    assert backup_base.exists()
    backup_dirs = list(backup_base.iterdir())
    assert len(backup_dirs) == 1

    backup_dir = backup_dirs[0]
    assert (backup_dir / "bitwize-state.json").exists()
    assert (backup_dir / "bitwize-config.yaml").exists()

    original_state = source_dir / "cache" / "state.json"
    backup_state = backup_dir / "bitwize-state.json"
    assert original_state.read_bytes() == backup_state.read_bytes()

def test_atomic_rename_no_torn_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    source_dir = setup_bitwize_source(tmp_path)
    dest_dir = tmp_path / "dest"

    # Run once to set up destination
    res = run_migrator(source_dir, dest_dir, "--no-backup")
    assert res.returncode == 0
    dest_state = dest_dir / "cache" / "state.json"
    original_bytes = dest_state.read_bytes()

    import sys
    # Provide an isolated environment for the test using subprocess instead of loading the module and monkeypatching os.replace directly
    # Wait, the test uses monkeypatch to mock `os.replace`. To do that we have to load it.
    import subprocess
    import importlib.util

    # Since state.migrators is not a package (no __init__.py), let's ensure its parent is in sys.path
    _repo_root = str(MIGRATOR_SCRIPT.parent.parent.parent)
    if _repo_root not in sys.path:
        sys.path.insert(0, _repo_root)

    # Let's write a small script and run it to avoid import issues
    # First, modify the source so it thinks it needs to run
    (source_dir / "cache" / "state.json").write_text('{"albums": {"New": {}}}')

    test_script_content = f"""
import sys
import os
from pathlib import Path
sys.path.insert(0, '{_repo_root}')

import state.migrators.bitwize_v091_to_agency as migrator

def mock_replace(src, dst):
    raise OSError("Simulated crash during replace")

os.replace = mock_replace

sys.exit(migrator.main(["--source-dir", "{source_dir}", "--dest-dir", "{dest_dir}", "--no-backup"]))
"""
    test_script_path = dest_dir / "crash_script.py"
    test_script_path.write_text(test_script_content)

    ret = subprocess.run([sys.executable, str(test_script_path)], capture_output=True)
    assert ret.returncode == 2

    assert dest_state.read_bytes() == original_bytes
    assert len(list((dest_dir / "cache").glob("*.tmp"))) == 0

def test_idempotency_second_run_noop(tmp_path: Path) -> None:
    source_dir = setup_bitwize_source(tmp_path)
    dest_dir = tmp_path / "dest"

    res1 = run_migrator(source_dir, dest_dir)
    assert res1.returncode == 0

    dest_state = dest_dir / "cache" / "state.json"
    original_bytes = dest_state.read_bytes()

    res2 = run_migrator(source_dir, dest_dir)
    assert res2.returncode == 0
    assert "already migrated" in res2.stdout

    assert dest_state.read_bytes() == original_bytes

def test_deprecation_marker_written(tmp_path: Path) -> None:
    source_dir = setup_bitwize_source(tmp_path)
    dest_dir = tmp_path / "dest"

    res = run_migrator(source_dir, dest_dir, "--no-backup")
    assert res.returncode == 0

    assert (source_dir / "DEPRECATED.md").exists()

def test_schema_mismatch_exits_nonzero(tmp_path: Path) -> None:
    source_dir = setup_bitwize_source(tmp_path, valid=False)
    dest_dir = tmp_path / "dest"

    res = run_migrator(source_dir, dest_dir)
    assert res.returncode == 2
    assert '"error": "schema"' in res.stderr
    assert not dest_dir.exists() or not any(dest_dir.iterdir())

def test_no_bitwize_state_returns_clean(tmp_path: Path) -> None:
    source_dir = tmp_path / "empty"
    source_dir.mkdir()
    dest_dir = tmp_path / "dest"

    res = run_migrator(source_dir, dest_dir)
    assert res.returncode == 0
    assert "no bitwize state found" in res.stdout
    assert not dest_dir.exists() or not any(dest_dir.iterdir())

def test_config_seed_uses_empty_defaults_when_template_missing(tmp_path: Path) -> None:
    source_dir = setup_bitwize_source(tmp_path)
    dest_dir = tmp_path / "dest"

    # Passing an empty directory as repo_root to ensure no template is found
    empty_repo = tmp_path / "empty_repo"
    empty_repo.mkdir()

    res = run_migrator(source_dir, dest_dir, "--no-backup", "--repo-root", str(empty_repo))
    assert res.returncode == 0

    dest_config = dest_dir / "config.yaml"
    assert dest_config.exists()

    data = yaml.safe_load(dest_config.read_text(encoding="utf-8"))
    assert "novel" in data
    assert data["novel"] == {}
    assert "jules" in data
    assert data["jules"] == {}
    assert "agentic" in data
    assert data["agentic"] == {}
    assert "shared" in data
    assert data["shared"] == {}
    assert "music" in data
    assert "content" in data["music"]  # bitwize merged correctly

def test_config_seed_from_template_when_present(tmp_path: Path) -> None:
    source_dir = setup_bitwize_source(tmp_path)
    dest_dir = tmp_path / "dest"

    repo_root = tmp_path / "fake_repo"
    config_dir = repo_root / "config"
    config_dir.mkdir(parents=True)
    template_path = config_dir / "agency-system.config.template.yaml"

    template_path.write_text("""
version: "1.0.0"
novel:
  author: TestAuthor
jules:
  branch: fake/branch
agentic:
  flag: true
shared:
  cache: true
    """, encoding="utf-8")

    res = run_migrator(source_dir, dest_dir, "--no-backup", "--repo-root", str(repo_root))
    assert res.returncode == 0

    dest_config = dest_dir / "config.yaml"
    assert dest_config.exists()

    data = yaml.safe_load(dest_config.read_text(encoding="utf-8"))
    assert data["novel"]["author"] == "TestAuthor"
    assert data["jules"]["branch"] == "fake/branch"
    assert data["agentic"]["flag"] is True
    assert data["shared"]["cache"] is True
    assert "content" in data["music"] # bitwize merged correctly
