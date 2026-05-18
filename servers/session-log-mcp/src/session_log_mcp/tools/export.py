import json
from typing import Optional
from fastmcp import FastMCP
from session_log_mcp.db import get_conn

def register(mcp: FastMCP) -> None:
    @mcp.tool(tags=["domain:agentic"])
    def session_log_export_md(
        spec_id: Optional[str] = None,
        session_id: Optional[str] = None,
        since: Optional[str] = None,
        limit: int = 200
    ) -> str:
        """Export session log events as markdown."""
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
        query = f"SELECT * FROM events{where_clause} ORDER BY session_id, ts ASC LIMIT ?"
        params.append(limit)

        with get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()

        if not rows:
            return "No events found."

        output = []
        current_session = None

        for row in rows:
            sid = row["session_id"] or "Unknown Session"
            if sid != current_session:
                output.append(f"## session {sid}")
                current_session = sid

            payload_str = row["payload"]
            try:
                # Try to pretty print json if possible
                payload_obj = json.loads(payload_str)
                payload_str = json.dumps(payload_obj, separators=(',', ':'))
            except json.JSONDecodeError:
                pass

            kind = row["kind"]
            ts = row["ts"]
            output.append(f"- **{ts}** [{kind}]: {payload_str}")

        return "\n".join(output)
