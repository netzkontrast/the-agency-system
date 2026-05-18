---
spec_id: 124
slug: graphqlite-codemode
status: draft
owner: jules
depends_on: [008, 100, 111, 112, 113, 122]
affects:
  - servers/agency-mcp/pyproject.toml
  - servers/agency-mcp/src/agency_mcp/lib/graphqlite/__init__.py
  - servers/agency-mcp/src/agency_mcp/lib/graphqlite/schema.py
  - servers/agency-mcp/src/agency_mcp/lib/graphqlite/ingest.py
  - servers/agency-mcp/src/agency_mcp/handlers/graph/__init__.py
  - servers/agency-mcp/src/agency_mcp/handlers/graph/anchors.py
  - servers/agency-mcp/src/agency_mcp/handlers/graph/algorithms.py
  - servers/agency-mcp/src/agency_mcp/codemode/manifest.json
  - servers/agency-mcp/src/agency_mcp/server.py
  - hooks/hooks.json
  - hooks/graph_ingest.py
  - tests/unit/graph/test_schema.py
  - tests/unit/graph/test_ingest.py
  - tests/unit/graph/test_anchors.py
  - tests/integration/test_graph_cypher_roundtrip.py
  - tests/integration/test_graph_algorithms.py
  - docs/architecture/graphqlite-integration.md
source-repos: [colliery-io/graphqlite @ main]
domain: cross
wave: D
estimated_jules_sessions: 3
research: Plan/_research/graphqlite-codemode/findings.md
---

# Spec 124: GraphQLite Code Mode Integration

## Why

The plugin's unified ontology (Spec 122) structures the relationships across music, novel, jules, and agentic domains. However, Path B (Specs 111-113) only provides a flat, BM25-searchable text manifest. To unlock the value of the ontology graph, we need a query mechanism. By integrating `colliery-io/graphqlite` as an SQLite loadable extension, we gain the ability to execute expressive Cypher queries (`MATCH`) and standard graph algorithms (PageRank, Shortest Path) over our data. This allows the model to answer complex relational questions (e.g. shortest dependency path between specs) entirely locally without requiring heavy external graph database servers like Neo4j.

## Done When

- `graphqlite` is pinned in `servers/agency-mcp/pyproject.toml` (recommend `graphqlite>=0.4.4,<0.5` while upstream is pre-1.0).
- A dedicated SQLite graph database is initialised at `~/.agency-system/cache/graph.sqlite` on MCP server boot, in WAL mode.
- Three eager anchor tools (`graph_cypher`, `graph_describe_node`, `graph_run_algorithm`) are registered and classified in `codemode/manifest.json`.
- `graph_cypher` supports `dry_run=True`, which MUST NOT mutate the database; mutating queries return `{would_apply, explain_sql, warnings}`.
- `hooks/graph_ingest.py` is created and wired as `PostToolUse` on Markdown writes; integrates with Spec 113's watcher events.
- `graph_describe_node(id, expand=1)` retrieves a node and its immediate inbound/outbound neighbours.
- `pytest` integration tests verify Cypher read/write operations and graph algorithm accuracy (PageRank sums to ≈1.0, etc.).
- Boot token budget impact of the graph anchors MUST keep `tools/list` within 1.10× of the pre-graph baseline.
- Performance baseline documented: simple MATCH ≤ 5 ms on 10k-node graph (in-memory + WAL), PageRank on 100k nodes ≤ 200 ms.

## Source clones (run first)

```bash
git clone --depth=1 --branch=main \
  https://github.com/colliery-io/graphqlite.git \
  ~/work/vendor/graphqlite
```

If the import smoke test fails on the Jules runner, open a draft PR labelled `[BLOCKED: graphqlite-install]` and stop.

## Files

**Create:**
- `servers/agency-mcp/src/agency_mcp/lib/graphqlite/__init__.py`
- `servers/agency-mcp/src/agency_mcp/lib/graphqlite/schema.py`
- `servers/agency-mcp/src/agency_mcp/lib/graphqlite/ingest.py`
- `servers/agency-mcp/src/agency_mcp/handlers/graph/__init__.py`
- `servers/agency-mcp/src/agency_mcp/handlers/graph/anchors.py`
- `servers/agency-mcp/src/agency_mcp/handlers/graph/algorithms.py`
- `hooks/graph_ingest.py`
- `tests/unit/graph/test_schema.py`
- `tests/unit/graph/test_ingest.py`
- `tests/unit/graph/test_anchors.py`
- `tests/integration/test_graph_cypher_roundtrip.py`
- `tests/integration/test_graph_algorithms.py`
- `docs/architecture/graphqlite-integration.md`

**Modify:**
- `servers/agency-mcp/pyproject.toml`
- `servers/agency-mcp/src/agency_mcp/codemode/manifest.json`
- `servers/agency-mcp/src/agency_mcp/server.py`
- `hooks/hooks.json`

## Approach

1. **Gate 1 — Confidence.** Smoke-test `python3 -c "import graphqlite"`. Pin version `0.4.4` (current at research time) with cap `<0.5` until upstream cuts 1.0. Confirm MIT license. Verify no copyleft conflicts in `pyproject.toml`.
2. **Schema and connection setup.** In `schema.py`, establish `GraphManager` pointing to `~/.agency-system/cache/graph.sqlite` with WAL mode. Define mapping from Spec 122's L1/L2 frontmatter into the EAV node/edge tables — L1 fields become typed properties, L2 namespaced fields go into `node_props_json`, edge declarations become `(source, target, type)` rows.
3. **Graph tools implementation.**
   - `graph_cypher` in `anchors.py`. Honors `dry_run=True` by parsing the query, returning generated SQL via the graphqlite EXPLAIN-prefix flag, and skipping execution.
   - `graph_describe_node(id, expand=1)` fetches a node + both-direction adjacent edges in a single query.
   - `graph_run_algorithm` in `algorithms.py`. Supports `pagerank`, `louvain`, `shortest_path`, `bfs`, `dfs`, `components` (initial scope). Large scopes return `return_plan` envelope; small scopes return inline.
4. **Ingestion hooks.** `hooks/graph_ingest.py` triggers on PostToolUse for Markdown writes. Maps frontmatter L1/L2 + relationship headers → Cypher UPSERT (MERGE semantics). After mutation, calls `g.reload_graph()` to refresh the CSR cache.
5. **Code Mode classification.** `codemode/manifest.json`: `graph_cypher` + `graph_describe_node` = **eager**, `graph_run_algorithm` = **background** (companion `graph_run_algorithm_status(job_id)`), `graph_ingest_frontmatter` = **deferred**.
6. **Path B integration.** `server.py` intercepts file-change notifications from Spec 113's watcher and triggers incremental graph updates (single-file UPSERT + CSR reload) instead of full rebuild. Spec 112's `context_describe(id)` calls `graph_describe_node` internally to populate `neighbours`.
7. **Bootstrap mode.** First-boot full rebuild uses `GraphManager.insert_nodes_bulk()` + `insert_edges_bulk()` (100-500× faster than Cypher CREATE) by walking the repo, parsing frontmatter, and bulk-inserting in a single transaction.
8. **Gate 2 — TDD.**
   - **RED:** `test_schema.py` (EAV mapping), `test_anchors.py` (tool envelopes), `test_ingest.py` (UPSERT idempotence). Integration: `test_graph_cypher_roundtrip.py` (CREATE → MATCH → DELETE), `test_graph_algorithms.py` (PageRank sums ≈ 1.0, BFS reaches all reachable nodes).
   - **GREEN:** Implement to satisfy.
   - **REFACTOR:** DRY up Cypher query builders.
9. **Gate 3 — Evidence.** pytest stdout. Boot-token-budget measurement showing `tools/list` ≤ 1.10× baseline. Latency probe output showing MATCH on 10k nodes ≤ 5 ms.
10. **Gate 4 — Self-Review.** Verify the 4 protocol gates. Document any schema-mapping discrepancies from Spec 122 frontmatter in the PR body.

## Acceptance (Gherkin)

```gherkin
# anchor: 124.1
Scenario: graph_cypher read operation performance
  Given a populated graph database with 10,000 nodes
  When a read-only MATCH Cypher query is executed via graph_cypher
  Then the response rows are returned in ≤ 5 ms median (≤ 50 ms p99 for large result sets)

# anchor: 124.2
Scenario: graph_cypher honors dry_run
  Given the caller executes graph_cypher with `CREATE ... RETURN id` and dry_run=True
  When the tool processes the request
  Then the graph database is NOT mutated
  And the tool returns `{would_apply, explain_sql, warnings}`

# anchor: 124.3
Scenario: graph_describe_node retrieves neighbours
  Given a node exists with incoming and outgoing relationships
  When graph_describe_node is called with expand=1
  Then the tool returns the node properties
  And it returns lists of immediate neighbours in both directions

# anchor: 124.4
Scenario: PageRank execution yields normalised scores
  Given graph_run_algorithm is called with algo="pagerank" and scope={"type": "skill"}
  When the algorithm completes
  Then the algorithm returns scores for nodes in the scope
  And the sum of all scores is ≈ 1.0

# anchor: 124.5
Scenario: Ingest hook triggers on Markdown modification
  Given a Markdown file containing L1 frontmatter
  When the file is modified via a Write tool
  Then hooks/graph_ingest.py is triggered
  And the corresponding graph node's properties are updated within 500 ms
  And the CSR cache is reloaded

# anchor: 124.6
Scenario: Graceful error handling on bad Cypher
  Given an unparseable Cypher query is passed to graph_cypher
  When the tool executes
  Then it returns `{ok: False, error: "<exact graphqlite error>"}`
  And it does NOT raise an unhandled exception

# anchor: 124.7
Scenario: Boot token budget restriction
  Given the graph anchors are added to the Code Mode manifest
  When tools/list is called
  Then the token size of the response is ≤ 1.10× the pre-graph baseline

# anchor: 124.8
Scenario: Bootstrap from cold cache uses bulk insert
  Given graph.sqlite does not exist
  When the MCP server boots
  Then the ingest layer walks the repo, parses frontmatter, and calls insert_nodes_bulk / insert_edges_bulk
  And cold-start ingest of 1,000 artefacts completes in ≤ 5 seconds
```

## Findings highlights

(From `Plan/_research/graphqlite-codemode/findings.md` — 1456 lines, full detail there.)

**GraphQLite capabilities confirmed:**

- License **MIT**, current version **0.4.4** (pre-1.0 — abstracted away behind `graph_*` tools so a future backend swap to Neo4j / Apache AGE / kuzu doesn't break MCP signatures).
- **Cypher subset supported:** MATCH, OPTIONAL MATCH, CREATE, MERGE, SET, REMOVE, DELETE, DETACH DELETE, RETURN, WITH, WHERE, UNWIND, FOREACH, UNION, FROM (multi-graph).
- **Cypher NOT supported:** correlated subqueries (`CALL {}`), procedure invocations (`CALL procedure`), `CREATE INDEX`, `CASE` on `SET` LHS, nested `FOREACH`, native EXPLAIN/PROFILE.
- **18 graph algorithms built in.** Core: PageRank, Louvain, Dijkstra, A*, BFS, DFS, Weakly/Strongly Connected Components. Extended: Degree/Betweenness/Closeness/Eigenvector Centrality, Label Propagation, Node Similarity, KNN, Triangle Count, All-Pairs Shortest Path. Run on an in-memory CSR cache built from the EAV tables.

**Cross-domain query examples (motivating use-cases):**

| Domain | Cypher | Use-case |
|---|---|---|
| Music | `MATCH (t:track)-[:PROMPTED_BY]->(p:suno_prompt {genre: "synthwave"}) RETURN t.id` | Find all tracks influenced by a Suno prompt + genre |
| Novel | `MATCH (w:work)-[:CONTAINS]->(c:chapter)-[:CONTAINS]->(s:scene) WHERE s.throughline = "Cost" RETURN s.id` | Find scenes tied to a Dramatica throughline |
| Jules | `MATCH p = shortestPath((s1:spec {id:"plan:020"})-[:DEPENDS_ON*]->(s2:spec {id:"plan:003"})) RETURN p` | Shortest dependency path between two specs |
| Agentic | `MATCH (s:spec)<-[:INFORMED]-(r:research) WHERE s.id = "plan:020" RETURN r.id` | All research briefs informing a given spec |
| Shared | `CALL pagerank() YIELD node, score MATCH (n) WHERE n = node RETURN n.id, score ORDER BY score DESC LIMIT 10` | Top-10 most-cited artefacts across all domains |

**Schema mapping (EAV — Entity-Attribute-Value):**
- Node id → external string (e.g. `plan:124-graphqlite-codemode:spec`)
- Spec 122 `type` field → GraphQLite node `label`
- L1 fields → typed properties (int/text/real/bool)
- L2 namespaced fields → JSON property in `node_props_json` table
- Edge declarations from `header-ontology.json` → `(source, target, type)` rows
- Storage: nodes in `nodes(id)`, edges in `edges(id, source_id, target_id, type)`, properties in 10 type-specific tables (5 node + 5 edge) for indexing

**Performance baseline (findings benchmarks, single-core MacBook, in-memory + WAL):**
- Extension load: ~5 ms (one-time per connection)
- Simple MATCH: 0.5–2 ms (10 nodes), 1–5 ms (100 relationships)
- `gql_load_graph()` on 100k nodes: 50–100 ms
- PageRank on 100k nodes: ~180 ms; on 1M nodes: ~38 s

## Path B integration

| Path B surface | Integration point |
|---|---|
| **Spec 111 manifest** | Bootstrap path: `bin/build_context_manifest.py` reads frontmatter, calls `GraphManager.insert_nodes_bulk()` + `insert_edges_bulk()` directly (bypasses Cypher parser for speed). Manifest entries get `graph_id` field pointing to the corresponding node. |
| **Spec 112 describe** | `context_describe(id)` enriches its payload with `graph_describe_node(id, expand=1).neighbours`. Adds `{incoming: [...], outgoing: [...]}` to the describe envelope. |
| **Spec 113 watcher** | On `ChangeEvent(modified\|added\|deleted)`, `on_change` callback calls `hooks/graph_ingest.py` → single-file UPSERT → `g.reload_graph()`. Incremental, not full rebuild. |
| **Spec 111 BM25 search** | Coexists — BM25 handles fuzzy text discovery, `graph_cypher` handles structural traversal. Both surfaced via the same anchor triad; users pick the right tool for the question. |
| **Spec 122 schemas** | Spec 122 declares the type enum and edge ontology that 124's EAV mapping consumes. Schema changes in 122 require a graph rebuild (delete `graph.sqlite` + restart). |
| **Spec 100 session-log** | Graph mutations emit structured session-log events (`graph.upsert`, `graph.delete`) for audit. |

## Open questions

(See `Plan/_research/_synthesis-122-123-124.md` §4 for cross-spec rationale.)

| # | Question | Resolution (this spec) |
|---|---|---|
| **Q5** | GraphQLite pre-1.0 abandonment risk | **MITIGATED**: pin `>=0.4.4,<0.5`; abstract via `graph_*` MCP tools so backend swap doesn't break the signatures. |
| **Q4** | Boot-token budget impact | ≤ 1.10× Spec 008 baseline; verified by `bin/measure_token_budget` post-merge. |
| **Q6** | Schema migration when Spec 122 evolves | **DEFERRED**: graph.sqlite is a derived index. On breaking ontology change, delete + rebuild on next boot. Forward-migration policy is a follow-up spec. |
| TBD | Cross-platform extension loading | `.dylib` / `.so` / `.dll` auto-selected by `graphqlite.get_loadable_path()`. CI MUST test on all three. If a platform fails wheel install, open `[BLOCKED: graphqlite-install]` PR. |
| TBD | Multi-writer safety | SQLite WAL mode + per-connection `asyncio.Lock` on mutations. Reads are concurrent. |
| TBD | dry_run return envelope | `{would_apply: bool, explain_sql: str, warnings: [str]}`. NOT a unified diff — graphqlite EXPLAIN returns generated SQL, not row-level deltas. |
| TBD | CSR reload trigger frequency | Coalesced: a debounced reload fires 250 ms after the last write to avoid thrashing when many files change at once (e.g. a batch script run). |

## Out of scope

- Replacing BM25 text search (Spec 111) or semantic embedding vector search.
- Altering the foundational JSON-vs-SQLite storage model of Spec 003's `StateCache`.
- Attempting to load the entire graph structure into the LLM context window.
- Forward schema migration when Spec 122 evolves (Q6) — delete + rebuild is the only supported path initially.
- Partial-ingest rollback / transactional safety on hook crash mid-write — out of scope; assume idempotent UPSERT and hook re-run on next file touch.

## References

- `Plan/008-codemode-registry/spec.md`
- `Plan/100-session-log-mcp/spec.md`
- `Plan/111-context-mode-manifest/spec.md`
- `Plan/112-context-anchor-triad/spec.md`
- `Plan/113-context-cache-and-subscriptions/spec.md`
- `Plan/122-centralized-ontology/spec.md`
- `Plan/_research/graphqlite-codemode/findings.md`
- `Plan/_research-briefs/03-graphqlite-codemode.md`
- `Plan/_research/_synthesis-122-123-124.md`
- GraphQLite documentation: https://colliery-io.github.io/graphqlite/
