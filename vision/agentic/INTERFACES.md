# Interfaces: agentic column

This document guarantees the API contracts for the `agentic` column across the 3×N matrix. It declares what `agentic` exposes to the other columns, and what it strictly requires from them to function. Mismatches against other column `INTERFACES.md` files are considered merge-blocking.

## 1. Contracts EXPOSED by `agentic`

The following are provided by the `agentic` column and can be relied upon by `workflow` and `context`.

### 1.1 Central Routing Skill (`/agency`)
- **Description:** A row-agnostic slash command surveyor that determines the correct row and cell for the user's intent using graph adjacency.
- **Shape:** A skill exposed globally via Claude Code, returning the name of a specific row's skill slug to execute next.

### 1.2 Central MCP Boot Loop
- **Description:** The `agentic` column provides the central FastMCP instance (`servers/agency-mcp/run.py`). It reads `agentic/<row>/manifest.toml` and invokes `register_<row>_<group>(mcp)` for every declared tool group.
- **Shape:** `def boot_mcp() -> FastMCP` (Internal bootstrapper that iterates cell manifests).

### 1.3 Cross-Row Dispatch Surface
- **Description:** The mechanism for "harness-in-harness" calls, allowing a handler in row A to invoke a pipeline in row B.
- **Shape:**
  ```python
  def dispatch_skill(row: str, phase: str, context_refs: list[str]) -> ToolResult:
      # Writes DispatchedTo edge in graph, invokes workflow gate, returns standard envelope
  ```

### 1.4 Code Mode Delegation
- **Description:** The wiring that connects `prefers_codemode: true` in a skill's frontmatter to the FastMCP sandbox transform.
- **Shape:** Configuration hook that intercepts skill boot and modifies the server context.

## 2. Contracts REQUIRED by `agentic`

The following are external dependencies `agentic` needs from `workflow` and `context`.

### 2.1 From `context`: Schema Definitions
- **Description:** The `agentic` column does not own schemas. It needs JSON schemas to validate its own files.
- **Shape Required:**
  - `agentic-cell.schema.json` (Validates `agentic/<row>/manifest.toml`)
  - `skill-frontmatter.schema.json` (Validates `skills/<slug>/SKILL.md`)

### 2.2 From `context`: Graph Types and Writes
- **Description:** `agentic` tools and routing rely on the context graph to record edges and query intent.
- **Shape Required:**
  - Standard edge types: `DispatchedTo`, `InvokedTool`.
  - A utility to record edges natively: `def write_edge(source_id: str, target_id: str, relation: str) -> None`

### 2.3 From `workflow`: Pipeline Entry Point
- **Description:** For cross-row dispatch, `agentic` needs a uniform way to hand off control to a row's workflow pipeline.
- **Shape Required:**
  ```python
  def execute_pipeline(row: str, phase: str, inputs: dict) -> ToolResult:
      # Starts the gate-guarded pipeline for the specified row/phase
  ```

### 2.4 From `workflow`: Scaffold Meta-Row
- **Description:** `agentic/workflow` relies on the meta-row to provide the actual logic for creating a new row.
- **Shape Required:**
  - An MCP tool `mcp__workflow_scaffold_row(row_name: str)` that renders the templates for `agentic`, `workflow`, and `context`.
