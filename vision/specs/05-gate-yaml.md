---
slug: spec-05-gate-yaml
type: spec
status: ready
owner: claude
created: 2026-05-19
updated: 2026-05-19
summary: YAML schema for `workflow/<row>/gates/<gate-id>.yaml`. Defines hard-blocking and advisory gates with pluggable evaluators (callable/schema/sql/manual). `on_success.emit_edge` is the canonical way to emit `SATISFIES_PHASE` graph edges, resolving the gate-edge-emission ownership tension from Phase 3.
affects:
  - vision/specs/05-gate-yaml.md
depends_on:
  - vision/workflow/INTEGRATED-DRAFT.md
  - vision/context/INTEGRATED-DRAFT.md
referenced_by:
  - vision/specs/01-cell-manifest.md
  - vision/specs/07-workflow-base.md
---

# Spec 05 — Gate YAML

## Purpose

Gates are the policy unit of the workflow column. Each gate lives at
`workflow/<row>/gates/<gate-id>.yaml` and is referenced from the row's
`manifest.toml` `[[gates]]` table (see spec 01). The workflow runner
evaluates gates at phase boundaries; hard-blocking gate failures halt
the pipeline, advisory gate failures surface warnings without blocking.

This spec resolves the Phase 3 gate-edge-emission ownership tension.
The workflow runner OWNS gate evaluation and edge construction; the
context column INGESTS the emitted edge via its PostToolUse hook. When
a gate passes, the runner constructs a `SATISFIES_PHASE` edge per
`on_success.emit_edge` and writes it into `tool_result.data`. The
context store's PostToolUse hook upserts that edge into the SQLite
ontology graph. Workflow defines and executes; context ingests.

## Schema

JSON Schema (draft 2020-12), `$id = "tag:agency-system.local,2026:schema:shared/gate"`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "tag:agency-system.local,2026:schema:shared/gate",
  "type": "object",
  "additionalProperties": false,
  "required": ["id", "type", "evaluator"],
  "properties": {
    "id":          {"type": "string", "pattern": "^[a-z][a-z0-9-]{0,60}$"},
    "type":        {"enum": ["hard-blocking", "advisory"]},
    "description": {"type": "string"},
    "blocks_phase":{"type": "string", "pattern": "^[0-9]{2}$"},
    "evaluator": {
      "type": "object",
      "required": ["kind"],
      "properties": {
        "kind":     {"enum": ["callable", "schema", "sql", "manual"]},
        "module":   {"type": "string"},
        "callable": {"type": "string"},
        "args":     {"type": "object"}
      }
    },
    "on_success": {
      "type": "object",
      "properties": {
        "emit_edge": {
          "type": "object",
          "required": ["type", "from", "to"],
          "properties": {
            "type":            {"const": "SATISFIES_PHASE"},
            "from":            {"type": "string"},
            "to":              {"type": "string"},
            "target_ontology": {"type": "string"}
          }
        }
      }
    },
    "on_failure": {
      "type": "object",
      "properties": {
        "message":        {"type": "string"},
        "fix_hint_tools": {"type": "array", "items": {"type": "string"}}
      }
    }
  },
  "allOf": [
    {
      "if":   {"properties": {"type": {"const": "hard-blocking"}}},
      "then": {"required": ["blocks_phase"]}
    }
  ]
}
```

## Evaluator kinds

Four kinds; each has a fixed signature the runner enforces:

| Kind     | Signature / contract |
|----------|----------------------|
| callable | Python `(envelope: dict, args: dict) -> {ok: bool, message: str}`. Imported from `workflow.runner.evaluators.<module>`. Pure; no I/O beyond envelope. |
| schema   | Validates a context node payload against a JSON Schema. `args.schema_id` selects schema; `args.node_id` selects node. ok=true iff valid. |
| sql      | Cypher-like query against the context SQLite store. `args.query` is the query. ok=true iff result set non-empty. Read-only. |
| manual   | Passes when a human acknowledges via `workflow.resume(session_id, phase_id, "approve")`. Runner yields `status="blocked_on_gate"` until ack. |

Return-shape enforcement: evaluators MUST yield a dict with exactly
the keys `ok` (bool) and `message` (string). Extra keys are rejected.
A raised exception is treated as `ok=false`, `message = repr(exc)`.

## Worked example

`workflow/music/gates/lyrics-reviewed.yaml`:

```yaml
id: lyrics-reviewed
type: hard-blocking
description: |
  Lyrics for the current track have passed the 14-point QC.

evaluator:
  kind: callable
  module: workflow.runner.evaluators.frontmatter_status
  callable: assert_status_equals
  args:
    field: review_status
    expected: passed

blocks_phase: "03"

on_success:
  emit_edge:
    type: SATISFIES_PHASE
    from: artefact
    to: phase:music/02
    target_ontology: workflow.phase

on_failure:
  message: |
    Lyrics review has not passed yet. Run `/bitwize-music:lyric-reviewer`
    on the current track, then retry.
  fix_hint_tools:
    - mcp__music_lyric_review
```

Flow: runner enters phase `03`. Before the phase body, it loads the
gate, resolves `from: artefact` against the active artefact node (per
`[storage]` in the context manifest), calls the evaluator, and on
`ok=true` writes the `SATISFIES_PHASE` edge into
`tool_result.data.emitted_edges[]`. The PostToolUse hook in the
context store upserts the edge into SQLite.

## Acceptance criteria

```gherkin
Scenario: Hard-blocking gate halts pipeline on failure
  Given a hard-blocking gate "lyrics-reviewed" with blocks_phase = "03"
  And the evaluator returns {ok: false, message: "review missing"}
  When the runner reaches phase "03"
  Then the runner yields PhaseStateEnvelope with status = "blocked_on_gate"
  And phase "03" body is NOT executed
  And the failure message reaches the caller in tool_result.data.error

Scenario: on_success emits SATISFIES_PHASE edge
  Given a gate with on_success.emit_edge defined
  And the evaluator returns {ok: true, message: "passed"}
  When the runner records the gate pass
  Then tool_result.data.emitted_edges contains exactly one edge
  And that edge has type = "SATISFIES_PHASE"
  And the context PostToolUse hook upserts the edge into SQLite

Scenario: Advisory gate surfaces warning only
  Given an advisory gate (type = "advisory") with no blocks_phase
  And the evaluator returns {ok: false, message: "voice-check warning"}
  When the runner records the gate failure
  Then tool_result.warnings contains the gate message
  And the next phase executes normally
  And no SATISFIES_PHASE edge is emitted

Scenario: Callable evaluator return-shape enforced
  Given a callable evaluator returns {ok: true, extra: "field"}
  When the runner validates the return value
  Then validation fails with error "evaluator return must be exactly {ok, message}"
  And the gate is treated as ok=false

Scenario: Manual gate awaits resume
  Given a gate with evaluator.kind = "manual"
  When the runner reaches that gate
  Then the runner yields status = "blocked_on_gate"
  And the session persists until workflow.resume(session_id, phase_id, "approve") is called
  And on resume the gate is treated as ok=true
```

## Dependencies

- `vision/specs/01-cell-manifest.md` — `[[gates]]` table references gate files at `workflow/<row>/gates/<gate-id>.yaml`.
- `vision/specs/02-tool-result-envelope.md` — emitted edges and gate state live inside `tool_result.data`; root envelope is frozen.
- `vision/specs/04-phase-state-envelope.md` — wraps `tool_result` for workflow yields; the runner surfaces gate failures via `status = "blocked_on_gate"`.
- `vision/specs/07-workflow-base.md` — implements the gate evaluator and edge-emission logic defined here.
- `vision/workflow/INTEGRATED-DRAFT.md` — establishes `on_success: emit_edge` as the workflow column's resolution to graph-emission ownership.
- `vision/context/INTEGRATED-DRAFT.md` — establishes the PostToolUse-driven ingestion path for emitted edges.
