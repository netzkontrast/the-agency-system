import pytest
import json
import tiktoken
import asyncio
from agency_mcp.server import create_mcp

@pytest.mark.asyncio
async def test_boot_token_budget():
    mcp = create_mcp()

    # mcp.list_tools() gets all tools across all mounted providers (local + CodeMode transformed proxy)
    tools = await mcp.list_tools()

    # Check that search, get_schema, execute are present (provided by CodeMode proxy)
    tool_names = [t.name for t in tools]
    assert "search" in tool_names, f"search missing, got {tool_names}"
    assert "get_schema" in tool_names
    assert "execute" in tool_names

    # To check token size, we serialize the tools similarly to what is sent over the wire
    # The actual MCP protocol sends a dictionary with name, description, inputSchema.
    tool_dicts = [{"name": t.name, "description": t.description, "inputSchema": t.parameters} for t in tools]
    json_blob = json.dumps(tool_dicts, separators=(',', ':'))

    enc = tiktoken.get_encoding("cl100k_base")
    tokens = len(enc.encode(json_blob))

    byte_size = len(json_blob.encode("utf-8"))
    print(f"\ntools_list_tokens={tokens}, byte_size={byte_size}")

    assert byte_size <= 3000, f"Boot payload {byte_size}B exceeds 3000-byte ceiling (CodeMode baseline ~1800B + ~4 anchors per domain). If new domains are added, audit anchor classifications."
    assert tokens <= 500, f"Boot payload {tokens}t exceeds 500-token budget. Move tools from eager to deferred."
