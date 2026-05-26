"""Shared state-machine helpers for the jules-row orchestration handlers.

The six orchestration handlers (dispatch, await_plan, monitor, verify,
recover, integrate) advance a `JulesSession` ontology node through a
deterministic state machine:

```
DISPATCHED  →  IN_PROGRESS  →  AWAITING_PLAN_APPROVAL  →  IN_PROGRESS
                                                              ↓
                                                          COMPLETED
                                                          ↓        ↓
                                                       VERIFIED   SILENT_FAIL
                                                                    ↓
                                                              PATCH_EXTRACTED
                                                                    ↓
                                                                 APPLIED
```

`FAILED` is a terminal sink reachable from any non-terminal state when a
handler hits an unrecoverable API error.

This module is the *only* place the transition table lives — handlers
import `assert_can_transition` so an illegal jump (e.g. `verify` on a
`DISPATCHED` session) returns `SESSION_STATE_INVALID` instead of
silently corrupting the node.
"""

from __future__ import annotations

import time
from typing import Any, Dict, FrozenSet, Optional

from context import get_store
from context._shared import error_codes


_ALLOWED_TRANSITIONS: Dict[str, FrozenSet[str]] = {
    "DISPATCHED": frozenset({"IN_PROGRESS", "AWAITING_PLAN_APPROVAL", "COMPLETED", "FAILED"}),
    "IN_PROGRESS": frozenset({"AWAITING_PLAN_APPROVAL", "COMPLETED", "FAILED"}),
    "AWAITING_PLAN_APPROVAL": frozenset({"IN_PROGRESS", "COMPLETED", "FAILED"}),
    "COMPLETED": frozenset({"VERIFIED", "SILENT_FAIL", "FAILED"}),
    "VERIFIED": frozenset({"FAILED"}),
    "SILENT_FAIL": frozenset({"PATCH_EXTRACTED", "FAILED"}),
    "PATCH_EXTRACTED": frozenset({"APPLIED", "FAILED"}),
    "APPLIED": frozenset({"FAILED"}),
    "FAILED": frozenset(),
}

TERMINAL_STATES: FrozenSet[str] = frozenset({"VERIFIED", "APPLIED", "FAILED"})


def session_node_id(session_id: str) -> str:
    """Canonical ontology node id for a Jules session."""
    return f"jules-session/{session_id}"


def load_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Return the JulesSession node payload or None when missing."""
    g = get_store()
    rows = g.query(
        "MATCH (s:JulesSession {session_id: $sid}) RETURN s",
        params={"sid": session_id},
    )
    if not rows:
        return None
    s = rows[0].get("s", rows[0]) if isinstance(rows[0], dict) else None
    if not isinstance(s, dict):
        return None
    props = s.get("properties") or s.get("payload") or s
    if isinstance(props, str):
        import json
        try:
            props = json.loads(props)
        except Exception:
            return None
    return props if isinstance(props, dict) else None


def assert_can_transition(current: str, target: str) -> Optional[str]:
    """Return an error message when the jump is illegal, else None.

    Idempotent self-loops (current == target) are allowed silently so a
    handler called twice doesn't error — the second call is a no-op
    transition.
    """
    if current == target:
        return None
    allowed = _ALLOWED_TRANSITIONS.get(current, frozenset())
    if target not in allowed:
        return (
            f"illegal state transition {current} -> {target}; "
            f"allowed targets from {current}: {sorted(allowed) or '(terminal)'}"
        )
    return None


def write_session(session_id: str, **fields: Any) -> Dict[str, Any]:
    """Upsert the JulesSession node with a partial set of fields.

    The full prior payload is preserved; only the keys passed in are
    overwritten. Returns the merged payload.
    """
    g = get_store()
    existing = load_session(session_id) or {"session_id": session_id}
    existing.update(fields)
    g.upsert_node(
        session_node_id(session_id),
        existing,
        label="JulesSession",
    )
    return existing


def now_epoch() -> int:
    return int(time.time())


def err_envelope(code: str, message: str) -> Dict[str, Any]:
    """Standard failure envelope helper for orchestration handlers."""
    return {
        "ok": False,
        "data": {"error": {"code": code, "message": message}},
        "warnings": [],
        "next_suggested_tools": [],
    }


def session_missing_envelope(session_id: str) -> Dict[str, Any]:
    return err_envelope(
        error_codes.SESSION_NOT_FOUND,
        f"no JulesSession node for session_id={session_id}",
    )
