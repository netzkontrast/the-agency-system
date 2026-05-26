---
phase_id: "05"
entry_verb: "monitor"
description: "Probe the session's Jules-API state once; record it on the JulesSession node. Caller drives external polling."
---

# Phase 05 — Monitor

The monitor phase is a one-shot polling primitive. It issues a single
`jules_get`, stamps the observed Jules-API state onto the local
`JulesSession.jules_state` field, and:

- On `COMPLETED` — bumps local state to `COMPLETED`, stamps
  `completed_at`, suggests `mcp__jules_verify` next.
- On `FAILED` — bumps local state to `FAILED`, stamps `last_error`.
- On any other state (`IN_PROGRESS`, `AWAITING_PLAN_APPROVAL`) —
  returns `still_running=true` so the caller can poll again. No local
  state transition.

The pipeline drives the outer poll loop; this phase intentionally
does not block on a Jules state change so it does not hold a tool
slot open for the duration of the session.

**Inputs.**
- `session_id` (string, required).

**Outputs.** Envelope `data.state` carries the **local** label;
`data.jules_state` carries the API label; `data.still_running` is
`true` whenever the session has not yet reached a terminal label.

**Gates.** Blocked by `plan-approved` (hard-blocking) — the session
must have advanced past `AWAITING_PLAN_APPROVAL` before monitoring
proceeds. This catches callers who skip phase 04 entirely.
