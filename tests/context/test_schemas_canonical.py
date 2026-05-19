"""N2 — round-trip every runtime schema against a canonical example.

The six JSON Schemas under ``context/_shared/schemas/`` are the runtime
source of truth for cell manifests, gate definitions, the tool-result
envelope, and the Artefact node payload. This test asserts that:

1. Every schema file parses as valid JSON Schema (Draft 2020-12).
2. A canonical positive example validates against its schema.
3. A canonical negative example fails validation, so the schema isn't
   merely permissive.

If a new schema is added under ``context/_shared/schemas/``, add an
entry to ``EXAMPLES`` to keep coverage complete.
"""

import json
from pathlib import Path

import jsonschema
import pytest

SCHEMA_DIR = Path(__file__).resolve().parents[2] / "context" / "_shared" / "schemas"


_AGENTIC_CELL_OK = {
    "cell": {"row": "demo", "column": "agentic"},
    "skills": {"exports": ["research"]},
    "tools": {"exports": ["query"]},
}

_WORKFLOW_CELL_OK = {
    "cell": {"row": "demo", "column": "workflow"},
    "workflow": {"entry_verbs": ["start", "resume"]},
    "phases": [{"id": "01", "path": "phases/01-research.md"}],
}

_CONTEXT_CELL_OK = {
    "cell": {"row": "demo", "column": "context"},
    "ontology": {"node_types": ["ResearchTopic", "Finding"]},
}

_GATE_OK = {
    "id": "research-complete",
    "type": "hard-blocking",
    "blocks_phase": "01",
    "evaluator": {"kind": "callable", "module": "workflow.demo.gates", "callable": "is_done"},
}

_TOOL_RESULT_OK = {
    "ok": True,
    "data": {"foo": "bar"},
    "warnings": [],
    "next_suggested_tools": [],
}

_ARTEFACT_NODE_OK = {
    "content_type": "text/plain",
    "sha256": "a" * 64,
    "size_bytes": 5,
    "created_at": "2026-05-19T00:00:00Z",
    "produced_by": {"skill": "demo", "phase": "01", "session_id": "s1"},
    "derived_from": [],
    "artifact_driver": "fs",
    "driver_pointer": "result/demo/output.txt",
}

EXAMPLES: dict[str, tuple[dict, dict]] = {
    "agentic-cell.schema.json": (
        _AGENTIC_CELL_OK,
        {"cell": {"row": "demo", "column": "agentic"}},  # missing required `skills` + `tools`
    ),
    "workflow-cell.schema.json": (
        _WORKFLOW_CELL_OK,
        {"cell": {"row": "demo", "column": "workflow"}},  # missing required `workflow` + `phases`
    ),
    "context-cell.schema.json": (
        _CONTEXT_CELL_OK,
        {"cell": {"row": "demo", "column": "context"}},  # missing required `ontology`
    ),
    "gate.schema.json": (
        _GATE_OK,
        {"id": "x", "type": "hard-blocking"},  # `evaluator` required + hard-blocking needs `blocks_phase`
    ),
    "tool_result.schema.json": (
        _TOOL_RESULT_OK,
        {"ok": True, "data": "not-an-object", "warnings": [], "next_suggested_tools": []},
    ),
    "artefact-node.schema.json": (
        _ARTEFACT_NODE_OK,
        {"sha256": "a" * 64},  # missing required `content_type`, `size_bytes`, etc.
    ),
}


@pytest.mark.parametrize("filename", sorted(EXAMPLES.keys()))
def test_schema_accepts_positive_example(filename):
    schema = json.loads((SCHEMA_DIR / filename).read_text())
    positive, _ = EXAMPLES[filename]
    jsonschema.validate(instance=positive, schema=schema)


@pytest.mark.parametrize("filename", sorted(EXAMPLES.keys()))
def test_schema_rejects_negative_example(filename):
    schema = json.loads((SCHEMA_DIR / filename).read_text())
    _, negative = EXAMPLES[filename]
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=negative, schema=schema)


def test_no_orphan_schema_files():
    """Every runtime schema must have a coverage entry in EXAMPLES."""
    on_disk = {p.name for p in SCHEMA_DIR.glob("*.schema.json")}
    covered = set(EXAMPLES.keys())
    missing = on_disk - covered
    assert not missing, (
        f"Schemas in {SCHEMA_DIR} are not covered by EXAMPLES: {sorted(missing)}. "
        "Add a positive + negative example."
    )


def test_no_lingering_sidecar_filename():
    """N2 — the rename to artefact-node.schema.json must leave no stragglers."""
    assert not (SCHEMA_DIR / "sidecar.schema.json").exists()
    assert (SCHEMA_DIR / "artefact-node.schema.json").exists()
