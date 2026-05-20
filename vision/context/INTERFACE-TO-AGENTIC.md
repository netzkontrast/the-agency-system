# Context Interface to Agentic

## 1. Stance
The `context` column views the `agentic` column as the active execution engine—the entity that performs side-effects, invokes tools, and writes state. `context` provides the structural reality (graph, schemas, templates) that `agentic` relies on to make intelligent routing decisions and ensure data consistency. `context` expects `agentic` to be a compliant writer: it must strictly validate data against schemas before writing and faithfully emit graph events (nodes and edges) after every state change.

## 2. Surface
`context` exposes the following concrete interfaces to `agentic`:

- **Graph Query Surface**: `query_graph(cypher: str) -> list[dict]`
  - Used by the `/agency` router to find adjacent skills and nodes.
  - Example: `MATCH (r:Row {name: "music"})-[:CONTAINS]->(c:Cell) RETURN c.path`
- **Cell Schema Enforcers**: `JSONSchema` files in `context/_shared/schemas/`
  - `agentic-cell.schema.json`
  - `skill-frontmatter.schema.json`
- **Envelope Schema**: `ToolResult`
  - `tag:agency-system.local,2026:schema:shared/tool_result` ensures that all agentic FastMCP handlers yield identically shaped envelopes.
- **Template Loader**: `load_template(row: str, template_slug: str, vars: dict) -> str`
  - Allows `agentic` handlers to render correct file scaffolding before writing.

## 3. Required of Target (`agentic`)
For the context column to function and maintain an accurate graph, `agentic` MUST provide:

- **PreToolUse Validation Hook**: `agentic` MUST execute `validate_frontmatter(payload, schema_id)` before writing any markdown file to disk.
- **PostToolUse Ingest Hook**: `agentic` MUST execute `ingest_node(filepath: str, frontmatter: dict)` after any successful file write to UPSERT the node and its `related:` / `depends_on:` edges to the SQLite graph.
- **Envelope Compliance**: `agentic` tools MUST return a serialized payload matching the `tool_result.schema.json`.
- **Graph Edge Writing**: `agentic` handlers MUST explicitly call `write_edge(source_id, target_id, "DispatchedTo")` during cross-row handoffs.

## 4. Isomorphism Map
The `context` column maps perfectly to `agentic`'s need for strict, column-wide consistency. `agentic` relies heavily on `manifest.toml` and structured `skills/`; `context` dictates the schema that keeps those files isomorphic.
*Friction note:* `agentic` dynamically builds FastMCP namespaces based on manifests, which creates a slight temporal delay between an agent writing a new skill and the tool surface actually reflecting it until the next boot.

## 5. Gherkin Scenarios

```gherkin
  # Maps to Scenario #7: Frontmatter pre-write gate
  Scenario: Agentic strictly validates frontmatter via context schema
    Given an agentic handler prepares to write `agentic/music/skills/new-skill.md`
    When the PreToolUse hook fires
    Then the payload is validated against `context/_shared/schemas/skill-frontmatter.schema.json`
    And an invalid `summary` length blocks the write operation

  # Maps to Scenario #8: Graph auto-ingest
  Scenario: Agentic populates the context graph post-write
    Given an agentic tool successfully writes a new artefact
    When the PostToolUse hook fires
    Then `agentic` triggers the context ingest path
    And the context SQLite store UPSERTs the new node and its relations
```