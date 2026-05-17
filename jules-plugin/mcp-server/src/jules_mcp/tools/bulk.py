from fastmcp import FastMCP
from ..api import _paginate, _request, _short_id
from ..trim import apply_list_trim

def jules_status_all(page_size: int = 100, max_pages: int = 20, fields: str = "id,state,title") -> dict:
    """Bulk status: returns a compact dict of every session's current state.

    Walks nextPageToken up to max_pages so accounts with more than
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
            "state": s.get("state") or "STATE_UNSPECIFIED",
            "title": s.get("title") or ""
        }
        entry.update(s) # so we can extract other fields
        
        trimmed_entry = apply_list_trim([entry], fields)[0]
        
        st = entry["state"]
        if st not in by_state:
            by_state[st] = []
        by_state[st].append(trimmed_entry)
        all_s.append(trimmed_entry)
        
    return {
        "by_state": by_state,
        "sessions": all_s,
        "pages_scanned": pages,
        "truncated": truncated
    }

def jules_approve(session_id: str) -> dict:
    """Approve the plan on a session that is in AWAITING_PLAN_APPROVAL.
    Internal helper for jules_approve_awaiting."""
    sid = _short_id(session_id)
    _request("POST", f"/v1alpha/sessions/{sid}:approvePlan", body={})
    return {"ok": True, "session_id": sid}

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

def register_bulk_tools(mcp: FastMCP) -> None:
    mcp.tool()(jules_status_all)
    mcp.tool()(jules_approve_awaiting)
    mcp.tool()(jules_quota)
