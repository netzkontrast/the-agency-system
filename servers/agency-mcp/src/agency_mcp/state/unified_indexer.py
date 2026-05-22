"""Unified state indexer."""

from agency_mcp.state.indexers import music_indexer, novel_indexer, jules_indexer, ncp_indexer


def build_unified_state(domains: list[str]) -> dict:
    """Build a unified state dictionary from individual domain indexers."""
    state = {"_version": "1.0.0"}

    # We only call the indexers that are requested, or default to all?
    # Actually wait, the spec says build_unified_state calls each per-domain stub and assembles top-level dict

    state["music"] = music_indexer.build() if "music" in domains else {"_generated": None}
    state["novel"] = novel_indexer.build() if "novel" in domains else {"_generated": None}
    state["jules"] = jules_indexer.build() if "jules" in domains else {"_generated": None}
    state["agentic"] = ncp_indexer.build() if "agentic" in domains else {"_generated": None}

    return state
