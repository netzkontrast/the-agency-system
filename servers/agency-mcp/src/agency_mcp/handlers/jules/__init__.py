from fastmcp import FastMCP
from .lifecycle import register_lifecycle_tools
from .patches import register_patch_tools
from .bulk import register_bulk_tools
from .aliases import register_alias_tools

def register_jules_handlers(mcp: FastMCP) -> None:
    register_lifecycle_tools(mcp)
    register_patch_tools(mcp)
    register_bulk_tools(mcp)
    register_alias_tools(mcp)
