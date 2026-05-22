"""Smoke tests for Spec 001 — scaffold-plugin-skeleton.

Verifies that the unified `agency-mcp` FastMCP server boots, exposes the
health_check tool, and survives a CodeMode ImportError gracefully.
"""
from __future__ import annotations

import asyncio
import builtins
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SERVER_DIR = REPO_ROOT / "servers" / "agency-mcp"
SERVER_SRC = SERVER_DIR / "src"


@pytest.fixture(autouse=True)
def _ensure_server_src_on_path():
    if str(SERVER_SRC) not in sys.path:
        sys.path.insert(0, str(SERVER_SRC))
    yield


def test_create_mcp_returns_fastmcp_instance(mcp_instance):
    from fastmcp import FastMCP

    assert isinstance(mcp_instance, FastMCP)
    assert mcp_instance.name == "agency-system"


@pytest.mark.asyncio
async def test_health_check_tool_registered(mcp_instance):
    tool = await mcp_instance.get_tool("health_check")
    assert tool is not None
    assert tool.name == "health_check"


def test_codemode_import_failure_does_not_break_boot(monkeypatch):
    """Anchor 001.3: optional CodeMode import failing must not break boot."""
    real_import = builtins.__import__

    def _faulty_import(name, *args, **kwargs):
        if name == "fastmcp.experimental.transforms.code_mode":
            raise ImportError("simulated absence of code-mode extra")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _faulty_import)
    sys.modules.pop("agency_mcp.server", None)
    sys.modules.pop("agency_mcp", None)

    from agency_mcp.server import create_mcp

    mcp = create_mcp()
    tool = asyncio.run(mcp.get_tool("health_check"))
    assert tool is not None
    assert tool.name == "health_check"


def test_run_check_cli_prints_healthy_line():
    """Anchor 001.1: `python run.py --check` exits 0 and prints the line."""
    result = subprocess.run(
        [sys.executable, str(SERVER_DIR / "run.py"), "--check"],
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert result.returncode == 0, f"stderr: {result.stderr}\nstdout: {result.stdout}"
    assert "agency-system v0.0.1 healthy" in result.stdout
