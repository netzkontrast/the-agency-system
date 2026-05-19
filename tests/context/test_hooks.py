import os
import json
import pytest
from context._hooks import pre_tool_use, post_tool_use
from context._store.sqlite import Store

def test_pre_tool_use_rejects_invalid_agentic_manifest():
    toml_content = """
    [cell]
    row = "test"
    column = "agentic"
    """

    args = {"path": "agentic/test/manifest.toml", "content": toml_content}
    res = pre_tool_use.validate_envelope_in("mcp__test_write_manifest", args)

    assert not res["ok"]
    assert "errors" in res
    assert any("missing required key [skills]" in e for e in res["errors"])

def test_post_tool_use_logs_every_envelope(monkeypatch, tmp_path):
    db_path = str(tmp_path / "ontology.db")
    monkeypatch.setattr("context._hooks.post_tool_use.Store", lambda: Store(db_path=db_path))

    envelope = {"ok": True, "data": {}, "warnings": [], "next_suggested_tools": []}

    post_tool_use.ingest("some_tool", envelope)

    store = Store(db_path=db_path)
    import sqlite3
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.execute("SELECT tool, envelope FROM tools_call_log")
    rows = cursor.fetchall()
    assert len(rows) == 1
    assert rows[0]["tool"] == "some_tool"
    assert json.loads(rows[0]["envelope"]) == envelope


def test_post_tool_use_artefact_metadata(monkeypatch, tmp_path):
    db_path = str(tmp_path / "ontology.db")
    monkeypatch.setattr("context._hooks.post_tool_use.Store", lambda: Store(db_path=db_path))

    artefact_metadata = {
      "artefact_path": "result/music/whispers/master.mp3",
      "content_type":  "audio/mpeg",
      "sha256":        "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08",
      "size_bytes":    7340032,
      "created_at":    "2026-05-19T14:22:07Z",
      "produced_by": {
        "skill":      "music-producer",
        "phase":      "04-master",
        "session_id": "wf-2026-05-19-whispers-a1b2"
      },
      "derived_from": [
        "music/LyricSheet/whispers",
        "music/SunoPrompt/whispers-v3"
      ],
      "satisfies_phase": "04-master"
    }

    envelope = {"ok": True, "data": {"artefact_metadata": artefact_metadata}, "warnings": [], "next_suggested_tools": []}

    post_tool_use.ingest("some_tool", envelope)

    store = Store(db_path=db_path)
    res = store.query("MATCH (n:Artefact) RETURN n")
    assert len(res) == 1

    # Check edges
    edges = store.query("MATCH (a:Artefact)-[:DERIVED_FROM]->(b) RETURN a, b")
    # For basic mock test, just verify the edges exist via simple SQL
    import sqlite3
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.execute("SELECT * FROM edges WHERE type = 'DERIVED_FROM'")
    edges_sql = cursor.fetchall()
    assert len(edges_sql) == 2

def test_satisfies_phase_edge_from_gate_emission(monkeypatch, tmp_path):
    db_path = str(tmp_path / "ontology.db")
    monkeypatch.setattr("context._hooks.post_tool_use.Store", lambda: Store(db_path=db_path))

    envelope = {"ok": True, "data": {"emitted_edges": [{"type": "SATISFIES_PHASE", "from": "music/Artefact/abc", "to": "phase:music/02"}]}}
    post_tool_use.ingest("some_tool", envelope)

    store = Store(db_path=db_path)
    import sqlite3
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.execute("SELECT type, from_node, to_node FROM edges WHERE type = 'SATISFIES_PHASE'")
    rows = cursor.fetchall()
    assert len(rows) == 1
    assert rows[0]["from_node"] == "music/Artefact/abc"
    assert rows[0]["to_node"] == "phase:music/02"
