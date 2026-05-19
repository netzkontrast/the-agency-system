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

## Purpose

This spec defines the implementation contract for the **context column
base layer** at `context/` (repo root, NOT under `vision/`). It is the
target a Jules session executes to build the context column's
infrastructure: the SQLite ontology store, the Pre/PostToolUse hook
callables, and the cross-cutting JSON Schemas in `_shared/schemas/`.

The context column owns the schemas the rest of the matrix validates
against. Agentic and workflow base layers (specs 06 and 07) **import**
these schemas by path — they do NOT redefine them. This is the
resolution to the Phase 3 schema-locality friction: schemas live in
exactly one canonical place; anyone needing isomorphism reads from
there.

This spec also resolves Phase 3 **Context Q2** (hook execution layer):
hooks are exposed as plain Python callables in `context._hooks`. The
agentic harness applies them as decorators during tool registration —
the context column ships the logic, not the wiring.

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

Row-specific cells (`context/<row>/`) do NOT land in this PR — they
arrive through the meta-row pipeline. This base layer must boot with
zero rows present.

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
- `boot()` is idempotent: applies `schema.sql` if the file is new.
- `upsert_node` uses `INSERT ... ON CONFLICT(id) DO UPDATE SET payload = excluded.payload, updated_at = ?`.
- `upsert_edge` upserts on `(type, from_node, to_node)` and returns the row id.
- `log_tool_call` is append-only; provenance must never be mutated.
- All writes are wrapped in a single SQLite transaction per call.

### 2. Cypher-compatible query subset

`context/_store/cypher_adapter.py` exposes:

```python
def translate(cypher: str, params: dict | None = None) -> tuple[str, list]: ...
```

Returns a parameterized SQL string and its positional argument list.
The `Store.query` method calls this then executes against `nodes` /
`edges`.

Supported dialect (initial slice — additions land in follow-up PRs):

- `MATCH (n:NodeType) RETURN n`
- `MATCH (n:NodeType {prop: $val}) RETURN n`
- `MATCH (a)-[:EDGE_TYPE]->(b) RETURN a, b`
- `MATCH (a:NodeTypeA {prop: $val})-[:EDGE_TYPE]->(b:NodeTypeB) RETURN a, b`
- `LIMIT N` clause appended to any of the above.

**Out of scope:** variable-length paths (`*1..3`), `WHERE` clauses,
aggregation (`count`, `collect`), `WITH`, `OPTIONAL MATCH`, edge
payload filters, multi-hop chains beyond a single `(a)-[:E]->(b)`.

### 3. PreToolUse hook

`context/_hooks/pre_tool_use.py` exposes:

```python
def validate(tool_name: str, args: dict) -> dict:
    """Return {ok: bool, errors: list[str]}."""
```

Behavior:

- If `tool_name` matches `mcp__*_write_*` AND `args` contains a `path`
  that ends in `manifest.toml`, dispatch on the path prefix:
  `agentic/` → `agentic-cell.schema.json`, `workflow/` →
  `workflow-cell.schema.json`, `context/` → `context-cell.schema.json`.
  Parse the TOML, validate, accumulate errors.
- If `args` contains a `path` ending in `.gate.yaml` or matching
  `workflow/*/gates/*.yaml`, validate against `gate.schema.json`.
- If `args` contains a `path` ending in `.md` AND `args.content`
  starts with `---`, parse the YAML frontmatter and validate it
  against the frontmatter schema selected by `frontmatter.type`.
  Frontmatter schemas live alongside their owning cell; the base layer
  ships the universal shape only (slug/type/status/owner/created/
  updated/summary/affects). Row-specific frontmatter validation
  attaches once `context/<row>/` lands.
- Return `{ok: True, errors: []}` for any tool the hook does not
  recognise — silence is non-blocking.

### 4. PostToolUse hook

`context/_hooks/post_tool_use.py` exposes:

```python
def ingest(tool_name: str, envelope: dict) -> None: ...
```

Behavior:

1. Log the envelope to `tools_call_log` regardless of `ok` value.
   Provenance is unconditional.
2. If `envelope.ok is False`, return.
3. If `envelope.data.artefact_ref` is present, read the sidecar JSON
   from that path. Validate against `sidecar.schema.json`. Upsert a
   node `(<row>/Artefact/<sha256>, type="Artefact", payload=sidecar)`.
4. For each entry in `sidecar.derived_from`, upsert an edge
   `(DERIVED_FROM, artefact_node, derived_from_entry)`.
5. If `sidecar.satisfies_phase` is set, upsert an edge
   `(SATISFIES_PHASE, artefact_node, phase:<row>/<phase_id>)`.
6. If `envelope.data.emitted_edges` is a list (spec 05), upsert each
   edge as-typed. This is the workflow-runner-driven path.
7. The binary at `sidecar.artefact_path` is NEVER read.

### 5. Hook execution layer (Context Q2 resolved)

Default execution model: **Python decorators applied by the agentic
harness during tool registration**. The agentic harness imports
`context._hooks.pre_tool_use.validate` and
`context._hooks.post_tool_use.ingest` and wraps each registered
FastMCP tool. The context column ships only the callables — wiring
is owned by agentic (spec 06).

MCP-native middleware is deferred. If FastMCP gains middleware support
the same callables will move there with no signature change.

### 6. Schemas exported

All six JSON Schemas land as files in `_shared/schemas/`. Each is the
canonical instance derived verbatim from its source spec:

| File | Source | `$id` |
|---|---|---|
| `tool_result.schema.json` | spec 02 | `tag:agency-system.local,2026:schema:shared/tool_result` |
| `agentic-cell.schema.json` | spec 01 | `tag:agency-system.local,2026:schema:agentic-cell` |
| `workflow-cell.schema.json` | spec 01 | `tag:agency-system.local,2026:schema:workflow-cell` |
| `context-cell.schema.json` | spec 01 | `tag:agency-system.local,2026:schema:context-cell` |
| `sidecar.schema.json` | spec 03 | `tag:agency-system.local,2026:schema:shared/sidecar` |
| `gate.schema.json` | spec 05 | `tag:agency-system.local,2026:schema:shared/gate` |

Schemas are public — any column reads them by path. There is no
in-memory schema registry; readers re-load from disk on cold boot.

## SQL schema

Full contents of `context/_store/schema.sql`:

```sql
-- context/_store/schema.sql
-- Ontology + provenance store for the 3xN matrix.
-- Idempotent: every CREATE uses IF NOT EXISTS.

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
graph must accept forward references — an edge can land before the
node it points at exists. The PostToolUse ingest order does not
guarantee node-before-edge.

## Cypher subset

Each example shows the Cypher input and the SQL the adapter emits.

**Single label:**

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
SELECT
  a.id AS a_id, a.type AS a_type, a.payload AS a_payload,
  b.id AS b_id, b.type AS b_type, b.payload AS b_payload
FROM edges e
JOIN nodes a ON a.id = e.from_node
JOIN nodes b ON b.id = e.to_node
WHERE e.type = ? AND a.type = ?;
-- params: ["DERIVED_FROM", "Artefact"]
```

**Typed both ends:**

```cypher
MATCH (a:Artefact {sha256: $hash})-[:SATISFIES_PHASE]->(b:Phase) RETURN a, b
```

```sql
SELECT
  a.id AS a_id, a.type AS a_type, a.payload AS a_payload,
  b.id AS b_id, b.type AS b_type, b.payload AS b_payload
FROM edges e
JOIN nodes a ON a.id = e.from_node
JOIN nodes b ON b.id = e.to_node
WHERE e.type = ? AND a.type = ? AND b.type = ?
  AND json_extract(a.payload, '$.sha256') = ?;
-- params: ["SATISFIES_PHASE", "Artefact", "Phase", <hash>]
```

Rows return as `list[dict]`. Multi-node rows expose `n_id`,
`n_type`, `n_payload` per matched binding name (`a_*`, `b_*`).

## Worked example

Cold boot, no rows present:

1. Process imports `context._store.sqlite.Store`. `Store().boot()`
   creates `context/_store/ontology.db` with the three tables.
2. The agentic harness imports `context._hooks` and decorates a
   synthetic tool `mcp__test_write_manifest`.
3. The harness invokes the tool with
   `args = {"path": "agentic/test/manifest.toml", "content": "<toml>"}`.
   PreToolUse fires first. The hook detects the `manifest.toml`
   filename + `agentic/` prefix, validates against
   `agentic-cell.schema.json`. If `[skills]` is missing, the hook
   returns `{ok: False, errors: ["agentic-cell: missing [skills]"]}`,
   the harness short-circuits and does not invoke the tool body.
4. With a valid manifest the body runs and returns
   `{"ok": true, "data": {"artefact_ref": "result/test/.meta/foo.mp3.meta.json"}, "warnings": [], "next_suggested_tools": []}`.
5. PostToolUse fires. It (a) inserts a row into `tools_call_log`,
   (b) reads the sidecar, validates against `sidecar.schema.json`,
   (c) upserts node `test/Artefact/<sha256>`, (d) emits one
   `DERIVED_FROM` edge per entry, (e) if `satisfies_phase` is set,
   emits `SATISFIES_PHASE` from the artefact to `phase:test/<id>`.
6. A subsequent `MATCH (a:Artefact)-[:DERIVED_FROM]->(b) RETURN a, b`
   query returns the new edge in a single SQL round-trip.

## Acceptance criteria

```gherkin
Scenario: Store boots and creates the database
  Given an empty `context/_store/` directory
  When `Store().boot()` is invoked
  Then `context/_store/ontology.db` exists
  And tables `nodes`, `edges`, `tools_call_log` exist
  And the four required indexes exist
  And re-invoking `boot()` is a no-op

Scenario: PreToolUse rejects an invalid agentic manifest
  Given a write call targeting `agentic/test/manifest.toml`
  And the TOML body omits the required `[skills]` table
  When `pre_tool_use.validate(tool_name, args)` runs
  Then it returns `{ok: False, errors: [...]}`
  And at least one error mentions the missing required key

Scenario: PreToolUse passes a valid context-cell manifest
  Given a write call targeting `context/music/manifest.toml`
  And the TOML body conforms to `context-cell.schema.json`
  When `pre_tool_use.validate` runs
  Then it returns `{ok: True, errors: []}`

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
  Given the three sample manifests in `vision/specs/01-cell-manifest.md` (agentic/music, workflow/music, context/music)
  When each is validated against its matching `*-cell.schema.json`
  Then all three pass without error

Scenario: Cypher single-hop translates to SQL
  Given the query `MATCH (a:Artefact)-[:DERIVED_FROM]->(b) RETURN a, b`
  When `cypher_adapter.translate` runs
  Then the emitted SQL joins `edges` with `nodes` twice
  And the parameter list contains `["DERIVED_FROM", "Artefact"]`
  And executing it against a populated store returns the expected rows

Scenario: Unsupported Cypher raises a clear error
  Given the query `MATCH (a)-[:E*1..3]->(b) RETURN a`
  When `cypher_adapter.translate` runs
  Then it raises `NotImplementedError` mentioning "variable-length path"
```

## `affects:` allow-list for the implementation PR

The Jules session that executes this spec writes ONLY these paths:

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
to edit another column, it must stop with a friction note instead.

## Out of scope

- Template rendering (pandoc / Jinja) — that's a later spec.
- Full Cypher coverage — only the documented single-hop subset.
- Hot reload of schemas — schemas re-read on cold boot only.
- Row-specific frontmatter schemas (`context/<row>/schemas/*.json`) —
  arrive with the row scaffold pipeline.
- In-memory graph caching — every query hits SQLite. Sub-millisecond
  latency at thousands of nodes is acceptable per `ONTOLOGY.md`.
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
