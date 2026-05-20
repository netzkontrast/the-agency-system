"""State-machine tests for the jules-row orchestration handlers.

Exercises the six orchestration verbs (dispatch, await_plan, monitor,
verify, recover, integrate) against an in-memory Store and a stubbed
``jules_mcp.server`` module, so the lifecycle can be driven without
touching the real Jules API.

What's covered:

* Happy path — DISPATCHED → IN_PROGRESS (plan approved) → COMPLETED
  → VERIFIED (clean landing) → terminal integrate.
* Silent-fail path — COMPLETED → SILENT_FAIL → PATCH_EXTRACTED → APPLIED.
* Illegal transitions surface ``SESSION_STATE_INVALID`` rather than
  silently corrupting the node.
* Missing JulesSession surfaces ``SESSION_NOT_FOUND``.
* API exceptions surface ``JULES_API_ERROR`` and stamp ``last_error``.
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest

import context
from context._store.sqlite import Store


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def store(monkeypatch, tmp_path):
    """Swap the process-singleton Store for an isolated tmp DB."""
    db_path = str(tmp_path / "ontology.db")
    s = Store(db_path=db_path)
    s.boot()
    monkeypatch.setattr(context, "_STORE", s, raising=False)
    yield s


class _FakeJulesAPI:
    """Stand-in for ``jules_mcp.server`` covering only the lifecycle calls
    the orchestration handlers use. Each call records its args + returns a
    canned response per a per-test script."""

    def __init__(self):
        self.calls = []
        self.resolve_source_response = {"source": "sources/abc123", "github": {"owner": "o", "repo": "r"}}
        self.create_response = {
            "id": "9876543210",
            "name": "sessions/9876543210",
            "state": "IN_PROGRESS",
            "title": "test session",
            "url": "https://jules.google.com/session/9876543210",
        }
        self.get_responses = []  # FIFO queue
        self.approve_response = {"ok": True, "session_id": "9876543210"}
        self.patch_summary_response = {
            "files": [],
            "lines_added": 0,
            "lines_removed": 0,
            "patch_bytes": 0,
            "base_commit": "",
            "suggested_commit_message": "",
        }
        self.patch_apply_response = {
            "applied": True,
            "dry_run": False,
            "files": ["a.py"],
            "lines_added": 10,
            "lines_removed": 2,
        }
        self.raise_on = set()  # methods that should raise

    def _maybe_raise(self, name):
        if name in self.raise_on:
            raise RuntimeError(f"boom: {name}")

    def jules_resolve_source(self, owner, repo):
        self.calls.append(("resolve_source", owner, repo))
        self._maybe_raise("resolve_source")
        return self.resolve_source_response

    def jules_create(self, **kwargs):
        self.calls.append(("create", kwargs))
        self._maybe_raise("create")
        return self.create_response

    def jules_get(self, session_id, fields="id,state,title"):
        self.calls.append(("get", session_id))
        self._maybe_raise("get")
        if self.get_responses:
            return self.get_responses.pop(0)
        return {"id": session_id, "state": "IN_PROGRESS", "title": "x"}

    def jules_approve(self, session_id):
        self.calls.append(("approve", session_id))
        self._maybe_raise("approve")
        return self.approve_response

    def jules_patch_summary(self, session_id):
        self.calls.append(("patch_summary", session_id))
        self._maybe_raise("patch_summary")
        return self.patch_summary_response

    def jules_patch_apply(self, session_id):
        self.calls.append(("patch_apply", session_id))
        self._maybe_raise("patch_apply")
        return self.patch_apply_response


@pytest.fixture
def fake_api(monkeypatch):
    """Patch every orchestration handler's `jules_api` module attribute."""
    api = _FakeJulesAPI()
    from agentic.jules.handlers import (
        dispatch,
        await_plan,
        monitor,
        verify,
        recover,
        integrate,
    )
    for mod in (dispatch, await_plan, monitor, verify, recover, integrate):
        monkeypatch.setattr(mod, "jules_api", api, raising=True)
    return api


# ---------------------------------------------------------------------------
# Happy path — clean landing
# ---------------------------------------------------------------------------


def test_clean_landing_full_lifecycle(store, fake_api):
    """DISPATCHED → IN_PROGRESS (approved) → COMPLETED → VERIFIED → integrate (no-op)."""
    from agentic.jules.handlers import (
        dispatch as h_dispatch,
        await_plan as h_await,
        monitor as h_monitor,
        verify as h_verify,
        integrate as h_integrate,
        _session_state as ss,
    )

    # 1. dispatch
    out = h_dispatch.handle(
        prompt="Add a comment to README",
        owner="netzkontrast",
        repo="the-agency-system",
        branch="Master",
        title="readme tweak",
    )
    assert out["ok"], out
    sid = out["data"]["session_id"]
    assert sid == "9876543210"
    session = ss.load_session(sid)
    assert session["state"] == "DISPATCHED"

    # 2. await_plan — first Jules state returns AWAITING_PLAN_APPROVAL,
    # handler calls jules_approve and bumps to IN_PROGRESS.
    fake_api.get_responses = [{"id": sid, "state": "AWAITING_PLAN_APPROVAL", "title": "x"}]
    out = h_await.handle(session_id=sid)
    assert out["ok"], out
    assert out["data"]["state"] == "IN_PROGRESS"
    assert out["data"]["plan_approved"] is True
    assert ("approve", sid) in fake_api.calls

    # 3. monitor — Jules state still IN_PROGRESS, then COMPLETED.
    fake_api.get_responses = [{"id": sid, "state": "IN_PROGRESS", "title": "x"}]
    out = h_monitor.handle(session_id=sid)
    assert out["ok"] and out["data"]["still_running"], out

    fake_api.get_responses = [{"id": sid, "state": "COMPLETED", "title": "x"}]
    out = h_monitor.handle(session_id=sid)
    assert out["ok"] and not out["data"]["still_running"], out
    session = ss.load_session(sid)
    assert session["state"] == "COMPLETED"
    assert session["completed_at"] is not None

    # 4. verify — patch summary reports zero diff → clean landing.
    fake_api.patch_summary_response = {
        "files": [], "lines_added": 0, "lines_removed": 0, "patch_bytes": 0,
        "base_commit": "", "suggested_commit_message": "",
    }
    out = h_verify.handle(session_id=sid)
    assert out["ok"], out
    assert out["data"]["state"] == "VERIFIED"
    assert out["data"]["branch_on_remote"] is True

    # 5. integrate from VERIFIED — no patch apply, session stays VERIFIED.
    out = h_integrate.handle(session_id=sid, pr_url="https://github.com/o/r/pull/1")
    assert out["ok"], out
    assert out["data"]["state"] == "VERIFIED"
    assert out["data"]["terminal"] is True
    session = ss.load_session(sid)
    assert session["pr_url"] == "https://github.com/o/r/pull/1"

    # And nobody called jules_patch_apply on the VERIFIED path.
    assert not any(c[0] == "patch_apply" for c in fake_api.calls)


# ---------------------------------------------------------------------------
# Silent-fail path
# ---------------------------------------------------------------------------


def test_silent_fail_recovery_path(store, fake_api):
    """COMPLETED → SILENT_FAIL → PATCH_EXTRACTED → APPLIED."""
    from agentic.jules.handlers import (
        dispatch as h_dispatch,
        await_plan as h_await,
        monitor as h_monitor,
        verify as h_verify,
        recover as h_recover,
        integrate as h_integrate,
        _session_state as ss,
    )
    from context import get_store

    # Dispatch + skip-plan path (jules_get reports COMPLETED early; this is
    # the rare path where Jules auto-approves trivial tasks).
    out = h_dispatch.handle(prompt="p", owner="o", repo="r", branch="b")
    sid = out["data"]["session_id"]
    fake_api.get_responses = [{"id": sid, "state": "COMPLETED", "title": "x"}]
    h_await.handle(session_id=sid)
    # session should now be in COMPLETED via the await_plan COMPLETED branch.
    assert ss.load_session(sid)["state"] == "COMPLETED"

    # Verify with a non-empty patch → SILENT_FAIL.
    fake_api.patch_summary_response = {
        "files": ["src/foo.py"],
        "lines_added": 5, "lines_removed": 1,
        "patch_bytes": 1024,
        "base_commit": "abc", "suggested_commit_message": "fix",
    }
    out = h_verify.handle(session_id=sid)
    assert out["ok"] and out["data"]["state"] == "SILENT_FAIL", out

    # Recover.
    out = h_recover.handle(session_id=sid)
    assert out["ok"] and out["data"]["state"] == "PATCH_EXTRACTED", out
    assert out["data"]["files"] == ["src/foo.py"]
    # SessionPatch node created.
    g = get_store()
    patch_rows = g.query(
        "MATCH (p:SessionPatch {session_id: $sid}) RETURN p",
        params={"sid": sid},
    )
    assert patch_rows, "SessionPatch node should exist after recover"

    # Integrate with apply=True → APPLIED.
    out = h_integrate.handle(session_id=sid)
    assert out["ok"] and out["data"]["state"] == "APPLIED", out
    assert out["data"]["patch_applied_locally"] is True


# ---------------------------------------------------------------------------
# State-machine guards
# ---------------------------------------------------------------------------


def test_session_not_found_error(store, fake_api):
    from agentic.jules.handlers import monitor as h_monitor
    out = h_monitor.handle(session_id="nope")
    assert not out["ok"]
    assert out["data"]["error"]["code"] == "SESSION_NOT_FOUND"


def test_illegal_transition_rejected(store, fake_api):
    """Calling verify on a DISPATCHED session must reject — verify needs COMPLETED."""
    from agentic.jules.handlers import (
        dispatch as h_dispatch,
        verify as h_verify,
    )
    out = h_dispatch.handle(prompt="p", owner="o", repo="r", branch="b")
    sid = out["data"]["session_id"]

    out = h_verify.handle(session_id=sid)
    assert not out["ok"]
    assert out["data"]["error"]["code"] == "SESSION_STATE_INVALID"
    assert "COMPLETED" in out["data"]["error"]["message"]


def test_api_exception_records_last_error(store, fake_api):
    from agentic.jules.handlers import (
        dispatch as h_dispatch,
        monitor as h_monitor,
        _session_state as ss,
    )
    out = h_dispatch.handle(prompt="p", owner="o", repo="r", branch="b")
    sid = out["data"]["session_id"]

    fake_api.raise_on.add("get")
    out = h_monitor.handle(session_id=sid)
    assert not out["ok"]
    assert out["data"]["error"]["code"] == "JULES_API_ERROR"
    session = ss.load_session(sid)
    assert session["last_error"] is not None
    assert "boom" in session["last_error"]


def test_resolve_source_failure(store, fake_api):
    from agentic.jules.handlers import dispatch as h_dispatch
    fake_api.resolve_source_response = {"error": "no matching source"}
    out = h_dispatch.handle(prompt="p", owner="o", repo="r", branch="b")
    assert not out["ok"]
    assert out["data"]["error"]["code"] == "JULES_SOURCE_UNRESOLVED"


def test_dispatch_missing_required_inputs(store, fake_api):
    from agentic.jules.handlers import dispatch as h_dispatch
    out = h_dispatch.handle(owner="o", repo="r")
    assert not out["ok"]
    assert out["data"]["error"]["code"] == "HANDLER_BAD_SIGNATURE"


def test_auto_approve_false_persists_continuation_signal(store, fake_api):
    """When the caller opts out of auto-approve and the session is at
    AWAITING_PLAN_APPROVAL, the envelope signals blocked_on_user so the
    pipeline can persist a Continuation."""
    from agentic.jules.handlers import (
        dispatch as h_dispatch,
        await_plan as h_await,
    )
    out = h_dispatch.handle(prompt="p", owner="o", repo="r", branch="b")
    sid = out["data"]["session_id"]

    fake_api.get_responses = [{"id": sid, "state": "AWAITING_PLAN_APPROVAL", "title": "x"}]
    out = h_await.handle(session_id=sid, auto_approve=False)
    assert out["ok"]
    assert out["data"]["blocked_on_user"] is True
    assert out["data"]["resume_token"] == f"await_plan/{sid}"
    # Nobody called approve.
    assert not any(c[0] == "approve" for c in fake_api.calls)


def test_state_transition_table_is_complete():
    """Sanity: every state-machine label declared in the schema enum has
    an entry in the transition table (even if its allowed set is empty)."""
    import json
    from pathlib import Path
    from agentic.jules.handlers._session_state import _ALLOWED_TRANSITIONS

    repo = Path(__file__).resolve().parents[2]
    schema = json.loads(
        (repo / "context" / "jules" / "schemas" / "jules-session.schema.json").read_text()
    )
    enum_states = set(schema["properties"]["state"]["enum"])
    table_states = set(_ALLOWED_TRANSITIONS.keys())
    assert enum_states == table_states, (
        f"schema-only: {enum_states - table_states}; table-only: {table_states - enum_states}"
    )
