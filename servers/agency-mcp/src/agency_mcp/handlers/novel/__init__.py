from fastmcp import FastMCP

from . import work_ops
from . import content
from . import core
from . import ideas
from . import status
from . import coherence
from . import structure
from . import characters
from . import world
from . import prose_analysis
from . import gates
from . import revision
from . import promo


def register_novel_core_handlers(mcp: FastMCP) -> None:
    """Register all novel core handlers to the provided MCP server."""
    work_ops.register(mcp)
    content.register(mcp)
    core.register(mcp)
    ideas.register(mcp)
    status.register(mcp)
    # Spec 013 — structural / coherence / prose handlers.
    coherence.register(mcp)
    structure.register(mcp)
    characters.register(mcp)
    world.register(mcp)
    prose_analysis.register(mcp)
    gates.register(mcp)
    revision.register(mcp)
    promo.register(mcp)
