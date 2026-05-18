import json
from typing import Any, Dict, Optional
from fastmcp import FastMCP
from session_log_mcp.db import get_conn

def summary_events(
    spec_id: Optional[str] = None,
    session_id: Optional[str] = None,
    since: Optional[str] = None
) -> str:
    """Summarize events from the session log."""
    conditions = []
    params = []

    if spec_id is not None:
        conditions.append("spec_id = ?")
        params.append(spec_id)
    if session_id is not None:
        conditions.append("session_id = ?")
        params.append(session_id)
    if since is not None:
        conditions.append("ts >= ?")
        params.append(since)

    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""

    counts_query = f"SELECT kind, COUNT(*) as count FROM events{where_clause} GROUP BY kind"
    latest_query = f"SELECT * FROM events{where_clause} ORDER BY ts DESC LIMIT 1"

    with get_conn() as conn:
        cursor = conn.cursor()

        cursor.execute(counts_query, params)
        counts_by_kind = {row["kind"]: row["count"] for row in cursor.fetchall()}

        total = sum(counts_by_kind.values())

        cursor.execute(latest_query, params)
        latest_row = cursor.fetchone()

        latest_event = dict(latest_row) if latest_row else None
        if latest_event:
            try:
                latest_event["payload"] = json.loads(latest_event["payload"])
            except json.JSONDecodeError:
                pass

    return json.dumps({
        "counts_by_kind": counts_by_kind,
        "latest_event": latest_event,
        "total": total
    })

def register(mcp: FastMCP) -> None:
    @mcp.tool(tags=["domain:agentic"])
    def session_log_summary(
        spec_id: Optional[str] = None,
        session_id: Optional[str] = None,
        since: Optional[str] = None
    ) -> str:
        """Summarize events from the session log."""
        return summary_events(spec_id, session_id, since)
