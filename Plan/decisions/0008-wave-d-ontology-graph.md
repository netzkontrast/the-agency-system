---
slug: 0008-wave-d-ontology-graph
type: adr
status: ready
owner: claude
created: 2026-05-19
updated: 2026-05-19
domain: shared
wave: A
adr_id: ADR-0008
adr_status: Proposed
adr_supersedes: []
adr_superseded_by: []
related:
  - 2026-05-19-agency-base-canvas
  - harness-vocabulary
  - 122-centralized-ontology
  - 124-graphqlite-codemode
  - 0004-anchor-triad-as-wire-form
  - 0006-frontmatter-canon
summary: Adopt an 18-type node ontology backed by a GraphQLite Cypher store at `state/graph.sqlite`; PostToolUse hook ingests frontmatter on write; backs `agency_skill_search` ranking.
---

# ADR-0008 — Wave D ontology graph + GraphQLite Cypher

## Context and Problem Statement

Cross-domain links in this corpus today are prose-only. A spec citing `related: [023, 131]` is a list of slugs the reader resolves by grep. The `agency_skill_search` anchor tool (ADR-0004) must rank candidates somehow — without a graph, it falls back to substring matching on the manifest, which loses semantic adjacency (e.g. "this skill is downstream of that one" is unreachable from substring). Specs 122 (`122-centralized-ontology`) and 124 (`124-graphqlite-codemode`) already exist as point fixes: spec 122 defines an 18-type node ontology; spec 124 specifies a GraphQLite Cypher backing store. Neither has shipped. The reviewer's canvas-v1 critique scored graph discovery **0/3** — none of the three pieces (ontology, store, hook-driven ingest) were specified end-to-end.

Canvas §8 ("The Wave D graph — graph-discovery restored") folds specs 122 + 124 into the base and specifies the missing third piece: a PostToolUse hook (`graph_ingest.py`) that walks frontmatter on every `Write` and updates the graph. With all three in place, `agency_skill_search` can execute Cypher queries (e.g. *"return skills that share a `related:` edge with the current skill"*).

## Decision Drivers

- Canvas §1 pillar 5 ("One Graph — Wave D ontology").
- Canvas §8 — specifies the 18-type ontology, the edge types, the backing store, and the hook-driven refresh path verbatim.
- Spec 122 — pre-existing 18-type node schema; canvas §8 promotes it.
- Spec 124 — pre-existing GraphQLite Cypher backing; canvas §8 promotes it.
- ADR-0004 — `agency_skill_search` needs a ranking surface beyond substring; the graph is it.
- ADR-0006 — the PreToolUse hook gates frontmatter shape on write; the PostToolUse hook on the same event ingests it into the graph. The two hooks share an event but not a concern.
- Research brief 01 (`Plan/_research-briefs/01-centralized-ontology.md`) — the research basis for the 18-type schema.

## Considered Options

### Option A — 18-type node ontology + GraphQLite Cypher + hook-driven refresh (RECOMMENDED)

Schema lives at `lib/schemas/ontology-node.schema.json` and `ontology-edge.schema.json`. Backing store is `state/graph.sqlite` (GraphQLite SQLite extension, ~50 MB ceiling per spec 124). Built by `bin/agency-build-graph` from frontmatter + manifest + commits. Refreshed by a PostToolUse hook (`hooks/graph_ingest.py`) that ingests on every `Write` to a frontmatter-bearing file. Query surface: `agency_skill_search` + `agency_tool_search` execute Cypher (`MATCH (s:Skill)-[:RELATED_TO]->(:Skill {name:$intent}) RETURN s`); fall back to manifest scan when the graph is cold.

Node types (18, per spec 122): `Plugin, Domain, Tool, Skill, Reference, Schema, Spec, ADR, Lesson, ResearchBrief, SessionState, Override, State, Manifest, Handler, Hook, Template, Test`.
Edge types: `RELATED_TO, PREREQUISITE_OF, SUPERSEDES, USES_SCHEMA, AFFECTS, DISPATCHES, VALIDATES, REVIEWED_BY, ANCHORED_BY`.

### Option B — No graph (manifest only)

Stay with the flat manifest. `agency_skill_search` ranks by substring match. Zero infrastructure cost. Forfeits semantic adjacency forever.

### Option C — In-memory graph (no SQLite)

Build the graph at MCP boot, hold in process memory. No disk dependency. Loses persistence — every cold start re-walks frontmatter (~80 artefacts × parse cost). Loses cross-session query history. Forfeits Cypher (in-memory libraries are weaker on query semantics).

### Option D — Full triple-store (RDF + SPARQL)

Heavier semantic stack — RDF triples, SPARQL queries, named-graph isolation. Stronger for cross-corpus federation; overkill for one repo. Higher dependency footprint, higher author learning cost.

## Decision Outcome

**Chosen: Option A — 18-type ontology + GraphQLite Cypher + PostToolUse ingest hook.**

- Node schema: `lib/schemas/ontology-node.schema.json`; 18 types per spec 122.
- Edge schema: `lib/schemas/ontology-edge.schema.json`; nine edge types per canvas §8.
- Backing store: `state/graph.sqlite` (GraphQLite extension); 50 MB soft ceiling per spec 124.
- Builder: `bin/agency-build-graph` (canvas §13 spec 008) walks frontmatter + manifest + commits.
- Hook: `hooks/graph_ingest.py` (PostToolUse) fires on `Write` to any frontmatter-bearing file; idempotent UPSERT against the SQLite store.
- Decorator emission: `@domain_tool` (ADR-0005) emits `:Tool` and `:Handler` nodes plus their `:USES_SCHEMA` and `:RELATED_TO` edges at registration time.
- Query path: `agency_skill_search` and `agency_tool_search` (ADR-0004) execute Cypher when the graph is warm; fall back to manifest substring scan when cold.
- Reviewer score: spec 122 + spec 124 + this ADR closes the 0/3 graph-discovery gap to 3/3 once shipped.

## Consequences

### Positive

- `agency_skill_search` gets a real ranking surface — semantic adjacency, not substring. The router's "what next?" query (ADR-0001 step 2) becomes a Cypher path-find instead of a heuristic.
- `related:` and `supersedes:` reciprocity (VOCABULARY §6B) becomes graph-queryable, not grep-checkable — successor of spec 134's per-pair checker.
- Wave D landing in the base layer means downstream skills can assume the graph exists; no per-skill "is the graph available?" branching.
- The PostToolUse hook makes ingest automatic — no "you forgot to run `agency-build-graph`" failure class.

### Negative

- GraphQLite Cypher is a non-stdlib dependency. Installation cost on dev boxes; some friction on CI. Mitigation: optional, with manifest-scan fallback when the extension is missing.
- The 50 MB SQLite store is per-repo state; it must be `.gitignore`'d or it bloats the repo. The state cache is rebuildable from frontmatter, so loss is recoverable but inconvenient.
- The PostToolUse hook runs on every `*.md` write — perceptible latency on large frontmatter (rare; most artefacts are small). Hook errors must be non-fatal or every write becomes a failure surface.
- Cypher is an additional query language for authors to learn. The router and search tools hide it; advanced cross-domain queries do not.
- 18 node types is genuinely large. Some types (e.g. `Hook`, `Template`) will have few instances; the schema may feel over-engineered for small corpora.

### Neutral

- The graph does not change any wire shape — `agency_skill_search` returns the same `ToolResult` whether backed by graph or fallback.
- Node types can be added in a successor ADR; the schema's `$defs` pattern (ADR-0006) supports it.

## Falsifier triggers

- If graph queries are routinely slower than the manifest fallback (per measurement), the SQLite backing is wrong — successor reopens Option C (in-memory) or sharding.
- If the `graph_ingest` hook fails on `main` for two consecutive PR cycles, the ingest is fragile — successor ADR redesigns the hook contract.
- If more than three new node types are added inside one release cycle, the 18-type schema is undersized — successor ADR expands or restructures.
- If `agency_skill_search` is found to still rank by substring (graph unused) in `main` after this ADR ships, the query path is broken — successor ADR.
