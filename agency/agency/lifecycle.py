"""Lifecycle — task/agent state-machine. Verb frame: open · move · close (write)
+ status (read). States align with A2A tasks. An *agent* is a Lifecycle
parameterization (a who-session), linked DISPATCHED_TO. Gates record a PASSED
edge; a failing gate that needs a human -> INPUT_REQUIRED (intent re-entry).

Lifecycle state mutates in place (so SERVES/DISPATCHED_TO edges stay stable);
append-only bi-temporality is demonstrated on Intent (see intent.py).
"""
from __future__ import annotations

from typing import Optional

from .memory import Memory

# A2A-aligned task states
SUBMITTED, WORKING, INPUT_REQUIRED, COMPLETED, FAILED, CANCELED = (
    "submitted", "working", "input-required", "completed", "failed", "canceled",
)


class Lifecycle:
    def __init__(self, memory: Memory):
        self.m = memory

    def open(self, intent_id: str, agent: Optional[str] = None) -> str:
        lc = self.m.record("Lifecycle", {"state": WORKING, "phase": 0})
        self.m.link(lc, intent_id, "SERVES")
        if agent:
            agent_id = self.m.record("Agent", {"runtime": "cloud-async"}, node_id=f"agent:{agent}")
            self.m.link(lc, agent_id, "DISPATCHED_TO")
        return lc

    def move(self, lc_id: str, gate: str, ok: bool) -> str:
        if ok:
            g = self.m.record("Gate", {"name": gate, "passed": True})
            self.m.link(lc_id, g, "PASSED")
            phase = (self.m.recall(lc_id) or {}).get("phase", 0) + 1
            self.m.update(lc_id, {"phase": phase, "state": WORKING})
            return WORKING
        self.m.update(lc_id, {"state": INPUT_REQUIRED})  # human (intent) re-entry
        return INPUT_REQUIRED

    def complete(self, lc_id: str) -> str:
        self.m.update(lc_id, {"state": COMPLETED})
        return COMPLETED

    def status(self, lc_id: str) -> Optional[str]:
        props = self.m.recall(lc_id)
        return props.get("state") if props else None
