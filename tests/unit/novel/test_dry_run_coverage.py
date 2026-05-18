import pytest
import pytest_asyncio
from agency_mcp.handlers.novel import work_ops, ideas, status
from agency_mcp.state.cache import StateCache
from agency_mcp.handlers.novel import _shared

@pytest.fixture
def mock_cache():
    cache = _shared.get_cache()
    return cache

@pytest.mark.asyncio
@pytest.mark.parametrize("tool_func,kwargs", [
    (work_ops.novel_rebuild_state, {}),
    (ideas.novel_create_premise_idea, {"title": "T", "logline": "L"}),
])
async def test_dry_run_returns_would_apply_creation(mock_cache, tool_func, kwargs):
    kwargs["dry_run"] = True
    res = await tool_func(**kwargs)
    assert res["ok"] is True
    assert "would_apply" in res["data"]
    assert res["data"]["would_apply"] is True
    assert "diff" in res["data"]

@pytest.mark.asyncio
@pytest.mark.parametrize("tool_func,kwargs", [
    (ideas.novel_update_premise_idea, {"idea_id": "id1", "title": "T2"}),
    (ideas.novel_delete_premise_idea, {"idea_id": "id1"}),
    (ideas.novel_promote_premise, {"idea_id": "id1", "author": "a", "genre": "g", "slug": "s"}),
])
async def test_dry_run_returns_would_apply_idea_ops(mock_cache, tool_func, kwargs):
    await mock_cache.write("novel", {
        "premise_ideas": {
            "id1": {"title": "T1", "logline": "L1"}
        }
    })
    kwargs["dry_run"] = True
    res = await tool_func(**kwargs)
    assert res["ok"] is True
    assert "would_apply" in res["data"]
    assert res["data"]["would_apply"] is True
    assert "diff" in res["data"]

@pytest.mark.asyncio
@pytest.mark.parametrize("tool_func,kwargs", [
    (status.novel_update_work_status, {"author": "a", "work_slug": "w", "status": "done"}),
    (status.novel_update_chapter_status, {"author": "a", "work_slug": "w", "chapter_slug": "ch01", "status": "review"}),
    (status.novel_update_scene_status, {"author": "a", "work_slug": "w", "scene_slug": "ch01-s01", "status": "review"}),
])
async def test_dry_run_returns_would_apply_status_ops(mock_cache, tool_func, kwargs, tmp_path):
    import agency_mcp.handlers.novel.status
    agency_mcp.handlers.novel.status.PLUGIN_ROOT = tmp_path

    await mock_cache.write("novel", {
        "authors": {
            "a": {
                "works": {
                    "w": {
                        "genre": "g",
                        "status": "in_progress"
                    }
                }
            }
        }
    })

    # Setup files
    work_dir = tmp_path / "novels" / "a" / "works" / "g" / "w"
    work_dir.mkdir(parents=True, exist_ok=True)
    (work_dir / "chapters").mkdir(exist_ok=True)
    (work_dir / "scenes").mkdir(exist_ok=True)

    (work_dir / "work.md").write_text("---\nstatus: in_progress\n---\n")
    (work_dir / "chapters" / "ch01.md").write_text("---\nstatus: in_progress\n---\n")
    (work_dir / "scenes" / "ch01-s01.md").write_text("---\nstatus: in_progress\n---\n")

    kwargs["dry_run"] = True
    res = await tool_func(**kwargs)
    assert res["ok"] is True
    assert "would_apply" in res["data"]
    assert res["data"]["would_apply"] is True
    assert "diff" in res["data"]

from agency_mcp.handlers.novel import work_ops, content, core

@pytest.mark.asyncio
@pytest.mark.parametrize("tool_func,kwargs", [
    (work_ops.novel_rename_work, {"author": "a", "old_slug": "w", "new_slug": "w-new"}),
    (content.novel_rename_chapter, {"author": "a", "work_slug": "w", "old_slug": "ch01", "new_slug": "ch01-new"}),
])
async def test_dry_run_returns_would_apply_renames(mock_cache, tool_func, kwargs, tmp_path):
    import agency_mcp.handlers.novel.work_ops
    import agency_mcp.handlers.novel.content
    agency_mcp.handlers.novel.work_ops.PLUGIN_ROOT = tmp_path
    agency_mcp.handlers.novel.content.PLUGIN_ROOT = tmp_path

    await mock_cache.write("novel", {
        "authors": {
            "a": {
                "works": {
                    "w": {
                        "genre": "g",
                        "status": "in_progress"
                    }
                }
            }
        }
    })

    work_dir = tmp_path / "novels" / "a" / "works" / "g" / "w"
    work_dir.mkdir(parents=True, exist_ok=True)
    (work_dir / "chapters").mkdir(exist_ok=True)
    (work_dir / "chapters" / "ch01.md").write_text("content")

    kwargs["dry_run"] = True
    res = await tool_func(**kwargs)
    assert res["ok"] is True
    assert "would_apply" in res["data"]
    assert res["data"]["would_apply"] is True
    assert "diff" in res["data"]
