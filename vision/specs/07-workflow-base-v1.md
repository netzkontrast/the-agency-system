---
slug: spec-07-workflow-base-v1
type: impl-spec
status: ready
owner: claude
created: 2026-05-19
updated: 2026-05-19
summary: v1 rewrite of the workflow base layer at `workflow/` (repo root). Phases become graph nodes (`Phase{id, row, body_ref}`) walked by a generic traverser; the hard-coded `[[phases]]` array in the cell manifest is replaced by `[workflow.lazy_link]` opt-in plus a graph lookup. `_run_meta_scaffold` emits Cell + Row + Phase + PRECEDES into the ontology graph. The `_MockContext` seam in `envelope.py` is replaced by real `context.Store` wiring; Continuation lives only as a graph node. Supersedes `vision/specs/07-workflow-base.md`.
affects:
  - vision/specs/07-workflow-base-v1.md
  - workflow/_runner/pipeline.py
  - workflow/_runner/envelope.py
  - workflow/meta/manifest.toml
  - context/_shared/schemas/workflow-cell.schema.json
depends_on:
  - vision/specs/01-cell-manifest.md
  - vision/specs/02-tool-result-envelope.md
  - vision/specs/04-phase-state-envelope.md
  - vision/specs/05-gate-yaml.md
  - vision/specs/08-context-base-v1.md
  - vision/03-architecture.md
referenced_by: []
supersedes:
  - vision/specs/07-workflow-base.md
---

# Spec 07-v1 — Workflow Base Layer (graph-walker rewrite)

> **STATUS — 2026-05-19**: ✅ **Ready for review.** Locks the open
> architectural decisions left dangling after PR #150 + the N0 + N2
> phases (PR #155): lazy-link opt-in mechanism, the graph-walker that
> handles non-meta rows in `pipeline.start`, and the removal of the
> `_MockContext` seam in `envelope.py`. **Supersedes** the v0 spec at
> `vision/specs/07-workflow-base.md`, which remains in the tree only
> for archeology — it is annotated DEPRECATED at the top.

## Purpose

The v0 workflow base layer (PR #150) shipped a pipeline runner whose
phases were filesystem markdown files enumerated from a `[[phases]]`
TOML array. That model couples the workflow column to a particular
on-disk layout and prevents cross-row dispatch (planned spec 09) from
asking the graph "what comes next for row R?" without first parsing a
TOML file.

`vision/03-architecture.md` §8 demands that **Phase definitions are
graph nodes** — the prose body referenced by a `body_ref` field, never
indexed through a manifest array. This spec locks that shift, the
lazy-link opt-in syntax, and the wiring that turns
`workflow._runner.envelope.persist` from a mock into a real graph
write.

## What changes vs v0

| v0 (spec 07)                                       | v1 (this spec)                                                                  |
|---|---|
| `[[phases]]` array in `workflow/<row>/manifest.toml` | `[workflow.lazy_link]` boolean; phases live as `Phase` nodes in the graph     |
| `phases/<NN>-*.md` is the source of truth         | `body_ref` field on the `Phase` node points at the prose; the file is fallback |
| `pipeline.start` returns "row not supported" for non-meta rows | Generic graph walker reads `Phase` nodes by `(row, phase_id)`                  |
| `envelope.py` writes Continuation through `_MockContext` | `envelope.persist` writes Continuation via `context.Store().upsert_node(...)`  |
| TTL sweep deletes `workflow/_state/*.json` files  | TTL sweep deletes `Continuation` nodes from the graph                          |

The v0 facts that **survive unchanged**: the four-verb contract is the
agentic surface (spec 06); workflow exposes `start` / `resume` /
`scaffold` callables that agentic registers as MCP tools; phase markdown
files still live on disk and are still read for the prose body — they
just stop being the index. The meta-row keeps both phases (`01-bootstrap`,
`02-scaffold`); the scaffolder's W5 graph emission (PR #155) is the
example case for this spec.

## Folder layout (unchanged from v0 except for the meta manifest)

```
workflow/
├── __init__.py
├── _runner/
│   ├── __init__.py
│   ├── pipeline.py               # graph-walker entry; meta scaffolder
│   ├── gate.py
│   ├── envelope.py               # Continuation → context.Store (no _MockContext)
│   └── evaluators/...            # unchanged
└── meta/
    ├── manifest.toml             # `[workflow.lazy_link] = false`
    ├── phases/                   # phase prose, body_ref targets
    │   ├── 01-bootstrap.md
    │   └── 02-scaffold.md
    └── templates/...             # unchanged
```

`workflow/_state/` from the v0 spec is **gone**. It does not exist in
the tree; the Jules base-layer PR #150 already shipped without it
(Continuation is a `context.Store().upsert_node` call). Removing this
spec line was the architecture-update probe-wave fix.

## Functional requirements

### FR1 — Lazy-link manifest field

`workflow/<row>/manifest.toml` adds an optional table:

```toml
[workflow]
entry_verbs = ["start", "resume"]

[workflow.lazy_link]
enabled = false
```

`enabled = false` (the default — and the only legal value for the
meta-row) tells the pipeline runner to **refuse** when a queried
`(row, phase_id)` has no Phase node in the graph. `enabled = true`
permits the runner to create a placeholder Phase node and continue
under the rules in `vision/03-architecture.md` §4. The boolean is
opt-in per row because lazy creation produces nodes the user did not
explicitly approve.

The `workflow-cell.schema.json` is updated accordingly: `[workflow]` is
required (already the case); the `lazy_link` sub-table is optional with
a boolean `enabled` field that defaults to `false`.

The legacy `[[phases]]` array remains valid in the schema for the meta-row
**only** (so its two-phase prose body keeps working through this transition).
Other rows MUST NOT declare `[[phases]]`; their phases live in the graph.

### FR2 — Phase nodes in the graph

A `Phase` node has the identity convention:

```
phase/<row>/<phase_id>
```

…and the payload:

```json
{
  "row": "<row>",
  "phase_id": "<NN>",
  "body_ref": "phases/<NN>-<slug>.md",
  "lazy_created": false
}
```

`body_ref` is a path relative to `workflow/<row>/`. The runner reads the
prose body lazily — only when the phase actually executes — preserving
the cold-boot token budget the agentic harness owns. `lazy_created`
defaults to `false`; the lazy-link branch (FR3) sets it `true` and
records the session id that created it.

Phase nodes are populated by the meta-row scaffolder when a new row is
created and by row-specific seed routines invoked during the row's
first boot. Phases are **never** derived from filesystem scanning at
runtime — that anti-pattern is what v1 erases.

### FR3 — Generic graph walker in `pipeline.start`

`pipeline.start(row, phase_id, inputs, lazy_link=False)` becomes a
graph walker:

```python
def start(row: str, phase_id: str, inputs: dict, lazy_link: bool = False) -> PhaseStateEnvelope:
    session_id = str(uuid.uuid4())
    g = Store()
    g.boot()

    phase_node = g.query(
        "MATCH (p:Phase {row: $row, phase_id: $pid}) RETURN p",
        params={"row": row, "pid": phase_id},
    )

    if not phase_node:
        if not lazy_link:
            return _failed_envelope(session_id, row, phase_id,
                                    f"row {row} phase {phase_id} not in graph")
        # lazy-link branch
        phase_node = _lazy_create_phase(g, row, phase_id, session_id)

    if row == "meta":
        return _run_meta_scaffold(session_id, inputs)

    return _walk_phase(session_id, phase_node, inputs)
```

`_walk_phase` reads the `body_ref`, dispatches to the row's handler
(located via the row's `agentic/<row>/` manifest), evaluates any gates
linked to the Phase node via `BLOCKS` edges, and returns a
`PhaseStateEnvelope`. `_lazy_create_phase` upserts a Phase node with
`lazy_created=true, scaffolded_by=session_id` and returns it. This
generalizes — across non-meta rows — what `_run_meta_scaffold` already
does for the bootstrap/scaffold pair (W5 in PR #155).

The `lazy_link` keyword argument's value is also checked against the
caller's `manifest.lazy_link.enabled`. A caller cannot pass
`lazy_link=True` for a row that opted out. Concretely: if
`workflow/<row>/manifest.toml` has `[workflow.lazy_link] enabled = false`,
the runner ignores `lazy_link=True` and returns a failed envelope
explaining the conflict, so a row's opt-out is honoured even by an
explicit override at the callsite.

### FR4 — Continuation via real `context.Store`

`workflow/_runner/envelope.py` drops the `_MockContext` class entirely.
`persist` becomes:

```python
def persist(envelope: PhaseStateEnvelope) -> str:
    store = Store()
    store.boot()
    node_id = f"continuation:{envelope['session_id']}:{envelope['phase_id']}"
    store.upsert_node(
        node_id,
        {
            "session_id": envelope["session_id"],
            "phase_id":   envelope["phase_id"],
            "opaque_state": envelope["opaque_state"],
            "envelope":   envelope,
        },
        label="Continuation",
    )
    return node_id
```

`hydrate` reads the same node by `MATCH (c:Continuation {id: $id})`;
`delete` removes it. `sweep_ttl` performs a Cypher query for
`Continuation` nodes whose `created_at` is older than 30 days and
deletes them — the cleanup that used to walk `workflow/_state/` now
walks the graph.

### FR5 — Meta-row scaffolder retains its v0 contract

`_run_meta_scaffold` (PR #150 + the W5 emission in PR #155) is the
concrete example of the FR2 + FR3 model. After 02-scaffold runs it has
already emitted:

- `cell/<col>/<new_row>` Cell node, one per column (3 total).
- `row/<new_row>` Row node.
- `phase/meta/02:<new_row>` Phase node for the scaffold-completed
  instance, with a `PRECEDES` edge from `phase/meta/01` to the new
  Phase node.

The Phase node for any row's bootstrap (`phase/<row>/01`) is **not**
emitted by the meta-scaffolder — the row's own seed routine (agentic
column, on first boot) is responsible. The meta scaffolder ships the
graph stubs the row's seed picks up.

### FR6 — Entry verbs unchanged

`workflow/<row>/manifest.toml [workflow] entry_verbs` keeps the v0
shape. The legal vocabulary is `["scaffold", "start", "resume"]`. The
runner exports callables; agentic (spec 06) decides MCP wiring.

### FR7 — TTL sweep targets graph nodes

`pipeline.boot()` runs a Cypher query against the graph for
`Continuation` nodes whose `created_at` is older than 30 days and
deletes them, logging each session id and phase id. The 30-day
threshold from v0 is preserved. The sweep is best-effort; a delete
failure logs a warning but does NOT abort boot.

## Worked example — non-meta row (jules)

Cold boot after `jules` row exists, an envelope blocked, user resumes:

1. Agentic harness calls `pipeline.boot()`. TTL sweep finds no expired
   continuations. No-op.
2. User invokes `mcp__jules_start(phase_id="01", inputs={"topic": "x"})`.
3. Harness translates to `pipeline.start(row="jules", phase_id="01", inputs={...})`.
4. `pipeline.start` queries the graph: `MATCH (p:Phase {row: "jules", phase_id: "01"}) RETURN p`.
5. The Phase node returns with `body_ref = "phases/01-research.md"`.
6. `_walk_phase` reads `workflow/jules/phases/01-research.md`, dispatches
   to the row handler, and returns `status="blocked_on_user"` because a
   gate stops on the first user-input request.
7. `envelope.persist` upserts a `Continuation` node in the graph.
8. User replies. `pipeline.resume(session_id, "01", user_response)`
   reads the Continuation, merges the response into `opaque_state`,
   returns `status="completed"`.
9. The Continuation node is deleted by `delete(session_id, "01")`.

## Acceptance criteria

```gherkin
Scenario: lazy-link opt-out blocks unknown phase
  Given workflow/jules/manifest.toml has [workflow.lazy_link] enabled = false
  And no Phase node exists for (row="jules", phase_id="99")
  When pipeline.start(row="jules", phase_id="99", inputs={}) is invoked
  Then the returned envelope has status="failed"
  And tool_result.data.error.message mentions "not in graph"

Scenario: lazy-link opt-in creates placeholder
  Given workflow/sandbox/manifest.toml has [workflow.lazy_link] enabled = true
  And no Phase node exists for (row="sandbox", phase_id="07")
  When pipeline.start(row="sandbox", phase_id="07", inputs={}, lazy_link=True) is invoked
  Then a Phase node phase/sandbox/07 exists with lazy_created=true
  And the envelope's status is "running" or "blocked_on_user" (not "failed")

Scenario: non-meta row walks the graph
  Given a Phase node phase/jules/01 with body_ref="phases/01-research.md"
  And workflow/jules/phases/01-research.md exists
  When pipeline.start(row="jules", phase_id="01", inputs={"topic": "x"}) is invoked
  Then the envelope's phase_id == "01" and row == "jules"
  And the envelope is NOT a "row not supported" failure

Scenario: Continuation lands as a graph node, not a file
  Given a pipeline yields status="blocked_on_user"
  When envelope.persist runs
  Then a Continuation node exists at continuation:<sid>:<pid> in ontology.db
  And no file appears under workflow/_state/

Scenario: TTL sweep deletes expired Continuation nodes
  Given a Continuation node with created_at 31 days old
  When pipeline.boot runs
  Then the Continuation node is deleted from the graph
  And a log line records the session id and phase id
```

## `affects:` allow-list

The implementation PR that lands FR1–FR7 writes ONLY these paths:

- `vision/specs/07-workflow-base-v1.md` (this file)
- `workflow/_runner/pipeline.py`
- `workflow/_runner/envelope.py`
- `workflow/meta/manifest.toml`
- `context/_shared/schemas/workflow-cell.schema.json`
- `tests/workflow/test_pipeline.py`
- `tests/workflow/test_envelope.py`

Any other path is out of scope. Drop the `_MockContext` class from
`envelope.py` in the same PR — no compatibility shim. Other-row
manifests (e.g., `workflow/jules/manifest.toml`) are written by their
own row-creation PRs, not by this spec's PR.

## Out of scope

- **Cross-row dispatch** (planned spec 09) — handing an envelope from
  row R1 into row R2 is not enabled by this spec.
- **Phase-node mutation outside the meta-scaffolder** — row-specific
  seed routines (which write a row's bootstrap Phase) live in the
  agentic column, not here.
- **Hot reload of phase prose bodies** — re-reading a file mid-run is
  still cold-restart-only.
- **Gate prelinking** — `BLOCKS` edges from Phase nodes to Gate nodes
  are owned by the gate evaluator (FR2 of v0 spec 07) and unchanged.

## Dependencies

- **Spec 01** — cell manifest schema. The `[workflow.lazy_link]`
  sub-table extends the workflow-cell schema; v1 carries that change.
- **Spec 02** — `tool_result` envelope; failed/lazy-create paths both
  conform.
- **Spec 04** — `PhaseStateEnvelope` shape. The wire format is
  unchanged; only the serialization target moves (graph node, no file).
- **Spec 05** — gate YAML; gate evaluator dispatch is unchanged.
- **Spec 08-v1** — provides `context.Store` (the `upsert_node` /
  `query` / `boot` API), the Artefact node schema, and the driver
  registry. Without 08-v1 the Continuation rewrite has nothing to wire
  against.
- **`vision/03-architecture.md`** §4–§8 — the architectural mandate for
  phases-as-graph-nodes and the deprecation of the `workflow/_state/`
  file pattern.
