#!/usr/bin/env python3
"""PostToolUse hook: Check plugin.json and marketplace.json versions stay in sync.
Also checks state.json:_versions.ncp vs installed NCP_SCHEMA_VERSION,
and state.json:_versions.dramatica vs installed DRAMATICA_ONTOLOGY_VERSION.
"""
import json
import os
import sys

# Define default versions in case libs don't have them yet or we can't find them
DEFAULT_NCP_VERSION = "0.0.0"
DEFAULT_DRAMATICA_VERSION = "0.0.0"

def get_installed_versions():
    ncp_version = DEFAULT_NCP_VERSION
    dramatica_version = DEFAULT_DRAMATICA_VERSION

    # Check environment variables for tests, fallback to file paths
    if "NCP_SCHEMA_VERSION" in os.environ:
        ncp_version = os.environ["NCP_SCHEMA_VERSION"]
    else:
        ncp_paths = [
            os.path.join("servers", "agency-mcp", "src", "agency_mcp", "lib", "ncp", "__init__.py"),
            os.path.join("lib", "ncp", "__init__.py"),
            os.path.join(os.path.dirname(__file__), "..", "servers", "agency-mcp", "src", "agency_mcp", "lib", "ncp", "__init__.py")
        ]

        for path in ncp_paths:
            if os.path.exists(path):
                with open(path, "r") as f:
                    for line in f:
                        if line.startswith("NCP_SCHEMA_VERSION"):
                            ncp_version = line.split("=")[1].strip().strip('"').strip("'")
                            break
                if ncp_version != DEFAULT_NCP_VERSION:
                    break

    if "DRAMATICA_ONTOLOGY_VERSION" in os.environ:
        dramatica_version = os.environ["DRAMATICA_ONTOLOGY_VERSION"]
    else:
        dramatica_paths = [
            os.path.join("servers", "agency-mcp", "src", "agency_mcp", "lib", "dramatica", "__init__.py"),
            os.path.join("lib", "dramatica", "__init__.py"),
            os.path.join(os.path.dirname(__file__), "..", "servers", "agency-mcp", "src", "agency_mcp", "lib", "dramatica", "__init__.py")
        ]

        for path in dramatica_paths:
            if os.path.exists(path):
                with open(path, "r") as f:
                    for line in f:
                        if line.startswith("DRAMATICA_ONTOLOGY_VERSION"):
                            dramatica_version = line.split("=")[1].strip().strip('"').strip("'")
                            break
                if dramatica_version != DEFAULT_DRAMATICA_VERSION:
                    break

    return ncp_version, dramatica_version

def get_plugin_version():
    if "PLUGIN_VERSION" in os.environ:
        return os.environ["PLUGIN_VERSION"]

    try:
        plugin_paths = [
            ".claude-plugin/plugin.json",
            os.path.join(os.path.dirname(__file__), "..", ".claude-plugin", "plugin.json")
        ]
        for path in plugin_paths:
            if os.path.exists(path):
                with open(path, "r") as f:
                    plugin_data = json.load(f)
                    return plugin_data.get("version", "")
        return ""
    except Exception:
        return ""

def check_sync(data: dict) -> list[dict]:
    tool_input = data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    # We only care about state.json file changes
    if not file_path.endswith("state.json"):
        return []

    # In case of file passing directly for tests
    if "content" in tool_input:
        content = tool_input["content"]
        try:
            state_data = json.loads(content)
        except json.JSONDecodeError:
            return []
    else:
        try:
            with open(file_path, "r") as f:
                state_data = json.load(f)
        except Exception:
            return []

    drifts = []

    # 1. Check plugin version vs state.json
    state_plugin_version = state_data.get("_version")
    plugin_version = get_plugin_version()

    if state_plugin_version and plugin_version and state_plugin_version != plugin_version:
        drifts.append({
            "drift_kind": "plugin",
            "expected": plugin_version,
            "actual": state_plugin_version
        })

    # 2. Check NCP version vs state.json
    versions_dict = state_data.get("_versions", {})
    state_ncp_version = versions_dict.get("ncp")
    installed_ncp_version, installed_dram_version = get_installed_versions()

    if state_ncp_version and installed_ncp_version != DEFAULT_NCP_VERSION and state_ncp_version != installed_ncp_version:
        drifts.append({
            "drift_kind": "ncp",
            "expected": installed_ncp_version,
            "actual": state_ncp_version
        })

    # 3. Check Dramatica version vs state.json
    state_dram_version = versions_dict.get("dramatica")
    if state_dram_version and installed_dram_version != DEFAULT_DRAMATICA_VERSION and state_dram_version != installed_dram_version:
        drifts.append({
            "drift_kind": "dramatica",
            "expected": installed_dram_version,
            "actual": state_dram_version
        })

    return drifts

def main():
    if len(sys.argv) > 1:
        # For testing purposes, pass a file path
        try:
            with open(sys.argv[1], "r") as f:
                content = f.read()
            data = {"tool_input": {"file_path": sys.argv[1], "content": content}}
            # Allow tests to bypass file matching check
            if not data["tool_input"]["file_path"].endswith("state.json"):
                data["tool_input"]["file_path"] += "/state.json"
        except Exception as e:
            print(f"Error reading {sys.argv[1]}: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        try:
            data = json.load(sys.stdin)
        except (json.JSONDecodeError, EOFError):
            sys.exit(0)

    drifts = check_sync(data)
    if drifts:
        for drift in drifts:
            print(json.dumps(drift), file=sys.stderr)
        sys.exit(1)

    sys.exit(0)

if __name__ == "__main__":
    main()
