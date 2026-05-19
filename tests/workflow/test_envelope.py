import pytest
from workflow._runner import persist, hydrate
from workflow._runner.envelope import context

def test_blocked_envelope_serializes_and_resumes():
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

    # Write to mock context graph
    node_id = persist(env)
    assert node_id == "continuation:test-session-123:02"

    # Verify in graph
    node = context.get_node(node_id)
    assert node is not None
    assert node["label"] == "Continuation"

    # Hydrate
    restored = hydrate("test-session-123", "02")
    assert restored["status"] == "blocked_on_user"
    assert restored["opaque_state"] == {"k": "v"}
