from typing import Any
import importlib.util
import os
import sys
import urllib.parse
from pathlib import Path
from fastmcp import FastMCP
from agency_mcp.lib.codemode.projection import apply_view
from ._shared import _request, _paginate, _short_id
from .source import _coerce_source, _resolve_github_source
from .trim import apply_fields, apply_summary, apply_list_trim


def _log(msg: str) -> None:
    print(f"[jules-mcp] {msg}", file=sys.stderr, flush=True)


def _load_sessions_state():
    """3-tier loader: installed package → CLAUDE_PLUGIN_ROOT/lib → relative."""
    try:
        from jules_plugin.lib import sessions_state as ss  # type: ignore
        return ss
    except ImportError:
        pass
    root = os.environ.get("CLAUDE_PLUGIN_ROOT")
    candidates = []
    if root:
        candidates.append(os.path.join(root, "lib", "sessions_state.py"))

    # Path(__file__) is servers/agency-mcp/src/agency_mcp/handlers/jules/lifecycle.py
    # .parents[6] goes up to repo root
    repo_root = Path(__file__).resolve().parents[6]
    candidates.append(
        str(repo_root / "jules-plugin" / "lib" / "sessions_state.py")
    )

    for path in candidates:
        if os.path.exists(path):
            spec = importlib.util.spec_from_file_location("sessions_state", path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                return module
    _log("Could not locate sessions_state (tried jules_plugin.lib, CLAUDE_PLUGIN_ROOT, relative)")
    return None


sessions_state = _load_sessions_state()

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


@apply_view
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


@apply_view
def jules_get(session_id: str) -> dict:
    """Fetch a single Jules session's current state and metadata.

    Args:
        session_id: The numeric session id (or 'sessions/<id>').

    Returns: a dict with state, title, source, branch, url, outputs (if any).
    """
    sid = _short_id(session_id)
    s = _request("GET", f"/v1alpha/sessions/{sid}")
    raw_dict = {
        "id": s.get("id") or _short_id(s.get("name", "")),
        "state": s.get("state"),
        "title": s.get("title", ""),
        "source": (s.get("sourceContext") or {}).get("source"),
        "branch": ((s.get("sourceContext") or {}).get("githubRepoContext") or {}).get("startingBranch"),
        "url": s.get("url", ""),
        "has_outputs": bool(s.get("outputs")),
        "require_plan_approval": s.get("requirePlanApproval"),
    }
    return raw_dict


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


def jules_activities(session_id: str, page_size: int = 10, only_kinds: str = "", page_token: str = "", summary_only: bool = True) -> dict:
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
        if summary_only:
            out.append(apply_summary(a))
        else:
            out.append(a)
    return {"activities": out, "nextPageToken": raw.get("nextPageToken", "")}



def jules_plan(session_id: str, max_pages: int = 5, include_descriptions: bool = False) -> dict:
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
    steps = []
    for s in (plan.get("steps") or []):
        step = {"title": s.get("title", "")}
        if include_descriptions:
            step["description"] = s.get("description", "")
        steps.append(step)
    return {"steps": steps, "create_time": best_time}


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

def register_lifecycle_tools(mcp: FastMCP) -> None:
    mcp.tool(tags={"domain:jules"})(jules_resolve_source)
    mcp.tool(tags={"domain:jules"})(jules_create)
    mcp.tool(tags={"domain:jules"})(jules_list)
    mcp.tool(tags={"domain:jules"})(jules_get)
    mcp.tool(tags={"domain:jules"})(jules_activities)
    mcp.tool(tags={"domain:jules"})(jules_plan)
    mcp.tool(tags={"domain:jules"})(jules_approve)
    mcp.tool(tags={"domain:jules"})(jules_message)
    mcp.tool(tags={"domain:jules"})(jules_stop)
