"""Unit tests for the Code Mode manifest registry.

Spec: Plan/008-codemode-registry/spec.md (Gate 2 — TDD §7).
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from agency_mcp.lib.codemode import registry


@pytest.fixture(autouse=True)
def _clear_manifest_cache():
    """Drop the lru_cache on load_manifest between tests so each test
    sees a freshly parsed manifest."""
    registry._reset_cache()
    yield
    registry._reset_cache()


def test_manifest_loads():
    """The shipped manifest.json parses and declares schema version 1.0.0."""
    manifest = registry.load_manifest()
    assert manifest["_version"] == "1.0.0"
    assert "tools" in manifest
    assert isinstance(manifest["tools"], dict)


def test_eager_tools_keep_schema():
    """The 4 anchor tools are present in the manifest and classified eager."""
    anchors = registry.anchor_tools()
    assert len(anchors) == 4, f"expected 4 anchors, got {len(anchors)}: {anchors}"
    for anchor in anchors:
        assert registry.classify(anchor) == "eager", (
            f"anchor {anchor!r} not classified eager"
        )


def test_deferred_tools_drop_schema():
    """At least one non-anchor tool exists and is classified deferred."""
    manifest = registry.load_manifest()
    anchors = set(registry.anchor_tools())
    deferred = [
        name
        for name, entry in manifest["tools"].items()
        if entry["classification"] == "deferred" and name not in anchors
    ]
    assert len(deferred) > 0, "expected at least one deferred non-anchor tool"


def test_background_requires_status_companion(tmp_path):
    """Every background tool must carry a status_companion field; the
    loader raises ValueError if any background entry is missing it."""
    # Positive path — well-formed background entry passes validation.
    good_manifest = {
        "_version": "1.0.0",
        "anchor_tools": [],
        "tools": {
            "long_runner": {
                "classification": "background",
                "domain": "test",
                "status_companion": "long_runner_status",
            }
        },
    }
    good_path = tmp_path / "good.json"
    good_path.write_text(json.dumps(good_manifest))
    registry._reset_cache()
    parsed = registry.load_manifest(good_path)
    assert parsed["tools"]["long_runner"]["status_companion"] == "long_runner_status"

    # Negative path — background entry missing companion raises ValueError.
    bad_manifest = {
        "_version": "1.0.0",
        "anchor_tools": [],
        "tools": {
            "long_runner": {
                "classification": "background",
                "domain": "test",
            }
        },
    }
    bad_path = tmp_path / "bad.json"
    bad_path.write_text(json.dumps(bad_manifest))
    registry._reset_cache()
    with pytest.raises(ValueError, match="status_companion"):
        registry.load_manifest(bad_path)


def test_unclassified_tool_raises_value_error():
    """Calling classify() on a name not in the manifest raises ValueError
    so missing entries fail loudly rather than silently defaulting to
    eager registration (which would blow the boot-token budget)."""
    with pytest.raises(ValueError, match="unclassified tool"):
        registry.classify("this_tool_does_not_exist_anywhere")
