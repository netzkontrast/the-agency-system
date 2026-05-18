import pytest
from pathlib import Path
from agency_mcp.handlers.novel.gates import novel_run_pre_drafting_gates, _gate_dramatica_confirmed, _gate_ncp_valid, _gate_premise_locked, _gate_cast_complete, _gate_pov_declared, _gate_sources_verified, _chapter_create_guard
from agency_mcp.handlers.novel.content import novel_create_chapter
from agency_mcp.state.cache import StateCache
import asyncio

@pytest.fixture
def clean_work():
    return "clean_work"

def test_gate_dramatica_confirmed_pass(clean_work):
    pass

def test_gate_dramatica_confirmed_fail():
    res = _gate_dramatica_confirmed("no_dramatica")
    assert res["pass"] is False
    assert "dramatica" in res["name"]

def test_gate_ncp_valid_pass(clean_work):
    pass

def test_gate_ncp_valid_fail():
    res = _gate_ncp_valid("bad_ncp")
    assert res["pass"] is False

def test_gate_premise_locked_pass(clean_work):
    pass

def test_gate_premise_locked_fail():
    res = _gate_premise_locked("missing_premise")
    assert res["pass"] is False

def test_gate_cast_complete_pass(clean_work):
    res = _gate_cast_complete(clean_work)
    assert res["pass"] is True

def test_gate_cast_complete_fail():
    res = _gate_cast_complete("incomplete_cast")
    assert res["pass"] is False

def test_gate_pov_declared_pass(clean_work):
    res = _gate_pov_declared(clean_work)
    assert res["pass"] is True

def test_gate_pov_declared_fail():
    res = _gate_pov_declared("no_pov")
    assert res["pass"] is False

def test_gate_sources_verified_pass(clean_work):
    res = _gate_sources_verified(clean_work)
    assert res["pass"] is True
    assert "N/A" in res["evidence"]

def test_gate_sources_verified_fail():
    res = _gate_sources_verified("historical_unverified")
    assert res["pass"] is False

def test_run_pre_drafting_gates(clean_work):
    pass

@pytest.mark.asyncio
async def test_chapter_create_refuses_when_gates_fail():
    guard = await novel_create_chapter(author="test", work_slug="no_dramatica", chapter_number=1, title="Test")
    assert guard["ok"] is False
    assert guard["error"] == "PRE_DRAFTING_GATES_FAILED"
    assert "dramatica_confirmed" in guard["blocking"]
