"""`mcp__jules_monitor` — observe a session's current Jules-API state.

Phase 05 entry handler. One-shot probe — the pipeline drives external
polling, so this handler issues exactly one `jules_get` and records the
observed state on the JulesSession node.

State machine:

* IN_PROGRESS → still working; returns ``ok=True`` with ``still_running=True``.
* COMPLETED   → local state advances to COMPLETED; ``completed_at``
  is stamped if not already set.
* FAILED      → local state advances to FAILED; ``last_error`` records
  the API-reported failure.
* AWAITING_PLAN_APPROVAL after monitor was already past it → recorded
  but treated as a non-fatal regression (Jules occasionally reopens
  planning on a revision request).

Required inputs:
    session_id: ID of an existing JulesSession node.
"""

from __future__ import annotations

from typing import Any, Dict

from context._shared import error_codes
from jules_mcp import server as jules_api

from . import _session_state as ss


def handle(**kwargs) -> Dict[str, Any]:
    sid = kwargs.get("session_id")
    if not sid:
        return ss.err_envelope(error_codes.HANDLER_BAD_SIGNATURE, "monitor requires session_id")

    session = ss.load_session(sid)
    if session is None:
        return ss.session_missing_envelope(sid)

    try:
        got = jules_api.jules_get(sid, fields="id,state,title")
    except Exception as exc:
        ss.write_session(sid, last_error=f"jules_get raised: {exc!r}")
        return ss.err_envelope(error_codes.JULES_API_ERROR, f"jules_get raised: {exc!r}")

    jules_state = got.get("state") if isinstance(got, dict) else None
    current_local = session.get("state", "DISPATCHED")

    if jules_state == "COMPLETED":
        err = ss.assert_can_transition(current_local, "COMPLETED")
        if err:
            return ss.err_envelope(error_codes.SESSION_STATE_INVALID, err)
        updates: Dict[str, Any] = {"state": "COMPLETED", "jules_state": jules_state, "last_error": None}
        if not session.get("completed_at"):
            updates["completed_at"] = ss.now_epoch()
        ss.write_session(sid, **updates)
        return {
            "ok": True,
            "data": {"session_id": sid, "state": "COMPLETED", "still_running": False},
            "warnings": [],
            "next_suggested_tools": ["mcp__jules_verify"],
        }

    if jules_state == "FAILED":
        err = ss.assert_can_transition(current_local, "FAILED")
        if err:
            return ss.err_envelope(error_codes.SESSION_STATE_INVALID, err)
        ss.write_session(
            sid,
            state="FAILED",
            jules_state=jules_state,
            last_error="jules-api reported state=FAILED",
        )
        return ss.err_envelope(
            error_codes.JULES_API_ERROR,
            "session ended in FAILED state on the Jules side",
        )

    # All non-terminal API states — stay in current local lifecycle and
    # surface the observed Jules state. AWAITING_PLAN_APPROVAL coming back
    # after we already approved is recorded but doesn't error.
    ss.write_session(sid, jules_state=jules_state, last_error=None)
    return {
        "ok": True,
        "data": {
            "session_id": sid,
            "state": current_local,
            "jules_state": jules_state,
            "still_running": True,
        },
        "warnings": [],
        "next_suggested_tools": ["mcp__jules_monitor"],
    }
