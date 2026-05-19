---
slug: spec-08-context-base-v1
type: impl-spec
status: ready
owner: claude
created: 2026-05-19
updated: 2026-05-19
summary: v1 rewrite of the context base layer at `context/` (repo root). Locks GraphQLite as the single graph driver (no raw-SQLite fallback), specifies the artifact-driver registry (`context/_drivers/__init__.py` exposes `REGISTRY: dict[str, ArtefactDriver]`, drivers self-register on import), promotes the renamed `artefact-node.schema.json` to canonical, and pins the graph-bootstrap behaviour (`Store.boot()` idempotent, opens-or-creates `ontology.db`, seeds zero nodes — rows materialize via the meta-row scaffolder). Supersedes `vision/specs/08-context-base.md`.
affects:
  - vision/specs/08-context-base-v1.md
  - context/_store/sqlite.py
  - context/_drivers/__init__.py
  - context/_drivers/fs.py
  - context/_drivers/protocol.py
  - context/_hooks/post_tool_use.py
  - context/_shared/schemas/artefact-node.schema.json
depends_on:
  - vision/specs/01-cell-manifest.md
  - vision/specs/02-tool-result-envelope.md
  - vision/specs/05-gate-yaml.md
  - vision/03-architecture.md
referenced_by:
  - vision/specs/07-workflow-base-v1.md
supersedes:
  - vision/specs/08-context-base.md
  - vision/specs/03-sidecar-metadata.md
---

# Spec 08-v1 — Context Base Layer (GraphQLite-only, driver registry)

> **STATUS — 2026-05-19**: ✅ **Ready for review.** Locks the open
> architectural decisions left dangling after PR #149 + the N0 + N2
> phases (PR #155): GraphQLite is the single graph substrate (raw-SQLite
> fallback removed), drivers register through an importable `REGISTRY`,
> the Artefact node schema (renamed in N2 from `sidecar.schema.json` →
> `artefact-node.schema.json`) is the canonical form, and graph
> bootstrap behaviour is pinned. **Supersedes** the v0 spec at
> `vision/specs/08-context-base.md` and **retires the deprecated
> `vision/specs/03-sidecar-metadata.md` file-on-disk format**.

## Purpose

The v0 context base (PR #149) shipped a `Store` class with two code
paths: GraphQLite when its native extension loads, raw-SQLite otherwise.
The fallback wrote tables (`nodes`, `edges`, `from_node`, `to_node`)
that diverge from GraphQLite's schema (`source_id`, `target_id`,
`node_labels`, `node_props_*`). Tests that assert against the fallback
columns silently fail under a real install (see the two
known-pre-existing failures in `tests/context/test_hooks.py`). The
fallback also lets the system limp along under a partial install,
which violates the "one engine, one graph" tenet of
`vision/03-architecture.md`.

This spec **removes the fallback**, **pins GraphQLite as the lone
substrate**, and **lifts the driver registry** from an implicit
convention to a documented `context/_drivers/__init__.py` surface that
PostToolUse and any future ingest path can rely on.

## What changes vs v0

| v0 (spec 08)                                              | v1 (this spec)                                                                  |
|---|---|
| GraphQLite + raw-SQLite fallback                          | GraphQLite only; `Store.boot` raises a clear error if the extension is absent |
| `sidecar.schema.json` (file-on-disk artefact metadata)    | `artefact-node.schema.json` (Artefact node payload; no `.meta.json` on disk)  |
| Artifact-driver Protocol declared; no registry            | `context/_drivers/__init__.py` exposes `REGISTRY: dict[str, ArtefactDriver]`; `fs` self-registers on import |
| PostToolUse hard-codes the `fs` driver                    | PostToolUse resolves the driver from `Artefact.artifact_driver` via `REGISTRY` |
| `Store.upsert_node(node_id, node_type, payload)`          | `Store.upsert_node(node_id, payload, *, label)` (GraphQLite-native ordering)  |
| `Store.upsert_edge(edge_type, from, to, payload)`         | `Store.upsert_edge(from, to, payload, *, rel_type)` (GraphQLite-native)       |
| `context/_hooks/pre_tool_use.validate`                    | `validate_envelope_in` (renamed for role clarity; PreToolUse envelope-in)     |
| Hand-written `schema.sql` + `cypher_adapter.py`           | GraphQLite owns the schema; the hand-written `cypher_adapter` retires (dead) |

The signature flips and the rename to `validate_envelope_in` already
shipped in PR #155 (N0). The Artefact-node schema rename + canonical
`artifact_driver` / `driver_pointer` fields already shipped in PR #155
(N2). This spec **locks** those choices and adds the remaining v1
mandates (driver REGISTRY, drop the fallback, retire `cypher_adapter`).

## Folder layout

```
context/
├── __init__.py
├── _store/
│   ├── __init__.py
│   ├── sqlite.py                  # Store(): GraphQLite only — no fallback
│   └── ontology.db                # gitignored; created by Store.boot()
├── _hooks/
│   ├── __init__.py
│   ├── pre_tool_use.py            # validate_envelope_in()
│   └── post_tool_use.py           # ingest(); resolves driver via REGISTRY
├── _drivers/
│   ├── __init__.py                # exports REGISTRY: dict[str, ArtefactDriver]
│   ├── protocol.py                # ArtefactDriver Protocol
│   └── fs.py                      # FSArtefactDriver — the one mandatory v1 driver
└── _shared/
    └── schemas/
        ├── tool_result.schema.json
        ├── agentic-cell.schema.json
        ├── workflow-cell.schema.json
        ├── context-cell.schema.json
        ├── artefact-node.schema.json   (canonical name as of N2)
        └── gate.schema.json
```

`schema.sql`, `cypher_adapter.py`, and the raw-SQLite fallback branches
of `sqlite.py` are removed by the v1 implementation PR. GraphQLite owns
the table layout; Cypher goes straight through `Graph.query`.

## Functional requirements

### FR1 — GraphQLite is the only graph substrate

`context/_store/sqlite.py::Store`:

```python
class Store:
    def __init__(self, db_path: str | None = None) -> None: ...
    def boot(self) -> None:
        """Open or create ontology.db. Raises StoreUnavailable
        if the GraphQLite extension cannot load."""
    def upsert_node(self, node_id: str, payload: dict, *, label: str) -> None: ...
    def upsert_edge(self, from_node: str, to_node: str, payload: dict | None = None, *, rel_type: str) -> None: ...
    def log_tool_call(self, tool: str, envelope: dict) -> None: ...
    def query(self, cypher: str, params: dict | None = None) -> list[dict]: ...
    def close(self) -> None: ...
```

- `Store.boot()` is **idempotent** — calling it twice is harmless;
  the second call reuses the open `Graph` instance.
- `boot()` calls `Graph(self.db_path)` exactly once. If the extension
  fails to load (`RuntimeError` mentioning "SQLite extension loading
  not available" or any other initialization failure), the method
  raises a `StoreUnavailable` exception with the original cause
  chained. The fallback in `_get_graph()` that returned `None` and
  switched to raw SQLite is **deleted**, including every `if g:` /
  `else:` branch in `upsert_node`, `upsert_edge`, and `query`.
- Class invariant: outside of test monkeypatching, a single `Store`
  instance per FastMCP process is the norm. Multiple instances are
  legal (each holds its own `Graph` handle) but discouraged.
- The `db_path` default resolves to `context/_store/ontology.db`
  (relative to the repo root, not the module path) so the runtime
  doesn't fight the cwd switching tests do.

`StoreUnavailable` lives at the top of `sqlite.py` as a module-level
exception. The FastMCP bootloader catches it and surfaces a fix-hint
("Install graphqlite: pip install graphqlite") rather than panicking.

### FR2 — Graph bootstrap is "open or create, seed nothing"

`Store.boot()` MUST NOT seed any nodes. The graph starts empty on a
fresh install; rows materialize through the meta-row scaffolder
(`workflow/meta/`, spec 07-v1). This is the inversion of "schema-first
ORM with seed data" — schemas are JSON in `context/_shared/schemas/`,
the graph is a substrate.

Concretely:

- Cell, Phase, Row, Continuation nodes appear when
  `_run_meta_scaffold` writes them (spec 07-v1 FR5).
- Artefact nodes appear when PostToolUse ingests an envelope's
  `data.artefact_metadata`.
- Tool-call log rows appear unconditionally per tool call (provenance).

Nothing else. Cold-boot evidence: a brand-new `ontology.db` immediately
after `Store().boot()` contains the GraphQLite-managed metadata tables
(nodes, edges, node_labels, node_props_*, edge_props_*) all empty, plus
the system `tools_call_log` table empty until the first hook ingest.

### FR3 — Driver REGISTRY

`context/_drivers/__init__.py` exposes a public registry:

```python
from typing import Protocol
from .protocol import ArtefactDriver
from .fs import FSArtefactDriver

REGISTRY: dict[str, ArtefactDriver] = {}

def register(key: str, driver: ArtefactDriver) -> None:
    """Self-registration hook. Raises KeyError on duplicate key
    unless `os.environ.get('AGENCY_DRIVER_OVERRIDE')` is set."""
    if key in REGISTRY and not os.environ.get("AGENCY_DRIVER_OVERRIDE"):
        raise KeyError(f"driver {key!r} already registered")
    REGISTRY[key] = driver

# `fs` is the one mandatory v1 driver — register on import.
register("fs", FSArtefactDriver())
```

Future drivers (`repo`, `s3`, `http`, `drive`) are introduced by adding
a new module under `context/_drivers/` whose import calls
`register(...)` once. They are NOT part of v1; this spec defines the
extension surface only.

`Artefact.artifact_driver` (a payload field on the node, see FR5)
selects which driver resolves bytes. PostToolUse and any future
`get_bytes` / `put_bytes` callsite looks up via:

```python
from context._drivers import REGISTRY
driver = REGISTRY[artefact_node["artifact_driver"]]
```

Unknown driver keys raise `KeyError` with the available keys listed in
the message. Drivers are never instantiated by callers; the registry
holds singletons.

### FR4 — PostToolUse resolves drivers via REGISTRY

`context/_hooks/post_tool_use.ingest` becomes:

```python
def ingest(tool_name: str, envelope: dict) -> None:
    store = Store()
    store.boot()
    store.log_tool_call(tool_name, envelope)
    if not envelope.get("ok"):
        return

    metadata = envelope.get("data", {}).get("artefact_metadata")
    if not metadata or not isinstance(metadata, dict):
        # No artefact emitted; just provenance.
        _ingest_emitted_edges(envelope.get("data", {}).get("emitted_edges"))
        return

    # Validate against the canonical Artefact-node schema.
    jsonschema.validate(instance=metadata, schema=_artefact_schema())

    node_id = _derive_artefact_id(metadata)
    store.upsert_node(node_id, metadata, label="Artefact")

    # Resolve the driver and (if raw bytes are inlined) persist.
    driver_key = metadata.get("artifact_driver")
    if driver_key and "raw_bytes" in metadata:
        driver = REGISTRY[driver_key]   # KeyError surfaces a fix-hint
        driver.put_bytes(metadata, metadata["raw_bytes"])
        del metadata["raw_bytes"]

    for entry in metadata.get("derived_from", []):
        store.upsert_edge(node_id, entry, rel_type="DERIVED_FROM")

    satisfies = metadata.get("satisfies_phase")
    if satisfies:
        row = _derive_row(metadata)
        store.upsert_edge(node_id, f"phase:{row}/{satisfies}", rel_type="SATISFIES_PHASE")

    _ingest_emitted_edges(envelope.get("data", {}).get("emitted_edges"))
```

The "if path + raw_bytes are both present, ask the driver to write"
heuristic from v0 is replaced by **the driver_key gate**. Without
`artifact_driver` the bytes path is skipped — the node still lands.

`_artefact_schema()` reads
`context/_shared/schemas/artefact-node.schema.json` (the N2 rename).
`_derive_artefact_id` and `_derive_row` are unchanged from v0.

### FR5 — Artefact node schema is canonical

`context/_shared/schemas/artefact-node.schema.json` (renamed in N2) is
the canonical Artefact-node payload schema. Required fields:

- `content_type`, `sha256`, `size_bytes`, `created_at`, `produced_by`,
  `derived_from` — carried over from spec 03.

Optional fields canonical in v1:

- `artifact_driver` — key into `REGISTRY`. Optional **only** because
  some artefacts (e.g., pure provenance nodes that derive from other
  artefacts but don't have their own bytes) never need driver
  resolution. When present, it MUST match a registered driver at
  PostToolUse time.
- `driver_pointer` — driver-specific bytes pointer; the `fs` driver
  uses it as a path string, `s3` would use it as a key, and so on.
- `artefact_path` — LEGACY compatibility field, retained for the `fs`
  driver's transitional reads of old nodes. New writes set
  `driver_pointer` instead.
- `satisfies_phase` — emits a `SATISFIES_PHASE` edge when present
  (unchanged).

The previous `sidecar.schema.json` file is **gone** as of N2 PR #155
(git-renamed; no lingering file). `vision/specs/03-sidecar-metadata.md`
is annotated DEPRECATED at the top and remains in the tree as
archeology only.

### FR6 — PreToolUse name + validator

`context/_hooks/pre_tool_use.py` exposes `validate_envelope_in(tool_name, args)`
(renamed in N0 PR #155). Behaviour is unchanged from v0: manifest-write
tools validate the TOML body against the matching `*-cell` schema;
unrecognized tools pass through. The rename makes the role explicit and
matches the import in `agentic/_bootloader.py`.

### FR7 — Cypher access uses GraphQLite directly

`Store.query(cypher, params)` is a thin pass-through to
`Graph.query(cypher, params=params)`. The hand-rolled
`cypher_adapter.py` is **deleted** by the v1 PR. Callers (gate
evaluator, PostToolUse, future graph walkers in spec 07-v1) write
Cypher and get rows back. The Cypher dialect available is whatever
GraphQLite supports; no project-specific translation layer.

Examples (verbatim from spec 07-v1 §FR3 + §FR4):

```cypher
MATCH (p:Phase {row: $row, phase_id: $pid}) RETURN p
MATCH (c:Continuation {id: $id}) RETURN c
MATCH (n:Artefact) WHERE n.sha256 = $hash RETURN n
```

### FR8 — Provenance log is append-only

`Store.log_tool_call(tool, envelope)` writes one row to a
GraphQLite-side `tools_call_log` virtual table (created on first call
via `CREATE TABLE IF NOT EXISTS` in `Store.boot`'s extension prelude).
The table holds `(tool, envelope, called_at)`. Provenance never
mutates; rows accumulate. Storage is the system's concern, not the
user's — these rows do not surface in `result/` directories or driver
exports.

## Worked example — cold boot of an empty install

1. The FastMCP process imports `context._store.sqlite.Store`. Nothing
   touches disk.
2. The agentic bootloader (`agentic/_bootloader.boot`) constructs a
   `Store()` instance and calls `boot()`. GraphQLite opens
   `context/_store/ontology.db` (creating an empty file via SQLite's
   create-on-write behaviour, then initialising GraphQLite's metadata
   tables on first node/edge upsert).
3. The driver REGISTRY is populated by `context._drivers.__init__`'s
   import side-effects — `fs` self-registers.
4. `discover()` finds zero rows in `agentic/`, `workflow/`, `context/`.
   The four-verb tools are registered; no row-specific tools land.
5. The user invokes `mcp__meta_scaffold(new_row="jules")`. PreToolUse
   `validate_envelope_in` passes through (the args carry no
   manifest-write payload). The meta-scaffolder writes filesystem cells
   AND emits the Cell + Row + Phase graph nodes (spec 07-v1 FR5).
   PostToolUse `ingest` records the tool call and finds no
   `artefact_metadata` — no Artefact node lands.
6. A subsequent `MATCH (r:Row {row: "jules"}) RETURN r` returns the
   single Row node, confirming the scaffolder's graph emission.

## Acceptance criteria

```gherkin
Scenario: Store.boot is idempotent and creates the database
  Given an empty context/_store directory
  When Store().boot() runs once
  Then context/_store/ontology.db exists
  And the file is a valid SQLite database with GraphQLite's metadata tables
  When Store().boot() runs a second time
  Then no error is raised and the existing handle is reused

Scenario: Store.boot raises StoreUnavailable when GraphQLite is missing
  Given the GraphQLite extension cannot load
  When Store().boot() runs
  Then a StoreUnavailable exception is raised
  And the exception message names "graphqlite"

Scenario: Driver REGISTRY exposes fs on first import
  Given context._drivers has not been imported in this process
  When `from context._drivers import REGISTRY` runs
  Then REGISTRY["fs"] is an FSArtefactDriver instance

Scenario: Driver REGISTRY rejects duplicate registration
  Given REGISTRY already contains key "fs"
  When register("fs", FSArtefactDriver()) is called without AGENCY_DRIVER_OVERRIDE
  Then a KeyError is raised

Scenario: PostToolUse resolves the driver from artifact_driver
  Given an envelope with data.artefact_metadata including artifact_driver="fs", driver_pointer="result/test/x.txt", raw_bytes=b"x"
  When post_tool_use.ingest runs
  Then an Artefact node lands in the graph
  And the bytes are written via the fs driver
  And metadata no longer contains raw_bytes after ingest

Scenario: Missing driver_key surfaces a useful KeyError
  Given an envelope with artefact_metadata setting artifact_driver="s3" and raw_bytes present
  And no driver is registered under key "s3"
  When post_tool_use.ingest runs
  Then a KeyError is raised
  And the message lists the available driver keys

Scenario: Artefact node schema is the canonical name
  Given the schema file context/_shared/schemas/artefact-node.schema.json exists
  And context/_shared/schemas/sidecar.schema.json does NOT exist
  When post_tool_use.ingest validates artefact_metadata
  Then the validation uses artefact-node.schema.json

Scenario: Graph bootstrap seeds nothing
  Given an empty context/_store directory
  When Store().boot() runs
  Then the graph contains zero nodes
  And the graph contains zero edges
```

## `affects:` allow-list

The implementation PR that lands FR1–FR8 writes ONLY these paths:

- `vision/specs/08-context-base-v1.md` (this file)
- `context/_store/sqlite.py`
- `context/_drivers/__init__.py`
- `context/_drivers/protocol.py` (already exists; touch only if needed)
- `context/_drivers/fs.py` (touch only if needed)
- `context/_hooks/post_tool_use.py`
- `context/_shared/schemas/artefact-node.schema.json` (touch only if needed)
- `tests/context/test_store.py`
- `tests/context/test_hooks.py`
- `tests/context/test_drivers_registry.py` (new)

Deleted by this PR: `context/_store/schema.sql`,
`context/_store/cypher_adapter.py`, and the raw-SQLite branches inside
`context/_store/sqlite.py`. The two pre-existing
`tests/context/test_hooks.py` failures (raw-SQL columns vs GraphQLite
schema) are resolved by rewriting those tests against the GraphQLite
Cypher API.

## Out of scope

- **Drivers beyond `fs`** (`repo`, `s3`, `http`, `drive`) — follow-up
  per `vision/03-architecture.md` §5.2. v1 ships only `fs` to satisfy
  the "one mandatory driver" rule.
- **Hot reload of schemas** — re-read on cold boot only.
- **Cross-process graph access** — GraphQLite is in-process; multiple
  FastMCP servers reading the same `ontology.db` is unsupported.
- **Multi-tenant ontologies** — one graph per repo.
- **Background TTL for `tools_call_log`** — the provenance table grows
  unbounded; a sweeper is out of scope here.

## Dependencies

- **Spec 01** — cell manifests. The PreToolUse hook validates manifest
  bodies; unchanged.
- **Spec 02** — `tool_result` envelope. PostToolUse logs every envelope
  and reads `data.artefact_metadata` from it.
- **Spec 05** — gate YAML; gate evaluator-emitted edges flow through
  `Store.upsert_edge`.
- **`vision/03-architecture.md`** §5.1, §5.2, §5.3, §8 — the architectural
  mandates this spec codifies.
- **Spec 07-v1** — the workflow rewrite that wires `_run_meta_scaffold`
  and `envelope.persist` through this `Store`.
