# agency-mcp

This is the unified FastMCP server for the `agency-system` plugin. It handles tasks related to music, novel, jules, and agentic workflows.

## Dev Install

To install the server for local development directly from the source tree:

```bash
cd servers/agency-mcp
uv pip install -e .
```

This creates an editable install, meaning changes to the python files under `src/` are immediately reflected without needing a reinstall.

## Entrypoint Contract

The canonical entrypoint for the MCP server is `run.py`.

```bash
python run.py
```

It is a thin wrapper that invokes `agency_mcp.server.create_mcp().run()`. The Claude Code plugin is configured in `.mcp.json` to start this file.
