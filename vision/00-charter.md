---
slug: vision-charter
type: vision-charter
status: ready
owner: claude
created: 2026-05-19
updated: 2026-05-19
summary: Shared inheritance for the three column-owning Jules agents — matrix law, three isomorphism rules, meta-row, 18 Gherkin scenarios, source-repo conventions.
---

# Charter — the 3×N matrix and its three rules
> **Successor: see `vision/00.1-Overview.md`**

Every Jules agent dispatched from `vision/` MUST read this charter
before doing any column-specific work. The charter is the floor; each
column brief refines.

## The matrix

```
                ┌───────────────┬───────────────┬───────────────┐
                │   agentic     │   workflow    │   context     │
                │ (skills + MCP │ (pipelines +  │ (graph +      │
                │  + harness-in-│  handoffs +   │  frontmatter +│
                │  harness)     │  gates)       │  templates +  │
                │               │               │  schemas +    │
                │               │               │  search +     │
                │               │               │  pandoc)      │
┌───────────────┼───────────────┼───────────────┼───────────────┤
│ music         │ agentic/music │ workflow/music│ context/music │
├───────────────┼───────────────┼───────────────┼───────────────┤
│ novel         │ agentic/novel │ workflow/novel│ context/novel │
├───────────────┼───────────────┼───────────────┼───────────────┤
│ jules         │ agentic/jules │ workflow/jules│ context/jules │
├───────────────┼───────────────┼───────────────┼───────────────┤
│ workflow      │ agentic/      │ workflow/     │ context/      │
│ (meta-row)    │ workflow      │ workflow      │ workflow      │
│               │ (workflow-    │ (scaffold     │ (cell-shape   │
│               │  author skill)│  pipeline)    │  templates)   │
└───────────────┴───────────────┴───────────────┴───────────────┘
```

## The three rules

1. **Column isomorphism.** Every cell in column X has the same canonical
   shape. If you know one `agentic/*`, you know them all. Same for
   `workflow/*` and `context/*`. The shape is enforced by a canonical
   cell schema living in the context column.

2. **Row isomorphism.** Every row's three cells share naming, ontology
   types, and handoff verbs. If you know the music row, the novel row's
   shape is predictable from the music row alone.

3. **Name-driven discovery.** Knowing a row's name (e.g. `music`) lets
   an agent discover all three of that row's cells through the graph
   alone — via ontology edges, never substring search.

These three rules guarantee that **any agent can safely guess** how
any part of the system works. Knowing one cell teaches you all cells
in its column and all cells in its row.

## The meta-row: `workflow/workflow`

`workflow` is itself a row. Its three cells are:

- `agentic/workflow` — the **workflow-author skill**, which scaffolds
  new rows.
- `workflow/workflow` — the **scaffold pipeline**, which is the
  workflow-of-creating-a-workflow.
- `context/workflow` — the **cell-shape templates** that the author
  skill renders.

A new row (e.g. `podcast`) is produced by invoking `workflow/workflow`
via `agentic/workflow`, which renders three new cells from templates
in `context/workflow`. Every new row is automatically isomorphic to
all the others because the meta-row's templates enforce the shape.

## Where Jules lives

Jules WAS a top-level domain. Under the matrix, Jules is **a row, not
a column** — `agentic/jules`, `workflow/jules`, `context/jules`. The
"harness-in-harness" recursion (one agent orchestrating others) is a
**property of the agentic column**, not its own domain: any row's
agentic cell may dispatch into other rows' cells, and that cross-row
dispatch is recorded as a graph edge.

## Existing material to read (canon + inputs)

- `Plan/harness/VOCABULARY.md` — the canonical glossary. Reuse terms
  where they fit; flag divergences in your `DIVERGENCE.md`.
- `CLAUDE.md` — project rules.
- `Plan/JULES_PROTOCOL.md` — discipline contract.
- `jules-plugin/skills/jules/SKILL.md` — the only existing skill;
  reference for cell shape under the agentic column.
- The two existing plugins in source (bitwize-music, jules-plugin) —
  use them as **MVP examples** of what music and jules rows currently
  do, NOT as the canonical shape. The MVPs need to be redesigned to fit
  the matrix.

## Quarantined material (DO NOT READ)

The current PR #133 (`claude/agency-system-refactor-wSuD3`) carries a
prior design that uses the 5+1 model. Your value to the human is
independence from that PR.

- `docs/superpowers/specs/2026-05-19-agency-base-design.md`
- `Plan/decisions/0001-…0008-*.md`
- `docs/superpowers/specs/_drafts/agency-*-prototype.md`
- `docs/superpowers/specs/_drafts/2026-05-19-agency-base-canvas.md`
- `Plan/_reviews/`  (prior review sessions A/B)
- `Plan/_jules-briefs/`  (prior dispatch)

If you accidentally open these, close them immediately.

## Acceptance contract — 18 Gherkin scenarios (every column-brief inherits these)

Scenarios 1–12 are feature scenarios. Scenarios 13–18 enforce the
matrix invariants directly. Each column's brief declares which
scenarios it owns and which it shares.

```gherkin
Feature: Core agency-system base (3×N matrix)

  # === Feature scenarios (1–12) ===

  Scenario: Session-start routing
    Given a fresh Claude Code session
    When the session loads the agency-system plugin
    Then a routing surface is available within the documented cold-load budget
    And the routing surface explains the workflow rows currently registered

  Scenario: What-next query
    Given the user asks "what should I do next?"
    When the routing surface processes the intent
    Then candidates are returned ranked by graph adjacency, not substring match

  Scenario: New row plug-in
    Given a developer adds a new row "podcast"
    When they create the three cells from canonical templates
    Then no base file is modified
    And the central MCP picks up the new tools on next boot
    And the central routing skill picks up the new skills automatically

  Scenario: Typed envelope
    Given a tool returns a result
    When the wire payload is inspected
    Then it matches the ToolResult schema (ok, data, warnings, archived_to, next_suggested_tools, error)

  Scenario: Cross-column reference via graph
    Given a workflow cell cites a context cell in its frontmatter
    When the graph is queried for cells adjacent to that context node
    Then the workflow cell appears in the result

  Scenario: Code-mode delegation
    Given a skill frontmatter declares code-mode preference
    When the skill is dispatched
    Then the central MCP renders the skill's call surface in Code Mode
    And an envelope-archive interceptor applies inside the sandbox

  Scenario: Frontmatter pre-write gate
    Given any cell writes a markdown file with frontmatter
    When the PreToolUse hook fires
    Then the frontmatter is schema-validated against the appropriate kind
    And invalid frontmatter blocks the write

  Scenario: Graph auto-ingest
    Given a new frontmatter-bearing file lands in any cell
    When the PostToolUse hook fires
    Then the graph store is updated with the new node and edges
    And no manual rebuild is required

  Scenario: Lesson-learned link-back
    Given a skill execution produces a lesson
    When the lesson is written
    Then its frontmatter cites the originating spec
    And the graph records a lesson→spec edge

  Scenario: Harness-in-harness (cross-row dispatch)
    Given an agentic cell from row R1 dispatches into a workflow cell from row R2
    When the dispatch occurs
    Then the dispatching handler uses the SAME four-verb contract as a leaf cell
    And the graph records the cross-row dispatch edge with both row identities

  Scenario: Cold-boot budget
    Given a fresh session loads the plugin
    When token-usage is measured by a documented method
    Then the cold-boot total is below a documented numeric budget
    And the budget is enforced by a CI check

  Scenario: Pandoc render (context column)
    Given a context cell node with frontmatter and body
    When the user invokes `pandoc render <node>`
    Then the node is rendered to all output formats declared in its frontmatter
    And the output paths are recorded in the graph

  # === Matrix invariants (13–18) ===

  Scenario: Column isomorphism (agentic)
    Given any two rows R1 and R2
    When their agentic cells are inspected
    Then both cells expose the same canonical files
    And both cells satisfy the agentic-cell schema

  Scenario: Column isomorphism (workflow)
    Given any two rows R1 and R2
    When their workflow cells are inspected
    Then both cells expose the same canonical files
    And both cells satisfy the workflow-cell schema

  Scenario: Column isomorphism (context)
    Given any two rows R1 and R2
    When their context cells are inspected
    Then both cells expose the same canonical files
    And both cells satisfy the context-cell schema

  Scenario: Name-driven discovery
    Given an agent knows only a row name "music"
    When it queries the graph for that name
    Then it can discover the row's three cells via ontology edges
    And no substring search is required

  Scenario: Workflow-of-creating-a-workflow (meta-row recursion)
    Given a developer invokes the meta-row with row name "podcast"
    When the meta-workflow runs
    Then it creates `agentic/podcast`, `workflow/podcast`, `context/podcast` from canonical templates
    And all three new cells pass column-isomorphism on the first commit

  Scenario: Workflow-owned MCP tools registered in Code Mode
    Given a workflow row defines MCP tools in its agentic cell
    When the central MCP boots
    Then those tools are registered under the namespace `<row>_*`
    And they are exposed in Code Mode by default
```

## Source repos to clone (read-only, `~/work/vendor/`)

```bash
git clone --depth=1 --branch=claude/agency-plugin-refactor-PgMQ4 \
  https://github.com/netzkontrast/agency.git ~/work/vendor/agency

git clone --depth=1 https://github.com/jlowin/fastmcp.git ~/work/vendor/fastmcp

git clone --depth=1 --branch=v0.91.0 \
  https://github.com/bitwize-music-studio/claude-ai-music-skills.git \
  ~/work/vendor/bitwize-music
```

The `agency` repo is the human's stated inspiration. Mine it for prior
art on the `workflow` (singular) vocabulary, on column-isomorphic
cell shapes, and on graph-driven discovery. Reject what feels
overkill; steal what looks isomorphic.

## Trio-interface guarantee

Each agent writes one `INTERFACES.md` declaring:

1. The contracts THIS column exposes to the other two (function
   signatures, schema names, file paths, wire shapes).
2. The contracts THIS column REQUIRES from the other two.

The merge check (run by Claude) is that contract X from column A
matches contract Y from column B when they describe the same crossing.
Mismatches surface as merge-conflict findings the human resolves.

## Discipline (`Plan/JULES_PROTOCOL.md`)

- Gate-1 confidence ≥ 0.90; cite VOCABULARY § or source-repo file:line.
- `## Evidence` + `## Self-Review` in your PR body.
- `affects:` allow-list = `vision/<your-column>/*` ONLY.
- Publish your work via the standard flow.
