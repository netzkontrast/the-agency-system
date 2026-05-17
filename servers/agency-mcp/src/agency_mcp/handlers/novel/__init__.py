from fastmcp import FastMCP

from . import work_ops
from . import content
from . import core
from . import ideas
from . import status

def register_novel_core_handlers(mcp: FastMCP) -> None:
    """Register all novel core handlers to the provided MCP server."""
    work_ops.register(mcp)
    content.register(mcp)
    core.register(mcp)
    ideas.register(mcp)
    status.register(mcp)
