import pytest
from pathlib import Path
from agentic._harness.name_deriver import (
    ManifestLintError,
    skill_name,
    mcp_tool_name,
    skill_md_path,
    handler_module,
    _assert_no_row_prefix,
)


def test_derivation_rules():
    assert skill_name("music", "producer") == "music-producer"
    assert mcp_tool_name("music", "analysis") == "mcp__music_analysis"
    assert skill_md_path("music", "producer") == Path(
        "agentic/music/skills/producer/SKILL.md"
    )
    assert handler_module("music", "analysis") == "agentic.music.handlers.analysis"


def test_redundant_row_prefix_is_rejected():
    with pytest.raises(ManifestLintError) as exc:
        skill_name("music", "music-producer")
    assert "must not contain the row prefix" in str(exc.value)

    with pytest.raises(ManifestLintError) as exc:
        mcp_tool_name("music", "music_analysis")
    assert "must not contain the row prefix" in str(exc.value)
