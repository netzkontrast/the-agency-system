"""Acceptance tests for the spec 07-v1 §FR3 graph walker.

Covers the four Acceptance scenarios called out in the task:

1. lazy-link opt-out blocks unknown phase
2. handler-not-found surfaces ``HANDLER_NOT_FOUND``
3. phase body missing surfaces ``PHASE_BODY_MISSING`` with the resolved path
4. first hard-blocking gate failure short-circuits; subsequent gates are NOT evaluated
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

import context
from context._store.sqlite import Store
from workflow._runner import manifest as manifest_reader
from workflow._runner import pipeline


@pytest.fixture
def tmp_store(monkeypatch, tmp_path):
    """Swap the process-singleton Store for a tmp-DB instance."""
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
    """Each test starts with empty manifest + handler caches."""
    manifest_reader._reset_cache_for_tests()
    pipeline._reset_handler_registry_for_tests()
    yield
    manifest_reader._reset_cache_for_tests()
    pipeline._reset_handler_registry_for_tests()


def test_lazy_link_opt_out_blocks_unknown_phase(tmp_store):
    """Spec 07-v1 §FR3 — jules's `enabled=false` refuses an unknown phase."""
    env = pipeline.start(
        row="jules",
        phase_id="99",
        inputs={},
        lazy_link=False,
    )
    assert env["status"] == "failed", env
    assert "not in graph" in env["tool_result"]["data"]["error"]["message"]


def test_walk_phase_handler_not_found(tmp_store, monkeypatch, tmp_path):
    """A Phase node with NO registered handler returns HANDLER_NOT_FOUND."""
    # Seed a Phase node for an isolated tmp row whose workflow cell ships
    # a manifest.toml + a phase body but NO agentic cell — so the cell
    # registry won't register `mcp__<row>_query` (or any handler).
    row = "sandboxnohandler"
    wf_dir = tmp_path / "wf_root" / "workflow" / row
    (wf_dir / "phases").mkdir(parents=True)
    (wf_dir / "phases" / "01-foo.md").write_text(
        '---\nphase_id: "01"\nentry_verb: "query"\n---\n# phase body\n',
        encoding="utf-8",
    )
    # workflow manifest so manifest_reader doesn't default-default.
    (wf_dir / "manifest.toml").write_text(
        textwrap.dedent(
            f"""\
            [cell]
            row = "{row}"
            column = "workflow"

            [workflow]
            entry_verbs = ["start"]
            """
        ),
        encoding="utf-8",
    )

    # Point the pipeline's phase-body reader at this tmp tree by switching cwd.
    monkeypatch.chdir(tmp_path / "wf_root")

    # Re-create the Store in the new cwd so the tmp DB is reachable.
    db = Path(tmp_path / "wf_root" / "ontology.db")
    store = Store(db_path=str(db))
    store.boot()
    monkeypatch.setattr(context, "_STORE", store, raising=False)

    store.upsert_node(
        f"phase/{row}/01",
        {"row": row, "phase_id": "01", "body_ref": "phases/01-foo.md"},
        label="Phase",
    )

    pipeline._reset_handler_registry_for_tests()
    env = pipeline.start(row=row, phase_id="01", inputs={})
    assert env["status"] == "failed", env
    assert env["tool_result"]["data"]["error"].get("code") == "HANDLER_NOT_FOUND", env


def test_walk_phase_body_missing(tmp_store, monkeypatch, tmp_path):
    """A Phase node whose body_ref points nowhere returns PHASE_BODY_MISSING."""
    row = "sandboxnobody"
    wf_dir = tmp_path / "wf_root2" / "workflow" / row
    (wf_dir / "phases").mkdir(parents=True)
    (wf_dir / "manifest.toml").write_text(
        textwrap.dedent(
            f"""\
            [cell]
            row = "{row}"
            column = "workflow"

            [workflow]
            entry_verbs = ["start"]
            """
        ),
        encoding="utf-8",
    )
    # Note: we deliberately do NOT write phases/01-missing.md.

    monkeypatch.chdir(tmp_path / "wf_root2")

    db = Path(tmp_path / "wf_root2" / "ontology.db")
    store = Store(db_path=str(db))
    store.boot()
    monkeypatch.setattr(context, "_STORE", store, raising=False)

    store.upsert_node(
        f"phase/{row}/01",
        {"row": row, "phase_id": "01", "body_ref": "phases/01-missing.md"},
        label="Phase",
    )

    pipeline._reset_handler_registry_for_tests()
    env = pipeline.start(row=row, phase_id="01", inputs={})
    assert env["status"] == "failed", env
    err = env["tool_result"]["data"]["error"]
    assert err.get("code") == "PHASE_BODY_MISSING", env
    # Resolved path appears verbatim in the error message.
    assert "phases/01-missing.md" in err["message"], env


def test_walk_phase_gate_short_circuit(tmp_store, monkeypatch, tmp_path):
    """First hard-blocking gate failure short-circuits — second gate NOT evaluated."""
    row = "sandboxgate"
    wf_dir = tmp_path / "wf_root3" / "workflow" / row
    (wf_dir / "phases").mkdir(parents=True)
    (wf_dir / "gates").mkdir(parents=True)

    # A workflow manifest so the row's lazy_link defaults False.
    (wf_dir / "manifest.toml").write_text(
        textwrap.dedent(
            f"""\
            [cell]
            row = "{row}"
            column = "workflow"

            [workflow]
            entry_verbs = ["start"]
            """
        ),
        encoding="utf-8",
    )

    # Phase body referencing the registered jules-row handler (mcp__jules_query)
    # — we re-point the phase at the jules row's tool so the handler resolves,
    # but the gate short-circuits before the handler runs.
    (wf_dir / "phases" / "02-x.md").write_text(
        '---\nphase_id: "02"\nentry_verb: "query"\n---\n# x\n',
        encoding="utf-8",
    )

    # Counter-spy: G2's evaluator increments a module-level counter. The
    # spy lives on an importable module so workflow._runner.gate.evaluate_gate
    # can import it like any other callable.
    spy_mod = tmp_path / "wf_root3" / "spy_eval.py"
    spy_mod.write_text(
        textwrap.dedent(
            """\
            CALLS = []
            def evaluate(envelope, args):
                CALLS.append(1)
                return {"ok": True, "message": "should never run"}
            """
        ),
        encoding="utf-8",
    )

    # G1: hard-blocking, FAILS via an evaluator that returns ok=False.
    failing_eval = tmp_path / "wf_root3" / "fail_eval.py"
    failing_eval.write_text(
        textwrap.dedent(
            """\
            def evaluate(envelope, args):
                return {"ok": False, "message": "g1 deliberately failing"}
            """
        ),
        encoding="utf-8",
    )

    (wf_dir / "gates" / "01-g1.yaml").write_text(
        textwrap.dedent(
            """\
            id: g1
            type: hard-blocking
            blocks_phase: "02"
            description: First gate, fails hard.
            evaluator:
              kind: callable
              module: fail_eval
              callable: evaluate
            on_failure:
              message: "g1 said no"
            """
        ),
        encoding="utf-8",
    )
    (wf_dir / "gates" / "02-g2.yaml").write_text(
        textwrap.dedent(
            """\
            id: g2
            type: hard-blocking
            blocks_phase: "02"
            description: Second gate, must NOT be evaluated.
            evaluator:
              kind: callable
              module: spy_eval
              callable: evaluate
            """
        ),
        encoding="utf-8",
    )

    monkeypatch.chdir(tmp_path / "wf_root3")
    # Ensure spy_eval / fail_eval are importable from cwd.
    import sys

    monkeypatch.syspath_prepend(str(tmp_path / "wf_root3"))

    db = Path(tmp_path / "wf_root3" / "ontology.db")
    store = Store(db_path=str(db))
    store.boot()
    monkeypatch.setattr(context, "_STORE", store, raising=False)

    store.upsert_node(
        f"phase/{row}/02",
        {"row": row, "phase_id": "02", "body_ref": "phases/02-x.md"},
        label="Phase",
    )

    pipeline._reset_handler_registry_for_tests()

    # Inject a handler for mcp__sandboxgate_query so HANDLER_NOT_FOUND
    # isn't what we hit. We forge the registry directly because building
    # a full agentic cell on the fly is overkill.
    from agentic._harness.cell_loader import CellRegistry

    reg = CellRegistry()
    reg.tools[f"mcp__{row}_query"] = lambda **kw: {
        "ok": True, "data": {}, "warnings": [], "next_suggested_tools": []
    }
    monkeypatch.setattr(pipeline, "_HANDLER_REGISTRY", reg)

    env = pipeline.start(row=row, phase_id="02", inputs={})

    assert env["status"] == "blocked_on_gate", env
    assert env["blocked_reason"] == "g1 said no", env

    # The spy must NOT have been called.
    import importlib

    spy = importlib.import_module("spy_eval")
    assert spy.CALLS == [], f"g2 evaluator was invoked: {spy.CALLS}"
