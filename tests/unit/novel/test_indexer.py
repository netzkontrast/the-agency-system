import pytest_asyncio
import pytest
from pathlib import Path
import json
from unittest.mock import patch

from agency_mcp.state.indexers.novel_indexer import NovelIndexer
from agency_mcp.state.cache import StateCache

@pytest.mark.asyncio
async def test_novel_indexer_populates_state(tmp_path: Path):
    # Setup cache and temp directory
    cache = StateCache()
    # Mock cache path for testing
    with patch("agency_mcp.state.cache.StateCache._state_file", new_callable=pytest.MonkeyPatch) as mock_file:
        pass

    # We will use patch context inside the test
    with patch("agency_mcp.state.cache.STATE_CACHE_DIR", tmp_path):
        # Pre-populate state to check isolation
        await cache.write("music", {"some": "value"})

        # Setup directories
        novel_dir = tmp_path / "novels"
        work_dir = novel_dir / "ms" / "works" / "darkwave" / "test"
        work_dir.mkdir(parents=True)

        # Create chapters and scenes dirs
        (work_dir / "chapters").mkdir()
        (work_dir / "scenes").mkdir()

        # Create some chapters and scenes to count
        (work_dir / "chapters" / "ch01-intro.md").touch()
        (work_dir / "chapters" / "ch02-action.md").touch()
        (work_dir / "scenes" / "ch01-s01.md").touch()

        # Create work.md frontmatter
        work_file = work_dir / "work.md"
        work_file.write_text("""---
type: novel.work
author_slug: ms
work_slug: test
created: "2024-05-17T12:00:00Z"
status: draft
genre_slug: darkwave
work_title: "Test Work"
target_word_count: 80000
---

# Test Work
""")

        # Run indexer
        indexer = NovelIndexer(cache, novel_dir)
        await indexer.rebuild()

        # Verify state
        state = await cache.snapshot()

        # Verify namespace isolation
        assert state.get("music") == {"some": "value"}

        # Verify novel state
        novel_state = state.get("novel", {})
        assert "authors" in novel_state

        author_works = novel_state["authors"]["ms"]["works"]
        assert "test" in author_works

        work_data = author_works["test"]
        assert work_data["genre"] == "darkwave"
        assert work_data["status"] == "draft"
        assert work_data["created"] == "2024-05-17T12:00:00Z"
        assert work_data["chapter_count"] == 2
        assert work_data["scene_count"] == 1

        # Check _indexed_at was set
        assert "_indexed_at" in novel_state
