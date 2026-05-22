import pytest
from agency_mcp.handlers.novel.promo import novel_build_promo_pack, novel_get_promo_content, novel_update_promo_field

@pytest.mark.asyncio
async def test_build_promo_pack():
    res = novel_build_promo_pack("clean_work")
    assert res["ok"] is True
    assert "blurb" in res["data"]
    assert "logline" in res["data"]
    assert "jacket_flap" in res["data"]
    assert "press_kit" in res["data"]

    # Check idempotent behavior
    res2 = novel_build_promo_pack("clean_work")
    assert res["data"] == res2["data"]

@pytest.mark.asyncio
async def test_get_promo_content():
    res = novel_get_promo_content("clean_work", "blurb")
    assert res["ok"] is True
    assert res["data"]["content"]

@pytest.mark.asyncio
async def test_update_promo_field():
    import shutil
    import os
    if os.path.exists("tests/fixtures/novel/temp_promo_work"):
        shutil.rmtree("tests/fixtures/novel/temp_promo_work")
    shutil.copytree("tests/fixtures/novel/clean_work", "tests/fixtures/novel/temp_promo_work")

    with open("tests/fixtures/novel/temp_promo_work/README.md", "w") as f:
        f.write("---\n")
        f.write("genre: fiction\n")
        f.write('logline: "A clean work."\n')
        f.write("---\n")

    res = novel_update_promo_field("temp_promo_work", "blurb", "logline", "Updated logline text.")
    assert res["ok"] is True

    with open("tests/fixtures/novel/temp_promo_work/README.md", "r") as f:
        readme_content = f.read()
    assert "Updated logline text." in readme_content

    shutil.rmtree("tests/fixtures/novel/temp_promo_work")
