"""Gate-evaluator tests for the jules-row orchestration gates.

The four gates are:

* ``research-complete``  — phase 02; counts Finding nodes in the graph.
* ``plan-approved``      — phase 05; reads JulesSession.plan_approved_at.
* ``session-completed``  — phase 06; reads JulesSession.state.
* ``patch-applied``      — phase 08; reads JulesSession.state.

The first one rewires from the v0.1 placeholder; the latter three are new.
"""

from __future__ import annotations

import pytest

import context
from context._store.sqlite import Store


@pytest.fixture
def store(monkeypatch, tmp_path):
    db_path = str(tmp_path / "ontology.db")
    s = Store(db_path=db_path)
    s.boot()
    monkeypatch.setattr(context, "_STORE", s, raising=False)
    yield s


# ---------------------------------------------------------------------------
# research-complete
# ---------------------------------------------------------------------------


def test_research_complete_blocks_on_empty_graph(store):
    from workflow.jules.gates.research_complete import evaluate
    result = evaluate({"row": "jules", "phase_id": "02", "inputs": {"topic": "x"}}, None)
    assert result["ok"] is False
    assert "no Finding" in result["message"]


def test_research_complete_passes_after_finding_seeded(store):
    from workflow.jules.gates.research_complete import evaluate
    store.upsert_node(
        "finding/topic-x/1",
        {"topic": "x", "claim": "the sky is blue", "confidence": 0.9, "source_urls": []},
        label="Finding",
    )
    result = evaluate({"row": "jules", "phase_id": "02", "inputs": {"topic": "x"}}, None)
    assert result["ok"] is True


def test_research_complete_topic_filter(store):
    """Findings for unrelated topics don't satisfy the gate."""
    from workflow.jules.gates.research_complete import evaluate
    store.upsert_node(
        "finding/other/1",
        {"topic": "other", "claim": "z", "confidence": 0.5, "source_urls": []},
        label="Finding",
    )
    result = evaluate({"row": "jules", "phase_id": "02", "inputs": {"topic": "x"}}, None)
    assert result["ok"] is False


# ---------------------------------------------------------------------------
# plan-approved
# ---------------------------------------------------------------------------


def _seed_session(store, sid: str, **fields):
    payload = {
        "session_id": sid,
        "state": "DISPATCHED",
        "owner": "o",
        "repo": "r",
        "branch": "b",
        "prompt": "p",
        "created_at": 1,
    }
    payload.update(fields)
    store.upsert_node(f"jules-session/{sid}", payload, label="JulesSession")


def test_plan_approved_blocks_when_session_dispatched(store):
    from workflow.jules.gates.plan_approved import evaluate
    _seed_session(store, "1", state="DISPATCHED")
    result = evaluate({"inputs": {"session_id": "1"}}, None)
    assert result["ok"] is False


def test_plan_approved_passes_when_plan_approved_at_set(store):
    from workflow.jules.gates.plan_approved import evaluate
    _seed_session(store, "1", state="IN_PROGRESS", plan_approved_at=999)
    result = evaluate({"inputs": {"session_id": "1"}}, None)
    assert result["ok"] is True


def test_plan_approved_passes_when_state_past_approval(store):
    """Even without plan_approved_at stamped, a COMPLETED session counts
    as having cleared the planning checkpoint."""
    from workflow.jules.gates.plan_approved import evaluate
    _seed_session(store, "1", state="COMPLETED")
    result = evaluate({"inputs": {"session_id": "1"}}, None)
    assert result["ok"] is True


def test_plan_approved_needs_session_id(store):
    from workflow.jules.gates.plan_approved import evaluate
    result = evaluate({"inputs": {}}, None)
    assert result["ok"] is False
    assert "session_id" in result["message"]


# ---------------------------------------------------------------------------
# session-completed
# ---------------------------------------------------------------------------


def test_session_completed_blocks_pre_completion(store):
    from workflow.jules.gates.session_completed import evaluate
    _seed_session(store, "1", state="IN_PROGRESS")
    result = evaluate({"inputs": {"session_id": "1"}}, None)
    assert result["ok"] is False


def test_session_completed_passes_at_completed(store):
    from workflow.jules.gates.session_completed import evaluate
    _seed_session(store, "1", state="COMPLETED")
    result = evaluate({"inputs": {"session_id": "1"}}, None)
    assert result["ok"] is True


def test_session_completed_passes_at_verified(store):
    """VERIFIED is post-completion, so the gate must pass — useful when
    integrate re-evaluates the chain on a clean-landing path."""
    from workflow.jules.gates.session_completed import evaluate
    _seed_session(store, "1", state="VERIFIED")
    result = evaluate({"inputs": {"session_id": "1"}}, None)
    assert result["ok"] is True


# ---------------------------------------------------------------------------
# patch-applied
# ---------------------------------------------------------------------------


def test_patch_applied_blocks_at_silent_fail(store):
    """SILENT_FAIL is not a valid pre-integrate state — the caller must
    run recover first to get to PATCH_EXTRACTED."""
    from workflow.jules.gates.patch_applied import evaluate
    _seed_session(store, "1", state="SILENT_FAIL")
    result = evaluate({"inputs": {"session_id": "1"}}, None)
    assert result["ok"] is False


def test_patch_applied_passes_at_patch_extracted(store):
    from workflow.jules.gates.patch_applied import evaluate
    _seed_session(store, "1", state="PATCH_EXTRACTED")
    result = evaluate({"inputs": {"session_id": "1"}}, None)
    assert result["ok"] is True


def test_patch_applied_passes_at_verified(store):
    from workflow.jules.gates.patch_applied import evaluate
    _seed_session(store, "1", state="VERIFIED")
    result = evaluate({"inputs": {"session_id": "1"}}, None)
    assert result["ok"] is True


def test_patch_applied_blocks_pre_completion(store):
    from workflow.jules.gates.patch_applied import evaluate
    _seed_session(store, "1", state="DISPATCHED")
    result = evaluate({"inputs": {"session_id": "1"}}, None)
    assert result["ok"] is False
