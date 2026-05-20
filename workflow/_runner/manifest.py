"""Workflow-cell manifest reader.

Spec 07-v1 §FR3 — exposes ``get_lazy_link(row)`` for the generic graph
walker in :mod:`workflow._runner.pipeline`. Result is cached for the
lifetime of the process; manifest edits during a session do not
retroactively flip behaviour. Cold-restart to refresh. Tests reset the
cache between cases via :func:`_reset_cache_for_tests`.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

_LAZY_LINK_CACHE: dict[str, bool] = {}


def get_lazy_link(row: str) -> bool:
    """Return the row's ``[workflow.lazy_link] enabled`` boolean.

    Defaults to ``False`` when the manifest file is missing or when the
    ``[workflow.lazy_link]`` sub-table is absent. Cached for the lifetime
    of the process — cold-restart to refresh after a manifest edit.

    Args:
        row: The row name whose manifest is queried.

    Returns:
        Whether the row opts in to lazy-link Phase node creation.
    """
    if row in _LAZY_LINK_CACHE:
        return _LAZY_LINK_CACHE[row]

    path = Path(f"workflow/{row}/manifest.toml")
    if not path.exists():
        _LAZY_LINK_CACHE[row] = False
        return False

    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError:
        _LAZY_LINK_CACHE[row] = False
        return False

    enabled = bool(
        data.get("workflow", {}).get("lazy_link", {}).get("enabled", False)
    )
    _LAZY_LINK_CACHE[row] = enabled
    return enabled


def _reset_cache_for_tests() -> None:
    """Clear the in-process cache. Test-only helper.

    Production code MUST NOT call this — the cache invariant per spec
    07-v1 §FR3 is "cold-restart-only".
    """
    _LAZY_LINK_CACHE.clear()
