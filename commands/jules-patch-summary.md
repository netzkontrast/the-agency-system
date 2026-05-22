---
description: Summarize the patch produced by a Jules session.
argument-hint: <session-id>
allowed-tools: [mcp__agency-system, Bash]
---

# /agency-system:jules-patch-summary

Summarize the patch (files changed, lines added/removed, key edits) a
Jules session has produced so far — used to decide whether to approve,
ask Jules to revise, or land the patch locally.

## Action

This command delegates to the `jules-orchestrator` skill, which calls the
unified MCP tool `jules_patch_summary`.

Run: `Skill('jules-orchestrator', 'patch-summary $ARGUMENTS')` to invoke.
