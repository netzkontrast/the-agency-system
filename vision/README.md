---
slug: vision-readme
type: vision-charter
status: ready
owner: claude
created: 2026-05-19
updated: 2026-05-19
summary: Navigation map of `vision/`. Base layer SHIPPED — `agentic/`, `workflow/`, `context/` live at repo root. Current canon at `00.1-Overview.md` + `03-architecture.md`; next-step plan at `04-nextsteps.md`. Phase 1-3 column drafts kept as historical archive.
---

# `/vision` — design canon for the agency-system

The agency-system is a **3-column × N-row matrix**: columns are fixed (`agentic`, `workflow`, `context`); rows are domains (jules, music, novel, podcast, …). The vision folder holds the design that drives implementation. **Implementation code lives at the REPO ROOT** in `agentic/`, `workflow/`, `context/` — not under `vision/`.

## Status snapshot

- ✅ **Vision design**: stable. Canonical reading order at [Canon](#canon-read-in-order) below.
- ✅ **Base layer (v0)**: MERGED to Master.
  - `agentic/` — FastMCP harness, four-verb contract, cell loader, name deriver. (PR #148)
  - `context/` — GraphQLite-backed store (with raw-SQLite fallback), Pre/PostToolUse hooks, artifact-driver protocol + `fs` driver, six JSON Schemas. (PR #149)
  - `workflow/` — pipeline runner, gate evaluator, envelope persistence into the graph, lazy_link flag, meta-row scaffold templates. (PR #150)
- ✅ **Schema drafts (column POVs)**: two of three landed.
  - `vision/specs/schemas/agentic/` — 11 schemas + README. (PR #151)
  - `vision/specs/schemas/context/` — 30+ schemas (nodes/edges/drivers/hooks) + README. (PR #152)
  - `vision/specs/schemas/workflow/` — patch ready; Jules silent-failed at push (10 files: phase-node, gate-node, continuation, phase-state-envelope, pipeline-run, gate-yaml, meta-row + interface-to-{agentic,context}). Apply in next session via `tools/jules-patch-extract.py 17230962122169358495`.
- 🟡 **Two integration gaps** to close before v0.1 (see `04-nextsteps.md`):
  - **W5** — meta-row scaffolder writes filesystem cells but doesn't emit `Cell`/`Phase`/`Row` graph nodes.
  - **C5** — Pre/PostToolUse hooks exist in `context/_hooks/` but are not registered with the FastMCP server in `agentic/_bootloader.py`.
- ⏭️ **Next milestone — v0.1**: running `agency` MCP plugin with all three columns wired, basic skill/workflow/context definitions, `jules` as the first materialized row. See `04-nextsteps.md`.

## The architecture in one paragraph

One engine — **FastMCP** — walks the **context graph**, stored as SQLite at `context/_store/ontology.db` via the **[GraphQLite](https://github.com/colliery-io/graphqlite)** extension (Cypher + node/edge primitives + graph algorithms). Workflows are *paths* through the graph; if a path doesn't exist, the engine lazily links a new one (no fixed pipelines). System metadata lives in the graph; user-facing artifact bytes live OUTSIDE via pluggable artifact drivers (`fs` mandatory in v1; `repo` / `s3` / `http` / `drive` follow-up). Skills + MCP are the universal interface. No `.meta.json` sidecar files are written to user storage — all metadata is properties on `Artefact` graph nodes.

This architecture dissolves the four cross-column "ownership" tensions surfaced in Phase 3 (gate-edge execution, mid-phase block serialization, hook execution layer, sidecar sandbox). Full rationale in `03-architecture.md`.

## Canon (read in order)

1. **[`00.1-Overview.md`](00.1-Overview.md)** — matrix law, result registry conclusion, strict cell manifests, column-specific Code Mode contracts.
2. **[`03-architecture.md`](03-architecture.md)** — runtime model: one engine + GraphQLite + artifact drivers. Resolves the four Phase-3 seams.
3. **[`02-plan.md`](02-plan.md)** — implementation plan (status: ✅ complete — base layer shipped).
4. **[`04-nextsteps.md`](04-nextsteps.md)** — what's next: close gaps W5/C5, write v1 specs, materialize the `jules` row as v0.1 proof.
5. **`specs/01..05`** — foundation contracts every column honors.
   - [`specs/01-cell-manifest.md`](specs/01-cell-manifest.md) — strict `manifest.toml` + name-derivation rules.
   - [`specs/02-tool-result-envelope.md`](specs/02-tool-result-envelope.md) — frozen FastMCP envelope; extensions in `data`.
   - [`specs/03-sidecar-metadata.md`](specs/03-sidecar-metadata.md) — **DEPRECATED as file-on-disk**; field-set canonicalized as `Artefact` node properties (see `03-architecture.md` §8).
   - [`specs/04-phase-state-envelope.md`](specs/04-phase-state-envelope.md) — **wire format preserved**; file-on-disk serialization superseded by `Continuation` graph node.
   - [`specs/05-gate-yaml.md`](specs/05-gate-yaml.md) — gate definitions as graph edge constructors.
6. **`specs/06..08`** — per-column base-layer implementation specs. All three SHIPPED (PR #148/#149/#150). Two known gaps (W5, C5) — see `04-nextsteps.md`.
   - [`specs/06-agentic-base.md`](specs/06-agentic-base.md) ✅ shipped — `agentic/`.
   - [`specs/07-workflow-base.md`](specs/07-workflow-base.md) ✅ shipped (W5 gap) — `workflow/`.
   - [`specs/08-context-base.md`](specs/08-context-base.md) ✅ shipped (C5 gap) — `context/`.
7. **`specs/schemas/`** — column-POV JSON Schema drafts (Draft 2020-12). Used as the source-of-truth pool for canonical schemas under `context/_shared/schemas/`. See `specs/schemas/agentic/README.md` and `specs/schemas/context/README.md`.

## Implementation code map (repo root)

| Path | What lives here |
|---|---|
| `agentic/_bootloader.py` | FastMCP server entry point |
| `agentic/_harness/{fastmcp_boot,cell_loader,name_deriver,codemode}.py` | Engine + cell discovery + naming |
| `workflow/_runner/{pipeline,gate,envelope}.py` | Pipeline walker, gate evaluator, envelope persistence into graph |
| `workflow/_runner/evaluators/{frontmatter_status,schema_match}.py` | Gate evaluators |
| `workflow/meta/{manifest.toml,phases/,templates/}` | The meta-row that scaffolds new rows |
| `context/_store/sqlite.py` | GraphQLite Python binding (with raw-SQLite fallback) |
| `context/_hooks/{pre,post}_tool_use.py` | Manifest validation + Artefact upsert |
| `context/_drivers/{protocol,fs}.py` | Artifact-driver protocol + `fs` implementation |
| `context/_shared/schemas/*.schema.json` | Six runtime-loaded JSON Schemas |
| `tests/{agentic,workflow,context}/` | Per-column unit tests |

## Per-column design archive (Phase 1-3 + meta)

The folders under `vision/` carry the work that produced the canon above. Treat as **historical reference, not active spec**.

- **`agentic/`** — Phase 1-3 column drafts: `BRIEF.md`, `COLUMN.md`, `INTERFACES.md`, `INTERFACE-TO-{WORKFLOW,CONTEXT}.md`, `GHERKIN-OWNED.md`, `ROW-EXAMPLES.md`, `RESEARCH-PATTERNS.md`, `REVIEW-OF-{WORKFLOW,CONTEXT}.md`, `INTEGRATED-DRAFT.md`, `Vision.md`.
- **`workflow/`** — same structure plus `META-WORKFLOW.md`.
- **`context/`** — same structure plus `ONTOLOGY.md`.

These were the inputs to specs 06/07/08 + `03-architecture.md`. Useful for tracing decisions; not authoritative.

## Out of scope (post-v0.1)

- Cross-row dispatch (planned `specs/09-cross-row-dispatch.md`) — `mcp__music_dispatch jules` calling into jules' agentic column from music's workflow.
- Central plugin bootloader (planned `specs/10-bootloader.md`) — glob-scan + tool registration at boot.
- Artifact drivers beyond `fs` (`repo` / `s3` / `http` / `drive`).
- Hot-reload of skills.
- Additional rows beyond `jules` (music / novel / podcast scaffolded via meta-row once architecture is proven).

## Charter (superseded)

[`00-charter.md`](00-charter.md) holds the original matrix law + 18 Gherkin scenarios. Superseded by `00.1-Overview.md`; kept for traceability.
