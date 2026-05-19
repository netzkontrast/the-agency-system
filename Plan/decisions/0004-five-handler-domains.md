---
type: adr
status: draft
slug: five-handler-domains
summary: "Six fixed domains: music, novel, jules, context, shared are handler-bearing today; agentic ships skills now with 32 handlers planned in Spec 016."
created: 2026-05-19
updated: 2026-05-19
owner: jules
adr_id: ADR-0004
adr_status: Proposed
adr_owner: jules
adr_tags: [domain:cross, topic:architecture]
adr_supersedes: null
adr_superseded_by: null
---

# ADR-0004 — Six fixed domains; agentic is skill-shipping with planned handlers

## Context and Problem Statement

The system's capabilities are divided into specific namespace domains, but the exact set and nature of these domains are only implicitly defined across various documents (e.g., `Plan/harness/VOCABULARY.md:94`, `Plan/harness/design.md:280`). We must formalise the exact list of domains and distinguish between those that contain executable handlers (Python code) today and those that are conceptual/skill-only today but planned to grow handlers per existing specs.

A naive reading of "agentic is skill-only" conflicts with `Plan/016-agentic-handlers-and-skills/spec.md` (lines 7-17 and 44-51), which explicitly authors 32 first-class MCP tools under `servers/agency-mcp/src/agency_mcp/handlers/agentic/*` and is `status: ready`. The ADR must not invalidate Spec 016; it must instead capture the current state of disk (no agentic handlers yet) plus the planned trajectory (Spec 016 lands 32 handlers).

## Decision Drivers

- Establishing a bounded taxonomy for categorising all new tools and skills.
- Ensuring the Harness Path A/B structures have a fixed set of targets to normalise.
- Clarifying where cross-cutting orchestrator logic belongs.

## Considered Options

1. **Fixed Six (5 handler-bearing + agentic, with agentic on a state-of-disk vs planned trajectory)** — `music`, `novel`, `jules`, `context`, `shared` are handler-bearing today; `agentic` ships skills today (`skills/agentic/`) and gains 32 native handlers when Spec 016 lands.
2. **Fixed Five plus skill-only agentic (originally chosen, now revised)** — Treat agentic as permanently skill-only. Rejected because it conflicts with Spec 016 (ready, scheduled in Phase 7) which authors 32 agentic handlers; agents enforcing this would treat Spec 016 as architecturally invalid.
3. **Open/Dynamic Domains** — Allow arbitrary new domains to be created at will. Rejected because it complicates cross-domain orchestration, graph ontology generation, and the `agency-system` tool registration loop.

## Decision Outcome

Chosen option: **Fixed Six**. The repository contains six fixed domains: `music`, `novel`, `jules`, `context`, `shared` already expose FastMCP tools today (handler modules under `servers/agency-mcp/src/agency_mcp/handlers/<name>/`). `agentic` currently ships only skills (`skills/agentic/`) but has **32 first-class MCP tools planned** in `Plan/016-agentic-handlers-and-skills/spec.md` (lines 7-17, 44-51, `status: ready`). When Spec 016 lands, `agentic` becomes the sixth handler-bearing domain and `handlers/agentic/` is populated; until then, agentic-domain skills compose tools exposed by the other five domains.

The set is **closed**: no seventh domain ships without superseding this ADR.

## Consequences (Positive / Negative / Neutral)

- **Positive:** Provides a rigid, predictable structure for the `servers/agency-mcp/src/agency_mcp/handlers/` directory.
- **Positive:** Clarifies that, **today**, agentic-domain skills compose tools from the other five domains. Once Spec 016 lands, agentic gains native handlers.
- **Positive:** Spec 016 is no longer architecturally invalid under this ADR — it is the agentic domain's first handler module.
- **Negative:** Adding a genuinely new top-level domain (e.g., `cli`, `web`) requires a formal architectural update and refactoring of the registration loop.
- **Neutral:** VOCABULARY §4 will be aligned in the same PR to read "five domains with handlers on disk today + agentic with planned handlers (Spec 016)" rather than the bare "agentic skill-only".

## Falsifier triggers

This ADR must be reconsidered and superseded if:
1. A seventh top-level domain (e.g., `web`, `system`) is added to the repository.
2. Spec 016 is abandoned without being superseded — i.e., the planned 32 agentic handlers are explicitly rejected as part of a strategy shift back to "agentic = orchestration-only".
3. A handler-bearing domain (one of the six) is consolidated into another or removed.
