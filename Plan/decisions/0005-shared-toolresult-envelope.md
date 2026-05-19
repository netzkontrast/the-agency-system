---
slug: 0005-shared-toolresult-envelope
type: adr
status: ready
owner: claude
created: 2026-05-19
updated: 2026-05-19
domain: shared
wave: A
adr_id: ADR-0005
adr_status: Proposed
adr_supersedes: []
adr_superseded_by: []
related:
  - 2026-05-19-agency-base-canvas
  - harness-vocabulary
  - 130-shared-toolresult-envelope
  - 117-tool-result-archive
  - 0003-domain-plugin-contract
  - 0007-code-mode-opt-in
summary: Adopt a shared `ToolResult` TypedDict + authoritative JSONSchema, enforced by a `@domain_tool` decorator. Replaces the hand-rolled per-handler dict pattern.
---

# ADR-0005 — Shared ToolResult envelope (TypedDict + authoritative JSONSchema)

## Context and Problem Statement

Every MCP handler today returns a dict-shaped result, hand-rolled per handler. The canonical hand-roll lives at `handlers/shared/skills.py:48-54` (canvas §0); the same shape is re-implemented dozens of times across the music, jules, and shared domains with subtle drift (missing `warnings`, inconsistent `error` shape, ad-hoc `artefacts_written`). Lesson 06 (`06-spec-vs-schema-drift.md`) names this drift class explicitly: when spec prose and runtime shape disagree, runtime wins and the spec rots. Spec 130 (`130-shared-toolresult-envelope`) was filed to fix this but has not shipped.

Canvas §5 promotes spec 130 to the base and adds the missing piece: a **schema-authoritative** envelope. The prose in spec 130 describes the schema; the schema (`lib/schemas/toolresult.schema.json`) is the contract. Per lesson 06, when prose and schema disagree, the schema wins.

The `@domain_tool` decorator is the enforcement surface: it wraps every handler return value in the `ToolResult` shape and validates against the JSONSchema before emission.

## Decision Drivers

- Canvas §5 ("The envelope: `ToolResult`") — specifies the schema verbatim plus the decorator signature.
- Canvas §1 pillar 3 ("One Envelope").
- Lesson 06 — schema-vs-prose drift is a measured failure class in this corpus.
- Lesson 14 (`14-token-consumption-postmortem.md`) — oversize result bodies were a top-3 token sink; the envelope's `archived_to:` field plus the spec-117 archive intercept that pattern.
- Spec 130 already specifies the wire shape; this ADR ratifies the schema-authority clause and the decorator enforcement surface.

## Considered Options

### Option A — TypedDict + authoritative JSONSchema, enforced via `@domain_tool` (RECOMMENDED)

`ToolResult` is a `TypedDict` for Python static analysis. The truth is `lib/schemas/toolresult.schema.json` — generators emit the TypedDict from the schema. The decorator `@domain_tool(domain, summary, ...)` (canvas §5 signature) wraps every handler: validates input against `input_schema`, wraps the return value, routes oversize bodies (> 4 KB) to the spec-117 archive, emits Wave D graph nodes (ADR-0008).

### Option B — Pydantic model

`ToolResult` as a Pydantic v2 model. Stronger runtime validation, automatic schema export. Adds a heavy dependency (pydantic) to every handler entry point. Heavier per-call cost (validation on every invocation). Loses the schema-as-source-of-truth pattern — Pydantic's exported schema vs. the hand-curated JSONSchema becomes a new drift surface.

### Option C — Hand-rolled dict (status quo)

Keep the per-handler dict. Zero migration cost. Locks in the lesson-06 drift class forever. No way to enforce `warnings` is present, `error` is shaped correctly, or oversize bodies are archived.

### Option D — MCP-native return shape only

Drop the envelope; return whatever shape each MCP tool wants. Loses cross-handler uniformity entirely. Breaks the router's ability to inspect `next_suggested_tools` (ADR-0001 step 6 depends on it).

## Decision Outcome

**Chosen: Option A — TypedDict + authoritative JSONSchema + `@domain_tool` decorator.**

- Schema lives at `lib/schemas/toolresult.schema.json` (canvas §5 body, verbatim).
- TypedDict lives at `lib/envelope/toolresult.py`, generated from the schema by `bin/agency-gen-types` (per canvas §13 spec 006).
- Decorator lives at `lib/envelope/decorator.py`; signature is canvas §5's `domain_tool(...)`.
- Schema-authority clause: when the schema and the prose in spec 130 (or any spec) disagree, the schema wins (lesson 06).
- Required fields: `ok`, `warnings`, `artefacts_written`. Optional: `data`, `next_suggested_tools`, `error`, `archived_to`.
- The decorator routes any return body > 4 KB to the spec-117 archive and replaces it with a pointer in `archived_to`. This is the wire-level mitigation for lesson 14.
- Migration: `handlers/shared/skills.py:48-54` (the canonical hand-roll) gets `@domain_tool(domain="shared", summary="...", anchor=True)`; the returned dict shape is preserved bit-for-bit; existing tests pass without modification.

## Consequences

### Positive

- One envelope shape across the whole MCP surface — no per-handler drift. Lesson 06's class is closed.
- The decorator centralises five behaviours (registration, wrapping, input validation, archive routing, graph emission); each had been a per-handler concern.
- Schema-as-source-of-truth means future schema-driven tooling (graph queries, manifest validation, MCP introspection) all read from one file.
- The `archived_to:` field plus spec-117 archive routing is the structural fix for lesson 14's oversize-body sink.

### Negative

- Migrating ~44 existing handlers to the decorator is non-trivial work and a measurable surface for regressions. The bit-for-bit return-shape invariant in §5 mitigates risk but does not eliminate it.
- TypedDict gives no runtime validation — without the decorator running, a handler could return any shape and Python would not complain. The decorator is therefore load-bearing; bypassing it (e.g. for performance) silently breaks the contract.
- The decorator wraps every handler call in extra Python frames; per-call overhead is small (microseconds) but non-zero and uniform.
- Schema generators (TypedDict from JSONSchema) add a build-step dependency — drift between the generated TypedDict and the schema is a new (smaller) failure class.

### Neutral

- The schema does not change the MCP wire format; clients see the same JSON shape they always did.
- Code-Mode-flagged skills (ADR-0007) consume `ToolResult` no differently from default skills — the envelope is orthogonal to code-mode opt-in.

## Falsifier triggers

- If a handler ships in `main` without `@domain_tool` for two consecutive PR cycles, the enforcement surface is being routed around — successor ADR mandates lint coverage.
- If the JSONSchema and the TypedDict drift in `main` (generator broken or skipped), schema-as-source is falsified — successor reopens the generator contract.
- If oversize bodies (>4 KB) bypass `archived_to:` for a measurable fraction of handlers (per spec-117 telemetry), the decorator's archive routing is not closing lesson 14 — successor ADR.
