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

### FR1 — GraphQLite is the only graph substrate (process-singleton Store)

`context/_store/sqlite.py::Store`:

```python
class StoreUnavailable(RuntimeError):
    """Raised when the GraphQLite native extension cannot load.

    The FastMCP bootloader catches this and surfaces a fix-hint
    ("Install graphqlite: pip install graphqlite") rather than panicking.
    """

class Store:
    def __init__(self, db_path: str | None = None) -> None: ...
    def boot(self) -> None:
        """Open or create ontology.db. Raises StoreUnavailable
        if the GraphQLite extension cannot load. Idempotent — the
        second call reuses the open Graph instance."""
    def upsert_node(self, node_id: str, payload: dict, *, label: str) -> None: ...
    def upsert_edge(self, from_node: str, to_node: str, payload: dict | None = None, *, rel_type: str) -> None: ...
    def log_tool_call(self, tool: str, envelope: dict) -> None: ...
    def query(self, cypher: str, params: dict | None = None) -> list[dict]: ...
    def close(self) -> None: ...
```

Singleton accessor (module-level, in `context/__init__.py`):

```python
_STORE: Store | None = None

def get_store() -> Store:
    """Return the process-wide Store singleton.

    All runtime callers (hooks, pipeline, gate evaluator) reach the
    graph through this accessor. Constructing `Store()` directly is
    permitted only in tests (which monkeypatch the singleton via
    `monkeypatch.setattr("context._STORE", Store(db_path=tmp))`).
    """
    global _STORE
    if _STORE is None:
        _STORE = Store()
        _STORE.boot()
    return _STORE
```

Rationale: GraphQLite holds an open SQLite connection per `Graph`
instance. Re-constructing `Store()` on every hook fire opens a new
connection each time — under any concurrency, that contends for the
same WAL file. The singleton accessor pins one connection per process.

- `Store.boot()` is **idempotent**. Calling it twice is harmless; the
  second call observes the already-opened `Graph` and returns. The
  singleton accessor calls `boot()` exactly once on first access.
- `boot()` calls `Graph(self.db_path)` exactly once per `Store`. If
  GraphQLite fails to load (`RuntimeError` mentioning "SQLite extension
  loading not available" or any other initialisation failure),
  `boot()` raises `StoreUnavailable` with the original cause chained
  via `raise StoreUnavailable(...) from e`. The fallback in
  `_get_graph()` that returned `None` and switched to raw SQLite is
  **deleted**, including every `if g:` / `else:` branch in
  `upsert_node`, `upsert_edge`, and `query`.
- The `db_path` default resolves to `context/_store/ontology.db`
  resolved relative to the repo root via `Path(__file__).resolve().parents[2]`,
  not the module path or the cwd, so the runtime doesn't fight the
  cwd-switching tests do.

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
import os
from typing import Protocol
from .protocol import ArtefactDriver
from .fs import FSArtefactDriver

REGISTRY: dict[str, ArtefactDriver] = {}

_TRUTHY = {"1", "true", "yes", "on"}

def _override_enabled() -> bool:
    """AGENCY_DRIVER_OVERRIDE truthiness — explicit allow-list, not
    bool(string). Acceptable values: '1', 'true', 'yes', 'on' (case-
    insensitive). Empty / unset / any other value is False."""
    return os.environ.get("AGENCY_DRIVER_OVERRIDE", "").lower() in _TRUTHY

def register(key: str, driver: ArtefactDriver) -> None:
    """Self-registration hook. Raises KeyError on duplicate key unless
    AGENCY_DRIVER_OVERRIDE is set to a truthy value (see _override_enabled).
    The override is read on every call — set it before importing the
    duplicate driver, unset it afterwards."""
    if key in REGISTRY and not _override_enabled():
        raise KeyError(f"driver {key!r} already registered")
    REGISTRY[key] = driver

def resolve(key: str) -> ArtefactDriver:
    """Lookup helper that surfaces a useful error message.

    Raises KeyError listing the available keys when `key` is unknown.
    Callers SHOULD use this rather than `REGISTRY[key]` directly so
    every miss produces a consistent fix-hint."""
    if key not in REGISTRY:
        raise KeyError(
            f"driver {key!r} not registered. Available drivers: "
            f"{sorted(REGISTRY.keys())}"
        )
    return REGISTRY[key]

# `fs` is the one mandatory v1 driver — register on import.
register("fs", FSArtefactDriver())
```

Future drivers (`repo`, `s3`, `http`, `drive`) are introduced by adding
a new module under `context/_drivers/` whose import calls
`register(...)` once. They are NOT part of v1; this spec defines the
extension surface only.

`Artefact.artifact_driver` (a payload field on the node, see FR5)
selects which driver resolves bytes. PostToolUse and any future
`get_bytes` / `put_bytes` callsite looks up via `resolve(key)`, never
`REGISTRY[key]` directly. Drivers are never instantiated by callers;
the registry holds singletons.

### FR4 — PostToolUse resolves drivers via REGISTRY (validation-first)

`context/_hooks/post_tool_use.ingest` becomes:

```python
from context import get_store
from context._drivers import resolve as resolve_driver

def ingest(tool_name: str, envelope: dict) -> None:
    store = get_store()                           # singleton — see FR1
    store.log_tool_call(tool_name, envelope)
    if not envelope.get("ok"):
        return

    metadata = envelope.get("data", {}).get("artefact_metadata")
    if not metadata or not isinstance(metadata, dict):
        _ingest_emitted_edges(envelope.get("data", {}).get("emitted_edges"))
        return

    # 1. Schema validation (single source of truth).
    jsonschema.validate(instance=metadata, schema=_artefact_schema())

    # 2. Driver-key validation BEFORE node upsert. A bad driver_key
    #    must not produce a dangling Artefact node with no resolver.
    driver = None
    driver_key = metadata.get("artifact_driver")
    if driver_key:
        driver = resolve_driver(driver_key)        # KeyError if unknown

    # 3. Node upsert.
    node_id = _derive_artefact_id(metadata)
    store.upsert_node(node_id, metadata, label="Artefact")

    # 4. Bytes persistence (only if raw_bytes inlined AND driver resolved).
    if driver is not None and "raw_bytes" in metadata:
        driver.put_bytes(metadata, metadata["raw_bytes"])
        del metadata["raw_bytes"]                  # never persist raw bytes in the graph

    for entry in metadata.get("derived_from", []):
        store.upsert_edge(node_id, entry, rel_type="DERIVED_FROM")

    satisfies = metadata.get("satisfies_phase")
    if satisfies:
        row = _derive_row(metadata)
        store.upsert_edge(node_id, f"phase:{row}/{satisfies}", rel_type="SATISFIES_PHASE")

    _ingest_emitted_edges(envelope.get("data", {}).get("emitted_edges"))
```

**Validation timing — pinned**: `artifact_driver` is resolved against
`REGISTRY` immediately after schema validation and BEFORE the node
upsert. Unknown driver keys raise `KeyError` and the node never lands
(failing loud beats a dangling pointer). The `raw_bytes` decision is
independent and downstream.

`_artefact_schema()` reads
`context/_shared/schemas/artefact-node.schema.json` (the N2 rename).

#### `_derive_artefact_id` and `_derive_row` — locked

```python
def _derive_artefact_id(metadata: dict) -> str:
    """Artefact node id = "{row}/Artefact/{sha256}".

    Row resolution order:
      1. Explicit metadata["row"] field (preferred — set by producers).
      2. metadata["produced_by"]["skill"].split("-", 1)[0] (legacy).
      3. "unknown" — logged as a warning.
    """
    row = _derive_row(metadata)
    sha = metadata["sha256"]
    return f"{row}/Artefact/{sha}"

def _derive_row(metadata: dict) -> str:
    if "row" in metadata:
        return metadata["row"]
    skill = metadata.get("produced_by", {}).get("skill", "")
    if "-" in skill:
        return skill.split("-", 1)[0]
    logger.warning("artefact metadata missing row and unresolvable skill; tagging 'unknown'")
    return "unknown"
```

The v0 heuristic of parsing `result/<row>/...` from `artefact_path` is
**dropped** — it never worked for non-`fs` drivers (an `s3` key like
`my-bucket/foo/bar.mp3` is not a row hint). Producers SHOULD set
`metadata["row"]` explicitly. The schema in FR5 adds this field as
optional in v1; v2 will make it required.

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
  PostToolUse time — the resolver fails loud (KeyError) before the
  node is upserted (see FR4).
- `driver_pointer` — driver-specific bytes pointer. Format per
  driver:
  - `fs` — repo-root-relative path string, e.g. `result/jules/research.md`.
  - `s3` (future) — `<bucket>/<key>` form, e.g. `my-bucket/jules/research.md`.
  - `http` (future) — full URL with optional `#etag=...` fragment.
  - `drive` (future) — Google Drive file id.
- `artefact_path` — LEGACY compatibility field, retained for the `fs`
  driver's transitional reads of old nodes. New writes set
  `driver_pointer` instead.
- `row` — row name for ontology key derivation (see FR4
  `_derive_row`). Optional in v1; v2 makes it required. Producers
  SHOULD set this; the legacy fallback parses
  `produced_by.skill.split("-", 1)[0]`.
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

Scenario: get_store returns the same instance across calls
  Given the context._STORE module-global is None
  When get_store() is called twice from different modules
  Then both calls return the same Store instance
  And Graph(<db_path>) was constructed exactly once

Scenario: Unknown driver_key fails BEFORE the node is upserted
  Given an envelope with artefact_metadata setting artifact_driver="s3"
  And no driver is registered under key "s3"
  When post_tool_use.ingest runs
  Then resolve_driver raises KeyError
  And the message lists the registered driver keys (e.g. ["fs"])
  And no Artefact node lands in the graph

Scenario: Missing artifact_driver leaves a metadata-only node
  Given an envelope with artefact_metadata that omits artifact_driver
  When post_tool_use.ingest runs
  Then an Artefact node lands with the validated metadata
  And no driver is invoked
  And raw_bytes (if present) is NOT persisted via any driver

Scenario: AGENCY_DRIVER_OVERRIDE truthy allows duplicate registration
  Given REGISTRY already contains key "fs"
  And the environment variable AGENCY_DRIVER_OVERRIDE="1"
  When register("fs", FSArtefactDriver()) is called again
  Then no KeyError is raised
  And REGISTRY["fs"] now points at the new driver instance

Scenario: AGENCY_DRIVER_OVERRIDE non-truthy keeps the duplicate guard
  Given REGISTRY already contains key "fs"
  And AGENCY_DRIVER_OVERRIDE="" (empty or unset)
  When register("fs", FSArtefactDriver()) is called again
  Then KeyError is raised

Scenario: _derive_row prefers the explicit row field
  Given metadata = {"row": "music", "produced_by": {"skill": "novel-writer", ...}, ...}
  When _derive_row(metadata) runs
  Then it returns "music" (NOT "novel" from the skill prefix)

Scenario: _derive_row falls back to the skill prefix when row is absent
  Given metadata = {"produced_by": {"skill": "music-master", ...}, ...} with no `row` field
  When _derive_row(metadata) runs
  Then it returns "music"

Scenario: StoreUnavailable wraps the GraphQLite ImportError
  Given the graphqlite extension cannot load (RuntimeError on construction)
  When Store().boot() runs
  Then StoreUnavailable is raised
  And the chained `__cause__` is the original RuntimeError
  And the message includes "graphqlite"
```

Existing test coverage on PR #155 to reference:
- `tests/agentic/test_hooks_registered.py::test_post_hook_ingests_artefact_node`
  (PostToolUse wiring + Artefact node landing).
- `tests/context/test_schemas_canonical.py` (round-trip for every
  schema in `context/_shared/schemas/`, plus the
  `test_no_lingering_sidecar_filename` regression guard).

Jules MUST NOT rebuild these fixtures.

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
