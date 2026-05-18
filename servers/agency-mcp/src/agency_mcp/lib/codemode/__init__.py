"""Code Mode registry — manifest-driven tool classification.

Spec: Plan/008-codemode-registry/spec.md
"""
from agency_mcp.lib.codemode.registry import (
    anchor_tools,
    background_companions,
    classify,
    load_manifest,
)
from agency_mcp.lib.codemode.deferred_loader import register_tool
from agency_mcp.lib.codemode.context_anchor_triad import register_context_anchor_triad

__all__ = [
    "anchor_tools",
    "background_companions",
    "classify",
    "load_manifest",
    "register_tool",
    "register_context_anchor_triad",
]
