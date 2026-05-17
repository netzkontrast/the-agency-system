import pytest
import re
import asyncio
from fastmcp import FastMCP
from agency_mcp.server import create_mcp
from agency_mcp.handlers.music import register_music_handlers
from agency_mcp.handlers.music import _shared
from pathlib import Path
from agency_mcp.state.cache import StateCache

def test_all_modules_register_at_least_one_tool():
    mcp = FastMCP("test")
    _shared.cache = StateCache()
    _shared.PLUGIN_ROOT = Path("/tmp")
    register_music_handlers(mcp)
    tools = asyncio.run(mcp._local_provider.list_tools())
    assert len(tools) > 0, "No tools were registered"

def test_tool_count_at_least_60():
    mcp = create_mcp()
    tools = asyncio.run(mcp._local_provider.list_tools())
    assert len(tools) >= 60, f"Expected at least 60 tools, got {len(tools)}"

def test_every_music_tool_has_domain_tag():
    mcp = FastMCP("test")
    _shared.cache = StateCache()
    _shared.PLUGIN_ROOT = Path("/tmp")
    register_music_handlers(mcp)

    tools = asyncio.run(mcp._local_provider.list_tools())
    music_tools_count = 0
    for t in tools:
        name = t.name
        app_tool = t
        tags = getattr(app_tool, "tags", set())

        if name.startswith("music_"):
            music_tools_count += 1
            assert "domain:music" in tags, f"Tool {name} missing 'domain:music' tag"
        elif "domain:music" in tags:
            assert name.startswith("music_"), f"Tool {name} has domain:music but doesn't start with music_"

    assert music_tools_count > 0, "No music_ tools found"

def test_tool_names_match_naming_convention():
    mcp = FastMCP("test")
    _shared.cache = StateCache()
    _shared.PLUGIN_ROOT = Path("/tmp")
    register_music_handlers(mcp)

    tools = asyncio.run(mcp._local_provider.list_tools())
    pattern = re.compile(r"^music_[a-z]+(_[a-z0-9]+)+$")
    tool_names = [t.name for t in tools]
    for name in tool_names:
        if name.startswith("music_"):
            assert pattern.match(name), f"Tool name {name} does not match naming convention"

    assert "find_album" not in tool_names
    assert "create_track" not in tool_names
    assert "master_album" not in tool_names
