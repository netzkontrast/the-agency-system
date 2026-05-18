"""agency-system FastMCP server.

Spec: Plan/001-scaffold-plugin-skeleton/spec.md
"""
from __future__ import annotations
from pathlib import Path

from fastmcp import FastMCP

import warnings

try:
    from fastmcp.experimental.transforms.code_mode import CodeMode
    CODE_MODE_AVAILABLE = True
except ImportError as e:
    CODE_MODE_AVAILABLE = False
    warnings.warn(f"CodeMode unavailable: {e}; all tools eager")

from agency_mcp.handlers.shared.health import register_health_tools
from agency_mcp.handlers.jules import register_jules_handlers
from agency_mcp.state.cache import StateCache
from agency_mcp.lib.codemode import apply_codemode_manifest


def register_all(mcp: FastMCP) -> None:
    """Register every domain's handlers on the unified MCP.

    Wave-A specs 004-009 extend this stub by importing their own
    ``register_<domain>_handlers`` entry points here.
    """
    from agency_mcp.handlers.music import register_music_handlers
    from agency_mcp.handlers.music import _shared

    _shared.cache = StateCache()
    _shared.PLUGIN_ROOT = Path(__file__).resolve().parents[4]

    cache = _shared.cache
    cache.name = "agency-system"
    cache.dir = Path.home() / ".agency-system"
    register_health_tools(mcp)
    register_music_handlers(mcp)
    register_jules_handlers(mcp)

    from agency_mcp.handlers.shared import register_shared_handlers
    register_shared_handlers(mcp)

    manifest_path = Path(__file__).parent / "codemode" / "manifest.json"
    apply_codemode_manifest(mcp, manifest_path, CODE_MODE_AVAILABLE)


def create_mcp() -> FastMCP:
    mcp = FastMCP(
        "agency-system",
        dereference_schemas=False,
    )
    register_all(mcp)
    return mcp


if __name__ == "__main__":
    create_mcp().run()
