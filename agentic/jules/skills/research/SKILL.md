---
name: research
description: Research a topic and return findings as a tool-result envelope.
model: claude-opus-4-7
---

# research

Use this skill when a caller needs a structured investigation of a single
topic — a question, a claim to verify, a person, a project, or a concept —
and wants the result back as a tool-result envelope ready to be ingested
by the context column.

## Inputs

- `topic` (string, required): the subject under investigation. One topic
  per invocation; if the caller has several, dispatch the skill once per
  topic in parallel.

## Outputs

A standard `tool_result` envelope (see
`context/_shared/schemas/tool_result.schema.json`). On success,
`data.topic` echoes the input and `data.findings` is a non-empty list of
finding strings. `warnings` and `next_suggested_tools` are empty for the
v0.1 placeholder implementation.

## When to use it

Reach for `research` whenever upstream work needs background context
before drafting, planning, or deciding — for example, before promoting an
idea to an album, before writing lyrics that lean on real-world events,
or before answering a question that depends on facts the caller does not
already hold. Skip it when the caller already has verified sources in
hand; this skill produces findings, not citations.

The v0.1 implementation is a placeholder that returns a single synthetic
finding so downstream wiring (cell loader, hooks, ontology) can be
exercised end-to-end. Real retrieval, ranking, and citation come in a
later phase.
