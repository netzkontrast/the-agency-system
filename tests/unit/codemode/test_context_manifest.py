import pytest
import os
import tempfile
import json
from pathlib import Path
from agency_mcp.lib.codemode.context_manifest import load_context_manifest, ContextManifestError, ContextManifest
from agency_mcp.lib.codemode.context_indexer import extract_summary

FIXTURE_DIR = Path("tests/unit/codemode/fixtures/context_corpus")

def test_schema_rejects_unknown_tag_prefix():
    manifest_data = {
        "entries": [{
            "id": "test:id",
            "title": "Title",
            "summary": "Summary",
            "tags": ["random-string"],
            "path": "test/id.md",
            "mime": "text/markdown",
            "size_bytes": 10,
            "last_modified": "2026-05-01T00:00:00Z",
            "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "views": {
                "summary": {"token_estimate": 10},
                "preview": {"token_estimate": 20},
                "full": {"token_estimate": 30}
            }
        }]
    }
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(manifest_data, f)
        temp_path = f.name

    try:
        with pytest.raises(ContextManifestError) as exc:
            load_context_manifest(temp_path)
        assert "random-string" in str(exc.value)
        assert any(p in str(exc.value) for p in ["domain:", "kind:", "topic:", "spec:", "slug:", "lesson_id:"])
    finally:
        os.unlink(temp_path)

def test_summary_extraction_is_deterministic():
    plan_path = FIXTURE_DIR / "plan_sample.md"
    body = plan_path.read_text()

    summary1 = extract_summary(str(plan_path), body)
    summary2 = extract_summary(str(plan_path), body)

    assert summary1 == summary2
    assert "Spec 111" in summary1
    assert "manifest half" in summary1
    assert len(summary1) <= 400

def test_id_collision_raises():
    import subprocess
    import sys

    with tempfile.TemporaryDirectory() as d:
        p = Path(d)
        (p / "Plan").mkdir()
        (p / "Plan/dir1").mkdir()

        # In build script, ID is based on relative path from root.
        # But wait, if two files map to the same id?
        # Actually, if I write to Plan/docs/a.md and Plan/docs/a.json?
        # They map to the same id: plan:docs:a! That's a perfect collision.
        with open(p / "Plan/collision.md", "w") as f:
            f.write("# A\nbody")
        with open(p / "Plan/collision.json", "w") as f:
            f.write('{"title": "B"}')

        cmd = [sys.executable, "servers/agency-mcp/bin/build_context_manifest.py", "--root", d, "--out", f"{d}/out.json"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        assert res.returncode != 0
        assert "duplicate" in res.stderr.lower() or "collision" in res.stderr.lower()

def test_check_mode_detects_stale_sha256():
    import subprocess
    import sys

    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "Plan" / "docs"
        p.mkdir(parents=True)
        f_path = p / "test.md"
        f_path.write_text("# Test\ncontent")

        out_path = Path(d) / "manifest.json"

        # Build first time
        cmd = [sys.executable, "servers/agency-mcp/bin/build_context_manifest.py", "--root", d, "--out", str(out_path)]
        subprocess.run(cmd, check=True)

        # Mutate
        f_path.write_text("# Test\nmutated content")

        # Check mode
        cmd = [sys.executable, "servers/agency-mcp/bin/build_context_manifest.py", "--root", d, "--out", str(out_path), "--check"]
        res = subprocess.run(cmd, capture_output=True, text=True)

        assert res.returncode == 1
        assert "drift" in res.stderr.lower() or "sha256" in res.stderr.lower()
        assert "test.md" in res.stderr

def test_search_ranks_title_match_above_body_match():
    manifest_data = {
        "entries": [
            {
                "id": "plan:012-dramatica-and-ncp-libs:spec",
                "title": "Spec 012",
                "summary": "Dramatica spec",
                "tags": ["topic:dramatica"],
                "path": "plan/012.md",
                "mime": "text/markdown",
                "size_bytes": 100,
                "last_modified": "2026-05-01T00:00:00Z",
                "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                "views": {
                    "summary": {"token_estimate": 10}, "preview": {"token_estimate": 20}, "full": {"token_estimate": 30}
                }
            },
            {
                "id": "other",
                "title": "Other",
                "summary": "A file that only mentions dramatica incidentally.",
                "tags": [],
                "path": "other.md",
                "mime": "text/markdown",
                "size_bytes": 100,
                "last_modified": "2026-05-01T00:00:00Z",
                "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                "views": {
                    "summary": {"token_estimate": 10}, "preview": {"token_estimate": 20}, "full": {"token_estimate": 30}
                }
            }
        ]
    }

    manifest = ContextManifest.from_dict(manifest_data)
    results = manifest.search("dramatica", limit=5)

    assert len(results) > 0
    assert results[0]["id"] == "plan:012-dramatica-and-ncp-libs:spec"
    assert "score" in results[0]

def test_search_filters_by_domain_and_tags():
    manifest_data = {
        "entries": [
            {
                "id": "doc1",
                "title": "Doc1",
                "summary": "sum",
                "tags": ["domain:music", "kind:spec"],
                "path": "doc1.md",
                "mime": "text/markdown",
                "size_bytes": 10, "last_modified": "2026-05-01T00:00:00Z", "sha256": "e3b",
                "views": { "summary": {"token_estimate": 1}, "preview": {"token_estimate": 2}, "full": {"token_estimate": 3} }
            },
            {
                "id": "doc2",
                "title": "Doc2",
                "summary": "sum",
                "tags": ["domain:music", "kind:lesson"],
                "path": "doc2.md",
                "mime": "text/markdown",
                "size_bytes": 10, "last_modified": "2026-05-01T00:00:00Z", "sha256": "e3b",
                "views": { "summary": {"token_estimate": 1}, "preview": {"token_estimate": 2}, "full": {"token_estimate": 3} }
            },
             {
                "id": "doc3",
                "title": "Doc3",
                "summary": "sum",
                "tags": ["domain:novel", "kind:spec"],
                "path": "doc3.md",
                "mime": "text/markdown",
                "size_bytes": 10, "last_modified": "2026-05-01T00:00:00Z", "sha256": "e3b",
                "views": { "summary": {"token_estimate": 1}, "preview": {"token_estimate": 2}, "full": {"token_estimate": 3} }
            }
        ]
    }
    manifest = ContextManifest.from_dict(manifest_data)

    # Filter by domain only
    results = manifest.search("sum", domain="music")
    assert len(results) == 2
    assert {r["id"] for r in results} == {"doc1", "doc2"}

    # Filter by tags only
    results = manifest.search("sum", tags=["kind:spec"])
    assert len(results) == 2
    assert {r["id"] for r in results} == {"doc1", "doc3"}

    # Composite filter
    results = manifest.search("sum", domain="music", tags=["kind:spec"])
    assert len(results) == 1
    assert results[0]["id"] == "doc1"

def test_missing_file_in_manifest_fails_validation():
    manifest_data = {
        "entries": [{
            "id": "test:id",
            "title": "Title",
            "summary": "Summary",
            "tags": ["domain:music"],
            "path": "test/missing_file.md",
            "mime": "text/markdown",
            "size_bytes": 10,
            "last_modified": "2026-05-01T00:00:00Z",
            "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "views": {
                "summary": {"token_estimate": 10},
                "preview": {"token_estimate": 20},
                "full": {"token_estimate": 30}
            }
        }]
    }
    with tempfile.TemporaryDirectory() as d:
        manifest_path = Path(d) / "manifest.json"
        with open(manifest_path, "w") as f:
            json.dump(manifest_data, f)

        manifest = ContextManifest.from_dict(manifest_data, repo_root=d)
        with pytest.raises(ContextManifestError) as exc:
            manifest.validate_against_schema()
        assert "missing_file.md" in str(exc.value)

def test_view_token_budgets_are_enforced():
    manifest_data = {
        "entries": [{
            "id": "test:id",
            "title": "Title",
            "summary": "Summary",
            "tags": ["domain:music"],
            "path": "test/id.md",
            "mime": "text/markdown",
            "size_bytes": 10,
            "last_modified": "2026-05-01T00:00:00Z",
            "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "views": {
                "summary": {"token_estimate": 121}, # Exceeds budget
                "preview": {"token_estimate": 20},
                "full": {"token_estimate": 30}
            }
        }]
    }
    with tempfile.TemporaryDirectory() as d:
        manifest_path = Path(d) / "manifest.json"
        with open(manifest_path, "w") as f:
            json.dump(manifest_data, f)

        # create mock file
        os.makedirs(Path(d) / "test", exist_ok=True)
        with open(Path(d) / "test" / "id.md", "w") as f:
            f.write("content")

        manifest = ContextManifest.from_dict(manifest_data, repo_root=d)
        with pytest.raises(ContextManifestError) as exc:
            manifest.validate_against_schema()
        assert "token budget" in str(exc.value) or "views.summary.token_estimate" in str(exc.value)
