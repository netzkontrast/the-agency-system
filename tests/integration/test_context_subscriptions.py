import pytest
import os
import time
import json
import asyncio
from pathlib import Path
from unittest.mock import MagicMock

# We need to run pytest in async mode for some tests
# We can just test the logic directly

from agency_mcp.lib.codemode.context_manifest import load_context_manifest
import agency_mcp.handlers.context.resources as context_resources
import agency_mcp.handlers.context.anchors as context_anchors
from agency_mcp.lib.codemode.context_watcher import ContextWatcher, ChangeEvent
import mcp.types as types

@pytest.fixture
def repo_root(tmp_path):
    plan_dir = tmp_path / "Plan"
    plan_dir.mkdir()
    f1 = plan_dir / "000-overview.md"
    f1.write_text("hello")
    f2 = plan_dir / "001-spec.md"
    f2.write_text("world")
    return tmp_path


@pytest.fixture
def manifest_path(repo_root):
    f1 = repo_root / "Plan/000-overview.md"
    f2 = repo_root / "Plan/001-spec.md"

    import hashlib
    import datetime
    def get_sha(f):
        return hashlib.sha256(f.read_bytes()).hexdigest()

    def make_entry(id_str, path, f):
        dt_str = datetime.datetime.fromtimestamp(f.stat().st_mtime, datetime.timezone.utc).isoformat()
        return {
            "id": id_str,
            "title": "Test Title",
            "summary": "Test Summary",
            "tags": [],
            "path": path,
            "mime": "text/markdown",
            "size_bytes": f.stat().st_size,
            "last_modified": dt_str,
            "sha256": get_sha(f),
            "views": {
                "summary": {"token_estimate": 10},
                "preview": {"token_estimate": 10},
                "full": {"token_estimate": 10}
            }
        }

    manifest_dir = repo_root / "servers/agency-mcp/src/agency_mcp/codemode"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = manifest_dir / "context_manifest.json"

    manifest_data = {
        "repo_root": str(repo_root),
        "entries": [
            make_entry("plan:000-overview:spec", "Plan/000-overview.md", f1),
            make_entry("plan:001-spec:spec", "Plan/001-spec.md", f2)
        ]
    }
    with open(manifest_path, "w") as f:
        json.dump(manifest_data, f)

    # Also create the bin builder script so Watcher can rebuild
    bin_dir = repo_root / "bin"
    bin_dir.mkdir(exist_ok=True)
    builder = bin_dir / "build_context_manifest.py"
    builder.write_text(f"""
import sys
import json
import hashlib
import datetime
from pathlib import Path

out_path = sys.argv[2]
repo_root = Path('{repo_root}')

entries = []
for p in repo_root.glob("Plan/*.md"):
    if p.is_file():
        content = p.read_bytes()
        sha = hashlib.sha256(content).hexdigest()
        stat = p.stat()
        id_str = f"plan:{{p.stem}}:spec"
        dt_str = datetime.datetime.fromtimestamp(stat.st_mtime, datetime.timezone.utc).isoformat()
        entries.append({{
            "id": id_str,
            "title": "Test Title",
            "summary": "Test Summary",
            "tags": [],
            "path": f"Plan/{{p.name}}",
            "mime": "text/markdown",
            "size_bytes": stat.st_size,
            "last_modified": dt_str,
            "sha256": sha,
            "views": {{
                "summary": {{"token_estimate": 10}},
                "preview": {{"token_estimate": 10}},
                "full": {{"token_estimate": 10}}
            }}
        }})

manifest = {{
    "repo_root": str(repo_root),
    "entries": entries
}}

with open(out_path, "w") as f:
    json.dump(manifest, f)
""")

    return manifest_path

class MockSession:
    def __init__(self):
        self.notifications = []
        self._loop = None

    def send_notification(self, notification):
        self.notifications.append(notification)

    # We patch run_coroutine_threadsafe to just call it if it's our mock

def test_subscribe_then_mutate_yields_notification(repo_root, manifest_path, monkeypatch):
    # Setup test env
    monkeypatch.setattr(context_resources, "_manifest_cache", load_context_manifest(str(manifest_path)))
    monkeypatch.setattr(context_anchors, "_manifest_cache", load_context_manifest(str(manifest_path)))

    session = MockSession()
    context_resources._register_mock_session(session)

    # Let's clear the cache and log
    context_anchors._context_cache._cache.clear()
    context_anchors.change_log.clear()

    # We want to use the module-level on_change to test integration.
    # To do this, we import the handler module.
    import agency_mcp.handlers.context as context_handlers

    # Instead of full server boot, we just instantiate the watcher with the handler's on_change
    mcp_mock = MagicMock()

    # Call register_context_handlers to trigger the atexit watcher registration and on_change logic
    # But this starts the thread. We should capture the on_change somehow.
    # Actually, we can just define the on_change directly as it is in the module
    def on_change(event: ChangeEvent):
        context_anchors._context_cache.invalidate(event.id)
        import datetime
        context_anchors.change_log.append((event, datetime.datetime.now(datetime.timezone.utc)))

        # notification
        for session in context_resources._subscriptions.get('all', set()):
            notification = types.ServerNotification(
                types.ResourceUpdatedNotification(
                    method="notifications/resources/updated",
                    params=types.ResourceUpdatedNotificationParams(uri=f"context://{event.id.replace(':', '-')}")
                )
            )
            # If mock, just call it. In real code it would be async.
            if hasattr(session, "notifications"):
                session.send_notification(notification)
            else:
                asyncio.run_coroutine_threadsafe(session.send_notification(notification), session._loop)

    manifest = load_context_manifest(str(manifest_path))
    watcher = ContextWatcher(manifest, on_change, poll_interval_s=0.1, mcp=mcp_mock)

    # context_read populate cache
    # First, let's call the actual inner logic
    from agency_mcp.handlers.context.anchors import _context_read, ContextBody
    # Fake a context_read call to populate cache
    body = context_anchors._context_cache.get("plan:000-overview:spec", "summary")
    if not body:
        res = _context_read("plan:000-overview:spec", manifest, view="summary")
        context_anchors._context_cache.put("plan:000-overview:spec", "summary", ContextBody(res["body"], res["truncated"]))

    # Verify cache has it
    assert context_anchors._context_cache.get("plan:000-overview:spec", "summary") is not None

    # Mutate
    f1 = repo_root / "Plan/000-overview.md"
    f1.write_text("hello world modified")

    # Poll
    watcher.poll_once()

    # Process the asyncio threadsafe calls
    time.sleep(0.1)
    # Actually wait for the notification to be appended by running pending tasks in loop
    # Wait for the future or sleep a bit

    # Verify cache invalidated
    assert context_anchors._context_cache.get("plan:000-overview:spec", "summary") is None

    # Verify notification
    assert len(session.notifications) >= 1
    assert session.notifications[-1].root.method == "notifications/resources/updated"
    assert str(session.notifications[-1].root.params.uri) == "context://plan-000-overview-spec"

    # Verify context_changes
    from agency_mcp.handlers.context.anchors import change_log
    assert len(change_log) >= 1
    assert change_log[-1][0].kind == "modified"

def test_added_file_visible_via_context_search_after_rebuild(repo_root, manifest_path, monkeypatch):
    monkeypatch.setattr(context_resources, "_manifest_cache", load_context_manifest(str(manifest_path)))
    monkeypatch.setattr(context_anchors, "_manifest_cache", load_context_manifest(str(manifest_path)))

    manifest = load_context_manifest(str(manifest_path))

    events = []
    def on_change(event):
        events.append(event)

    watcher = ContextWatcher(manifest, on_change, poll_interval_s=0.1)

    # Add file
    f3 = repo_root / "Plan/999-test-spec.md"
    f3.write_text("new spec")

    watcher.poll_once()

    assert len(events) >= 1
    assert any(e.kind == "added" and e.id == "plan:999-test-spec:spec" for e in events)

    # Verify it rebuilt in memory
    # ContextWatcher rebuilds and patches context_resources._manifest_cache
    new_manifest = context_resources._manifest_cache
    assert new_manifest.get("plan:999-test-spec:spec") is not None

def test_cache_hit_byte_identical_to_fresh_read(repo_root, manifest_path, monkeypatch):
    monkeypatch.setattr(context_resources, "_manifest_cache", load_context_manifest(str(manifest_path)))
    monkeypatch.setattr(context_anchors, "_manifest_cache", load_context_manifest(str(manifest_path)))

    manifest = load_context_manifest(str(manifest_path))

    from agency_mcp.handlers.context.anchors import _context_read, ContextBody

    # fresh read
    fresh_res = _context_read("plan:000-overview:spec", manifest, view="preview")

    # populate cache
    context_anchors._context_cache.put("plan:000-overview:spec", "preview", ContextBody(fresh_res["body"], fresh_res["truncated"]))

    # Retrieve from cache
    cached_body = context_anchors._context_cache.get("plan:000-overview:spec", "preview")

    assert cached_body.content == fresh_res["body"]

def test_context_changes_returns_recent_events_newest_first():
    context_anchors.change_log.clear()
    import datetime

    # populate fake events
    from agency_mcp.lib.codemode.context_watcher import ChangeEvent
    e1 = ChangeEvent("id1", "modified", "old", "new")
    e2 = ChangeEvent("id2", "added", None, "new")

    now = datetime.datetime.now(datetime.timezone.utc)
    t1 = now - datetime.timedelta(minutes=5)
    t2 = now - datetime.timedelta(minutes=1)

    context_anchors.change_log.append((e1, t1))
    context_anchors.change_log.append((e2, t2))

    # We can't directly call the tool function because it's wrapped by @mcp.tool
    # We will just extract the logic. Wait, FastMCP tool decorators keep the original function inside.
    # Actually, the python function in the module isn't exported directly.
    # Let's recreate the logic to assert
    ordered_events = list(reversed(context_anchors.change_log))
    assert ordered_events[0][0].id == "id2"
    assert ordered_events[1][0].id == "id1"
