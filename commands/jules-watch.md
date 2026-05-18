---
description: Watch a Jules session and stream activities until completion.
argument-hint: <session-id> [--poll-secs 10]
allowed-tools: [mcp__agency-system, Bash]
---

# /agency-system:jules-watch

Start a watcher loop for one Jules session. Polls `jules_watcher_status`
until the session reaches a terminal state (done / failed / blocked) and
surfaces activity transitions as they happen. There is no single MCP call
that does this — the watcher is a bash-side loop driven by the skill.

## Action

This command delegates to the `jules-orchestrator` skill, which runs the
bash watcher (poll loop over `jules_watcher_status`).

Run: `Skill('jules-orchestrator', 'watch $ARGUMENTS')` to invoke.
