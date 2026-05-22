# Interface: agentic → workflow

This document defines the intersection between the `agentic` column (the actors, skills, handlers) and the `workflow` column (the pipelines, phases, gates). It specifies the contracts `agentic` exposes to `workflow` and what it requires in return.

## 1. Stance

The `agentic` column views `workflow` as the stateful engine that defines the "what" and the "when". Agentic tools (handlers) are stateless workers; workflow pipelines are the managers. Agentic expects workflow to provide clear entry points for starting phases, and expects workflow to return standard `ToolResult` envelopes so agentic can communicate progress back to the orchestrator (or user).

## 2. Surface Exposed to Workflow

Agentic provides the execution substrate for workflow pipelines.

### 2.1 The Four-Verb Call Contract
- **Description:** The core FastMCP integration layer that workflow pipelines use to execute steps or query capabilities.
- **Signatures:**
  - `list_tools(domain: str = None) -> list[dict]`
  - `call_tool(name: str, arguments: dict) -> ToolResult`
  - `list_skills() -> list[dict]`
  - `dispatch_skill(skill_id: str, args: dict) -> ToolResult`
- **Isomorphism Note:** Workflow uses this same surface regardless of row.

### 2.2 Central MCP Bootloader
- **Description:** Exposes the mechanism by which tools defined in `agentic` handlers become available to workflow phases running in Code Mode.
- **Signature:** `boot_mcp() -> FastMCP`
- **Effect:** Reads `[tools]` exports in `agentic/<row>/manifest.toml` and wires the routes.

## 3. Required of Target (Workflow)

For agentic to function correctly when orchestrating tasks, it needs strict guarantees from workflow.

### 3.1 Pipeline Entry Point (`execute_pipeline`)
- **Description:** When a skill uses `dispatch_skill` to trigger a workflow phase, workflow must expose a standard executor.
- **Required Signature:**
  ```python
  def execute_pipeline(row: str, phase: str, inputs: dict) -> ToolResult
  ```

### 3.2 Phase/Gate Manifest Declarations
- **Description:** To support routing and the "what next?" query, workflow must declare its phases.
- **Required Shape:** JSON array in `manifest.toml` (e.g., `[[phases]]`) exposing `phase_id` and `blocking_gates`, as listed in `vision/workflow/INTERFACES.md`.

### 3.3 Meta-Row Scaffold Entry
- **Description:** For the `agentic/workflow` meta-skill to create a new row, workflow must expose the scaffolding tool.
- **Required Signature:**
  ```python
  def mcp__workflow_scaffold_row(row_name: str) -> ToolResult
  ```

## 4. Isomorphism Map

Agentic perfectly maps onto the workflow's phase definitions. A skill in `agentic/<row>` corresponds to one or more phases in `workflow/<row>`. The primary friction lies in state: agentic handlers are strictly stateless, while workflow phases manage state transitions. This requires careful passing of `context_refs` and opaque state identifiers across the `dispatch_skill` boundary to avoid state leakage into the agentic column.

## 5. Gherkin Scenarios

Mapped from `vision/00-charter.md`.

```gherkin
  # Anchor: Scenario 10 (Harness-in-harness)
  Scenario: Agentic dispatches to workflow phase
    Given an agentic skill handler in row "music"
    When the handler calls `execute_pipeline(row="music", phase="analyze_stems", inputs={...})`
    Then the workflow engine initializes the phase gates
    And returns a standard `ToolResult` envelope containing the gate outcomes
```

```gherkin
  # Anchor: Scenario 17 (Workflow-owned MCP tools)
  Scenario: Workflow tools are booted via agentic
    Given `agentic/music/manifest.toml` declares tool exports
    When the `boot_mcp()` routine runs
    Then the tools are available to the `workflow/music` pipelines via the `call_tool` primitive
```
