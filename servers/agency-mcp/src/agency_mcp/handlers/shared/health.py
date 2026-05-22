"""Health-check tool — the eager anchor tool for the shared domain."""
from __future__ import annotations

from fastmcp import FastMCP

from agency_mcp import __version__


def register_health_tools(mcp: FastMCP) -> None:
    @mcp.tool
    def health_check() -> dict:
        """Return liveness status of the agency-system MCP server."""
        return {"ok": True, "version": __version__, "name": "agency-system"}
