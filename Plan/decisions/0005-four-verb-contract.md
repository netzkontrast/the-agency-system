---
type: adr
status: draft
slug: four-verb-contract
summary: "The harness operates on a strict four-verb contract: list_tools, call_tool, list_skills, dispatch_skill."
created: 2026-05-19
updated: 2026-05-19
owner: jules
adr_id: ADR-0005
adr_status: Proposed
adr_owner: jules
adr_tags: [domain:cross, topic:architecture]
adr_supersedes: null
adr_superseded_by: null
---

# ADR-0005 — Four-verb harness contract

## Context and Problem Statement

The interaction between the different layers of the system (L1 in-process, L2 hook chain, L3 HTTP daemon) requires a unified interface. Currently, this interface is described implicitly or as a "design" in `Plan/harness/design.md:24` and `Plan/harness/VOCABULARY.md:24`. We need to formally decide that these four specific verbs are the only required interface to interact with the system's capabilities.

## Decision Drivers

- Cross-layer consistency (L1 through L3 must expose the same capabilities).
- Minimising the surface area of the API.
- Abstracting the underlying FastMCP implementation from the higher-level orchestrators.

## Considered Options

1. **Four-Verb Contract** — Restrict the interface to exactly `list_tools`, `call_tool`, `list_skills`, and `dispatch_skill`.
2. **Expose FastMCP Directly** — Let consumers interact directly with FastMCP internals. Rejected because it breaks encapsulation and makes it impossible to insert middleware (like the L2 hook chain) consistently.
3. **Expanded API** — Add verbs for streaming, subscribing, etc. Rejected because the current use cases (Claude Code integration, Jules batching) are fully satisfied by request-response tooling.

## Decision Outcome

Chosen option: **Four-Verb Contract**. The cross-layer invariant for interacting with the-agency-system is strictly limited to four operations: `list_tools`, `call_tool`, `list_skills`, and `dispatch_skill`. All harness layers (L1, L2, L3) must implement exactly these four.

## Consequences (Positive / Negative / Neutral)

- **Positive:** Extremely simple API surface for new consumers to implement.
- **Positive:** Trivial to mock and test.
- **Negative:** Cannot support real-time streaming or pub/sub without breaking the contract.

## Falsifier triggers

This ADR must be reconsidered and superseded if:
1. A fifth verb (e.g., `subscribe_events`, `stream_tool`) is added to the harness interface.
2. The separation between "tools" (executable handlers) and "skills" (markdown prompts) is eliminated.
