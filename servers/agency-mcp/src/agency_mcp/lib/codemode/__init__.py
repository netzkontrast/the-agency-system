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

__all__ = [
    "anchor_tools",
    "background_companions",
    "classify",
    "load_manifest",
    "register_tool",
]
