# Review of Agentic from Workflow's Perspective

## 1. Verdict on `agentic/COLUMN.md`
**Does it preserve column isomorphism?**
Yes. `agentic` strictly defines its domain as handlers, slash commands, and MCP tools (`agentic/COLUMN.md:5`). It defers all orchestration to `workflow`.
**Where does it break?**
The "Harness-in-Harness" cross-row dispatch (`agentic/COLUMN.md:59`) creates an implicit state dependency. By demanding that R1 handlers await the typed envelope result from the R2 workflow gate, `agentic` is blocking synchronously on workflow state, which blurs the line between stateless handlers and stateful pipelines.

## 2. Verdict on `agentic/INTERFACE-TO-WORKFLOW.md`
**What they expect:**
Agentic requires workflow to provide `execute_pipeline(row, phase, inputs) -> ToolResult` (`agentic/INTERFACE-TO-WORKFLOW.md:31`). It expects to trigger workflows and get a synchronous `ToolResult` back.
**Is it satisfiable while preserving invariants?**
Partially. Workflow manages long-running state. Returning a synchronous `ToolResult` for a multi-phase workflow is impossible unless the tool result represents a "Phase Started / Yielded" state rather than "Workflow Completed". The expectation needs adapting so `execute_pipeline` yields Phase Envelopes (handoffs), not just final execution results.

## 3. Verdict on Ontology / Pipeline / Dispatch Model
**Conflict:**
Agentic's central `/agency` routing skill (`agentic/COLUMN.md:48`) maps user intent to a row, but agentic then calls `execute_pipeline`. This makes Agentic the *caller* of Workflow. However, Workflow views Agentic as the *worker* it invokes (`workflow/INTERFACE-TO-AGENTIC.md:7`).
This creates a control-flow cycle: Agentic -> Workflow (`execute_pipeline`) -> Agentic (`dispatch_skill`).

## 4. Conflicts List
- **C1. Synchronous vs Async Yielding:** Agentic demands `execute_pipeline` returns a `ToolResult` (`vision/agentic/INTERFACE-TO-WORKFLOW.md:33`), but workflow phases can block on gates or askuser prompts (`skills/novel-architect/phases/phase5-scene-matrix.md:20`).
- **C2. State Leakage:** Agentic mentions passing `context_refs` and opaque identifiers across `dispatch_skill` (`vision/agentic/INTERFACE-TO-WORKFLOW.md:46`). Workflow must define the exact schema of this opaque state so Agentic doesn't accidentally mutate it.
- **C3. Control Flow Inversion:** Agentic's routing handler invokes workflow (`vision/agentic/INTERFACE-TO-WORKFLOW.md:57`), while workflow's manifest says it invokes agentic (`vision/workflow/COLUMN.md:35`). We need a clear "Intent (Agentic) -> Scaffold/Resume (Workflow) -> Work (Agentic)" delineation.
