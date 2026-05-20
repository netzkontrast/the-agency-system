"""v0.2 follow-up #1 — pipeline.boot() seeds Phase nodes for hand-rolled rows.

Before this fix, V7 (`pipeline.start(row="jules", phase_id="01", ...)`)
returned `not in graph` on a fresh ontology because nothing seeded
`phase/jules/01`. Now `boot()` walks `workflow/<row>/phases/*.md` for
non-meta rows and upserts the corresponding Phase nodes.
"""

from pathlib import Path

import pytest

import context
import workflow._runner.pipeline as pipeline
from context._store.sqlite import Store


@pytest.fixture
def fresh_store(tmp_path, monkeypatch):
    db = tmp_path / "ontology.db"
    s = Store(db_path=str(db))
    s.boot()
    monkeypatch.setattr(context, "_STORE", s)
    monkeypatch.setattr(pipeline, "get_store", lambda: s)
    yield s


def test_boot_seeds_jules_phase_nodes(fresh_store, monkeypatch):
    monkeypatch.chdir(Path(__file__).resolve().parents[2])

    before = fresh_store.query(
        "MATCH (p:Phase {row: $row}) RETURN p", params={"row": "jules"}
    )
    assert before == []

    pipeline.boot()

    after = fresh_store.query(
        "MATCH (p:Phase {row: $row}) RETURN p", params={"row": "jules"}
    )
    phase_ids = sorted(
        (p.get("p", p).get("properties") or p.get("p", p).get("payload") or {}).get(
            "phase_id"
        )
        if isinstance(p.get("p", p), dict)
        else None
        for p in after
    )
    assert "01" in phase_ids and "02" in phase_ids


def test_boot_does_not_seed_meta_row(fresh_store, monkeypatch):
    monkeypatch.chdir(Path(__file__).resolve().parents[2])

    pipeline.boot()

    meta_phases = fresh_store.query(
        "MATCH (p:Phase {row: $row}) RETURN p", params={"row": "meta"}
    )
    assert meta_phases == []


def test_boot_is_idempotent(fresh_store, monkeypatch):
    monkeypatch.chdir(Path(__file__).resolve().parents[2])

    pipeline.boot()
    first = fresh_store.query(
        "MATCH (p:Phase {row: $row}) RETURN p", params={"row": "jules"}
    )
    pipeline.boot()
    second = fresh_store.query(
        "MATCH (p:Phase {row: $row}) RETURN p", params={"row": "jules"}
    )

    assert len(first) == len(second)
