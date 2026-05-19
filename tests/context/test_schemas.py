import json
import jsonschema
import pytest
from pathlib import Path

def test_json_schemas_validate_sample_manifests():
    # Scenario: JSON Schemas validate sample manifests from spec 01
    agentic_schema_path = Path("context/_shared/schemas/agentic-cell.schema.json")
    workflow_schema_path = Path("context/_shared/schemas/workflow-cell.schema.json")
    context_schema_path = Path("context/_shared/schemas/context-cell.schema.json")

    with open(agentic_schema_path) as f:
        agentic_schema = json.load(f)
    with open(workflow_schema_path) as f:
        workflow_schema = json.load(f)
    with open(context_schema_path) as f:
        context_schema = json.load(f)

    agentic_manifest = {
        "cell": {"row": "music", "column": "agentic"},
        "skills": {"exports": ["producer", "master"]},
        "tools": {"exports": ["analysis", "synthesis", "review"]}
    }

    workflow_manifest = {
        "cell": {"row": "music", "column": "workflow"},
        "workflow": {"entry_verbs": ["scaffold", "start", "resume"]},
        "phases": [
            {"id": "01", "path": "phases/01-concept.md"},
            {"id": "02", "path": "phases/02-lyrics.md"}
        ],
        "gates": [
            {"id": "lyrics-reviewed", "path": "gates/lyrics-reviewed.yaml", "blocks_phase": "03"}
        ],
        "artefacts": {"produced": ["track.mp3"]}
    }

    context_manifest = {
        "cell": {"row": "music", "column": "context"},
        "ontology": {"node_types": ["Track", "Album", "LyricSheet"]},
        "templates": {"lyric_sheet": {"path": "templates/lyric_sheet.md.jinja"}},
        "schemas": {"track_meta": {"path": "schemas/track.schema.json"}},
        "storage": {"vault_root": "result/music"}
    }

    jsonschema.validate(instance=agentic_manifest, schema=agentic_schema)
    jsonschema.validate(instance=workflow_manifest, schema=workflow_schema)
    jsonschema.validate(instance=context_manifest, schema=context_schema)
