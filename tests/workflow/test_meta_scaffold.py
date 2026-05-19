import pytest
import shutil
from pathlib import Path
from workflow._runner import pipeline
from context._store.sqlite import Store

def test_meta_row_scaffolds_three_cells(monkeypatch, tmp_path):
    # Pipe Store writes through a tmp DB so the test doesn't touch the real ontology.
    db_path = str(tmp_path / "ontology.db")
    monkeypatch.setattr(
        "workflow._runner.pipeline.Store", lambda: Store(db_path=db_path)
    )

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


def test_emits_cell_nodes(monkeypatch, tmp_path):
    """W5 — scaffolding a new row must emit Cell + Row + Phase nodes into
    the ontology graph so the row is discoverable beyond the filesystem."""
    db_path = str(tmp_path / "ontology.db")
    monkeypatch.setattr(
        "workflow._runner.pipeline.Store", lambda: Store(db_path=db_path)
    )

    new_row = "demo"
    for col in ("agentic", "workflow", "context"):
        if Path(col) / new_row in (Path(col).iterdir() if Path(col).exists() else []):
            shutil.rmtree(Path(col) / new_row)
    for col in ("agentic", "workflow", "context"):
        target = Path(col) / new_row
        if target.exists():
            shutil.rmtree(target)

    try:
        env = pipeline.start(row="meta", phase_id="01", inputs={"new_row": new_row})
        assert env["status"] == "completed", env

        store = Store(db_path=db_path)
        store.boot()

        cells = store.query("MATCH (n:Cell) RETURN n")
        rows = store.query("MATCH (n:Row) RETURN n")
        phases = store.query("MATCH (n:Phase) RETURN n")

        assert len(cells) == 3, f"expected 3 Cell nodes, got {len(cells)}"
        assert len(rows) == 1, f"expected 1 Row node, got {len(rows)}"
        assert len(phases) == 1, f"expected 1 Phase node, got {len(phases)}"
    finally:
        for col in ("agentic", "workflow", "context"):
            target = Path(col) / new_row
            if target.exists():
                shutil.rmtree(target)
