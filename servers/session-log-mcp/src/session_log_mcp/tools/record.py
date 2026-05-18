import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Union
from fastmcp import FastMCP
from session_log_mcp.db import get_conn

def record_event(
    kind: str,
    payload: Union[str, Dict[str, Any]],
    spec_id: Optional[str] = None,
    session_id: Optional[str] = None,
    pr_number: Optional[int] = None,
    actor: Optional[str] = None,
    ts: Optional[str] = None
) -> str:
    """Core logic to record an event."""
    if ts is None:
        ts = datetime.now(timezone.utc).isoformat()

    if isinstance(payload, dict):
        payload_str = json.dumps(payload)
    else:
        payload_str = str(payload)

    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO events (ts, kind, spec_id, session_id, pr_number, actor, payload)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (ts, kind, spec_id, session_id, pr_number, actor, payload_str))

        inserted = cursor.rowcount > 0
        if inserted:
            row_id = cursor.lastrowid
        else:
            cursor.execute("""
                SELECT id FROM events WHERE session_id = ? AND ts = ? AND kind = ?
            """, (session_id, ts, kind))
            row = cursor.fetchone()
            row_id = row["id"] if row else None

        conn.commit()

    return json.dumps({"id": row_id, "inserted": inserted})

def register(mcp: FastMCP) -> None:
    @mcp.tool(tags=["domain:agentic"])
    def session_log_record(
        kind: str,
        payload: Union[str, Dict[str, Any]],
        spec_id: Optional[str] = None,
        session_id: Optional[str] = None,
        pr_number: Optional[int] = None,
        actor: Optional[str] = None,
        ts: Optional[str] = None
    ) -> str:
        """Record an event to the session log."""
        return record_event(kind, payload, spec_id, session_id, pr_number, actor, ts)
