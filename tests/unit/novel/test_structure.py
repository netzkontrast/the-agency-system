import pytest
from agency_mcp.handlers.novel.structure import novel_check_slot_fill, novel_check_throughline_partition, novel_check_crucial_element_placement

def test_check_slot_fill():
    res = novel_check_slot_fill("good_work")
    assert res["status"] == "PASS"

def test_check_throughline_partition():
    res = novel_check_throughline_partition("good_work")
    assert res["status"] == "PASS"

def test_check_crucial_element_placement():
    res = novel_check_crucial_element_placement("good_work")
    assert res["status"] == "PASS"
