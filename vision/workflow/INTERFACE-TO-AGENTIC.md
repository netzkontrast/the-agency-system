# Workflow interface to Agentic (`[w→a]`)

## 1. Stance

The `workflow` column sees `agentic` as the pure execution engine and the intent-router. Workflow provides the strict pipeline map (phases, gates, handoffs); agentic is the machinery that walks that map. Workflow expects agentic to host the MCP tools, expose the slash commands that trigger pipelines, and strictly honor the phase ordering and blocking gates defined in `workflow/<row>/manifest.toml`.

## 2. Surface Exposed to Agentic

Workflow exposes these concrete structures to agentic for discovery and execution:

- **Manifest entry point:**
  ```toml
  # Read by agentic during boot/discovery
  [workflow]
  entry_verbs = ["scaffold", "start", "resume"]
  ```

- **Phase Sequence & Gate definitions (JSON representation of `manifest.toml`):**
  ```json
  {
    "phases": [
      { "id": "phase-01", "path": "phases/01-first.md" }
    ],
    "gates": [
      { "id": "gate-01", "blocks": "phase-02", "path": "gates/review-gate.md" }
    ]
  }
  ```

- **Phase definition metadata (Frontmatter):**
  ```yaml
  id: phase-01
  driven_by_skill: agentic/<row>/skills/<skill-name>.md
  ```

## 3. Required of Target (Agentic)

For workflow to function, `agentic` MUST provide:

- **`boot_mcp() -> FastMCP`**: To register any workflow-owned MCP tools.
- **`dispatch_skill(skill_id: str, args: dict) -> ToolResult`**: The execution hook. When a pipeline hits a phase, it uses this to invoke the `driven_by_skill` handler.
- **`execute_pipeline(row: str, phase: str, inputs: dict) -> ToolResult`**: A uniform entry point (often triggered by slash commands) to initiate the workflow logic.
- **Graph edge creation (`write_edge`)**: When R1 dispatches to R2 workflow, agentic must record the `DispatchedTo` edge.

## 4. Isomorphism Map

- **Fit:** The `workflow` pipeline seamlessly plugs into `agentic`'s `/agency` router. Agentic queries the graph for the row, finds the `entry_verbs` exposed by the workflow manifest, and triggers `execute_pipeline`.
- **Friction:** Agentic handlers currently return an envelope `{"ok": bool, "data": Any, "warnings": list, "next_suggested_tools": list}`. Workflow requires tracking `audit_trail` (Graph Provenance). Agentic's ToolResult envelope must be cleanly extended to accept the `audit_trail` field without schema validation failures.

## 5. Gherkin

```gherkin
Feature: Workflow to Agentic integration

  # Maps to Scenario 10: Harness-in-harness (cross-row dispatch)
  Scenario: Agentic triggers a workflow phase
    Given a user intent resolves to a workflow via `/agency`
    When the agentic router calls `execute_pipeline(row, phase, inputs)`
    Then the workflow reads `manifest.toml` to verify gate status
    And the workflow delegates execution back to agentic via `dispatch_skill`

  # Maps to Scenario 18: Workflow-owned MCP tools
  Scenario: Boot loads workflow tools
    Given `workflow/<row>/manifest.toml` exposes entry verbs
    When `agentic` executes `boot_mcp()`
    Then the workflow tools are mapped to `mcp__<row>_<verb>`
    And made available to the agentic sandbox
```
