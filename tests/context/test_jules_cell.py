"""N4 — context cell for the ``jules`` row.

Asserts that:

1. ``context/jules/manifest.toml`` validates against
   ``context/_shared/schemas/context-cell.schema.json``.
2. The ``ResearchTopic`` and ``Finding`` schemas accept a canonical
   positive example and reject a canonical negative example
   (round-trip pattern from ``test_schemas_canonical.py``).
3. The ``research-brief.md.jinja`` template renders a brief that
   contains the three required H2 headings, surfaces every finding
   claim, and dedupes overlapping source URLs across findings.
"""

from __future__ import annotations

import json
import sys
import tomllib
from pathlib import Path

import jinja2
import jsonschema
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
CELL_DIR = REPO_ROOT / "context" / "jules"
SHARED_SCHEMA_DIR = REPO_ROOT / "context" / "_shared" / "schemas"


def test_jules_context_manifest_validates(monkeypatch):
    """The jules cell manifest must conform to the spec-01 cell schema."""
    monkeypatch.chdir(REPO_ROOT)

    manifest_path = CELL_DIR / "manifest.toml"
    assert manifest_path.exists(), f"missing {manifest_path}"

    with manifest_path.open("rb") as fh:
        manifest = tomllib.load(fh)

    cell_schema = json.loads(
        (SHARED_SCHEMA_DIR / "context-cell.schema.json").read_text()
    )
    jsonschema.validate(instance=manifest, schema=cell_schema)

    # Spot-check the bits downstream code will read.
    assert manifest["cell"]["row"] == "jules"
    assert manifest["cell"]["column"] == "context"
    assert "ResearchTopic" in manifest["ontology"]["node_types"]
    assert "Finding" in manifest["ontology"]["node_types"]

    # Referenced schema + template files must actually exist on disk.
    for node_type, entry in manifest["schemas"].items():
        ref = CELL_DIR / entry["path"]
        assert ref.exists(), f"schema for {node_type} missing at {ref}"
    for tmpl_name, entry in manifest["templates"].items():
        ref = CELL_DIR / entry["path"]
        assert ref.exists(), f"template {tmpl_name} missing at {ref}"


_RESEARCH_TOPIC_OK = {
    "topic": "Jules silent-fail recovery patterns",
    "created_at": "2026-05-19T12:00:00Z",
    "description": "Investigate COMPLETED-with-no-branch cases.",
    "status": "investigating",
}

# Negative: `topic` exceeds maxLength (200).
_RESEARCH_TOPIC_BAD = {
    "topic": "x" * 201,
    "created_at": "2026-05-19T12:00:00Z",
}


def test_research_topic_schema_round_trip():
    schema = json.loads(
        (CELL_DIR / "schemas" / "research-topic.schema.json").read_text()
    )
    jsonschema.validate(instance=_RESEARCH_TOPIC_OK, schema=schema)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=_RESEARCH_TOPIC_BAD, schema=schema)


_FINDING_OK = {
    "topic": "jules-silent-fail",
    "claim": "COMPLETED state does not imply a branch was pushed to origin.",
    "confidence": 0.92,
    "source_urls": [
        "https://example.com/jules-protocol#section-8",
        "https://example.com/incident-notes",
    ],
}

# Negative: confidence > 1.
_FINDING_BAD = {
    "topic": "jules-silent-fail",
    "claim": "x",
    "confidence": 1.5,
    "source_urls": ["https://example.com/x"],
}


def test_finding_schema_round_trip():
    schema = json.loads((CELL_DIR / "schemas" / "finding.schema.json").read_text())
    jsonschema.validate(instance=_FINDING_OK, schema=schema)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=_FINDING_BAD, schema=schema)


def test_research_brief_template_renders():
    template_dir = CELL_DIR / "templates"
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(template_dir)),
        autoescape=False,
        keep_trailing_newline=True,
        undefined=jinja2.StrictUndefined,
    )
    template = env.get_template("research-brief.md.jinja")

    topic = {
        "topic": "Jules silent-fail recovery patterns",
        "created_at": "2026-05-19T12:00:00Z",
        "description": "Investigate COMPLETED-with-no-branch cases.",
        "status": "investigating",
    }
    findings = [
        {
            "topic": "jules-silent-fail",
            "claim": "COMPLETED can mean idle, not done.",
            "confidence": 0.95,
            "source_urls": [
                "https://example.com/jules-protocol#section-8",
                "https://example.com/incident-notes",
            ],
        },
        {
            "topic": "jules-silent-fail",
            "claim": "Re-dispatching loses the in-flight patch.",
            "confidence": 0.7,
            "source_urls": [
                # Duplicate URL across findings — must be deduped.
                "https://example.com/jules-protocol#section-8",
                "https://example.com/respawn-risk",
            ],
        },
    ]

    rendered = template.render(topic=topic, findings=findings)

    # Required headings.
    assert "## Topic" in rendered
    assert "## Findings" in rendered
    assert "## Sources" in rendered

    # Every claim surfaces somewhere in the body.
    for finding in findings:
        assert finding["claim"] in rendered

    # Confidence formatting — two-decimal probability.
    assert "0.95" in rendered
    assert "0.70" in rendered

    # Source dedupe: the shared URL appears exactly once.
    shared_url = "https://example.com/jules-protocol#section-8"
    assert rendered.count(shared_url) == 1
    # The two unique URLs from each finding also appear.
    assert "https://example.com/incident-notes" in rendered
    assert "https://example.com/respawn-risk" in rendered

    # Sources section actually contains the URLs (sanity: they fall
    # below the heading rather than only appearing earlier in the body).
    sources_idx = rendered.index("## Sources")
    assert shared_url in rendered[sources_idx:]
    assert "https://example.com/respawn-risk" in rendered[sources_idx:]
