import pytest
from agency_mcp.handlers.novel.revision import novel_mark_revision_pass, novel_list_revision_passes, novel_revert_to_pass

@pytest.mark.asyncio
async def test_mark_and_list_revision_pass():
    res_mark1 = await novel_mark_revision_pass("test_work", "structural")
    assert res_mark1["ok"] is True

    res_mark2 = await novel_mark_revision_pass("test_work", "line")
    assert res_mark2["ok"] is True

    res_list = await novel_list_revision_passes("test_work")
    assert res_list["ok"] is True
    assert len(res_list["data"]["revisions"]) >= 2

@pytest.mark.asyncio
async def test_revert_to_pass_dry_run():
    await novel_mark_revision_pass("test_revert", "structural")
    await novel_mark_revision_pass("test_revert", "line")

    res_revert = await novel_revert_to_pass("test_revert", "structural", dry_run=True)
    assert res_revert["would_apply"] is True
    assert "entries ->" in res_revert["diff"]
