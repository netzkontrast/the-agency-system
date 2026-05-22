"""Deferred-load helper for tool registration.

Spec: Plan/008-codemode-registry/spec.md (Done When §lib/codemode/deferred_loader.py).

FastMCP 3.3.1 does not expose a ``defer_schema=True`` kwarg on
``@mcp.tool()``; the CodeMode transform in
``fastmcp.experimental.transforms.code_mode`` is what hides tools at
listing time. The deferred classification therefore has no direct
side-effect on the registration call — its only job is to record the
intent in the manifest so the boot-budget test and future tooling can
audit which tools are anchor-eligible and which are not.

This module is a thin pass-through that calls ``mcp.add_tool`` while
recording the classification on the function object. CodeMode's
``transform_tools`` is what actually hides deferred tools from
``tools/list``.
"""
from __future__ import annotations

from typing import Any, Callable


def register_tool(
    mcp: Any,
    fn: Callable[..., Any],
    name: str | None = None,
    *,
    classification: str | None = None,
) -> None:
    """Register ``fn`` on ``mcp`` and stamp its classification.

    Args:
        mcp: A FastMCP instance.
        fn: The tool callable to register.
        name: Optional explicit tool name (defaults to ``fn.__name__``).
        classification: One of ``"eager"``, ``"deferred"``,
            ``"background"`` — recorded on the function but does not
            change how the tool is registered. CodeMode's transform
            handles the actual hiding.

    The CodeMode transform layer (configured in ``server.py``) is what
    hides deferred/background tools from ``tools/list``. This helper
    exists so callers don't have to know that detail — they just say
    "register me deferred" and trust the transform to do the right thing.
    """
    # Record intent on the function — useful for downstream introspection
    # and for the boot-budget test to distinguish eager from deferred.
    fn._codemode_classification = classification  # type: ignore[attr-defined]
    mcp.tool(name=name)(fn) if name else mcp.tool()(fn)
