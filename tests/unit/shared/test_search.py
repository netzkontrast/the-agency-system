import pytest
from unittest.mock import patch, MagicMock

from agency_mcp.handlers.shared.search import shared_search
from agency_mcp.state.cache import StateCache

@pytest.fixture
def mock_cache():
    cache = StateCache()
    cache._state = {
        "novel": {"dramatica": {"note": "test dramatica note"}},
        "agentic": {"specs": [{"title": "dramatica primer"}]},
        "music": {},
        "jules": {}
    }
    return cache

@pytest.mark.asyncio
async def test_shared_search_empty_query():
    result = await shared_search("", None)
    assert result["ok"] is True
    assert result["data"] == []
    assert "empty query" in result["warnings"]

@pytest.mark.asyncio
async def test_shared_search_hits(mock_cache):
    with patch("agency_mcp.handlers.shared.search._get_cache", return_value=mock_cache):
        result = await shared_search("dramatica", None)
        assert result["ok"] is True

        namespaces = [hit["namespace"] for hit in result["data"]]
        assert "novel" in namespaces
        assert "agentic" in namespaces
        assert len(result["data"]) <= 20
