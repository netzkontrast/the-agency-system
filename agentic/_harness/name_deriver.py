import re
from pathlib import Path


class ManifestLintError(Exception):
    """Raised when a manifest breaks derivation rules."""

    pass


def _assert_no_row_prefix(row: str, export: str) -> None:
    if export.startswith(f"{row}-") or export.startswith(f"{row}_"):
        raise ManifestLintError(
            f"Export '{export}' must not contain the row prefix '{row}'."
        )


def skill_name(row: str, export: str) -> str:
    """('music','producer') -> 'music-producer'."""
    _assert_no_row_prefix(row, export)
    return f"{row}-{export}"


def mcp_tool_name(row: str, export: str) -> str:
    """('music','analysis') -> 'mcp__music_analysis'."""
    _assert_no_row_prefix(row, export)
    return f"mcp__{row}_{export}"


def skill_md_path(row: str, export: str) -> Path:
    return Path(f"agentic/{row}/skills/{export}/SKILL.md")


def handler_module(row: str, export: str) -> str:
    return f"agentic.{row}.handlers.{export}"
