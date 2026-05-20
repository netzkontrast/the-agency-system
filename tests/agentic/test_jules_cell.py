"""N4 — verify the agentic `jules` cell: manifest, query tool, and
discovery.

Three assertions:

1. The manifest validates against the agentic-cell schema.
2. ``agentic.jules.handlers.query.handle`` returns a result that conforms
   to the shared ``tool_result`` schema and carries the expected payload.
3. The cell loader's ``discover()`` finds the cell and registers the
   ``mcp__jules_query`` tool name.
"""

import json
from pathlib import Path

import pytest

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - fallback for older runtimes
    import tomli as tomllib

import jsonschema

from agentic._harness.cell_loader import discover


REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = REPO_ROOT / "agentic" / "jules" / "manifest.toml"
AGENTIC_CELL_SCHEMA = (
    REPO_ROOT / "context" / "_shared" / "schemas" / "agentic-cell.schema.json"
)
TOOL_RESULT_SCHEMA = (
    REPO_ROOT / "context" / "_shared" / "schemas" / "tool_result.schema.json"
)


def test_jules_manifest_validates():
    with open(MANIFEST_PATH, "rb") as f:
        manifest = tomllib.load(f)
    with open(AGENTIC_CELL_SCHEMA, "r") as f:
        schema = json.load(f)

    jsonschema.validate(instance=manifest, schema=schema)

    assert manifest["cell"]["row"] == "jules"
    assert manifest["cell"]["column"] == "agentic"
    assert manifest["skills"]["exports"] == ["research"]
    assert manifest["tools"]["exports"] == ["query"]


def test_jules_query_tool_returns_valid_envelope():
    from agentic.jules.handlers import query as query_mod

    result = query_mod.handle(topic="x")

    with open(TOOL_RESULT_SCHEMA, "r") as f:
        schema = json.load(f)
    jsonschema.validate(instance=result, schema=schema)

    assert result["ok"] is True
    assert result["data"]["topic"] == "x"
    assert isinstance(result["data"]["findings"], list)
    assert len(result["data"]["findings"]) > 0


def test_jules_cell_discoverable(monkeypatch):
    monkeypatch.chdir(REPO_ROOT)

    registry = discover(Path("."))

    assert "mcp__jules_query" in registry.tools
