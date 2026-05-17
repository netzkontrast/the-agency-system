import pytest
from unittest.mock import patch, MagicMock

from jules_mcp.tools.patches import (
    _parse_diff_header_b_path,
    _parse_diff_metadata,
    jules_patch_apply,
)


def test_parse_diff_header_b_path():
    # Unquoted form
    assert _parse_diff_header_b_path("diff --git a/path/to/file.txt b/path/to/file.txt") == "path/to/file.txt"
    # Quoted form
    assert _parse_diff_header_b_path('diff --git "a/path with spaces.txt" "b/path with spaces.txt"') == "path with spaces.txt"
    # Edge case: quotes with escapes inside
    assert _parse_diff_header_b_path('diff --git "a/path \\"with\\" spaces.txt" "b/path \\"with\\" spaces.txt"') == 'path \\"with\\" spaces.txt'
    # Missing form
    assert _parse_diff_header_b_path("diff --git") is None
    # Invalid form
    assert _parse_diff_header_b_path('diff --git "a/path/with/unclosed') is None
    # No b/ prefix
    assert _parse_diff_header_b_path("diff --git a/file b/file") == "file"


def test_parse_diff_metadata():
    patch_text = """diff --git a/file1.py b/file1.py
index e69de29..d95f3ad 100644
--- a/file1.py
+++ b/file1.py
@@ -0,0 +1,2 @@
+line1
+line2
diff --git a/file2.py b/file2.py
index e69de29..d95f3ad 100644
--- a/file2.py
+++ b/file2.py
@@ -1,2 +0,0 @@
-line1
-line2
"""
    meta = _parse_diff_metadata(patch_text)
    assert meta["files"] == ["file1.py", "file2.py"]
    assert meta["lines_added"] == 2
    assert meta["lines_removed"] == 2


@patch("jules_mcp.tools.patches._fetch_patch")
@patch("jules_mcp.tools.patches.subprocess.run")
def test_jules_patch_apply_only_files(mock_run, mock_fetch):
    patch_text = """diff --git a/file1.py b/file1.py
index e69de29..d95f3ad 100644
--- a/file1.py
+++ b/file1.py
@@ -0,0 +1,2 @@
+line1
+line2
diff --git a/file2.py b/file2.py
index e69de29..d95f3ad 100644
--- a/file2.py
+++ b/file2.py
@@ -1,2 +0,0 @@
-line1
-line2
"""
    mock_fetch.return_value = {
        "patch": patch_text,
        "base_commit": "abc",
        "suggested_commit_message": "test",
    }
    
    # Mock subprocess success
    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

    res = jules_patch_apply("sess_123", only_files="file1.py")
    assert res["applied"] is True
    assert res["files"] == ["file1.py"]
    assert res["lines_added"] == 2
    assert res["lines_removed"] == 0

    # Test error when file not in patch
    res = jules_patch_apply("sess_123", only_files="file3.py")
    assert res["applied"] is False
    assert "error" in res

