---
slug: 0006-frontmatter-canon
type: adr
status: ready
owner: claude
created: 2026-05-19
updated: 2026-05-19
domain: shared
wave: A
adr_id: ADR-0006
adr_status: Proposed
adr_supersedes: []
adr_superseded_by: []
related:
  - 2026-05-19-agency-base-canvas
  - harness-vocabulary
  - 134-plan-adr-convention
  - 0005-shared-toolresult-envelope
  - 0008-wave-d-ontology-graph
summary: Adopt 14 canonical L1 frontmatter fields plus an `extra:` map for L2 namespace keys; one JSONSchema is the contract; a PreToolUse hook validates on every `Write` to `*.md`.
---

# ADR-0006 — Frontmatter canon (14 fixed L1 fields + `extra:` map)

## Context and Problem Statement

VOCABULARY §6A specifies 14 canonical frontmatter keys (`slug`, `summary`, `status`, `type`, `owner`, `created`, `updated`, `depends_on`, `related`, `supersedes`, `superseded_by`, `affects`, `domain`, `wave`). Adoption is uneven: some Plan/ artefacts carry the canon plus L2 namespace keys (e.g. `adr_id`, `task_uses_prompts`); others carry ad-hoc keys (`lesson_id`, `seen_in`); some skills miss `summary` entirely. There is no machine-checkable contract — the canon is prose-only.

Canvas §6 ("Schemas everywhere") names a destination: one JSONSchema (`lib/schemas/frontmatter.schema.json`) plus a PreToolUse hook (`frontmatter_validate.py`) that fires on every `Write` to `*.md`. The hook is the only point where canon adherence is forced.

The two open shape questions:
1. **Fixed or extensible?** A pure-fixed schema forbids new L2 keys (e.g. `lesson_id`); a pure-free-form schema rots the canon.
2. **Per-type or single schema?** ADRs need `adr_id`; lessons need `lesson_id`; skills need `skill_kind`. Either we ship N schemas keyed by `type:` or one schema with conditional branches.

Canvas D-08 picks 14 + `extra:`. This ADR ratifies that choice and the single-schema-with-`type`-keyed-branches shape.

## Decision Drivers

- Canvas §6 ("Schemas everywhere") — names the schema, the hook, the lint.
- Canvas D-08 — picks 14 + `extra:`.
- VOCABULARY §6A — the canonical 14 keys, already documented.
- VOCABULARY §6B — reciprocity rules (`supersedes` ↔ `superseded_by`, etc.) must be enforced; the schema can't enforce them alone, but a companion validator can.
- Lesson 06 (`06-spec-vs-schema-drift.md`) — schema-as-source-of-truth is the corpus pattern.
- Spec 134 (`134-plan-adr-convention`) — already specifies a `check_adr.py` validator; this ADR generalises that pattern to all `*.md` artefacts.

## Considered Options

### Option A — 14 canonical L1 fields + `extra:` map (RECOMMENDED)

The schema fixes the 14 L1 keys verbatim, with their types and required/optional flags per VOCABULARY §6A. L2 namespace keys (e.g. `adr_id`, `lesson_id`, `skill_kind`) live inside an optional `extra:` mapping. The PreToolUse hook validates the L1 fields strictly; the `extra:` map is permissive (any string-keyed scalars). Per-type schemas for `extra:` shape live as JSONSchema $defs (e.g. `$defs/adr-extra`, `$defs/lesson-extra`) keyed by `type:`.

### Option B — Pure free-form (status quo)

Keep the prose canon; no JSONSchema. Zero migration cost; locks in drift.

### Option C — Fully fixed (no `extra:`)

The schema lists every L1 + L2 key ever used in the corpus. New L2 keys require a schema update. Strictest; highest review-friction for new artefact types.

### Option D — Per-type schemas

One JSONSchema per `type:` (`spec.schema.json`, `adr.schema.json`, `lesson.schema.json`, etc.). The PreToolUse hook dispatches on `type:`. More files to maintain; harder to share L1 invariants across types.

## Decision Outcome

**Chosen: Option A — 14 fixed L1 fields + `extra:` map, one schema with `type`-keyed `$defs`.**

- Schema lives at `lib/schemas/frontmatter.schema.json` (canvas §6).
- L1 keys: per VOCABULARY §6A, no additions, no removals. `summary` cap differs per `type:` (≤120 for skills, ≤240 for ADRs/specs/research); enforced by the schema's `maxLength` keyword inside the type-keyed `$defs`.
- L2 keys: live inside an optional `extra: {...}` mapping. Each `type:` has a `$defs/<type>-extra` branch listing its expected L2 keys. The branch is permissive on L2 keys it doesn't name (so a session-state artefact's `session_id` field doesn't break the schema when the schema hasn't yet enumerated it).
- The PreToolUse hook `hooks/frontmatter_validate.py` runs on every `Write` to `*.md`; load + parse YAML frontmatter; validate against the schema; block on error.
- Reciprocity (VOCABULARY §6B) is **not** enforced by this schema — that's the manifest-generator's job (canvas §7 spec 009 + spec 134's `check_adr.py`). The schema handles per-file shape; the validator handles cross-file invariants.

## Consequences

### Positive

- One schema, one hook, one validation surface — `Write` to any `*.md` either passes the canon or is blocked at hook-time.
- `extra:` map preserves room for new artefact types without schema-version bumps. Adding "session-state" to the corpus is a one-line `$defs` addition, not a 14-field re-spec.
- Per-type `maxLength` for `summary` codifies the existing VOCABULARY §6A split (120/240).
- The schema becomes the source-of-truth for downstream tooling (manifest generator, graph ingestor, ADR validator).

### Negative

- `extra:` is a soft escape hatch. Authors who don't know a key's correct home can dump it in `extra:` and never get flagged. Mitigation: per-type `$defs` document the *expected* L2 keys, surfacing intent without forbidding the new.
- The PreToolUse hook adds latency to every `Write` on `*.md`. YAML parse + schema validation is fast (~ms) but uniform.
- Migration cost: every existing `*.md` artefact in `Plan/` must be audited for L1 compliance. The corpus has ~80 artefact subtrees; mass-edit cost is real but bounded.
- Schema and VOCABULARY §6A are now two surfaces describing the same canon. Lesson 06 says the schema wins on disagreement, but a human reading VOCABULARY may not know that.

### Neutral

- No change to the skill/spec body sections; only frontmatter shape is gated.
- The hook does not retroactively gate files already in `main` — only `Write` events.

## Falsifier triggers

- If `extra:` accumulates more than ~12 distinct top-level keys across all types, the "fixed L1 + small extra map" claim is breaking — successor ADR re-promotes some L2 keys to L1.
- If the PreToolUse hook ships a `--skip` flag and that flag is used in `main` more than once per release cycle, the enforcement surface is being routed around — successor ADR.
- If a third schema (e.g. `frontmatter-strict.schema.json` next to `frontmatter.schema.json`) lands, the "one schema" claim is broken — successor ADR.
