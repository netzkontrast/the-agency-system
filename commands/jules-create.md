---
description: Create a new Jules asynchronous coding session.
argument-hint: <prompt> [--source owner/repo] [--branch name]
allowed-tools: [mcp__agency-system, Bash]
---

# /agency-system:jules-create

Start a new Jules session to delegate a long-running coding task (refactor,
multi-file edit, test generation, feature implementation, PR creation) to the
Google Jules remote agent. The local terminal acts as control plane; Jules
runs the work asynchronously and returns a session id you can watch or
patch.

## Action

This command delegates to the `jules-orchestrator` skill, which in turn
calls the unified MCP tool `jules_create` for session creation.

Run: `Skill('jules-orchestrator', 'create $ARGUMENTS')` to invoke.
