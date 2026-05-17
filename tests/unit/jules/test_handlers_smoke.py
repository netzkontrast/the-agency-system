import pytest
import asyncio
from fastmcp import FastMCP
from agency_mcp.handlers.jules import register_jules_handlers

def test_jules_tools_registration_and_tags():
    mcp = FastMCP("test-jules")
    register_jules_handlers(mcp)

    tools = asyncio.run(mcp._local_provider.list_tools())

    jules_tools = [t for t in tools if 'domain:jules' in (t.tags or {})]

    assert len(jules_tools) >= 12, f"Expected at least 12 jules tools, got {len(jules_tools)}"

    for t in jules_tools:
        assert t.name.startswith("jules_"), f"Tool {t.name} must start with jules_"
        parts = t.name.split("_")
        assert len(parts) >= 2, f"Tool {t.name} must be snake_case verb_object"

    names = {t.name for t in jules_tools}
    assert "jules_start_watcher" in names
    assert "jules_watcher_status" in names
    assert "jules_stop_watcher" in names
