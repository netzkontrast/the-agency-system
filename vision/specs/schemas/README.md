---
slug: vision-schemas-readme
type: catalog
status: draft
owner: claude
created: 2026-05-19
updated: 2026-05-19
summary: Top-level catalog of column-POV JSON Schema drafts (Draft 2020-12). Two of three landed (agentic, context); workflow patch ready, Jules silent-failed at push.
---

# `vision/specs/schemas/` — column-POV JSON Schema drafts

Three Jules sessions (`agentic-schemas` / `workflow-schemas` / `context-schemas`) wrote independent JSON Schema drafts (Draft 2020-12) capturing each column's view of its own domain plus its interfaces to the other two columns. The three views are NOT pre-reconciled — overlap and disagreement are expected (e.g., both workflow and context define `phase.schema.json`). The intersection happens in a follow-up pass that produces the canonical runtime schemas under `context/_shared/schemas/`.

## Status

| Column | Folder | PR | Status |
|---|---|---|---|
| agentic | `agentic/` | [#151](https://github.com/netzkontrast/the-agency-system/pull/151) | ✅ landed — 11 schemas + README |
| context | `context/` | [#152](https://github.com/netzkontrast/the-agency-system/pull/152) | ✅ landed — nodes/edges/drivers/hooks + README |
| workflow | _missing_ | — | 🟡 patch exists, Jules silent-failed at push. Apply via `PYTHONPATH=jules-plugin/mcp-server/src python3 tools/jules-patch-extract.py 17230962122169358495` |

The workflow patch contains: `phase-node`, `gate-node`, `continuation-node`, `phase-state-envelope`, `pipeline-run`, `gate-yaml`, `meta-row`, `interface-to-agentic`, `interface-to-context` + README.

## Catalog

### `agentic/` — see `agentic/README.md`

`skill-frontmatter` · `tool-manifest` · `harness-bootstrap` · `four-verb/{list-tools,call-tool,list-skills,dispatch-skill}-{request,response}` · `interface-to-{workflow,context}`.

### `context/` — see `context/README.md`

`nodes/{skill,tool,phase,gate,artefact,row,cell,session,continuation,template,schema}` · `edges/{precedes,blocks,blocked-on,produces,consumes,derived-from,satisfies-phase,dispatched-to,invoked-tool}` · `artifact-driver/{driver-manifest,get-bytes-{request,response},put-bytes-{request,response}}` · `hooks/{pretooluse,posttooluse,session-start}` · `interface-to-{agentic,workflow}`.

### `workflow/` (pending — patch ready)

`phase-node` · `gate-node` · `continuation-node` · `phase-state-envelope` · `pipeline-run` · `gate-yaml` · `meta-row` · `interface-to-{agentic,context}`.

## How these become runtime schemas

1. **These drafts are the spec-side reference.** They document what each column thinks it owns and what shapes it exchanges with peers.
2. **Runtime schemas live at `context/_shared/schemas/*.schema.json`** — loaded by `context/_hooks/{pre,post}_tool_use.py`. These are what hooks validate against.
3. **Intersection pass** (planned in `vision/04-nextsteps.md`): diff `vision/specs/schemas/<col>/` against `context/_shared/schemas/`. For each runtime-loaded schema, promote the vision draft over the v0 stub. Where columns disagree on a shared schema (e.g., `phase`), arbitrate in favor of the column that OWNS that node type per `03-architecture.md` §4 (context owns graph schemas authoritatively).
4. After intersection, this folder remains the column-POV canonical reference; `context/_shared/schemas/` is the runtime canonical.

## $id convention

Each schema sets `$id` under `https://agency-system.dev/schemas/<column>/<relative-path>.schema.json`. The host is informational (not currently resolvable); the path uniquely identifies the schema across the matrix.
