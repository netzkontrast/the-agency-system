import pytest
import os
import tempfile
import asyncio
from pathlib import Path
from agency_mcp.state.cache import StateCache

@pytest.fixture
def temp_cache_dir(monkeypatch):
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        monkeypatch.setattr("agency_mcp.state.cache.STATE_CACHE_DIR", tmp_path)
        yield tmp_path

@pytest.mark.asyncio
async def test_cache_propagates_write_errors(temp_cache_dir, monkeypatch):
    cache = StateCache()
    # Make dir read-only to simulate IOError
    state_file = cache._state_file

    # We will mock open to always throw OSError to ensure it triggers
    def mock_open(*args, **kwargs):
        raise OSError("Simulated write error")

    monkeypatch.setattr("builtins.open", mock_open)

    with pytest.raises(OSError, match="Simulated write error"):
        await cache.write("music", {"test": "data"})
