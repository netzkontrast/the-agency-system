---
slug: agentic-vision
type: vision-charter
status: draft
owner: claude
created: 2026-05-19
summary: Consolidates the vision for the `agentic` column within the 3xN agency matrix, outlining canonical cell shapes, integration patterns, and Gherkin scenario compliance.
affects:
  - vision/agentic/Vision.md
---

# Agentic Column Vision

This document consolidates the architectural vision for the `agentic` column of the `agency-system`. It synthesizes the matrix invariants defined in `00.1-Overview.md`, the integration resolutions from `INTEGRATED-DRAFT.md`, and the foundational patterns harvested from prior MVPs (`the-agency-system` and `agency`).

## 1. Role in the Matrix

The `agentic` column owns the **WHO** and the **HOW** of the system.
It is the execution engine, the intent router, and the boundary layer between the human prompt environment (Claude Code) and the system's inner workings.

**It explicitly does NOT own:**
- Pipeline state, phase order, or gating rules (owned by `workflow`).
- Schemas, ontology validation rules, or the memory graph (owned by `context`).
- Final output artifacts (owned by the `result/` registry).

By strictly confining `agentic` to execution and routing, we enforce the **Scheduler Pattern** (derived from `agency`'s `ralph-spec.md` R.2.1), ensuring the main conversational context remains uncluttered and token-efficient.

## 2. Canonical Cell Shape (`agentic/<row>`)

To satisfy **Column Isomorphism**, every cell in the agentic column (e.g., `agentic/music`, `agentic/novel`) adheres to a strict, minimal token-economy layout:

```text
agentic/<row>/
├── manifest.toml         # Boot registry. Exports skills and tool groups.
├── handlers/             # Python logic yielding FastMCP ToolResults.
│   ├── __init__.py
│   ├── execution.py      # Core domain tools
│   └── routing.py        # Cross-row / dispatch capabilities
└── skills/               # Declarative command entry points
    └── <slug>/
        ├── SKILL.md      # Slim frontmatter + trigger body
        └── references/   # T3 deep-dive references (load on demand)
```

**Manifest Optimization**: As mandated by `00.1-Overview.md`, the `manifest.toml` uses strict prefix-omission. It exports only the local `slug`, while the FastMCP harness programmatically derives the full namespace (`mcp__<row>_<slug>`) to preserve token budgets during tool discovery.

## 3. Integration & Conflict Resolution

The `agentic` column acts as the bridge between `workflow` and `context`. Through the Phase 3 design integration, key boundary conflicts were resolved to preserve `agentic`'s isomorphism:

### Resolving the Envelope Conflict
- **Demand**: `workflow` requested injecting `audit_trail` into the `ToolResult` envelope; `context` demanded strict JSONSchema compliance against its own definitions.
- **Resolution**: `agentic` strictly uses the native FastMCP `ToolResult` envelope (`ok`, `data`, `warnings`, `next_suggested_tools`). Schema validation from `context` and payload extensions from `workflow` occur *inside* the arbitrary `data` dict, shielding the core execution envelope from external drift.

### Resolving Graph Write Responsibilities
- **Demand**: Both `workflow` and `context` required `agentic` handlers to manually write graph edges (e.g., `write_edge` for `DispatchedTo`).
- **Resolution**: `agentic` handlers remain pure. Graph updates and schema validation are applied via decorator-driven middleware (the `PreToolUse` and `PostToolUse` hooks). The execution layer yields metadata; the interceptor maps it to the SQLite graph.

### Resolving Execution Boundaries
- **Demand**: `workflow` expected `agentic` to read and evaluate workflow gates.
- **Resolution**: `agentic` only invokes `workflow_mcp__start_phase(phase_id)`. The actual gating evaluation stays in the workflow-owned MCP handler.

## 4. Key Operational Patterns

Harvested from prior MVPs, `agentic` enforces the following patterns:
- **Codemode Opt-in**: Skills use `prefers_codemode: true` to trigger FastMCP code mode, keeping massive code reads out of the primary conversational loop.
- **Progressive Disclosure**: Skills use a T1 (Trigger) / T2 (Body) / T3 (References) ladder. Deep theoretical logic is exiled to `references/` and loaded only on demand.
- **Harness-in-Harness**: Cross-row dispatch is handled via the four-verb harness contract (`list_tools`, `call_tool`, `list_skills`, `dispatch_skill`).

## 5. Acceptance Contract: Gherkin Scenarios

The following 10 scenarios dictate the required behavioral tests for the `agentic` implementation:

```gherkin
Feature: Agentic Column Operations

  # anchor: agentic.session-routing
  Scenario: Session-start routing
    Given a fresh Claude Code session
    When the session loads the agency-system plugin
    Then a routing surface is available within the documented cold-load budget (< 500 tokens)
    And the routing surface explains the workflow rows currently registered

  # anchor: agentic.what-next
  Scenario: What-next query
    Given the user asks "what should I do next?"
    When the routing surface processes the intent
    Then candidates are returned ranked by graph adjacency, not substring match
    And the candidate maps to an `agentic/<row>/skills/<slug>`

  # anchor: agentic.new-row
  Scenario: New row plug-in
    Given a developer adds a new row "podcast"
    When they create the three cells from canonical templates
    Then no base file is modified
    And the central MCP glob-reads `agentic/podcast/manifest.toml` and picks up new tools on next boot

  # anchor: agentic.typed-envelope
  Scenario: Typed envelope
    Given a tool returns a result
    When the wire payload is inspected
    Then it strictly matches the FastMCP ToolResult schema
    And any domain-specific extensions are contained within the `data` key

  # anchor: agentic.codemode
  Scenario: Code-mode delegation
    Given a skill frontmatter declares `prefers_codemode: true`
    When the skill is dispatched
    Then the central MCP renders the skill's call surface in Code Mode
    And an envelope-archive interceptor limits payload to 4 KB

  # anchor: agentic.pre-write-gate
  Scenario: Frontmatter pre-write gate
    Given any cell writes a markdown file with frontmatter
    When the PreToolUse hook fires
    Then the frontmatter is schema-validated against the context column
    And an invalid frontmatter blocks the write

  # anchor: agentic.auto-ingest
  Scenario: Graph auto-ingest
    Given a new frontmatter-bearing file is written by an agentic handler
    When the PostToolUse hook fires
    Then the context graph store is updated with the new node and edges without manual `write_edge` calls in the handler

  # anchor: agentic.cross-dispatch
  Scenario: Harness-in-harness (cross-row dispatch)
    Given an agentic cell from row R1 dispatches into a workflow cell from row R2
    When the `dispatch_skill` tool is called
    Then the dispatching handler uses the standard four-verb contract
    And the payload specifically includes target row, phase, and context refs

  # anchor: agentic.cold-boot
  Scenario: Cold-boot budget
    Given a fresh session loads the plugin
    When token-usage is measured
    Then the cold-boot total is < 500 tokens
    And `defer_schema=True` is employed for non-anchor tools

  # anchor: agentic.isomorphism
  Scenario: Column isomorphism (agentic)
    Given any two rows R1 and R2
    When their agentic cells are inspected
    Then both cells expose exactly `manifest.toml`, `handlers/`, and `skills/`
    And tools are namespaced mathematically as `<row>_*`
```