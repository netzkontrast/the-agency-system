import os
import pytest
import sqlite3
from context._store.sqlite import Store

def test_store_boots_and_creates_database(tmp_path):
    # Scenario: Store boots and creates the database
    db_path = str(tmp_path / "ontology.db")
    store = Store(db_path=db_path)

    # When `Store().boot()` is invoked
    store.boot()

    # Then `ontology.db` exists
    assert os.path.exists(db_path)

    # And tables exist
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cursor.fetchall()}
    assert "nodes" in tables
    assert "edges" in tables
    assert "tools_call_log" in tables

    # And the required indexes exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
    indexes = {row[0] for row in cursor.fetchall()}
    assert "idx_nodes_type" in indexes

    # And re-invoking `boot()` is a no-op
    store.boot()

def test_upsert_edge_idempotent(tmp_path):
    # Scenario: SATISFIES_PHASE edge from gate emission
    # ... idempotent across re-runs
    db_path = str(tmp_path / "ontology.db")
    store = Store(db_path=db_path)
    store.boot()

    id1 = store.upsert_edge("SATISFIES_PHASE", "music/Artefact/abc", "phase:music/02")
    id2 = store.upsert_edge("SATISFIES_PHASE", "music/Artefact/abc", "phase:music/02")

    assert id1 == id2
