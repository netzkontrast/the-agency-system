"""Pytest configuration for agency-mcp.

Spec: Plan/harness/design.md §3.3
"""
import pytest
import pytest_asyncio
import gc
from tests._harness.mcp import harness_mcp, list_tools as _list_tools, call_tool as _call_tool
from tests._harness.skills import load_skill as _load_skill, dispatch_skill as _dispatch_skill, list_skills as _list_skills, REPO_ROOT

@pytest.fixture(scope="session")
def mcp_instance():
    """Session-scoped FastMCP instance."""
    return harness_mcp()

@pytest_asyncio.fixture
async def call_tool(mcp_instance):
    """Fixture to call tools and unpack envelopes."""
    async def _call(name: str, params: dict = None) -> dict:
        return await _call_tool(mcp_instance, name, params)
    return _call

@pytest_asyncio.fixture
async def tools(mcp_instance):
    """Fixture to list all tools."""
    return await _list_tools(mcp_instance)

@pytest.fixture
def load_skill():
    """Fixture to load a skill."""
    return _load_skill

@pytest.fixture
def dispatch_skill():
    """Fixture to resolve a skill."""
    return _dispatch_skill

def pytest_sessionfinish(session, exitstatus):
    """
    Hook to clean up resources after the test session finishes.
    Spec 113 ContextWatcher daemon-thread leak fix.
    """
    # Find the ContextWatcher thread and stop it
    # We can inspect instances in the garbage collector since ContextWatcher is instantiated in context/__init__.py
    for obj in gc.get_objects():
        if type(obj).__name__ == "ContextWatcher":
            if hasattr(obj, "stop"):
                obj.stop()
