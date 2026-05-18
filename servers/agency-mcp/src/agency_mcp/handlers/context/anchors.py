import typing
from pathlib import Path
from fastmcp import FastMCP
from agency_mcp.lib.codemode.context_manifest import ContextManifest, load_context_manifest
from agency_mcp.lib.codemode.context_anchor_triad import (
    _context_search,
    _context_describe,
    _context_read
)

# Module-level cache
_manifest_cache: ContextManifest | None = None

def _get_manifest() -> ContextManifest:
    global _manifest_cache
    if _manifest_cache is None:
        # Load from default path
        manifest_path = Path(__file__).resolve().parents[2] / "codemode" / "context_manifest.json"
        _manifest_cache = load_context_manifest(str(manifest_path))
    return _manifest_cache

def register_context_anchor_tools(mcp: FastMCP) -> None:
    @mcp.tool(tags={"domain:cross", "anchor:context"})
    def context_search(query: str, domain: str | None = None, tags: list[str] | None = None, limit: int = 10) -> list[dict]:
        """Search the deferred-context manifest (specs, lessons, overrides, references) by query, optionally filtered by domain or tag."""
        return _context_search(query, _get_manifest(), domain=domain, tags=tags, limit=limit)

    @mcp.tool(tags={"domain:cross", "anchor:context"})
    def context_describe(id: str) -> dict:
        """Get the full metadata and views summary for a context entry by ID."""
        return _context_describe(id, _get_manifest())

    @mcp.tool(tags={"domain:cross", "anchor:context"})
    def context_read(id: str, view: typing.Literal["summary", "preview", "full"] = "summary", fields: list[str] | None = None) -> dict:
        """Read the body of a context entry at a specific view tier, optionally projecting fields for JSON content."""
        return _context_read(id, _get_manifest(), view=view, fields=fields)
