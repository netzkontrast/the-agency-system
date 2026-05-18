---
name: jules
description: >
  Delegates long-running codebase tasks (refactors, multi-file edits, test
  generation, feature implementation, automated PR creation) to the Google
  Jules asynchronous coding agent. Supports fan-out parallel orchestration
  across many concurrent sessions. Use when the user mentions "Jules",
  "remote agent", "asynchronous task", asks for a cloud-side coding job
  that would block the local terminal, or asks for parallel work.
argument-hint: <action> [args...]   # actions: create | list | status | activities | approve | message | fanout | dashboard | help (note: stop is unsupported)
model: claude-sonnet-4-6
allowed-tools:
  - Bash
  - Read
  - mcp__jules
---

## Your Task

**Input:** `$ARGUMENTS`

You are an orchestrator for the Google Jules asynchronous coding agent. The
user's local terminal is a control plane; Jules is the remote worker. Your
job is to start, monitor, decide on, interact with, and stop Jules sessions
on the user's behalf — never to simulate the work locally.

## Preferred path: MCP tools

When the `jules` MCP server is connected, **always prefer its tools over
raw API calls or scripts** — they are reliable, structured, and the model sees them in
its tool list natively.

| Tool | Purpose |
|---|---|
| `jules_create` | Start a new session. Required: `prompt`. Optional: `title`, `source`, `branch`, `auto_create_pr`. |
| `jules_get` | Fetch session state (`IN_PROGRESS`, `AWAITING_PLAN_APPROVAL`, etc) and outputs. |
| `jules_list` | List all sessions. Defaults to active only. |
| `jules_activities` | Fetch activity log (events like plan generated, errors, etc). |
| `jules_plan` | Fetch the current plan as Markdown. |
| `jules_approve` | Approve a session waiting in `AWAITING_PLAN_APPROVAL`. |
| `jules_message` | Send feedback to a session, either to answer a question or correct a plan. |
| `jules_resolve_source` | Convert a GitHub `owner/repo` into a Jules opaque source resource ID. |
| `jules_patch` | Fetch the full unified diff of a completed session. |
| `jules_patch_apply` | Apply a completed session's diff to the local working tree (supports dry-run). |
| `jules_patch_summary` | Get metadata for a patch (files changed, lines added/removed) without the full diff. |
| `jules_status_all` | Fast overview of all sessions grouped by state. |
| `jules_approve_awaiting` | Bulk-approve all sessions matching a title prefix. |
| `jules_quota` | Check remaining daily session quota. |
| `jules_resolve_alias` | Look up a session ID by its human-readable alias. |

*(Note: `jules_stop` is NOT supported upstream. Do not attempt to stop sessions.)*

## Critical Gotchas

1. **`COMPLETED` ≠ terminal.** It means "session is idle, waiting for input" — NOT "done, success". A `COMPLETED` session can be resumed by sending `jules_message(sid, ...)`; it transitions back to `IN_PROGRESS` and continues working. Two distinct sub-cases:
   - `COMPLETED` with patch artifacts AND branch on remote AND PR open → real terminal success.
   - `COMPLETED` with missing branch/PR (silent-fail per JULES_PROTOCOL §8) → recovery is a continuation `jules_message`, not a fresh dispatch. Probe with one focused message ("your state is COMPLETED but no branch on origin — please push and reply with PR URL") and give ~5 minutes. After 2-3 probes still no branch, switch to local subagent + extracted patch — never re-dispatch a fresh session on the same spec.
2. **Approve quickly when truly awaiting.** If a session is in `AWAITING_PLAN_APPROVAL` for an extended time the Jules backend may discard it. Fetch the plan and approve fast. (This is distinct from the `COMPLETED` case above — only `AWAITING_PLAN_APPROVAL` has the timeout risk; `COMPLETED` sessions persist indefinitely.)
3. **Stop is not supported.** The Jules API does not expose a stop/cancel method.
4. **Harvest via patches.** The `auto_create_pr=True` flag is currently unreliable. The preferred harvest path is `jules_patch_apply(session_id)` or `tools/jules-patch-extract.py <sid>`. Alternatively, prompt the agent to push to `jules/<alias>` branches.
5. **Always verify branch on remote before trusting `COMPLETED`.** Use `mcp__github__list_branches` to confirm the work was published. State alone is not evidence of delivery.

## Writing prompts Jules can act on

Name the tools Jules actually has so it picks them naturally — e.g. cite
`replace_with_git_merge_diff` for partial edits, `run_in_bash_session` for
shell work, `pre_commit_instructions()` before `submit`, and
`request_code_review()` for a Critic pass before the human sees the PR.
Point Jules at `Plan/JULES_PROTOCOL.md` and any local `AGENTS.md` so it loads
the binding rules during exploration. For multi-file tasks, request a
`list_files` + `read_file` pass first. Full cheatsheet (environment, AGENTS.md
scoping, Standard + Special tools): [`references/jules-native-toolset.md`](references/jules-native-toolset.md).

## References

For deeper behaviour, see the following reference files:

- **State Machine:** See [`references/state-machine.md`](references/state-machine.md) for the full lifecycle and what to do in each state.
- **Error Handling:** See [`references/error-normalization.md`](references/error-normalization.md) for HTTP error codes and normalisation.
- **Worked Examples:** See [`references/worked-examples.md`](references/worked-examples.md) for concrete sequences of user requests.
- **Parallel Orchestration:** See [`references/parallel-orchestration.md`](references/parallel-orchestration.md) for fan-out tasks and batching.
- **Harvest Patterns:** See [`references/harvest-patterns.md`](references/harvest-patterns.md) for the differences between PR harvest and patch harvest.
- **Caveats:** See [`references/caveats.md`](references/caveats.md) for what this skill does NOT do and edge-cases.
- **Combined Watcher:** See [`references/combined_watcher.md`](references/combined_watcher.md) for the orchestrator's polling pattern (multi-session + multi-PR), plus the canonical Python script at [`references/combined_watcher.py`](references/combined_watcher.py). Use this when you have ≥2 in-flight Jules sessions or open PRs to track.
- **Jules native toolset & DSL:** See [`references/jules-native-toolset.md`](references/jules-native-toolset.md) — what tools Jules actually has, and how to instruct it to use them.
