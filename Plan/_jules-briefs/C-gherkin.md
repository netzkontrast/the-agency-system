# Session C — acceptance Gherkin + extended brief (rev 2: 3×N matrix)

Read this file as the long-form contract for the Session-C brief.
The short prompt in `Plan/_jules-briefs/dispatch.yaml` (entry
`review-C-from-scratch`) points here for the bulk.

## Quarantine — DO NOT READ these files

- `docs/superpowers/specs/2026-05-19-agency-base-design.md`  (PR design)
- `Plan/decisions/0001-…0008-*.md`                            (PR ADRs)
- `docs/superpowers/specs/_drafts/agency-*-prototype.md`     (PR prototypes)
- `docs/superpowers/specs/_drafts/2026-05-19-agency-base-canvas.md` (PR canvas)

If you accidentally open these, close them immediately. Your value to
the human is **independence**.

## The human's design law: a 3×N isomorphic matrix

The system is a strict **3-column × N-row matrix**:

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
│ (meta — the   │ workflow      │ workflow      │ workflow      │
│  workflow-of- │ (= workflow-  │ (= scaffold   │ (= templates  │
│  workflow)    │  author skill)│  pipeline)    │  for cells)   │
└───────────────┴───────────────┴───────────────┴───────────────┘
```

### Three load-bearing rules of the matrix

1. **Column isomorphism** — every cell in column X has the same shape.
   If you know one `agentic/*`, you know them all. Same for `workflow/*`
   and `context/*`. The shape is enforced by a canonical-cell schema.

2. **Row isomorphism** — every row's three cells use the same naming,
   the same ontology types, and the same handoff verbs. If you know
   the music row, the novel row's shape is predictable.

3. **Name-driven discovery** — knowing a row's name (e.g. "music")
   lets an agent discover all three of that row's cells through the
   graph alone (ontology edges, not substring search).

### The meta-row: `workflow/workflow`

`workflow` is itself a row. The cell `workflow/workflow` IS the
pipeline of bootstrapping a new row (music, novel, podcast, …). The
cell `agentic/workflow` IS the workflow-author skill that drives the
pipeline. The cell `context/workflow` IS the cell-shape templates the
author skill renders.

That self-reference is the recursion: any new workflow is created by
the workflow-of-creating-a-workflow, which produces a row that itself
contains a `workflow/<new>` cell — and that new cell is automatically
isomorphic to all the others because the meta cell rendered it.

### Where Jules lives

Jules was a top-level domain in earlier drafts. Under the matrix,
Jules is **a row, not a column** — Jules has its own three cells
(`agentic/jules`, `workflow/jules`, `context/jules`) just like music
and novel. The "harness-in-harness" recursion appears not as a fourth
domain but as a property of the agentic column: any row's agentic
cell may dispatch into other rows' cells, and that cross-row dispatch
is recorded as a graph edge.

## Acceptance contract — 18 Gherkin scenarios

Your design must pass all 18. Scenarios 13–18 enforce the matrix
invariants; scenarios 1–12 are the original feature scenarios.

```gherkin
Feature: Core agency-system base (3×N matrix)

  # === Original 12 ===

  Scenario: Session-start routing
    Given a fresh Claude Code session
    When the session loads the agency-system plugin
    Then a routing surface is available within the documented cold-load budget
    And the routing surface explains the workflow rows currently registered

  Scenario: What-next query
    Given the user asks "what should I do next?"
    When the routing surface processes the intent
    Then candidates are returned ranked by graph adjacency, not substring match

  Scenario: New domain plug-in
    Given a developer adds a new workflow row "podcast"
    When they create the three cells (agentic/podcast, workflow/podcast, context/podcast) from canonical templates
    Then no base file is modified
    And the central MCP picks up the new tools on next boot
    And the central routing skill picks up the new skills automatically

  Scenario: Typed envelope
    Given a tool returns a result
    When the wire payload is inspected
    Then it matches the ToolResult schema (ok, data, warnings, archived_to, next_suggested_tools, error)

  Scenario: Cross-domain reference via graph
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

  # === Matrix invariants (scenarios 13–18) ===

  Scenario: Column isomorphism (agentic)
    Given any two rows R1 and R2
    When their agentic cells are inspected
    Then both cells expose the same canonical files (manifest.toml, skills/, handlers/, README.md)
    And both cells satisfy the agentic-cell schema in `context/workflow/schemas/agentic-cell.schema.json`

  Scenario: Column isomorphism (workflow)
    Given any two rows R1 and R2
    When their workflow cells are inspected
    Then both cells expose the same canonical files (manifest.toml, phases/, gates/, README.md)
    And both cells satisfy the workflow-cell schema

  Scenario: Column isomorphism (context)
    Given any two rows R1 and R2
    When their context cells are inspected
    Then both cells expose the same canonical files (templates/, schemas/, references/, README.md)
    And both cells satisfy the context-cell schema

  Scenario: Name-driven discovery
    Given an agent knows only a row name "music"
    When it queries the graph for that name
    Then it can discover the row's three cells via ontology edges
    And no substring search is required

  Scenario: Workflow-of-creating-a-workflow (meta-row recursion)
    Given a developer invokes `agentic/workflow:scaffold` with row name "podcast"
    When the meta-workflow runs
    Then it creates `agentic/podcast`, `workflow/podcast`, and `context/podcast` from canonical templates
    And all three new cells pass column-isomorphism on the first commit

  Scenario: Workflow-owned MCP tools registered in Code Mode
    Given a workflow row defines MCP tools in its agentic cell
    When the central MCP boots
    Then those tools are registered under the namespace `<row>_*`
    And they are exposed in Code Mode by default

  Scenario: Workflow uses context templates only
    Given a workflow cell's pipeline produces an artefact
    When the artefact is rendered
    Then it is rendered from a template in either `context/<row>/templates/` or `context/_shared/templates/`
    And no template lives outside the context column
```

## Output requirements

Write 5 files under `Plan/_reviews/session-C-from-scratch/` ONLY:

1. `CORE.md` (≤300 lines) — the 3×N matrix as the spine. Four-verb
   contract, central routing skill, codemode MCP, ToolResult envelope,
   graph, manifest. ASCII diagram of the matrix + interfaces between
   columns. Address column-isomorphism, row-isomorphism, name-discovery.

2. `DOMAIN-EXAMPLES.md` (≤200 lines) — sketch THREE rows under the
   matrix: `music`, `novel`, and `workflow` (the meta-row). For each,
   show all three cells' file shape and how they interlink.

3. `GRAPH.md` (≤200 lines) — the ontology that makes name-driven
   discovery work. Node types per cell. Edge types between cells.
   One Cypher example for each:
     (a) "discover all cells of row X from its name"
     (b) "find skills adjacent to a context template"
     (c) "find all cross-row dispatch edges from row R"
   One Graphviz/ASCII visualization of the matrix with edges. Explicit
   harness-in-harness via cross-row dispatch edges.

4. `GHERKIN.md` (≤250 lines) — the 18 scenarios above, refined with
   concrete expected outputs (exact file paths, exact envelope values,
   exact graph edge types).

5. `DIVERGENCE.md` (≤100 lines) — for every term you used that differs
   from `Plan/harness/VOCABULARY.md`, note: old term → new term +
   one-sentence rationale. Includes structural divergences.

## Source repos to clone (read-only, `~/work/vendor/`)

```bash
git clone --depth=1 --branch=claude/agency-plugin-refactor-PgMQ4 \
  https://github.com/netzkontrast/agency.git ~/work/vendor/agency
git clone --depth=1 https://github.com/jlowin/fastmcp.git ~/work/vendor/fastmcp
git clone --depth=1 --branch=v0.91.0 \
  https://github.com/bitwize-music-studio/claude-ai-music-skills.git \
  ~/work/vendor/bitwize-music
```

The `agency` repo is the human's stated inspiration — use it to ground
the row/cell vocabulary if it has prior art on `workflow` (singular).

## Discipline (`Plan/JULES_PROTOCOL.md` applies)

- Gate-1 confidence ≥ 0.90; cite VOCABULARY § numbers or source-repo file:line.
- `## Evidence` + `## Self-Review` in the PR body.
- `affects:` allow-list = `Plan/_reviews/session-C-from-scratch/*` only.

Publish your work via the standard flow.
