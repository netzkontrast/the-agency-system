---
spec_id: 124
slug: graphqlite-codemode
status: draft
owner: jules
depends_on: [008, 100, 111, 122]
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
source-repos:
  - graphqlite @ main
estimated_jules_sessions: 3
domain: cross
wave: D
---

> **Jules: read `Plan/JULES_PROTOCOL.md` before starting.** Run gates 1→4 in order:
> (1) Confidence ≥ 0.90, (2) TDD Red-Green-Refactor, (3) Evidence pasted under `## Evidence`, (4) Self-Review answered.
> Branch: `claude/document-context-mode-specs-qX8h7`. Only modify paths under `affects:` below.
> Source repos under `source-repos:` are clone-and-read-only into `~/work/vendor/`; never commit them.
> If anything is ambiguous, open a draft PR labelled `[BLOCKED: clarification]` and stop — do not guess.

# Spec 124 — GraphQLite Code Mode Integration

## Why

The plugin's unified ontology (Brief 1 / Spec 122) structures the relationships across music, novel, jules, and agentic domains. However, Path B (Specs 111-113) only provides a flat, BM25-searchable text manifest. To unlock the value of the ontology graph, we need a query mechanism. By integrating `colliery-io/graphqlite` as an SQLite loadable extension, we gain the ability to execute expressive Cypher queries (`MATCH`) and standard graph algorithms (PageRank, Shortest Path) over our data. This allows the model to answer complex relational questions (e.g., shortest dependency path between specs) entirely locally without requiring heavy external graph database servers like Neo4j.

## Done When

- [ ] `graphqlite` is added as a dependency in `servers/agency-mcp/pyproject.toml`.
- [ ] A dedicated SQLite graph database is initialized at `~/.agency-system/cache/graph.sqlite` upon MCP server boot.
- [ ] Three eager anchor tools (`graph_cypher`, `graph_describe_node`, `graph_run_algorithm`) are registered and classified in `codemode/manifest.json`.
- [ ] `graph_cypher` supports `dry_run=True`, which MUST NOT mutate the database.
- [ ] `hooks/graph_ingest.py` is created and wired to trigger upon changes to files.
- [ ] `graph_describe_node(id, expand=1)` retrieves a node and its immediate inbound/outbound neighbours.
- [ ] `pytest` integration tests verify Cypher read/write operations and graph algorithm accuracy.
- [ ] Boot token budget impact of the graph anchors MUST keep `tools/list` within 1.10× of the pre-graph baseline.

## Source clones (run first)

```bash
git clone --depth=1 --branch=main \
  https://github.com/colliery-io/graphqlite.git \
  ~/work/vendor/graphqlite
```

If the import smoke test fails on the Jules runner, open a draft PR labelled `[BLOCKED: graphqlite-install]` and stop.

## Files

- **Create**:
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
- **Modify**:
  - `servers/agency-mcp/pyproject.toml`
  - `servers/agency-mcp/src/agency_mcp/codemode/manifest.json`
  - `servers/agency-mcp/src/agency_mcp/server.py`
  - `hooks/hooks.json`
- **Delete**: none.

## Approach

1. **Gate 1 — Confidence.** Verify `graphqlite` can be imported via a smoke test (`python3 -c "import graphqlite"`). Document the release tag and verify MIT license. Review `servers/agency-mcp/pyproject.toml` to ensure no copyleft conflicts.
2. **Schema and Connection Setup.** In `schema.py`, establish the `GraphManager` pointing to `~/.agency-system/cache/graph.sqlite`. Define the schema mapping from Brief 1's L1/L2 frontmatter into `GraphQLite` `(label, properties, type)`.
3. **Graph Tools Implementation.**
   - Implement `graph_cypher` in `anchors.py`. It MUST honor `dry_run=True` by prepending `EXPLAIN` to mutating queries and returning the parsed execution plan instead of mutating.
   - Implement `graph_describe_node(id, expand=1)` to fetch a node and its adjacent edges in both directions.
   - Implement `graph_run_algorithm` in `algorithms.py`. Support `pagerank`, `louvain`, `shortest_path`, `bfs`, `dfs`, and `components`. If the target scope is large, the tool MUST utilize `return_plan` semantics.
4. **Ingestion Hooks.** Implement `graph_ingest.py` and register it in `hooks.json` as a `PostToolUse` hook triggered when Markdown files are edited. It MUST map the file's L1 and L2 frontmatter keys to graph node properties, and its relationship headers to directed Cypher edges.
5. **Code Mode Classification.** Update `codemode/manifest.json` to include the new `graph_*` tools. `graph_cypher` and `graph_describe_node` are `eager`. `graph_run_algorithm` is `background` (with a status companion). `graph_ingest_frontmatter` is `deferred`.
6. **Path B Integration.** Modify `server.py` to intercept file change notifications from Spec 113's watcher. When the watcher emits an event, trigger an incremental graph update rather than a full rebuild. Ensure Spec 112's `context_describe(id)` fetches the `neighbours` property via `graph_describe_node`.
7. **TDD — Gate 2.** RED: Write unit tests `test_schema.py` and `test_anchors.py`. Write integration tests verifying Cypher roundtrip queries (`CREATE`, `MATCH`) and that graph algorithms yield mathematically sensible results (e.g., PageRank summing to 1.0). Write a performance test verifying that `graph_cypher` reads return under 100ms. GREEN: Implement features to pass tests. REFACTOR: DRY up Cypher query building.
8. **Gate 3 — Evidence.** Provide output of test runs. Paste stdout showing boot-token budget validation demonstrating `< 1.10x` impact on the `tools/list` payload.
9. **Gate 4 — Self-Review.** Verify the 4 protocol gates. Explicitly assess any schema mapping discrepancies from upstream frontmatter and document them in the PR body.

## Acceptance (Gherkin)

```gherkin
# anchor: 124.1
Scenario: graph_cypher read operation performance
  Given a populated graph database with 10,000 nodes
  When a read-only MATCH Cypher query is executed via graph_cypher
  Then the response rows are returned in ≤ 100 ms

# anchor: 124.2
Scenario: graph_cypher honors dry_run
  Given the caller executes graph_cypher with CREATE ... RETURN id and dry_run=True
  When the tool processes the request
  Then the graph database is not mutated
  And the tool returns a structure containing {would_apply, diff, warnings}

# anchor: 124.3
Scenario: graph_describe_node retrieves neighbours
  Given a node exists with incoming and outgoing relationships
  When graph_describe_node is called with expand=1
  Then the tool returns the node properties
  And it returns lists of immediate neighbours in both directions

# anchor: 124.4
Scenario: PageRank execution yields normalized scores
  Given graph_run_algorithm is called with algo="pagerank" and scope={"type": "skill"}
  When the algorithm completes
  Then the algorithm returns scores for nodes in the scope
  And the sum of all scores is ≈ 1.0

# anchor: 124.5
Scenario: Ingest hook triggers on Markdown modification
  Given a Markdown file containing L1 frontmatter
  When the file is modified
  Then hooks/graph_ingest.py is triggered
  And the corresponding graph node's properties are updated within 500 ms

# anchor: 124.6
Scenario: Graceful error handling on bad Cypher
  Given an unparseable Cypher query is passed to graph_cypher
  When the tool executes
  Then it returns {ok: False, error: "<exact graphqlite error>"}
  And it does not raise an unhandled exception

# anchor: 124.7
Scenario: Boot token budget restriction
  Given the graph anchors are added to the Code Mode manifest
  When tools/list is called
  Then the token size of the response is ≤ 1.10× the pre-graph baseline
```

## Out of scope
- Replacing BM25 text search (Spec 111) or semantic embedding vector search.
- Altering the foundational JSON vs SQLite storage model of Spec 003's `StateCache`.
- Attempting to load the entire graph structure into the LLM context window.

## References
- `Plan/008-codemode-registry/spec.md`
- `Plan/100-session-log-mcp/spec.md`
- `Plan/111-context-mode-manifest/spec.md`
- `Plan/_research-briefs/01-centralized-ontology.md`
- GraphQLite documentation: https://colliery-io.github.io/graphqlite/
