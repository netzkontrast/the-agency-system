# Development Setup

This document describes the workflow for installing and testing the `agency-system` plugin locally directly from the source tree. This is useful for plugin developers working on Wave B / Wave C specifications.

## Prerequisites

- **Python 3.11+**
- **[uv](https://docs.astral.sh/uv/)** for fast package installation
- **claude CLI** (Claude Code) installed

## Installation

Run the bootstrap script to set up the editable python installation and verify the manifest configuration:

```bash
bin/agency-dev-install
```

This script will:
1. Perform an editable installation (`uv pip install -e`) of the python MCP server in `servers/agency-mcp/`.
2. Verify the server boot process.
3. Verify that paths in `.mcp.json` resolve correctly within the tree.
4. Verify all skills adhere to the `agency-system:` namespace.

## Verification

Load the plugin locally to verify it boots with all skills and tools:

```bash
claude --plugin-dir /path/to/the-agency-system /help
```

You should see `agency-system` in the listing, along with standard skill namespaces (`agency-system:music-*`, `agency-system:jules-*`, etc).

## Troubleshooting

1. **Missing `tiktoken` or audio dependencies (`librosa`, `soundfile`)**:
   - Make sure you ran `bin/agency-dev-install` which properly installs these via `pyproject.toml`.
2. **Mismatched FastMCP version (CodeMode errors)**:
   - Make sure `fastmcp[code-mode]>=3.1.0` is properly installed. The editable install handles this, but your environment might shadow it.
3. **Stale `.mcp.json` path**:
   - If `.mcp.json` fails to find `run.py`, ensure the `${CLAUDE_PLUGIN_ROOT}` variable is parsed correctly and that `servers/agency-mcp/run.py` exists in your checkout.
4. **Missing `CLAUDE_PLUGIN_ROOT`**:
   - Claude Code automatically sets this when using `--plugin-dir`. If testing manually, ensure you define it.
5. **ImportError when loading the server**:
   - This usually means `servers/agency-mcp/src` is missing from your python path or the package isn't installed. The editable installation fixes this.
