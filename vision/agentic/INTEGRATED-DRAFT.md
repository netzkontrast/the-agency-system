# Integrated Draft: Agentic Synthesis

This document synthesizes the incoming demands from the `workflow` and `context` columns, resolving conflicts to establish a cohesive operational model for the `agentic` column.

## 1. Diff of Incoming Expectations

**Agreement**:
- Both columns rely on `agentic` as the pure execution engine.
- Both columns expect `agentic` to handle the standard typed envelope (`ToolResult`).
- Both columns expect `agentic` to be responsible for cross-row dispatch and lifecycle operations (e.g., `boot_mcp()`, `dispatch_skill()`).

**Conflicts**:
1. **Envelope Mutation vs. Schema Supremacy**: `workflow` demands extending `ToolResult` with `audit_trail`. `context` demands strict schema compliance to its own local `tool_result.schema.json`. Both conflict with `agentic`'s reliance on the native FastMCP envelope definition.
2. **Graph Responsibility**: `workflow` expects `agentic` to manually trigger `write_edge()` on cross-row dispatches. `context` demands `agentic` manually trigger `write_edge()` while *also* demanding a `PostToolUse` auto-ingest hook.
3. **Execution Boundary**: `workflow` expects `agentic` to expose `execute_pipeline()` and evaluate gates. This pushes workflow logic into the agentic namespace.

## 2. Integration Strategy

To preserve `agentic` isomorphism, we implement the following concrete patterns:

- **Conflict 1: The Envelope**
  - *Strategy*: Use the FastMCP `data` field payload to carry column-specific extensions, rather than modifying the root envelope schema.
  - *Signature*:
    ```python
    class ToolResult(TypedDict):
        ok: bool
        data: dict  # Workflow injects 'audit_trail' inside here; Context validates the inner schema.
        warnings: list[str]
        next_suggested_tools: list[str]
    ```
- **Conflict 2: Graph Writing & Hooks**
  - *Strategy*: `agentic` does NOT manually write graph edges in its handlers. Instead, the central FastMCP server wrapper implemented by `agentic` registers middleware hooks provided by `context`. `agentic` yields standard metadata; the hook maps it to the graph.
  - *Signature*: `@mcp.tool(tags={"domain:<row>"}, context_edges=[("DispatchedTo", target_id)])`
- **Conflict 3: Pipeline Execution**
  - *Strategy*: `agentic` does not evaluate workflow gates. `agentic`'s `/agency` router invokes `workflow_mcp__start_phase(phase_id)`. The workflow cell's *own* handler (registered via MCP) evaluates the gate and returns the envelope to the agentic runner.

## 3. What is Ceded / What is Retained

- **Accepted**:
  - `agentic` accepts the responsibility of implementing the middleware hook execution architecture (Pre/Post tool use).
  - `agentic` accepts the responsibility for routing slash commands to workflow execution.
- **Rejected**:
  - `agentic` rejects modifying the root FastMCP `ToolResult` envelope to add `audit_trail`. (Moved to `data`).
  - `agentic` rejects manual `write_edge()` calls inside domain handlers. (Moved to middleware/decorators).
  - `agentic` rejects evaluating workflow gate logic.
- **Adapted**:
  - `context`'s `tool_result.schema.json` is adapted to be an authoritative schema *of the inner `data` payload* for specific actions, leaving the root envelope as pure FastMCP.

## 4. Updated Cell-Shape Sketch (`agentic/<row>`)

The canonical shape evolves to cleanly demarcate core logic from middleware annotations.

```
agentic/<row>/
├── manifest.toml         # Routing namespace and skill exports
├── handlers/
│   ├── __init__.py
│   ├── execution.py      # Core logic yielding ToolResult
│   └── routing.py        # /agency cross-row dispatch logic
└── skills/
    └── <slug>/
        ├── SKILL.md      # Slash command mapping, frontmatter
        └── references/   # T3 deep-dive references
```
*Note: Graph writes and schema validation are removed from `handlers/` code and occur transparently via FastMCP decorators/interceptors.*

## 5. Open Questions for the Harness

1. **State Refresh Rate**: If `agentic` tools dynamically generate based on newly created skills (e.g., `novel-architect` writing a new phase), does the MCP server require a hard reboot to expose the new tools, or is there an active reload signal supported by the harness?
2. **Hook Failure Recovery**: If the `context` PreToolUse hook blocks an agentic write due to schema failure, does the agentic loop silently absorb the error into the `warnings` array, or does it throw a hard exception terminating the pipeline?