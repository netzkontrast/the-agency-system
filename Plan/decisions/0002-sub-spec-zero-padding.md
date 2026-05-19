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

Chosen option: **`NNN-<slug>` (Zero-padded 3 digits)**. All sub-spec directories must be named with exactly three digits, zero-padded, followed by a hyphen and a descriptive kebab-case slug. The canonical document resides at `Plan/NNN-<slug>/spec.md`.

## Consequences (Positive / Negative / Neutral)

- **Positive:** Lexicographical sorting matches chronological/sequential ordering perfectly.
- **Positive:** References like "Spec 042" map unambiguously to `042-*` directories.
- **Negative:** Hard limit at 999 specs.
- **Neutral:** Requires authors to manually find the next available number.

## Falsifier triggers

This ADR must be reconsidered and superseded if:
1. The project approaches 999 specs (requiring a move to 4 digits).
2. The `Plan/` directory structure is fundamentally reorganised (e.g., fully replaced by the phase-folder model).
