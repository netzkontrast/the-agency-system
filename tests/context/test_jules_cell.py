import json
from pathlib import Path
import jsonschema
import pytest
from jinja2 import Environment, FileSystemLoader

JULES_CELL_DIR = Path(__file__).resolve().parents[2] / "context" / "jules"
SCHEMA_DIR = Path(__file__).resolve().parents[2] / "context" / "_shared" / "schemas"

def test_jules_context_manifest_validates():
    try:
        import tomli as tomllib
    except ImportError:
        import tomllib

    with open(JULES_CELL_DIR / "manifest.toml", "rb") as f:
        manifest = tomllib.load(f)

    with open(SCHEMA_DIR / "context-cell.schema.json") as f:
        schema = json.load(f)

    jsonschema.validate(instance=manifest, schema=schema)

_RESEARCH_TOPIC_OK = {
    "topic": "The mating habits of the giant squid",
    "created_at": "2026-05-19T00:00:00Z",
    "description": "A comprehensive study",
    "status": "investigating"
}

_FINDING_OK = {
    "topic": "The mating habits of the giant squid",
    "claim": "They mate in the deep sea.",
    "confidence": 0.95,
    "source_urls": ["https://example.com/squid"]
}

EXAMPLES = {
    "research-topic.schema.json": (
        _RESEARCH_TOPIC_OK,
        {"topic": "Missing created_at"}
    ),
    "finding.schema.json": (
        _FINDING_OK,
        {"claim": "Missing topic", "confidence": 0.5, "source_urls": []}
    )
}

@pytest.mark.parametrize("filename", EXAMPLES.keys())
def test_schema_accepts_positive_example(filename):
    schema_path = JULES_CELL_DIR / "schemas" / filename
    schema = json.loads(schema_path.read_text())
    positive, _ = EXAMPLES[filename]
    jsonschema.validate(instance=positive, schema=schema)

@pytest.mark.parametrize("filename", EXAMPLES.keys())
def test_schema_rejects_negative_example(filename):
    schema_path = JULES_CELL_DIR / "schemas" / filename
    schema = json.loads(schema_path.read_text())
    _, negative = EXAMPLES[filename]
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=negative, schema=schema)

def test_research_brief_template_renders():
    env = Environment(loader=FileSystemLoader(str(JULES_CELL_DIR / "templates")))
    template = env.get_template("research-brief.md.jinja")

    output = template.render(topic=_RESEARCH_TOPIC_OK, findings=[_FINDING_OK])

    assert "Topic" in output
    assert "Findings" in output
    assert "Sources" in output
    assert "https://example.com/squid" in output
    assert "giant squid" in output
