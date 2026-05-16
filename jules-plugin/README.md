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

## Smoke Test

You can verify the installation by calling the `jules_list` tool in Claude. It should respond with an array of sessions.

## Design and Architecture
For a comprehensive overview of the design, see the design specification:
[2026-05-16-jules-suite-refactor-design.md](../docs/superpowers/specs/2026-05-16-jules-suite-refactor-design.md)
