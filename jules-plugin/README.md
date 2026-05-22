# Jules Orchestrator Plugin

Complete suite for orchestrating Jules asynchronous coding sessions.

This plugin allows the Claude desktop to interface with the Jules AI orchestration service, allowing for sophisticated multi-agent coding sessions, task planning, and execution via MCP (Model Context Protocol).

## Installation

### Local Development
To install the plugin locally for development purposes, run:
```bash
claude --plugin-dir ./jules-plugin
```

### Distribution
To install the plugin from the marketplace:
```bash
/plugin install jules-orchestrator@netzkontrast
```

## Configuration

The plugin requires the `JULES_API_KEY` environment variable to be set for authentication with the Jules service.

## Local CLI tools (jules-bulk, jules-dev-install)

The plugin ships two helper scripts under `bin/`:

- `bin/jules-bulk` — fanout / dashboard / approve-awaiting / quota over the MCP server's Python entry points.
- `bin/jules-dev-install` — idempotent bootstrap for the Python deps these scripts need.

When you invoke `claude --plugin-dir ./jules-plugin` *inside* Claude Code, the
harness installs the MCP server's deps automatically. When you drive the
helpers from a plain shell (or from a Claude Code agent that has not yet
loaded the plugin), `fastmcp[code-mode]` is not on the system path and
`bin/jules-bulk` aborts with a clear preflight error pointing at
`bin/jules-dev-install`.

To bootstrap the CLI environment from scratch:

```bash
./jules-plugin/bin/jules-dev-install
export JULES_API_KEY=…                # required for the API client
export CLAUDE_PLUGIN_ROOT=$(pwd)/jules-plugin
./jules-plugin/bin/jules-bulk dashboard
```

The script installs `fastmcp[code-mode] >= 3.1.0`, `httpx`, and `PyYAML`,
verifies imports of `FastMCP`, `CodeMode`, `jules_create`, and `create_mcp`,
and pre-creates the session registry directory
(`${CLAUDE_PLUGIN_DATA:-$HOME/.jules}`). It is safe to run repeatedly.

## Smoke Test

You can verify the installation by calling the `jules_list` tool in Claude. It should respond with an array of sessions.

## Design and Architecture
For a comprehensive overview of the design, see the design specification:
[2026-05-16-jules-suite-refactor-design.md](../docs/superpowers/specs/2026-05-16-jules-suite-refactor-design.md)
