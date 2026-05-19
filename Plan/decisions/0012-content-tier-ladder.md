---
type: adr
status: draft
slug: content-tier-ladder
summary: "Every artefact follows a three-tier progressive disclosure ladder (T1 Trigger, T2 Body, T3 References)."
created: 2026-05-19
updated: 2026-05-19
owner: jules
adr_id: ADR-0012
adr_status: Proposed
adr_owner: jules
adr_tags: [domain:cross, topic:architecture]
adr_supersedes: null
adr_superseded_by: null
---

# ADR-0012 — Three-tier content ladder

## Context and Problem Statement

To support the L3 daemon's progressive disclosure goals and prevent large documents from overwhelming the context window upon initial discovery, artefacts must be structurally divided. `Plan/harness/VOCABULARY.md:12` (§6D) specifies a T1/T2/T3 content tier model, which is distinct from the repair-authority tiers.

## Decision Drivers

- Token budget management during tool discovery and use.
- Clear delineation between immediate context and deep-dive reference material.

## Considered Options

1. **Three-Tier Ladder** — T1 Trigger (manifest summary), T2 Body (the main file), T3 References (unlimited size sidecars).
2. **Flat Documents** — Load everything at once. Rejected because it violates the token efficiency north star.

## Decision Outcome

Chosen option: **Three-Tier Ladder**. Every artefact must support progressive loading:
- **T1 Trigger:** ≤ 200 chars target (currently the extractor emits up to ~400 chars synthesised from title + first body paragraph; tightening to use the frontmatter `summary:` field verbatim is tracked as a follow-up to Spec 111 / the build-context-manifest script).
- **T2 Body:** ≤ 5 KB, loaded on explicit dispatch.
- **T3 References:** Unlimited size, lives in a `references/` subdirectory, loaded only on specific demand.

## Consequences (Positive / Negative / Neutral)

- **Positive:** Drastically reduces token usage during the discovery phase.
- **Negative:** Requires authors to strictly partition their documentation.
- **Neutral:** Until the manifest extractor is tightened to honour the cap (or to use the frontmatter `summary:` verbatim per VOCABULARY §6A), agents validating against this ADR will measure non-compliance on every artefact. The aspirational cap is preserved; the closure of the gap is follow-up work on `build_context_manifest.py`.

## Falsifier triggers

This ADR must be reconsidered and superseded if:
1. The token constraints are relaxed to the point where full document loading is preferred.
2. The L3 daemon is redesigned to stream documents rather than using discrete tiers.
