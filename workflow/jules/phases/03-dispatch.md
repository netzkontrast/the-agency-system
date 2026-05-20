---
phase_id: "03"
entry_verb: "dispatch"
description: "Create a Jules session for the task brief; record the new JulesSession ontology node in state DISPATCHED."
---

# Phase 03 — Dispatch

The dispatch phase is the entry point of the Jules-orchestration
workflow. It takes a `prompt`, an `owner`, and a `repo`, resolves the
GitHub source to an opaque Jules source id, calls `jules_create`, and
upserts a `JulesSession` node into the ontology with the freshly
minted session id.

**Inputs.**
- `prompt` (string, required): the task brief sent to Jules.
- `owner` (string, required): GitHub owner / org.
- `repo` (string, required): repository name.
- `branch` (string, default `"main"`): starting branch.
- `title` (string, optional): human-readable session title.
- `require_plan_approval` (bool, default `true`): when true, Jules
  halts at AWAITING_PLAN_APPROVAL so phase 04 has something to
  approve.

**Outputs.** A `tool_result` envelope whose `data.session_id` carries
the Jules id, `data.state` is `"DISPATCHED"`, and `data.url` is the
Jules web UI URL. The `next_suggested_tools` field nominates
`mcp__jules_await_plan` as the natural follow-up.

**State machine.** Dispatch is the only entry that legally writes a
new JulesSession node. Subsequent phases load the existing node by
`session_id` and refuse to run on an unknown id with
`SESSION_NOT_FOUND`.

**Gates.** No gates — dispatch is the source of new sessions, so the
graph cannot have a precondition that depends on one.
