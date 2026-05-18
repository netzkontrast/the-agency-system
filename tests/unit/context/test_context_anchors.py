import pytest
from agency_mcp.lib.codemode.context_anchor_triad import (
    ContextNotFound,
    _context_search,
    _context_describe,
    _context_read
)
from agency_mcp.lib.codemode.context_manifest import ContextManifest

@pytest.fixture
def mock_manifest():
    data = {
        "entries": [
            {
                "id": "spec:001",
                "title": "Spec 001",
                "summary": "First spec",
                "tags": ["domain:cross", "spec:001"],
                "path": "Plan/001-spec/spec.md",
                "mime": "text/markdown",
                "size_bytes": 100,
                "views": {
                    "summary": {"byte_offset": 0, "byte_length": 20, "token_estimate": 10},
                    "preview": {"byte_offset": 0, "byte_length": 50, "token_estimate": 25},
                    "full": {"byte_offset": 0, "byte_length": 100, "token_estimate": 50}
                }
            },
            {
                "id": "reference:ontology",
                "title": "Ontology",
                "summary": "JSON Ontology",
                "tags": ["domain:novel"],
                "path": "reference/ontology.json",
                "mime": "application/json",
                "size_bytes": 10000,
                "views": {
                    "summary": {"byte_offset": 0, "byte_length": 100, "token_estimate": 20},
                    "preview": {"byte_offset": 0, "byte_length": 500, "token_estimate": 100},
                    "full": {"byte_offset": 0, "byte_length": 10000, "token_estimate": 5000}
                }
            },
            {
                "id": "lesson:001",
                "title": "Lesson 001",
                "summary": "A tiny lesson",
                "tags": ["domain:music"],
                "path": "Plan/_lessons-learned/001.md",
                "mime": "text/markdown",
                "size_bytes": 40,
                "views": {
                    "full": {"byte_offset": 0, "byte_length": 40, "token_estimate": 15}
                }
            }
        ]
    }
    return ContextManifest.from_dict(data)

def test_search_returns_at_most_limit_entries(mock_manifest):
    results = _context_search("spec", mock_manifest, limit=1)
    assert len(results) == 1

def test_describe_includes_views_block(mock_manifest):
    desc = _context_describe("spec:001", mock_manifest)
    assert "views" in desc
    assert "summary" in desc["views"]
    assert "preview" in desc["views"]
    assert "full" in desc["views"]

def test_read_summary_view_under_120_tokens(mock_manifest, tmp_path):
    repo_root = tmp_path
    mock_manifest.repo_root = str(repo_root)
    file_path = repo_root / "Plan/001-spec/spec.md"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text("A" * 100)

    result = _context_read("spec:001", mock_manifest, view="summary")
    assert result["token_estimate"] <= 120
    assert result["view"] == "summary"

def test_read_full_truncates_when_over_4000_tokens(mock_manifest, tmp_path):
    repo_root = tmp_path
    mock_manifest.repo_root = str(repo_root)
    file_path = repo_root / "reference/ontology.json"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text("A" * 10000)

    result = _context_read("reference:ontology", mock_manifest, view="full")
    assert result["truncated"] is True
    assert result["body"].endswith("… [truncated; ask for fields= or read direct file]")
    assert result["token_estimate"] <= 4100

def test_read_with_fields_projects_json(mock_manifest, tmp_path):
    repo_root = tmp_path
    mock_manifest.repo_root = str(repo_root)
    file_path = repo_root / "reference/ontology.json"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text('{"meta": {"version": 1}, "classes": []}')

    result = _context_read("reference:ontology", mock_manifest, view="full", fields=["meta"])
    import json
    body_json = json.loads(result["body"])
    assert "meta" in body_json
    assert "classes" not in body_json
    assert result["token_estimate"] < 5000

def test_read_unknown_id_raises_context_not_found(mock_manifest):
    with pytest.raises(ContextNotFound):
        _context_read("unknown:id", mock_manifest)

def test_read_missing_view_falls_back_gracefully(mock_manifest, tmp_path):
    repo_root = tmp_path
    mock_manifest.repo_root = str(repo_root)
    file_path = repo_root / "Plan/_lessons-learned/001.md"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text("Small file")

    result = _context_read("lesson:001", mock_manifest, view="preview")
    # Should fall back to 'full' since preview isn't defined
    assert result["view"] == "full"
