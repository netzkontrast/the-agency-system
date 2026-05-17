import json
import pytest
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent

def test_root_manifest_has_required_keys():
    manifest_path = ROOT_DIR / ".claude-plugin" / "plugin.json"
    assert manifest_path.exists()

    with open(manifest_path) as f:
        data = json.load(f)

    assert data.get("name") == "agency-system"
    assert data.get("version") == "0.1.0"
    assert "description" in data
    assert "author" in data
    assert data.get("homepage") == "https://github.com/netzkontrast/the-agency-system"

def test_root_manifest_omits_mcpservers():
    manifest_path = ROOT_DIR / ".claude-plugin" / "plugin.json"
    assert manifest_path.exists()

    with open(manifest_path) as f:
        data = json.load(f)

    assert "mcpServers" not in data

def test_marketplace_descriptor_is_single_plugin_shape():
    marketplace_path = ROOT_DIR / ".claude-plugin" / "marketplace.json"
    assert marketplace_path.exists()

    with open(marketplace_path) as f:
        data = json.load(f)

    assert "plugins" in data
    assert isinstance(data["plugins"], list)
    assert len(data["plugins"]) == 1
    assert data["plugins"][0].get("name") == "agency-system"

def test_jules_plugin_manifest_is_deprecated():
    manifest_path = ROOT_DIR / "jules-plugin" / ".claude-plugin" / "plugin.json"
    assert manifest_path.exists()

    with open(manifest_path) as f:
        data = json.load(f)

    assert data.get("deprecated") is True
    assert data.get("description", "").endswith("superseded by agency-system at repo root; will be removed in Spec 020.")
