"""Unified state indexer."""

from agency_mcp.state.indexers import music_indexer, novel_indexer, jules_indexer, ncp_indexer


def build_unified_state(domains: list[str]) -> dict:
    """Build a unified state dictionary from individual domain indexers."""
    state = {"_version": "1.0.0"}

    # We call each per-domain stub and assemble the top-level dict as requested by spec

    state["music"] = music_indexer.build()
    state["novel"] = novel_indexer.build()
    state["jules"] = jules_indexer.build()
    state["agentic"] = ncp_indexer.build()

    return state
