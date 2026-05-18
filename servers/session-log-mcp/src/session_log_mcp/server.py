"""Server definition."""
from fastmcp import FastMCP
from session_log_mcp.db import schema
from session_log_mcp import tools

def create_mcp() -> FastMCP:
    """Create and configure the FastMCP server."""
    mcp = FastMCP("session-log")
    schema.ensure()
    tools.register_all(mcp)
    return mcp
