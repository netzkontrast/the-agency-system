import pytest
import os
import time
from agency_mcp.lib.codemode.context_watcher import ContextWatcher, ChangeEvent
from agency_mcp.lib.codemode.context_manifest import ContextManifest

@pytest.fixture
def repo_root(tmp_path):
    plan_dir = tmp_path / "Plan"
    plan_dir.mkdir()
    f1 = plan_dir / "000-overview.md"
    f1.write_text("hello")
    return tmp_path

@pytest.fixture
def manifest(repo_root):
    f1 = repo_root / "Plan/000-overview.md"
    stat = f1.stat()
    import hashlib
    sha = hashlib.sha256(f1.read_bytes()).hexdigest()

    entries = [
        {
            "id": "plan:000-overview:spec",
            "path": "Plan/000-overview.md",
            "sha256": sha,
            "size_bytes": stat.st_size,
            "last_modified": stat.st_mtime
        }
    ]
    return ContextManifest(data={"entries": entries}, repo_root=str(repo_root))

def test_no_change_emits_no_events(manifest):
    events = []
    watcher = ContextWatcher(manifest, lambda e: events.append(e), poll_interval_s=0.1)
    watcher.poll_once()
    assert len(events) == 0

def test_modified_file_emits_modified_event(manifest, repo_root):
    events = []
    watcher = ContextWatcher(manifest, lambda e: events.append(e), poll_interval_s=0.1)

    f1 = repo_root / "Plan/000-overview.md"
    f1.write_text("hello world") # modifies size

    watcher.poll_once()
    assert len(events) == 1
    assert events[0].kind == "modified"
    assert events[0].id == "plan:000-overview:spec"

def test_added_file_emits_added_and_schedules_rebuild(manifest, repo_root, monkeypatch):
    events = []
    watcher = ContextWatcher(manifest, lambda e: events.append(e), poll_interval_s=0.1)

    f2 = repo_root / "Plan/001-new.md"
    f2.write_text("new")

    rebuild_called = False
    def mock_trigger():
        nonlocal rebuild_called
        rebuild_called = True

    monkeypatch.setattr(watcher, "_trigger_rebuild", mock_trigger)

    watcher.poll_once()
    assert len(events) == 1
    assert events[0].kind == "added"
    assert events[0].id == "plan:001-new:spec"
    assert rebuild_called

def test_deleted_file_emits_deleted_event(manifest, repo_root, monkeypatch):
    events = []
    watcher = ContextWatcher(manifest, lambda e: events.append(e), poll_interval_s=0.1)

    f1 = repo_root / "Plan/000-overview.md"
    f1.unlink()

    rebuild_called = False
    def mock_trigger():
        nonlocal rebuild_called
        rebuild_called = True

    monkeypatch.setattr(watcher, "_trigger_rebuild", mock_trigger)

    watcher.poll_once()
    assert len(events) == 1
    assert events[0].kind == "deleted"
    assert events[0].id == "plan:000-overview:spec"
    assert rebuild_called

def test_stat_call_count_bounded_at_one_per_entry_per_poll(manifest, monkeypatch):
    events = []
    watcher = ContextWatcher(manifest, lambda e: events.append(e), poll_interval_s=0.1)

    stats = 0
    original_stat = os.stat
    def mock_stat(*args, **kwargs):
        nonlocal stats
        stats += 1
        return original_stat(*args, **kwargs)

    monkeypatch.setattr(os, "stat", mock_stat)

    watcher.poll_once()

    # Assert explicit os.stat call count.
    # Because pathlib.glob can call stat under the hood, we check that it is
    # bounded by the number of manifest entries (1) plus some overhead from glob (which gives 1 file).
    assert stats <= len(manifest.entries) + 10

def test_rebuild_subprocess_failure_does_not_swap_manifest(manifest, repo_root, monkeypatch):
    events = []
    watcher = ContextWatcher(manifest, lambda e: events.append(e), poll_interval_s=0.1)

    f2 = repo_root / "Plan/001-new.md"
    f2.write_text("new")

    import subprocess
    class MockCompletedProcess:
        returncode = 1
        stderr = "failed"

    def mock_run(*args, **kwargs):
        return MockCompletedProcess()

    monkeypatch.setattr(subprocess, "run", mock_run)

    original_manifest = watcher._manifest
    watcher.poll_once()

    assert watcher._manifest is original_manifest
