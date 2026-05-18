"""Tool registrations."""
from fastmcp import FastMCP
from . import record, query, summary, export, tokens

def register_all(mcp: FastMCP) -> None:
    record.register(mcp)
    query.register(mcp)
    summary.register(mcp)
    export.register(mcp)
    tokens.register(mcp)
