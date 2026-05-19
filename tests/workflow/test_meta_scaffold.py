import pytest
import shutil
from pathlib import Path
from workflow._runner import pipeline

def test_meta_row_scaffolds_three_cells():
    # Given templates exist
    assert Path("workflow/meta/templates/agentic-cell.toml.jinja").exists()

    # And no row "podcast" exists
    if Path("agentic/podcast").exists():
        shutil.rmtree("agentic/podcast")
    if Path("workflow/podcast").exists():
        shutil.rmtree("workflow/podcast")
    if Path("context/podcast").exists():
        shutil.rmtree("context/podcast")

    # When start is called
    env = pipeline.start(row="meta", phase_id="01", inputs={"new_row": "podcast"})

    # Then it completes and creates files
    assert env["status"] == "completed"
    assert "created_cells" in env["tool_result"]["data"]

    assert Path("agentic/podcast/manifest.toml").exists()
    assert Path("workflow/podcast/manifest.toml").exists()
    assert Path("context/podcast/manifest.toml").exists()

    # Clean up
    shutil.rmtree("agentic/podcast")
    shutil.rmtree("workflow/podcast")
    shutil.rmtree("context/podcast")
