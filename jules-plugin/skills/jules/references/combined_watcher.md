# Combined watcher pattern

`combined_watcher.py` is a context-safe polling loop the orchestrator
uses to track multiple in-flight Jules sessions + PRs without burning
tokens between events. Internal-loop mode — exits only on real events
(state transitions to `AWAITING_PLAN_APPROVAL` / `AWAITING_USER_FEEDBACK`
/ `COMPLETED` / `FAILED` / `CANCELLED`, or a new PR comment / review /
check_run failure).

## Usage

```bash
# Track 4 sessions + 2 PRs, exit on first event or after 6h deadline
python3 jules-plugin/skills/jules/references/combined_watcher.py \
    /tmp/jules_sessions.json /tmp/jules_prs.json
```

Input files:
- **`sessions.json`** — JSON list of Jules session IDs to poll
- **`prs.json`** — JSON list of `{"owner", "repo", "number"}` triples

State is persisted to `/tmp/jules_combined_watcher_state.json` so
restarts don't double-fire on already-seen events.

## Heartbeat mode

A heartbeat variant (exit every 60s with `{"event": "heartbeat"}`)
was tried during the 2026-05-17 session and reverted — the token cost
of replying to each tick outweighed the container-keepalive benefit.
Internal-loop mode is the canonical setup.

## When to use vs not

**Use when:** you have ≥2 in-flight Jules sessions OR ≥1 open PR you
need to track for new comments / Codex reviews.

**Don't use when:** the orchestrator is doing focused single-session
work — direct `jules_get` / `pull_request_read` calls are fine for one
session.

## Companion tool

`tools/jules-patch-extract.py` — when a session ends `COMPLETED` but
the watcher reports no branch on remote, that script recovers the work
via `session.outputs[].changeSet.gitPatch.unidiffPatch`. See
`Plan/JULES_PROTOCOL.md §8`.

## Future direction

This pattern should be folded into the `jules` MCP server itself as
a `jules_watch` tool (per Spec 101 jules-mcp-tool-additions) so it
becomes invokable via the unified MCP surface rather than a shell
subprocess. Until then, the script lives here as the canonical
implementation reference.
