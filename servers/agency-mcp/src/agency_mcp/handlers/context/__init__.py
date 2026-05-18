from fastmcp import FastMCP
from agency_mcp.handlers.context.anchors import register_context_anchor_tools
from agency_mcp.handlers.context.resources import register_context_resources

def register_context_handlers(mcp: FastMCP) -> None:
    register_context_anchor_tools(mcp)
    register_context_resources(mcp)
