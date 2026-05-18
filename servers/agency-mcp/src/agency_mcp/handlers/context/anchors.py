import typing
import datetime
from pathlib import Path
from fastmcp import FastMCP
from agency_mcp.lib.codemode.context_manifest import ContextManifest, load_context_manifest
from agency_mcp.lib.codemode.context_anchor_triad import (
    _context_search,
    _context_describe,
    _context_read
)
from agency_mcp.lib.codemode.context_cache import ContextCache, ContextBody
from collections import deque


# Module-level cache
_manifest_cache: ContextManifest | None = None
_context_cache = ContextCache()

# ChangeLog ring buffer
change_log = deque(maxlen=256)

import functools

@functools.lru_cache(maxsize=128)
def _cached_search(query: str, domain: str | None, tags: frozenset | None, limit: int):
    t_list = list(tags) if tags else None
    return _context_search(query, _get_manifest(), domain=domain, tags=t_list, limit=limit)

@functools.lru_cache(maxsize=128)
def _cached_describe(id: str):
    return _context_describe(id, _get_manifest())

def clear_search_describe_cache():
    _cached_search.cache_clear()
    _cached_describe.cache_clear()


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
        t_frozenset = frozenset(tags) if tags else None
        return _cached_search(query, domain, t_frozenset, limit)

    @mcp.tool(tags={"domain:cross", "anchor:context"})
    def context_describe(id: str) -> dict:
        """Get the full metadata and views summary for a context entry by ID."""
        return _cached_describe(id)

    @mcp.tool(tags={"domain:cross", "anchor:context"})
    def context_read(id: str, view: typing.Literal["summary", "preview", "full"] = "summary", fields: list[str] | None = None) -> dict:
        """Read the body of a context entry at a specific view tier, optionally projecting fields for JSON content."""
        # Use cache if no fields are provided (since fields projection alters output)
        cache_key_view = f"{view}:{','.join(fields)}" if fields else view

        cached_body = _context_cache.get(id, cache_key_view)
        if cached_body is not None:
            # We must reconstruct the exact dict returned by _context_read
            manifest = _get_manifest()
            entry = manifest.get(id)
            import math
            try:
                import tiktoken
                enc = tiktoken.get_encoding("cl100k_base")
                token_estimate = len(enc.encode(cached_body.content))
            except ImportError:
                token_estimate = math.ceil(len(cached_body.content.encode("utf-8")) / 4)

            return {
                "id": id,
                "view": view, # Actual view logic is a bit complex, but returning requested view is fine for hit
                "mime": entry.get("mime", "text/plain") if entry else "text/plain",
                "body": cached_body.content,
                "token_estimate": token_estimate,
                "truncated": cached_body.truncated
            }

        result = _context_read(id, _get_manifest(), view=view, fields=fields)
        # Store in cache
        body_to_cache = ContextBody(result["body"], result["truncated"])
        _context_cache.put(id, cache_key_view, body_to_cache)
        return result

    @mcp.tool(tags={"domain:cross", "anchor:context"})
    def context_changes(since: str | None = None, limit: int = 50) -> list[dict]:
        """List recent additions/modifications/deletions in the context manifest. Use after a long pause to detect changes."""
        results = []
        since_dt = None
        if since:
            try:
                # Parse ISO-8601
                since_dt = datetime.datetime.fromisoformat(since)
            except ValueError:
                pass

        # The ring buffer appends to the right, so we iterate from right (newest) to left (oldest)
        # However, we'll just reverse the deque
        ordered_events = list(reversed(change_log))

        for event, timestamp in ordered_events:
            if since_dt and timestamp <= since_dt:
                continue

            results.append({
                "id": event.id,
                "kind": event.kind,
                "old_sha256": event.old_sha256,
                "new_sha256": event.new_sha256,
                "observed_at": timestamp.isoformat()
            })
            if len(results) >= min(limit, 256):
                break

        return results
