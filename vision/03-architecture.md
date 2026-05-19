---
slug: vision-architecture
type: vision-architecture
status: ready
owner: claude
created: 2026-05-19
updated: 2026-05-19
summary: The runtime architecture beneath the 3×N matrix. One engine (FastMCP) walks one substrate (the context graph). Workflows are lazily-created paths through the graph. Drivers (sqlite / fs / repo / s3 / http / drive) map nodes to external substrates. This document supplements `00.1-Overview.md` (the design law) with the execution model.
affects:
  - vision/03-architecture.md
depends_on:
  - vision/00.1-Overview.md
  - vision/02-plan.md
referenced_by:
  - vision/README.md
  - vision/specs/07-workflow-base.md
  - vision/specs/08-context-base.md
---

# Architecture — one engine, one graph, pluggable drivers

`00.1-Overview.md` defines the system's **design law** — 3 columns × N rows, strict cell manifests, result registry, column isomorphism. This document defines the **runtime model** — how the law actually executes. The two are complementary; they do not conflict.

The four Phase-3 cross-column "ownership" tensions (gate-edge execution, mid-phase block serialization, hook execution layer, sidecar sandbox) were each a category error — mixing architecture (what's permanent) with user-facing concerns (drivers, storage, presentation). Once those layers are separated, the seams dissolve.

## 1. The model in five sentences

There is ONE engine — **FastMCP** — that walks ONE substrate — the **context graph**, stored as a SQLite file via the **[GraphQLite](https://github.com/colliery-io/graphqlite)** extension (SQLite + Cypher; system-internal at `context/_store/ontology.db`). Workflows are not pre-defined pipelines; they are *Cypher paths* through the graph, lazily linked when the requested traversal does not yet exist. **Pluggable artifact drivers** (fs / repo / s3 / http / drive) map `Artefact` nodes to external user-owned storage — the bytes the user keeps; system metadata never leaks into user storage. **Skills + MCP** are the universal interface — no domain has its own runtime, no domain owns its own infrastructure, no domain writes outside the graph. The MCP server handles the workflow of every operation, including ingest and output, because every operation IS a workflow.

## 2. Three columns + drivers — the architecture/user-facing split

The 3-column matrix is the architecture. Drivers are the user-facing edge. Conflating them is what produced the Phase-3 tensions.

| Layer | Concern | Examples |
|---|---|---|
| `agentic` | the engine surface — skills, MCP tools, four-verb contract | `/music-producer`, `mcp__music_analysis`, harness-in-harness |
| `workflow` | path-walking — graph traversal, lazy node creation, gate evaluation | "start music phase 02", "resume blocked phase", "scaffold new row" |
| `context` | the graph + driver registry — nodes, edges, schemas, drivers | `Track` node, `SATISFIES_PHASE` edge, `tool_result` schema, the sqlite/fs/s3/... drivers |
| **drivers** | user-facing I/O — moving bytes between the graph and the world | sqlite default; fs for local files; s3 for buckets; http for URLs; drive for Google Drive |

**Architecture asks**: "what nodes does the system know about? what edges connect them? what skills walk those edges?"
**User-facing asks**: "where do the bytes live? how do they get in? how do they come out?"

Architecture decisions are permanent. User-facing decisions are configurable per row, per artifact, per session. Conflating them — making "where the MP3 lives" an architecture concern — produced false ownership disputes.

## 3. The engine

**FastMCP IS the runtime.** There is no separate "workflow engine" or "context engine" or "agentic engine". One server process, one event loop, one tool registry. Every column's behavior is expressed as MCP tools and skills on that one engine.

The four-verb contract (`mcp__list_tools`, `mcp__call_tool`, `mcp__list_skills`, `mcp__dispatch_skill`) is the engine's public surface. Every other tool the system exposes (`mcp__music_analysis`, `mcp__workflow_start`, `mcp__context_query`, …) is just another entry in the registry that FastMCP serves over that contract.

`agentic/_harness/` (spec 06) IS this engine. It is not a "column-specific" component — it is the engine that hosts all columns.

## 4. The graph as workflow substrate

The **context graph** is the system's only persistent state. It contains:

- **Nodes** — typed objects with payloads. Node types include `Skill`, `Tool`, `Phase`, `Gate`, `Artefact`, `Row`, `Cell`, `Session`, `Template`, `Schema`, …
- **Edges** — typed directed relations. Edge types include `PRECEDES`, `BLOCKS`, `PRODUCES`, `CONSUMES`, `DERIVED_FROM`, `SATISFIES_PHASE`, `DISPATCHED_TO`, `INVOKED_TOOL`, …

**Workflows are paths through the graph.** Executing a workflow = traversing edges from a start node to a goal node, calling the skill/tool at each node, emitting provenance edges as you go.

### Lazy path creation

The graph is not pre-populated with every possible workflow. When the user asks "do step 3 of music for track X", the engine queries the graph for a path from the current state to "step 3 for track X". If the path exists, it walks it. If it doesn't — because step 2 hasn't been done — the engine has two options:

1. **Block-and-prompt**: surface a gate failure (`step 2 must precede step 3 for track X`) and ask the user how to proceed.
2. **Lazy-link**: create the missing nodes/edges (e.g., a placeholder `Phase{id: "02", track: X}` node) and continue, marking the placeholders for completion later.

Which option the engine picks is governed by gate semantics (spec 05) and the workflow row's manifest. The default is block-and-prompt; lazy-link is opt-in per row.

### State lives in the graph

There is no separate state file, envelope-on-disk, or session-store outside the graph. When a workflow yields (because a gate blocks or the user needs to answer), the yield state is a graph node (`Continuation{session_id, phase_id, opaque_state}`). When the user replies, the engine queries the graph for the continuation, resumes from the node, deletes/marks the continuation when complete.

This dissolves spec 04's `PhaseStateEnvelope` file-on-disk model. The envelope still exists as a wire-format (the JSON the MCP tool returns), but its serialized form is just a graph node, not a separate `.json` file in `workflow/_state/`.

## 5. Drivers — the user-facing boundary

A **driver** is a backend that maps graph nodes to external substrates. Drivers split cleanly into two roles, and that split matches the system/user-storage boundary:

### 5.1 The graph driver (system-internal) — GraphQLite

Graph metadata — every node, every edge, every provenance trail, every `Continuation`, every audit trace — lives in ONE place: a single SQLite file at `context/_store/ontology.db`, accessed through the **[GraphQLite](https://github.com/colliery-io/graphqlite)** SQLite extension (MIT, C core + Python binding, ~340★, active). This is the system's internal store. It is not configurable per-row — every install has exactly one graph database, and it is the source of truth for everything the system knows.

GraphQLite gives us, on top of plain SQLite:

- **Native node/edge primitives** — `upsert_node(id, props, label=...)`, `upsert_edge(src, dst, props, rel_type=...)` — instead of hand-rolled adjacency tables.
- **Cypher query language** — `MATCH (a:Phase)-[:PRECEDES]->(b:Phase) RETURN ...` — instead of recursive CTEs over our own schema.
- **Built-in graph algorithms** — `pagerank()`, `louvain()`, `dijkstra()` — used for routing decisions (shortest workflow path between two states, importance ranking when picking which artefact to surface, community detection when grouping related rows).
- **Embedded, no server** — fits the "one SQLite file" requirement; works in the FastMCP process directly.

The graph driver is therefore **not pluggable in v1**. GraphQLite + SQLite is the chosen substrate, and that choice is part of the architecture, not a per-row decision. (Future may add Postgres or another Cypher store as an alternative driver if a deployment outgrows embedded SQLite — that is a deployment concern, not a row-config concern.)

#### Sketch of the in-process API

```python
# context/_store/graph.py — system-internal, single instance per FastMCP process
from graphqlite import Graph

g = Graph("context/_store/ontology.db")  # opens or creates

# A phase node + its precedence edge
g.upsert_node("music:tinytrash:phase:02",
              {"row": "music", "cell": "tinytrash", "phase_id": "02",
               "status": "blocked", "blocked_on_gate": "lyrics_reviewed"},
              label="Phase")
g.upsert_edge("music:tinytrash:phase:01", "music:tinytrash:phase:02",
              {"reason": "lyrics_reviewed=true"},
              rel_type="PRECEDES")

# Cypher traversal — find every blocked phase whose gate has been satisfied
g.query("""
    MATCH (p:Phase {status: 'blocked'})-[:BLOCKED_ON]->(g:Gate)
    WHERE g.satisfied = true
    RETURN p
""")
```

The Python binding is what the FastMCP server wraps. Every column's MCP tools that read or write context state go through this one `Graph` instance — there is no second writer.

### 5.2 Artifact drivers (user-storage)

**Results are stored OUTSIDE the system.** The MP3 the user takes home, the PDF they publish, the rendered video they post — these are user-owned artifacts living in user-owned storage. The graph knows ABOUT them (via `Artefact` nodes with provenance, hash, mime, derived_from edges) but does NOT hold the bytes.

Each `Artefact` node has an `artifact_driver` field that says which backend holds the actual bytes:

- **`fs`** — bytes live in a user-configured filesystem vault. Graph stores `(vault_root, rel_path)`.
- **`repo`** — bytes are git-tracked in a user repo (this repo or external). Graph stores `(repo_url, commit, path)`.
- **`s3`** — bytes in a user-owned bucket. Graph stores `(bucket, key, version)`.
- **`http`** — bytes fetched on-demand from a URL. Graph stores URL + ETag. Used for cited research sources.
- **`drive`** — Google Drive documents. Graph stores `(drive_file_id, last_modified)`.

Critically: **there is no `.meta.json` sidecar file written next to user artifacts**. Metadata stays in the graph SQLite. The user's storage holds only the bytes the user actually wants. The earlier `vision/specs/03-sidecar-metadata.md` schema is therefore not how artifacts are tracked — it was a leakage of system state into user storage. The fields it specified (sha256, provenance, derived_from, satisfies_phase) all live as columns/edges on the `Artefact` node in the graph instead.

### 5.3 The artifact-driver interface (high-level — concrete signature in v1 of spec 08)

- `get_bytes(node) -> bytes | str` — fetch the bytes from external storage.
- `put_bytes(node, bytes) -> None` — write the bytes; the driver MAY set hash/size/etag fields on the node, which the engine writes back to the graph.
- `list_changes(since_token) -> list[event]` — for subscription/change-detection (optional).
- `materialize_for_export(node, target_format) -> ...` — format conversion (e.g., render markdown to PDF) before writing.

**The MCP server is the workflow runner for every I/O operation.** Ingesting a research PDF, exporting a master track to streaming, syncing a Drive doc into the graph — every one is a workflow path:

```
external source --[via artifact driver]--> ingest skill --> Artefact node (graph SQLite)
```

```
Artefact node (graph SQLite) --> export skill --[via artifact driver]--> external destination
```

The Artefact node is the system's record. The bytes are the user's possession. The graph SQLite is the system's record of WHAT exists; the artifact driver is the bridge to WHERE the bytes live.

## 6. Skills + MCP as universal interface

The system's only public surface is **slash commands (skills)** and **MCP tools**. Every behavior — domain work, system maintenance, ingest, export, validation, scaffolding — is exposed through one of those two. There is no separate "admin API", "result CDN", or "registry service".

This forces a useful constraint: anything the user might want is something the engine can do. Anything the engine can do, the user can trigger via a skill or tool.

## 7. The four Phase-3 seams dissolve

| Seam | Phase-3 framing | Resolution under this architecture |
|---|---|---|
| Gate-edge execution ownership | workflow defines `on_success: emit_edge`; context expects via PostToolUse; agentic refuses | False question. Gates are edges in the path; FastMCP traverses them. The gate evaluator writes the edge through the same graph API anything else uses. No cross-column hand-off. |
| Mid-phase block serialization | `PhaseStateEnvelope` needs to suspend across user turns | The conversation IS the continuation. The yield state is a `Continuation` node in the graph; the next turn queries it. No file-on-disk artifact. |
| Hook execution layer | MCP middleware vs Python decorators vs FastMCP-native interceptors | Hooks are workflow phases — graph nodes the engine walks like any other. The decision "where to wire them" is a non-question; they're just more graph. |
| Sidecar sandbox permission | can FastMCP write `.meta/` next to a user vault? | False premise. The system writes NO sidecar files into user storage. All metadata lives in the graph SQLite (system-owned). Artifact drivers only move bytes; they never write system state into user storage. |

Each seam was the symptom of asking an architecture question of a user-facing concern, or vice versa.

## 8. Consequences for the spec set

These specs are unaffected by the architecture clarification:

- **`specs/01-cell-manifest.md`** — strict manifest + derivation rules. Same.
- **`specs/02-tool-result-envelope.md`** — frozen FastMCP envelope. Same.
- **`specs/03-sidecar-metadata.md`** — **deprecated.** The sidecar `.meta.json` file pattern is wrong: it leaks system metadata into user storage. All artifact metadata (sha256, content_type, derived_from, satisfies_phase, produced_by) lives in the graph SQLite as fields on the `Artefact` node. User storage holds only the bytes. Spec 03's fields remain useful as the field-set on the Artefact node; the file-on-disk format does not. A v1 rewrite or a deprecation marker should land.
- **`specs/05-gate-yaml.md`** — gate definition as edge constructor. Same; the `emit_edge` directive writes through the graph driver, not through cross-column negotiation.
- **`specs/06-agentic-base.md`** — FastMCP harness + four-verb contract. Same; this IS the engine.

These specs need a v1 rewrite under this architecture:

- **`specs/07-workflow-base.md`** → `specs/07-workflow-base-v1.md` (rewrite, not patch):
  - Drop `phases/<NN>-*.md` as canonical artifact. Phase definitions are graph nodes (`Phase` type) with a body reference. The runner is a graph traverser, not a pipeline.
  - Drop `workflow/_state/` JSON-file resume. Continuation is a graph node.
  - Add lazy-path-creation as a first-class operation.
  - The meta-row stays — it's the workflow that scaffolds new row cells from templates. But it scaffolds INTO the graph (creating nodes) as well as INTO the filesystem (via the fs driver).

- **`specs/08-context-base.md`** → `specs/08-context-base-v1.md` (rewrite):
  - Replace the hand-rolled SQLite schema with **GraphQLite** (SQLite extension + Cypher). One `Graph` instance, one `ontology.db` file, in-process inside the FastMCP server.
  - Define the canonical node-type taxonomy (`Skill`, `Tool`, `Phase`, `Gate`, `Artefact`, `Row`, `Cell`, `Session`, `Continuation`, `Template`, `Schema`, …) and edge-type catalog (`PRECEDES`, `BLOCKS`, `BLOCKED_ON`, `PRODUCES`, `CONSUMES`, `DERIVED_FROM`, `SATISFIES_PHASE`, `DISPATCHED_TO`, `INVOKED_TOOL`, …) as Cypher constraints.
  - Specify the **artifact-driver protocol** (concrete Python signature) and the registry: how `fs`, `repo`, `s3`, `http`, `drive` register themselves; how an `Artefact` node's `artifact_driver` field resolves to a driver instance at read/write time.
  - GraphQLite is the only graph driver in v1. `fs` is the only mandatory artifact driver in v1 (so a user can write to their vault); `repo` / `s3` / `http` / `drive` are follow-up tasks.

Spec 04 (`PhaseStateEnvelope`) becomes mostly informational:

- The TypedDict shape is still useful as wire format for tool returns.
- The file-on-disk serialization section is obsolete (replaced by `Continuation` graph node).
- Keep as a reference; flag the deprecated sections in a v1 rewrite.

## 9. Migration status (v0 → v0.1)

**Update 2026-05-19**: the three v0 base-layer Jules sessions absorbed the architecture-update messages in-flight and pushed second commits. The merged v0 PRs (#148/#149/#150) therefore already include most of what was originally planned for a v1 refactor wave:

- **v0 agentic** (PR #148) — FastMCP harness + four-verb contract + cell loader. Unchanged by the architecture clarification, as expected.
- **v0 workflow** (PR #150) — Continuation persisted via `context.upsert_node(Continuation{...})` (no `workflow/_state/` JSON files). Pipeline runner abstracts Phase retrieval through a mockable `_query_phase` seam (real `context.query` wiring is the v1 follow-up). `lazy_link` flag is first-class on `pipeline.start()`. **Gap W5**: `_run_meta_scaffold` writes filesystem cells but does NOT yet emit `Cell`/`Phase`/`Row` graph nodes.
- **v0 context** (PR #149) — GraphQLite Python binding (`from graphqlite import Graph`) with raw-SQLite fallback. Artifact-driver Protocol + `fs` driver. PostToolUse hook upserts an `Artefact` node; no `.meta.json` sidecar files written. **Gap C5**: hooks exist as standalone modules but are not registered with the FastMCP server in `agentic/_bootloader.py`.

What remains for the v0.1 milestone (see `04-nextsteps.md`):

1. **Close W5 + C5** in one in-session follow-up PR (~50 lines + 2 tests).
2. **Canonicalize schemas** — diff `vision/specs/schemas/<col>/` drafts against `context/_shared/schemas/` runtime stubs; promote the vision drafts.
3. **Write specs 07-v1 and 08-v1** to lock the lazy-link opt-in mechanism, driver registry, Artefact node schema (rename `sidecar.schema.json` → `artefact-node.schema.json`), and graph bootstrap.
4. **Materialize the first row (`jules`)** via the meta-row scaffolder, prove the architecture end-to-end. Plan: `vision/04-nextsteps.md`.
5. **Drop the raw-SQLite fallback** once GraphQLite is locked in as the substrate.

## 10. What is NOT in this document

- Concrete Driver Protocol Python signatures (in v1 of spec 08).
- Concrete graph node-type taxonomy and edge-type catalog (in v1 of spec 08).
- How lazy path creation negotiates with the user (in v1 of spec 07).
- How cross-row dispatch works in the graph (planned `specs/09-cross-row-dispatch.md`).
- How the central plugin bootloader registers everything at boot (planned `specs/10-bootloader.md`).
