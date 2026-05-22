"""Envelope persistence tests — spec 07-v1 §FR4.

The v0 ``_MockContext`` seam is gone; persistence flows through the
process-singleton :func:`context.get_store`. Tests swap the singleton
for a tmp-DB :class:`context.Store` so the real `ontology.db` is never
touched.
"""

from __future__ import annotations

import pytest

import context
from context._store.sqlite import Store
from workflow._runner import pipeline
from workflow._runner.envelope import persist, hydrate


@pytest.fixture
def tmp_store(monkeypatch, tmp_path):
    db_path = str(tmp_path / "ontology.db")
    store = Store(db_path=db_path)
    store.boot()
    monkeypatch.setattr(context, "_STORE", store, raising=False)
    return store


def test_blocked_envelope_serializes_and_resumes(tmp_store):
    env = {
        "status": "blocked_on_user",
        "phase_id": "02",
        "row": "music",
        "session_id": "test-session-123",
        "opaque_state": {"k": "v"},
        "tool_result": {
            "ok": True,
            "data": {},
            "warnings": [],
            "next_suggested_tools": [],
        },
        "blocked_reason": "needs auth",
        "resume_token": "token1",
    }

    node_id = persist(env)
    assert node_id == "continuation:test-session-123:02"

    # The Continuation node landed in the graph.
    rows = tmp_store.query(
        "MATCH (c:Continuation {id: $id}) RETURN c",
        params={"id": node_id},
    )
    assert rows, "Continuation node did not land in the graph"

    # Hydrate round-trips the envelope.
    restored = hydrate("test-session-123", "02")
    assert restored is not None
    assert restored["status"] == "blocked_on_user"
    assert restored["opaque_state"] == {"k": "v"}


def test_resume_terminal_envelope_surfaces_resume_terminal(tmp_store):
    """Spec 07-v1 §FR4: a hydrated terminal envelope returns RESUME_TERMINAL."""
    # NB: graphqlite's Cypher serializer rejects JSON `null` in nested
    # property maps; the production code never persists terminal envelopes
    # (only `blocked_*` reach `persist`), so we use sentinel strings here
    # to round-trip the envelope through the store for the test.
    env = {
        "status": "completed",
        "phase_id": "03",
        "row": "music",
        "session_id": "sess-term-1",
        "opaque_state": {"a": 1},
        "tool_result": {
            "ok": True, "data": {}, "warnings": [], "next_suggested_tools": [],
        },
        "blocked_reason": "terminal-test",
        "resume_token": "terminal-test",
    }
    persist(env)

    out = pipeline.resume("sess-term-1", "03", user_response={"b": 2})
    assert out["tool_result"]["ok"] is False
    assert out["tool_result"]["data"]["error"]["code"] == "RESUME_TERMINAL"


def test_resume_merges_user_response_and_rewalks(tmp_store, monkeypatch):
    """Spec 07-v1 §FR4: shallow-merge user_response, re-walk, delete on terminal."""
    # Seed a Phase node so resume's re-walk has a body_ref to resolve.
    tmp_store.upsert_node(
        "phase/sandboxresume/01",
        {"row": "sandboxresume", "phase_id": "01", "body_ref": "phases/01.md"},
        label="Phase",
    )

    # Persist a blocked_on_user Continuation.
    blocked = {
        "status": "blocked_on_user",
        "phase_id": "01",
        "row": "sandboxresume",
        "session_id": "sess-rewalk-1",
        "opaque_state": {"a": 1},
        "tool_result": {
            "ok": False, "data": {}, "warnings": [], "next_suggested_tools": [],
        },
        "blocked_reason": "awaiting input",
        "resume_token": "rt-1",
    }
    persist(blocked)

    # Stub _walk_phase to capture the merged opaque_state and return a
    # completed envelope. The real walker requires phase bodies + handlers
    # on disk; we're testing resume's wiring, not the walker.
    captured: dict = {}

    def fake_walk(session_id, row, phase_id, phase_node, inputs):
        captured["inputs"] = inputs
        captured["row"] = row
        captured["phase_id"] = phase_id
        return {
            "status": "completed",
            "phase_id": phase_id,
            "row": row,
            "session_id": session_id,
            "opaque_state": dict(inputs),
            "tool_result": {
                "ok": True, "data": {}, "warnings": [], "next_suggested_tools": [],
            },
            "blocked_reason": None,
            "resume_token": None,
        }

    monkeypatch.setattr(pipeline, "_walk_phase", fake_walk)
    monkeypatch.setattr(pipeline, "get_store", lambda: tmp_store)

    out = pipeline.resume("sess-rewalk-1", "01", user_response={"b": 2})

    # Shallow merge: both keys present, top-level overwrite semantics.
    assert captured["inputs"] == {"a": 1, "b": 2}
    assert captured["row"] == "sandboxresume"
    assert captured["phase_id"] == "01"

    # Re-walked envelope is returned.
    assert out["status"] == "completed"
    assert out["session_id"] == "sess-rewalk-1"

    # Continuation was deleted on terminal status.
    assert hydrate("sess-rewalk-1", "01") is None


def test_resume_missing_phase_node_returns_resume_phase_gone(tmp_store, monkeypatch):
    """If the Phase node is gone on resume, surface RESUME_PHASE_GONE."""
    blocked = {
        "status": "blocked_on_user",
        "phase_id": "01",
        "row": "ghostrow",
        "session_id": "sess-gone-1",
        "opaque_state": {},
        "tool_result": {
            "ok": False, "data": {}, "warnings": [], "next_suggested_tools": [],
        },
        "blocked_reason": "x",
        "resume_token": "rt",
    }
    persist(blocked)
    monkeypatch.setattr(pipeline, "get_store", lambda: tmp_store)

    out = pipeline.resume("sess-gone-1", "01", user_response={})
    assert out["status"] == "failed"
    assert out["tool_result"]["data"]["error"]["code"] == "RESUME_PHASE_GONE"
    # Continuation also cleaned up.
    assert hydrate("sess-gone-1", "01") is None
