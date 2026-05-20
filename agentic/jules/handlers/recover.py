"""`mcp__jules_recover` — extract a silent-failed session's patch.

Phase 07 entry handler. Only runs on sessions in SILENT_FAIL state. The
real work is calling `jules_patch_summary` to record the patch metadata
on a `SessionPatch` ontology node, then advancing the session to
PATCH_EXTRACTED. Applying the patch (or opening a PR for it) is the
integrate handler's job.

The handler does NOT shell out to git. Patch application moved into
this row would couple the orchestration layer to a working tree, which
the harness deliberately keeps out. Integrate calls `jules_patch_apply`
when `apply=True` is requested.

Required inputs:
    session_id: ID of an existing JulesSession node in SILENT_FAIL.
"""

from __future__ import annotations

from typing import Any, Dict

from context import get_store
from context._shared import error_codes
from jules_mcp import server as jules_api

from . import _session_state as ss


def handle(**kwargs) -> Dict[str, Any]:
    sid = kwargs.get("session_id")
    if not sid:
        return ss.err_envelope(error_codes.HANDLER_BAD_SIGNATURE, "recover requires session_id")

    session = ss.load_session(sid)
    if session is None:
        return ss.session_missing_envelope(sid)

    current = session.get("state", "DISPATCHED")
    if current != "SILENT_FAIL":
        return ss.err_envelope(
            error_codes.SESSION_STATE_INVALID,
            f"recover expects state=SILENT_FAIL, got {current}",
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

    extracted_at = ss.now_epoch()
    patch_payload = {
        "session_id": sid,
        "files": summary.get("files", []) or [],
        "lines_added": int(summary.get("lines_added", 0) or 0),
        "lines_removed": int(summary.get("lines_removed", 0) or 0),
        "patch_bytes": int(summary.get("patch_bytes", 0) or 0),
        "base_commit": summary.get("base_commit", "") or "",
        "suggested_commit_message": summary.get("suggested_commit_message", "") or "",
        "extracted_at": extracted_at,
        "applied": None,
        "applied_at": None,
    }

    g = get_store()
    g.upsert_node(
        f"session-patch/{sid}",
        patch_payload,
        label="SessionPatch",
    )
    g.upsert_edge(
        f"session-patch/{sid}",
        ss.session_node_id(sid),
        {"role": "patch-for"},
        rel_type="DERIVED_FROM",
    )

    ss.write_session(
        sid,
        state="PATCH_EXTRACTED",
        patch_bytes=patch_payload["patch_bytes"],
        patch_files=len(patch_payload["files"]),
        last_error=None,
    )

    return {
        "ok": True,
        "data": {
            "session_id": sid,
            "state": "PATCH_EXTRACTED",
            "patch_bytes": patch_payload["patch_bytes"],
            "files": patch_payload["files"],
            "lines_added": patch_payload["lines_added"],
            "lines_removed": patch_payload["lines_removed"],
        },
        "warnings": [],
        "next_suggested_tools": ["mcp__jules_integrate"],
    }
