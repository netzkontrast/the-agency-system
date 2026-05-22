---
slug: spec-08-context-base
type: impl-spec
status: ready
owner: claude
created: 2026-05-19
updated: 2026-05-19
summary: Implementation spec for the context column base layer at `context/` (repo root). SQLite ontology store with Cypher-compat query subset, Pre/PostToolUse hook callables, and the cross-cutting JSON Schemas (`_shared/schemas/`) that every column validates against.
affects:
  - vision/specs/08-context-base.md
depends_on:
  - vision/specs/01-cell-manifest.md
  - vision/specs/02-tool-result-envelope.md
  - vision/specs/03-sidecar-metadata.md
  - vision/specs/05-gate-yaml.md
referenced_by: []
implements_for_jules:
  - context/__init__.py
  - context/_store/__init__.py
  - context/_store/sqlite.py
  - context/_store/schema.sql
  - context/_store/cypher_adapter.py
  - context/_hooks/__init__.py
  - context/_hooks/pre_tool_use.py
  - context/_hooks/post_tool_use.py
  - context/_shared/schemas/tool_result.schema.json
  - context/_shared/schemas/agentic-cell.schema.json
  - context/_shared/schemas/workflow-cell.schema.json
  - context/_shared/schemas/context-cell.schema.json
  - context/_shared/schemas/sidecar.schema.json
  - context/_shared/schemas/gate.schema.json
  - tests/context/test_store.py
  - tests/context/test_hooks.py
  - tests/context/test_cypher_subset.py
  - tests/context/test_schemas.py
---

# Spec 08 — Context Base Layer

> **DEPRECATED — 2026-05-19**: superseded by
> [`vision/specs/08-context-base-v1.md`](08-context-base-v1.md). The
> v1 spec locks GraphQLite as the lone graph substrate (no raw-SQLite
> fallback), pins the driver `REGISTRY` surface in
> `context/_drivers/__init__.py`, names the Artefact node schema
> canonical (renamed in N2 PR #155 from `sidecar.schema.json` →
> `artefact-node.schema.json`), and codifies the graph-bootstrap
> behaviour. This v0 document is retained for archeology only — do
> not implement against it. The `sidecar.schema.json` references
> below describe a file that no longer exists in the tree.

> **STATUS — 2026-05-19**: ✅ **Implemented and merged** in PR #149. The substrate is **GraphQLite** (https://github.com/colliery-io/graphqlite) via `from graphqlite import Graph` in `context/_store/sqlite.py`, with a raw-SQLite fallback when the extension isn't installed. Six runtime JSON Schemas live at `context/_shared/schemas/`. Artifact-driver Protocol (`_drivers/protocol.py`) + `fs` driver (`_drivers/fs.py`) are in place. PostToolUse hook upserts `Artefact` nodes; **no `.meta.json` sidecar files are written to user storage** (deprecation of spec 03 file-on-disk pattern per `vision/03-architecture.md` §8). **Open follow-up (C5)**: the Pre/PostToolUse hooks need to be **registered** with the FastMCP server in `agentic/_bootloader.py::boot()` so they fire on every tool call — see `vision/04-nextsteps.md`. The v1 rewrite anchored by `vision/03-architecture.md` also locks: driver registry pattern (`context/_drivers/__init__.py` exposing a `REGISTRY: dict`), Artefact node JSON Schema (rename `sidecar.schema.json` → `artefact-node.schema.json`), graph bootstrap behaviour, drop the raw-SQLite fallback.

## Purpose

Implementation contract for the **context column base layer** at
`context/` (repo root, NOT under `vision/`). A Jules session reads
this spec and builds: the SQLite ontology store, the Pre/PostToolUse
hook callables, and the cross-cutting JSON Schemas in
`_shared/schemas/` that the agentic and workflow base layers import
by path. Schemas live in exactly one canonical place. Anyone needing
isomorphism reads from there. Row-specific cells (`context/<row>/`)
do not land in this PR — the base layer must boot with zero rows.

Resolves Phase 3 **Context Q2** (hook execution layer): hooks are
plain Python callables in `context._hooks`. The agentic harness
applies them as decorators during tool registration; this column
ships logic, not wiring.

## Folder layout

```
context/
├── __init__.py
├── _store/
│   ├── __init__.py
│   ├── sqlite.py                # SQLite ontology + Cypher-compat query interface
│   ├── schema.sql               # CREATE TABLE statements
│   └── cypher_adapter.py        # translates a small subset of Cypher → SQL
├── _hooks/
│   ├── __init__.py
│   ├── pre_tool_use.py          # validates frontmatter & manifest schemas
│   └── post_tool_use.py         # graph upsert + sidecar ingestion
└── _shared/
    └── schemas/
        ├── tool_result.schema.json     (from spec 02 verbatim)
        ├── agentic-cell.schema.json    (from spec 01)
        ├── workflow-cell.schema.json   (from spec 01)
        ├── context-cell.schema.json    (from spec 01)
        ├── sidecar.schema.json         (from spec 03)
        └── gate.schema.json            (from spec 05)
```

## Functional requirements

### 1. SQLite ontology store

`context/_store/sqlite.py` exposes a `Store` class:

```python
class Store:
    def __init__(self, db_path: str | None = None) -> None: ...
    def boot(self) -> None: ...
    def upsert_node(self, node_id: str, node_type: str, payload: dict) -> None: ...
    def upsert_edge(self, edge_type: str, from_node: str, to_node: str, payload: dict | None = None) -> int: ...
    def log_tool_call(self, tool: str, envelope: dict) -> None: ...
    def query(self, cypher: str, params: dict | None = None) -> list[dict]: ...
    def close(self) -> None: ...
```

- Default `db_path` resolves to `context/_store/ontology.db`.
- `boot()` is idempotent; applies `schema.sql` if file is new.
- `upsert_node` uses `INSERT ... ON CONFLICT(id) DO UPDATE SET payload = excluded.payload, updated_at = ?`.
- `upsert_edge` upserts on `(type, from_node, to_node)`; returns row id.
- `log_tool_call` is append-only; provenance never mutates.
- Each call wraps a single SQLite transaction.

### 2. Cypher-compatible query subset

`context/_store/cypher_adapter.py` exposes:

```python
def translate(cypher: str, params: dict | None = None) -> tuple[str, list]: ...
```

Returns parameterized SQL + positional args. `Store.query` calls it
and executes against `nodes` / `edges`. Supported dialect:

- `MATCH (n:NodeType) RETURN n`
- `MATCH (n:NodeType {prop: $val}) RETURN n`
- `MATCH (a)-[:EDGE_TYPE]->(b) RETURN a, b`
- `MATCH (a:A {prop: $val})-[:EDGE_TYPE]->(b:B) RETURN a, b`
- `LIMIT N` clause appended to any of the above.

**Out of scope:** variable-length paths, `WHERE`, aggregation, `WITH`,
`OPTIONAL MATCH`, edge-payload filters, multi-hop chains beyond a
single `(a)-[:E]->(b)`.

### 3. PreToolUse hook

`context/_hooks/pre_tool_use.py` exposes:

```python
def validate(tool_name: str, args: dict) -> dict:
    """Return {ok: bool, errors: list[str]}."""
```

- If `tool_name` matches `mcp__*_write_*` AND `args.path` ends in
  `manifest.toml`: dispatch on path prefix (`agentic/` →
  `agentic-cell.schema.json`, `workflow/` → `workflow-cell.schema.json`,
  `context/` → `context-cell.schema.json`). Parse TOML, validate.
- If `args.path` ends in `.gate.yaml` or matches
  `workflow/*/gates/*.yaml`, validate against `gate.schema.json`.
- If `args.path` ends in `.md` AND `args.content` starts with `---`,
  parse YAML frontmatter and validate against the frontmatter schema
  selected by `frontmatter.type`. Base layer ships only the universal
  shape (slug/type/status/owner/created/updated/summary/affects);
  row-specific frontmatter validation attaches later.
- Unknown tools: return `{ok: True, errors: []}` (silence is
  non-blocking).

### 4. PostToolUse hook

`context/_hooks/post_tool_use.py` exposes:

```python
def ingest(tool_name: str, envelope: dict) -> None: ...
```

1. Log envelope to `tools_call_log` regardless of `ok` value.
   Provenance is unconditional.
2. If `envelope.ok is False`, return.
3. If `envelope.data.artefact_ref` present: read sidecar JSON,
   validate against `sidecar.schema.json`, upsert node
   `(<row>/Artefact/<sha256>, type="Artefact", payload=sidecar)`.
4. For each entry in `sidecar.derived_from`, upsert edge
   `(DERIVED_FROM, artefact_node, entry)`.
5. If `sidecar.satisfies_phase` set, upsert edge
   `(SATISFIES_PHASE, artefact_node, phase:<row>/<phase_id>)`.
6. If `envelope.data.emitted_edges` is a list (spec 05), upsert each
   edge as-typed. This is the workflow-runner-driven path.
7. The binary at `sidecar.artefact_path` is NEVER read.

### 5. Hook execution layer (Context Q2 resolved)

Default execution model: **Python decorators applied by the agentic
harness during tool registration.** Agentic imports
`context._hooks.pre_tool_use.validate` and
`context._hooks.post_tool_use.ingest` and wraps each registered
FastMCP tool. The context column ships only the callables; wiring is
owned by agentic (spec 06). MCP-native middleware is deferred; the
same callables move there with no signature change if FastMCP later
exposes middleware.

### 6. Schemas exported

All six JSON Schemas land verbatim from their source specs:

| File | Source | `$id` |
|---|---|---|
| `tool_result.schema.json` | spec 02 | `tag:agency-system.local,2026:schema:shared/tool_result` |
| `agentic-cell.schema.json` | spec 01 | `tag:agency-system.local,2026:schema:agentic-cell` |
| `workflow-cell.schema.json` | spec 01 | `tag:agency-system.local,2026:schema:workflow-cell` |
| `context-cell.schema.json` | spec 01 | `tag:agency-system.local,2026:schema:context-cell` |
| `sidecar.schema.json` | spec 03 | `tag:agency-system.local,2026:schema:shared/sidecar` |
| `gate.schema.json` | spec 05 | `tag:agency-system.local,2026:schema:shared/gate` |

Schemas are public — any column reads them by path. No in-memory
schema registry; readers re-load from disk on cold boot.

## SQL schema

Full contents of `context/_store/schema.sql`:

```sql
-- context/_store/schema.sql
-- Ontology + provenance store for the 3xN matrix.
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS nodes (
    id          TEXT PRIMARY KEY,
    type        TEXT NOT NULL,
    payload     JSON,
    created_at  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    updated_at  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);
CREATE INDEX IF NOT EXISTS idx_nodes_type ON nodes(type);

CREATE TABLE IF NOT EXISTS edges (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    type        TEXT NOT NULL,
    from_node   TEXT NOT NULL,
    to_node     TEXT NOT NULL,
    payload     JSON,
    created_at  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    UNIQUE(type, from_node, to_node)
);
CREATE INDEX IF NOT EXISTS idx_edges_type      ON edges(type);
CREATE INDEX IF NOT EXISTS idx_edges_from_node ON edges(from_node);
CREATE INDEX IF NOT EXISTS idx_edges_to_node   ON edges(to_node);

CREATE TABLE IF NOT EXISTS tools_call_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    tool        TEXT NOT NULL,
    envelope    JSON NOT NULL,
    called_at   TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);
CREATE INDEX IF NOT EXISTS idx_tools_call_log_tool ON tools_call_log(tool);
```

Foreign keys are NOT declared on `edges.from_node` / `to_node`. The
graph accepts forward references — an edge can land before the node
it points at exists.

## Cypher subset

**Single label + LIMIT:**

```cypher
MATCH (n:Artefact) RETURN n LIMIT 5
```
```sql
SELECT id, type, payload FROM nodes WHERE type = ? LIMIT ?;
-- params: ["Artefact", 5]
```

**Label + property:**

```cypher
MATCH (n:Phase {name: $name}) RETURN n
```
```sql
SELECT id, type, payload FROM nodes
WHERE type = ? AND json_extract(payload, '$.name') = ?;
-- params: ["Phase", <name>]
```

**Single-hop traversal:**

```cypher
MATCH (a:Artefact)-[:DERIVED_FROM]->(b) RETURN a, b
```
```sql
SELECT a.id AS a_id, a.type AS a_type, a.payload AS a_payload,
       b.id AS b_id, b.type AS b_type, b.payload AS b_payload
FROM edges e
JOIN nodes a ON a.id = e.from_node
JOIN nodes b ON b.id = e.to_node
WHERE e.type = ? AND a.type = ?;
-- params: ["DERIVED_FROM", "Artefact"]
```

Rows return as `list[dict]`. Multi-node rows expose `<name>_id`,
`<name>_type`, `<name>_payload` per binding (`a_*`, `b_*`).

## Worked example

Cold boot, no rows present:

1. Process imports `context._store.sqlite.Store`. `Store().boot()`
   creates `context/_store/ontology.db` with three tables.
2. The agentic harness imports `context._hooks` and decorates a
   synthetic tool `mcp__test_write_manifest`.
3. The harness invokes the tool with
   `args = {"path": "agentic/test/manifest.toml", "content": "<toml>"}`.
   PreToolUse fires, detects the `manifest.toml` filename + `agentic/`
   prefix, validates against `agentic-cell.schema.json`. If `[skills]`
   is missing it returns `{ok: False, errors: [...]}`; the harness
   short-circuits and the tool body never runs.
4. With a valid manifest the body returns
   `{"ok": true, "data": {"artefact_ref": "result/test/.meta/foo.mp3.meta.json"}, "warnings": [], "next_suggested_tools": []}`.
5. PostToolUse fires: inserts a `tools_call_log` row; reads the
   sidecar; validates against `sidecar.schema.json`; upserts node
   `test/Artefact/<sha256>`; emits one `DERIVED_FROM` edge per entry;
   if `satisfies_phase` set, emits a `SATISFIES_PHASE` edge from the
   artefact to `phase:test/<id>`.
6. A subsequent
   `MATCH (a:Artefact)-[:DERIVED_FROM]->(b) RETURN a, b`
   returns the new edge in a single SQL round-trip.

## Acceptance criteria

```gherkin
Scenario: Store boots and creates the database
  Given an empty `context/_store/` directory
  When `Store().boot()` is invoked
  Then `context/_store/ontology.db` exists
  And tables `nodes`, `edges`, `tools_call_log` exist
  And the required indexes exist
  And re-invoking `boot()` is a no-op

Scenario: PreToolUse rejects an invalid agentic manifest
  Given a write call targeting `agentic/test/manifest.toml`
  And the TOML body omits the required `[skills]` table
  When `pre_tool_use.validate(tool_name, args)` runs
  Then it returns `{ok: False, errors: [...]}`
  And at least one error mentions the missing required key

Scenario: PostToolUse logs every envelope
  Given a tool returns any well-formed envelope
  When `post_tool_use.ingest(tool_name, envelope)` runs
  Then a row in `tools_call_log` records `(tool, envelope, called_at)`

Scenario: Sidecar reference materializes an Artefact node
  Given an envelope has `data.artefact_ref = "result/music/.meta/whispers/master.mp3.meta.json"`
  And the sidecar file validates against `sidecar.schema.json`
  When `post_tool_use.ingest` runs
  Then a node `music/Artefact/<sha256>` exists
  And one DERIVED_FROM edge exists per entry in `sidecar.derived_from`

Scenario: SATISFIES_PHASE edge from gate emission
  Given an envelope has `data.emitted_edges = [{type: "SATISFIES_PHASE", from: "music/Artefact/abc", to: "phase:music/02"}]`
  When `post_tool_use.ingest` runs
  Then exactly one row in `edges` has `(type, from_node, to_node) = ("SATISFIES_PHASE", "music/Artefact/abc", "phase:music/02")`
  And the upsert is idempotent across re-runs

Scenario: JSON Schemas validate sample manifests from spec 01
  Given the three sample manifests in `vision/specs/01-cell-manifest.md`
  When each is validated against its matching `*-cell.schema.json`
  Then all three pass without error

Scenario: Cypher single-hop translates to SQL
  Given the query `MATCH (a:Artefact)-[:DERIVED_FROM]->(b) RETURN a, b`
  When `cypher_adapter.translate` runs
  Then the emitted SQL joins `edges` with `nodes` twice
  And the parameter list contains `["DERIVED_FROM", "Artefact"]`

Scenario: Unsupported Cypher raises a clear error
  Given the query `MATCH (a)-[:E*1..3]->(b) RETURN a`
  When `cypher_adapter.translate` runs
  Then it raises `NotImplementedError` mentioning "variable-length path"
```

## `affects:` allow-list for the implementation PR

The Jules session writes ONLY these paths:

```
context/__init__.py
context/_store/__init__.py
context/_store/sqlite.py
context/_store/schema.sql
context/_store/cypher_adapter.py
context/_hooks/__init__.py
context/_hooks/pre_tool_use.py
context/_hooks/post_tool_use.py
context/_shared/schemas/tool_result.schema.json
context/_shared/schemas/agentic-cell.schema.json
context/_shared/schemas/workflow-cell.schema.json
context/_shared/schemas/context-cell.schema.json
context/_shared/schemas/sidecar.schema.json
context/_shared/schemas/gate.schema.json
tests/context/test_store.py
tests/context/test_hooks.py
tests/context/test_cypher_subset.py
tests/context/test_schemas.py
```

Any path outside this list — `agentic/`, `workflow/`, `vision/`,
existing repo files — is out of scope. If the session feels pressure
to edit another column, it must stop with a friction note.

## Out of scope

- Template rendering (pandoc / Jinja) — later spec.
- Full Cypher coverage — only the documented single-hop subset.
- Hot reload of schemas — re-read on cold boot only.
- Row-specific frontmatter schemas — arrive with the row scaffold.
- In-memory graph caching — every query hits SQLite.
- Cross-row dispatch — owned by spec 09 (follow-up).

## Dependencies

- `vision/specs/01-cell-manifest.md` — source of the three
  `*-cell.schema.json` shapes validated by PreToolUse.
- `vision/specs/02-tool-result-envelope.md` — source of
  `tool_result.schema.json` and the envelope shape PostToolUse logs.
- `vision/specs/03-sidecar-metadata.md` — source of
  `sidecar.schema.json` and the ingest path triggered by
  `data.artefact_ref`.
- `vision/specs/05-gate-yaml.md` — source of `gate.schema.json` and
  the `emitted_edges` payload PostToolUse upserts into `edges`.
