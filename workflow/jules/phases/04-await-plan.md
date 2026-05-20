---
phase_id: "04"
entry_verb: "await_plan"
description: "Poll the session; when state=AWAITING_PLAN_APPROVAL, call jules_approve and bump local state to IN_PROGRESS."
---

# Phase 04 — Await Plan

This phase is the planning checkpoint. Jules generates a multi-step
plan, halts at state `AWAITING_PLAN_APPROVAL`, and waits for an
explicit approve call. The phase handler is one-shot: it issues a
single `jules_get`, and either approves (default), persists a
Continuation for human review (`auto_approve=False`), or returns
`still_waiting=True` when the session is still in `IN_PROGRESS` (so an
external caller can poll again).

**Inputs.**
- `session_id` (string, required): the JulesSession id minted by
  phase 03.
- `auto_approve` (bool, default `true`).

**Outputs.** Envelope `data.session_id` echoes the input; `data.state`
is either `IN_PROGRESS` (approved) or `AWAITING_PLAN_APPROVAL` (when
the caller opted out of auto-approve). On the latter case the envelope
also sets `blocked_on_user=true` and a `resume_token` so the pipeline
persists a Continuation.

**State machine.** Legal transitions from any non-terminal state into
`IN_PROGRESS`. The handler also tolerates a Jules-API state of
`COMPLETED` (the session skipped past planning) and advances the
local label accordingly.

**Gates.** No precondition gate — the handler itself rejects with
`SESSION_NOT_FOUND` when the JulesSession is missing.
