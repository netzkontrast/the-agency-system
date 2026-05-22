import pytest
from agency_mcp.handlers.novel._shared import STATUS_TRANSITIONS

def test_transition_table_valid_paths():
    # Work level
    assert "review" in STATUS_TRANSITIONS["work"]["in_progress"]
    assert "done" in STATUS_TRANSITIONS["work"]["review"]
    assert "archived" in STATUS_TRANSITIONS["work"]["done"]

def test_transition_table_invalid_paths():
    # Work level explicitly rejects done -> review
    assert "review" not in STATUS_TRANSITIONS["work"]["done"]
    # Work level explicitly rejects archived -> draft
    assert "draft" not in STATUS_TRANSITIONS["work"]["archived"]
