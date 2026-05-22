---
slug: 0002-single-codemode-mcp-server
type: adr
status: ready
owner: claude
created: 2026-05-19
updated: 2026-05-19
domain: shared
wave: A
adr_id: ADR-0002
adr_status: Proposed
adr_supersedes: []
adr_superseded_by: []
related:
  - 2026-05-19-agency-base-canvas
  - harness-vocabulary
  - 002-manifest-and-marketplace
  - 008-codemode-registry
  - 0004-anchor-triad-as-wire-form
summary: Collapse to one FastMCP server `agency-mcp` hosting all domain handlers + the anchor triads. `session-log-mcp` folds into `domains/shared/handlers/session_log.py`; `jules-plugin/mcp-server` is decommissioned.
---

# ADR-0002 — Single codemode MCP server (`agency-mcp`)

## Context and Problem Statement

Today the harness hosts (or plans) three MCP servers: `agency-mcp` (codemode + anchor triad, partially built), `jules-plugin/mcp-server` (the legacy jules orchestrator MCP shipped under `jules-plugin/`), and `session-log-mcp` (a side-quest server documented by lesson 11). Three servers means three startup costs, three classifier instances, three `manifest.json` views, three independent permission surfaces, and three places to register a tool. Cross-server tool calls cannot share the `_AnchorAwareCodeMode` classifier or the Wave D graph cache.

Canvas §4 names the destination: **"One MCP — `agency-mcp` — codemode + anchor triad (tool-side + skill-side, six eager tools total)."** Spec 008 (`008-codemode-registry`) already lays the registry plumbing. The decision is whether to commit to that one-server end-state and decommission the others, or to keep multi-MCP for isolation.

## Decision Drivers

- Canvas §1 ("Six pillars") — pillar 2 is *"One MCP — `agency-mcp`"*.
- Canvas D-02 (v2 recommendation, unchanged from v1): *"YES. session-log-mcp folds into `domains/shared/handlers/session_log.py`."*
- Lesson 11 (`11-side-quest-session-log-mcp.md`) — session-log-mcp was a side-quest server; its tools belong in the `shared` domain.
- VOCABULARY §1 invariant: *"one plugin, one MCP server."* (Top-line invariant — already canon, this ADR just ratifies.)
- Spec 008 already specifies `_AnchorAwareCodeMode` as a single classifier — multi-MCP forces N classifiers and breaks the spec.

## Considered Options

### Option A — Single `agency-mcp` server, fold the other two (RECOMMENDED)

One FastMCP process. All five handler-bearing domains (music, novel, jules, context, shared) register into it. Anchor triads (ADR-0004) live in `domains/shared/handlers/anchors.py`. `session-log-mcp` becomes `domains/shared/handlers/session_log.py` — same tools, no separate process. `jules-plugin/mcp-server` is decommissioned (its 16 tools port into `domains/jules/handlers/`).

### Option B — Keep multi-MCP, add a proxy

Status quo plus a proxy server that aggregates tools from the three backends. Preserves isolation but adds a fourth process; the proxy itself needs a classifier; tool calls cross two processes minimum. Failure modes multiply.

### Option C — Keep multi-MCP, no proxy

Status quo. Each server stands alone; users register them independently in `settings.json`. No code change cost today; high coordination cost forever.

## Decision Outcome

**Chosen: Option A — single `agency-mcp` server.**

- `agency-mcp` is the canonical server. Path: `servers/agency-mcp/`.
- All five handler-bearing domains register via `Domain.register(mcp)` (ADR-0003).
- `session-log-mcp` is decommissioned in spec 009 (`009-shared-handlers`); its handlers move to `domains/shared/handlers/session_log.py`.
- `jules-plugin/mcp-server` is decommissioned in spec 006 (`006-jules-handlers-port`); its 16 tools port to `domains/jules/handlers/`.
- The classifier (`_AnchorAwareCodeMode`) is a single instance per process; defer-vs-eager classification spans the full tool catalogue.

## Consequences

### Positive

- One startup cost, one classifier, one manifest view — matches VOCABULARY §1 invariant.
- Anchor triads (ADR-0004) work uniformly across all domains; no cross-server search hops.
- Wave D graph (ADR-0008) can index one process's tool catalogue without proxy fanout.
- Fewer permission grants in `settings.json` (one server, one `allow` entry per tool family).
- Spec 008's `_AnchorAwareCodeMode` design holds without modification.

### Negative

- Single-process failure mode: an OOM or panic in one domain's handler can take down all five. Mitigation: handler-level try/except + ToolResult error envelope (ADR-0005).
- Decommissioning `jules-plugin/mcp-server` is a breaking change for any user with the standalone jules plugin installed. The Jules orchestration plugin block in CLAUDE.md cites the standalone path; that doc must update on cutover.
- Folding `session-log-mcp` requires re-implementing its tools as `@domain_tool`-decorated handlers in `domains/shared/handlers/session_log.py` — non-trivial port surface (~6 tools, lesson 11).

### Neutral

- The MCP wire protocol stays MCP — no client changes needed beyond endpoint reconfiguration.
- Per-tool permission grants stay one-grant-per-tool; just under one server now.

## Falsifier triggers

- If a sixth distinct MCP server lands in the harness for any reason other than third-party plugins (e.g. for an isolated sandbox), the single-server invariant is broken — successor ADR.
- If the classifier's defer-vs-eager performance degrades non-linearly past ~200 tools (canvas estimate: ~150 handler-bearing tools across 5 domains), the single-process assumption is falsified — sharding ADR follows.
- If a single-process panic takes the whole harness offline more than once per release cycle, isolation matters more than uniformity — successor reopens Option B.
