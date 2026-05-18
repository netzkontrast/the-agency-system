import os
import sys
from pathlib import Path

def test_indexer_skills_count_is_at_least_one():
    from agency_mcp.tools.state.indexer import scan_skills, _PROJECT_ROOT
    res = scan_skills(_PROJECT_ROOT)
    assert res["count"] >= 1
