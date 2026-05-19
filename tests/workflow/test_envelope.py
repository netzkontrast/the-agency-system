import pytest
import os
import time
from pathlib import Path
from workflow._runner import persist, hydrate
from workflow._runner.envelope import sweep_ttl

def test_blocked_envelope_serializes_and_resumes(monkeypatch):
    # Setup mock env
    env = {
        "status": "blocked_on_user",
        "phase_id": "02",
        "row": "music",
        "session_id": "test-session-123",
        "opaque_state": {"k": "v"},
        "tool_result": {"ok": True, "data": {}, "warnings": [], "next_suggested_tools": []},
        "blocked_reason": "needs auth",
        "resume_token": "token1"
    }

    # redirect to tmp state dir
    def mock_get_state_dir(session_id):
        return Path(f"workflow/_test_state/{session_id}")
    import workflow._runner.envelope as env_mod
    monkeypatch.setattr(env_mod, "get_state_dir", mock_get_state_dir)

    # Write
    path = persist(env)
    assert path.exists()
    assert str(path).endswith("02.json")

    # Hydrate
    restored = hydrate("test-session-123", "02")
    assert restored["status"] == "blocked_on_user"
    assert restored["opaque_state"] == {"k": "v"}

    # Clean up
    if path.exists():
        path.unlink()
    try:
        path.parent.rmdir()
    except:
        pass

def test_ttl_sweep(tmp_path, monkeypatch):
    import workflow._runner.envelope as env_mod

    # We patch Path("workflow") / "_state" to point to our tmp_path
    monkeypatch.setattr(env_mod, "Path", lambda *args: tmp_path if args and args[0] == "workflow" else Path(*args))

    state_dir = tmp_path / "_state" / "test-ttl"
    state_dir.mkdir(parents=True)

    env_file = state_dir / "01.json"
    env_file.write_text("{}")

    # Modify mtime to be 31 days old
    old_time = time.time() - (31 * 24 * 60 * 60)
    os.utime(env_file, (old_time, old_time))

    # Also create a dummy README
    readme = tmp_path / "_state" / "README.md"
    readme.write_text("layout info")

    env_mod.sweep_ttl()

    assert not env_file.exists()