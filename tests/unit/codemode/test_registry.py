import pytest
import json
from pathlib import Path
from fastmcp import FastMCP
from agency_mcp.lib.codemode.registry import apply_codemode_manifest

@pytest.fixture
def temp_manifest(tmp_path):
    manifest_path = tmp_path / "manifest.json"
    manifest_data = {
        "eager_tool": {"classification": "eager", "domain": "test"},
        "deferred_tool": {"classification": "deferred", "domain": "test"},
        "background_tool": {
            "classification": "background",
            "domain": "test",
            "status_companion": "background_tool_status"
        },
        "background_tool_status": {"classification": "eager", "domain": "test"}
    }
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest_data, f)
    return manifest_path

@pytest.fixture
def mcp_with_tools():
    mcp = FastMCP("test")

    @mcp.tool
    def eager_tool(): pass

    @mcp.tool
    def deferred_tool(): pass

    @mcp.tool
    def background_tool(): pass

    @mcp.tool
    def background_tool_status(): pass

    return mcp

def test_manifest_loads(temp_manifest, mcp_with_tools):
    # Should not raise any errors
    apply_codemode_manifest(mcp_with_tools, temp_manifest, codemode_available=False)

def test_eager_tools_keep_schema(temp_manifest, mcp_with_tools):
    apply_codemode_manifest(mcp_with_tools, temp_manifest, codemode_available=True)
    # eager_tool should still be on main MCP
    assert "tool:eager_tool@" in mcp_with_tools._local_provider._components

def test_deferred_tools_drop_schema(temp_manifest, mcp_with_tools):
    apply_codemode_manifest(mcp_with_tools, temp_manifest, codemode_available=True)
    # deferred_tool should NOT be on main MCP directly (it's moved to the mounted server)
    assert "tool:deferred_tool@" not in mcp_with_tools._local_provider._components
    # The mounted server is accessible via mcp_with_tools._mounted_servers (dict mapping namespace to server)
    # Wait, if we used `mount` with no namespace, FastMCP manages it differently. Let's just check it's not on the main provider.

def test_background_requires_status_companion(tmp_path):
    manifest_path = tmp_path / "manifest.json"
    # background_tool has status_companion, but status_companion is NOT defined in manifest
    manifest_data = {
        "background_tool": {
            "classification": "background",
            "domain": "test",
            "status_companion": "missing_status_tool"
        }
    }
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest_data, f)

    mcp = FastMCP("test")
    @mcp.tool
    def background_tool(): pass

    with pytest.raises(ValueError, match="status_companion not found in manifest: missing_status_tool"):
        apply_codemode_manifest(mcp, manifest_path, codemode_available=False)

def test_unclassified_tool_raises_value_error(temp_manifest, mcp_with_tools):
    @mcp_with_tools.tool
    def unclassified_tool(): pass

    with pytest.raises(ValueError, match="unclassified tool: unclassified_tool"):
        apply_codemode_manifest(mcp_with_tools, temp_manifest, codemode_available=False)
