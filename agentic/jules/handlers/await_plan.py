"""`mcp__jules_await_plan` — poll a session until AWAITING_PLAN_APPROVAL,
then call `jules_approve` if `auto_approve=True` (the default).

Phase 04 entry handler. Reads the JulesSession node, calls `jules_get`
once, and:

* If the session is still IN_PROGRESS (and hasn't reached the planning
  checkpoint yet), returns ``ok=True`` with ``state=IN_PROGRESS`` so the
  caller can poll again — the handler is intentionally one-shot so the
  pipeline can loop externally without consuming a long-running slot.
* If the session is in AWAITING_PLAN_APPROVAL, optionally calls
  `jules_approve` (default), records ``plan_approved_at``, and bumps
  the local state to IN_PROGRESS.
* If the session has already advanced past plan approval (state in
  COMPLETED / IN_PROGRESS post-approval), records observed state and
  exits cleanly.

Required inputs:
    session_id: ID of an existing JulesSession node.

Optional:
    auto_approve: When True (default), call `jules_approve` on the
        AWAITING_PLAN_APPROVAL state. When False, leave the session
        paused and return ``blocked_on_user=True`` so the pipeline
        persists a Continuation for the user to surface the plan.
"""

from __future__ import annotations

from typing import Any, Dict

from context._shared import error_codes
from jules_mcp import server as jules_api

from . import _session_state as ss


def handle(**kwargs) -> Dict[str, Any]:
    sid = kwargs.get("session_id")
    auto_approve = bool(kwargs.get("auto_approve", True))

    if not sid:
        return ss.err_envelope(error_codes.HANDLER_BAD_SIGNATURE, "await_plan requires session_id")

    session = ss.load_session(sid)
    if session is None:
        return ss.session_missing_envelope(sid)

    try:
        got = jules_api.jules_get(sid, fields="id,state,title")
    except Exception as exc:
        ss.write_session(sid, last_error=f"jules_get raised: {exc!r}")
        return ss.err_envelope(error_codes.JULES_API_ERROR, f"jules_get raised: {exc!r}")

    jules_state = got.get("state") if isinstance(got, dict) else None

    if jules_state == "AWAITING_PLAN_APPROVAL":
        if not auto_approve:
            ss.write_session(sid, jules_state=jules_state, state="AWAITING_PLAN_APPROVAL")
            return {
                "ok": True,
                "data": {
                    "session_id": sid,
                    "state": "AWAITING_PLAN_APPROVAL",
                    "blocked_on_user": True,
                    "blocked_reason": "plan awaits user approval (auto_approve=False)",
                    "resume_token": f"await_plan/{sid}",
                },
                "warnings": [],
                "next_suggested_tools": ["mcp__jules_approve"],
            }

        try:
            jules_api.jules_approve(sid)
        except Exception as exc:
            ss.write_session(sid, jules_state=jules_state, last_error=f"jules_approve raised: {exc!r}")
            return ss.err_envelope(error_codes.JULES_API_ERROR, f"jules_approve raised: {exc!r}")

        err = ss.assert_can_transition(session.get("state", "DISPATCHED"), "IN_PROGRESS")
        if err:
            return ss.err_envelope(error_codes.SESSION_STATE_INVALID, err)

        ss.write_session(
            sid,
            state="IN_PROGRESS",
            jules_state="IN_PROGRESS",
            plan_approved_at=ss.now_epoch(),
            last_error=None,
        )
        return {
            "ok": True,
            "data": {"session_id": sid, "state": "IN_PROGRESS", "plan_approved": True},
            "warnings": [],
            "next_suggested_tools": ["mcp__jules_monitor"],
        }

    if jules_state == "COMPLETED":
        target = "COMPLETED"
        err = ss.assert_can_transition(session.get("state", "DISPATCHED"), target)
        if err:
            return ss.err_envelope(error_codes.SESSION_STATE_INVALID, err)
        ss.write_session(sid, state=target, jules_state=jules_state, completed_at=ss.now_epoch(), last_error=None)
        return {
            "ok": True,
            "data": {"session_id": sid, "state": target, "skipped_approval": True},
            "warnings": [],
            "next_suggested_tools": ["mcp__jules_verify"],
        }

    target = "IN_PROGRESS" if jules_state == "IN_PROGRESS" else session.get("state", "DISPATCHED")
    err = ss.assert_can_transition(session.get("state", "DISPATCHED"), target)
    if err:
        return ss.err_envelope(error_codes.SESSION_STATE_INVALID, err)
    ss.write_session(sid, state=target, jules_state=jules_state, last_error=None)
    return {
        "ok": True,
        "data": {
            "session_id": sid,
            "state": target,
            "jules_state": jules_state,
            "still_waiting": True,
        },
        "warnings": [],
        "next_suggested_tools": ["mcp__jules_await_plan"],
    }
