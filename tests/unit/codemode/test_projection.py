import json
from agency_mcp.lib.codemode.views import View
from agency_mcp.lib.codemode.projection import project, apply_view

# Example data based on the spec Acceptance (Gherkin)
sample_album = {
    "id": "a1",
    "name": "Together We Confide",
    "state": "released",
    "status": "Final",
    "body": "x" * 2000,
    "title": "A Title",
    "genre": "electronic",
    "path": "/some/path",
    "tracks": {"t1": "track1"},
    "extra1": 1,
    "extra2": 2,
    "extra3": 3,
    "extra4": 4
}


def test_projection_default_summary():
    """# anchor: 103.1 Default view returns summary projection"""
    # Simulate default since view=View.summary is the default argument in the contract
    result = project(sample_album)

    # Check keys - it includes status and title as we added them to summary keys for completeness
    assert "id" in result
    assert "name" in result
    assert "state" in result
    assert "body" not in result
    assert "truncated_marker" not in result


def test_projection_preview_truncates_long_body():
    """# anchor: 103.2 Preview view truncates body and sets truncated_marker"""
    result = project(sample_album, view=View.preview)

    assert "body" in result
    assert len(result["body"]) == 400
    assert result["truncated_marker"] is True
    assert "id" in result
    assert "name" in result
    assert "state" in result


def test_projection_preview_no_truncation_short_body():
    """Preview view with short body doesn't truncate or set marker"""
    short_album = sample_album.copy()
    short_album["body"] = "short text"

    result = project(short_album, view=View.preview)
    assert result["body"] == "short text"
    assert "truncated_marker" not in result


def test_projection_explicit_fields():
    """# anchor: 103.3 Explicit fields override view tier"""
    result = project(sample_album, view=View.full, fields=["id", "state"])

    assert set(result.keys()) == {"id", "state"}


def test_projection_id_view():
    result = project(sample_album, view=View.id)
    assert result == {"id": "a1"}


def test_projection_full_view():
    result = project(sample_album, view=View.full)
    assert result == sample_album


def test_token_budget_regression():
    """# anchor: 103.4 Token-budget regression — summary is ≤25% of full"""
    summary_dict = project(sample_album, view=View.summary)
    full_dict = project(sample_album, view=View.full)

    summary_len = len(json.dumps(summary_dict))
    full_len = len(json.dumps(full_dict))

    assert summary_len <= 0.25 * full_len, f"Summary len {summary_len} > 25% of full len {full_len}"

def test_apply_view_decorator_sync():
    @apply_view
    def dummy_func():
        return json.dumps({"data": sample_album.copy()}) # Use an envelope to match normal handler output

    res = dummy_func(view=View.id)
    assert isinstance(res, str) # Due to json.dumps in _handle_result for dicts
    assert json.loads(res) == {"data": {"id": "a1"}}

import asyncio
def test_apply_view_decorator_async():
    @apply_view
    async def dummy_async_func():
        return json.dumps({"data": sample_album.copy()})

    res = asyncio.run(dummy_async_func(view=View.id))
    assert isinstance(res, str)
    assert json.loads(res) == {"data": {"id": "a1"}}
