import json
from pathlib import Path

def test_marketplace_name():
    marketplace_json = Path(".claude-plugin/marketplace.json")
    assert marketplace_json.exists()
    data = json.loads(marketplace_json.read_text())
    assert data["name"] == "netzkontrast", f"Expected name 'netzkontrast', got {data.get('name')}"

def test_readme_instruction():
    readme = Path("README.md")
    assert readme.exists()
    content = readme.read_text()
    assert "agency-system@netzkontrast" in content, "README.md should instruct using agency-system@netzkontrast"
