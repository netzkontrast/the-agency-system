#!/usr/bin/env python3
"""
FastMCP server for the Google Jules asynchronous coding agent.

Exposes the Jules REST API as MCP tools so an orchestrating LLM can drive
session lifecycles directly without log-tailing or shell glue. Reads
JULES_API_KEY from the environment; never logs it.

Tools (one per Jules action plus a few ergonomic compounds):

  jules_create        — start a new session
  jules_list          — list sessions (paginated)
  jules_get           — get a single session by id
  jules_activities    — list activities for a session (filtered, paginated)
  jules_plan          — fetch the latest planGenerated activity, rendered
  jules_approve       — approve a pending plan
  jules_message       — send a user message to a session
  jules_stop          — NOT SUPPORTED upstream; returns an explanatory error
  jules_patch         — extract the unified-diff patch from a completed session
  jules_status_all    — bulk: get every active session's state in one call
  jules_approve_awaiting — bulk: approve every session currently AWAITING_PLAN_APPROVAL
  jules_resolve_source — look up the opaque sources/{id} for a GitHub org/repo

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


class JulesAPIError(RuntimeError):
    """Raised when the Jules REST API returns a non-2xx response.

    Carries the HTTP status code so callers can react to specific cases
    (e.g. 404 → 'session not found', not 'unknown error') instead of
    string-matching the message.
    """

    def __init__(self, status: int, message: str, body: str = ""):
        super().__init__(message)
        self.status = status
        self.body = body


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
        raise JulesAPIError(e.code, msg, err_body) from None


def _translate_http_error(code: int, body: str) -> str:
    mapping = {
        400: "400 Bad Request — malformed payload. Body: ",
        401: "401 Unauthorized — JULES_API_KEY rejected. Re-export the key.",
        403: "403 Permission Denied — Jules cannot access the source. Connect the GitHub repo via the Jules GitHub app.",
        404: "404 Not Found — resource does not exist.",
        405: "405 Method Not Allowed — endpoint exists but does not accept this verb.",
        409: "409 Conflict — illegal state transition. Check current session state first.",
        429: "429 Quota Exceeded — pause polling and check billing/quota.",
    }
    if 500 <= code < 600:
        return f"5xx Server Error ({code}) — retryable. Body: {body[:300]}"
    base = mapping.get(code, f"HTTP {code}")
    if code == 400 and body:
        return base + body[:500]
    return base


def _paginate(path: str, params: dict, max_pages: int = 50) -> tuple[list[dict], str, int, bool]:
    """Walk pageToken across a list endpoint and concatenate the first array
    field in the response. Returns (items, last_page_token, pages_scanned, truncated).

    Stops early when nextPageToken is empty or max_pages is reached.
    """
    items: list[dict] = []
    token = ""
    pages = 0
    truncated = False
    array_key: str | None = None
    while pages < max_pages:
        q = dict(params)
        if token:
            q["pageToken"] = token
        sep = "&" if "?" in path else "?"
        raw = _request("GET", f"{path}{sep}{urllib.parse.urlencode(q)}")
        pages += 1
        if array_key is None:
            for k, v in raw.items():
                if isinstance(v, list):
                    array_key = k
                    break
            if array_key is None:
                break
        items.extend(raw.get(array_key, []) or [])
        token = raw.get("nextPageToken", "")
        if not token:
            return items, "", pages, False
    truncated = bool(token)
    return items, token, pages, truncated


def _short_id(name_or_id: str) -> str:
    """Accept 'sessions/123' or '123' and return '123'."""
    return name_or_id.rsplit("/", 1)[-1]


def _coerce_source(source: str) -> str:
    """Translate a user-supplied source string into the opaque form Jules expects.

    Accepts:
      - 'sources/<opaque>'              → returned unchanged (correct form)
      - 'owner/repo'                    → resolved via sources.list
      - 'sources/github/owner/repo'     → owner/repo extracted, resolved
      - 'https://github.com/owner/repo' → owner/repo extracted, resolved

    Raises JulesAPIError-like RuntimeError when no matching connected source
    is found, so the caller gets an actionable message instead of a 400 from
    the upstream API.
    """
    s = (source or "").strip()
    if not s:
        raise RuntimeError(
            "source is required. Pass 'sources/<id>', 'owner/repo', or a "
            "GitHub URL; use jules_resolve_source to look it up first."
        )
    if s.startswith("sources/") and s.count("/") == 1:
        return s
    owner: str | None = None
    repo: str | None = None
    if s.startswith("sources/github/"):
        rest = s[len("sources/github/"):]
        if rest.count("/") == 1:
            owner, repo = rest.split("/", 1)
    elif "github.com" in s:
        path = s.split("github.com", 1)[1].lstrip(":/").rstrip("/")
        if path.endswith(".git"):
            path = path[:-4]
        parts = path.split("/")
        if len(parts) >= 2:
            owner, repo = parts[0], parts[1]
    elif "/" in s and not s.startswith("sources/"):
        parts = s.split("/")
        if len(parts) == 2:
            owner, repo = parts
    if owner and repo:
        resolved = _resolve_github_source(owner, repo)
        if "error" in resolved:
            raise RuntimeError(resolved["error"])
        return resolved["source"]
    raise RuntimeError(
        f"could not parse source '{source}'. Expected 'sources/<id>', "
        "'owner/repo', or a github.com URL."
    )


mcp = FastMCP("jules")


def _resolve_github_source(owner: str, repo: str) -> dict:
    """Lookup the opaque sources/{id} for a GitHub owner/repo.

    Returns the same shape as the public tool wrapper below.
    """
    items, _, _, _ = _paginate("/v1alpha/sources", {"pageSize": 100}, max_pages=10)
    for s in items:
        gh = s.get("githubRepo") or {}
        if gh.get("owner") == owner and gh.get("repo") == repo:
            return {
                "source": s.get("name", ""),
                "github": {"owner": owner, "repo": repo},
            }
    return {
        "error": (
            f"no Jules source connected for github.com/{owner}/{repo}. "
            "Connect the repository via the Jules GitHub app, then retry."
        )
    }


@mcp.tool()
def jules_resolve_source(owner: str, repo: str) -> dict:
    """Resolve a GitHub owner/repo to its opaque Jules source resource name.

    The Jules API uses opaque source IDs of the form `sources/{id}`; the
    composition is NOT documented and is not `sources/github/{owner}/{repo}`.
    The only safe way to obtain the right name is to list `sources` and
    match on `githubRepo.owner` and `githubRepo.repo`.

    Args:
        owner: GitHub organisation or user (e.g. 'netzkontrast').
        repo: Repository name (e.g. 'the-agency-system').

    Returns:
        {"source": "sources/<id>", "github": {"owner": ..., "repo": ...}}
        or {"error": "no matching source connected to Jules"}.
    """
    return _resolve_github_source(owner, repo)


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
        source: Either an opaque Jules source name 'sources/<id>' OR a
            GitHub 'owner/repo' shorthand which will be resolved via
            sources.list. Slash-delimited 'sources/github/owner/repo'
            forms are NOT valid Jules source names and will be rejected
            by the upstream API.
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
    resolved_source = _coerce_source(source)
    body: dict[str, Any] = {
        "prompt": prompt,
        "sourceContext": {
            "source": resolved_source,
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


# Keys on an Activity that are NOT the polymorphic event-type field. Any of
# these can co-occur with the actual event (planGenerated, agentMessaged,
# sessionFailed, …) and must NOT be mistaken for the event kind.
_ACTIVITY_META_KEYS = {
    "name", "id", "createTime", "updateTime", "originator",
    "description", "artifacts",
}

# The canonical Activity.activity oneof per the Jules v1alpha schema.
_ACTIVITY_KINDS = {
    "agentMessaged", "userMessaged", "planGenerated", "planApproved",
    "progressUpdated", "sessionCompleted", "sessionFailed",
}


def _activity_kind(a: dict) -> str:
    """Pick the activity's event kind, preferring known oneof members over
    arbitrary metadata fields. Falls back to the first unknown key only when
    no canonical kind matches."""
    for k in _ACTIVITY_KINDS:
        if k in a:
            return k
    for k in a.keys():
        if k not in _ACTIVITY_META_KEYS:
            return k
    return "unknown"


@mcp.tool()
def jules_activities(
    session_id: str,
    page_size: int = 10,
    only_kinds: str = "",
    page_token: str = "",
) -> dict:
    """List activities for a session. Aggressively filtered.

    Args:
        session_id: The session id.
        page_size: 1..100, default 10.
        only_kinds: Comma-separated activity kinds to keep, e.g.
            'planGenerated,agentMessaged,sessionFailed'. Empty = all kinds.
        page_token: Pagination cursor from a previous response's nextPageToken.

    Returns: {"activities": [...], "nextPageToken": "..."} — each entry is
    trimmed to {id, originator, kind, summary} so context isn't blown.
    """
    sid = _short_id(session_id)
    q: dict[str, Any] = {"pageSize": max(1, min(page_size, 100))}
    if page_token:
        q["pageToken"] = page_token
    qs = urllib.parse.urlencode(q)
    raw = _request("GET", f"/v1alpha/sessions/{sid}/activities?{qs}")
    wanted = {k.strip() for k in only_kinds.split(",") if k.strip()}
    out: list[dict] = []
    for a in raw.get("activities", []) or []:
        kind = _activity_kind(a)
        if wanted and kind not in wanted:
            continue
        summary = _summarize_activity_payload(kind, a.get(kind), a)
        out.append({
            "id": _short_id(a.get("name", "")),
            "originator": a.get("originator"),
            "kind": kind,
            "summary": summary,
        })
    return {"activities": out, "nextPageToken": raw.get("nextPageToken", "")}


def _summarize_activity_payload(kind: str, payload: Any, activity: dict | None = None) -> str:
    if kind == "planGenerated" and isinstance(payload, dict):
        plan = payload.get("plan") or {}
        steps = plan.get("steps") or []
        if not steps:
            return "(empty plan)"
        return "; ".join(f"{s.get('title', '?')}" for s in steps[:6])
    if kind == "agentMessaged" and isinstance(payload, dict):
        text = payload.get("agentMessage") or ""
        return (text[:300] + "…") if len(text) > 300 else text
    if kind == "userMessaged" and isinstance(payload, dict):
        text = payload.get("userMessage") or ""
        return (text[:300] + "…") if len(text) > 300 else text
    if kind == "sessionFailed" and isinstance(payload, dict):
        return payload.get("reason") or "(no reason given)"
    if kind == "sessionCompleted":
        return "session completed"
    if kind == "planApproved":
        return "plan approved"
    if kind == "progressUpdated" and isinstance(payload, dict):
        title = payload.get("title") or ""
        desc = payload.get("description") or ""
        return f"{title}: {desc}".strip(": ") if (title or desc) else "progress"
    if activity is not None:
        arts = activity.get("artifacts")
        if isinstance(arts, list) and arts:
            return f"+ {len(arts)} artifact(s)"
    return ""


@mcp.tool()
def jules_plan(session_id: str, max_pages: int = 5) -> dict:
    """Fetch the most recent planGenerated activity, fully rendered.

    Use this when a session is in AWAITING_PLAN_APPROVAL and you need to
    show the plan to the user before calling jules_approve.

    The Jules activities endpoint does not document a sort order, so we
    paginate up to ``max_pages`` and pick the planGenerated activity with
    the largest ``createTime``. Multi-revision sessions therefore see the
    latest plan, not a stale one.

    Returns: {"steps": [{"title": ..., "description": ...}, "create_time": "..."}
    or {"error": "no plan found"}.
    """
    sid = _short_id(session_id)
    items, _, _, _ = _paginate(
        f"/v1alpha/sessions/{sid}/activities",
        {"pageSize": 100},
        max_pages=max_pages,
    )
    best: dict | None = None
    best_time = ""
    for a in items:
        pg = a.get("planGenerated")
        if not pg:
            continue
        ct = a.get("createTime", "")
        if best is None or ct > best_time:
            best = pg
            best_time = ct
    if best is None:
        return {"error": "no planGenerated activity found"}
    plan = (best.get("plan") or {})
    steps = [
        {"title": s.get("title", ""), "description": s.get("description", "")}
        for s in (plan.get("steps") or [])
    ]
    return {"steps": steps, "create_time": best_time}


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
    """Attempt to stop a Jules session.

    The Jules REST API (v1alpha) does NOT expose a delete/cancel/stop method
    on the sessions resource — only create/get/list/approvePlan/sendMessage
    are documented. There is therefore no way to terminate a running session
    via the API. The session can transition to PAUSED state, but no public
    method to trigger that pause exists.

    Returns an explanatory error so callers do not silently send an
    unsupported request to the upstream API.
    """
    sid = _short_id(session_id)
    return {
        "error": "unsupported",
        "session_id": sid,
        "message": (
            "The Jules v1alpha API does not support session cancellation. "
            "If you must intervene, use jules_message to instruct the agent "
            "to stop and leave changes uncommitted, or wait for the session "
            "to reach a terminal state (COMPLETED / FAILED)."
        ),
    }


def _fetch_patch(sid: str, max_pages: int = 5) -> dict:
    """Internal: returns {"patch": str, "base_commit": str, "suggested_commit_message": str}
    or raises RuntimeError.

    Patches live as activity ARTIFACTS, not in `Session.outputs[]` (which
    carries the PR resource, when auto_create_pr is set). Walk activities,
    look for `artifacts[].changeSet.gitPatch.unidiffPatch`, and return the
    newest patch by ``createTime``.
    """
    items, _, _, _ = _paginate(
        f"/v1alpha/sessions/{sid}/activities",
        {"pageSize": 100},
        max_pages=max_pages,
    )
    best: dict | None = None
    best_time = ""
    for a in items:
        artifacts = a.get("artifacts") or []
        for art in artifacts:
            cs = art.get("changeSet") or {}
            gp = cs.get("gitPatch") or {}
            patch = gp.get("unidiffPatch")
            if not patch:
                continue
            ct = a.get("createTime", "")
            if best is None or ct > best_time:
                best = {
                    "patch": patch,
                    "base_commit": gp.get("baseCommitId", ""),
                    "suggested_commit_message": gp.get("suggestedCommitMessage", ""),
                }
                best_time = ct
    if best is not None:
        return best
    # Provide a useful diagnostic by checking session state.
    try:
        s = _request("GET", f"/v1alpha/sessions/{sid}")
        state = s.get("state") or "UNKNOWN"
    except JulesAPIError:
        state = "UNKNOWN"
    raise RuntimeError(
        f"no patch artifact found in activities (session state={state})"
    )


def _parse_diff_header_b_path(line: str) -> str | None:
    """Extract the b-side path from a `diff --git a/X b/Y` header.

    Handles git's two header forms:
      - unquoted:  diff --git a/path/to/file b/path/to/file
      - quoted:    diff --git "a/path with spaces" "b/path with spaces"
    Returns the file path with the `b/` (or `"b/`) prefix stripped, or None
    if the header is malformed.
    """
    body = line[len("diff --git "):].rstrip("\n")
    # Quoted form: both halves are double-quoted, possibly with C-escapes.
    if body.startswith('"'):
        end = 1
        while end < len(body):
            if body[end] == "\\":
                end += 2
                continue
            if body[end] == '"':
                break
            end += 1
        if end >= len(body):
            return None
        b_part = body[end + 1:].lstrip()
        if not b_part.startswith('"'):
            return None
        b_end = 1
        while b_end < len(b_part):
            if b_part[b_end] == "\\":
                b_end += 2
                continue
            if b_part[b_end] == '"':
                break
            b_end += 1
        if b_end >= len(b_part):
            return None
        inner = b_part[1:b_end]
        return inner[2:] if inner.startswith("b/") else inner
    parts = body.split(" ")
    if len(parts) < 2:
        return None
    p = parts[-1]
    return p[2:] if p.startswith("b/") else p


def _parse_diff_metadata(patch: str) -> dict:
    """Count files touched and added/removed lines from a unidiff. Stdlib only."""
    files: list[str] = []
    added = 0
    removed = 0
    for line in patch.splitlines():
        if line.startswith("diff --git "):
            p = _parse_diff_header_b_path(line)
            if p:
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
                p = _parse_diff_header_b_path(line.rstrip("\n")) or ""
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
def jules_status_all(page_size: int = 100, max_pages: int = 20) -> dict:
    """Bulk status: returns a compact dict of every session's current state.

    Walks ``nextPageToken`` up to ``max_pages`` so accounts with more than
    100 sessions get a complete picture rather than a silently-truncated
    first page.

    Returns: {"by_state": {"AWAITING_PLAN_APPROVAL": [...], ...},
              "sessions": [{"id":..., "state":..., "title":...}, ...],
              "pages_scanned": int, "truncated": bool}.
    """
    items, _, pages, truncated = _paginate(
        "/v1alpha/sessions",
        {"pageSize": max(1, min(page_size, 100))},
        max_pages=max_pages,
    )
    by_state: dict[str, list[dict]] = {}
    all_s: list[dict] = []
    for s in items:
        entry = {
            "id": s.get("id") or _short_id(s.get("name", "")),
            "state": s.get("state"),
            "title": s.get("title", ""),
            "url": s.get("url", ""),
        }
        all_s.append(entry)
        by_state.setdefault(entry["state"] or "STATE_UNSPECIFIED", []).append(entry)
    return {
        "by_state": by_state,
        "sessions": all_s,
        "pages_scanned": pages,
        "truncated": truncated,
    }


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
    carries a `createTime` (UTC ISO-8601), so we paginate sessions and
    count those created since today's UTC midnight.

    The Jules sessions.list API does NOT document a sort order, so this
    function does not assume one — it scans every page up to ``max_pages``
    and filters by date. ``truncated=true`` in the response means more
    pages exist than were scanned and the count may be incomplete.

    A running session still occupies its slot for the day — there is no
    way to reclaim a slot, and the Jules API does not expose a stop
    method. Extend existing sessions via ``jules_message`` rather than
    creating new ones for related follow-up work.

    Args:
        daily_limit: Quota assumed for the account (default 100).
        max_pages: Safety cap on pagination (default 5 = up to 500
            sessions scanned).

    Returns:
        {
          "daily_limit": int,
          "used_today": int,                   # all states
          "remaining_today": int,
          "active_today": int,                 # non-terminal — still useful
          "by_state_today": {STATE: count},
          "today_utc": "YYYY-MM-DD",
          "newest_today_id": str | None,       # newest by createTime among today's sessions
          "pages_scanned": int,
          "truncated": bool                    # true if more pages exist
        }
    """
    import datetime
    today = datetime.datetime.now(datetime.timezone.utc).date().isoformat()
    today_prefix = today  # ISO-8601 createTime strings start with YYYY-MM-DD

    items, _, pages, truncated = _paginate(
        "/v1alpha/sessions",
        {"pageSize": 100},
        max_pages=max_pages,
    )

    NON_TERMINAL = {
        "QUEUED", "PLANNING", "IN_PROGRESS",
        "AWAITING_PLAN_APPROVAL", "AWAITING_USER_FEEDBACK",
        "PAUSED", "STATE_UNSPECIFIED",
    }

    used = 0
    by_state: dict[str, int] = {}
    newest_today: tuple[str, str | None] = ("", None)
    for s in items:
        ct = s.get("createTime", "")
        if not ct.startswith(today_prefix):
            continue
        used += 1
        st = s.get("state") or "STATE_UNSPECIFIED"
        by_state[st] = by_state.get(st, 0) + 1
        if ct > newest_today[0]:
            sid = s.get("id") or _short_id(s.get("name", ""))
            newest_today = (ct, sid)

    active = sum(by_state.get(st, 0) for st in NON_TERMINAL)
    return {
        "daily_limit": daily_limit,
        "used_today": used,
        "remaining_today": max(0, daily_limit - used),
        "active_today": active,
        "by_state_today": by_state,
        "today_utc": today,
        "newest_today_id": newest_today[1],
        "pages_scanned": pages,
        "truncated": truncated,
    }


if __name__ == "__main__":
    _log(f"starting jules-mcp; base={BASE_URL}; key={'set' if os.environ.get('JULES_API_KEY') else 'MISSING'}")
    mcp.run()
