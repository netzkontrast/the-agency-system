---
type: adr
status: draft
slug: code-mode-anchor-triad
summary: "Code Mode uses eager registration for ~4 anchor tools per domain; all other tools are deferred."
created: 2026-05-19
updated: 2026-05-19
owner: jules
adr_id: ADR-0006
adr_status: Proposed
adr_owner: jules
adr_tags: [domain:cross, topic:performance]
adr_supersedes: null
adr_superseded_by: null
---

# ADR-0006 — Code Mode anchor triad is eager; bulk tools are deferred

## Context and Problem Statement

To maintain the strict < 500 token boot budget for the MCP server, we cannot eagerly load schemas for all 100+ tools. The repository relies on FastMCP's Code Mode (`Plan/008-codemode-registry/spec.md:53`, `Plan/000-overview.md:16`), but the exact split between what is eager and what is deferred is an implicit convention.

## Decision Drivers

- Token budget constraints (`tools/list` < 4 KB).
- Model discoverability (the model needs *some* starting point to know what capabilities exist).

## Considered Options

1. **Anchor Triad + Deferred Bulk** — Register ~4 "anchor" tools per domain eagerly (e.g., `search`, `describe`, `invoke`); defer the rest by classifying them as deferred via `lib/codemode/deferred_loader.register_tool()`.
2. **All Eager** — Register all tools normally. Rejected because it blows past the 34k token boot context, breaking the core directive of the refactor.
3. **All Deferred** — Defer everything, relying solely on `search_tools`. Rejected because Claude struggles to discover capabilities if the initial `tools/list` is completely empty.

## Decision Outcome

Chosen option: **Anchor Triad + Deferred Bulk**. We use an eager anchor triad (typically `search`, `describe`, `invoke`/`read`) for each domain. These anchors are registered normally. All other tools are registered and stamped with a classification (`eager`, `deferred`, `background`) via `lib/codemode/deferred_loader.register_tool()`. The CodeMode transform (configured in `server.py`) is what hides deferred tools from `tools/list` at listing time. The manifest classification is the audit invariant; the transform is the runtime mechanism (cf. `deferred_loader.py:1-45` and `Plan/008-codemode-registry/spec.md`).

## Consequences (Positive / Negative / Neutral)

- **Positive:** Solves the token budget problem while maintaining discoverability.
- **Negative:** Requires strict discipline when adding new tools (must remember to defer them).
- **Negative:** Adds latency as the model must make an extra round-trip to discover tool schemas.

## Falsifier triggers

This ADR must be reconsidered and superseded if:
1. FastMCP fundamentally changes how Code Mode or deferred schemas work.
2. The number of eager tools grows to the point where `tools/list` exceeds 4 KB.
