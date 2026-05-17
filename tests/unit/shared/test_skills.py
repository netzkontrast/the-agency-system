import pytest
from unittest.mock import patch

from agency_mcp.handlers.shared.skills import plugin_help, shared_list_skills, shared_get_skill

def test_plugin_help_unknown_domain():
    result = plugin_help("does-not-exist")
    assert result["ok"] is False
    assert "unknown domain: does-not-exist" in result["warnings"][0]

@patch("agency_mcp.handlers.shared.skills.shared_list_skills")
@patch("pathlib.Path.exists")
@patch("pathlib.Path.read_text")
def test_plugin_help_music(mock_read_text, mock_exists, mock_list_skills):
    mock_exists.return_value = True
    mock_read_text.return_value = "Music Prologue"
    mock_list_skills.return_value = {
        "ok": True,
        "data": [
            {"name": "music-lyric-writer", "summary": "Writes lyrics"}
        ],
        "warnings": []
    }

    result = plugin_help("music")
    assert result["ok"] is True
    assert result["data"].startswith("# /agency-system:music-*")
    assert "Writes lyrics" in result["data"]

def test_shared_list_skills():
    pass
    # We will implement more tests as we iterate.
