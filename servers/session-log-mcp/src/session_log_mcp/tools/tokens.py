import json
from typing import Optional
from fastmcp import FastMCP
from .record import record_event

def register(mcp: FastMCP) -> None:
    @mcp.tool(tags=["domain:agentic"])
    def session_log_record_tokens(
        session_id: str,
        input_tokens: int,
        output_tokens: int,
        model: str,
        ts: Optional[str] = None
    ) -> str:
        """Record token usage for a session."""
        payload = {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "model": model
        }
        return record_event(
            kind="tokens",
            payload=payload,
            session_id=session_id,
            ts=ts
        )
