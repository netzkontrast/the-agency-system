import json
from pathlib import Path
from fastmcp import FastMCP
from typing import Dict, Any

def apply_codemode_manifest(mcp: FastMCP, manifest_path: Path, codemode_available: bool = True) -> None:
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest: Dict[str, Dict[str, Any]] = json.load(f)

    # 1. First verification pass: make sure every tool is in the manifest,
    # and all background companions exist.
    # Note: the FastMCP components keys are like 'tool:music_find_album@'
    tools = {}
    for key, tool in mcp._local_provider._components.items():
        if key.startswith('tool:'):
            # Extract just the name of the tool, assuming format `tool:<name>@<version>`
            name = key.split(':')[1].split('@')[0]
            tools[name] = tool

            if name not in manifest:
                raise ValueError(f"unclassified tool: {name}")

            entry = manifest[name]
            if entry.get("classification") == "background":
                companion = entry.get("status_companion")
                if not companion:
                    raise ValueError(f"background tool missing status_companion: {name}")
                # We defer checking if companion exists until we process all tools or check manifest keys
                if companion not in manifest:
                    raise ValueError(f"status_companion not found in manifest: {companion}")

    for name, entry in manifest.items():
        if entry.get("classification") == "background":
            companion = entry.get("status_companion")
            if companion and companion not in tools and companion not in manifest:
                 raise ValueError(f"status_companion {companion} missing for background tool {name}")

    if not codemode_available:
        return

    # To defer tools with FastMCP 3.3 CodeMode, we must put them on a proxy server
    # that has the CodeMode transform, then mount it onto the main server.

    from fastmcp.experimental.transforms.code_mode import CodeMode
    deferred_mcp = FastMCP("agency-deferred", transforms=[CodeMode()])

    # We will move deferred tools from mcp to deferred_mcp
    keys_to_remove = []

    for key, tool in mcp._local_provider._components.items():
        if key.startswith('tool:'):
            name = key.split(':')[1].split('@')[0]
            entry = manifest.get(name, {})

            # background tools are also deferred (hidden behind CodeMode),
            # but their _status companion is eager (kept on main MCP).
            if entry.get("classification") in ["deferred", "background"]:
                # Add to deferred server
                deferred_mcp._local_provider._components[key] = tool
                keys_to_remove.append(key)

    # Remove them from main server
    for key in keys_to_remove:
        del mcp._local_provider._components[key]

    mcp.mount(deferred_mcp)
