---
type: adr
status: draft
slug: sub-spec-zero-padding
summary: "Plan/ uses zero-padded NNN-<slug>/spec.md for sub-specs to ensure stable lexical sorting."
created: 2026-05-19
updated: 2026-05-19
owner: jules
adr_id: ADR-0002
adr_status: Proposed
adr_owner: jules
adr_tags: [domain:cross, topic:structure]
adr_supersedes: null
adr_superseded_by: null
---

# ADR-0002 — Plan/ uses zero-padded NNN-<slug>/spec.md for sub-specs

## Context and Problem Statement

Sub-specifications within the `Plan/` directory need a consistent naming and numbering scheme to ensure they are listed chronologically and are easy to reference. Currently, the tree implicitly uses a three-digit zero-padded prefix (e.g., `000-overview.md`, `008-codemode-registry/spec.md`) as seen throughout the repository structure, but this is not formally documented.

## Decision Drivers

- Predictable file and directory sorting in IDEs and GitHub.
- Easy unambiguous referencing in PRs and other documents (e.g., "Spec 008").
- Avoiding the "1, 10, 2" sorting problem inherent in non-padded numbering.

## Considered Options

1. **`NNN-<slug>` (Zero-padded 3 digits)** — E.g., `042-new-feature`. Provides stable sorting up to 999 specs.
2. **Unpadded `<N>-<slug>`** — E.g., `42-new-feature`. Rejected because `10-x` sorts before `2-y`, making directory listings confusing.
3. **Date-based prefixing** — E.g., `YYYY-MM-DD-<slug>`. Rejected because specs are often long-lived and updated; a sequential ID is better for referencing than a creation date.

## Decision Outcome

Chosen option: **`NNN-<slug>` (Zero-padded 3 digits)**. Sub-spec directories use `NNN-<slug>` for original specs and `NNNa-<slug>` / `NNNb-<slug>` etc. for lettered follow-ups that extend the same scope (cf. `Plan/004a-music-lib-port/` extending Spec 004, and `Plan/011a-novel-handlers-core-hardening/` extending Spec 011). The canonical document resides at `<directory>/spec.md`.

## Consequences (Positive / Negative / Neutral)

- **Positive:** Lexicographical sorting matches chronological/sequential ordering perfectly.
- **Positive:** References like "Spec 042" map unambiguously to `042-*` directories.
- **Negative:** Hard limit at 999 specs.
- **Neutral:** Requires authors to manually find the next available number.
- **Neutral:** Lettered suffix is the canonical extension pattern when a spec spawns hardening / lib-port follow-ups too small for a fresh number.

## Falsifier triggers

This ADR must be reconsidered and superseded if:
1. The project approaches 999 specs (requiring a move to 4 digits).
2. The `Plan/` directory structure is fundamentally reorganised (e.g., fully replaced by the phase-folder model).
