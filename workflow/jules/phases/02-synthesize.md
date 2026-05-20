---
phase_id: "02"
entry_verb: "query"
description: "Synthesize the Finding nodes for a topic into a single research brief."
---

# Phase 02 — Synthesize

The synthesize phase consumes the `Finding` nodes that phase 01
produced for a topic and renders them into a single research brief.
The brief uses the Jinja template at
`context/jules/templates/research-brief.md.jinja` (shipped by the jules
context cell, see task 1) so the formatting is consistent across runs.

**Inputs.** A `topic` string identifying which Findings to bundle. The
phase reads matching Finding nodes from the graph via the row's
`mcp__jules_query` handler — v0.1 returns a placeholder summary, with
real aggregation arriving alongside the cross-row dispatch in spec 09.

**Outputs.** A Markdown research brief plus an `Artefact` node
recording the brief's bytes (driver-keyed via `artifact_driver` per
spec 08-v1 §FR3) and a `SATISFIES_PHASE` edge linking the artefact to
`phase:jules/02`.

**Gate.** The `research-complete` hard-blocking gate (in
`workflow/jules/gates/research-complete.yaml`) blocks this phase until
the graph contains at least one Finding for the topic. If the gate
fails, the runner short-circuits with `status="blocked_on_gate"` and
the gate's `on_failure.message` becomes the envelope's `blocked_reason`
— synthesize will not run on an empty graph.
