# Research Findings: GraphQLite as the Plugin's Graph Query Layer

## 1. Executive Summary

Adopting `colliery-io/graphqlite` as the single cross-domain graph query layer for `the-agency-system` is highly recommended, albeit with a structured partial-adoption strategy (wrapping the engine behind domain-agnostic `graph_*` tools).

GraphQLite is an MIT-licensed SQLite extension that adds Cypher graph querying and graph algorithms directly into SQLite databases. By bringing graph traversals (via MATCH) and computations (like PageRank and Shortest Path) natively to the data layer, we eliminate the need to run separate, resource-intensive graph database services like Neo4j, avoiding Elastic 2.0 restrictions while keeping data tightly embedded in our system. The overarching win is that all the isolated domains (Music, Novel, Jules, Agentic, and Shared) can query their latent, implicit graphical structures within an existing, zero-configuration SQLite context, answering complex relation questions without costly application-side multi-hop fetching.

**The single biggest win:** The ability to execute Cypher queries on the centralized ontology (proposed in Brief 1) natively in SQLite, with graph algorithms (Dijkstra, Louvain, PageRank, etc.) out-of-the-box. This bridges our flat metadata cache with true relational traversals.

**The single biggest risk:** Project maturity. While GraphQLite is promising, it is relatively young (v0.4.4) and the Cypher subset and algorithms operate over a custom Entity-Attribute-Value (EAV) storage model. If we strongly couple application-level schema and lifecycle directly to GraphQLite's EAV tables, migrating to another system later (like DuckDB or kuzu) would be difficult. Therefore, we must treat GraphQLite purely as a derived index of the frontmatter source-of-truth, built behind a strict `graph_*` tool abstraction.

## 2. What GraphQLite Is

### Architectural Shape
GraphQLite is an SQLite loadable extension (`graphqlite.dylib`/`.so`). The Python binding (`graphqlite-0.4.4` available on PyPI) wraps the extension using either `sqlite3` or `apsw`. The `Graph` Python object acts as the primary API, automatically loading the extension, dispatching `.query()` as `SELECT cypher(?, ?)` and abstracting away the internal graph algorithm calls.

The architecture is outlined in the `docs/src/explanation/architecture.md` file (lines 10-60). It works in four stages:
1.  **The Parser:** Uses a Bison GLR grammar to parse Cypher queries. It produces a typed AST.
2.  **The Transformer:** Walks the AST and emits SQL strings specifically against GraphQLite's EAV tables.
3.  **The Executor:** Orchestrates the pipeline, calling SQLite's prepare and step functions.
4.  **Result Formatting:** Serializes results into JSON objects.

### Cypher Subset Supported
GraphQLite implements a large and very useful subset of openCypher, as detailed in `docs/src/reference/cypher.md` (lines 5-30):
*   **Supported:** `MATCH`, `OPTIONAL MATCH`, `CREATE`, `MERGE`, `SET`, `REMOVE`, `DELETE`, `DETACH DELETE`, `RETURN`, `WITH`, `WHERE`, `UNWIND`, `FOREACH`, `UNION`, and multi-graph `FROM`.
*   **Not Supported:** Correlated subqueries (`CALL {}`), procedure invocations (`CALL procedure(...)`), index creation via Cypher (`CREATE INDEX`), `CASE` expressions on the LHS of `SET`, and nested `FOREACH`.

### Built-in Algorithms
GraphQLite implements multiple graph algorithms directly in C/Rust on top of an in-memory Compressed Sparse Row (CSR) cache built on demand from the SQLite tables. These are documented in `docs/src/reference/algorithms.md`:
*   **PageRank**: `$graph.pagerank(damping=0.85, iterations=20)` - $O(iterations \times E)$ (lines 15-40)
*   **Louvain**: `$graph.louvain(resolution=1.0)` - Community detection. (lines 120-145)
*   **Dijkstra (Shortest Path)**: `$graph.shortest_path(source, target, weight_property)` (lines 280-310)
*   **A-Star**: `$graph.astar(source, target, lat_prop, lon_prop)` (lines 315-340)
*   **BFS / DFS**: `$graph.bfs(start, max_depth)` / `$graph.dfs(start, max_depth)` (lines 380-420)
*   **Connected Components**: `weakly_connected_components()`, `strongly_connected_components()` - $O(V + E)$ (lines 230-270)

*Caveat:* Algorithms run against an in-memory CSR cache (`gql_load_graph()`). This cache must be reloaded explicitly (`gql_reload_graph()`) after mutations. Memory overhead is roughly `~20N + 8E` bytes. A 10K node graph consumes minimal memory (<1MB), but caching should be managed proactively.

### Concurrency and Durability
*   **Concurrency:** GraphQLite piggybacks on SQLite's concurrency model. WAL mode is highly recommended to allow concurrent reads alongside writes. The Cypher query holds the SQLite lock for its duration.
*   **Durability:** Data is stored in standard SQLite tables. It survives crash recovery exactly like any SQLite database. Indices are persisted. The CSR graph cache is purely in-memory and rebuilt on open/demand.

## 3. Schema Model

### Physical Storage and Schema Structure
GraphQLite does not store nodes and edges in a single monolithic table. It uses an Entity-Attribute-Value (EAV) model heavily split by data type to optimize SQLite B-tree indices. As explained in `docs/src/explanation/storage-model.md` (lines 10-40):
*   Nodes are in `nodes(id)`.
*   Edges are in `edges(id, source_id, target_id, type)`.
*   Properties are mapped into 10 type-specific tables (5 for nodes, 5 for edges): `node_props_int`, `node_props_text`, `node_props_real`, `node_props_bool`, `node_props_json`.
*   Labels are typed string tags in `node_labels(node_id, label)`.
*   Reverse edges are managed transparently by indices (`idx_edges_source` and `idx_edges_target`), so the writer only needs to insert the forward edge.

### Ontology Mapping Table
Mapping Brief 1's ontology frontmatter to GraphQLite is straightforward. The GraphQLite node `label` will map to the Brief 1 `type`.

| Brief 1 Entity | GraphQLite Mapping | Example |
| :--- | :--- | :--- |
| `id` | Node External ID | `plan:124-graphqlite-codemode:spec` |
| `type` | Node `label` | `spec` |
| L1 Core Fields | Node Properties (typed) | `slug: "graphqlite-codemode"`, `status: "draft"` |
| L2 Namespaced Fields | JSON Property (`_json`) | `music: { genre: "darkwave" }` stored in `node_props_json` |
| Edge Declarations | Edges (`type`) | `(spec)-[:DEPENDS_ON]->(spec)` |

## 4. Code Mode Integration Design

### The Single SQLite File Question
**Recommendation:** Three separate DBs.
`Plan/000-overview.md` dictates `~/.agency-system/cache/state.json` (from Spec 003) and `~/.agency-system/session-log/log.db` (Spec 100). The graph DB is an entirely separate concern—an indexing layer built from immutable Markdown/frontmatter sources. Sharing a database with the high-write `session-log` or state cache introduces unnecessary write contention.
We will use a dedicated `~/.agency-system/cache/graph.sqlite`.

### Tools to Register
Per `Plan/008-codemode-registry/spec.md`, we register these tools. Naming adheres to the `graph_<verb>_<object>` convention with tags `tags={"domain:shared", "kind:graph"}`.

*   `graph_cypher(query: str, params: dict = {}, limit: int = 100, dry_run: bool = False) -> ToolResult`
    *   Classification: **Eager**
    *   Executes Cypher. Enforces `dry_run` for mutating queries.
*   `graph_describe_node(id: str, expand: int = 1) -> dict`
    *   Classification: **Eager**
    *   Retrieves a node and its adjacent neighbors.
*   `graph_run_algorithm(algo: Literal["pagerank","louvain","shortest_path","bfs","dfs","components"], scope: dict, params: dict = {}) -> ToolResult`
    *   Classification: **Background** (Algorithms can be expensive, and they require a graph cache reload). It should have a `graph_run_algorithm_status` poll companion.
    *   Returns a plan via `return_plan` on large scopes.
*   `graph_ingest_frontmatter(path: str, dry_run: bool = True) -> ToolResult`
    *   Classification: **Deferred**
    *   Parses frontmatter at `path` and upserts into the graph.
*   `graph_export(format: Literal["jsonld","graphml","cypher"], filter: dict = {}) -> bytes`
    *   Classification: **Deferred**

### `dry_run` Semantics
If `dry_run=True` on `graph_cypher` or `graph_ingest_frontmatter`, we must NOT execute `MERGE`/`CREATE`/`SET`/`DELETE`. For `graph_cypher`, we use GraphQLite's EXPLAIN prefix (`EXPLAIN MATCH...`) to return the intended SQL AST plan (`{would_apply, diff, warnings}`), fulfilling overview §2.1 #7.

### `return_plan` Semantics
`graph_run_algorithm` on an unbounded scope (e.g., Louvain across the entire graph) could return hundreds of communities. The tool will honor `return_plan`, yielding `{plan: "Compute Louvain across 15,000 nodes, write results to temp JSON file for retrieval, return summary"}` instead of blasting the context window.

## 5. Path B Integration (Specs 111/112/113)

*   **Spec 111 (Context Manifest):** When `bin/build_context_manifest.py` runs, it will iterate all manifests, gather the `id`, `views`, and extracted tags, and feed them into the graph. We will use the `GraphManager.insert_nodes_bulk()` and `insert_edges_bulk()` APIs directly to bypass Cypher parser overhead during full bootstrap.
*   **Spec 112 (Anchor Triad):** `context_describe(id)` will be enhanced. Instead of just querying the flat JSON manifest, it will execute `graph_describe_node(id, expand=1)` behind the scenes to append the required `neighbours: { incoming: [...], outgoing: [...] }` to the describe payload.
*   **Spec 113 (Cache & Watcher):** The watcher emits `ChangeEvent(modified|added|deleted)`. In the `on_change` callback, instead of just rebuilding the JSON manifest, we run `graph_ingest_frontmatter` on the specific changed file. This incrementally updates the graph. We then invalidate the GraphQLite algorithm CSR cache (`g.reload_graph()`).

## 6. Cross-Domain Examples

| Domain | Cypher Query | Expected Result |
| :--- | :--- | :--- |
| **Music** | `MATCH (t:track)-[:PROMPTED_BY]->(p:suno_prompt {genre: "synthwave"}) RETURN t.id` | List of `track` IDs |
| **Novel** | `MATCH (w:work)-[:CONTAINS]->(c:chapter)-[:CONTAINS]->(s:scene) WHERE s.throughline = "Cost" RETURN s.id` | List of `scene` IDs within chapters |
| **Jules** | `MATCH p = shortestPath((s1:spec {id: "plan:020"})-[:DEPENDS_ON*]->(s2:spec {id: "plan:003"})) RETURN p` | Array of ordered `spec` IDs comprising the path |
| **Agentic** | `MATCH (s:spec)<-[:INFORMED]-(r:research) WHERE s.id = "plan:020" RETURN r.id` | List of research brief IDs |
| **Shared** | `CALL pagerank() YIELD node, score MATCH (n) WHERE n = node RETURN n.id, score ORDER BY score DESC LIMIT 10` | Top 10 most-cited items in the entire plugin graph |

## 7. Migration Strategy

1.  **Bootstrap:** The graph lives at `~/.agency-system/cache/graph.sqlite`. If the DB file does not exist, the Code Mode startup sequence calls a bootstrap utility that walks the repo, parses frontmatter using Brief 1's definitions, and bulk-inserts using `insert_nodes_bulk`.
2.  **Ongoing Ingest:** We implement a `PostToolUse` hook (`hooks/graph_ingest.py`). When the LLM edits a Markdown file, the hook parses the file and executes an UPSERT Cypher query to reconcile the node and its immediate edges.
3.  **Rollback:** The SQLite graph is a *derived index*. If schema drift occurs or the DB corrupts, deleting `~/.agency-system/cache/graph.sqlite` and restarting the server forces a full `insert_nodes_bulk` rebuild from the canonical Markdown files.

## 8. Risks

*   **Project Maturity:** GraphQLite is currently version 0.4.4. The latest releases are active, but it has not reached 1.0. We will mitigate this by abstracting the Cypher execution behind our `graph_cypher` MCP tool. If GraphQLite becomes abandoned, we can swap the backend to Neo4j, Apache AGE, or kuzuDB with zero changes to the MCP tool signatures or the LLM's prompt behaviors.
*   **Concurrency with existing db_tools:** Music currently has `db_*` tools writing to bitwize databases. Since we isolated the graph DB to `graph.sqlite`, there is zero lock contention with bitwize SQLite databases.
*   **Binary Distribution:** The `graphqlite` Python package pre-compiles wheels for major platforms, but Alpine Linux or custom ARM devices might require Rust/C toolchains to compile from source. We must use `get_loadable_path()` provided by the package safely.

## 9. What GraphQLite Does NOT Replace
GraphQLite is an explicit, semantic graph engine.
*   It does **not** replace Brief 3's vector/embedding search (which handles semantic similarity: "find specs similar in meaning to X").
*   It does **not** replace Spec 111's BM25 search (which handles fuzzy text search: "find documents containing the word 'dramatica'").
*   It does **not** replace the file-system. Markdown files are the source of truth. GraphQLite is a disposable read-replica.

## 10. References
- colliery-io/graphqlite Github repo: `~/work/vendor/graphqlite`
- GraphQLite Python Bindings: `~/work/vendor/graphqlite/bindings/python`
- `Plan/000-overview.md` (lines 1-100)
- `Plan/003-unified-statecache-port/spec.md` (lines 1-50)
- `Plan/008-codemode-registry/spec.md` (lines 1-80)
- `Plan/111-context-mode-manifest/spec.md` (lines 1-100)
- `Plan/112-context-anchor-triad/spec.md` (lines 1-100)
- `Plan/113-context-cache-and-subscriptions/spec.md` (lines 1-100)
- `Plan/_research-briefs/01-centralized-ontology.md` (lines 1-100)
- `Plan/_research-briefs/02-agency-tooling-codemode.md` (lines 1-100)
# Cypher Support Reference

GraphQLite implements a substantial subset of openCypher. This page is a quick-reference index; details are in the sub-pages.

## Clauses

| Clause | Status | Notes |
|--------|--------|-------|
| `MATCH` | Supported | Node, relationship, variable-length, named path patterns |
| `OPTIONAL MATCH` | Supported | Left outer join semantics |
| `CREATE` | Supported | Nodes and relationships |
| `MERGE` | Supported | `ON CREATE SET`, `ON MATCH SET` |
| `SET` | Supported | Property assign, map replace (`=`), map merge (`+=`), label add |
| `REMOVE` | Supported | Property removal, label removal |
| `DELETE` | Supported | Nodes and relationships |
| `DETACH DELETE` | Supported | Cascading edge removal |
| `RETURN` | Supported | `AS`, `DISTINCT`, `ORDER BY`, `LIMIT`, `SKIP`, `*` |
| `WITH` | Supported | Aggregation, filtering, projection between clauses |
| `WHERE` | Supported | All predicates; pattern predicates |
| `UNWIND` | Supported | List expansion |
| `FOREACH` | Supported | Mutation inside list iteration |
| `UNION` / `UNION ALL` | Supported | |
| `LOAD CSV WITH HEADERS FROM` | Supported | Local file paths |
| `FROM` | Supported | Multi-graph queries (GraphQLite extension) |
| `CALL {}` subqueries | **Not supported** | |
| `CALL procedure` | **Not supported** | No procedure registry |
| `CREATE INDEX` | **Not supported** | Schema is managed automatically |
| `CASE` in `SET` | **Not supported** | Use `CASE` in `RETURN`/`WITH` instead |
| Nested `FOREACH` | **Not supported** | |
| `EXPLAIN` / `PROFILE` | **Not supported** | |

## Functions

| Category | Functions |
|----------|-----------|
| String | `toUpper`, `toLower`, `trim`, `ltrim`, `rtrim`, `btrim`, `substring`, `replace`, `reverse`, `left`, `right`, `split`, `toString`, `size`, `isEmpty`, `char_length`, `character_length` |
| Math | `abs`, `ceil`, `floor`, `round`, `sqrt`, `sign`, `log`, `log10`, `exp`, `e`, `pi`, `rand`, `toInteger`, `toFloat` |
| Trigonometry | `sin`, `cos`, `tan`, `asin`, `acos`, `atan`, `atan2`, `degrees`, `radians`, `cot`, `haversin`, `sinh`, `cosh`, `tanh`, `coth`, `isNaN` |
| List | `size`, `head`, `tail`, `last`, `range`, `collect`, `keys`, `reduce`, `[expr FOR x IN list [WHERE cond]]` |
| Aggregation | `count`, `sum`, `avg`, `min`, `max`, `collect`, `stdev`, `stdevp` |
| Entity | `id`, `elementId`, `labels`, `type`, `properties`, `startNode`, `endNode`, `nodes`, `relationships`, `length` |
| Type conversion | `toString`, `toInteger`, `toFloat`, `toBoolean`, `toStringOrNull`, `toIntegerOrNull`, `toFloatOrNull`, `toBooleanOrNull`, `valueType` |
| Temporal | `date`, `time`, `datetime`, `localdatetime`, `duration`, `datetime.fromepoch`, `datetime.fromepochmillis`, `duration.inDays`, `duration.inSeconds`, `date.truncate` |
| Spatial | `point`, `distance`, `point.withinBBox` |
| Predicate | `exists`, `coalesce`, `nullIf` |
| CASE | `CASE WHEN … THEN … END`, `CASE expr WHEN v THEN … END` |
| Graph algorithms | `pageRank`, `labelPropagation`, `louvain`, `dijkstra`, `astar`, `degreeCentrality`, `betweennessCentrality`, `closenessCentrality`, `eigenvectorCentrality`, `weaklyConnectedComponents`, `stronglyConnectedComponents`, `bfs`, `dfs`, `nodeSimilarity`, `knn`, `triangleCount`, `apsp`, `shortestPath` |

## Operators

| Category | Operators |
|----------|-----------|
| Arithmetic | `+`, `-`, `*`, `/`, `%` |
| Comparison | `=`, `<>`, `<`, `>`, `<=`, `>=` |
| Boolean | `AND`, `OR`, `NOT`, `XOR` |
| String | `STARTS WITH`, `ENDS WITH`, `CONTAINS`, `=~` (regex) |
| List | `IN`, `+` (concat), `[index]`, `[start..end]` (slice) |
| Null | `IS NULL`, `IS NOT NULL` |
| Property access | `.` (dot notation), `['key']` (subscript) |

## Not Supported

- `CALL {}` correlated subqueries
- `CALL procedure(...)` procedure invocations
- `CREATE INDEX ON :Label(prop)`
- `EXPLAIN` / `PROFILE`
- `CASE` expressions on the left-hand side of `SET`
- Nested `FOREACH`

## Sub-pages

- [Clauses](./cypher-clauses.md) — syntax, description, and examples for every clause
- [Functions](./cypher-functions.md) — signature, return type, and example for every function
- [Operators](./cypher-operators.md) — all operators with precedence table
# Graph Algorithms Reference

GraphQLite provides 18 built-in graph algorithms accessible via Cypher functions, the Python `Graph` API, and the Rust `Graph` API.

> For guidance on choosing the right algorithm for your use case, see [Using Graph Algorithms](../how-to/graph-algorithms.md).

---

## PageRank

**Cypher**

```cypher
CALL pageRank([damping, iterations]) YIELD node, score
```

**Python**

```python
graph.pagerank(damping=0.85, iterations=20)
```

**Rust**

```rust
graph.pagerank(damping: f64, iterations: usize) -> Result<Vec<PageRankResult>>
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `damping` | Float | `0.85` | Damping factor |
| `iterations` | Integer | `20` | Number of power iterations |

**Return shape**

Python: `list[dict]` with keys `node_id`, `user_id`, `score`

Rust: `Vec<PageRankResult>` — fields: `node_id: i64`, `user_id: String`, `score: f64`

**Complexity**: O(iterations × (V + E))

**Example**

```python
results = graph.pagerank(damping=0.85, iterations=30)
for r in sorted(results, key=lambda x: x['score'], reverse=True)[:5]:
    print(r['user_id'], r['score'])
```

---

## Degree Centrality

**Cypher**

```cypher
CALL degreeCentrality() YIELD node, in_degree, out_degree, degree
```

**Python**

```python
graph.degree_centrality()
```

**Rust**

```rust
graph.degree_centrality() -> Result<Vec<DegreeCentralityResult>>
```

**Parameters**: none

**Return shape**

Python: `list[dict]` with keys `node_id`, `user_id`, `in_degree`, `out_degree`, `degree`

Rust: `Vec<DegreeCentralityResult>` — fields: `node_id: i64`, `user_id: String`, `in_degree: usize`, `out_degree: usize`, `degree: usize`

**Complexity**: O(V + E)

**Example**

```python
for r in graph.degree_centrality():
    print(r['user_id'], 'in:', r['in_degree'], 'out:', r['out_degree'])
```

---

## Betweenness Centrality

**Cypher**

```cypher
CALL betweennessCentrality() YIELD node, score
```

**Python**

```python
graph.betweenness_centrality()
```

**Rust**

```rust
graph.betweenness_centrality() -> Result<Vec<BetweennessCentralityResult>>
```

**Parameters**: none

**Return shape**

Python: `list[dict]` with keys `node_id`, `user_id`, `score`

Rust: `Vec<BetweennessCentralityResult>` — fields: `node_id: i64`, `user_id: String`, `score: f64`

**Complexity**: O(V × E)

**Example**

```python
results = graph.betweenness_centrality()
```

---

## Closeness Centrality

**Cypher**

```cypher
CALL closenessCentrality() YIELD node, score
```

**Python**

```python
graph.closeness_centrality()
```

**Rust**

```rust
graph.closeness_centrality() -> Result<Vec<ClosenessCentralityResult>>
```

**Parameters**: none

**Return shape**

Python: `list[dict]` with keys `node_id`, `user_id`, `score`

Rust: `Vec<ClosenessCentralityResult>` — fields: `node_id: i64`, `user_id: String`, `score: f64`

**Complexity**: O(V × (V + E))

**Example**

```python
results = graph.closeness_centrality()
```

---

## Eigenvector Centrality

**Cypher**

```cypher
CALL eigenvectorCentrality([iterations]) YIELD node, score
```

**Python**

```python
graph.eigenvector_centrality(iterations=100)
```

**Rust**

```rust
graph.eigenvector_centrality(iterations: usize) -> Result<Vec<EigenvectorCentralityResult>>
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `iterations` | Integer | `100` | Power iteration count |

**Return shape**

Python: `list[dict]` with keys `node_id`, `user_id`, `score`

Rust: `Vec<EigenvectorCentralityResult>` — fields: `node_id: i64`, `user_id: String`, `score: f64`

**Complexity**: O(iterations × E)

---

## Louvain Community Detection

**Cypher**

```cypher
CALL louvain([resolution]) YIELD node, community
```

**Python**

```python
graph.louvain(resolution=1.0)
```

**Rust**

```rust
graph.louvain(resolution: f64) -> Result<Vec<CommunityResult>>
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `resolution` | Float | `1.0` | Resolution parameter controlling community granularity |

**Return shape**

Python: `list[dict]` with keys `node_id`, `user_id`, `community`

Rust: `Vec<CommunityResult>` — fields: `node_id: i64`, `user_id: String`, `community: i64`

**Example**

```python
communities = graph.louvain(resolution=0.5)
```

---

## Leiden Community Detection

**Python only**

```python
graph.leiden_communities(resolution=1.0, random_seed=None)
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `resolution` | Float | `1.0` | Resolution parameter |
| `random_seed` | Integer \| None | `None` | Seed for reproducibility |

**Return shape**: `list[dict]` with keys `node_id`, `user_id`, `community`

---

## Label Propagation

**Cypher**

```cypher
CALL labelPropagation([iterations]) YIELD node, community
```

**Python**

```python
graph.community_detection(iterations=10)
```

**Rust**

```rust
graph.community_detection(iterations: usize) -> Result<Vec<CommunityResult>>
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `iterations` | Integer | `10` | Maximum iterations |

**Return shape**

Python: `list[dict]` with keys `node_id`, `user_id`, `community`

Rust: `Vec<CommunityResult>` — fields: `node_id: i64`, `user_id: String`, `community: i64`

---

## Weakly Connected Components

**Cypher**

```cypher
CALL weaklyConnectedComponents() YIELD node, component
```

**Python**

```python
graph.weakly_connected_components()
```

**Rust**

```rust
graph.weakly_connected_components() -> Result<Vec<ComponentResult>>
```

**Parameters**: none

**Return shape**

Python: `list[dict]` with keys `node_id`, `user_id`, `component`

Rust: `Vec<ComponentResult>` — fields: `node_id: i64`, `user_id: String`, `component: i64`

**Complexity**: O(V + E)

---

## Strongly Connected Components

**Cypher**

```cypher
CALL stronglyConnectedComponents() YIELD node, component
```

**Python**

```python
graph.strongly_connected_components()
```

**Rust**

```rust
graph.strongly_connected_components() -> Result<Vec<ComponentResult>>
```

**Parameters**: none

**Return shape**

Python: `list[dict]` with keys `node_id`, `user_id`, `component`

Rust: `Vec<ComponentResult>` — fields: `node_id: i64`, `user_id: String`, `component: i64`

**Complexity**: O(V + E) (Tarjan or Kosaraju)

---

## Shortest Path

**Cypher (path function)**

```cypher
MATCH p = shortestPath((a)-[*]->(b))
RETURN p
```

**Cypher (Dijkstra)**

```cypher
CALL dijkstra(source, target[, weight_property]) YIELD path, distance
```

**Python**

```python
graph.shortest_path(source, target, weight_property=None)
```

**Rust**

```rust
graph.shortest_path(source: &str, target: &str, weight_property: Option<&str>) -> Result<ShortestPathResult>
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `source` | String | required | Source node user ID |
| `target` | String | required | Target node user ID |
| `weight_property` | String \| None | `None` | Edge property to use as weight; unweighted BFS if `None` |

**Return shape**

Python: `dict` with keys `path` (list of user IDs), `distance` (float), `found` (bool)

Rust: `ShortestPathResult` — fields: `path: Vec<String>`, `distance: f64`, `found: bool`

**Example**

```python
result = graph.shortest_path('alice', 'bob', weight_property='cost')
if result['found']:
    print(result['path'], result['distance'])
```

---

## A* (A-Star)

**Cypher**

```cypher
CALL astar(source, target[, lat_prop, lon_prop]) YIELD path, distance
```

**Python**

```python
graph.astar(source, target, lat_prop=None, lon_prop=None)
```

**Rust**

```rust
graph.astar(source: &str, target: &str, lat_prop: Option<&str>, lon_prop: Option<&str>) -> Result<AStarResult>
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `source` | String | required | Source node user ID |
| `target` | String | required | Target node user ID |
| `lat_prop` | String \| None | `None` | Node property for latitude |
| `lon_prop` | String \| None | `None` | Node property for longitude |

**Return shape**

Python: `dict` with keys `path`, `distance`, `found`, `nodes_explored`

Rust: `AStarResult` — fields: `path: Vec<String>`, `distance: f64`, `found: bool`, `nodes_explored: usize`

---

## All-Pairs Shortest Path

**Cypher**

```cypher
CALL apsp() YIELD source, target, distance
```

**Python**

```python
graph.all_pairs_shortest_path()
```

**Rust**

```rust
graph.all_pairs_shortest_path() -> Result<Vec<ApspResult>>
```

**Parameters**: none

**Return shape**

Python: `list[dict]` with keys `source`, `target`, `distance`

Rust: `Vec<ApspResult>` — fields: `source: String`, `target: String`, `distance: f64`

**Complexity**: O(V × (V + E))

---

## BFS (Breadth-First Search)

**Cypher**

```cypher
CALL bfs(start[, max_depth]) YIELD node, depth, order
```

**Python**

```python
graph.bfs(start, max_depth=-1)
```

**Rust**

```rust
graph.bfs(start: &str, max_depth: i64) -> Result<Vec<TraversalResult>>
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `start` | String | required | Starting node user ID |
| `max_depth` | Integer | `-1` | Maximum depth; `-1` means unlimited |

**Return shape**

Python: `list[dict]` with keys `user_id`, `depth`, `order`

Rust: `Vec<TraversalResult>` — fields: `user_id: String`, `depth: usize`, `order: usize`

---

## DFS (Depth-First Search)

**Cypher**

```cypher
CALL dfs(start[, max_depth]) YIELD node, depth, order
```

**Python**

```python
graph.dfs(start, max_depth=-1)
```

**Rust**

```rust
graph.dfs(start: &str, max_depth: i64) -> Result<Vec<TraversalResult>>
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `start` | String | required | Starting node user ID |
| `max_depth` | Integer | `-1` | Maximum depth; `-1` means unlimited |

**Return shape**: same as BFS — `list[dict]` / `Vec<TraversalResult>` with `user_id`, `depth`, `order`

---

## Node Similarity

**Cypher**

```cypher
CALL nodeSimilarity([node1, node2, threshold, top_k]) YIELD node1, node2, similarity
```

**Python**

```python
graph.node_similarity(node1_id=None, node2_id=None, threshold=0.0, top_k=0)
```

**Rust**

```rust
graph.node_similarity(node1_id: Option<i64>, node2_id: Option<i64>, threshold: f64, top_k: usize) -> Result<Vec<NodeSimilarityResult>>
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `node1_id` | Integer \| None | `None` | Fix first node; `None` means all pairs |
| `node2_id` | Integer \| None | `None` | Fix second node; `None` means all pairs |
| `threshold` | Float | `0.0` | Minimum similarity to include |
| `top_k` | Integer | `0` | Return at most `top_k` results; `0` means all |

**Algorithm**: Jaccard similarity based on shared neighbors.

**Return shape**

Python: `list[dict]` with keys `node1`, `node2`, `similarity`

Rust: `Vec<NodeSimilarityResult>` — fields: `node1: String`, `node2: String`, `similarity: f64`

---

## KNN (k-Nearest Neighbors)

**Cypher**

```cypher
CALL knn(node, k) YIELD neighbor, similarity, rank
```

**Python**

```python
graph.knn(node_id, k=10)
```

**Rust**

```rust
graph.knn(node_id: i64, k: usize) -> Result<Vec<KnnResult>>
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `node_id` | Integer | required | Source node internal ID |
| `k` | Integer | `10` | Number of neighbors to return |

**Return shape**

Python: `list[dict]` with keys `neighbor`, `similarity`, `rank`

Rust: `Vec<KnnResult>` — fields: `neighbor: String`, `similarity: f64`, `rank: usize`

---

## Triangle Count

**Cypher**

```cypher
CALL triangleCount() YIELD node, triangles, clustering_coefficient
```

**Python**

```python
graph.triangle_count()
```

**Rust**

```rust
graph.triangle_count() -> Result<Vec<TriangleCountResult>>
```

**Parameters**: none

**Return shape**

Python: `list[dict]` with keys `node_id`, `user_id`, `triangles`, `clustering_coefficient`

Rust: `Vec<TriangleCountResult>` — fields: `node_id: i64`, `user_id: String`, `triangles: usize`, `clustering_coefficient: f64`

**Complexity**: O(V × degree²)

**Example**

```python
for r in graph.triangle_count():
    print(r['user_id'], r['triangles'], r['clustering_coefficient'])
```
# Architecture Overview

GraphQLite adds a Cypher query language interface to SQLite by functioning as a transpiler: it parses Cypher, translates it to SQL, and executes the resulting SQL against a set of tables that represent a property graph. Understanding this pipeline helps you reason about query behaviour, error messages, and performance.

## Why a Transpiler, Not a Custom Engine

The most important architectural decision in GraphQLite is what it chose not to build: a dedicated graph storage engine or query runtime.

Building a purpose-built graph engine would require implementing disk layout, buffer management, query optimisation, transaction handling, concurrency control, and crash recovery. SQLite already provides all of this, and provides it correctly across a wide range of platforms, with a 35-year track record of reliability.

The transpiler approach means:

- **Durability and atomicity come for free.** Every write goes through SQLite's WAL and journalling machinery.
- **Standard tooling works.** The underlying tables are plain SQLite tables. You can inspect them with the SQLite CLI, use SQLite backup APIs, and attach the database to other tools.
- **Query execution is handled by a proven optimiser.** The generated SQL benefits from SQLite's query planner, covering indexes, and prepared statement caching.

The cost of this approach is translation overhead on every query, and the impedance mismatch between graph patterns and relational joins. Both are manageable: the translation is fast (typically under 1ms for simple queries), and the join structure is deterministic once you understand the EAV schema.

## The Query Pipeline

A Cypher query passes through four stages before results are returned:

```
Cypher string
      │
      ▼
┌─────────────────────────────────┐
│  1. PARSER                      │
│  cypher_gram.y + cypher_scanner.l│
│  ──────────────────────────────  │
│  Cypher string → AST nodes      │
└──────────────┬──────────────────┘
               │ ast_node tree
               ▼
┌─────────────────────────────────┐
│  2. TRANSFORMER                 │
│  transform_match.c, etc.        │
│  ──────────────────────────────  │
│  AST → SQL string               │
└──────────────┬──────────────────┘
               │ SQL string
               ▼
┌─────────────────────────────────┐
│  3. EXECUTOR                    │
│  cypher_executor.c              │
│  ──────────────────────────────  │
│  sqlite3_prepare + step         │
└──────────────┬──────────────────┘
               │ raw SQLite rows
               ▼
┌─────────────────────────────────┐
│  4. RESULT FORMATTER            │
│  executor_result.c, agtype.c    │
│  ──────────────────────────────  │
│  rows → JSON text returned      │
│  by the cypher() SQL function   │
└─────────────────────────────────┘
```

### Stage 1: The Parser

The parser is a Bison GLR grammar (`cypher_gram.y`) with a Flex scanner (`cypher_scanner.l`). It produces a typed AST: `ast_node` structs that include `cypher_query`, `cypher_match`, `cypher_create`, `cypher_return`, `cypher_node_pattern`, `cypher_rel_pattern`, and expression types like `cypher_binary_op`, `cypher_property`, `cypher_identifier`, and `cypher_literal_*`.

**Why GLR?** Cypher has syntactic ambiguities that a standard LALR(1) parser cannot resolve. The most visible example is that `(n)` is simultaneously valid as a parenthesised expression and as a node pattern. GLR allows the parser to pursue both interpretations in parallel and resolve the ambiguity once more context is available. The grammar currently declares `%expect 4` shift/reduce conflicts and `%expect-rr 3` reduce/reduce conflicts — these are known, documented, and intentional.

Identifiers can be regular alphanumeric names or backtick-quoted names (`BQIDENT`), which the scanner strips to their bare text. The `END_P` keyword is also permitted as an identifier through the grammar's `identifier` rule, allowing queries like `MATCH (n) RETURN n.end`.

Error recovery is handled at this stage. When parsing fails, `parse_cypher_query_ext()` returns a `cypher_parse_result` with a populated `error_message` containing position information, which propagates back to the `cypher()` SQL function as a SQLite error.

### Stage 2: The Transformer

The transformer walks the AST and emits SQL strings. It is not a general-purpose SQL generator: it knows the exact schema of GraphQLite's EAV tables and generates SQL specifically against those tables.

Key files and responsibilities:

| File | Responsibility |
|---|---|
| `cypher_transform.c` | Entry point; creates transform context |
| `transform_match.c` | MATCH patterns → SQL FROM/JOIN/WHERE |
| `transform_return.c` | RETURN items → SQL SELECT list |
| `transform_expr_ops.c` | Expression operators and property access |
| `transform_create.c` | CREATE → INSERT INTO nodes/edges/properties |
| `transform_set.c` | SET → UPDATE on property tables |
| `transform_delete.c` | DELETE → DELETE FROM |
| `transform_variables.c` | Variable-to-alias tracking across clauses |
| `sql_builder.c` | Dynamic string buffer for SQL construction |
| `transform_func_*.c` | Function dispatch (string, math, path, etc.) |

The transform context (`cypher_transform_context`) carries the SQL buffer being built, a variable context (`var_ctx`) that maps Cypher variable names to SQL table aliases, and flags like `in_comparison` that alter how property access is generated.

**Concrete translation example.** Consider:

```cypher
MATCH (a:Person)-[:KNOWS]->(b)
WHERE a.name = 'Alice'
RETURN b.name
```

The transformer produces SQL roughly equivalent to:

```sql
SELECT
  (SELECT COALESCE(
    (SELECT npt.value FROM node_props_text npt
     JOIN property_keys pk ON npt.key_id = pk.id
     WHERE npt.node_id = n2.id AND pk.key = 'name'),
    (SELECT CAST(npi.value AS TEXT) FROM node_props_int npi
     JOIN property_keys pk ON npi.key_id = pk.id
     WHERE npi.node_id = n2.id AND pk.key = 'name'),
    ...
  )) AS "b.name"
FROM nodes n1
JOIN node_labels nl1 ON nl1.node_id = n1.id AND nl1.label = 'Person'
JOIN edges e1 ON e1.source_id = n1.id AND e1.type = 'KNOWS'
JOIN nodes n2 ON n2.id = e1.target_id
WHERE (SELECT COALESCE(
    (SELECT npt.value FROM node_props_text npt
     JOIN property_keys pk ON npt.key_id = pk.id
     WHERE npt.node_id = n1.id AND pk.key = 'name'),
    ...
  )) = 'Alice'
```

Each property access becomes a correlated subquery that fans out across all five typed property tables (`node_props_text`, `node_props_int`, `node_props_real`, `node_props_bool`, `node_props_json`) using `COALESCE` to return whichever type holds the value. In comparison contexts (WHERE clauses) the types are preserved natively; in RETURN contexts everything is cast to text.

**Nested property access.** For expressions like `n.metadata.city` — where `metadata` is stored as a JSON blob — the transformer generates `json_extract(n_metadata_subquery, '$.city')`, recursively building the extraction path.

### Stage 3: The Executor

The executor orchestrates the full pipeline and manages the SQLite connection state. Its entry point is `cypher_executor_execute()`, which:

1. Calls `parse_cypher_query_ext()` to get the AST.
2. Calls `cypher_executor_execute_ast()` to dispatch on AST type.
3. For `AST_NODE_QUERY` and `AST_NODE_SINGLE_QUERY`, delegates to `dispatch_query_pattern()`.
4. `dispatch_query_pattern()` analyses the clause combination present in the query (MATCH, RETURN, CREATE, SET, DELETE, etc.) and selects the best-matching handler from the pattern registry.
5. The selected handler calls the appropriate transformer functions to produce SQL, then calls `sqlite3_prepare_v2()` and `sqlite3_step()` to execute it.
6. UNION queries bypass the pattern dispatcher and go directly through the transform layer, which handles them as a special `AST_NODE_UNION` case.

**EXPLAIN mode.** If the query starts with `EXPLAIN`, the executor runs the transformer but does not execute the SQL. Instead it returns a text result containing the matched pattern name, the clause flags, and the generated SQL string. This is useful for debugging unexpected behaviour.

### Stage 4: Result Formatting

Raw SQLite column values are formatted into JSON by `executor_result.c` and `agtype.c`. The `cypher()` SQL function always returns a JSON array of row objects:

```json
[{"b.name": "Bob"}, {"b.name": "Carol"}]
```

For rich graph objects (nodes and relationships returned as entities rather than scalar properties), the AGE-compatible `agtype` system serialises them with type annotations. Modification queries without a RETURN clause return a plain-text statistics string.

## Extension Architecture

GraphQLite loads into SQLite as a shared library extension. The entry point `sqlite3_graphqlite_init()` registers several SQL functions on the current database connection.

### Per-Connection Caching

The most important structural detail is the `connection_cache`:

```c
typedef struct {
    sqlite3 *db;
    cypher_executor *executor;
    csr_graph *cached_graph;
} connection_cache;
```

This struct is allocated once per database connection and registered via `sqlite3_create_function`'s user-data pointer. It holds:

- A `cypher_executor` instance, which in turn holds the schema manager and the property key cache. Because executors are expensive to create (schema initialisation, prepared statement allocation), they are created on the first call to `cypher()` and reused for all subsequent calls on the same connection.
- A `csr_graph` pointer for the in-memory graph needed by algorithm functions. This is `NULL` until the user explicitly calls `gql_load_graph()`.

When the database connection closes, SQLite calls the destructor registered with the function, which frees both the executor and any cached graph.

### Registered SQL Functions

The extension registers:

| Function | Purpose |
|---|---|
| `cypher(query)` | Execute a Cypher query, return JSON |
| `cypher(query, params_json)` | Execute with parameters |
| `graphqlite_test()` | Health check |
| `gql_load_graph()` | Build CSR from current tables, cache it |
| `gql_unload_graph()` | Free cached CSR graph |
| `gql_reload_graph()` | Invalidate and rebuild CSR cache |

Schema initialisation (`CREATE TABLE IF NOT EXISTS ...`) happens inside `cypher_executor_create()`, which is called on the first `cypher()` invocation. Extension loading takes approximately 5ms to complete this step.

## Language Bindings

Both the Python and Rust bindings wrap the `cypher()` SQL function rather than linking directly against GraphQLite's C API.

**Python.** `Connection._load_extension()` calls `sqlite3.Connection.load_extension()` with the path to `graphqlite.dylib` (or `.so`/`.dll`). After loading, every `connection.cypher(query, params)` call issues `SELECT cypher(?, ?)` against the underlying `sqlite3.Connection`. The JSON result is parsed and returned as a `CypherResult` object (a list of dicts). This means Python adds one round-trip through `sqlite3_exec` but no C-level coupling beyond the SQLite extension API.

**Rust.** The Rust binding uses `rusqlite` and similarly loads the extension via `Connection::load_extension()`. Cypher queries are executed as `SELECT cypher(?)` statements. Higher-level helpers in `src/` (graph operations, algorithm wrappers) build Cypher strings and parse the JSON results. The `Graph` struct maintains an open `rusqlite::Connection` with the extension already loaded.

## Graph Algorithm Integration

Graph algorithms (PageRank, Betweenness Centrality, Dijkstra, Louvain, etc.) operate on the CSR graph cache rather than on the EAV tables directly. The integration path is:

1. User calls `SELECT gql_load_graph()`. This reads all rows from `nodes` and `edges`, builds a CSR (Compressed Sparse Row) representation in heap memory, and stores it in `connection_cache.cached_graph`.
2. Each subsequent `cypher()` call syncs the `cached_graph` pointer into the current executor: `executor->cached_graph = cache->cached_graph`.
3. When the query dispatcher processes a RETURN-only query and finds a function name like `pageRank()` or `dijkstra()`, it dispatches to the graph algorithm subsystem instead of the normal SQL path.
4. The algorithm reads the CSR structure, runs its computation in C, and returns results as a JSON array, which is formatted and returned by the normal result formatter.

The CSR provides O(1) access to a node's neighbours (via the `row_ptr` and `col_idx` arrays), which is critical for iterative algorithms that traverse the graph many times. The EAV tables do not have this property — following an edge via SQL requires at minimum a B-tree lookup on `edges.source_id`.

If `gql_load_graph()` has not been called, algorithm functions will fail with an error indicating the graph is not loaded. After bulk inserts or other modifications, the cache must be explicitly refreshed with `gql_reload_graph()`.
# Storage Model

GraphQLite stores property graphs in SQLite using an Entity-Attribute-Value (EAV) schema. This document explains why that design was chosen, how the tables are structured, and what the trade-offs look like in practice.

## Why EAV?

A property graph has two requirements that are in tension with standard relational design:

1. **Schema flexibility.** Different nodes can have completely different properties. A `Person` node might have `name`, `age`, and `email`. A `Document` node might have `title`, `content`, and `created_at`. You cannot know the full set of property names at schema creation time.

2. **Type heterogeneity.** A property named `score` might be an integer on one node and a float on another. Cypher does not enforce types on property keys.

Three storage strategies are common:

| Strategy | Approach | Problem |
|---|---|---|
| Fixed schema | One table per node type | Requires schema migration for every new property; hard to query across types |
| JSON blob | Single `properties TEXT` column | No index support on property values; comparisons require full-table scans |
| EAV | Separate row per property | Flexible schema, indexable values, but more joins per query |

GraphQLite uses EAV. This trades query complexity (more JOIN operations per Cypher query) for schema flexibility and efficient indexed lookups on property values.

## Table Structure

### Core Tables

**`nodes`** is intentionally minimal:

```sql
CREATE TABLE nodes (
  id INTEGER PRIMARY KEY AUTOINCREMENT
);
```

A node is just an identity. All semantic content lives in the label and property tables. This allows the core table to stay compact and allows the autoincrement sequence to serve as a reliable surrogate key.

**`edges`** carries connectivity and type:

```sql
CREATE TABLE edges (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source_id INTEGER NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
  target_id INTEGER NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
  type TEXT NOT NULL
);
```

The relationship type (`KNOWS`, `FOLLOWS`, `WORKS_AT`, etc.) is stored inline because it is always present and is the primary filter when traversing the graph. The `ON DELETE CASCADE` constraints mean deleting a node automatically removes all its incident edges without requiring explicit cleanup in Cypher.

**`node_labels`** is a many-to-many table between nodes and labels:

```sql
CREATE TABLE node_labels (
  node_id INTEGER NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
  label TEXT NOT NULL,
  PRIMARY KEY (node_id, label)
);
```

A node can carry multiple labels (e.g., `Person` and `Employee`). The composite primary key prevents duplicate labels and serves as the natural index for label lookups.

**`property_keys`** is a normalisation table:

```sql
CREATE TABLE property_keys (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  key TEXT UNIQUE NOT NULL
);
```

Rather than storing the property key string (e.g., `"name"`) directly in every property row, GraphQLite stores an integer `key_id` and looks up the string once. This reduces storage for graphs with many nodes sharing the same property names, and enables the property key cache described below.

### Property Tables

There are ten property tables in total: five for nodes and five for edges. They follow the same pattern:

```sql
-- Node properties, integer values
CREATE TABLE node_props_int (
  node_id INTEGER NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
  key_id  INTEGER NOT NULL REFERENCES property_keys(id),
  value   INTEGER NOT NULL,
  PRIMARY KEY (node_id, key_id)
);

-- Node properties, text values
CREATE TABLE node_props_text (
  node_id INTEGER NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
  key_id  INTEGER NOT NULL REFERENCES property_keys(id),
  value   TEXT NOT NULL,
  PRIMARY KEY (node_id, key_id)
);

-- node_props_real, node_props_bool, node_props_json follow the same shape
-- edge_props_int, edge_props_text, edge_props_real, edge_props_bool, edge_props_json likewise
```

Booleans are stored as `INTEGER CHECK (value IN (0, 1))` because SQLite has no native boolean type. JSON values are stored as `TEXT CHECK (json_valid(value))` — the constraint ensures the stored bytes are parseable JSON.

## Why Separate Tables per Type?

The type-per-table design might seem verbose. Why not a single `node_props` table with a `type` discriminator column?

**Efficient indexes.** SQLite's B-tree indexes work best when a column contains values of a single type. An index on `node_props_int(key_id, value, node_id)` allows the query planner to use a range scan when evaluating `a.age > 30`. If integers and strings were mixed in one column, comparisons would degrade to text comparisons, silently changing semantics.

**No type coercion surprises.** SQLite's flexible type affinity means that storing `42` as text and later comparing it to the integer `42` would require careful `CAST`. Keeping types in separate tables makes the column's affinity unambiguous.

**COALESCE fan-out.** The transformer generates a `COALESCE(...)` that tries each type table in sequence and returns the first non-null result. This works correctly because a given `(node_id, key_id)` pair can exist in at most one type table — a property cannot simultaneously be an integer and a string.

## Property Type Inference

When Cypher writes a property, the type is inferred from the value:

| Value | Table |
|---|---|
| Integer literal (`42`) | `node_props_int` |
| Float literal (`3.14`) | `node_props_real` |
| `true` / `false` | `node_props_bool` |
| JSON object or array | `node_props_json` |
| Everything else | `node_props_text` |

Python's `bool` type is checked before `int` (since `bool` is a subclass of `int` in Python), so `True` goes to `_bool` rather than `_int`.

## Property Key Cache

Looking up a key's integer ID in `property_keys` is necessary for every property read or write. Without caching, a simple `MATCH (n) RETURN n.name, n.age` would issue two `SELECT id FROM property_keys WHERE key = ?` queries per result row, which becomes expensive when returning thousands of rows.

The schema manager maintains a hash table of 1024 slots using the djb2 algorithm:

```c
static unsigned long hash_string(const char *str) {
    unsigned long hash = 5381;
    int c;
    while ((c = *str++)) {
        hash = ((hash << 5) + hash) + c;  // hash * 33 + c
    }
    return hash;
}
```

Each slot holds a `property_key_entry` with the string and its integer ID. On a cache hit, no SQL is issued. On a miss, the key is looked up (or inserted) and the result is stored in the cache.

1024 slots is enough to cover most graphs without collision chains. A graph with 50 distinct property keys will have a load factor under 5%, meaning nearly every lookup resolves in O(1) without a collision. The cache is per-executor, which means per-connection — multiple connections to the same database file each maintain their own independent cache.

## How Property Access Translates to SQL

Consider `RETURN a.age` where `a` is a node. The full translation chain:

1. **Parser** produces an `AST_NODE_PROPERTY` node with `expr = identifier("a")` and `property_name = "age"`.
2. **`transform_property_access()`** checks whether the context is a comparison (`WHERE a.age > 30`) or a projection (`RETURN a.age`). This matters because comparisons need the native type, while projections cast everything to text for uniform JSON serialisation.
3. The transformer emits a correlated `SELECT COALESCE(...)` subquery that queries all five type tables:

```sql
(SELECT COALESCE(
  (SELECT npt.value
   FROM node_props_text npt
   JOIN property_keys pk ON npt.key_id = pk.id
   WHERE npt.node_id = a.id AND pk.key = 'age'),
  (SELECT CAST(npi.value AS TEXT)
   FROM node_props_int npi
   JOIN property_keys pk ON npi.key_id = pk.id
   WHERE npi.node_id = a.id AND pk.key = 'age'),
  (SELECT CAST(npr.value AS TEXT)
   FROM node_props_real npr
   JOIN property_keys pk ON npr.key_id = pk.id
   WHERE npr.node_id = a.id AND pk.key = 'age'),
  (SELECT CASE WHEN npb.value THEN 'true' ELSE 'false' END
   FROM node_props_bool npb
   JOIN property_keys pk ON npb.key_id = pk.id
   WHERE npb.node_id = a.id AND pk.key = 'age'),
  (SELECT npj.value
   FROM node_props_json npj
   JOIN property_keys pk ON npj.key_id = pk.id
   WHERE npj.node_id = a.id AND pk.key = 'age')
))
```

4. **SQLite executes** this subquery. Because the composite indexes on each property table include `(key_id, value, node_id)`, and `property_keys` has an index on `key`, the join between `property_keys` and the property table resolves via index lookup. SQLite evaluates the COALESCE branches lazily — once a branch returns a non-null value, the rest are skipped.

The result is that each property access is effectively two index lookups (one for the key ID, one for the value) in the common case.

## JSON and Nested Property Storage

Properties whose values are JSON objects or arrays are stored in `node_props_json` (or `edge_props_json`). The `CHECK (json_valid(value))` constraint on those tables ensures that only valid JSON is stored.

Nested access — `n.metadata.city` — is handled at transform time. When `transform_property_access()` sees that the base of a property access is itself a property access (i.e., the AST has `AST_NODE_PROPERTY` nested inside another `AST_NODE_PROPERTY`), it generates a `json_extract()` call:

```sql
json_extract(
  (SELECT COALESCE(...) WHERE pk.key = 'metadata'),
  '$.city'
)
```

This means `metadata` is fetched from `node_props_json` as a JSON text value, and `json_extract` then navigates into it. Deeper nesting (`n.a.b.c`) produces nested `json_extract` calls.

String-keyed subscripts like `n['metadata']` are normalised at transform time to behave identically to `n.metadata`. The `AST_NODE_SUBSCRIPT` case in `transform_expression()` checks whether the key is a string literal and, if so, converts it to a property access before generating SQL.

## Index Strategy

GraphQLite creates the following indexes at schema initialisation time:

| Index | Columns | Purpose |
|---|---|---|
| `idx_edges_source` | `edges(source_id, type)` | Outgoing traversal with type filter |
| `idx_edges_target` | `edges(target_id, type)` | Incoming traversal with type filter |
| `idx_edges_type` | `edges(type)` | Full-graph type scans |
| `idx_node_labels_label` | `node_labels(label, node_id)` | Label-to-node lookup |
| `idx_property_keys_key` | `property_keys(key)` | Key name to ID lookup |
| `idx_node_props_int_key_value` | `node_props_int(key_id, value, node_id)` | Covered index for int property filters |
| `idx_node_props_text_key_value` | `node_props_text(key_id, value, node_id)` | Covered index for text property filters |
| `idx_node_props_real_key_value` | `node_props_real(key_id, value, node_id)` | Covered index for real property filters |
| `idx_node_props_bool_key_value` | `node_props_bool(key_id, value, node_id)` | Covered index for bool property filters |
| `idx_node_props_json_key_value` | `node_props_json(key_id, node_id)` | JSON key scans (value omitted; not comparable) |
| *(same pattern for edge_props_\*)* | | |

The property indexes use a **covering index** pattern: `(key_id, value, node_id)`. When SQLite evaluates `WHERE a.age = 42`, it can satisfy the entire lookup from the index without touching the table heap — `key_id` filters to the right property, `value` satisfies the predicate, and `node_id` is the output needed to join back to the nodes table.

The JSON index omits the value because JSON blobs are not comparable as a unit; individual JSON paths are accessed via `json_extract()` at query time.

## Trade-offs

**Read performance.** A simple `MATCH (n:Person) RETURN n.name` requires a label scan via `idx_node_labels_label` plus one correlated subquery per returned property per row. For small graphs (under 100K nodes), this is fast. As the result set grows, the correlated subqueries become the bottleneck. The optimizer cannot always lift them into a join, though covering indexes mitigate this significantly.

**Write overhead.** Creating a single node with three properties requires:
- 1 insert into `nodes`
- 1 insert into `node_labels`
- Up to 3 inserts into `property_keys` (or cache hits)
- 3 inserts into the appropriate `node_props_*` tables

That is 7 or more inserts per node. For bulk loading, the Python and Rust bindings provide `insert_nodes_bulk()` and `insert_edges_bulk()` methods that bypass the Cypher parser and use direct SQL within a single `BEGIN IMMEDIATE` transaction. This is 100–500x faster than issuing `CREATE` queries through `cypher()`.

**Schema flexibility.** Adding new properties to existing nodes requires no migration. A `Person` node created yesterday with `name` and `age` can have `email` added tomorrow with no schema change. This is a significant advantage for evolving data models.

**Query complexity.** The generated SQL for even simple Cypher queries is verbose. This makes the `EXPLAIN` prefix particularly valuable: `EXPLAIN MATCH (a)-[:KNOWS]->(b) RETURN b.name` returns the generated SQL so you can understand exactly what SQLite will execute.
# Performance Characteristics

GraphQLite's performance profile is shaped by three factors: the overhead of the Cypher-to-SQL translation pipeline, the cost of the EAV schema's join-heavy queries, and the behaviour of the in-memory CSR cache for graph algorithms. Understanding these factors lets you make informed decisions about data loading, query structure, and when to reach for the bulk APIs.

## Benchmark Reference Numbers

These figures come from a single-core MacBook workload with an in-memory SQLite database (`:memory:`). Disk-backed databases will be faster with WAL mode enabled and slower when the OS page cache is cold.

| Operation | Typical latency |
|---|---|
| Extension loading (schema init) | ~5ms (once per connection) |
| Simple `CREATE (:Person {name: 'Alice'})` | 0.5–1ms |
| Simple `MATCH (n:Person) RETURN n.name` (10 nodes) | 0.5–2ms |
| `MATCH (a)-[:KNOWS]->(b) RETURN b.name` (100 relationships) | 1–5ms |
| Bulk insert via Python `insert_nodes_bulk()` | 100–500x faster than Cypher CREATE |
| `gql_load_graph()` on 100K nodes/edges | ~50–100ms |
| PageRank on 100K nodes | ~180ms |
| PageRank on 1M nodes | ~38s |
| Property key cache lookup (hit) | O(1), no SQL |
| Property key cache lookup (miss) | 1 SQL roundtrip to `property_keys` |

The 5ms extension loading cost is a one-time expense per connection. After the first `cypher()` call, the executor is cached and reused for all subsequent calls on the same connection.

## The CSR Graph Cache

Graph algorithms (PageRank, Dijkstra, Betweenness Centrality, Louvain, etc.) cannot run efficiently against the EAV tables. Finding a node's neighbours requires a B-tree lookup on `edges.source_id`, and iterative algorithms like PageRank traverse the full graph hundreds of times. At 1M nodes that would be hundreds of millions of B-tree lookups.

The CSR (Compressed Sparse Row) representation solves this. After `SELECT gql_load_graph()`, GraphQLite:

1. Reads all rows from `nodes` to build the node ID array.
2. Builds a hash table mapping node IDs to CSR array indices.
3. Reads all rows from `edges` twice: first to count out-edges per node (to compute row pointer offsets), then to fill the column index arrays.
4. Builds a parallel in-edges structure for algorithms that need reverse traversal.

The result is two arrays (`row_ptr` and `col_idx`) where `row_ptr[i]` is the offset in `col_idx` where node `i`'s neighbours begin, and `row_ptr[i+1] - row_ptr[i]` is its degree. Neighbour access is O(1): `col_idx[row_ptr[i] .. row_ptr[i+1]]`.

### When to Load

The cache must be loaded before running any algorithm, and must be refreshed after structural changes (adding or deleting nodes or edges). The cache persists for the lifetime of the connection; a stale cache causes algorithms to operate on the graph state at the time of the last load, silently ignoring newer data.

For cache management instructions — when and how to call `gql_load_graph()`, `gql_reload_graph()`, and `gql_unload_graph()` — see [Using Graph Algorithms](../how-to/graph-algorithms.md).

### Memory Implications

The CSR graph holds two integer arrays of length `edge_count` (for `col_idx` and `in_col_idx`) and one array of length `node_count + 1` (for `row_ptr` and `in_row_ptr`). For a graph with N nodes and E edges:

- `row_ptr` arrays: 2 × (N+1) × 4 bytes ≈ 8N bytes
- `col_idx` arrays: 2 × E × 4 bytes ≈ 8E bytes
- Node ID array: N × 4 bytes ≈ 4N bytes
- Hash table: ~4 × N × 4 bytes ≈ 16N bytes (open addressing, load factor ~25%)

A graph with 1M nodes and 5M edges uses approximately 60MB of heap memory for the CSR structure. The user-defined ID strings (if present) add additional allocation per node.

If memory is constrained, `gql_unload_graph()` can be called after algorithm runs to free the CSR heap allocation. The trade-off is that the next algorithm call will require a full reload from the database tables. On a 1M-node graph, `gql_load_graph()` takes approximately 50–100ms, so unloading between algorithm calls is only worthwhile when memory pressure is severe.

## Property Key Cache

Every property read or write needs the integer `key_id` for the property name. The property key cache uses djb2 hashing over 1024 slots, held in the `cypher_schema_manager` (which is per-executor, so per-connection).

A typical graph with 20–50 distinct property keys will have a cache load factor well under 10%, meaning:

- **Cache hit**: Hash the key string, index into the slot array, compare the stored string, return the `key_id`. Zero SQL.
- **Cache miss**: Hash lookup fails; issue `SELECT id FROM property_keys WHERE key = ?` (covered by `idx_property_keys_key`); store the result in the cache for future lookups.

Cache misses only occur for property keys not yet seen in this connection's session. After the first query that touches a given key, all subsequent accesses to that key on the same connection are cache hits.

The cache has no eviction policy — it grows monotonically, but with at most 1024 slots before collisions occur. For graphs with more than a few hundred distinct property key names, you may start seeing hash collisions. Collisions do not cause correctness problems (misses fall through to SQL), but they do degrade performance toward one SQL lookup per property access.

## Bulk Insert

The most important performance optimisation available to users is bypassing the Cypher pipeline entirely for bulk data loading.

Issuing `SELECT cypher('CREATE (:Person {name: "Alice", age: 30})')` for each node in a large graph is slow because each call:

1. Parses the Cypher string (Bison GLR parse).
2. Transforms the AST to SQL insert statements.
3. Executes three or more SQL statements (insert nodes, insert label, insert properties).
4. Formats the result.

The Python `insert_nodes_bulk()` and `insert_edges_bulk()` methods skip steps 1 and 2 entirely and batch all of step 3 inside a single `BEGIN IMMEDIATE` transaction:

```python
id_map = g.insert_nodes_bulk([
    ("alice", {"name": "Alice", "age": 30}, "Person"),
    ("bob",   {"name": "Bob",   "age": 25}, "Person"),
])
g.insert_edges_bulk([
    ("alice", "bob", {"since": 2020}, "KNOWS"),
], id_map)
```

The transaction amortises the cost of page writes across thousands of rows. The `id_map` dictionary eliminates the need for a `SELECT node_id FROM node_props_text WHERE value = ?` lookup per edge source and target.

Benchmarks show 100–500x throughput improvement for bulk loads compared to equivalent Cypher CREATE queries. For a graph with 100K nodes and 500K edges, bulk insert completes in seconds; Cypher CREATE would take minutes.

The Rust binding offers the equivalent `Graph::insert_nodes_bulk()` method with the same semantics.

## Index Utilisation

SQLite's query planner makes decisions based on index statistics. For GraphQLite's EAV schema, the most important index patterns are:

**Label filtering** (`MATCH (n:Person)`): Uses `idx_node_labels_label` which is `(label, node_id)`. The query `WHERE label = 'Person'` is a single B-tree range scan that returns all node IDs with that label. This is the primary entry point for most read queries.

**Property equality** (`WHERE n.age = 30`): The generated SQL contains a correlated subquery that filters `node_props_int` with `key_id = ? AND value = 30`. The covering index `idx_node_props_int_key_value` on `(key_id, value, node_id)` allows this to be satisfied entirely from the index, returning the `node_id` without a table heap read.

**Edge traversal** (`MATCH (a)-[:KNOWS]->(b)`): Uses `idx_edges_source` on `(source_id, type)` for outgoing traversal. The type filter is folded into the index scan. Incoming traversal uses `idx_edges_target` on `(target_id, type)`.

**When indexes are not used**: Range predicates on JSON properties (e.g., `WHERE n.metadata.city = 'London'`) require evaluating `json_extract()` for every row that passes the outer filter. SQLite cannot use a B-tree index to accelerate `json_extract()` comparisons without a generated column or expression index.

## SQLite-Specific Optimisations

**WAL mode.** For disk-backed databases with any level of concurrent access (even one writer, one reader), WAL mode allows readers to proceed while a writer is active. This is the most impactful single setting for mixed read/write workloads of Cypher queries.

**Prepared statements.** The `cypher_executor` caches the executor per connection. Within each query execution, the generated SQL is prepared and executed, but the prepared statement is finalised after each use because the generated SQL changes with each Cypher query. For repeated identical queries, this means the SQL planning cost is paid each time. If you are calling the same parameterised Cypher query many times (e.g., a lookup by ID), issuing the same query string with different parameter values — rather than constructing slightly different Cypher strings — allows SQLite's prepared statement cache to reuse the plan.

**Page cache.** SQLite's default page cache is 2MB (512 pages × 4KB). For graphs with many nodes, the EAV tables span many pages. A larger cache reduces I/O on repeated queries, with the trade-off of higher baseline memory use per connection.

**Synchronous mode.** Reducing the synchronous setting eliminates fsync calls and can roughly double write throughput for bulk loads. The trade-off is reduced durability: a crash during a write can leave the database in an inconsistent state. This setting is appropriate for analytics workloads on expendable data, but should never be used for production data without explicit acceptance of that risk.

For the specific PRAGMA values to use and when to apply each setting, see the [how-to guides](../how-to/graph-algorithms.md).

## Scaling Characteristics

**Under 10K nodes**: Performance is dominated by connection overhead and query parsing. The EAV join pattern is fast because the tables fit in the SQLite page cache. Simple MATCH+RETURN queries complete in under 1ms.

**10K–100K nodes**: Property lookup correlated subqueries become noticeable. Queries that return many rows with many properties per row can take 5–50ms. The covering indexes keep most lookups out of the table heap, but the sheer number of subquery evaluations adds up. Bulk insert becomes worthwhile at this scale.

**100K–1M nodes**: The EAV fan-out is the dominant cost. A full-graph scan (no label filter, no index pushdown) requires visiting every row in the relevant label and property tables. Graph algorithms should always operate via the CSR cache at this scale, not via Cypher queries that generate SQL. PageRank on 100K nodes via CSR takes ~180ms; the equivalent SQL-based traversal would be orders of magnitude slower.

**Above 1M nodes**: Memory usage for the CSR cache becomes significant (60MB+ for 1M nodes, 5M edges). Disk-backed databases benefit strongly from WAL mode and a large page cache. PageRank on 1M nodes takes ~38s on a single core. For workloads at this scale, consider whether batching algorithm results, pre-computing centrality scores and storing them as properties, or partitioning the graph into sub-graphs makes sense for your use case.

## Memory Usage Guidelines

| Component | Approximate size |
|---|---|
| `cypher_executor` struct | ~1KB (plus schema manager) |
| Property key cache (1024 slots) | ~50KB empty, grows with distinct keys |
| CSR graph (N nodes, E edges) | ~(20N + 8E) bytes |
| SQL buffer per query | 1–50KB depending on query complexity |
| Result data | Proportional to row count × column count |

For a graph with 100K nodes and 500K edges, the CSR cache uses approximately 6MB. The property key cache for a graph with 100 distinct property names uses approximately 100KB. The executor and schema manager overhead is negligible.
