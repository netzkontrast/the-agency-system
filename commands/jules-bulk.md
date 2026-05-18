---
description: Fan out a Jules task across many sessions in parallel via the bulk CLI.
argument-hint: <subcommand> [args...]   # see `bin/jules-bulk --help`
allowed-tools: [mcp__agency-system, Bash]
---

# /agency-system:jules-bulk

Dispatch a Jules task across many sessions in parallel using the
`bin/jules-bulk` CLI. The CLI auto-detects the current `owner/repo` from
`git remote get-url origin` and the active branch, so fan-out works
without manual config. See `bin/jules-bulk --help` for subcommands.

## Action

This command delegates to the `jules-orchestrator` skill, which shells out
to the `bin/jules-bulk` CLI (a bash script — not a direct MCP tool).

Run: `Skill('jules-orchestrator', 'bulk $ARGUMENTS')` to invoke.
