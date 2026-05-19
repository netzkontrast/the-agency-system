---
type: adr
status: draft
slug: context-mode-path-b
summary: "Context Mode uses Path B (native JSON manifest) rather than Path A (mksglu adapter) for document index deferral."
created: 2026-05-19
updated: 2026-05-19
owner: jules
adr_id: ADR-0007
adr_status: Proposed
adr_owner: jules
adr_tags: [domain:context, topic:architecture]
adr_supersedes: null
adr_superseded_by: null
---

# ADR-0007 — Context Mode Path B (native manifest) chosen over Path A

## Context and Problem Statement

To prevent token window bloat, the system defers loading full documentation until requested. There were two proposed paths to achieve this: Path A (using the `mksglu` adapter) and Path B (a native JSON manifest). The decision to use Path B is documented across Phase 4 docs (`Plan/phase-4-context-mode-path-b/README.md:1-20`) and the overview (`Plan/000-overview.md:16-16`), but requires formalisation.

## Decision Drivers

- Token efficiency.
- Reducing external dependencies.
- Integration with the Wave D ontology graph.

## Considered Options

1. **Path A (`mksglu` adapter)** — Use the existing external adapter. Rejected because it adds an unnecessary dependency and doesn't cleanly integrate with our internal graph IDs.
2. **Path B (Native JSON Manifest)** — Implement a custom `context_manifest.json` schema.

## Decision Outcome

Chosen option: **Path B (Native JSON Manifest)**. The system relies on a native JSON manifest (`context_manifest.json`) that catalogues documents with `{id, title, summary, sha256, tags, views}` and integrates with the Code Mode anchor triad (`context_search`, `context_describe`, `context_read`).

## Consequences (Positive / Negative / Neutral)

- **Positive:** Zero external dependencies for context discovery.
- **Positive:** Trivial integration with the Wave D Cypher graph via shared `graph_id`s.
- **Negative:** Requires custom tooling to generate and sync the manifest.

## Falsifier triggers

This ADR must be reconsidered and superseded if:
1. The native BM25/keyword ranking proves inadequate for context search, forcing a return to an external adapter.
2. The `context_manifest.json` is replaced by a live vector database.
