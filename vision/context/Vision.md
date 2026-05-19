# Vision: Context Domain

## 1. Executive Summary

This document defines the overarching vision for the `context` domain within the agency system matrix. Evolving from the foundational rules established in `vision/00-charter.md` and refined by the strict token economy in `vision/00.1-Overview.md`, the Context domain provides the essential graph substrate, memory layout, and validation schemas that enable Name-Driven Discovery and Row Isomorphism. It represents the "WHAT" of the matrix, completely decoupled from execution (Agentic) and process flow (Workflow), while cleanly interfacing with the artifact product (Registry).

## 2. Core Stance

The Context column acts as the structural reality and definitive map of the system.
- **Graph as Authority:** Context owns the SQLite-backed ontology graph tracking files, schemas, templates, and references. It enforces the Graph Audit Trail.
- **Isomorphism Enforcer:** Context provides the schemas (`agentic-cell.schema.json`, `workflow-cell.schema.json`, `context-cell.schema.json`) that strictly govern the shape of the other columns.
- **Stateless Operation:** Context does not hold executing processes, session state variables, or user product artifacts (which belong in the `result/<row>` registry).
- **Token Efficiency:** The Context column optimizes search and discovery by minimizing yaml depth (maximum depth of 1) and pushing deep data into sidecar `.meta.json` files or the database.

## 3. Surface & Interfaces

The Context domain exposes specific boundaries and endpoints to the matrix:

### 3.1 Exposed to Agentic (`[c→a]`)
- **Query Surface:** `query_graph(cypher: str) -> list[dict]`. Enables the `/agency` router to discover skills and context nodes instantly.
- **Validation Hooks:** `PreToolUse` validation to ensure every written file respects canonical schemas, and `PostToolUse` ingestion to instantly Upsert nodes to the SQLite graph.
- **Envelope Schemas:** The canonical `tool_result.schema.json` ensuring all tools return isomorphic data.

### 3.2 Exposed to Workflow (`[c→w]`)
- **Scaffold Templates:** Render engines pointing to `context/workflow/templates/` that workflow uses to scaffold entirely new rows (e.g., scaffolding `agentic/novel`).
- **Audit Schemas:** Requires Workflow to pass `audit_trail` objects in the handoff envelope, enabling Context to map `SATISFIES_PHASE` and `DERIVED_FROM` edges.
- **Vault Mapping:** Translates workflow outputs (like an audio render) into Graph entries using the Sidecar Metadata Pattern (`.meta.json`).

### 3.3 Required Constraints
- **Registry Separation:** Context strictly demands that generated artifacts (audio, PDFs) reside in `result/<row>` and *not* within the `context/` tree. The graph only stores a lightweight pointer proxy.
- **Zero-Delay Graph:** Requires the backing store (SQLite) to ingest updates immediately on write, avoiding delayed manifest recompilations common in the MCP layer.

## 4. Ontology & Graph Substrate

The core of Context is the Ontology mapping system logic and history.

- **Storage:** SQLite with Cypher-compatibility (or equivalent recursive SQL mapping).
- **Primary Node Types:** Plugin, Row, Cell, Skill, Handler, Phase, Gate, Template, Schema, Session, Reference, ArtefactProxy.
- **Primary Edge Types:**
  - `CONTAINS` (Structural hierarchy)
  - `ADJACENT_TO` (Semantic proximity from `related:` tags)
  - `PREREQUISITE_OF` (Execution ordering)
  - `USES_TEMPLATE` / `USES_SCHEMA` (Generation dependencies)
  - `SATISFIES_PHASE` (Audit trailing)

## 5. Cell Shape Isomorphism

Every row within the `context` column strictly follows this layout:

```text
context/<row>/
├── manifest.toml           # The token-efficient export declaration
├── README.md               # Human overview
├── templates/              # Jinja/Pandoc skeletons
├── schemas/                # JSON Schema 2020-12 rules and partials
└── references/             # T3 conceptual docs (e.g., suno_prompt_guide)
```

**Manifest Rules:** The `manifest.toml` only exports what cannot be algorithmically derived (e.g., node_types, template entry points).

## 6. Gherkin Scenarios

The Context domain owns or co-owns the following verifiable rules:

```gherkin
# anchor: context.typed_envelope
Scenario: Context enforces typed envelopes
  Given an agentic handler returns a payload
  When the PreToolUse hook fires
  Then the payload MUST strictly validate against `context/_shared/schemas/tool_result.schema.json`
  And failure to validate aborts the write operation.

# anchor: context.graph_ingest
Scenario: Graph auto-ingests new content
  Given a new frontmatter-bearing markdown file is saved to the repository
  When the PostToolUse hook executes
  Then the SQLite backing store instantly UPSERTs the file as a graph node
  And parses `related:` keys to construct `ADJACENT_TO` edges.

# anchor: context.sidecar_metadata
Scenario: Binary artifacts map to graph via sidecars
  Given a workflow outputs `track.mp3` into the `result/music/` registry
  When the agent writes the file
  Then the agent MUST write a `track.mp3.meta.json` sidecar
  And Context ingests the sidecar to maintain the Audit Trail without parsing binary data.

# anchor: context.isomorphism_validation
Scenario: Matrix structural isomorphism
  Given the system boots
  When the structural linter runs
  Then `agentic/music`, `workflow/music`, and `context/music` MUST validate against their respective `*-cell.schema.json` defined by Context.

# anchor: context.discovery
Scenario: Name-driven Context Discovery
  Given the `/agency` router has only the string "novel"
  When it issues a Cypher query to the Context store
  Then it retrieves the exact path to `context/novel/manifest.toml` via `[:CONTAINS]` edges without regex searching.

# anchor: context.template_render
Scenario: Artefact Generation via Template
  Given an agent initiates `pandoc render` for a Plot Beat
  When the render request is processed
  Then Context locates `context/novel/templates/plot_beat.md.jinja`
  And outputs the file, recording a `DERIVED_FROM` edge in the graph.

# anchor: context.audit_trail
Scenario: Workflow Audit Trail Mapping
  Given a workflow phase completes
  When the phase passes the `audit_trail` envelope
  Then Context maps `SATISFIES_PHASE` between the generated artifact proxy and the workflow Phase node.

# anchor: context.flat_frontmatter
Scenario: Token-efficient frontmatter parsing
  Given an agent attempts to write nested JSON objects into a markdown file's YAML header
  When Context schema validation runs
  Then the write is rejected with an error enforcing a maximum YAML depth of 1.

# anchor: context.registry_isolation
Scenario: Registry decoupling from Context Graph
  Given a user requests the full context of the `novel` row
  When the `query_graph()` returns data
  Then it includes schemas and templates, but explicitly EXCLUDES the text body of finalized book chapters residing in `result/novel/`.

# anchor: context.schema_locality
Scenario: Local Handoff Extension
  Given `workflow/podcast` defines `handoffs/envelope.yaml`
  When Context validates the pipeline
  Then it enforces that the local envelope extends `context/_shared/schemas/tool_result.schema.json` via `$ref`.
```
