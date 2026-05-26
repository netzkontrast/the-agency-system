"""Callable evaluator for the `plan-approved` gate.

Returns ok=True when the JulesSession identified by
``envelope_state["inputs"]["session_id"]`` has a non-null
``plan_approved_at`` *or* its local lifecycle state is already past
the AWAITING_PLAN_APPROVAL checkpoint. ok=False means phase 04 must
run before phase 05 may proceed.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from agentic.jules.handlers._session_state import load_session


_PAST_PLAN_STATES = {
    "IN_PROGRESS",
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
        return {"ok": False, "message": "plan-approved gate needs inputs.session_id"}

    session = load_session(sid)
    if session is None:
        return {"ok": False, "message": f"no JulesSession node for session_id={sid}"}

    if session.get("plan_approved_at"):
        return {"ok": True, "message": "plan-approved at " + str(session["plan_approved_at"])}

    state = session.get("state", "DISPATCHED")
    if state in _PAST_PLAN_STATES:
        return {"ok": True, "message": f"local state {state} implies plan already cleared"}

    return {"ok": False, "message": f"session state {state} has not cleared AWAITING_PLAN_APPROVAL"}
