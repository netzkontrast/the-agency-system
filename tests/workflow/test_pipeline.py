"""Pipeline tests — spec 07-v1 §FR3.

The v0 file used hard-coded "row not supported in base pipeline"
phrasing; that branch is replaced by the generic graph walker, so the
v1 assertions check the new failure shapes:

- Unknown row + ``lazy_link=False`` -> ``error.message`` mentions "not in graph".
- Unknown row + ``lazy_link=True`` -> the row's manifest absence (and
  thus its missing ``[workflow.lazy_link] enabled=true`` opt-in) drives
  the runner to return the lazy-link conflict envelope.
"""

import pytest
from pathlib import Path

import context
from context._store.sqlite import Store
from workflow._runner import manifest as manifest_reader
from workflow._runner import pipeline


@pytest.fixture
def tmp_store(monkeypatch, tmp_path):
    db_path = str(tmp_path / "ontology.db")
    store = Store(db_path=db_path)
    store.boot()
    monkeypatch.setattr(context, "_STORE", store, raising=False)
    monkeypatch.setattr(
        "workflow._runner.pipeline.Store", lambda: Store(db_path=db_path)
    )
    yield store


@pytest.fixture(autouse=True)
def _reset_caches():
    manifest_reader._reset_cache_for_tests()
    pipeline._reset_handler_registry_for_tests()
    yield
    manifest_reader._reset_cache_for_tests()
    pipeline._reset_handler_registry_for_tests()


def test_pipeline_start_and_yields_running_envelope(tmp_store):
    # Given workflow/meta/manifest.toml exists
    assert Path("workflow/meta/manifest.toml").exists()

    # When start is called with invalid new_row
    env = pipeline.start(row="meta", phase_id="01", inputs={"new_row": "Invalid-Row"})

    # Then blocked envelope is returned
    assert env["status"] == "blocked_on_user"
    assert env["phase_id"] == "01"
    assert env["row"] == "meta"


def test_pipeline_lazy_create_path(tmp_store):
    # Calling an unknown row without lazy_link fails — "not in graph" wording.
    env = pipeline.start(row="unknown", phase_id="01", inputs={})
    assert env["status"] == "failed"
    assert "not in graph" in env["tool_result"]["data"]["error"]["message"]

    # Calling with lazy_link on a row whose manifest.toml does not exist
    # (so its `[workflow.lazy_link] enabled` resolves to the default False)
    # returns the lazy-link conflict envelope per spec 07-v1 §FR3.
    env2 = pipeline.start(row="unknown", phase_id="01", inputs={}, lazy_link=True)
    assert env2["status"] == "failed"
    assert "lazy_link" in env2["tool_result"]["data"]["error"]["message"]
