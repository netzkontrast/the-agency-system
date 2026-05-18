import pytest
import asyncio

@pytest.mark.asyncio
async def test_context_anchor_triad_end_to_end(mcp_instance, call_tool, tools):
    # 1. Check tools are registered and are eager
    tool_names = {t.name for t in tools}
    assert "context_search" in tool_names
    assert "context_describe" in tool_names
    assert "context_read" in tool_names
    
    # 2. Search for a known ontology
    search_results_json = await call_tool("context_search", {"query": "dramatica ontology", "limit": 5})
    
    # Simple check we got something
    assert isinstance(search_results_json, list)
    assert len(search_results_json) > 0
    
    top_id = search_results_json[0]["id"]
    
    # 3. Describe it
    desc = await call_tool("context_describe", {"id": top_id})
    
    assert desc["id"] == top_id
    assert "views" in desc
    assert "path" in desc
    
    # 4. Read it (summary view)
    summary = await call_tool("context_read", {"id": top_id, "view": "summary"})
    
    assert summary["view"] == "summary"
    assert summary["truncated"] is False
    assert summary["token_estimate"] <= 120
    
    # 5. Check resources
    safe_id = top_id.replace(":", "-")
    resources = await mcp_instance.list_resources()
    resource_uris = {str(r.uri) for r in resources}
    assert f"context://{safe_id}/" in resource_uris or f"context://{safe_id}" in resource_uris
