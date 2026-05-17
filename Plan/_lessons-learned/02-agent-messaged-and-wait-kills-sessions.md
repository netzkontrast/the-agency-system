---
lesson_id: 02
slug: agent-messaged-and-wait-kills-sessions
severity: high
seen_in: [spec-004a-first-attempt]
applies_to:
  - jules-protocol
  - spec-author
  - jules-mcp
captured_at: 2026-05-17
---

# agentMessaged-and-wait kills sessions

## Pattern

Spec 004a first attempt (`sessions/3738904739183261333`) hit a real ambiguity (tools/mixing wasn't in `affects:`). Jules sent the question via `agentMessaged` and… waited. The session went to **FAILED** state. The Jules platform appears to timeout sessions that block on `agentMessaged` for too long.

I revived it via `jules_message` (interestingly, FAILED → IN_PROGRESS — so message can restart) but in practice Jules treats it as dead and the work is at risk.

## Contrast with the right pattern

JULES_PROTOCOL §6 escalation says: open a draft PR labelled `[BLOCKED: <reason>]`, paste the ambiguity verbatim, propose two interpretations, and stop. This works because:

- The session COMPLETES cleanly (state → COMPLETED).
- The PR remains as a durable artefact.
- The human responds via PR comment on their own timeline — no session timeout.
- The session can be re-dispatched fresh (new quota slot) once the spec is clarified.

The `agentMessaged`-and-wait pattern doesn't satisfy any of these. The session is held open indefinitely, hits a hard timeout, and dies.

## What to change

### JULES_PROTOCOL §6 should explicitly forbid `agentMessaged`-and-wait:

> When you reach an ambiguity that needs human clarification, **NEVER** use `agentMessaged` and then idle waiting for a response. The session will time out and FAIL, losing work. Instead, ALWAYS use the BLOCKED-PR escalation: open a draft PR labelled `[BLOCKED: <reason>]`, paste the ambiguity, propose two interpretations, and submit. The session COMPLETES; the human responds asynchronously via PR comment.

### Dispatch prompts should reinforce this

Every dispatch prompt should include the line: "If anything is ambiguous, open a draft PR labelled `[BLOCKED: clarification]` and stop — do NOT use agentMessaged-and-wait (that killed spec 004a's first attempt)." I've been adding this to recent prompts; should be in the template.

## Concrete deliverable for the meta-spec

Patch `Plan/JULES_PROTOCOL.md` §6 with explicit anti-pattern callout. Also worth considering: does the Jules MCP's `jules_message` tool docstring discourage clients from using it as a synchronous prompt? It should — its only legitimate use is human-initiated context-injection into a session, not session-to-human Q&A.
