import json
from typing import Optional
from fastmcp import FastMCP
from .record import record_event

def register(mcp: FastMCP) -> None:
    @mcp.tool(tags=["domain:agentic"])
    def session_log_record_tokens(
        session_id: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        ts: Optional[str] = None
    ) -> str:
        """Record token usage for a session."""
        payload = {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "model": model
        }
        return record_event(
            kind="tokens",
            payload=payload,
            session_id=session_id,
            ts=ts
        )
