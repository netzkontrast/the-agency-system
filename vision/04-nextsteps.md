---
slug: vision-nextsteps
type: nextsteps-plan
status: ready
owner: claude
created: 2026-05-19
updated: 2026-05-19
summary: Concrete next-step plan after the base layer landed. Goal — v0.1 milestone — a running `agency` MCP plugin with three columns wired, basic skill/workflow/context definitions, and `jules` as the first materialized row. Six phases (N0–N5), Jules fan-out for the heavy parallel work, in-session Claude for integration glue.
depends_on:
  - vision/00.1-Overview.md
  - vision/03-architecture.md
  - vision/02-plan.md
referenced_by:
  - vision/README.md
---

# 04-nextsteps — From base layer to v0.1 running plugin

## Context

The base layer landed: `agentic/`, `workflow/`, `context/` are at the repo root with FastMCP harness, GraphQLite-backed graph, artifact drivers, and the workflow runner. Five architecture PRs merged on 2026-05-19. The implementation is correctly aligned with `vision/03-architecture.md` (one engine + graph + drivers) — most of the originally-planned v1 refactor delta was absorbed during the architecture-update probe wave.

Two **integration gaps** prevent the system from running end-to-end:

- **W5** — `workflow/_runner/pipeline.py::_run_meta_scaffold` writes filesystem cells but never calls `context.upsert_node()` for `Cell`/`Phase`/`Row` nodes. Scaffolded rows are invisible to the graph.
- **C5** — `context/_hooks/{pre,post}_tool_use.py` exist as standalone modules; `agentic/_bootloader.py::boot()` never imports them. Tool returns are not validated by `PreToolUse`; artifacts are not ingested by `PostToolUse`.

Beyond closing the gaps, v0.1 requires: (a) canonicalizing the column-POV JSON Schema drafts into `context/_shared/schemas/`, (b) writing the v1 specs that lock open architectural decisions (lazy-link mechanism, driver registry, Artefact node schema, graph bootstrap), and (c) **materializing the `jules` row** as the first proof point.

## The v0.1 milestone

**Definition of done**: a working `agency` MCP plugin (installed via the `.claude-plugin` marketplace mechanism this repo already supports) that exposes a slash command and a tool set per column for the `jules` row.

Concretely, after v0.1 a user can:

1. `claude plugin install agency` — installs the plugin from this repo.
2. `/agency:jules:research <topic>` — invokes a real agentic skill in `agentic/jules/skills/`.
3. `mcp__jules_workflow_start phase_id=01` — starts a `jules` workflow phase from `workflow/jules/phases/`.
4. `mcp__jules_context_query` — queries the `jules` row's graph via Cypher against `ontology.db`.
5. The MCP server boots from one entry, lists exactly the four base verbs + the jules row's derived tools, stays under the 500-token cold-boot budget.

## Phases

### N0 — Close the two gaps (in-session, ~60 min)

**Scope** — single PR `claude/architecture-base-gaps-Wxyz1`. Targets `agentic/_bootloader.py` (C5) and `workflow/_runner/pipeline.py` (W5).

**C5 fix** — `agentic/_bootloader.py::boot()`:

```python
from context._hooks.pre_tool_use import validate_envelope_in
from context._hooks.post_tool_use import ingest as ingest_envelope

# Replace the existing _wrapper closure with hook-wrapped variant.
# Bind t_name/t_func as defaults to avoid closure capture-by-reference bug.
def _wrapper(*, _t_name=t_name, _t_func=t_func, **kwargs) -> dict:
    validate_envelope_in(_t_name, kwargs)
    envelope = _t_func(**kwargs)
    ingest_envelope(_t_name, envelope)
    return envelope
```

**W5 fix** — `workflow/_runner/pipeline.py::_run_meta_scaffold`, after each `out_dir.mkdir(...)`:

```python
from context import Store  # at module top
g = Store()
g.upsert_node(f"cell/{col}/{new_row}", {"row": new_row, "column": col, "manifest_path": str(manifest_path)}, label="Cell")

# After the column loop:
g.upsert_node(f"row/{new_row}", {"row": new_row, "scaffolded_by": session_id}, label="Row")
g.upsert_node(f"phase/meta/02:{new_row}", {"row": "meta", "phase_id": "02", "target_row": new_row}, label="Phase")
g.upsert_edge("phase/meta/01", f"phase/meta/02:{new_row}", {}, rel_type="PRECEDES")
```

**Tests** — `tests/agentic/test_hooks_registered.py` (boot harness, call dummy tool emitting `artefact_metadata`, assert Artefact node lands), `tests/workflow/test_meta_scaffold.py::test_emits_cell_nodes` (scaffold "demo" row, assert 3 Cell + 1 Row + 1 Phase nodes in `ontology.db`).

### N1 — Apply the workflow-schemas patch (in-session, ~10 min)

Workflow-schemas Jules session (sid `17230962122169358495`) silent-failed at push. The patch has 10 files (8 schemas + README) in `vision/specs/schemas/workflow/`.

```bash
PYTHONPATH=jules-plugin/mcp-server/src python3 tools/jules-patch-extract.py 17230962122169358495
# Then apply via mcp__github__push_files to a new branch + PR.
```

### N2 — Canonicalize runtime schemas (in-session, ~30 min)

Diff `vision/specs/schemas/<col>/` against `context/_shared/schemas/` (the runtime path the v0 hooks load). For each runtime-loaded schema (`tool_result`, `agentic-cell`, `workflow-cell`, `context-cell`, `gate`, `sidecar`→`artefact-node`):

1. Promote the vision draft over the Jules-authored v0 stub.
2. Where columns disagree on a shared schema (e.g., `phase` — workflow and context both write one), favor the column that OWNS the node type per `03-architecture.md` §4 (context owns graph schemas).
3. Rename `context/_shared/schemas/sidecar.schema.json` → `artefact-node.schema.json`; update references in `context/_hooks/post_tool_use.py`.

Add `tests/context/test_schemas_canonical.py` round-tripping every schema example.

### N3 — Write v1 specs (in-session, ~45 min)

Two new specs:

- **`vision/specs/07-workflow-base-v1.md`** — lazy-link opt-in via `[workflow.lazy_link]` boolean in `workflow/<row>/manifest.toml`. Drop hard-coded `phases/NN-*.md` paths (Phase nodes are graph nodes; `body_ref` points at the prose). Wire real `context.Store` (drop `_MockContext` seam in `envelope.py`).
- **`vision/specs/08-context-base-v1.md`** — driver registry: `context/_drivers/__init__.py` exposes `REGISTRY: dict[str, ArtefactDriver]`, drivers self-register on import, PostToolUse resolves the right driver from `Artefact.artifact_driver`. Artefact node JSON Schema canonical (renamed from sidecar). Graph bootstrap: `Store.boot()` is idempotent, opens-or-creates `ontology.db`, seeds zero nodes, rows materialize via meta-row scaffolder. Drop the raw-SQLite fallback.

User signs off on v1 specs before N4 dispatches.

### N4 — Jules fan-out for v0.1 implementation (parallel, ~30 min dispatch + ~60 min Jules work)

Three Jules sessions in parallel (one per column), each implementing the v0.1 deliverables for its column. Allow-lists are strict — one column per session.

**Session 1 — agentic v0.1** (`agentic/jules/` + harness extensions):
- Create `agentic/jules/manifest.toml` with `[skills] exports = ["research"]` and `[tools] exports = ["query"]`.
- Create `agentic/jules/skills/research.md` — minimal agentic skill: research a topic and return findings.
- Create `agentic/jules/tools/query.py` — minimal MCP tool returning a `tool_result` envelope.
- Extend `agentic/_harness/cell_loader.py` if needed to actually invoke skills (currently only registers; doesn't dispatch).

**Session 2 — workflow v0.1** (`workflow/jules/`):
- Create `workflow/jules/manifest.toml` with `entry_verbs = ["start", "resume"]` and a `[workflow.lazy_link] = false` entry per v1 spec.
- Create `workflow/jules/phases/01-research.md` — minimal Phase body referenced by a `Phase` graph node.
- Create `workflow/jules/phases/02-synthesize.md`.
- Create `workflow/jules/gates/research-complete.yaml` per spec 05.
- Extend `workflow/_runner/pipeline.py::start` to handle non-meta rows by reading Phase nodes from the graph (replace the "row not supported" branch with a generic graph walker).

**Session 3 — context v0.1** (`context/jules/`):
- Create `context/jules/manifest.toml` with `[ontology] node_types = ["ResearchTopic", "Finding"]`.
- Create `context/jules/schemas/research-topic.schema.json` + `finding.schema.json`.
- Create `context/jules/templates/research-brief.md.jinja`.
- No changes to base `context/_store/` or `_hooks/` — these are owned by the base layer; the row only adds row-specific schemas and templates.

Each session opens its own PR. After all three merge, the `jules` row is materialized as the first non-meta row.

### N5 — Verify v0.1 end-to-end (in-session)

Run the verification checklist below. If green, declare v0.1 shipped and write `vision/05-v0-1-retrospective.md`.

## v0.1 verification checklist

| # | Item | How |
|---|---|---|
| V1 | Plugin installs cleanly | `claude plugin install agency` succeeds from this repo |
| V2 | FastMCP boots and serves four verbs | `python -m agentic._bootloader --emit-cold-boot` lists `mcp__list_tools`, `mcp__call_tool`, `mcp__list_skills`, `mcp__dispatch_skill` |
| V3 | Cold-boot payload < 500 tokens | `pytest tests/agentic/test_harness.py::test_cold_boot_under_500_tokens` |
| V4 | jules row cells discovered | `python -c "from agentic._harness.cell_loader import discover; print(discover().tools)"` includes `mcp__jules_*` entries |
| V5 | Hooks fire on every tool call (closes C5) | After N0, invoke any tool emitting `artefact_metadata`; assert `Artefact` node lands in `ontology.db` without manual ingest |
| V6 | Meta-row scaffold emits graph nodes (closes W5) | After N0, `mcp__workflow_start row=meta phase_id=02 inputs={"new_row":"demo"}`; query: 3 `Cell` + 1 `Row` + 1 `Phase` node |
| V7 | jules workflow phase starts | `mcp__jules_workflow_start phase_id=01` returns a `PhaseStateEnvelope` with `status="completed"` or `"blocked_on_user"`, NOT "row not supported" |
| V8 | jules research skill invokes | `/agency:jules:research <topic>` returns a non-error response with findings |
| V9 | jules context queries work | `mcp__jules_context_query` against `ontology.db` returns matching nodes for the row's node types |
| V10 | No sidecar files on disk | `find agentic/jules workflow/jules context/jules -name "*.meta.json"` returns nothing |
| V11 | Continuation is a graph node | After a blocked envelope, `workflow/_state/` does not exist AND `SELECT * FROM nodes WHERE label='Continuation'` returns rows |

When V1–V11 all pass on Master, **v0.1 is shipped**.

## Actor calibration

- **In-session Claude**: N0 (gaps), N1 (patch apply), N2 (schema canonicalization), N3 (v1 specs), N5 (verify).
- **Jules fan-out**: N4 (three parallel sessions, one per column).
- **User**: review/merge PRs from N0 + N4; sign off on v1 specs in N3.

## Out of scope for v0.1 (post-milestone)

- Additional rows (music, novel, podcast) — scaffolded via meta-row after `jules` proves the architecture.
- Cross-row dispatch (planned `specs/09`) — `mcp__music_workflow_start` calling into `agentic/jules/` via the harness-in-harness pattern.
- Central bootloader (`specs/10`) — currently `agentic/_bootloader.py` IS the boot; `specs/10` proposes generalizing it.
- Drivers beyond `fs` (`repo` / `s3` / `http` / `drive`).
- Hot-reload of skills.
- The `result/<row>/` artifact registry directory (architecture says artifacts live in user storage via drivers; the registry concept from `00.1-Overview.md` §2 is implemented by the driver pattern, not by a fixed directory).

## How to start the next session

Use `vision/NEXT-SESSION-PROMPT.md` — a 3500-char self-contained brief that drops a fresh Claude Code session into N0 with all context.
