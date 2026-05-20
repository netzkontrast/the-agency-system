---
phase_id: "01"
entry_verb: "query"
description: "Issue an investigative query and record one or more Finding nodes for the topic."
---

# Phase 01 — Research

The research phase is the first step in the jules row's research
workflow (phases 01-02), parallel to the orchestration workflow
(phases 03-08). Its job is to take a `topic` (a short subject keyword)
and produce one or more `Finding` nodes in the ontology graph that
capture what the query surfaced. The phase delegates to the row's
`mcp__jules_query` MCP tool — the v0.1 implementation lives at
`agentic/jules/handlers/query.py` and returns a placeholder finding so
the cell-loader / hook / ontology wiring can be exercised end-to-end
before real retrieval lands in a later phase.

**Inputs.** A `topic` string keyword argument. The tool tolerates a
missing topic by defaulting to the empty string so callers can probe
the envelope shape without arguments.

**Outputs.** A `tool_result` envelope whose `data.findings` lists the
raw findings. PostToolUse ingests any `artefact_metadata` on the
envelope as an `Artefact` node and emits a `DERIVED_FROM` / `SATISFIES_PHASE`
edge where appropriate; the gate evaluator picks up
`research-complete` next to decide whether phase 02 may run.

**Gate.** The `research-complete` gate (see
`workflow/jules/gates/research-complete.yaml`) blocks the `synthesize`
phase until at least one Finding exists for the topic. The gate is
hard-blocking and is evaluated on entry to phase 02, not phase 01 — the
research phase itself runs without a precondition.
