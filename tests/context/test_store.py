import os
import pytest
import sqlite3
from context._store.sqlite import Store

def test_store_boots_and_creates_database(tmp_path):
    db_path = str(tmp_path / "ontology.db")
    store = Store(db_path=db_path)

    store.boot()

    # In graphqlite fallback/mock, we create tables on upsert. Let's just do an upsert
    store.upsert_node('a', 'test', {})

    assert os.path.exists(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cursor.fetchall()}

    assert "nodes" in tables

def test_upsert_edge_idempotent(tmp_path):
    db_path = str(tmp_path / "ontology.db")
    store = Store(db_path=db_path)
    store.boot()

    store.upsert_edge("SATISFIES_PHASE", "music/Artefact/abc", "phase:music/02")
    store.upsert_edge("SATISFIES_PHASE", "music/Artefact/abc", "phase:music/02")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM edges WHERE type='SATISFIES_PHASE'")
    assert cursor.fetchone()[0] == 1
