# Review of Context Column

This document reviews the `context` column's defined shape and its expectations of the `agentic` column, analyzing compatibility and friction.

## 1. Verdict on `context/COLUMN.md`

The `context/COLUMN.md` defines the structural substrate (`schemas/`, `templates/`, `references/`) and the central source of truth for isomorphism.
- **Isomorphism Preservation**: It perfectly preserves column isomorphism. It acts as the anchor that guarantees the shapes of all cells across the matrix.
- **Where it breaks**: It does not break isomorphism, but it places heavy reliance on `JSONSchema 2020-12` validation at runtime, which imposes a strict performance and token constraint on `agentic` if errors occur and need to be summarized.

## 2. Verdict on `context/INTERFACE-TO-AGENTIC.md`

- **Demands**: `context` demands strict compliance: `agentic` must trigger `validate_frontmatter` (PreToolUse) before writes, `ingest_node` (PostToolUse) after writes, and strictly return `tool_result.schema.json` compliant envelopes.
- **Satisfiability**: Highly satisfiable. Using Pre/Post hooks is a standard, robust way to enforce consistency without cluttering the business logic in `agentic` handlers.
- **Friction**: The temporal delay noted in the interface ("agentic dynamically builds FastMCP namespaces... creates a slight temporal delay"). `context` expects the graph to be updated immediately via `ingest_node`, but `agentic` MCP tools won't reflect new skills until a server reboot or dynamic reload.

## 3. Verdict on Ontology / Pipeline / Dispatch Model

- **Conflict**: The `context` column dictates that the `tool_result` schema lives in `context/_shared/schemas/`. However, `agentic` uses standard FastMCP, which defines its own internal schemas. `context` is essentially trying to own the type definition of an external library (`agentic`'s FastMCP), which creates a boundary dispute. If FastMCP updates its envelope, `context`'s schema breaks.

## 4. Conflicts List

- **file: `vision/context/INTERFACE-TO-AGENTIC.md` line: 15** - `ToolResult` Envelope Ownership: `context` attempts to enforce `tag:agency-system.local,2026:schema:shared/tool_result`. This creates dual-master syndrome with `agentic`'s native FastMCP `ToolResult` definition.
- **file: `vision/context/INTERFACE-TO-AGENTIC.md` line: 30** - Hook Implementation Burden: `context` demands `PreToolUse` and `PostToolUse` hooks be implemented *by agentic*. While `agentic` triggers the tool, the logic of validating schemas and hitting SQLite (the graph) strictly belongs to the context domain. If `agentic` implements the hook logic, it violates the separation of concerns.
- **file: `vision/context/INTERFACE-TO-AGENTIC.md` line: 33** - Graph Edge Writing: `agentic` handlers are required to "explicitly call `write_edge`". This contradicts the `PostToolUse` auto-ingest hook paradigm and forces context-graph logic into the agentic execution handler.