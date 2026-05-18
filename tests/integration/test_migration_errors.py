import json
import os
import shutil
import subprocess
from pathlib import Path
import pytest

MIGRATOR_SCRIPT = Path("state/migrators/bitwize_v091_to_agency.py").resolve()

def setup_bitwize_source(tmp_path: Path) -> Path:
    source_dir = tmp_path / "source"
    source_dir.mkdir(parents=True)
    cache_dir = source_dir / "cache"
    cache_dir.mkdir(parents=True)
    state_file = cache_dir / "state.json"
    config_file = source_dir / "config.yaml"
    config_file.write_text("content:\n  root: '/tmp'\n  artist: 'Test'", encoding="utf-8")
    state_file.write_text(json.dumps({
        "albums": {"Test": {"album1": {"slug": "album1"}}}
    }), encoding="utf-8")
    return source_dir

def run_migrator(source_dir: Path, dest_dir: Path, *args: str) -> subprocess.CompletedProcess:
    cmd = ["python", str(MIGRATOR_SCRIPT), "--source-dir", str(source_dir), "--dest-dir", str(dest_dir)] + list(args)
    return subprocess.run(cmd, capture_output=True, text=True)

def test_no_migration_key_in_state(tmp_path: Path) -> None:
    source_dir = setup_bitwize_source(tmp_path)
    dest_dir = tmp_path / "dest"

    res = run_migrator(source_dir, dest_dir, "--no-backup")
    assert res.returncode == 0

    dest_state = dest_dir / "cache" / "state.json"
    data = json.loads(dest_state.read_text(encoding="utf-8"))

    # Assert _migration is NOT in state.json
    assert "_migration" not in data, "_migration key should not be in state.json"

    # Assert it IS in .migration-receipt.json
    receipt = dest_dir / ".migration-receipt.json"
    assert receipt.exists(), ".migration-receipt.json should exist"

    receipt_data = json.loads(receipt.read_text(encoding="utf-8"))
    assert "input_hash" in receipt_data

def test_missing_pyyaml_raises_runtime_error(tmp_path: Path, monkeypatch) -> None:
    source_dir = setup_bitwize_source(tmp_path)
    dest_dir = tmp_path / "dest"

    # Mocking yaml as None via monkeypatch before calling main
    import sys
    sys.path.insert(0, str(MIGRATOR_SCRIPT.parent.parent.parent))
    from state.migrators.bitwize_v091_to_agency import main
    import state.migrators.bitwize_v091_to_agency as migrator_mod
    monkeypatch.setattr(migrator_mod, "yaml", None)

    with pytest.raises(RuntimeError, match="PyYAML required for config.yaml migration"):
        main(["--source-dir", str(source_dir), "--dest-dir", str(dest_dir), "--no-backup"])
