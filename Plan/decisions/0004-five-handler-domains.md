---
type: adr
status: draft
slug: five-handler-domains
summary: "The system consists of exactly five handler-bearing domains plus an agentic skill-only domain."
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

# ADR-0004 — Five handler-bearing domains + agentic skill-only

## Context and Problem Statement

The system's capabilities are divided into specific namespace domains, but the exact set and nature of these domains are only implicitly defined across various documents (e.g., `Plan/harness/VOCABULARY.md:94`, `Plan/harness/design.md:280`). We must formalise the exact list of domains and distinguish between those that contain executable handlers (Python code) and those that are purely conceptual/skill-based.

## Decision Drivers

- Establishing a bounded taxonomy for categorising all new tools and skills.
- Ensuring the Harness Path A/B structures have a fixed set of targets to normalise.
- Clarifying where cross-cutting orchestrator logic belongs.

## Considered Options

1. **Fixed Set (5+1)** — Formally define `music`, `novel`, `jules`, `context`, and `shared` as handler-bearing domains, and `agentic` as a skill-only domain.
2. **Open/Dynamic Domains** — Allow arbitrary new domains to be created at will. Rejected because it complicates cross-domain orchestration, graph ontology generation, and the `agency-system` tool registration loop.

## Decision Outcome

Chosen option: **Fixed Set (5+1)**. The repository contains exactly five handler-bearing domains (`music`, `novel`, `jules`, `context`, `shared`) which expose FastMCP tools, and one skill-only domain (`agentic`) which contains orchestrator skills but no native Python handlers.

## Consequences (Positive / Negative / Neutral)

- **Positive:** Provides a rigid, predictable structure for the `servers/agency-mcp/src/agency_mcp/handlers/` directory.
- **Positive:** Clarifies that `agentic` skills must rely on tools exposed by the other five domains.
- **Negative:** Adding a genuinely new domain (e.g., `cli` or `web`) requires a formal architectural update and refactoring of the registration loop.

## Falsifier triggers

This ADR must be reconsidered and superseded if:
1. A new top-level domain (e.g., `web`, `system`) is added to the repository.
2. The `agentic` domain is modified to include its own native Python handlers instead of purely composing existing tools.
