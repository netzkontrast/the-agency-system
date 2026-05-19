import pytest
from pathlib import Path
from workflow._runner import pipeline

def test_pipeline_start_and_yields_running_envelope():
    # Given workflow/meta/manifest.toml exists
    assert Path("workflow/meta/manifest.toml").exists()

    # When start is called with invalid new_row
    env = pipeline.start(row="meta", phase_id="01", inputs={"new_row": "Invalid-Row"})

    # Then blocked envelope is returned
    assert env["status"] == "blocked_on_user"
    assert env["phase_id"] == "01"
    assert env["row"] == "meta"

def test_expired_envelope_auto_deletes_on_boot(tmp_path, monkeypatch):
    import workflow._runner.envelope as env_mod

    # We patch Path("workflow") / "_state" to point to our tmp_path
    monkeypatch.setattr(env_mod, "Path", lambda *args: tmp_path if args and args[0] == "workflow" else Path(*args))

    state_dir = tmp_path / "_state" / "test-ttl"
    state_dir.mkdir(parents=True)

    env_file = state_dir / "01.json"
    env_file.write_text("{}")

    # Modify mtime to be 31 days old
    import time
    import os
    old_time = time.time() - (31 * 24 * 60 * 60)
    os.utime(env_file, (old_time, old_time))

    # We mock pipeline to use the patched env_mod
    monkeypatch.setattr(pipeline, "sweep_ttl", env_mod.sweep_ttl)

    pipeline.boot()

    assert not env_file.exists()