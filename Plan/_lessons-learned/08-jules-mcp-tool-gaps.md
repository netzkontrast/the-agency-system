---
lesson_id: 08
slug: jules-mcp-tool-gaps
severity: medium
seen_in: [all-sessions]
applies_to:
  - jules-mcp
captured_at: 2026-05-17
---

# Gaps in the Jules MCP tool surface

## Pattern (observations across ~10 Jules sessions)

### 1. `jules_stop` is unsupported

The Jules v1alpha API has no cancel mechanism. When I wanted to stop a redundant session (e.g. spec-004 dormant), `jules_stop` returned `{"error": "unsupported"}`. The workaround was `jules_message` with a "STAND DOWN" instruction. Sometimes Jules respected it; sometimes it kept iterating.

### 2. State polling has racy reads

`jules_get(sid)` sometimes shows `IN_PROGRESS` immediately after a `FAILED` event the watcher caught. The state appears to oscillate or have eventual-consistency lag. This bit me twice — once I thought a FAILED session had self-revived, but it hadn't.

### 3. No "session bundle" tool

I had to call `jules_get + jules_activities (paginated) + jules_patch_summary` to assemble a full session view. A single `jules_session_summary(sid, max_activities=N)` tool returning {state, title, plan, activities_tail, patch_summary} would have saved hundreds of round-trips.

### 4. No "register webhook" tool

I rely on a Python polling loop (`/tmp/jules_combined_watcher.py`) because Jules has no push notification for state changes. A `jules_register_webhook(url, events=[...])` would let me wire a real notification service.

### 5. `jules_bulk` CLI was broken in this checkout

The `jules-bulk quota` subcommand bombed with `'jules_mcp.server' has no attribute 'jules_quota'` because the tools are defined in `jules_mcp/tools/bulk.py` but never re-exported on the server module. Easy to fix.

## What to change

### Add to Jules MCP

| Tool | Purpose | Notes |
|---|---|---|
| `jules_session_summary(sid)` | One-call view: state + title + recent activities + patch summary | Cuts orchestrator round-trips ~5x |
| `jules_stop(sid)` (real impl) | Genuine cancel | Requires upstream API support; if unavailable, document the workaround in the tool's "unsupported" error message |
| `jules_register_webhook(url)` | Push notifications | Eliminates polling; orchestrator can subscribe per-session |
| `jules_quota` re-exported on `jules_mcp.server` | Fix the bulk CLI breakage | Trivial: add `from .tools.bulk import jules_quota` to `server.py` |

### Fix `jules-bulk` CLI

The wrapper script calls `jules_mcp.server.jules_quota` directly. Either re-export the tools on `server.py` OR rewrite the wrapper to call `jules_mcp.tools.bulk.jules_quota`. The current behaviour (broken CLI) cost me a few minutes diagnosing on the first session.

## Concrete deliverable for the meta-spec

Two specs likely warranted:
1. **Plan/098-jules-mcp-tool-additions.md** — adds `jules_session_summary`, fixes the bulk CLI, documents `jules_stop` limitation in the docstring.
2. **Plan/JULES_PROTOCOL.md** — adds a "Tool gaps and workarounds" appendix listing the current limitations so future orchestrators don't rediscover them.
