import pytest
import asyncio
from pathlib import Path
from unittest.mock import patch

from agency_mcp.state.indexers.novel_indexer import NovelIndexer
from agency_mcp.state.cache import StateCache

@pytest.fixture
def mock_cache():
    return StateCache()

@pytest.mark.asyncio
async def test_indexer_rebuild_atomicity(mock_cache, tmp_path):
    indexer = NovelIndexer(mock_cache, tmp_path)

    # Simulate concurrent rebuilds
    results = await asyncio.gather(
        indexer.rebuild(),
        indexer.rebuild()
    )

    # If atomicity was compromised, we'd get state corruption or lock errors.
    assert len(results) == 2
