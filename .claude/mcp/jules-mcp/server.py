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


try:
    _mcp_dir = os.path.dirname(os.path.abspath(__file__))
    _jules_skills_dir = os.path.normpath(os.path.join(_mcp_dir, "..", "..", "skills", "jules"))
    sys.path.insert(0, _jules_skills_dir)
    import sessions_state
except ImportError as e:
    sessions_state = None
    _log(f"Could not import sessions_state: {e}")


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
    alias: str = "",
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

    resp = _request("POST", "/v1alpha/sessions", body)

    if sessions_state is not None:
        try:
            new_id = resp.get("id") or _short_id(resp.get("name", ""))
            sessions_state.register_session(
                id=new_id,
                title=title,
                source=source,
                branch=starting_branch,
                alias=(alias or None),
                url=resp.get("url", ""),
                status=resp.get("state")
            )
        except Exception as e:
            _log(f"Failed to register session locally: {e}")

    return resp


@mcp.tool()
def jules_resolve_alias(name_or_id: str) -> dict:
    """Resolve a session alias or id to its canonical session id.

    Args:
        name_or_id: The alias or id to resolve.

    Returns: {"id": "..."} on success, {"error": "..."} on failure.
    """
    if sessions_state is None:
        return {"error": "sessions_state is unavailable"}

    resolved = sessions_state.resolve(name_or_id)
    if resolved:
        return {"id": resolved}
    return {"error": f"Session alias or id not found: {name_or_id}"}


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


def _fetch_patch(sid: str) -> dict:
    """Internal: returns {"patch": str, "base_commit": str, "suggested_commit_message": str}
    or raises RuntimeError. Used by the metadata, apply, and (expensive) raw tools below."""
    s = _request("GET", f"/v1alpha/sessions/{sid}")
    outputs = s.get("outputs") or []
    if not outputs:
        raise RuntimeError(
            f"session has no outputs yet (state={s.get('state')})"
        )
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
    raise RuntimeError("no unidiff patch found in outputs")


def _parse_diff_metadata(patch: str) -> dict:
    """Count files touched and added/removed lines from a unidiff. Stdlib only."""
    files: list[str] = []
    added = 0
    removed = 0
    for line in patch.splitlines():
        if line.startswith("diff --git "):
            # form: 'diff --git a/path b/path'
            parts = line.split(" ")
            if len(parts) >= 4:
                # Take the 'b/' side and strip the prefix
                p = parts[3]
                if p.startswith("b/"):
                    p = p[2:]
                files.append(p)
        elif line.startswith("+") and not line.startswith("+++"):
            added += 1
        elif line.startswith("-") and not line.startswith("---"):
            removed += 1
    return {"files": files, "lines_added": added, "lines_removed": removed}


@mcp.tool()
def jules_patch_summary(session_id: str) -> dict:
    """Token-cheap metadata about a session's patch — files touched and
    line counts. Does NOT return the diff body.

    Use this to decide whether to apply a patch or to display its size
    to a user before deciding next steps.

    Returns:
        {
          "files": ["path1", ...],
          "lines_added": int,
          "lines_removed": int,
          "patch_bytes": int,
          "base_commit": str,
          "suggested_commit_message": str
        }
    """
    sid = _short_id(session_id)
    try:
        data = _fetch_patch(sid)
    except RuntimeError as e:
        return {"error": str(e)}
    meta = _parse_diff_metadata(data["patch"])
    return {
        **meta,
        "patch_bytes": len(data["patch"]),
        "base_commit": data["base_commit"],
        "suggested_commit_message": data["suggested_commit_message"],
    }


@mcp.tool()
def jules_patch_apply(
    session_id: str,
    dry_run: bool = False,
    cwd: str = "",
    only_files: str = "",
    three_way: bool = False,
) -> dict:
    """Apply a session's patch to a local git working tree WITHOUT
    returning the diff body in the response. Token-efficient — only
    metadata flows back through the model.

    The patch is written to a tempfile, fed to `git apply`, then
    deleted. Patch content never enters the tool result.

    Args:
        session_id: The session whose patch to apply.
        dry_run: When True, runs `git apply --check` instead of applying.
            Use this to validate a patch before committing to it.
        cwd: Working directory to apply in. Empty = current process cwd.
            Must be a git working tree.
        only_files: Comma-separated list of file paths. When non-empty,
            the patch is filtered to only these files before applying
            (useful when you want one Jules patch's contribution to a
            shared file but not its other touches).
        three_way: When True, passes `--3way` to git apply for
            conflict-tolerant application.

    Returns:
        {
          "applied": bool,
          "dry_run": bool,
          "files": ["path1", ...],
          "lines_added": int,
          "lines_removed": int,
          "base_commit": str,
          "suggested_commit_message": str,
          "git_stderr": str,           # captured on failure for triage
        }
    """
    import shutil
    import subprocess
    import tempfile

    sid = _short_id(session_id)
    try:
        data = _fetch_patch(sid)
    except RuntimeError as e:
        return {"error": str(e), "applied": False}

    patch_text = data["patch"]
    meta = _parse_diff_metadata(patch_text)

    if only_files:
        wanted = {f.strip() for f in only_files.split(",") if f.strip()}
        filtered_chunks: list[list[str]] = []
        current: list[str] = []
        keep_current = False
        for line in patch_text.splitlines(keepends=True):
            if line.startswith("diff --git "):
                if current and keep_current:
                    filtered_chunks.append(current)
                current = [line]
                parts = line.split(" ")
                p = parts[3] if len(parts) >= 4 else ""
                p = p[2:] if p.startswith("b/") else p
                p = p.rstrip()
                keep_current = p in wanted
            else:
                current.append(line)
        if current and keep_current:
            filtered_chunks.append(current)
        if not filtered_chunks:
            return {
                "applied": False,
                "dry_run": dry_run,
                "files": [],
                "error": f"none of {sorted(wanted)} matched files in patch",
            }
        patch_text = "".join("".join(c) for c in filtered_chunks)
        meta = _parse_diff_metadata(patch_text)

    tmp = tempfile.NamedTemporaryFile(
        prefix="jules-patch-", suffix=".diff", delete=False, mode="w"
    )
    try:
        tmp.write(patch_text)
        tmp.close()
        cmd = ["git", "apply"]
        if dry_run:
            cmd.append("--check")
        if three_way:
            cmd.append("--3way")
        cmd.append(tmp.name)
        proc = subprocess.run(
            cmd,
            cwd=cwd or None,
            capture_output=True,
            text=True,
            timeout=60,
        )
        applied = proc.returncode == 0
        result = {
            "applied": applied and not dry_run,
            "dry_run": dry_run,
            "files": meta["files"],
            "lines_added": meta["lines_added"],
            "lines_removed": meta["lines_removed"],
            "base_commit": data["base_commit"],
            "suggested_commit_message": data["suggested_commit_message"],
        }
        if not applied:
            # Truncate to keep token cost bounded even on failure
            err = (proc.stderr or proc.stdout or "").strip()
            result["git_stderr"] = err[:800]
            result["applied"] = False
        return result
    finally:
        try:
            os.unlink(tmp.name)
        except Exception:
            pass


@mcp.tool()
def jules_patch(session_id: str, max_bytes: int = 60000) -> dict:
    """Return the unified-diff patch body for a session.

    TOKEN-EXPENSIVE — the diff lands in the model's context. Prefer
    `jules_patch_apply` (applies on disk, returns metadata only) or
    `jules_patch_summary` (metadata only, no body) for routine work.
    Only call this when you need to inspect or transform the patch
    inside the conversation.

    Args:
        max_bytes: Refuse to return diffs larger than this (default 60 KB
            ≈ 15-20K tokens). Set higher only when you've already
            checked `jules_patch_summary` and accepted the cost.

    Returns: {"patch": "<unidiff>", "base_commit": ..., "suggested_commit_message": ...}
    or {"error": "..."} when too large or unavailable.
    """
    sid = _short_id(session_id)
    try:
        data = _fetch_patch(sid)
    except RuntimeError as e:
        return {"error": str(e)}
    if len(data["patch"]) > max_bytes:
        return {
            "error": (
                f"patch is {len(data['patch'])} bytes, exceeds max_bytes={max_bytes}. "
                "Use jules_patch_apply (no body returned) or raise max_bytes."
            )
        }
    return data


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


@mcp.tool()
def jules_quota(daily_limit: int = 100, max_pages: int = 5) -> dict:
    """Estimate how many Jules sessions you have left for today.

    Jules enforces a per-account daily session quota (default 100). The
    API does not expose remaining quota directly, but every session
    carries a `createTime` (UTC ISO-8601), so we paginate sessions
    newest-first and count those created since today's UTC midnight.

    A running session still occupies its slot for the day — stopping it
    early does NOT reclaim the slot. So the right way to be efficient
    is to (a) extend an existing session via `jules_message` rather
    than creating a new one for related follow-up work, and (b) avoid
    `jules_stop` unless the session is genuinely off-track.

    Args:
        daily_limit: Quota assumed for the account (default 100).
        max_pages: Safety cap on pagination (default 5 = up to 500
            sessions scanned). Today's sessions are typically on the
            first 1-2 pages.

    Returns:
        {
          "daily_limit": int,
          "used_today": int,                   # all states
          "remaining_today": int,
          "active_today": int,                 # non-terminal — still useful
          "by_state_today": {STATE: count},
          "today_utc": "YYYY-MM-DD",
          "newest_today_id": str | None,       # the most recently created session today
          "pages_scanned": int,
          "truncated": bool                    # true if max_pages was hit
        }
    """
    import datetime
    today = datetime.datetime.now(datetime.timezone.utc).date().isoformat()
    today_prefix = today  # ISO-8601 createTime strings start with YYYY-MM-DD

    used = 0
    by_state: dict[str, int] = {}
    newest_today_id: str | None = None
    token = ""
    pages = 0
    truncated = False

    NON_TERMINAL = {
        "QUEUED", "PLANNING", "IN_PROGRESS",
        "AWAITING_PLAN_APPROVAL", "AWAITING_USER_FEEDBACK",
        "PAUSED", "STATE_UNSPECIFIED",
    }

    while pages < max_pages:
        q = {"pageSize": 100}
        if token:
            q["pageToken"] = token
        qs = urllib.parse.urlencode(q)
        raw = _request("GET", f"/v1alpha/sessions?{qs}")
        pages += 1
        sessions = raw.get("sessions", []) or []

        # Sessions arrive newest-first; once we drop below today we can stop
        saw_older = False
        for s in sessions:
            ct = s.get("createTime", "")
            if not ct.startswith(today_prefix):
                saw_older = True
                continue
            used += 1
            st = s.get("state") or "STATE_UNSPECIFIED"
            by_state[st] = by_state.get(st, 0) + 1
            if newest_today_id is None:
                newest_today_id = s.get("id") or _short_id(s.get("name", ""))

        token = raw.get("nextPageToken", "")
        if not token or saw_older:
            break
    else:
        truncated = True  # exited via while-condition (pages >= max_pages)

    active = sum(by_state.get(st, 0) for st in NON_TERMINAL)
    return {
        "daily_limit": daily_limit,
        "used_today": used,
        "remaining_today": max(0, daily_limit - used),
        "active_today": active,
        "by_state_today": by_state,
        "today_utc": today,
        "newest_today_id": newest_today_id,
        "pages_scanned": pages,
        "truncated": truncated,
    }


if __name__ == "__main__":
    _log(f"starting jules-mcp; base={BASE_URL}; key={'set' if os.environ.get('JULES_API_KEY') else 'MISSING'}")
    mcp.run()
