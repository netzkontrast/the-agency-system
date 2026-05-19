import pytest
from pathlib import Path
from workflow._runner import pipeline

def test_pipeline_start_and_yields_running_envelope():
    # Given workflow/meta/manifest.toml exists
    assert Path("workflow/meta/manifest.toml").exists()

    # When start is called with invalid new_row
    env = pipeline.start(row="meta", phase_id="01", inputs={"new_row": "Invalid-Row"})

    # Then blocked envelope is returned
    assert env["status"] == "blocked_on_user"
    assert env["phase_id"] == "01"
    assert env["row"] == "meta"

def test_pipeline_lazy_create_path():
    # Calling an unknown row without lazy_link fails
    env = pipeline.start(row="unknown", phase_id="01", inputs={})
    assert env["status"] == "failed"
    assert "not found in graph" in env["tool_result"]["data"]["error"]["message"]

    # Calling with lazy_link creates a placeholder and continues (mock logic returns the failure mock for non-meta for now,
    # but lazy_create flag is parsed correctly, we just check if it fails differently or continues to the non-meta mock block)
    env2 = pipeline.start(row="unknown", phase_id="01", inputs={}, lazy_link=True)
    # The current pipeline logic falls through to the bottom mock for non-meta rows
    assert env2["status"] == "failed"
    assert "not supported in base pipeline" in env2["tool_result"]["data"]["error"]["message"]
