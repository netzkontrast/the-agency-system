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

@pytest.mark.asyncio
async def test_revert_to_pass():
    await novel_mark_revision_pass("test_revert2", "structural")
    await novel_mark_revision_pass("test_revert2", "line")

    res_list1 = await novel_list_revision_passes("test_revert2")
    assert len(res_list1["data"]["revisions"]) >= 2

    res_revert = await novel_revert_to_pass("test_revert2", "structural", dry_run=False)
    assert res_revert["ok"] is True

    res_list2 = await novel_list_revision_passes("test_revert2")
    assert len(res_list2["data"]["revisions"]) == 1
    assert res_list2["data"]["revisions"][0]["pass_kind"] == "structural"
