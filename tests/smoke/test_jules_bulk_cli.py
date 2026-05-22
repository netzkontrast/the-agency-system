"""Smoke test for bin/jules-bulk CLI.

Asserts that `bin/jules-bulk --help` exits 0 and emits usage text. This is
the behavioural piece of Spec 007 (the rest is config / file-moves). The
script's --help branch short-circuits the JULES_API_KEY check, so the
test runs unconditionally.
"""
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_jules_bulk_help_exits_zero():
    result = subprocess.run(
        [str(REPO_ROOT / "bin" / "jules-bulk"), "--help"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, f"stderr={result.stderr[:500]}"
    assert (
        "usage" in result.stdout.lower() or "usage" in result.stderr.lower()
    ), f"no 'usage' substring; stdout[:500]={result.stdout[:500]!r}"
