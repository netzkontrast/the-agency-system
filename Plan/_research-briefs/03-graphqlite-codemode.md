---
type: research-brief
status: dispatched
slug: graphqlite-codemode
summary: "Jules research brief — clone colliery-io/graphqlite, read all docs, write a research report + draft Plan Spec 124 on integrating GraphQLite (SQLite + Cypher + graph algorithms) into the MCP Code Mode server as a cross-domain graph query layer over the centralized ontology."
dispatched_to: jules
dispatched_at: 2026-05-18
parent_specs: [003, 008, 111, 112, 113]
sibling_briefs:
  - 01-centralized-ontology.md
  - 02-agency-tooling-codemode.md
output_branch: research/graphqlite-codemode
output_files:
  - Plan/_research/graphqlite-codemode/findings.md
  - Plan/_research/graphqlite-codemode/draft-spec.md
---

# Research Brief — GraphQLite as the Plugin's Graph Query Layer

This is the prompt body dispatched to Jules via direct `jules_create`. Sibling briefs: `01-centralized-ontology.md` (data shape) and `02-agency-tooling-codemode.md` (validation/lint machinery). This brief adds the **query/traversal layer** that lets the model walk the ontology graph natively.

---

## 1. Goal (one sentence)

Produce a research findings document + a draft Plan spec (`spec_id: 124`, `slug: graphqlite-codemode`) that defines **how `colliery-io/graphqlite` (a SQLite extension exposing Cypher queries and built-in graph algorithms — PageRank, Louvain, Dijkstra, BFS/DFS, connected components) is adopted as the cross-domain graph query layer** for `the-agency-system` plugin's MCP Code Mode server — serving music, novel, jules, agentic, and shared content via one unified ontology graph.

## 2. Why this matters

Path B (Specs 111 → 112 → 113) gives the model a flat, BM25-searchable manifest. Brief 1 adds an ontology with declared edges (`header-ontology.json` — `prompt_uses_role`, `task_references_locks`, `spec_defines_gherkin`, `task_produced_friction_log`, `hook_invokes_skill`, `adr_supersedes_lock`, …). **Today there is no mechanism to query those edges.** The model can read a single entry's `neighbours: {…}` if Spec 112 is extended (Brief 1's recommendation), but it cannot ask:

- *"Find every spec whose `depends_on` transitively reaches Spec 008."* (Dijkstra / BFS on dependency DAG)
- *"Which skills are most referenced across the plugin?"* (PageRank over `skill_referenced_by` reverse edges)
- *"Cluster the music override files by co-citation."* (Louvain on `override_cited_by` edges)
- *"Give me every NCP `players[]` motivation tagged `topic:dramatica` reachable from this work."* (Cypher MATCH with property filters)
- *"What's the shortest provenance path from this Suno-generated track back to its source research brief?"* (Dijkstra weighted by edge type)

GraphQLite ([github.com/colliery-io/graphqlite](https://github.com/colliery-io/graphqlite), MIT, docs at <https://colliery-io.github.io/graphqlite/>) supplies all of this **inside the existing SQLite file**. The plugin already has SQLite at three points:

1. `Plan/003-unified-statecache-port/spec.md` — unified `state.json` (currently JSON, not SQLite — re-evaluate)
2. Music-side persistence (bitwize `db_*` tools — tweets, album state)
3. Spec 100 `session-log-mcp` SQLite event store (already approved)

GraphQLite is an SQLite *extension*, so it plugs into existing connections — no new database server, no schema migration risk if applied selectively, MIT-licensed (no Elastic 2.0 review).

The cross-domain payoff is large because **every domain has graph structure that's currently flat**:

| Domain | Existing graph (latent) | Cypher query the model could run |
|---|---|---|
| Music | track → album → artist; track → suno-prompt → genre; album → mastering-preset | "find every track on `Together We Confide` mastered with `darkwave-mastering-preset.yaml`" |
| Novel | work → chapter → scene; scene → NCP players → motivations; scene → throughline | "list scenes in `Chapter 3` that exercise both MC `Goal` and IC `Cost`" |
| Jules | spec → depends_on → spec (DAG); spec → friction-log → lesson | "show the depends_on closure of Spec 020" |
| Agentic | plan → workflow → step; research → finding → spec | "which research briefs informed Spec 020?" |
| Shared | skill → references → skill; override → cited_by → skill | "PageRank over the skill graph — top 10 most-cited" |

## 3. Required reading (in order)

1. **`colliery-io/graphqlite` repo** — clone, then read in this order:
   - `README.md` — feature overview, install, quick-start
   - `LICENSE` — confirm MIT (or whatever is current)
   - The full `docs/` tree (the website at <https://colliery-io.github.io/graphqlite/> is generated from there)
   - `python/` — Python binding source + examples
   - `rust/` — Rust crate source + examples (skim, not deep-dive — Python is the integration target)
   - `tests/` — what's covered, what's not (especially: durability, concurrency, schema-version compat with vanilla SQLite)
   - `examples/` — every example end-to-end
   - `CHANGELOG.md` — release cadence, stability signal
   - Any benchmark folder — query latency, write amplification vs vanilla SQLite
2. **GraphQLite docs site** (WebFetch, do not clone if already in repo `docs/`):
   - <https://colliery-io.github.io/graphqlite/> — landing page
   - Tutorials section in full
   - API reference (Cypher subset supported, function list, algorithm parameters)
   - Any "limitations" / "caveats" / "known issues" page — load explicitly
3. **External Cypher / graph-DB context:**
   - openCypher reference: <https://opencypher.org/resources/>
   - Comparison points (skim only): SQLite-vss (vector), DuckDB (analytics over SQLite), Apache AGE on Postgres (Cypher elsewhere), kuzu (embedded graph DB), Neo4j Cypher 9
4. **the-agency-system Plan/** — integration surfaces:
   - `Plan/000-overview.md` — full plugin architecture; SQLite touchpoints in §1
   - `Plan/003-unified-statecache-port/spec.md` — current state store (verify shape: JSON vs SQLite; this brief MUST reconcile)
   - `Plan/008-codemode-registry/spec.md` — Code Mode registry; eager / deferred / background classification
   - `Plan/100-session-log-mcp/spec.md` — SQLite event store; first natural host for graphqlite
   - `Plan/111-context-mode-manifest/spec.md` — flat manifest (currently no graph)
   - `Plan/112-context-anchor-triad/spec.md` — `context_search` / `context_describe` / `context_read`
   - `Plan/113-context-cache-and-subscriptions/spec.md` — cache + watcher
   - `Plan/_research-briefs/01-centralized-ontology.md` — type set + edge declarations (this brief is its query layer)
   - `Plan/_research-briefs/02-agency-tooling-codemode.md` — validators that populate the graph
5. **MUST-NOT do:**
   - Inline-paste GraphQLite source code into findings.md. Cite by path + line.
   - Read every test file in full — read the test catalogue, then ~5 representative tests.
   - Compare to `sqlite-vss` (vector) at length — that's Brief 3's territory (proposed, not yet dispatched).

## 4. Source clones (run first)

```bash
git clone --depth=1 --branch=main \
  https://github.com/colliery-io/graphqlite.git \
  ~/work/vendor/graphqlite

# Build / import smoke test (Python path):
cd ~/work/vendor/graphqlite/python
python3 -c "import graphqlite; print(graphqlite.__version__)" || echo "BLOCKED: import failed — record exact error in PR Confidence"
```

If the import fails on the Jules runner, **open a draft PR labelled `[BLOCKED: graphqlite-install]`** with the exact stderr and stop. Do not synthesize integration details against an extension you couldn't load.

Never commit `~/work/vendor/graphqlite/` into the plugin tree.

## 5. Output

Two files on a new branch `research/graphqlite-codemode` **rebased onto `claude/document-context-mode-specs-qX8h7`** (NOT `Master` — match siblings):

### 5.1 `Plan/_research/graphqlite-codemode/findings.md`

A research report (~700–1400 lines). Structure:

1. **Executive summary** (≤300 words) — adopt / partial-adopt / reject recommendation with the single biggest risk and the single biggest win.
2. **What GraphQLite is**
   - Architectural shape: SQLite loadable extension; how Python binding wraps it; what API surface looks like end-to-end
   - Cypher subset supported (verbatim list of clauses); what's NOT supported (subqueries? procedures? OPTIONAL MATCH? path comprehension?)
   - Built-in algorithms — for each (PageRank, Louvain, Dijkstra, BFS, DFS, connected components, plus any others): parameters, complexity, in-memory vs streaming, deterministic vs not, suitable graph sizes
   - Concurrency model — does the extension hold the SQLite write lock for the duration of a Cypher query? WAL compatibility? Thread-safety?
   - Durability — does it survive crash recovery? Are graph indices rebuilt on open?
3. **Schema model**
   - How nodes / edges are physically stored (tables? virtual tables? blobs?)
   - How node/edge properties map to columns
   - Whether labels are typed columns or string property tags
   - Reverse-edge handling (does it auto-maintain reverse, or must the writer insert both directions?)
   - Index strategy (B-tree on `id`? Edge-by-label?)
   - **Concrete mapping table** from Brief 1's L1+L2 frontmatter ontology → graphqlite schema. One row per type. Include `id`, `type`, all L1 fields, all L2 namespaced fields, every edge key from `header-ontology.json`.
4. **Code Mode integration design**
   - The single SQLite file question: one DB shared across `session-log` + `statecache` + `ontology-graph`, or three separate DBs? Document the tradeoff (write contention vs. atomic cross-table transactions).
   - **Tools to register** — propose 3–5 eager anchors + N deferred tools (per overview §2.1):
     - `graph_cypher(query: str, params: dict = {}, limit: int = 100, dry_run: bool = False) -> ToolResult` — eager
     - `graph_describe_node(id: str, expand: int = 1) -> NodeWithNeighbours` — eager
     - `graph_run_algorithm(algo: Literal["pagerank","louvain","shortest_path","bfs","dfs","components"], scope: dict, params: dict = {}) -> AlgoResult` — eager
     - `graph_ingest_frontmatter(path: str, dry_run: bool = True) -> IngestPlan` — deferred (Brief 2 territory; declare interface only)
     - `graph_export(format: Literal["jsonld","graphml","cypher"], filter: dict = {}) -> bytes` — deferred
   - Tool naming: snake_case `graph_<verb>_<object>` per overview §2.1 #1. Tags: `tags={"domain:shared", "kind:graph"}`. Docstrings ≤120 chars.
   - Classification in `codemode/manifest.json`: which tools are `always_eager` (the cypher anchor + describe-node), which are `deferred`, which are `background` (e.g. PageRank on a 10k-node graph).
   - **`dry_run` semantics** (overview §2.1 #7): writes via Cypher (CREATE / MERGE / SET / DELETE) MUST honour dry-run and return `{would_apply, diff, warnings}` without commit.
   - **`return_plan` semantics** (overview §2.1 #8) for `graph_run_algorithm` when run against an unbounded scope.
5. **Path B integration** — bind to Specs 111/112/113:
   - Spec 111 `context_manifest.json` ingestion: how the manifest entries + their `views` + their inferred edges populate the graph (`graph_ingest_frontmatter` over the manifest).
   - Spec 112 `context_describe(id)` extended response: `neighbours: { incoming: [...], outgoing: [...] }` — computed via `graph_describe_node(id, expand=1)`.
   - Spec 113 watcher: on `ChangeEvent(modified|added|deleted)`, re-ingest the changed entry into the graph (incremental, not full rebuild) and invalidate any cached Cypher result that touches that node.
6. **Cross-domain examples** — produce one worked end-to-end Cypher query per domain (music, novel, jules, agentic, shared), with the schema lookup, the Cypher text, and the expected result shape. Use real plugin content (e.g. ask "shortest dependency path from Spec 020 to Spec 003").
7. **Migration strategy**
   - Schema bootstrap: where does the graph DB live? (`~/.agency-system/cache/graph.sqlite`?)
   - Initial ingest: how do we walk the existing tree and populate the graph the first time? (Use Brief 1's L1 + L2 frontmatter as the typed source; Brief 2's validator gates ensure schema conformance.)
   - Ongoing ingest: PostToolUse hook (`hooks/graph_ingest.py`) on every Markdown Write/Edit.
   - Rollback: how to drop the graph DB and rebuild without losing source-of-truth content. The frontmatter is canonical; the graph is a derived index.
8. **Risks**
   - **Project maturity** — explicit assessment: latest tag, contributor count, issue triage cadence, last commit. If alpha/pre-1.0, propose a "wrap behind an interface" pattern so we can swap for kuzu / Neo4j-embedded later.
   - SQLite version requirements (does it need 3.45+? statically linked or system?)
   - Binary distribution for users (PyPI wheels for every CPython × OS combo? Or compile-on-install?)
   - Concurrency with the existing music-side `db_*` tools — can graphqlite share their SQLite handle?
   - Backup / restore — does `.dump` produce a portable file the same way vanilla SQLite does?
9. **What graphqlite does NOT replace** — clarify scope vs. Brief 3 (embeddings/vectors), vs. BM25 in Spec 111, vs. the file-system as source of truth.
10. **References** — every URL, file path, line number, commit SHA, doc-site anchor cited.

### 5.2 `Plan/_research/graphqlite-codemode/draft-spec.md`

A draft Plan spec following the exact template of `Plan/111-context-mode-manifest/spec.md`. Apply **`spec-skill` BCP-14 conventions** (MUST / SHOULD / MAY) in Done When + Approach. Frontmatter:

```yaml
spec_id: 124
slug: graphqlite-codemode
status: draft
owner: jules
depends_on: [008, 100, 111, 122]   # 122 = Brief 1's draft (ontology types)
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
  - graphqlite @ main  # https://github.com/colliery-io/graphqlite
estimated_jules_sessions: 3
domain: cross
wave: D
```

Acceptance (Gherkin) — minimum 7 scenarios:
- `graph_cypher` with a read-only `MATCH` returns rows in ≤ 100 ms on a 10k-node graph
- Write Cypher (`CREATE … RETURN id`) with `dry_run=True` returns `{would_apply, diff, warnings}` without mutating the DB
- `graph_describe_node(id, expand=1)` returns the node + its immediate neighbours in both directions
- `graph_run_algorithm("pagerank", scope={"type": "skill"})` returns scores summing to ≈ 1.0
- A modified Markdown file triggers `hooks/graph_ingest.py` and the node's properties update within 500 ms
- An unparseable Cypher query returns `{ok: False, error: "<exact graphqlite error>"}` (NOT an exception)
- Boot-token budget: adding the graph anchors keeps `tools/list` ≤ 1.10× pre-graph baseline (per Spec 112's 1.05× regression bar + a 5 % allowance for this larger anchor set)

## 6. Acceptance — when is this brief "done"?

- [ ] `Plan/_research/graphqlite-codemode/findings.md` exists, ≥ 700 lines, every required-reading source cited at least once by path + line.
- [ ] `Plan/_research/graphqlite-codemode/draft-spec.md` exists, follows the Spec 111 template, passes spec-skill BCP-14 audit.
- [ ] Confidence section in the PR includes the `python3 -c "import graphqlite; print(graphqlite.__version__)"` output and the project's latest release tag + date.
- [ ] PR opened from `research/graphqlite-codemode` → `claude/document-context-mode-specs-qX8h7` (NOT `Master`) with Gates 1–4 in the body.
- [ ] No code under `servers/agency-mcp/` modified. Research-only.
- [ ] `~/work/vendor/graphqlite/` not committed.

## 7. Anti-patterns (Jules MUST NOT)

- Adopt graphqlite as a hard runtime dependency without flagging its maturity assessment (§8 of findings).
- Propose schema migrations on Spec 003's StateCache without explicitly reading `Plan/003-unified-statecache-port/spec.md` and reconciling the JSON-vs-SQLite question.
- Skip the dry-run discipline — every write-capable tool MUST honour `dry_run`.
- Inline Cypher result data into findings.md beyond ~10 rows per example.
- Compete with Brief 3's embedding/vector research (don't propose graph-as-vector replacement).
- Open the PR before the `graphqlite` import works end-to-end on the runner.

## 8. Estimated effort

1 Jules session for the research + draft spec; ~5–7 hours wall-clock. If the import smoke test fails, that session terminates at `[BLOCKED:graphqlite-install]` and recovery is a separate session, not a re-dispatch.
