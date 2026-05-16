#!/usr/bin/env python3
"""
FastMCP server for the Google Jules asynchronous coding agent.

Exposes the Jules REST API as MCP tools so an orchestrating LLM can drive
session lifecycles directly without log-tailing or shell glue. Reads
JULES_API_KEY from the environment; never logs it.

Tools (one per Jules action plus a few ergonomic compounds):

  jules_create        — start a new session
  jules_list          — list sessions
  jules_get           — get a single session by id
  jules_activities    — list activities for a session (filtered)
  jules_plan          — fetch the latest planGenerated activity, rendered
  jules_approve       — approve a pending plan
  jules_message       — send a user message to a session
  jules_stop          — delete a session
  jules_patch         — extract the unified-diff patch from a completed session
  jules_status_all    — bulk: get every active session's state in one call
  jules_approve_awaiting — bulk: approve every session currently AWAITING_PLAN_APPROVAL

stdio transport. Diagnostic logging goes to stderr so it never corrupts
the JSON-RPC stream on stdout.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from fastmcp import FastMCP

BASE_URL = os.environ.get("JULES_API_BASE_URL", "https://jules.googleapis.com")


def _log(msg: str) -> None:
    print(f"[jules-mcp] {msg}", file=sys.stderr, flush=True)


def _api_key() -> str:
    key = os.environ.get("JULES_API_KEY", "")
    if not key:
        raise RuntimeError(
            "JULES_API_KEY is not set. Export it in the shell that launched "
            "Claude Code, then restart the session."
        )
    return key


def _request(method: str, path: str, body: dict | None = None) -> dict:
    url = f"{BASE_URL}{path}"
    headers = {"x-goog-api-key": _api_key()}
    data: bytes | None = None
    if body is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        err_body = ""
        try:
            err_body = e.read().decode("utf-8")
        except Exception:
            pass
        msg = _translate_http_error(e.code, err_body)
        raise RuntimeError(msg) from None


def _translate_http_error(code: int, body: str) -> str:
    mapping = {
        400: "400 Bad Request — malformed payload. Body: ",
        401: "401 Unauthorized — JULES_API_KEY rejected. Re-export the key.",
        403: "403 Permission Denied — Jules cannot access the source. Connect the GitHub repo via the Jules GitHub app.",
        404: "404 Not Found — unknown session id.",
        409: "409 Conflict — illegal state transition. Check current session state first.",
        429: "429 Quota Exceeded — pause polling and check billing/quota.",
    }
    if 500 <= code < 600:
        return f"5xx Server Error ({code}) — retryable. Body: {body[:300]}"
    base = mapping.get(code, f"HTTP {code}")
    if code == 400 and body:
        return base + body[:500]
    return base


def _short_id(name_or_id: str) -> str:
    """Accept 'sessions/123' or '123' and return '123'."""
    return name_or_id.rsplit("/", 1)[-1]


mcp = FastMCP("jules")


@mcp.tool()
def jules_create(
    prompt: str,
    source: str,
    starting_branch: str,
    title: str = "",
    require_plan_approval: bool = True,
    auto_create_pr: bool = False,
) -> dict:
    """Create a new Jules session.

    Args:
        prompt: Natural language task description for the remote agent.
        source: GitHub source resource name, e.g. 'sources/github/org/repo'.
        starting_branch: Branch the agent should base its work on.
        title: Optional human-readable title for the session.
        require_plan_approval: When True (default and recommended), Jules halts
            at AWAITING_PLAN_APPROVAL until jules_approve is called. The
            backend appears to TIMEOUT and discard the session if approval
            never arrives, so callers must approve promptly.
        auto_create_pr: When True, Jules opens a real Pull Request on
            completion. When False (default), the patch comes back as a
            unified diff via jules_patch.

    Returns: the newly created session resource as a dict with id, state, title, url.
    """
    body: dict[str, Any] = {
        "prompt": prompt,
        "sourceContext": {
            "source": source,
            "githubRepoContext": {"startingBranch": starting_branch},
        },
        "requirePlanApproval": bool(require_plan_approval),
    }
    if title:
        body["title"] = title
    if auto_create_pr:
        body["automationMode"] = "AUTO_CREATE_PR"
    return _request("POST", "/v1alpha/sessions", body)


@mcp.tool()
def jules_list(page_size: int = 20, page_token: str = "") -> dict:
    """List Jules sessions on the account.

    Args:
        page_size: 1..100 (default 20).
        page_token: Pagination cursor from a previous response.

    Returns: {"sessions": [...], "nextPageToken": "..."} — sessions are
    trimmed to {id, state, title, url} for context-efficiency.
    """
    q = {"pageSize": max(1, min(page_size, 100))}
    if page_token:
        q["pageToken"] = page_token
    qs = urllib.parse.urlencode(q)
    raw = _request("GET", f"/v1alpha/sessions?{qs}")
    sessions = []
    for s in raw.get("sessions", []) or []:
        sessions.append({
            "id": s.get("id") or _short_id(s.get("name", "")),
            "state": s.get("state"),
            "title": s.get("title", ""),
            "url": s.get("url", ""),
        })
    return {"sessions": sessions, "nextPageToken": raw.get("nextPageToken", "")}


@mcp.tool()
def jules_get(session_id: str) -> dict:
    """Fetch a single Jules session's current state and metadata.

    Args:
        session_id: The numeric session id (or 'sessions/<id>').

    Returns: a dict with state, title, source, branch, url, outputs (if any).
    """
    sid = _short_id(session_id)
    s = _request("GET", f"/v1alpha/sessions/{sid}")
    return {
        "id": s.get("id") or _short_id(s.get("name", "")),
        "state": s.get("state"),
        "title": s.get("title", ""),
        "source": (s.get("sourceContext") or {}).get("source"),
        "branch": ((s.get("sourceContext") or {}).get("githubRepoContext") or {}).get(
            "startingBranch"
        ),
        "url": s.get("url", ""),
        "has_outputs": bool(s.get("outputs")),
        "require_plan_approval": s.get("requirePlanApproval"),
    }


@mcp.tool()
def jules_activities(session_id: str, page_size: int = 10, only_kinds: str = "") -> dict:
    """List activities for a session. Aggressively filtered.

    Args:
        session_id: The session id.
        page_size: 1..100, default 10.
        only_kinds: Comma-separated activity kinds to keep, e.g.
            'planGenerated,agentMessaged,artifacts'. Empty = all kinds.

    Returns: {"activities": [...], "nextPageToken": "..."} — each entry is
    trimmed to {id, originator, kind, summary} so context isn't blown.
    """
    sid = _short_id(session_id)
    q = {"pageSize": max(1, min(page_size, 100))}
    qs = urllib.parse.urlencode(q)
    raw = _request("GET", f"/v1alpha/sessions/{sid}/activities?{qs}")
    wanted = {k.strip() for k in only_kinds.split(",") if k.strip()}
    out: list[dict] = []
    for a in raw.get("activities", []) or []:
        meta_keys = {"name", "createTime", "originator", "id"}
        payload_keys = [k for k in a.keys() if k not in meta_keys]
        kind = payload_keys[0] if payload_keys else "unknown"
        if wanted and kind not in wanted:
            continue
        summary = _summarize_activity_payload(kind, a.get(kind))
        out.append({
            "id": _short_id(a.get("name", "")),
            "originator": a.get("originator"),
            "kind": kind,
            "summary": summary,
        })
    return {"activities": out, "nextPageToken": raw.get("nextPageToken", "")}


def _summarize_activity_payload(kind: str, payload: Any) -> str:
    if payload is None:
        return ""
    if kind == "planGenerated" and isinstance(payload, dict):
        plan = payload.get("plan") or {}
        steps = plan.get("steps") or []
        if not steps:
            return "(empty plan)"
        return "; ".join(f"{s.get('title', '?')}" for s in steps[:6])
    if kind == "agentMessaged" and isinstance(payload, dict):
        text = payload.get("agentMessage") or payload.get("message") or ""
        return (text[:300] + "…") if len(text) > 300 else text
    if kind == "userMessaged" and isinstance(payload, dict):
        text = payload.get("prompt") or payload.get("message") or ""
        return (text[:300] + "…") if len(text) > 300 else text
    if kind == "artifacts":
        return f"{len(payload)} artifact(s)" if isinstance(payload, list) else "1 artifact"
    if kind == "progressUpdated" and isinstance(payload, dict):
        return payload.get("title") or payload.get("status") or "progress"
    return ""


@mcp.tool()
def jules_plan(session_id: str) -> dict:
    """Fetch the most recent planGenerated activity, fully rendered.

    Use this when a session is in AWAITING_PLAN_APPROVAL and you need to
    show the plan to the user before calling jules_approve.

    Returns: {"steps": [{"title": ..., "description": ...}, ...]} or
    {"error": "no plan found"}.
    """
    sid = _short_id(session_id)
    raw = _request("GET", f"/v1alpha/sessions/{sid}/activities?pageSize=50")
    for a in raw.get("activities", []) or []:
        pg = a.get("planGenerated")
        if pg:
            plan = (pg.get("plan") or {})
            steps = []
            for s in plan.get("steps", []) or []:
                steps.append({
                    "title": s.get("title", ""),
                    "description": s.get("description", ""),
                })
            return {"steps": steps}
    return {"error": "no planGenerated activity found"}


@mcp.tool()
def jules_approve(session_id: str) -> dict:
    """Approve the plan on a session that is in AWAITING_PLAN_APPROVAL.

    The Jules backend appears to discard sessions whose plans are never
    approved (state ends up COMPLETED with empty outputs). Approve
    promptly after surfacing the plan.

    Returns: {"ok": true} on 2xx.
    """
    sid = _short_id(session_id)
    _request("POST", f"/v1alpha/sessions/{sid}:approvePlan", body={})
    return {"ok": True, "session_id": sid}


@mcp.tool()
def jules_message(session_id: str, prompt: str) -> dict:
    """Send a user message to a session — e.g. answer a question or
    request a plan revision.

    Args:
        session_id: The session id.
        prompt: The user-feedback text.

    Returns: {"ok": true} on 2xx.
    """
    sid = _short_id(session_id)
    _request("POST", f"/v1alpha/sessions/{sid}:sendMessage", body={"prompt": prompt})
    return {"ok": True, "session_id": sid}


@mcp.tool()
def jules_stop(session_id: str) -> dict:
    """Cancel and delete a Jules session. Destructive — confirm with the
    user first unless they used unambiguous cancel language.

    Returns: {"ok": true} on 2xx.
    """
    sid = _short_id(session_id)
    _request("DELETE", f"/v1alpha/sessions/{sid}")
    return {"ok": True, "session_id": sid}


@mcp.tool()
def jules_patch(session_id: str) -> dict:
    """Extract the unified-diff patch from a COMPLETED session's outputs.

    Returns: {"patch": "<unidiff>", "base_commit": "...", "suggested_commit_message": "..."}
    or {"error": "..."} if the session has no patch artifact.
    """
    sid = _short_id(session_id)
    s = _request("GET", f"/v1alpha/sessions/{sid}")
    outputs = s.get("outputs") or []
    if not outputs:
        return {"error": "session has no outputs yet (state="
                + str(s.get("state")) + ")"}
    for o in outputs:
        cs = o.get("changeSet") or {}
        gp = cs.get("gitPatch") or {}
        patch = gp.get("unidiffPatch")
        if patch:
            return {
                "patch": patch,
                "base_commit": gp.get("baseCommitId", ""),
                "suggested_commit_message": gp.get("suggestedCommitMessage", ""),
            }
    return {"error": "no unidiff patch found in outputs"}


@mcp.tool()
def jules_status_all(page_size: int = 100) -> dict:
    """Bulk status: returns a compact dict of every session's current state.

    Use this before approving/applying anything in a parallel workflow
    so the orchestrator has the full picture in one call rather than N.

    Returns: {"by_state": {"AWAITING_PLAN_APPROVAL": [...], ...},
              "sessions": [{"id":..., "state":..., "title":...}, ...]}.
    """
    raw = _request(
        "GET",
        f"/v1alpha/sessions?pageSize={max(1, min(page_size, 100))}",
    )
    by_state: dict[str, list[dict]] = {}
    all_s: list[dict] = []
    for s in raw.get("sessions", []) or []:
        entry = {
            "id": s.get("id") or _short_id(s.get("name", "")),
            "state": s.get("state"),
            "title": s.get("title", ""),
            "url": s.get("url", ""),
        }
        all_s.append(entry)
        by_state.setdefault(entry["state"] or "STATE_UNSPECIFIED", []).append(entry)
    return {"by_state": by_state, "sessions": all_s}


@mcp.tool()
def jules_approve_awaiting(only_titles_contain: str = "") -> dict:
    """Bulk-approve every session currently in AWAITING_PLAN_APPROVAL.

    Args:
        only_titles_contain: If non-empty, only approve sessions whose
            title contains this substring. Use for safety in shared
            accounts; leave empty to approve all.

    Returns: {"approved": ["id", ...], "skipped": ["id", ...], "errors": [{...}]}.
    """
    status = jules_status_all(page_size=100)
    awaiting = status["by_state"].get("AWAITING_PLAN_APPROVAL", [])
    approved: list[str] = []
    skipped: list[str] = []
    errors: list[dict] = []
    for s in awaiting:
        if only_titles_contain and only_titles_contain not in (s.get("title") or ""):
            skipped.append(s["id"])
            continue
        try:
            jules_approve(session_id=s["id"])
            approved.append(s["id"])
        except Exception as e:
            errors.append({"id": s["id"], "error": str(e)})
    return {"approved": approved, "skipped": skipped, "errors": errors}


if __name__ == "__main__":
    _log(f"starting jules-mcp; base={BASE_URL}; key={'set' if os.environ.get('JULES_API_KEY') else 'MISSING'}")
    mcp.run()
