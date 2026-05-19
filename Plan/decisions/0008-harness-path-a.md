---
type: adr
status: draft
slug: harness-path-a
summary: "The harness implements Path A (levers L-α, L-β, L-γ) now; Path B (full restructuring) is deferred as vision."
created: 2026-05-19
updated: 2026-05-19
owner: jules
adr_id: ADR-0008
adr_status: Proposed
adr_owner: jules
adr_tags: [domain:cross, topic:architecture]
adr_supersedes: null
adr_superseded_by: null
---

# ADR-0008 — Harness Path A levers ship now; Path B is vision

## Context and Problem Statement

The repository needs to normalise the interface across domains (domain isomorphism). `Plan/harness/design.md:280` identified two paths. Path A uses light wrappers (levers L-α, L-β, L-γ) to adapt the existing code. Path B is a full restructuring into `domains/<name>/` behind a `Domain` base class (`Plan/harness/restructure/spec.md`).

## Decision Drivers

- Immediate need for cross-domain uniformity without halting concurrent work.
- Avoiding massive merge conflicts across ~60 parallel Jules sessions.

## Considered Options

1. **Harness Path A** — Ship light normalisation levers now.
2. **Harness Path B** — Halt feature work and execute the full domain restructuring. Rejected because it creates an unacceptable merge bottleneck and blocks all Phase 2-8 progress.
3. **Harness Path C** — Move skills only. Rejected as an incomplete half-measure.

## Decision Outcome

Chosen option: **Harness Path A**. We commit to the Harness Path A trajectory: the three low-cost levers (L-α unified `register(mcp)`, L-β `@domain_tool` decorator, L-γ manifest auto-sync) are designed and approved in `Plan/harness/design.md` §11.2 and §11.6.1 but ship in a follow-up implementation PR alongside the harness design's first tag. Today's code base still uses the per-module registration pattern (`register_<domain>_<module>_handlers`). Path B (`Plan/harness/restructure/spec.md`) is on record as vision.

## Consequences (Positive / Negative / Neutral)

- **Positive:** Unblocks immediate harness development without causing repository-wide merge conflicts.
- **Negative:** Leaves technical debt (the underlying structure is still not perfectly isomorphic, requiring wrapper functions).
- **Neutral:** Path B remains fully designed and ready for execution when timing permits.
- **Neutral:** Until the implementation PR lands, future authors should not assume `domain_tool` exists; check imports before using.

## Falsifier triggers

This ADR must be reconsidered and superseded if:
1. A Phase 7+ spec hits the limit of Path A's capabilities, making Path B mandatory before Phase 8.
2. The `Plan/harness/restructure/spec.md` is executed and merged.
