---
slug: spec-07-workflow-base
type: impl-spec
status: ready
owner: claude
created: 2026-05-19
updated: 2026-05-19
summary: Implementation spec for the workflow column base layer at `workflow/` (repo root). Pipeline runner + gate evaluator + PhaseStateEnvelope serialization + the meta-row that scaffolds new rows from templates. No row-specific phase content in this PR (except the meta-row itself).
affects:
  - vision/specs/07-workflow-base.md
depends_on:
  - vision/specs/01-cell-manifest.md
  - vision/specs/02-tool-result-envelope.md
  - vision/specs/04-phase-state-envelope.md
  - vision/specs/05-gate-yaml.md
  - vision/specs/08-context-base.md
referenced_by: []
implements_for_jules:
  # STATUS 2026-05-19: ✅ shipped (PR #150). W5 follow-up gap noted below.
  - workflow/__init__.py
  - workflow/_runner/__init__.py
  - workflow/_runner/pipeline.py
  - workflow/_runner/gate.py
  - workflow/_runner/envelope.py
  - workflow/_runner/evaluators/__init__.py
  - workflow/_runner/evaluators/frontmatter_status.py
  - workflow/_runner/evaluators/schema_match.py
  - workflow/_state/README.md
  - workflow/_state/.gitkeep
  - workflow/meta/manifest.toml
  - workflow/meta/phases/01-bootstrap.md
  - workflow/meta/phases/02-scaffold.md
  - workflow/meta/templates/agentic-cell.toml.jinja
  - workflow/meta/templates/workflow-cell.toml.jinja
  - workflow/meta/templates/context-cell.toml.jinja
  - tests/workflow/test_pipeline.py
  - tests/workflow/test_gate.py
  - tests/workflow/test_envelope.py
  - tests/workflow/test_meta_scaffold.py
---

# Spec 07 — Workflow Base Layer

> **DEPRECATED — 2026-05-19**: superseded by
> [`vision/specs/07-workflow-base-v1.md`](07-workflow-base-v1.md). The
> v1 spec locks the open architectural decisions (lazy-link opt-in,
> phases-as-graph-nodes, generic non-meta-row walker, real
> `context.Store` for Continuation) and is the single source of truth
> for the workflow base layer from this point on. This v0 document is
> retained for archeology only — do not implement against it.

> **STATUS — 2026-05-19**: ✅ **Implemented and merged** in PR #150. Pipeline runner, gate evaluator, envelope persistence into the graph (Continuation as graph node — `workflow/_state/` JSON files are GONE), `lazy_link` flag, and the meta-row scaffolder templates all live under `workflow/`. **Open follow-up (W5)**: `_run_meta_scaffold` writes filesystem cells but does NOT yet emit `Cell`/`Phase`/`Row` graph nodes via `context.upsert_node()` — see `vision/04-nextsteps.md`. The v1 rewrite anchored by `vision/03-architecture.md` also locks: phases-as-graph-nodes (drop hard-coded `phases/NN-*.md` paths), lazy-link opt-in via `[workflow.lazy_link]` manifest field, real `context.Store` wiring (drop the `_MockContext` seam in `envelope.py`).

## Purpose

Implementation contract for `workflow/` at the repo root — the **WHEN** column of the 3×N matrix. A Jules session implementing this spec produces the pipeline runner, the gate evaluator, the `PhaseStateEnvelope` serializer, and the meta-row that scaffolds new rows from Jinja templates.

This PR ships the base layer only. No row-specific phase content lands here — except the meta-row itself (`workflow/meta/`), which IS a workflow row and is the seed every other row scaffolds from.

Boundaries (per `00.1-Overview.md` §1): workflow owns process state, phase ordering, gate evaluation, envelope construction. It does NOT register MCP tools (agentic, spec 06) and does NOT write the graph (context, spec 08) — it emits edge directives; context ingests.

## Folder layout

The Jules session creates exactly this tree under the repo root:

```
workflow/
├── __init__.py
├── _runner/
│   ├── __init__.py
│   ├── pipeline.py               # phase walker, lazy load
│   ├── gate.py                   # gate evaluator (reads spec 05 YAML)
│   ├── envelope.py               # PhaseStateEnvelope impl (spec 04)
│   └── evaluators/
│       ├── __init__.py
│       ├── frontmatter_status.py # callable-kind evaluators
│       └── schema_match.py
├── _state/                       # opaque state JSON files for resume
│   ├── README.md                 # explains the on-disk format; no .py
│   └── .gitkeep
└── meta/                         # the meta-row — scaffolds new rows
    ├── manifest.toml
    ├── phases/
    │   ├── 01-bootstrap.md
    │   └── 02-scaffold.md
    └── templates/
        ├── agentic-cell.toml.jinja
        ├── workflow-cell.toml.jinja
        └── context-cell.toml.jinja
```

`workflow/_state/` ships empty save for its README and a `.gitkeep`. No `.py` lives under `_state/` — it is a data directory, not a module.

## Functional requirements

### FR1 — Pipeline runner

Module: `workflow/_runner/pipeline.py`. Three entry callables:

```python
def boot() -> None: ...
def start(row: str, phase_id: str, inputs: dict) -> PhaseStateEnvelope: ...
def resume(session_id: str, phase_id: str, user_response: dict) -> PhaseStateEnvelope: ...
```

`start` loads `workflow/<row>/manifest.toml` per spec 01, enumerates `[[phases]]`, and lazy-loads ONLY the requested phase's markdown body. Other phases stay on disk — progressive disclosure is the token-economy invariant. `resume` reads `workflow/_state/<session_id>/<phase_id>.json`, hydrates the envelope (spec 04), merges `user_response` into `opaque_state`, and continues. Both return a `PhaseStateEnvelope`; on `blocked_*`, the envelope is also persisted (FR3).

### FR2 — Gate evaluator

Module: `workflow/_runner/gate.py`. Entry callable:

```python
def evaluate(gate_yaml_path: Path, envelope_state: dict) -> GateResult: ...
```

Reads the YAML per spec 05. Dispatches on `evaluator.kind`: `callable` → import `module.callable` from `workflow/_runner/evaluators/`; `schema` → JSON-Schema validate `envelope_state`; `sql` → run query against the context store (spec 08); `manual` → return blocked. On success: materializes `on_success.emit_edge` into a graph-edge write call into the context store. The runner does NOT write SQLite directly — it calls the context store's documented upsert path. Edge construction here; ingestion in context. Hard-blocking failure: `ok=False` with `tool_result.data.error.code = "GATE_FAILED"`. Advisory failure: `ok=True`, surfaced as `tool_result.warnings`.

Two evaluators ship under `_runner/evaluators/`:

- `frontmatter_status.py` — callable kind. Reads a file's YAML frontmatter, asserts a status field matches an expected value.
- `schema_match.py` — schema kind. Validates a payload against a named schema in `context/_shared/schemas/`.

### FR3 — Envelope persistence

Module: `workflow/_runner/envelope.py`. Implements the `PhaseStateEnvelope` TypedDict from spec 04 plus:

```python
def persist(envelope: PhaseStateEnvelope) -> Path: ...
def hydrate(session_id: str, phase_id: str) -> PhaseStateEnvelope: ...
```

When the pipeline yields `blocked_on_gate` or `blocked_on_user`, `persist` writes the envelope as JSON to `workflow/_state/<session_id>/<phase_id>.json` using the atomic write protocol from spec 04 (write to `*.tmp` in the same directory, `fsync`, `os.replace`). The session directory is created on first write. `hydrate` is the inverse — reads JSON, validates against the spec-04 schema, returns the TypedDict. On `status="completed"` or `"failed"`, the envelope file is deleted (logged, not silent).

### FR4 — Meta-row

`workflow/meta/` IS a workflow row (the only one in this PR). Manifest conforms to spec 01 with `row = "meta"`, `column = "workflow"`, `entry_verbs = ["scaffold"]`. Its pipeline scaffolds a new row's three cells from `workflow/meta/templates/`.

User invocation (via the agentic harness, spec 06):

```python
mcp__meta_start_phase(phase_id="02", inputs={"new_row": "podcast"})
```

This calls `pipeline.start(row="meta", phase_id="02", inputs={"new_row": "podcast"})` and returns the `PhaseStateEnvelope` with the three created paths in `tool_result.data.created_cells`.

Two phases:

- `phases/01-bootstrap.md` — verifies the new row name matches `^[a-z][a-z0-9-]{0,30}$` (spec 01) and that no cell exists at `agentic/<new_row>/`, `workflow/<new_row>/`, or `context/<new_row>/`. Returns `blocked_on_user` if any cell exists, with `tool_result.data.error.fix_hint = "row already exists; delete or pick a different name"`.
- `phases/02-scaffold.md` — runs after `01-bootstrap`. Renders the three Jinja templates substituting `{{ new_row }}` everywhere, writes the three manifest files, writes empty handler stubs, returns `status="completed"` with the created paths.

### FR5 — Entry verbs

`workflow/<row>/manifest.toml [workflow] entry_verbs` is the subset of the four-verb contract the runner offers as MCP-callable entry points (`["scaffold", "start", "resume"]` is the legal vocabulary). For the meta-row in this PR: `entry_verbs = ["scaffold"]`.

The runner DOES NOT register MCP tools itself. It exposes callables; the agentic harness (spec 06) iterates `entry_verbs` at boot and registers each as `mcp__<row>_<verb>`. One-directional: workflow exports callables, agentic decides how to surface them.

### FR6 — TTL sweep

On `pipeline.boot()` (called by the agentic bootloader, spec 06), the runner scans `workflow/_state/` and deletes envelope files whose mtime is older than 30 days. Each deletion is logged with the session id and phase id. Best-effort: a deletion failure logs a warning but does NOT abort boot. Silent expiry is forbidden.

## The meta-row scaffold

Concrete sequence for `scaffold(new_row="podcast")` after the bootstrap phase has passed:

1. **Read templates.** Load all three `*.toml.jinja` files from `workflow/meta/templates/` into memory. Jinja2 with `autoescape=False` (these produce TOML, not HTML).
2. **Substitute.** Render each template with `{"new_row": "podcast"}`. Every `{{ new_row }}` becomes `podcast`. No other substitutions in this PR — extension is out of scope.
3. **Write three manifests.** Create the cell directories and write the rendered output:
   - `agentic/podcast/manifest.toml`
   - `workflow/podcast/manifest.toml`
   - `context/podcast/manifest.toml`
   Each `mkdir` is `parents=True, exist_ok=False` — bootstrap has guaranteed the dirs do not exist.
4. **Write handler stubs.** Empty stubs the row will populate later: `agentic/podcast/skills/.gitkeep`, `agentic/podcast/tools/.gitkeep`, `workflow/podcast/phases/.gitkeep`, `workflow/podcast/gates/.gitkeep`, `context/podcast/schemas/.gitkeep`, `context/podcast/templates/.gitkeep`.
5. **Return.** A `PhaseStateEnvelope` with `status="completed"` and `tool_result`:

```json
{
  "ok": true,
  "data": {
    "created_cells": [
      "agentic/podcast/manifest.toml",
      "workflow/podcast/manifest.toml",
      "context/podcast/manifest.toml"
    ]
  },
  "warnings": [],
  "next_suggested_tools": ["mcp__podcast_scaffold"]
}
```

## Worked example

Cold boot of an EMPTY `workflow/` tree (no rows exist yet except `meta`):

1. The agentic harness calls `pipeline.boot()`. The TTL sweep finds an empty `_state/` — no-op.
2. The harness scans `workflow/*/manifest.toml`. The only file present is `workflow/meta/manifest.toml`.
3. The harness reads `meta`'s `entry_verbs = ["scaffold"]` and registers `mcp__meta_scaffold` as the sole workflow-column tool.
4. The user invokes `mcp__meta_scaffold(new_row="podcast")`. The agentic harness translates this to `pipeline.start(row="meta", phase_id="01", inputs={"new_row": "podcast"})`.
5. Phase `01-bootstrap` verifies kebab-case and confirms no `agentic/podcast/`, `workflow/podcast/`, or `context/podcast/` exists. Returns `status="running"`; the runner immediately continues into phase `02-scaffold`.
6. Phase `02-scaffold` renders three templates, writes three `manifest.toml` files, writes six `.gitkeep` stubs, and returns `status="completed"` with the created paths.
7. After the next agentic boot, `mcp__podcast_*` tools register (once that row's `agentic/podcast/manifest.toml` declares its exports — out of scope here).

## Acceptance criteria

```gherkin
Scenario: Pipeline starts and yields running envelope
  Given workflow/meta/manifest.toml exists with phases ["01", "02"]
  When `pipeline.start(row="meta", phase_id="01", inputs={"new_row": "podcast"})` is called
  Then a PhaseStateEnvelope is returned
  And the envelope validates against the spec-04 schema
  And envelope.phase_id == "01" and envelope.row == "meta"

Scenario: Blocked envelope serializes and resumes
  Given a pipeline yields PhaseStateEnvelope with status="blocked_on_user"
  When `envelope.persist(envelope)` is called
  Then a JSON file appears at `workflow/_state/<session_id>/<phase_id>.json`
  And the file validates against the spec-04 schema
  When `pipeline.resume(session_id, phase_id, user_response)` is called
  Then the envelope is hydrated from disk
  And opaque_state contains the merged user_response keys
  And the pipeline continues execution

Scenario: Meta-row scaffolds three cells from templates
  Given workflow/meta/templates/ contains three `*.toml.jinja` files
  And no row "podcast" exists in any column
  When `pipeline.start(row="meta", phase_id="01", inputs={"new_row": "podcast"})` completes through phase 02
  Then `agentic/podcast/manifest.toml`, `workflow/podcast/manifest.toml`, and `context/podcast/manifest.toml` exist
  And each file validates against its column's cell schema (spec 01)
  And `tool_result.data.created_cells` lists the three paths

Scenario: Gate evaluator emits SATISFIES_PHASE edge on success
  Given a gate YAML with kind="callable" and `on_success.emit_edge.type = "SATISFIES_PHASE"`
  And the referenced evaluator returns ok=True
  When `gate.evaluate(gate_yaml_path, envelope_state)` runs
  Then the result includes `tool_result.data.gate_state.edge_emitted = "SATISFIES_PHASE"`
  And the context store's edge-upsert callable is invoked exactly once

Scenario: Expired envelope auto-deletes on boot
  Given a file at `workflow/_state/<session_id>/<phase_id>.json` with mtime 31 days old
  When `pipeline.boot()` runs the TTL sweep
  Then the file is deleted
  And a log line records the session_id and phase_id of the deleted envelope
```

## `affects:` allow-list for the implementation PR

The Jules session implementing this spec writes ONLY these paths:

- `workflow/__init__.py`
- `workflow/_runner/__init__.py`
- `workflow/_runner/pipeline.py`
- `workflow/_runner/gate.py`
- `workflow/_runner/envelope.py`
- `workflow/_runner/evaluators/__init__.py`
- `workflow/_runner/evaluators/frontmatter_status.py`
- `workflow/_runner/evaluators/schema_match.py`
- `workflow/_state/README.md`
- `workflow/_state/.gitkeep`
- `workflow/meta/manifest.toml`
- `workflow/meta/phases/01-bootstrap.md`
- `workflow/meta/phases/02-scaffold.md`
- `workflow/meta/templates/agentic-cell.toml.jinja`
- `workflow/meta/templates/workflow-cell.toml.jinja`
- `workflow/meta/templates/context-cell.toml.jinja`
- `tests/workflow/test_pipeline.py`
- `tests/workflow/test_gate.py`
- `tests/workflow/test_envelope.py`
- `tests/workflow/test_meta_scaffold.py`

Any change outside this list is out of scope. If Jules feels the urge to edit `agentic/`, `context/`, or another `vision/` file, it must reply with a friction note and stop.

## Out of scope

- **Cross-row dispatch** — handing an envelope from row R1's workflow into row R2's workflow is spec 09. Single-row pipelines only here.
- **Row-specific phase content** — phases for `music`, `novel`, `podcast`, `jules`, etc. scaffold via the meta-row in a follow-up PR. The only phases that ship here are `meta`'s own two.
- **Graph store implementation** — the runner calls the context store's edge-upsert callable but does not implement it. Spec 08.
- **Hot reload of phase markdown** — editing a phase file does not invalidate the in-process cache mid-run. Cold-restart the harness.

## Dependencies

- **Spec 01** — cell manifest schema. The runner reads `workflow/<row>/manifest.toml` per this contract.
- **Spec 02** — tool result envelope. Every yield wraps a `tool_result` that matches.
- **Spec 04** — `PhaseStateEnvelope` shape, serialization protocol, status enum, atomic-write rules.
- **Spec 05** — gate YAML schema. The gate evaluator parses this shape and dispatches on `evaluator.kind`.
- **Spec 08** — context base. The gate evaluator calls the context store's edge-upsert path; the meta-row reads JSON Schemas from `context/_shared/schemas/` to validate scaffolded manifests.
