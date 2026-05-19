import json
from typing import TypedDict, Literal, Any, Dict, Optional

class PhaseStateEnvelope(TypedDict):
    status: Literal["running", "blocked_on_gate", "blocked_on_user", "completed", "failed"]
    phase_id: str
    row: str
    session_id: str
    opaque_state: dict[str, Any]
    tool_result: dict
    blocked_reason: Optional[str]
    resume_token: Optional[str]

# Mock context store for v1 architecture
class _MockContext:
    def __init__(self):
        self.nodes = {}

    def upsert_node(self, node_id: str, data: dict, label: str):
        self.nodes[node_id] = {"data": data, "label": label}

    def get_node(self, node_id: str):
        return self.nodes.get(node_id)

    def delete_node(self, node_id: str):
        if node_id in self.nodes:
            del self.nodes[node_id]

context = _MockContext()

def persist(envelope: PhaseStateEnvelope) -> str:
    """Emits a Continuation node to the context graph."""
    node_id = f"continuation:{envelope['session_id']}:{envelope['phase_id']}"
    # In v1 architecture, continuation is a graph node
    context.upsert_node(
        node_id,
        {
            "session_id": envelope["session_id"],
            "phase_id": envelope["phase_id"],
            "opaque_state": envelope["opaque_state"],
            "envelope": envelope  # storing full envelope for hydrate
        },
        label="Continuation"
    )
    return node_id

def hydrate(session_id: str, phase_id: str) -> Optional[PhaseStateEnvelope]:
    """Reads the Continuation node from the graph."""
    node_id = f"continuation:{session_id}:{phase_id}"
    node = context.get_node(node_id)
    if not node:
        return None
    return node["data"]["envelope"]

def delete(session_id: str, phase_id: str) -> None:
    """Deletes the Continuation node."""
    node_id = f"continuation:{session_id}:{phase_id}"
    context.delete_node(node_id)

def sweep_ttl() -> None:
    """No-op in v1. TTL is handled by graph driver or periodic job."""
    pass
