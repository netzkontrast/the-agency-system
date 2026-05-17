"""agency-system FastMCP server.

Spec: Plan/001-scaffold-plugin-skeleton/spec.md
"""
from __future__ import annotations

from fastmcp import FastMCP

try:
    from fastmcp.experimental.transforms.code_mode import CodeMode
    _transforms = [CodeMode()]
except ImportError:
    _transforms = []

from agency_mcp.handlers.shared.health import register_health_tools


def register_all(mcp: FastMCP) -> None:
    """Register every domain's handlers on the unified MCP.

    Wave-A specs 004-009 extend this stub by importing their own
    ``register_<domain>_handlers`` entry points here.
    """
    register_health_tools(mcp)
    from .handlers.novel import register_novel_core_handlers
    register_novel_core_handlers(mcp)

    from agency_mcp.handlers.shared import register_shared_handlers
    register_shared_handlers(mcp)


def create_mcp() -> FastMCP:
    mcp = FastMCP(
        "agency-system",
        transforms=_transforms,
        dereference_schemas=False,
    )
    register_all(mcp)
    return mcp


if __name__ == "__main__":
    create_mcp().run()
