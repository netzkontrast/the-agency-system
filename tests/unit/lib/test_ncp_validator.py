from agency_mcp.lib.ncp.validator import validate
from agency_mcp.lib.ncp.compiler import compile

# 012.5
def test_ncp_compiler_compile_produces_doc_that_validator_accepts(tmp_path):
    # scaffold work_dir
    work_dir = tmp_path / "novel"
    work_dir.mkdir()

    (work_dir / "dramatica.md").write_text("---\ntype: novel.dramatica\nauthor_slug: \"auth\"\nwork_slug: \"work\"\nresolve: \"character-dynamic.resolve\"\n---\n")
    (work_dir / "cast.md").write_text("---\ntype: novel.cast\nauthor_slug: \"auth\"\nwork_slug: \"work\"\n---\n")
    (work_dir / "premise.md").write_text("---\ntype: novel.premise\nauthor_slug: \"auth\"\nwork_slug: \"work\"\ntitle: \"My Title\"\nlogline: \"My Logline\"\n---\n")

    doc = compile(work_dir, write=False)

    # We test the schema keys according to real schema, but let's just make sure "story" is there.
    assert "story" in doc
    assert "schema_version" in doc
    assert "narratives" in doc["story"]

    res = validate(doc)
    assert res["ok"] is True
    assert len(res["errors"]) == 0

# 012.6
def test_ncp_validator_reports_errors_without_raising():
    # Hand-crafted doc that omits the required 'story' key
    doc = {
        "schema_version": "1.3.0"
        # missing 'story'
    }

    # We should catch this as an error, not an exception
    res = validate(doc)

    assert res["ok"] is False
    assert len(res["errors"]) > 0
    # Must contain human readable validation error
    assert any("story" in str(e) for e in res["errors"])
