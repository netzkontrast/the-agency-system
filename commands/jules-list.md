---
description: List active Jules sessions.
argument-hint: [--status running|done|all]
allowed-tools: [mcp__agency-system, Bash]
---

# /agency-system:jules-list

List currently active (or recently completed) Jules sessions with their
session id, status, and last activity. Use this to find a session id to
watch, patch, or summarize.

## Action

This command delegates to the `jules-orchestrator` skill, which calls the
unified MCP tool `jules_list` and returns the result table verbatim.

Run: `Skill('jules-orchestrator', 'list $ARGUMENTS')` to invoke.
