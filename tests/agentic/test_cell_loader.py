import pytest
from pathlib import Path
from agentic._harness.cell_loader import discover
import sys
import importlib


@pytest.fixture
def empty_matrix(tmp_path):
    import os

    orig_dir = os.getcwd()
    os.chdir(tmp_path)
    yield tmp_path
    os.chdir(orig_dir)


@pytest.fixture
def synthetic_matrix(tmp_path):
    import os

    orig_dir = os.getcwd()
    os.chdir(tmp_path)

    agentic_music = tmp_path / "agentic" / "music"
    agentic_music.mkdir(parents=True)
    (agentic_music / "manifest.toml").write_text("""
[cell]
row    = "music"
column = "agentic"

[skills]
exports = ["producer"]

[tools]
exports = ["analysis"]

[codemode]
prefers = ["analysis"]
""")

    # We need to make sure the dynamically loaded module exists
    # Create agentic.music.handlers package
    (tmp_path / "agentic" / "__init__.py").touch()
    (tmp_path / "agentic" / "music" / "__init__.py").touch()
    (tmp_path / "agentic" / "music" / "handlers").mkdir(parents=True)
    (tmp_path / "agentic" / "music" / "handlers" / "__init__.py").touch()
    (tmp_path / "agentic" / "music" / "handlers" / "analysis.py").write_text("""
def handle(**kwargs):
    return {"ok": True, "data": {"message": "Dynamic handle called"}, "warnings": [], "next_suggested_tools": []}
""")

    # We use a custom package root instead of appending to sys.path which might resolve to the real agentic/
    # if it's earlier in the PYTHONPATH

    yield tmp_path
    os.chdir(orig_dir)


def test_cell_loader_scans_all_columns(synthetic_matrix):
    registry = discover(synthetic_matrix)

    assert "mcp__music_analysis" in registry.get_all_tool_names()
    assert "/music-producer" in registry.get_all_skill_names()
    assert "mcp__music_analysis" in registry.codemode_set

    # We mock the import to avoid modifying sys.modules since agentic is already loaded as our package.
    # We can override the tool wrapper for testing the discovery.
    # The actual importlib behavior is standard python, we just test that the loader sets up the closure correctly.
    # The registry.tools should map to the tool_wrapper. We can mock importlib.import_module.

    from unittest.mock import patch

    with patch("importlib.import_module") as mock_import:
        mock_mod = type(
            "MockMod",
            (),
            {
                "handle": lambda **kwargs: {
                    "ok": True,
                    "data": {"message": "Mocked handle called"},
                    "warnings": [],
                    "next_suggested_tools": [],
                }
            },
        )
        mock_import.return_value = mock_mod

        result = registry.call_tool("mcp__music_analysis", {})
        assert result.get("prefers_codemode") is True
        assert result.get("data") == {"message": "Mocked handle called"}
        mock_import.assert_called_with("agentic.music.handlers.analysis")


def test_redundant_prefix_rejected(tmp_path):
    import os

    orig_dir = os.getcwd()
    os.chdir(tmp_path)

    agentic_music = tmp_path / "agentic" / "music"
    agentic_music.mkdir(parents=True)
    (agentic_music / "manifest.toml").write_text("""
[cell]
row    = "music"
column = "agentic"

[skills]
exports = ["music-producer"]
""")

    registry = discover(tmp_path)
    assert "/music-music-producer" not in registry.get_all_skill_names()
    assert len(registry.get_all_skill_names()) == 0

    os.chdir(orig_dir)
