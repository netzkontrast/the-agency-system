"""Validation tests for the jules workflow cell manifest.

Covers task-3 deliverables for `workflow/jules/manifest.toml` against
the updated workflow-cell schema (`context/_shared/schemas/workflow-cell.schema.json`
with the new `[workflow.lazy_link]` sub-table) — spec 07-v1 §FR1.
"""

import json
import tomllib
from pathlib import Path

import jsonschema

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "workflow" / "jules" / "manifest.toml"
SCHEMA = REPO / "context" / "_shared" / "schemas" / "workflow-cell.schema.json"


def test_jules_workflow_manifest_validates():
    """The jules workflow manifest parses and matches the updated schema."""
    assert MANIFEST.exists(), f"missing {MANIFEST}"
    data = tomllib.loads(MANIFEST.read_text(encoding="utf-8"))

    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.validate(instance=data, schema=schema)

    # The lazy_link sub-table is present and opted-out.
    assert data["workflow"]["lazy_link"]["enabled"] is False


def test_jules_workflow_entry_verbs():
    """The jules cell exports the `start` + `resume` verbs only."""
    data = tomllib.loads(MANIFEST.read_text(encoding="utf-8"))
    assert data["workflow"]["entry_verbs"] == ["start", "resume"]
