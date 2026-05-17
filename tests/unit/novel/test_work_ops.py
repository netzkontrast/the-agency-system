import pytest_asyncio
import pytest
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

from agency_mcp.handlers.novel import work_ops
from agency_mcp.state.cache import StateCache

@pytest.fixture
def temp_workspace(tmp_path: Path):
    # Setup template dir
    template_dir = tmp_path / "templates" / "novel"
    template_dir.mkdir(parents=True)

    templates = [
        "work.md", "premise.md", "cast.md", "dramatica.md",
        "outline.md", "ncp.json", "README.md"
    ]
    for t in templates:
        (template_dir / t).write_text(f"{{{{work_slug}}}} template content")

    (template_dir / "chapter.md").write_text("{{chapter_title}}")
    (template_dir / "scene.md").write_text("{{scene_title}}")
    (template_dir / "character.md").write_text("{{character_name}}")
    (template_dir / "world.md").write_text("{{world_name}}")

    cache = StateCache()

    with patch("agency_mcp.handlers.novel.work_ops.PLUGIN_ROOT", tmp_path, create=True), \
         patch("agency_mcp.handlers.novel.work_ops.cache", cache, create=True), \
         patch("agency_mcp.handlers.novel.work_ops._get_empty_state", create=True) as mock_empty_state, \
         patch("agency_mcp.state.cache.STATE_CACHE_DIR", tmp_path):
        yield tmp_path, cache

@pytest.mark.asyncio
async def test_novel_create_work_scaffolds(temp_workspace):
    workspace, cache = temp_workspace

    res = await work_ops.novel_create_work("ms", "darkwave", "test", "Test Title", "A logline", dry_run=False)

    assert res == {"ok": True, "data": {"created": True}, "warnings": []}

    # Check 11 files + 7 folders
    work_dir = workspace / "novels" / "ms" / "works" / "darkwave" / "test"
    assert work_dir.exists()

    for f in ["work.md", "premise.md", "cast.md", "dramatica.md", "outline.md", "ncp.json", "README.md"]:
        assert (work_dir / f).exists()
        assert "{{work_slug}}" not in (work_dir / f).read_text()

    for d in ["chapters", "scenes", "characters", "world", "revisions", "art", "research"]:
        assert (work_dir / d).is_dir()

@pytest.mark.asyncio
async def test_novel_create_work_idempotent(temp_workspace):
    workspace, cache = temp_workspace

    await work_ops.novel_create_work("ms", "darkwave", "test", dry_run=False)

    # Get initial mtime
    work_dir = workspace / "novels" / "ms" / "works" / "darkwave" / "test"
    mtime_before = (work_dir / "work.md").stat().st_mtime

    # Run again
    res = await work_ops.novel_create_work("ms", "darkwave", "test", dry_run=False)

    assert res["ok"] is True
    assert "work already exists" in res["warnings"]

    mtime_after = (work_dir / "work.md").stat().st_mtime
    assert mtime_before == mtime_after

@pytest.mark.asyncio
async def test_novel_create_work_dry_run(temp_workspace):
    workspace, cache = temp_workspace

    res = await work_ops.novel_create_work("ms", "darkwave", "test", dry_run=True)

    assert res["ok"] is True
    assert res["data"]["would_apply"] is True
    assert len(res["data"]["diff"]) > 0

    work_dir = workspace / "novels" / "ms" / "works" / "darkwave" / "test"
    assert not work_dir.exists()
