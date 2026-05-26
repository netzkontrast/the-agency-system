"""Callable evaluator for the `session-completed` gate.

Returns ok=True when the JulesSession's local state is at least
COMPLETED (i.e. has reached the post-completion lifecycle stages).
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from agentic.jules.handlers._session_state import load_session


_POST_COMPLETION_STATES = {
    "COMPLETED",
    "VERIFIED",
    "SILENT_FAIL",
    "PATCH_EXTRACTED",
    "APPLIED",
}


def _session_id(envelope_state: Dict[str, Any]) -> Optional[str]:
    inputs = envelope_state.get("inputs") if isinstance(envelope_state, dict) else None
    if isinstance(inputs, dict):
        sid = inputs.get("session_id")
        if isinstance(sid, str) and sid:
            return sid
    return None


def evaluate(envelope_state: Dict[str, Any], args: Dict[str, Any] | None = None) -> Dict[str, str]:
    sid = _session_id(envelope_state)
    if not sid:
        return {"ok": False, "message": "session-completed gate needs inputs.session_id"}

    session = load_session(sid)
    if session is None:
        return {"ok": False, "message": f"no JulesSession node for session_id={sid}"}

    state = session.get("state", "DISPATCHED")
    if state in _POST_COMPLETION_STATES:
        return {"ok": True, "message": f"local state {state} is past COMPLETED"}

    return {"ok": False, "message": f"session state {state} is pre-COMPLETED; keep polling monitor"}
