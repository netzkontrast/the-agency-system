"""`mcp__jules_dispatch` — create a new Jules session for a task brief.

Phase 03 entry handler. Resolves the GitHub repo to an opaque Jules
source name, calls `jules_create`, and writes the resulting session id
into the ontology as a `JulesSession` node in state ``DISPATCHED``.

Required inputs:
    prompt: Natural-language task brief.
    owner:  GitHub owner / org.
    repo:   Repository name.

Optional:
    branch: Starting branch (default "main").
    title:  Human-readable session title.
    require_plan_approval: Defaults True so phase 04 has something to
        approve; set False only when the caller wants Jules to skip the
        planning checkpoint.
"""

from __future__ import annotations

from typing import Any, Dict

from context._shared import error_codes
from jules_mcp import server as jules_api

from . import _session_state as ss


def handle(**kwargs) -> Dict[str, Any]:
    prompt = kwargs.get("prompt")
    owner = kwargs.get("owner")
    repo = kwargs.get("repo")
    branch = kwargs.get("branch", "main")
    title = kwargs.get("title", "")
    require_plan_approval = bool(kwargs.get("require_plan_approval", True))

    if not prompt or not owner or not repo:
        return ss.err_envelope(
            error_codes.HANDLER_BAD_SIGNATURE,
            "dispatch requires prompt, owner, repo",
        )

    try:
        src = jules_api.jules_resolve_source(owner=owner, repo=repo)
    except Exception as exc:
        return ss.err_envelope(error_codes.JULES_API_ERROR, f"jules_resolve_source raised: {exc!r}")

    if not isinstance(src, dict) or src.get("error") or not src.get("source"):
        msg = src.get("error") if isinstance(src, dict) else "non-dict source response"
        return ss.err_envelope(error_codes.JULES_SOURCE_UNRESOLVED, str(msg))

    try:
        result = jules_api.jules_create(
            prompt=prompt,
            source=src["source"],
            starting_branch=branch,
            title=title,
            require_plan_approval=require_plan_approval,
        )
    except Exception as exc:
        return ss.err_envelope(error_codes.JULES_DISPATCH_FAILED, f"jules_create raised: {exc!r}")

    if not isinstance(result, dict) or result.get("error") or not (result.get("id") or result.get("name")):
        return ss.err_envelope(
            error_codes.JULES_DISPATCH_FAILED,
            str(result.get("error", "jules_create returned no session id")),
        )

    sid = result.get("id") or result["name"].rsplit("/", 1)[-1]
    payload = ss.write_session(
        sid,
        state="DISPATCHED",
        jules_state=result.get("state"),
        title=title or prompt[:80],
        owner=owner,
        repo=repo,
        branch=branch,
        prompt=prompt,
        url=result.get("url", ""),
        created_at=ss.now_epoch(),
        plan_approved_at=None,
        completed_at=None,
        verified_at=None,
        branch_on_remote=None,
        pr_url=None,
        patch_bytes=None,
        patch_files=None,
        last_error=None,
    )

    return {
        "ok": True,
        "data": {
            "session_id": sid,
            "state": payload["state"],
            "jules_state": payload.get("jules_state"),
            "url": payload.get("url", ""),
        },
        "warnings": [],
        "next_suggested_tools": ["mcp__jules_await_plan"],
    }
