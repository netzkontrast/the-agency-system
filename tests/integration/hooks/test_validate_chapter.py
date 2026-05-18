import pytest
import subprocess
import json

def test_valid_chapter():
    result = subprocess.run(
        ["python3", "hooks/validate_chapter.py", "tests/fixtures/hooks/chapters/valid_chapter.md"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert result.stderr == ""

def test_malformed_chapter():
    result = subprocess.run(
        ["python3", "hooks/validate_chapter.py", "tests/fixtures/hooks/chapters/malformed_chapter.md"],
        capture_output=True,
        text=True
    )
    assert result.returncode != 0

    # Parse json lines
    lines = [line for line in result.stderr.split("\n") if line.strip()]
    errors = [json.loads(line) for line in lines]

    # Check specific errors
    fields_with_errors = [e["field"] for e in errors]
    assert "chapter_number" in fields_with_errors
    assert "pov" in fields_with_errors
    assert "scene_ids" in fields_with_errors
    assert "ncp_link" in fields_with_errors
