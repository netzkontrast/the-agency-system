import os
import pytest
import shutil
from pathlib import Path
from workflow._runner import pipeline
from context._store.sqlite import Store

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


def test_emits_cell_nodes(monkeypatch, tmp_path):
    """W5 — meta-row scaffold must upsert Cell/Row/Phase nodes into the graph."""
    # Stage a copy of the meta templates inside tmp_path so pipeline.start
    # resolves `workflow/meta/templates/` after we chdir there.
    src_tpl = Path(os.getcwd()) / "workflow" / "meta" / "templates"
    dst_tpl = tmp_path / "workflow" / "meta" / "templates"
    dst_tpl.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src_tpl, dst_tpl)

    db_path = str(tmp_path / "ontology.db")

    # Make pipeline's Store() target our sandbox DB.
    monkeypatch.setattr(
        "workflow._runner.pipeline.Store", lambda: Store(db_path=db_path)
    )

    orig_dir = os.getcwd()
    os.chdir(tmp_path)
    try:
        env = pipeline.start(row="meta", phase_id="01", inputs={"new_row": "demo"})
        assert env["status"] == "completed"

        # Verify 3 Cell nodes, 1 Row node, 1 Phase node, 1 PRECEDES edge.
        import sqlite3
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row

        cells = conn.execute(
            "SELECT id FROM nodes WHERE type = 'Cell'"
        ).fetchall()
        assert {r["id"] for r in cells} == {
            "cell/agentic/demo",
            "cell/workflow/demo",
            "cell/context/demo",
        }

        rows = conn.execute(
            "SELECT id FROM nodes WHERE type = 'Row'"
        ).fetchall()
        assert [r["id"] for r in rows] == ["row/demo"]

        phases = conn.execute(
            "SELECT id FROM nodes WHERE type = 'Phase'"
        ).fetchall()
        assert [r["id"] for r in phases] == ["phase/meta/02:demo"]

        edges = conn.execute(
            "SELECT type, from_node, to_node FROM edges WHERE type = 'PRECEDES'"
        ).fetchall()
        assert len(edges) == 1
        assert edges[0]["from_node"] == "phase/meta/01"
        assert edges[0]["to_node"] == "phase/meta/02:demo"
    finally:
        os.chdir(orig_dir)
