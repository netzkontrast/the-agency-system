---
lesson_id: 09
slug: watcher-pattern-idiom
severity: low
seen_in: [all-sessions]
applies_to:
  - jules-mcp
  - orchestrator-patterns
captured_at: 2026-05-17
---

# The combined-poller watcher pattern works

## Pattern

I built `/tmp/jules_combined_watcher.py` early in the session and reused it across the whole wave. It:

- Takes JSON files listing tracked Jules session IDs + tracked PR numbers.
- Polls every 60s; emits one JSONL event per state change.
- Persists seen state in `/tmp/jules_combined_watcher_state.json` so restarts don't double-fire.
- Exits the moment a "wake state" hits (AWAITING_PLAN_APPROVAL, AWAITING_USER_FEEDBACK, COMPLETED, FAILED, CANCELLED) OR a new PR comment appears.
- Lets the orchestrator (me) idle between events without burning context tokens on polling.

It's small (~70 lines) and saved enormous amounts of context-token spend versus inline `sleep`/poll loops.

## What to change

### Bake this pattern into the Jules MCP or skill

This is a generic enough idiom that it should live somewhere durable:

- Option A: New Jules MCP tool `jules_watch_until(sids, prs, wake_states, timeout_s)` that blocks until a wake event, returning the event payload.
- Option B: A `jules-watcher` standalone script in the jules-plugin, callable from any orchestrator.
- Option C: A SKILL.md in `skills/jules/` describing how to roll this pattern with sample code.

Option A is cleanest — single round-trip from orchestrator perspective. Option B is most portable. Option C is the lowest-effort starting point.

### Loosen the wake-state set

I originally included `PAUSED` in the wake set — bit me on spec 012 because PAUSED was a transient state during message processing, not a real human-required pause. Loosened to omit `PAUSED`. Lesson: distinguish "transient internal states" from "human-required states".

## Concrete deliverable for the meta-spec

Probably option B (a script in jules-plugin/bin/) — least intrusive, most reusable. The script becomes `bin/jules-watch-until --sessions sids.json --prs prs.json --wake AWAITING_PLAN_APPROVAL,COMPLETED,FAILED`.
