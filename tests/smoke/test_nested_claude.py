import os
import subprocess
import pytest
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent.resolve()

def _claude_on_path() -> bool:
    return subprocess.run(["which", "claude"], capture_output=True).returncode == 0

@pytest.mark.smoke_slow
@pytest.mark.skipif(not _claude_on_path(), reason="claude CLI not on PATH")
def test_nested_claude_plugin_boot():
    """L2 Subprocess probe: Tests the real --plugin-dir boot path."""
    env = os.environ.copy()
    # Ensure ANTHROPIC_API_KEY or CLAUDE_CODE_SIMPLE is somewhat handled,
    # but we will just pass -p exit which should be minimal.

    # Graceful skip if ANTHROPIC_API_KEY isn't set, since claude needs it
    if "ANTHROPIC_API_KEY" not in env:
        pytest.skip("ANTHROPIC_API_KEY not set, L2 probe cannot run")

    cmd = [
        "claude",
        "--bare",
        "--plugin-dir", str(REPO_ROOT),
        "--disable-slash-commands",
        "--debug", "plugins",
        "-p", "exit"
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=60,
        env=env
    )

    assert result.returncode == 0, f"claude exited with {result.returncode}\nstdout: {result.stdout}\nstderr: {result.stderr}"

    output = result.stdout + result.stderr
    assert "agency-system" in output, f"Plugin 'agency-system' was not logged in debug output. Output:\n{output}"
