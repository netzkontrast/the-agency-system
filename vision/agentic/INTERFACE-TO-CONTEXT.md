# Interface: agentic → context

This document defines the intersection between the `agentic` column (handlers, skills, routing) and the `context` column (graph, schemas, templates, storage).

## 1. Stance

The `agentic` column views `context` as the absolute source of truth for structure, memory, and validation. Agentic does not invent file shapes or persist arbitrary logs; it relies on `context` to provide the schemas for its manifests, the storage vaults for its outputs, and the graph database to record its actions. Agentic expects `context` to be queryable (via Cypher-like endpoints) and reliable for all read/write validation.

## 2. Surface Exposed to Context

Agentic provides the dynamic execution that populates the context graph.

### 2.1 ToolResult Envelope Structure
- **Description:** Agentic promises that every handler it executes will return data matching the envelope required by context.
- **Shape:** JSON object containing `{"ok": bool, "data": Any, "warnings": list, "artefacts_written": list, "next_suggested_tools": list, "error": str}`.

### 2.2 PreToolUse & PostToolUse Hook Triggers
- **Description:** Agentic exposes hook injection points around its tool executions so that `context` can perform validation and graph ingestion.
- **Signature (Hook Dispatcher):**
  ```python
  def execute_with_hooks(tool_name: str, args: dict, pre_hooks: list, post_hooks: list) -> ToolResult
  ```

## 3. Required of Target (Context)

Agentic relies heavily on context primitives to function securely and maintain the audit trail.

### 3.1 Schemas for Agentic Files
- **Description:** Required to validate the agentic column's own internal files.
- **Required Named Schemas:**
  - `agentic-cell.schema.json`
  - `skill-frontmatter.schema.json`

### 3.2 Graph Edge Recording & Audit Trail
- **Description:** Required to maintain the cross-domain ontology when an artefact is generated or a dispatch occurs.
- **Required Signatures:**
  - `def write_edge(source_id: str, target_id: str, relation: str) -> None`
  - Required Edge Types: `DispatchedTo`, `InvokedTool`, `GeneratedArtefact`, `UsesTemplate`, `ValidatedBySchema`.

### 3.3 Storage Vaults Layer
- **Description:** Required so agentic handlers know where to persist session logs and workflow artefacts (e.g., audio files, novel chapters) outside the plugin logic.
- **Required Signature:**
  ```python
  def get_vault_path(row: str, vault_type: str) -> str
  ```

### 3.4 Graph Query API
- **Description:** Required by the central routing skill (`/agency`) to discover skills by name/intent.
- **Required Signature:**
  ```python
  def query_graph(query: str) -> list[dict]
  ```

## 4. Isomorphism Map

Agentic handlers map 1:1 with context validation boundaries. For every file a handler writes, a context schema exists to validate it. Friction occurs when handlers produce binary artefacts (like MP3s) which cannot be schema-validated via frontmatter; agentic expects `context` storage vaults to handle binary persistence seamlessly while only graphing the metadata.

## 5. Gherkin Scenarios

Mapped from `vision/00-charter.md`.

```gherkin
  # Anchor: Scenario 7 (Frontmatter pre-write gate)
  Scenario: Agentic write triggers schema validation
    Given an agentic handler attempts to write `skills/new-skill/SKILL.md`
    When the PreToolUse hook fires
    Then the `context` column validates the content against `skill-frontmatter.schema.json`
    And blocks the write if invalid
```

```gherkin
  # Anchor: Scenario 8 (Graph auto-ingest)
  Scenario: Handler artefact generation updates audit trail
    Given an agentic handler successfully writes a rendered artefact to the vault
    When the PostToolUse hook fires
    Then `write_edge` is called to link the Skill, Template, Schema, and Artefact
    And the context graph accurately reflects the `GeneratedArtefact` edge
```
