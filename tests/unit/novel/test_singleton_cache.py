import pytest
from agency_mcp.handlers.novel import _shared
from agency_mcp.handlers.novel import work_ops, content, core, ideas, status
from agency_mcp.state.cache import StateCache

def test_singleton_cache_identity():
    cache1 = _shared.get_cache()
    cache2 = _shared.get_cache()

    assert cache1 is cache2
