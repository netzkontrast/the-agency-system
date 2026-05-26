"""`mcp__jules_integrate` — finalise a Jules session.

Phase 08 (terminal) entry handler. Two paths:

* From VERIFIED — the session already landed on origin; integrate
  records the (optional) PR url and stops.
* From PATCH_EXTRACTED — recover pulled the patch; integrate calls
  `jules_patch_apply` (when `apply=True`, the default) to land the
  diff onto the local working tree. The local state moves to APPLIED;
  the `SessionPatch` node's `applied` flag flips True.

Either way, the handler is the row's terminal phase — afterwards the
session machine has no further legal transitions (other than the
terminal FAILED sink).

Required inputs:
    session_id: ID of an existing JulesSession node.

Optional:
    apply: When True (default), call `jules_patch_apply` to land the
        diff. When False, mark PATCH_EXTRACTED → APPLIED bookkeeping
        only — useful when the caller is going to land the patch
        through a separate path (e.g. GitHub MCP).
    pr_url: Optional PR url to stamp onto the session (used when the
        caller has already opened one).
"""

from __future__ import annotations

from typing import Any, Dict

from context import get_store
from context._shared import error_codes
from jules_mcp import server as jules_api

from . import _session_state as ss


def handle(**kwargs) -> Dict[str, Any]:
    sid = kwargs.get("session_id")
    apply_patch = bool(kwargs.get("apply", True))
    pr_url = kwargs.get("pr_url")

    if not sid:
        return ss.err_envelope(error_codes.HANDLER_BAD_SIGNATURE, "integrate requires session_id")

    session = ss.load_session(sid)
    if session is None:
        return ss.session_missing_envelope(sid)

    current = session.get("state", "DISPATCHED")

    if current == "VERIFIED":
        updates: Dict[str, Any] = {"last_error": None}
        if pr_url:
            updates["pr_url"] = pr_url
        ss.write_session(sid, **updates)
        return {
            "ok": True,
            "data": {
                "session_id": sid,
                "state": "VERIFIED",
                "pr_url": pr_url or session.get("pr_url"),
                "terminal": True,
            },
            "warnings": [],
            "next_suggested_tools": [],
        }

    if current != "PATCH_EXTRACTED":
        return ss.err_envelope(
            error_codes.SESSION_STATE_INVALID,
            f"integrate expects state in (VERIFIED, PATCH_EXTRACTED), got {current}",
        )

    if not apply_patch:
        ss.write_session(
            sid,
            state="APPLIED",
            pr_url=pr_url,
            last_error=None,
        )
        _mark_patch_applied(sid, applied=None)
        return {
            "ok": True,
            "data": {
                "session_id": sid,
                "state": "APPLIED",
                "pr_url": pr_url,
                "patch_applied_locally": False,
                "terminal": True,
            },
            "warnings": ["apply=False — caller is responsible for landing the patch"],
            "next_suggested_tools": [],
        }

    try:
        result = jules_api.jules_patch_apply(sid)
    except Exception as exc:
        ss.write_session(sid, last_error=f"jules_patch_apply raised: {exc!r}")
        return ss.err_envelope(error_codes.PATCH_APPLY_FAILED, f"jules_patch_apply raised: {exc!r}")

    if not isinstance(result, dict) or not result.get("applied"):
        stderr = (result.get("git_stderr") or result.get("error") or "patch did not apply") if isinstance(result, dict) else "non-dict response"
        ss.write_session(sid, last_error=str(stderr))
        _mark_patch_applied(sid, applied=False)
        return ss.err_envelope(error_codes.PATCH_APPLY_FAILED, str(stderr))

    ss.write_session(
        sid,
        state="APPLIED",
        pr_url=pr_url,
        last_error=None,
    )
    _mark_patch_applied(sid, applied=True)

    return {
        "ok": True,
        "data": {
            "session_id": sid,
            "state": "APPLIED",
            "patch_applied_locally": True,
            "files": result.get("files", []),
            "lines_added": result.get("lines_added", 0),
            "lines_removed": result.get("lines_removed", 0),
            "pr_url": pr_url,
            "terminal": True,
        },
        "warnings": [],
        "next_suggested_tools": [],
    }


def _mark_patch_applied(session_id: str, *, applied: Any) -> None:
    """Stamp the SessionPatch node's `applied` field; tolerate absence."""
    g = get_store()
    rows = g.query(
        "MATCH (p:SessionPatch {session_id: $sid}) RETURN p",
        params={"sid": session_id},
    )
    if not rows:
        return
    p = rows[0].get("p", rows[0]) if isinstance(rows[0], dict) else None
    if not isinstance(p, dict):
        return
    props = p.get("properties") or p.get("payload") or p
    if isinstance(props, str):
        import json
        try:
            props = json.loads(props)
        except Exception:
            return
    if not isinstance(props, dict):
        return
    props["applied"] = applied
    if applied:
        props["applied_at"] = ss.now_epoch()
    g.upsert_node(f"session-patch/{session_id}", props, label="SessionPatch")
