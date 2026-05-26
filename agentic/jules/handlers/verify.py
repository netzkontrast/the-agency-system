"""`mcp__jules_verify` — JULES_PROTOCOL §8 silent-fail check.

Phase 06 entry handler. A `state=COMPLETED` Jules session does NOT
guarantee work landed on origin — the session can be `COMPLETED` while
its patch sits locally and was never pushed. This handler queries the
patch-summary endpoint as a proxy for "did work happen?" and bumps the
local state accordingly:

* No patch (lines_added + lines_removed == 0)  → VERIFIED (with a
  warning that the session produced no diff). The COMPLETED label
  matches reality.
* Patch present                                → SILENT_FAIL — the
  session has work to land but verification cannot confirm a remote
  branch from inside the handler. Phase 07 (recover) picks it up.

The handler intentionally does NOT shell out to git or call GitHub —
that I/O lives in the recovery flow. Verify's job is to set the state
flag; recover does the integration work.

Required inputs:
    session_id: ID of an existing JulesSession node.

Optional:
    require_remote_branch: When True, the handler skips the patch
        heuristic entirely and writes branch_on_remote=False with state
        SILENT_FAIL. Caller (e.g. a verify skill invoked by a human) is
        responsible for setting branch_on_remote=True once they've
        confirmed origin via GitHub MCP.
"""

from __future__ import annotations

from typing import Any, Dict

from context._shared import error_codes
from jules_mcp import server as jules_api

from . import _session_state as ss


def handle(**kwargs) -> Dict[str, Any]:
    sid = kwargs.get("session_id")
    require_remote_branch = bool(kwargs.get("require_remote_branch", False))
    if not sid:
        return ss.err_envelope(error_codes.HANDLER_BAD_SIGNATURE, "verify requires session_id")

    session = ss.load_session(sid)
    if session is None:
        return ss.session_missing_envelope(sid)

    current_local = session.get("state", "DISPATCHED")
    if current_local != "COMPLETED":
        return ss.err_envelope(
            error_codes.SESSION_STATE_INVALID,
            f"verify expects state=COMPLETED, got {current_local}",
        )

    try:
        summary = jules_api.jules_patch_summary(sid)
    except Exception as exc:
        ss.write_session(sid, last_error=f"jules_patch_summary raised: {exc!r}")
        return ss.err_envelope(error_codes.PATCH_UNAVAILABLE, f"patch summary raised: {exc!r}")

    if not isinstance(summary, dict) or summary.get("error"):
        msg = summary.get("error") if isinstance(summary, dict) else "non-dict response"
        ss.write_session(sid, last_error=f"patch_summary: {msg}")
        return ss.err_envelope(error_codes.PATCH_UNAVAILABLE, str(msg))

    added = int(summary.get("lines_added", 0) or 0)
    removed = int(summary.get("lines_removed", 0) or 0)
    has_diff = (added + removed) > 0

    if require_remote_branch:
        # Caller asserts the remote-branch check itself; we mark as
        # silent-fail so recover runs and the human/skill can override.
        target = "SILENT_FAIL"
        ss.write_session(
            sid,
            state=target,
            verified_at=ss.now_epoch(),
            branch_on_remote=False,
            last_error=None,
        )
        return {
            "ok": True,
            "data": {
                "session_id": sid,
                "state": target,
                "branch_on_remote": False,
                "reason": "require_remote_branch=True; defer to recover",
            },
            "warnings": ["caller asked for remote-branch verification — recover phase will run"],
            "next_suggested_tools": ["mcp__jules_recover"],
        }

    if not has_diff:
        # No patch, nothing to land — accept the COMPLETED state at face value.
        ss.write_session(
            sid,
            state="VERIFIED",
            verified_at=ss.now_epoch(),
            branch_on_remote=True,
            last_error=None,
        )
        return {
            "ok": True,
            "data": {
                "session_id": sid,
                "state": "VERIFIED",
                "branch_on_remote": True,
                "patch_bytes": 0,
            },
            "warnings": ["session completed with no diff — nothing to land"],
            "next_suggested_tools": ["mcp__jules_integrate"],
        }

    # Patch present but we cannot confirm origin from here — silent-fail.
    ss.write_session(
        sid,
        state="SILENT_FAIL",
        verified_at=ss.now_epoch(),
        branch_on_remote=False,
        patch_bytes=int(summary.get("patch_bytes", 0) or 0),
        patch_files=len(summary.get("files", []) or []),
        last_error=None,
    )
    return {
        "ok": True,
        "data": {
            "session_id": sid,
            "state": "SILENT_FAIL",
            "branch_on_remote": False,
            "patch_bytes": int(summary.get("patch_bytes", 0) or 0),
            "patch_files": len(summary.get("files", []) or []),
        },
        "warnings": ["patch present but no remote branch confirmed — recover phase will run"],
        "next_suggested_tools": ["mcp__jules_recover"],
    }
