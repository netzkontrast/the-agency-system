import json
from agency_mcp.lib.codemode.views import View
from agency_mcp.lib.codemode.projection import project, apply_view

def test_project_id_view():
    data = {"id": "a1", "name": "Test", "state": "active", "body": "123"}
    res = project(data, view=View.id)
    assert res == {"id": "a1"}

def test_project_summary_view():
    data = {"id": "a1", "name": "Test", "state": "active", "body": "123", "extra": "x"}
    res = project(data, view=View.summary)
    assert res == {"id": "a1", "name": "Test", "state": "active"}

def test_project_preview_view_long():
    long_text = "x" * 2000
    data = {"id": "a1", "name": "Test", "state": "active", "body": long_text}
    res = project(data, view=View.preview)
    assert res["id"] == "a1"
    assert res["name"] == "Test"
    assert res["state"] == "active"
    assert len(res["body"]) == 400
    assert res["truncated_marker"] is True
    assert "body" in res

def test_project_preview_view_short():
    short_text = "short text"
    data = {"id": "a1", "name": "Test", "state": "active", "body": short_text}
    res = project(data, view=View.preview)
    assert res["body"] == short_text
    assert "truncated_marker" not in res

def test_project_full_view():
    data = {"id": "a1", "name": "Test", "state": "active", "body": "123", "extra": "x"}
    res = project(data, view=View.full)
    assert res == data

def test_project_explicit_fields():
    data = {"id": "a1", "name": "Test", "state": "active", "body": "123"}
    res = project(data, view=View.full, fields=["id", "state"])
    assert res == {"id": "a1", "state": "active"}

def test_token_budget_regression():
    long_text = "x" * 2000
    data = {
        "id": "a1", "name": "Test Album", "state": "released",
        "body": long_text, "f1": 1, "f2": 2, "f3": 3, "f4": 4,
        "f5": 5, "f6": 6, "f7": 7, "f8": 8, "f9": 9, "f10": 10,
        "f11": 11, "f12": 12
    }

    summary_dict = project(data, view=View.summary)
    full_dict = project(data, view=View.full)

    assert len(json.dumps(summary_dict)) <= 0.25 * len(json.dumps(full_dict))

def test_apply_view_sync():
    @apply_view
    def sync_tool(id: str):
        return {"id": id, "name": "Sync", "body": "123"}

    res = sync_tool("s1", view=View.id)
    assert res == {"id": "s1"}

def test_apply_view_async():
    import asyncio

    @apply_view
    async def async_tool(id: str):
        return {"id": id, "name": "Async", "body": "123"}

    res = asyncio.run(async_tool("a1", view=View.id))
    assert res == {"id": "a1"}
