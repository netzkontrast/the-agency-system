import subprocess
import os

def test_help_exits_zero():
    env = os.environ.copy()
    env["JULES_API_KEY"] = "test-key"
    result = subprocess.run(["bin/jules-bulk", "--help"], capture_output=True, text=True, env=env)
    assert result.returncode == 0
