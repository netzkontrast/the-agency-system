---
type: adr
status: draft
slug: single-mcp-server
summary: "the-agency-system mounts a single MCP server (agency-system); session-log-mcp is a sibling event store, not a tool surface."
created: 2026-05-19
updated: 2026-05-19
owner: jules
adr_id: ADR-0003
adr_status: Proposed
adr_owner: jules
adr_tags: [domain:cross, topic:architecture]
adr_supersedes: null
adr_superseded_by: null
---

# ADR-0003 — One MCP server (agency-system); session-log-mcp is a sibling event store

## Context and Problem Statement

The system architecture needs a clear boundary for what is exposed to the language model. According to `Plan/000-overview.md:16` (North Star), the repository uses "One MCP, Code Mode native". However, Phase 6 introduces `servers/session-log-mcp/` (`Plan/phase-6-quality-loop-compaction/README.md:9`). We need to formalise that this does not violate the "One MCP" invariant because the session-log server is an internal event store consumed by hooks, not a tool surface exposed to the model.

## Decision Drivers

- Maintaining a strict token budget for the model's boot context (< 500 tokens).
- Keeping the tool discovery surface (`tools/list`) unified and compact.
- Distinguishing between model-facing capabilities and internal system infrastructure.

## Considered Options

1. **Single model-facing MCP (`agency-system`) + internal infrastructure MCPs** — Keep `agency-system` as the only server exposed in `.mcp.json`. Run other servers (like `session-log-mcp`) purely for internal component communication.
2. **Multiple model-facing MCPs** — Expose `session-log-mcp` and potentially others directly to the model. Rejected because it fragments the tool surface, bloats the boot context, and complicates cross-domain orchestration.

## Decision Outcome

Chosen option: **Single model-facing MCP (`agency-system`) + internal infrastructure MCPs**. The `agency-system` server is the singular tool surface. Any other MCP servers (e.g., `session-log-mcp`) are strictly internal event stores or infrastructure backends consumed via hooks (PostToolUse / PreCompact, etc.), and are never mounted in the primary `.mcp.json` for the model.

## Consequences (Positive / Negative / Neutral)

- **Positive:** Protects the < 500 token boot budget.
- **Positive:** Centralises all tool registration and dispatch logic.
- **Negative:** Internal communication might require its own setup/routing separate from the model's MCP connection.

## Falsifier triggers

This ADR must be reconsidered and superseded if:
1. A third sibling MCP server appears that is designed to be directly interacted with by the model.
2. The primary `.mcp.json` is modified to mount multiple distinct server binaries.
