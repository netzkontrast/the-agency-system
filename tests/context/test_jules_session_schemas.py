"""Schema round-trip tests for the JulesSession + SessionPatch nodes.

The jules row's orchestration handlers (dispatch / await_plan / monitor
/ verify / recover / integrate) upsert these nodes — the schemas guard
the state machine's contract: a JulesSession.state must be one of the
declared enum members, and SessionPatch line counts must be
non-negative integers.
"""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
CELL_DIR = REPO_ROOT / "context" / "jules"


_JULES_SESSION_OK = {
    "session_id": "9123456789",
    "state": "DISPATCHED",
    "title": "Refactor sidecars",
    "owner": "netzkontrast",
    "repo": "the-agency-system",
    "branch": "Master",
    "prompt": "Refactor the sidecar metadata module.",
    "url": "https://jules.google.com/session/9123456789",
    "created_at": 1764643200,
    "jules_state": "IN_PROGRESS",
}


_JULES_SESSION_BAD_STATE = {**_JULES_SESSION_OK, "state": "NOT_A_REAL_STATE"}


def test_jules_session_schema_round_trip():
    schema = json.loads((CELL_DIR / "schemas" / "jules-session.schema.json").read_text())
    jsonschema.validate(instance=_JULES_SESSION_OK, schema=schema)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=_JULES_SESSION_BAD_STATE, schema=schema)


_SESSION_PATCH_OK = {
    "session_id": "9123456789",
    "files": ["agentic/jules/handlers/dispatch.py"],
    "lines_added": 42,
    "lines_removed": 7,
    "patch_bytes": 2048,
    "base_commit": "abc123",
    "suggested_commit_message": "feat(agency): wire dispatch",
    "extracted_at": 1764643500,
}


_SESSION_PATCH_BAD = {**_SESSION_PATCH_OK, "lines_added": -1}


def test_session_patch_schema_round_trip():
    schema = json.loads((CELL_DIR / "schemas" / "session-patch.schema.json").read_text())
    jsonschema.validate(instance=_SESSION_PATCH_OK, schema=schema)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=_SESSION_PATCH_BAD, schema=schema)


def test_state_machine_terminal_states_in_enum():
    """Every state the row's handlers can write must appear in the schema enum."""
    schema = json.loads((CELL_DIR / "schemas" / "jules-session.schema.json").read_text())
    states = set(schema["properties"]["state"]["enum"])

    # State labels reachable from the orchestration handlers.
    expected = {
        "DISPATCHED",
        "IN_PROGRESS",
        "AWAITING_PLAN_APPROVAL",
        "COMPLETED",
        "VERIFIED",
        "SILENT_FAIL",
        "PATCH_EXTRACTED",
        "APPLIED",
        "FAILED",
    }
    assert expected.issubset(states), f"missing: {expected - states}"


def test_jules_context_manifest_declares_new_node_types():
    """The manifest must declare JulesSession + SessionPatch alongside the
    existing research-oriented types so the spec-01 cell schema sees them."""
    try:
        import tomllib
    except ModuleNotFoundError:  # pragma: no cover
        import tomli as tomllib
    manifest = tomllib.loads((CELL_DIR / "manifest.toml").read_text())
    assert "JulesSession" in manifest["ontology"]["node_types"]
    assert "SessionPatch" in manifest["ontology"]["node_types"]
    assert manifest["schemas"]["JulesSession"]["path"].endswith("jules-session.schema.json")
    assert manifest["schemas"]["SessionPatch"]["path"].endswith("session-patch.schema.json")
