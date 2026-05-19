---
slug: vision-brief-agentic
type: jules-brief
status: ready
owner: claude
created: 2026-05-19
column: agentic
summary: Brief for the Jules agent that owns the agentic column — the WHO of the system (skills, MCP tools, handlers, harness-in-harness recursion).
---

# Brief — agentic column owner

You own the **agentic** column of the 3×N matrix. Your job is to
specify the canonical cell-shape of `agentic/<row>` such that every
row's agentic cell is structurally identical and any agent can guess
how one works from any other.

> **READ FIRST**: [`vision/00-charter.md`](../00-charter.md). That
> file is the floor — matrix law, three rules, meta-row, 18 Gherkin
> scenarios, source repos, discipline. This brief refines.

## What "agentic" owns

Per the human's framing: *"agentic (is also Jules… And all stuff MCP
and skills and Harness in Harness)"*.

Concretely, the agentic column owns:

- **Skills** — markdown files invoked via slash commands; the
  intent→action surface.
- **MCP tools** — every Python handler registered against the central
  FastMCP server. Tools are namespaced `<row>_<verb>` (e.g.
  `music_polish_audio`, `novel_chapter_draft`, `jules_create`).
- **Handlers** — the Python modules that back the MCP tools.
- **Central routing skill** (`/agency`) — the row-agnostic surveyor
  that helps an agent discover which row + cell to enter.
- **Harness-in-harness** — recursion: an agentic cell from row R1 may
  dispatch into a workflow cell from row R2. This is a property of
  the column, not a separate domain. Cross-row dispatch is recorded
  as a graph edge.
- **Codemode wiring** — the central MCP runs with FastMCP CodeMode
  available; skills declare `prefers_codemode: true` to opt in.

## What you DO NOT own

- Pipelines, phases, gates → workflow column.
- Templates, schemas, search, pandoc, graph → context column.
- Frontmatter canon (you USE it; you don't define it) → context.

If your design needs to define something that lives in another column,
add it to your `INTERFACES.md` as a contract you REQUIRE from that
column — do not specify the other column's internals.

## Output (write these 4 files ONLY)

All under `vision/agentic/`. Affects allow-list = `vision/agentic/*`.

### 1. `COLUMN.md` (≤300 lines)

The canonical cell-shape for `agentic/<row>`. Sections:

- **Cell layout** — exact file tree of `agentic/<row>/` (directories,
  required files, optional files, naming rules).
- **Manifest schema** — what `agentic/<row>/manifest.toml` declares
  (skill list, tool list, namespace prefix, dependencies on other
  rows' cells).
- **Skill shape** — frontmatter fields, body length budget,
  reference-folder convention. Reference the existing
  `jules-plugin/skills/jules/SKILL.md` shape and propose a refinement.
- **Handler shape** — Python module conventions (where the
  `@mcp.tool` decorators live; how `register_<row>_<group>(mcp)` is
  exposed for the central MCP boot loop).
- **The central routing skill** — does `/agency` live in
  `agentic/_router/` (a meta-cell) or in `agentic/workflow/`
  (folded into the meta-row)? Choose one with justification.
- **Codemode opt-in** — exact frontmatter contract.
- **Harness-in-harness** — how an agentic cell dispatches into another
  row's workflow cell (which verb? which envelope? which graph edge?).

### 2. `ROW-EXAMPLES.md` (≤200 lines)

Fill in `agentic/<row>` for three rows:

- `agentic/music` — collapse the existing bitwize-music plugin's
  ~54 skills + ~90 MCP tools into the new shape. Cite the source
  plugin's current state as MVP-to-be-redesigned (it currently has
  bloat: 200–515-line skill bodies, 9 near-isomorphic researcher
  skills, 18-tool `core.py`). Show what the cell looks like after
  the redesign.
- `agentic/novel` — design from scratch (no MVP yet). Skills + tools
  for a chapter/scene pipeline.
- `agentic/jules` — collapse the existing `jules-plugin` into the new
  shape. Cite its current 16-tool surface + 85-line SKILL.md + 9
  references as MVP-to-be-redesigned. The existing slim-SKILL pattern
  is the right floor; the matrix shape extends it.

For each row, show: the manifest, the skill list (1–2 example
skills with frontmatter), the handler list (no implementation, just
signatures).

### 3. `INTERFACES.md` (≤200 lines)

Two halves:

**(a) Contracts agentic EXPOSES** — what the other two columns can
rely on this column to provide. Examples:

- `agentic` exposes a slash command `/agency` for routing.
- `agentic` exposes the central MCP server (FastMCP instance) and
  registers all row tools under the boot loop.
- `agentic` exposes a four-verb call surface for cross-row dispatch
  (verb names + envelope shape + graph-edge writes).
- `agentic` exposes `skill_kind` enum values from VOCABULARY §4.2.

**(b) Contracts agentic REQUIRES** from the other columns. Examples:

- Requires from `context`: frontmatter schemas for `Skill`, `Handler`,
  `Lesson`; the ontology types for `Skill`-edges; the
  `agentic-cell.schema.json` definition.
- Requires from `workflow`: a `dispatch(row, phase)` entry-point on
  every workflow cell; the phase-handoff envelope; the gate-result
  envelope.

Each contract: name + one-line description + concrete shape (TOML,
JSON, function signature). The other agents read this file when
they're writing their interfaces; mismatches become merge findings.

### 4. `GHERKIN-OWNED.md` (≤150 lines)

The Gherkin scenarios the agentic column owns or co-owns. From the
charter's 18:

- Own: #1 (session-start routing), #2 (what-next), #6 (code-mode
  delegation), #10 (harness-in-harness), #13 (column isomorphism —
  agentic), #17 (workflow-owned MCP tools).
- Co-own: #3 (new-row plug-in — agentic must pick up the new tools
  automatically), #11 (cold-boot budget — most cold-load weight is
  in the agentic surface).

For each owned scenario, refine the `When` and `Then` with concrete
expected outputs (file paths, envelope values, edge types).

## Source repos to study (read-only, `~/work/vendor/`)

Per the charter. Pay special attention to:

- `~/work/vendor/agency/` — search for `agentic/`, `workflow/`,
  `harness/` directories. The human cited this repo as the
  *inspiration* and pointed at `workflow` (singular) — look for
  whatever names the agentic-column equivalent uses.
- `~/work/vendor/fastmcp/` — `src/fastmcp/experimental/transforms/
  code_mode.py` and any tool-registration helpers.
- `~/work/vendor/bitwize-music/` — `.claude-plugin/`,
  `servers/bitwize-music-server/server.py`, the handler tree, the
  skill tree. Identify what's reusable shape vs. what's
  domain-shaped bloat.
- `jules-plugin/skills/jules/SKILL.md` (in this repo) — the only
  existing slim SKILL.md. Honest reference for the agentic cell.

## Discipline

Per the charter's discipline section + `Plan/JULES_PROTOCOL.md`. Gate-1
confidence ≥ 0.90. `## Evidence` and `## Self-Review` in the PR body.
`affects:` allow-list is `vision/agentic/*` only.

Publish your work via the standard flow.
