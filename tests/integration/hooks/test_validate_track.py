import pytest
import subprocess
import os

def test_valid_track():
    result = subprocess.run(
        ["python3", "hooks/validate_track.py", "tests/fixtures/hooks/tracks/valid_track.md"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert result.stderr == ""

def test_malformed_track():
    result = subprocess.run(
        ["python3", "hooks/validate_track.py", "tests/fixtures/hooks/tracks/malformed_track.md"],
        capture_output=True,
        text=True
    )
    assert result.returncode != 0
    assert "Missing required frontmatter field: track_number" in result.stderr
    assert "Invalid status 'Invalid Status'" in result.stderr
