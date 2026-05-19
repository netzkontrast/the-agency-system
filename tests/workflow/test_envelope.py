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
