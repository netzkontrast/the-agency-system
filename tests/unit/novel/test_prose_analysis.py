import pytest
from agency_mcp.handlers.novel.prose_analysis import novel_analyze_readability, novel_analyze_rhythm, novel_scan_pov_violations

def test_analyze_readability():
    res = novel_analyze_readability("This is a simple text. It has short sentences.")
    assert "flesch" in res
    assert "fog" in res

def test_analyze_rhythm():
    res = novel_analyze_rhythm("Short. Another short one. But then comes a much longer sentence that might indicate poor rhythm or simply variance.")
    assert "variance" in res

def test_scan_pov_violations():
    res = novel_scan_pov_violations("Anna looked out the window. Across the street, John felt a pang of guilt he would never admit.", "3rd_limited", "Anna")
    assert len(res) > 0
    assert res[0]["violation_type"] == "head_hop"
