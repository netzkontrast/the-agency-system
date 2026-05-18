import json
from typing import Any, Dict, List, Optional
from fastmcp import FastMCP
from session_log_mcp.db import get_conn

def query_events(
    spec_id: Optional[str] = None,
    session_id: Optional[str] = None,
    kind: Optional[str] = None,
    since: Optional[str] = None,
    until: Optional[str] = None,
    limit: int = 100
) -> str:
    """Query events from the session log."""
    conditions = []
    params = []

    if spec_id is not None:
        conditions.append("spec_id = ?")
        params.append(spec_id)
    if session_id is not None:
        conditions.append("session_id = ?")
        params.append(session_id)
    if kind is not None:
        conditions.append("kind = ?")
        params.append(kind)
    if since is not None:
        conditions.append("ts >= ?")
        params.append(since)
    if until is not None:
        conditions.append("ts <= ?")
        params.append(until)

    where_clause = " AND ".join(conditions) if conditions else "1=1"
    query = f"SELECT * FROM events WHERE {where_clause} ORDER BY ts DESC LIMIT ?"
    params.append(limit)

    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()

        results = []
        for row in rows:
            result = dict(row)
            try:
                result["payload"] = json.loads(result["payload"])
            except json.JSONDecodeError:
                pass
            results.append(result)

    return json.dumps(results)

def register(mcp: FastMCP) -> None:
    @mcp.tool(tags=["domain:agentic"])
    def session_log_query(
        spec_id: Optional[str] = None,
        session_id: Optional[str] = None,
        kind: Optional[str] = None,
        since: Optional[str] = None,
        until: Optional[str] = None,
        limit: int = 100
    ) -> str:
        """Query events from the session log."""
        return query_events(spec_id, session_id, kind, since, until, limit)
