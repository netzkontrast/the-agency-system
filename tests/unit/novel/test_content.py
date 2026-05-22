import pytest_asyncio
import pytest
from pathlib import Path
from unittest.mock import patch

from agency_mcp.handlers.novel import content
from agency_mcp.state.cache import StateCache

@pytest.fixture
def temp_workspace(tmp_path: Path):
    template_dir = tmp_path / "templates" / "novel"
    template_dir.mkdir(parents=True)

    (template_dir / "chapter.md").write_text("Chapter title: {{work_title}} - {{chapter_title}}")
    (template_dir / "scene.md").write_text("Scene: {{scene_number}}")

    cache = StateCache()

    with patch("agency_mcp.handlers.novel.content.PLUGIN_ROOT", tmp_path, create=True), \
         patch("agency_mcp.handlers.novel.content.cache", cache, create=True), \
         patch("agency_mcp.state.cache.STATE_CACHE_DIR", tmp_path):
        yield tmp_path, cache

@pytest.mark.asyncio
async def test_novel_create_chapter(temp_workspace):
    workspace, cache = temp_workspace

    # Setup work dir
    work_dir = workspace / "novels" / "ms" / "works" / "darkwave" / "test"
    (work_dir / "chapters").mkdir(parents=True)

    # Mock cache state for indexer lookup
    await cache.write("novel", {
        "authors": {
            "ms": {
                "works": {
                    "test": {
                        "work_title": "Test Novel",
                        "genre": "darkwave"
                    }
                }
            }
        }
    })

    res = await content.novel_create_chapter("ms", "test", 1, "The Beginning", dry_run=False, force=True)

    assert res["ok"] is True

    chap_file = work_dir / "chapters" / "ch01-the-beginning.md"
    assert chap_file.exists()

    content_text = chap_file.read_text()
    assert "Test Novel" in content_text
    assert "The Beginning" in content_text

@pytest.mark.asyncio
async def test_novel_create_scene(temp_workspace):
    workspace, cache = temp_workspace

    # Setup work dir
    work_dir = workspace / "novels" / "ms" / "works" / "darkwave" / "test"
    (work_dir / "scenes").mkdir(parents=True)

    await cache.write("novel", {
        "authors": {
            "ms": {
                "works": {
                    "test": {
                        "work_title": "Test Novel",
                        "genre": "darkwave"
                    }
                }
            }
        }
    })

    res = await content.novel_create_scene("ms", "test", 1, 1, dry_run=False)

    assert res["ok"] is True

    scene_file = work_dir / "scenes" / "ch01-s01.md"
    assert scene_file.exists()

    content_text = scene_file.read_text()
    assert "Scene: 1" in content_text
