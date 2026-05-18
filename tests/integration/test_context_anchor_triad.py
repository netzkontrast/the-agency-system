import pytest
import asyncio
from agency_mcp.server import create_mcp

@pytest.mark.asyncio
async def test_context_anchor_triad_end_to_end():
    mcp = create_mcp()

    # 1. Check tools are registered and are eager
    tools = await mcp.list_tools()
    tool_names = {t.name for t in tools}
    assert "context_search" in tool_names
    assert "context_describe" in tool_names
    assert "context_read" in tool_names

    import json
    # 2. Search for a known ontology
    search_results = await mcp.call_tool("context_search", {"query": "dramatica ontology", "limit": 5})

    # The result from fastmcp.call_tool is a ToolResult envelope with `content[0].text`
    search_results_json = json.loads(search_results.content[0].text)

    # Simple check we got something
    assert isinstance(search_results_json, list)
    assert len(search_results_json) > 0

    top_id = search_results_json[0]["id"]

    # 3. Describe it
    desc_result = await mcp.call_tool("context_describe", {"id": top_id})
    desc = json.loads(desc_result.content[0].text)

    assert desc["id"] == top_id
    assert "views" in desc
    assert "path" in desc

    # 4. Read it (summary view)
    summary_result = await mcp.call_tool("context_read", {"id": top_id, "view": "summary"})
    summary = json.loads(summary_result.content[0].text)

    assert summary["view"] == "summary"
    assert summary["truncated"] is False
    assert summary["token_estimate"] <= 120

    # 5. Check resources
    safe_id = top_id.replace(":", "-")
    resources = await mcp.list_resources()
    resource_uris = {str(r.uri) for r in resources}
    assert f"context://{safe_id}/" in resource_uris or f"context://{safe_id}" in resource_uris
