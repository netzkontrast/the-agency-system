"""N0 — C5 — verify PreToolUse / PostToolUse hooks fire on every registered
tool.

The bootloader wraps each discovered tool via ``make_hooked_wrapper`` so
``context._hooks.pre_tool_use.validate`` runs before the call and
``context._hooks.post_tool_use.ingest`` runs after. The tests below cover
both: the wrapper invokes pre-validation (no exception) and ingests the
returned envelope into the ontology graph.
"""

from agentic._bootloader import make_hooked_wrapper
from context._store.sqlite import Store


def _artefact_envelope() -> dict:
    return {
        "ok": True,
        "data": {
            "artefact_metadata": {
                "artefact_path": "result/test/dummy.txt",
                "content_type": "text/plain",
                "sha256": "a" * 64,
                "size_bytes": 5,
                "created_at": "2026-05-19T00:00:00Z",
                "produced_by": {
                    "skill": "test-dummy",
                    "phase": "01",
                    "session_id": "s1",
                },
                "derived_from": [],
                "satisfies_phase": "01",
            }
        },
        "warnings": [],
        "next_suggested_tools": [],
    }


def test_post_hook_ingests_artefact_node(monkeypatch, tmp_path):
    db_path = str(tmp_path / "ontology.db")
    monkeypatch.setattr(
        "context._hooks.post_tool_use.Store", lambda: Store(db_path=db_path)
    )

    def dummy_tool(**_kwargs) -> dict:
        return _artefact_envelope()

    wrapped = make_hooked_wrapper("mcp__test_dummy", dummy_tool)
    result = wrapped()

    assert result["ok"] is True

    store = Store(db_path=db_path)
    store.boot()
    res = store.query("MATCH (n:Artefact) RETURN n")
    assert len(res) >= 1, "PostToolUse.ingest did not write an Artefact node"


def test_pre_hook_runs_without_raising_for_normal_tool(monkeypatch, tmp_path):
    db_path = str(tmp_path / "ontology.db")
    monkeypatch.setattr(
        "context._hooks.post_tool_use.Store", lambda: Store(db_path=db_path)
    )

    calls = {"n": 0}

    def dummy_tool(**_kwargs) -> dict:
        calls["n"] += 1
        return {
            "ok": True,
            "data": {},
            "warnings": [],
            "next_suggested_tools": [],
        }

    wrapped = make_hooked_wrapper("mcp__noop", dummy_tool)
    wrapped(foo="bar")

    assert calls["n"] == 1


def test_wrapper_binds_closure_correctly(monkeypatch, tmp_path):
    """Loop-variable binding regression: each wrapper must call its own
    ``t_func`` rather than whichever was last bound by the enclosing loop."""
    db_path = str(tmp_path / "ontology.db")
    monkeypatch.setattr(
        "context._hooks.post_tool_use.Store", lambda: Store(db_path=db_path)
    )

    def make_tool(tag):
        def _tool(**_kwargs):
            return {
                "ok": True,
                "data": {"tag": tag},
                "warnings": [],
                "next_suggested_tools": [],
            }

        return _tool

    wrappers = {
        name: make_hooked_wrapper(name, make_tool(name))
        for name in ("a", "b", "c")
    }

    for name, w in wrappers.items():
        assert w()["data"]["tag"] == name
