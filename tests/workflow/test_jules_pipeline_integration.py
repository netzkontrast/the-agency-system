"""End-to-end pipeline integration: drive the jules state machine through
the real walker (pipeline.start → _walk_phase → gate evaluator → handler).

These tests are the integration glue — they confirm the handler registry
resolves the new orchestration verbs, the gate YAMLs parse, the gate
evaluators load via importlib, and the state-machine flag set by one
phase blocks/unblocks the next phase as expected.
"""

from __future__ import annotations

from pathlib import Path

import pytest

import context
import workflow._runner.pipeline as pipeline
from context._store.sqlite import Store


REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def harness(monkeypatch, tmp_path):
    """Tmp Store + cwd = repo root so the walker reads real phase bodies + gates."""
    monkeypatch.chdir(REPO_ROOT)
    db_path = str(tmp_path / "ontology.db")
    s = Store(db_path=db_path)
    s.boot()
    monkeypatch.setattr(context, "_STORE", s, raising=False)
    pipeline._reset_handler_registry_for_tests()
    # Seed real Phase nodes from disk.
    pipeline.boot()
    yield s
    pipeline._reset_handler_registry_for_tests()


class _StubAPI:
    """Trivial stand-in for jules_mcp.server — handlers + gates never call it
    in these tests because we pre-seed JulesSession nodes directly."""

    def jules_resolve_source(self, owner, repo):
        return {"source": "sources/x", "github": {"owner": owner, "repo": repo}}

    def jules_create(self, **kwargs):
        return {
            "id": "stub-sid-1",
            "name": "sessions/stub-sid-1",
            "state": "IN_PROGRESS",
            "url": "",
        }

    def jules_get(self, session_id, fields="id,state,title"):
        return {"id": session_id, "state": "IN_PROGRESS", "title": ""}

    def jules_approve(self, session_id):
        return {"ok": True, "session_id": session_id}

    def jules_patch_summary(self, session_id):
        return {
            "files": [], "lines_added": 0, "lines_removed": 0, "patch_bytes": 0,
            "base_commit": "", "suggested_commit_message": "",
        }

    def jules_patch_apply(self, session_id):
        return {"applied": True, "files": [], "lines_added": 0, "lines_removed": 0}


@pytest.fixture
def stub_api(monkeypatch):
    api = _StubAPI()
    from agentic.jules.handlers import (
        dispatch, await_plan, monitor, verify, recover, integrate,
    )
    for mod in (dispatch, await_plan, monitor, verify, recover, integrate):
        monkeypatch.setattr(mod, "jules_api", api, raising=True)
    return api


def _seed_session(store, sid: str, **fields):
    payload = {
        "session_id": sid,
        "state": "DISPATCHED",
        "owner": "o", "repo": "r", "branch": "b", "prompt": "p",
        "created_at": 1,
    }
    payload.update(fields)
    store.upsert_node(f"jules-session/{sid}", payload, label="JulesSession")


def test_monitor_blocked_by_plan_approved_gate(harness, stub_api):
    """Phase 05 (monitor) must be blocked by the plan-approved gate when
    the session is still in DISPATCHED."""
    _seed_session(harness, "sid-1", state="DISPATCHED")
    env = pipeline.start(row="jules", phase_id="05", inputs={"session_id": "sid-1"})
    assert env["status"] == "blocked_on_gate", env
    assert env["blocked_reason"] is not None
    assert "plan-approved" in env["blocked_reason"] or "session" in env["blocked_reason"]


def test_monitor_passes_when_plan_approved(harness, stub_api):
    _seed_session(harness, "sid-2", state="IN_PROGRESS", plan_approved_at=999)
    env = pipeline.start(row="jules", phase_id="05", inputs={"session_id": "sid-2"})
    # status is completed because monitor's handler returns ok=True.
    assert env["status"] == "completed", env
    # Either still_running (jules_state=IN_PROGRESS) or transitioned.
    assert env["tool_result"]["data"]["session_id"] == "sid-2"


def test_verify_blocked_by_session_completed_gate(harness, stub_api):
    _seed_session(harness, "sid-3", state="IN_PROGRESS", plan_approved_at=1)
    env = pipeline.start(row="jules", phase_id="06", inputs={"session_id": "sid-3"})
    assert env["status"] == "blocked_on_gate", env


def test_verify_runs_at_completed(harness, stub_api):
    _seed_session(harness, "sid-4", state="COMPLETED", plan_approved_at=1, completed_at=2)
    env = pipeline.start(row="jules", phase_id="06", inputs={"session_id": "sid-4"})
    assert env["status"] == "completed", env
    # Clean landing (stub returns zero diff) → VERIFIED.
    assert env["tool_result"]["data"]["state"] == "VERIFIED"


def test_integrate_blocked_pre_verified(harness, stub_api):
    """patch-applied gate keeps integrate out of reach from COMPLETED or DISPATCHED."""
    _seed_session(harness, "sid-5", state="COMPLETED", plan_approved_at=1, completed_at=2)
    env = pipeline.start(row="jules", phase_id="08", inputs={"session_id": "sid-5"})
    assert env["status"] == "blocked_on_gate", env


def test_integrate_runs_at_patch_extracted(harness, stub_api):
    _seed_session(
        harness, "sid-6",
        state="PATCH_EXTRACTED",
        plan_approved_at=1, completed_at=2, verified_at=3,
    )
    env = pipeline.start(row="jules", phase_id="08", inputs={"session_id": "sid-6"})
    assert env["status"] == "completed", env
    assert env["tool_result"]["data"]["state"] == "APPLIED"
