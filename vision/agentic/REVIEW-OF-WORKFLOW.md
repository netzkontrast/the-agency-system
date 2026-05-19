# Review of Workflow Column

This document reviews the `workflow` column's defined shape and its expectations of the `agentic` column, analyzing compatibility and friction.

## 1. Verdict on `workflow/COLUMN.md`

The `workflow/COLUMN.md` defines a strict pipeline map (`manifest.toml`, `phases/`, `gates/`, `handoffs/`).
- **Isomorphism Preservation**: It correctly preserves column isomorphism. All workflow cells follow a predictable structural map that the `agentic` column can parse.
- **Where it breaks**: Workflow defines its own `handoffs/envelope.yaml` that models the FastMCP `ToolResult` shape but expects `agentic` to use it for internal pipeline passing. If `workflow` changes this shape independently, it risks drifting from the central MCP standard that `agentic` relies on.

## 2. Verdict on `workflow/INTERFACE-TO-AGENTIC.md`

- **Demands**: `workflow` requires `agentic` to provide `boot_mcp()`, `dispatch_skill()`, `execute_pipeline()`, and `write_edge()`.
- **Satisfiability**:
  - `boot_mcp()` and `dispatch_skill()` are inherently agentic responsibilities and satisfy its invariants.
  - `write_edge()` is satisfiable but places the graph-writing burden directly on the execution handler rather than a middleware hook, which might clutter the handler code.
  - **Friction**: The requirement for `execute_pipeline(row, phase, inputs)` demands that `agentic` act as the active workflow runner, interpreting `manifest.toml` gates. This slightly blurs the line: if `agentic` executes the pipeline logic, `workflow` becomes purely static data.

## 3. Verdict on Ontology / Pipeline / Dispatch Model

- **Conflict**: Workflow expects the standard `ToolResult` envelope returned by `agentic` to be cleanly extended to accept an `audit_trail` (Graph Provenance) field. `agentic/COLUMN.md` strictly defines the envelope as `{"ok": bool, "data": Any, "warnings": list, "next_suggested_tools": list}`. Mutating this core MCP envelope specifically for workflow needs violates the `agentic` mandate that all row handlers use the identical base envelope.

## 4. Conflicts List

- **file: `vision/workflow/INTERFACE-TO-AGENTIC.md` line: 30** - Friction: `audit_trail` injection into the core `ToolResult` payload. Workflow demands a schema change to `agentic`'s envelope.
- **file: `vision/workflow/INTERFACE-TO-AGENTIC.md` line: 18** - `execute_pipeline()`: Forces `agentic` to read and interpret `workflow` gate state, pushing workflow logic into the agentic execution surface.
- **file: `vision/workflow/COLUMN.md` line: 55** - `handoffs/envelope.yaml`: Duplicates the definition of `ToolResult`. If the FastMCP specification changes, this localized `workflow` schema will drift.