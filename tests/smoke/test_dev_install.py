import json
import subprocess
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).parent.parent.parent.resolve()


def _claude_on_path() -> bool:
    return subprocess.run(["which", "claude"], capture_output=True).returncode == 0


def test_dev_install_manifest_is_agency_system():
    # 022.1 Scenario: Dev-mode boot loads the plugin (manifest contract).
    # The plugin name in .claude-plugin/plugin.json is the value `claude --plugin-dir`
    # resolves and exposes as the namespace prefix.
    manifest = json.loads((REPO_ROOT / ".claude-plugin" / "plugin.json").read_text())
    assert manifest["name"] == "agency-system"
    assert "version" in manifest


def test_dev_install_plugin_validates():
    # 022.1 Scenario: Dev-mode boot loads the plugin.
    # `claude plugin validate <path>` is the non-interactive verification primitive:
    # it parses the manifest, walks the skill tree, and exits non-zero on schema errors.
    if not _claude_on_path():
        pytest.skip("claude CLI not on PATH")

    result = subprocess.run(
        ["claude", "plugin", "validate", str(REPO_ROOT)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, (
        f"claude plugin validate exited with {result.returncode}\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )

@pytest.mark.asyncio
async def test_dev_install_loads_all_tools(tools):
    # L1 Harness assertion matching Codex P1 critique (assert len(tools) >= 113)
    # This verifies the complete backend loads and registers the full tool surface,
    # ensuring no silent domain-import failures hide behind the manifest validation.
    assert len(tools) >= 113, f"Expected at least 113 tools, got {len(tools)}"
