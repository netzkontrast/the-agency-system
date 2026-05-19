---
slug: vision-brief-context
type: jules-brief
status: ready
owner: claude
created: 2026-05-19
column: context
summary: Brief for the Jules agent that owns the context column — the substrate (graph, frontmatter, search, pandoc, templates, schemas). This column makes name-driven discovery work.
---

# Brief — context column owner

You own the **context** column of the 3×N matrix. Your job is to
specify the canonical cell-shape of `context/<row>` such that every
row's context cell is structurally identical, AND to define the
substrate (graph, ontology, schemas, templates, search, pandoc) that
makes the matrix's three rules — column isomorphism, row isomorphism,
name-driven discovery — actually work.

> **READ FIRST**: [`vision/00-charter.md`](../00-charter.md). That
> file is the floor — matrix law, three rules, meta-row, 18 Gherkin
> scenarios, source repos, discipline. This brief refines.

## What "context" owns

Per the human's framing: *"context is all stuff generating and
relating files to each other — it is Graph, it is frontmatter, it is
Search, it is pandoc, it is templates, it is Schemata"*.

Concretely, the context column owns:

- **The ontology** — node types, edge types, what kinds of artefacts
  exist and how they relate.
- **The graph store** — the backing data structure (file-based?
  SQLite? GraphQLite Cypher? in-memory?) that holds nodes + edges,
  and the ingest/query path.
- **Frontmatter canon** — every kind of markdown artefact's
  frontmatter schema (skill, handler, lesson, ADR, spec, template,
  phase, gate, …). Schema files in JSON Schema or equivalent.
- **Schemas** — for tool inputs/outputs (the ToolResult envelope),
  manifest files, handoff envelopes, gate results.
- **Templates** — pandoc/jinja/handlebars templates that produce
  artefacts. Includes the **cell-shape templates** that the meta-row
  `workflow/workflow` uses to scaffold new rows.
- **Search** — the anchor-triad pattern (search/describe/invoke) or
  whatever surface lets an agent find an artefact by name, by
  ontology type, by relation.
- **Pandoc rendering** — how context nodes get rendered to output
  formats (md/html/pdf/epub).

## What you DO NOT own

- Skills, handlers, MCP tools → agentic.
- Pipelines, phases, gates → workflow.
- The artefacts THEMSELVES — you define the SHAPE of an artefact;
  the artefacts live in agentic and workflow cells (and citable from
  context/_shared/).

## The context column makes the matrix-rules ACTUALLY WORK

Without context, the three rules of the matrix are aspirational. With
context:

- **Column isomorphism** is enforced by schemas. Every agentic cell
  validates against `agentic-cell.schema.json`. You define these
  schemas.
- **Row isomorphism** is enforced by templates. Every new row is
  scaffolded from `context/workflow/templates/`. You define these
  templates.
- **Name-driven discovery** is enforced by the ontology + graph.
  Knowing a row name lets an agent issue a Cypher (or equivalent)
  query to find all three cells via ontology edges. You define the
  ontology + the query surface.

If your design ducks any of these three, the matrix collapses.

## Output (write these 5 files ONLY)

All under `vision/context/`. Affects allow-list = `vision/context/*`.

### 1. `COLUMN.md` (≤300 lines)

The canonical cell-shape for `context/<row>`. Sections:

- **Cell layout** — exact file tree of `context/<row>/` (templates/,
  schemas/, references/, manifest.toml, README.md). Plus
  `context/_shared/` for cross-row artefacts.
- **Manifest schema** — what `context/<row>/manifest.toml` declares
  (template list, schema list, ontology types this row contributes,
  search-anchor entries).
- **Template shape** — frontmatter (rendering format, output paths,
  variable expectations), body conventions.
- **Schema shape** — JSON Schema 2020-12; where partials go; how
  schemas reference each other.
- **Reference-folder convention** — the slim-SKILL `/references/`
  pattern lives here; specify the linking convention.
- **Pandoc-render contract** — how a context node declares its
  output formats and how `pandoc render <node>` resolves them.

### 2. `ONTOLOGY.md` (≤300 lines)

The full ontology. Sections:

- **Node types** — every kind of node in the graph. At minimum:
  Plugin, Row, Cell, Skill, Handler, Tool, Spec, ADR, Lesson,
  Phase, Gate, Template, Schema, Artefact, Session, Reference.
  Specify each with its required + optional properties.
- **Edge types** — how nodes relate. At minimum:
  CONTAINS (Plugin→Row, Row→Cell, Cell→Artefact),
  ADJACENT_TO (cross-cell semantic links from frontmatter `related:`),
  PREREQUISITE_OF (phase→phase), SUPERSEDES (artefact→artefact),
  USES_SCHEMA (Artefact→Schema), USES_TEMPLATE (Artefact→Template),
  DISPATCHES (Skill→Phase), REVIEWED_BY (Spec→Review),
  PRODUCED_LESSON (Session→Lesson).
- **Backing store** — pick one with justification: SQLite with a
  Cypher extension (GraphQLite, AGE, …), in-memory NetworkX,
  file-only (frontmatter scanned per query), or hybrid. Defend your
  choice on terms of write latency, query latency, cold-start cost,
  dependency footprint.
- **Ingest path** — the PostToolUse hook that walks frontmatter on
  every Write and UPSERTs to the graph.
- **Query path** — how `agentic`'s anchor-triad and `/agency` router
  issue queries. Cypher example for each of the three matrix rules.

### 3. `ROW-EXAMPLES.md` (≤200 lines)

Fill in `context/<row>` for three rows:

- `context/music` — collapse the existing bitwize-music plugin's
  references (genres/, overrides/, reference/suno/) into the new
  shape. Templates for lyric files, style boxes, mastering presets.
  Schemas for tracks, albums, ideas.
- `context/novel` — design from scratch. Templates for outline,
  chapter, scene. Schemas for plot beats, characters, world.
- `context/jules` — minimal cell: schemas for confidence-gate
  evidence, friction-log entries, session-state recovery.

For each, show the manifest, 1–2 example templates (with frontmatter,
no actual rendering payload), 1–2 example schemas (names + purpose).

### 4. `INTERFACES.md` (≤200 lines)

Two halves:

**(a) Contracts context EXPOSES** to agentic and workflow. Examples:

- The `agentic-cell.schema.json`, `workflow-cell.schema.json`,
  `context-cell.schema.json` definitions (the column-isomorphism
  enforcers).
- The frontmatter schemas (per kind).
- The ToolResult envelope schema.
- The graph query API (Cypher-equivalent endpoint).
- The `load_template(name, variables) -> rendered` function.
- The `pandoc_render(node) -> output_paths` function.
- The anchor-triad search surface (or equivalent).

**(b) Contracts context REQUIRES** from agentic and workflow.
Examples:

- Requires `agentic` to call the PreToolUse hook before every write
  of frontmatter-bearing files.
- Requires `agentic` to register the PostToolUse graph-ingest hook.
- Requires `workflow` to declare each phase's `artefacts_written`
  list with ontology types (so the graph knows what's coming).
- Requires `workflow` to use only templates that live in
  `context/<row>/templates/` or `context/_shared/templates/` (no
  in-cell templates).

Each contract: name + one-line description + concrete shape.

### 5. `GHERKIN-OWNED.md` (≤150 lines)

The Gherkin scenarios the context column owns or co-owns. From the
charter's 18:

- Own: #4 (typed envelope — defined here), #5 (cross-column
  reference via graph), #7 (frontmatter pre-write gate), #8 (graph
  auto-ingest), #12 (pandoc render), #15 (column isomorphism —
  context), #16 (name-driven discovery — the substrate).
- Co-own: all column-isomorphism scenarios (you define the schemas
  that enforce them), #9 (lessons cite via graph), #17 (meta-row
  scaffolds via your templates).

For each owned scenario, refine `When` and `Then` with concrete
expected outputs.

## Source repos to study (read-only, `~/work/vendor/`)

Per the charter. Pay special attention to:

- `~/work/vendor/agency/` — search for `context/`, `ontology/`,
  `schemas/`, `templates/`. The human cited this repo as
  inspiration. Mine the prior ontology if it exists.
- `~/work/vendor/bitwize-music/reference/` — `SKILL_INDEX.md`,
  `terminology.md`, the suno/ subtree. Examples of the
  reference/template/schema patterns the matrix will generalise.
- `Plan/harness/VOCABULARY.md` — the existing canonical glossary.
  Your `INTERFACES.md` may amend it; flag every amendment in your
  `DIVERGENCE.md` (within `vision/context/`).

## Discipline

Per the charter + `Plan/JULES_PROTOCOL.md`. Gate-1 ≥ 0.90.
`affects:` allow-list = `vision/context/*` only.

Publish your work via the standard flow.
