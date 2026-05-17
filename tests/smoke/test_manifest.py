import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

def test_root_manifest_has_required_keys():
    manifest_path = REPO_ROOT / ".claude-plugin" / "plugin.json"
    assert manifest_path.exists(), f"Manifest missing at {manifest_path}"

    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data.get("name") == "agency-system"
    assert data.get("version") == "0.1.0"
    assert "description" in data
    assert "author" in data
    assert data.get("homepage") == "https://github.com/netzkontrast/the-agency-system"

def test_root_manifest_omits_mcpservers():
    manifest_path = REPO_ROOT / ".claude-plugin" / "plugin.json"
    if not manifest_path.exists():
        return

    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "mcpServers" not in data, "mcpServers should be omitted from plugin.json in favor of .mcp.json"

def test_marketplace_descriptor_is_single_plugin_shape():
    market_path = REPO_ROOT / ".claude-plugin" / "marketplace.json"
    assert market_path.exists(), f"Marketplace descriptor missing at {market_path}"

    with open(market_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    plugins = data.get("plugins")
    assert isinstance(plugins, list), "Marketplace plugins must be a list"
    assert len(plugins) == 1, "Marketplace must be single-plugin shape"
    assert plugins[0].get("name") == "agency-system"

def test_jules_plugin_manifest_is_deprecated():
    jules_manifest_path = REPO_ROOT / "jules-plugin" / ".claude-plugin" / "plugin.json"
    if not jules_manifest_path.exists():
        return

    with open(jules_manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data.get("deprecated") is True
    description = data.get("description", "")
    assert "superseded by agency-system at repo root" in description
