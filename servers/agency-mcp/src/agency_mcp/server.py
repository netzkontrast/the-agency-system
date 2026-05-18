"""agency-system FastMCP server.

Spec: Plan/001-scaffold-plugin-skeleton/spec.md
Spec: Plan/008-codemode-registry/spec.md (anchor-aware CodeMode)
"""
from __future__ import annotations

import warnings
from pathlib import Path
from typing import Sequence

from fastmcp import FastMCP

try:
    from fastmcp.experimental.transforms.code_mode import CodeMode
    from fastmcp.tools.base import Tool as _Tool

    class _AnchorAwareCodeMode(CodeMode):
        """CodeMode variant that keeps a small whitelist of anchor tools
        eagerly visible alongside the discovery + execute meta-tools.

        FastMCP 3.3.x's stock ``CodeMode.transform_tools`` returns only
        ``[*discovery, execute]`` — hiding every backend tool from
        ``tools/list``. Spec 008 calls for ~4 anchor tools per domain
        to remain visible so common operations don't require a
        search/get_schema/execute round-trip. This subclass merges the
        anchor list back into the transformed output.
        """

        def __init__(self, *, anchor_tool_names: Sequence[str] = (), **kwargs):
            super().__init__(**kwargs)
            self._anchor_tool_names = set(anchor_tool_names)

        async def transform_tools(
            self, tools: Sequence[_Tool]
        ) -> Sequence[_Tool]:
            base = await super().transform_tools(tools)
            anchors = [t for t in tools if t.name in self._anchor_tool_names]
            return [*base, *anchors]

    # Anchors are read lazily so a manifest error surfaces at boot, not
    # at import time. ``create_mcp`` builds the transform list with the
    # current anchor set on each call.
    _CODE_MODE_AVAILABLE = True
except ImportError as _e:
    CodeMode = None  # type: ignore[assignment]
    _AnchorAwareCodeMode = None  # type: ignore[assignment]
    _CODE_MODE_AVAILABLE = False
    warnings.warn(
        f"CodeMode unavailable ({_e}); all tools register eagerly",
        UserWarning,
        stacklevel=2,
    )

from agency_mcp.handlers.shared.health import register_health_tools
from agency_mcp.handlers.jules import register_jules_handlers
from agency_mcp.state.cache import StateCache


def register_all(mcp: FastMCP) -> None:
    """Register every domain's handlers on the unified MCP.

    Wave-A specs 004-009 extend this stub by importing their own
    ``register_<domain>_handlers`` entry points here.
    """
    from agency_mcp.handlers.context import register_context_handlers
    register_context_handlers(mcp)

    from agency_mcp.handlers.music import register_music_handlers
    from agency_mcp.handlers.music import _shared

    _shared.cache = StateCache()
    _shared.PLUGIN_ROOT = Path(__file__).resolve().parents[4]

    cache = _shared.cache
    cache.name = "agency-system"
    cache.dir = Path.home() / ".agency-system"
    register_health_tools(mcp)
    from .handlers.novel import register_novel_core_handlers
    register_novel_core_handlers(mcp)
    register_music_handlers(mcp)
    register_jules_handlers(mcp)

    from agency_mcp.handlers.shared import register_shared_handlers
    register_shared_handlers(mcp)


def _build_transforms() -> list:
    """Return the transform list, with the anchor-aware CodeMode if
    available. The anchor list comes from the manifest registry so
    boot fails loudly if the manifest is broken."""
    if not _CODE_MODE_AVAILABLE:
        return []
    from agency_mcp.lib.codemode.registry import anchor_tools
    anchors = anchor_tools()
    return [_AnchorAwareCodeMode(anchor_tool_names=anchors)]


def create_mcp() -> FastMCP:
    mcp = FastMCP(
        "agency-system",
        transforms=_build_transforms(),
        dereference_schemas=False,
    )
    register_all(mcp)
    return mcp


if __name__ == "__main__":
    create_mcp().run()
