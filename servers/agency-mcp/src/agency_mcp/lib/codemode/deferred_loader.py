from typing import Callable, Literal
from fastmcp import FastMCP

def register_tool(mcp: FastMCP, fn: Callable, classification: Literal["eager", "deferred", "background"]) -> None:
    """Helper to wrap tool registration if needed in the future.
    For FastMCP 3.3.1 using CodeMode, tools are registered normally,
    and then CodeMode manages hiding them later. So this is just a thin wrapper.
    """
    mcp.add_tool(fn)
