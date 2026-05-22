"""Code Mode manifest loader and classifier.

Spec: Plan/008-codemode-registry/spec.md (Done When §lib/codemode/registry.py).

The manifest at ``codemode/manifest.json`` is the single source of truth
for which tools are kept eagerly visible (anchors) and which are hidden
behind the FastMCP CodeMode meta-tools (``search``/``get_schema``/``execute``).

Public surface:
    load_manifest() -> dict
        Return the cached parsed manifest. Validates background entries
        on first load.

    classify(tool_name) -> "eager" | "deferred" | "background"
        Lookup classification for a tool. Raises ValueError if the tool
        is not present in the manifest — missing entries must fail loudly
        rather than silently default to eager.

    anchor_tools() -> list[str]
        The declared anchor list from the manifest (eager tools).

    background_companions() -> dict[str, str]
        Map of {background_tool_name: status_companion_name}.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

# Canonical manifest location: ``agency_mcp/codemode/manifest.json``.
# ``registry.py`` lives at ``agency_mcp/lib/codemode/registry.py``; the
# manifest is two levels up (``agency_mcp/``) plus ``codemode/manifest.json``.
_MANIFEST_PATH = (
    Path(__file__).resolve().parents[2] / "codemode" / "manifest.json"
)

_VALID_CLASSIFICATIONS = {"eager", "deferred", "background"}


def _validate(manifest: dict[str, Any]) -> None:
    """Validate manifest invariants. Raises ValueError on any breach."""
    if "_version" not in manifest:
        raise ValueError("manifest missing '_version' field")
    if "tools" not in manifest or not isinstance(manifest["tools"], dict):
        raise ValueError("manifest missing or invalid 'tools' mapping")

    for name, entry in manifest["tools"].items():
        if not isinstance(entry, dict):
            raise ValueError(f"manifest entry for {name!r} is not a dict")
        cls = entry.get("classification")
        if cls not in _VALID_CLASSIFICATIONS:
            raise ValueError(
                f"manifest entry {name!r} has invalid classification {cls!r}; "
                f"must be one of {sorted(_VALID_CLASSIFICATIONS)}"
            )
        if cls == "background" and "status_companion" not in entry:
            raise ValueError(
                f"background tool {name!r} missing required "
                f"'status_companion' field"
            )


@lru_cache(maxsize=1)
def load_manifest(path: str | Path | None = None) -> dict[str, Any]:
    """Load and cache the manifest JSON.

    Args:
        path: Optional override for the manifest path (used by tests).
            When ``None`` the default ``codemode/manifest.json`` ships.

    Returns:
        The parsed manifest dict.

    Raises:
        ValueError: if manifest fails validation (missing fields,
            invalid classification, background without status_companion).
        FileNotFoundError: if the manifest file does not exist.
    """
    manifest_path = Path(path) if path is not None else _MANIFEST_PATH
    with manifest_path.open("r", encoding="utf-8") as fh:
        manifest = json.load(fh)
    _validate(manifest)
    return manifest


def _reset_cache() -> None:
    """Drop the cached manifest. Test-only helper."""
    load_manifest.cache_clear()


def classify(tool_name: str) -> str:
    """Return the classification for ``tool_name``.

    Raises:
        ValueError: if ``tool_name`` is not in the manifest. Missing
            entries are a hard error so new tools cannot silently default
            to eager registration and blow the boot-token budget.
    """
    manifest = load_manifest()
    entry = manifest["tools"].get(tool_name)
    if entry is None:
        raise ValueError(
            f"unclassified tool: {tool_name!r} — add an entry to "
            f"codemode/manifest.json"
        )
    return entry["classification"]


def anchor_tools() -> list[str]:
    """Return the list of declared anchor (eager) tool names."""
    manifest = load_manifest()
    return list(manifest.get("anchor_tools", []))


def background_companions() -> dict[str, str]:
    """Return {background_tool: status_companion} mapping."""
    manifest = load_manifest()
    return {
        name: entry["status_companion"]
        for name, entry in manifest["tools"].items()
        if entry.get("classification") == "background"
    }
