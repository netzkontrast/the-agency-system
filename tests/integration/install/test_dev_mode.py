import subprocess
import json
import os
from pathlib import Path

def test_dev_install_idempotency(tmp_path, monkeypatch):
    """022.3 Scenario: Bootstrap script is idempotent"""
    repo_root = Path(__file__).parent.parent.parent.parent.resolve()
    script = repo_root / "bin" / "agency-dev-install"

    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    fake_uv = fake_bin / "uv"
    fake_uv.write_text("#!/usr/bin/env bash\necho 'fake uv'\n")
    fake_uv.chmod(0o755)

    fake_python = fake_bin / "python"
    fake_python.write_text("#!/usr/bin/env bash\nexit 0\n")
    fake_python.chmod(0o755)

    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:{env.get('PATH', '')}"

    # We need to test the script with a mocked environment just like the failure mode test
    # Because uv will fail if not in a virtualenv (and we removed the --system fallback)
    # We will use the test_repo to be safe.

    test_repo = tmp_path / "test_repo"
    test_repo.mkdir()
    (test_repo / "servers" / "agency-mcp").mkdir(parents=True)

    mcp_json_path = test_repo / ".mcp.json"
    mcp_json_path.write_text(json.dumps({
        "mcpServers": {
            "agency-system": {
                "type": "stdio",
                "command": "python",
                "args": ["${CLAUDE_PLUGIN_ROOT}/servers/agency-mcp/run.py"]
            }
        }
    }))
    run_py = test_repo / "servers" / "agency-mcp" / "run.py"
    run_py.write_text("")

    # Run once
    res1 = subprocess.run([str(script), str(test_repo)], capture_output=True, text=True, env=env)
    assert res1.returncode == 0

    # Run twice
    res2 = subprocess.run([str(script), str(test_repo)], capture_output=True, text=True, env=env)
    assert res2.returncode == 0
    assert "dev install successful! All checks pass." in res2.stdout

def test_dev_install_failure_modes(tmp_path, monkeypatch):
    """022.4 Scenario: Bootstrap script fails loudly on broken state"""
    repo_root = Path(__file__).parent.parent.parent.parent.resolve()
    script = repo_root / "bin" / "agency-dev-install"

    # We want to simulate the install without actually pip installing.
    # We can mock `uv` by putting a fake uv in the PATH for this test.
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    fake_uv = fake_bin / "uv"
    fake_uv.write_text("#!/usr/bin/env bash\necho 'fake uv'\n")
    fake_uv.chmod(0o755)

    # Make python just echo true to bypass server check
    fake_python = fake_bin / "python"
    fake_python.write_text("#!/usr/bin/env bash\nexit 0\n")
    fake_python.chmod(0o755)

    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:{env.get('PATH', '')}"

    test_repo = tmp_path / "test_repo"
    test_repo.mkdir()

    # Needs to copy empty structure so the script doesn't fail early
    (test_repo / "servers" / "agency-mcp").mkdir(parents=True)

    # Simulate a failure by breaking .mcp.json
    mcp_json_path = test_repo / ".mcp.json"
    mcp_json_path.write_text(json.dumps({
        "mcpServers": {
            "agency-system": {
                "type": "stdio",
                "command": "python",
                "args": ["${CLAUDE_PLUGIN_ROOT}/servers/agency-mcp/nonexistent.py"]
            }
        }
    }))

    res = subprocess.run([str(script), str(test_repo)], capture_output=True, text=True, env=env)
    assert res.returncode == 1
    assert "which does not exist." in res.stderr
