import pytest
import subprocess
import json
import os

def test_valid_state():
    # Pass mock versions via environment variables
    env = os.environ.copy()
    env["NCP_SCHEMA_VERSION"] = "1.3.0"
    env["DRAMATICA_ONTOLOGY_VERSION"] = "1.3.0"
    env["PLUGIN_VERSION"] = "0.1.0-dev"

    result = subprocess.run(
        ["python3", "hooks/check_version_sync.py", "tests/fixtures/hooks/state_versions/state_valid.json"],
        capture_output=True,
        text=True,
        env=env
    )
    assert result.returncode == 0
    assert result.stderr == ""

def test_drifted_state():
    # Pass mock versions via environment variables to verify the drift logic
    env = os.environ.copy()
    env["NCP_SCHEMA_VERSION"] = "1.3.0"
    env["DRAMATICA_ONTOLOGY_VERSION"] = "1.3.0"
    env["PLUGIN_VERSION"] = "0.1.0-dev"

    result = subprocess.run(
        ["python3", "hooks/check_version_sync.py", "tests/fixtures/hooks/state_versions/state_drifted.json"],
        capture_output=True,
        text=True,
        env=env
    )
    assert result.returncode != 0

    # Parse json lines
    lines = [line for line in result.stderr.split("\n") if line.strip()]
    errors = [json.loads(line) for line in lines]

    # Check specific errors
    drift_kinds = [e["drift_kind"] for e in errors]
    assert "plugin" in drift_kinds
    assert "ncp" in drift_kinds
    assert "dramatica" in drift_kinds

    ncp_error = next(e for e in errors if e["drift_kind"] == "ncp")
    assert ncp_error["expected"] == "1.3.0"
    assert ncp_error["actual"] == "1.2.0"
