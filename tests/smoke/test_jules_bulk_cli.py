import subprocess
import pytest

def test_help_exits_zero():
    res = subprocess.run(["bin/jules-bulk", "--help"], capture_output=True, text=True)
    assert res.returncode == 0
    assert "usage:" in res.stdout.lower()
