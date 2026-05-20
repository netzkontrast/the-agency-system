---
phase_id: "07"
entry_verb: "recover"
description: "Extract a silent-failed session's patch metadata into a SessionPatch node; advance state to PATCH_EXTRACTED."
---

# Phase 07 — Recover

The recover phase only runs on sessions whose verify outcome was
`SILENT_FAIL`. It pulls the patch summary via `jules_patch_summary`
(metadata only — no diff body in the model context), upserts a
`SessionPatch` ontology node, links it to the JulesSession via a
`DERIVED_FROM` edge, and bumps the session to `PATCH_EXTRACTED`.

This phase deliberately does NOT shell out to git. Applying the patch
is the integrate phase's responsibility. Splitting extraction from
application means a SessionPatch node lives in the graph as soon as
recovery starts — auditable even when the subsequent apply fails or
the caller opts for `apply=false`.

**Inputs.**
- `session_id` (string, required).

**Outputs.** Envelope `data.state="PATCH_EXTRACTED"`, plus
`data.files`, `data.patch_bytes`, `data.lines_added`,
`data.lines_removed`. Next suggested tool is `mcp__jules_integrate`.

**State machine.** Only `SILENT_FAIL → PATCH_EXTRACTED`. Other
incoming states reject with `SESSION_STATE_INVALID`.

**Gates.** None — recover is itself the recovery flow, and the
state-machine check at the handler boundary is sufficient.
