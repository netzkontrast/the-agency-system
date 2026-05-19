"""N0 / C5 — verify boot() wraps registered tools with pre/post hooks.

Spec: vision/04-nextsteps.md §N0.
"""
import os
import pytest
from pathlib import Path

import agentic._bootloader as bootloader
from agentic._harness.cell_loader import CellRegistry
from context._store.sqlite import Store


@pytest.mark.asyncio
async def test_post_tool_use_fires_on_wrapped_tool(monkeypatch, tmp_path):
    orig_dir = os.getcwd()
    os.chdir(tmp_path)
    try:
        db_path = str(tmp_path / "ontology.db")
        # Redirect the hook's Store to a sandbox DB.
        monkeypatch.setattr(
            "context._hooks.post_tool_use.Store", lambda: Store(db_path=db_path)
        )

        artefact_metadata = {
            "artefact_path": "result/jules/findings/topic.md",
            "content_type": "text/markdown",
            "sha256": "abc123",
            "size_bytes": 42,
            "created_at": "2026-05-19T14:22:07Z",
            "produced_by": {
                "skill": "jules-research",
                "phase": "01-research",
                "session_id": "wf-test",
            },
        }

        def _fake_tool(**kwargs):
            return {
                "ok": True,
                "data": {"artefact_metadata": artefact_metadata},
                "warnings": [],
                "next_suggested_tools": [],
            }

        registry = CellRegistry()
        registry.tools["mcp__jules_query"] = _fake_tool

        monkeypatch.setattr(bootloader, "discover", lambda: registry)

        mcp = bootloader.boot()

        # Invoke through FastMCP so we exercise the wrapper we installed.
        result = await mcp.call_tool("mcp__jules_query", {})
        import json
        envelope = json.loads(result.content[0].text)
        assert envelope["ok"] is True

        # PostToolUse should have logged the call and upserted the Artefact node.
        store = Store(db_path=db_path)
        nodes = store.query("MATCH (n:Artefact) RETURN n")
        assert len(nodes) >= 1
    finally:
        os.chdir(orig_dir)


@pytest.mark.asyncio
async def test_pre_tool_use_short_circuits_invalid_input(monkeypatch, tmp_path):
    orig_dir = os.getcwd()
    os.chdir(tmp_path)
    try:
        db_path = str(tmp_path / "ontology.db")
        monkeypatch.setattr(
            "context._hooks.post_tool_use.Store", lambda: Store(db_path=db_path)
        )

        called = {"hit": False}

        def _fake_write(**kwargs):
            called["hit"] = True
            return {"ok": True, "data": {}, "warnings": [], "next_suggested_tools": []}

        registry = CellRegistry()
        registry.tools["mcp__demo_write_manifest"] = _fake_write
        monkeypatch.setattr(bootloader, "discover", lambda: registry)

        mcp = bootloader.boot()

        import json
        bogus = {
            "path": "agentic/demo/manifest.toml",
            "content": "[cell]\nrow = \"demo\"\ncolumn = \"agentic\"\n",
        }
        result = await mcp.call_tool("mcp__demo_write_manifest", bogus)
        envelope = json.loads(result.content[0].text)
        assert envelope["ok"] is False
        assert envelope["data"]["error"]["code"] == "PRE_TOOL_USE_INVALID"
        assert called["hit"] is False
    finally:
        os.chdir(orig_dir)
