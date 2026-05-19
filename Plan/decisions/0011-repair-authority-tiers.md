---
type: adr
status: draft
slug: repair-authority-tiers
summary: "All changes must be classified into T1/T2/T3/T4 repair-authority tiers before execution."
created: 2026-05-19
updated: 2026-05-19
owner: jules
adr_id: ADR-0011
adr_status: Proposed
adr_owner: jules
adr_tags: [domain:cross, topic:governance]
adr_supersedes: null
adr_superseded_by: null
---

# ADR-0011 — Repair-authority tiers (T1/T2/T3/T4) on every change

## Context and Problem Statement

To prevent agents or humans from quietly making structural changes via inline edits, the system needs a strict classification of changes. `Plan/harness/VOCABULARY.md:12` (via §6C) documents four tiers: T1 Mechanical, T2 Additive, T3 Structural, and T4 Immutable. This implicitly governs all mutations but needs formal architectural codification.

## Decision Drivers

- Preventing silent structural drift (T3 changes masquerading as T1 typos).
- Protecting immutable records (T4) like Accepted ADRs.
- Defining clear boundaries for when a formal Spec is required.

## Considered Options

1. **Four-Tier System (T1-T4)** — Formalise the existing tier definitions.
2. **Binary System (Trivial vs Major)** — Simpler, but lacks the nuance needed to protect immutable records while allowing additive text. Rejected as too coarse.

## Decision Outcome

Chosen option: **Four-Tier System (T1-T4)**. Every change is classified: T1 (typos, mechanical) and T2 (additive) can be done in-place. T3 (structural, rewording, schemas) must be done via a formal Task/Spec. T4 (immutable records like Accepted ADRs) must never be mutated; they can only be superseded.

## Consequences (Positive / Negative / Neutral)

- **Positive:** Clear rules of engagement for Jules subagents modifying files.
- **Positive:** Guarantees historical accuracy of decision records.
- **Negative:** Adds procedural overhead for restructuring documentation.

## Falsifier triggers

This ADR must be reconsidered and superseded if:
1. The planned tier-validation mechanism (a `tier:` parameter on a future MCP mutation tool per VOCABULARY §6C, or an equivalent enforcement surface) is shipped and subsequently removed or weakened — supersede this ADR with one that names the new enforcement gap. Until that mechanism ships, the current enforcement is human discipline + commit-message classification, and this ADR documents the discipline rather than a code-level invariant.
2. A new tier is required to handle a category of changes not covered by T1-T4.
