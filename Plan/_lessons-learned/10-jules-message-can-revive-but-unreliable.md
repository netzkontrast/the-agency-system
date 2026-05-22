---
lesson_id: 10
slug: jules-message-can-revive-but-unreliable
severity: low
seen_in: [spec-004a-first-attempt, spec-004-stand-down]
applies_to:
  - jules-mcp
  - orchestrator-patterns
captured_at: 2026-05-17
---

# `jules_message` to a FAILED/COMPLETED session: revive-or-not is racy

## Pattern

- Spec 004a first attempt **FAILED**. I sent `jules_message` hoping to revive. The state briefly showed `IN_PROGRESS` again — but the user (correctly) believed the session was truly dead. Jules did no real follow-up work. My retry-dispatch was the right call.
- Spec 004 (dormant): after PR #36 marked DRAFT BLOCKED, I sent a "stand down" message. Jules apparently absorbed it (sent an acknowledging `agentMessaged`) but the session stayed `IN_PROGRESS` rather than going `COMPLETED`. Tedious.

## What this means

`jules_message` is best understood as "context injection into the session's history" — not as a true control plane. Side effects (state transitions, resumption, cancellation) are unreliable.

## What to change

### Orchestrator policy

- Treat `jules_message` as **input to a session you expect to continue running**. Use it for clarifications / approvals / mid-stream answers.
- Do NOT treat it as a way to revive FAILED sessions, cancel IN_PROGRESS sessions, or modify session intent. For those, dispatch a fresh session with a new alias.
- After `jules_message`, ALWAYS poll state for ≥2 cycles to confirm the message actually moved the session forward. Don't trust a single immediate `jules_get`.

### Jules MCP docstring

`jules_message`'s docstring should call out this limitation:

> WARNING: `jules_message` injects text into the session's input stream. It does NOT guarantee the session will act on the message (Jules may already be in a terminal state, or may have moved past the input it would have processed). For control-plane operations (stop, restart), the API does not currently support them; dispatch a fresh session instead.

## Concrete deliverable for the meta-spec

Tiny: update the `jules_message` tool docstring in `jules-plugin/mcp-server/src/jules_mcp/tools/lifecycle.py`. Document the "session-stop is unsupported; dispatch fresh" workaround in JULES_PROTOCOL.md Appendix.
