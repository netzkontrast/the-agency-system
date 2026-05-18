import subprocess
import os
import pytest
from pathlib import Path

def test_dev_install_plugin_loads():
    # 022.1 Scenario: Dev-mode boot loads the plugin
    claude_bin = subprocess.run(["which", "claude"], capture_output=True)
    if claude_bin.returncode != 0:
        pytest.skip("claude CLI not on PATH")

    repo_root = Path(__file__).parent.parent.parent.resolve()

    # Run claude --plugin-dir <repo> /help
    # We use /help or another basic command to force it to load the plugin and show skills
    result = subprocess.run(
        ["claude", "--plugin-dir", str(repo_root), "/help"],
        capture_output=True,
        text=True,
        timeout=30
    )

    assert result.returncode == 0, f"claude exited with {result.returncode}, stderr: {result.stderr}"
    assert "agency-system" in result.stdout or "agency-system" in result.stderr
