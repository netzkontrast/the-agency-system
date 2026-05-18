"""L1 Harness — FastMCP in-process plumbing.

Spec: Plan/harness/design.md §3.1
"""
import json
from functools import lru_cache
from fastmcp import FastMCP
from agency_mcp.server import create_mcp

class HarnessError(Exception):
    pass

@lru_cache(maxsize=1)
def harness_mcp() -> FastMCP:
    """Session-scoped memoised boot of the agency-mcp server."""
    return create_mcp()

async def list_tools(mcp: FastMCP) -> list:
    """Returns the full list of tools registered."""
    # FastMCP CodeMode hides all non-anchor tools from .list_tools().
    # We must access the original local provider to see the un-transformed list.
    return await mcp._local_provider.list_tools()

async def call_tool(mcp: FastMCP, name: str, params: dict = None) -> dict:
    """
    Invokes an in-memory tool and unwraps the envelope.
    """
    if params is None:
        params = {}

    result = await mcp.call_tool(name, params)
    if not result:
        raise HarnessError(f"Tool {name} returned empty result")
    if not result.content:
        raise HarnessError(f"Tool {name} result has no content")

    try:
        return json.loads(result.content[0].text)
    except Exception as e:
        raise HarnessError(f"Failed to decode tool {name} result: {e}\nRaw content: {result.content[0].text}")
