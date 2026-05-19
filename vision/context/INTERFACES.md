# The Context Column: Interfaces

This document defines the contracts the `context` column exposes to and requires from the `agentic` and `workflow` columns. The merge check ensures these contracts align across the matrix.

## Contracts context EXPOSES

The context column provides the structural substrate, templates, schemas, and query capabilities.

### 1. Canonical Cell Schemas
- **Name:** `agentic-cell.schema.json`, `workflow-cell.schema.json`, `context-cell.schema.json`
- **Description:** JSON Schema definitions that enforce column isomorphism.
- **Shape:** JSON Schema 2020-12 defining directory structure, required files (e.g., `manifest.toml`, `README.md`), and file location constraints.

### 2. Frontmatter Schemas
- **Name:** `<kind>.frontmatter.schema.json`
- **Description:** Schemas validating the frontmatter of every markdown artefact kind (skill, handler, spec, template, etc.).
- **Shape:** JSON Schema 2020-12 ensuring required L1 keys (`slug`, `summary`, `status`, `type`, `owner`) and cross-link constraints.

### 3. ToolResult Envelope Schema
- **Name:** `tool_result.schema.json`
- **Description:** The standard envelope schema that every FastMCP handler must return.
- **Shape:** Object containing `ok` (boolean), `data` (any), `warnings` (array), `artefacts_written` (array), `next_suggested_tools` (array), and `error` (string).

### 4. Graph Query API
- **Name:** `query_graph(query: str) -> list[dict]`
- **Description:** The Cypher-equivalent endpoint for name-driven discovery and relationship traversal.
- **Shape:** Accepts a Cypher query string; returns a list of dictionaries representing nodes and edges.

### 5. Template Loader
- **Name:** `load_template(row: str, name: str, variables: dict) -> str`
- **Description:** Renders a specified Jinja2 template from a row's `templates/` directory using provided variables.
- **Shape:** Accepts row name, template name, and context dict; returns rendered string.

### 6. Pandoc Renderer
- **Name:** `pandoc_render(node_slug: str) -> list[str]`
- **Description:** Renders a context node to its declared output formats.
- **Shape:** Accepts a node slug; returns a list of output file paths.

### 7. Anchor-Triad Search Surface
- **Name:** `search_context(query: str) -> list[dict]`
- **Description:** Resolves search intents to context nodes (schemas, templates, references) via ontology types or manifest summaries.
- **Shape:** Accepts a natural language or typed query; returns a list of relevant node metadata.

---

## Contracts context REQUIRES

The context column relies on the other columns to participate in the graph lifecycle and adhere to structural rules.

### 1. PreToolUse Frontmatter Validation
- **Required From:** `agentic`
- **Description:** Before writing any file containing frontmatter, `agentic` MUST invoke the PreToolUse hook to validate the frontmatter against the relevant schema exposed by `context`.
- **Shape:** Hook execution blocking the write operation if validation fails.

### 2. PostToolUse Graph Ingest
- **Required From:** `agentic`
- **Description:** After a successful file write, `agentic` MUST invoke the PostToolUse hook to parse the file (if applicable) and UPSERT the node and its edges into the graph store.
- **Shape:** Hook execution triggering a graph database transaction.

### 3. Workflow Artefact Declaration
- **Required From:** `workflow`
- **Description:** Every phase defined in a `workflow` cell MUST declare an `artefacts_written` list specifying the ontology types it intends to produce.
- **Shape:** Array of ontology type strings defined in the phase's specification or configuration.

### 4. Strict Template Location
- **Required From:** `workflow`
- **Description:** When scaffolding or rendering, `workflow` MUST ONLY use templates residing in `context/<row>/templates/` or `context/_shared/templates/`. In-cell templates within the `workflow` column are forbidden.
- **Shape:** File path constraint enforced during template load requests.
