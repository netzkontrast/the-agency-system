---
slug: vision-brief-workflow
type: jules-brief
status: ready
owner: claude
created: 2026-05-19
column: workflow
summary: Brief for the Jules agent that owns the workflow column — the WHAT of the system (pipelines, phases, handoffs, gates). Includes the meta-row workflow/workflow.
---

# Brief — workflow column owner

You own the **workflow** column of the 3×N matrix. Your job is to
specify the canonical cell-shape of `workflow/<row>` such that every
row's workflow cell is structurally identical, plus design the
meta-row `workflow/workflow` (the workflow-of-creating-a-workflow).

> **READ FIRST**: [`vision/00-charter.md`](../00-charter.md). That
> file is the floor — matrix law, three rules, meta-row, 18 Gherkin
> scenarios, source repos, discipline. This brief refines.

## What "workflow" owns

Per the human's framing: *"Workflow is music and novel"* (and jules,
podcast, …). Concretely:

- **Pipelines** — the ordered phases of a row (e.g. music:
  ideate → lyric → suno → mix → master → release; novel: outline →
  chapter → scene → revision → publish).
- **Phase definitions** — what each phase consumes, produces, and
  hands off.
- **Gates** — hard-blocking checks between phases (e.g. "lyric
  reviewed before suno generation"; "all chapters present before
  publish").
- **Handoff envelopes** — the typed payload shape that crosses a phase
  boundary.
- **The meta-row `workflow/workflow`** — the pipeline that scaffolds a
  new row. This is the most important part of your brief: it's how
  the system grows.

## What you DO NOT own

- Skills, MCP tools, handlers, central router → agentic column.
- Templates, schemas, graph, frontmatter, pandoc → context column.
- The MCP tools that DRIVE workflows (those live in agentic cells);
  you only declare what entry-points workflows expose.

## The meta-row is the heart of this brief

`workflow/workflow` is structurally identical to `workflow/music` and
`workflow/novel`, but its job is to **produce new rows**. Its phases
are something like:

```
phase 1: name + intent
phase 2: render templates (consume from context/workflow/templates/)
phase 3: scaffold the three cells (write agentic/<new>, workflow/<new>,
         context/<new>)
phase 4: validate column-isomorphism on all three cells
phase 5: register the row in the central manifest + graph
```

Specify these phases concretely. The meta-row is what makes the matrix
self-extending — without it, every new row is hand-crafted.

## Output (write these 4 files ONLY)

All under `vision/workflow/`. Affects allow-list = `vision/workflow/*`.

### 1. `COLUMN.md` (≤300 lines)

The canonical cell-shape for `workflow/<row>`. Sections:

- **Cell layout** — exact file tree of `workflow/<row>/` (phases/,
  gates/, handoffs/, manifest.toml, README.md).
- **Manifest schema** — what `workflow/<row>/manifest.toml` declares
  (phase list, gate list, entry-verbs, ontology types of artefacts
  produced).
- **Phase shape** — frontmatter, declared inputs/outputs, link to the
  agentic skill(s) that drive the phase.
- **Gate shape** — the conditions, the failure mode, the recovery
  path. Distinguish hard-blocking gates from advisory ones.
- **Handoff envelope** — the typed payload shape between phases.
  Match this to the central ToolResult envelope so cross-phase wire
  is isomorphic to cross-tool wire.
- **Dispatch contract** — how the agentic column invokes a phase
  (verb name, arguments, return shape).

### 2. `META-WORKFLOW.md` (≤250 lines)

The full spec for `workflow/workflow`. Sections:

- The phases of the meta-row (rendering, scaffolding, validation,
  registration).
- The templates the meta-row reads from `context/workflow/templates/`
  (specify which templates exist by name + purpose; the context
  agent will define their contents).
- The invariants the meta-row enforces on a newly-created row.
- A worked example: scaffolding `podcast` from scratch. Show the
  three new cells that the meta-row produces, with their file trees.
- How the meta-row interacts with itself: scaffolding
  `workflow/workflow` is impossible (chicken-and-egg). Specify a
  bootstrap path that humans use ONCE.

### 3. `ROW-EXAMPLES.md` (≤200 lines)

Fill in `workflow/<row>` for three rows:

- `workflow/music` — redesign the existing bitwize-music pipeline as
  matrix-shaped phases + gates. The current MVP has the chain
  `lyric-writer → suno-engineer → mastering → release-director`;
  reify that as phases with explicit handoff envelopes.
- `workflow/novel` — design from scratch. Phases for outline →
  chapter → scene → revision → publish (or your better cut).
- `workflow/jules` — the existing jules-plugin has very little
  workflow shape (one big SKILL); design what the cell SHOULD be:
  phases for `confidence-check → tdd → verification → self-review →
  submit`, gates on the four-gate JULES_PROTOCOL discipline.

For each row, show: manifest, phase list (1–2 example phases with
frontmatter), gates, entry-verbs.

### 4. `INTERFACES.md` (≤200 lines)

Two halves:

**(a) Contracts workflow EXPOSES** to agentic and context. Examples:

- Each `workflow/<row>` exposes a `phases` listing (so agentic can
  dispatch into them).
- Each phase exposes a `prerequisites` list (so agentic's router
  can answer "what next?").
- Each phase declares its `artefacts_written` and their ontology
  types (so context's graph can ingest correctly).
- Meta-row exposes a `scaffold(row_name)` entry-point.

**(b) Contracts workflow REQUIRES** from agentic and context.
Examples:

- Requires from `agentic`: the central MCP server, four-verb
  call surface, `dispatch_skill` for invoking the skill that drives
  a phase.
- Requires from `context`: the artefact templates (per phase),
  the handoff-envelope schema, the gate-result schema, the
  cell-shape templates for the meta-row, the ontology type names.

Each contract: name + one-line description + concrete shape.

### 5. `GHERKIN-OWNED.md` (≤150 lines)

The Gherkin scenarios the workflow column owns or co-owns. From the
charter's 18:

- Own: #3 (new-row plug-in — workflow's meta-row drives this), #9
  (lesson-learned link-back — lessons are workflow artefacts), #14
  (column isomorphism — workflow), #17 (workflow-of-creating-a-workflow),
  #18 (workflow-owned MCP tools in code-mode — workflow declares
  which tools, agentic registers them).
- Co-own: #10 (harness-in-harness — workflows are what gets
  recursed into), #11 (cold-boot — workflow manifests load on boot).

For each owned scenario, refine `When` and `Then` with concrete
expected outputs.

## Source repos to study (read-only, `~/work/vendor/`)

Per the charter. Pay special attention to:

- `~/work/vendor/agency/` — the human cited `workflow` (singular) and
  pointed at this repo. Search for `workflow/`, `phase`, `pipeline`,
  `gate` directories. Mine prior art on what a workflow cell looks
  like.
- `~/work/vendor/bitwize-music/skills/` — the chain
  `lyric-writer → ... → release-director` is already implied in the
  skill `prerequisites:` frontmatter. Reify that as explicit phases.
- The current `CLAUDE.md` § "RECOMMENDED: Follow the canonical
  workflow chains" — the chains in there are prose; convert them to
  structured phases.

## Discipline

Per the charter + `Plan/JULES_PROTOCOL.md`. Gate-1 ≥ 0.90.
`affects:` allow-list = `vision/workflow/*` only.

Publish your work via the standard flow.
