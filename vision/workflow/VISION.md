---
slug: vision-workflow-spec
type: vision-spec
status: active
owner: claude
created: 2026-05-19
updated: 2026-05-19
summary: The definitive vision document for the `workflow` column of the 3xN agency-system matrix. Describes pipelines, phase gating, state management, and cross-domain interfaces, along with the 10 core Gherkin scenarios.
affects:
  - vision/workflow/VISION.md
---

# Vision: The Workflow Column

The `workflow` column owns the **"WHEN"** of the agency-system matrix. While `agentic` defines the tools and `context` defines the data structures, `workflow` defines the process: pipelines, step-ordering, handoffs, and policy gates.

This document synthesizes findings from legacy patterns, cross-domain negotiations, and the overarching matrix law.

## 1. Domain Ownership & Boundaries

The workflow column strictly owns:
- **Pipelines:** The ordered phases of a row (e.g., `outline → chapter → scene → revision` for a novel).
- **Phase definitions:** The conceptual boundaries defining what each phase consumes, produces, and hands off.
- **Gates:** Hard-blocking or advisory checks evaluated between or within phases.
- **Handoff Envelopes:** The typed payload (`PhaseStateEnvelope`) that crosses phase boundaries.
- **The Meta-row (`workflow/workflow`):** The scaffolding pipeline used to generate new domains in the matrix.

**What it does NOT own:**
- Python code or MCP handlers (these belong to `agentic`).
- Schemas, templates, or graph substrates (these belong to `context`).
- Final output artifacts (these belong in the `result/` registry, per the new Overview doc).

## 2. Core Architectural Patterns

Based on research across multiple MVP repositories, the workflow column enforces several vital patterns:

### 2.1 The Phase Ladder
Pipelines must enforce logical decomposition before execution. Patterned after the legacy `analyze → brainstorm → design → workflow` ladder, `workflow` requires explicit planning phases before mutating state.

### 2.2 Progressive Disclosure
Phase definitions must not be loaded all at once. Markdown files in `workflow/<row>/phases/` (e.g., `phase0-bootstrap.md`, `phase1-intent.md`) are lazy-loaded only when the pipeline enters that phase. This protects the LLM token budget.

### 2.3 Separation of Planning and Execution
Workflow phases define the plan and the gates, but they do NOT execute code. Execution is deferred to the `agentic` column. The workflow invokes `agentic` to do the work, and `agentic` yields back to the workflow to evaluate gates.

## 3. The Cross-Domain Integration Strategy

Integrating `workflow` with its peer columns requires resolving conflicting expectations around control flow and schema rigidity.

### 3.1 Resolving Agentic Control Flow
`agentic` expects to call pipelines synchronously and receive a `ToolResult`. However, workflows are multi-step, stateful, and asynchronous (often blocking on user input via gates).
**Resolution:** Workflow exposes `execute_pipeline(row, phase, inputs)`. However, instead of a final execution result, it yields a `PhaseStateEnvelope`.
```python
class PhaseStateEnvelope(TypedDict):
    status: Literal["running", "blocked_on_gate", "completed"]
    phase_id: str
    opaque_state: dict[str, Any]  # Unvalidated state token for the pipeline
    tool_result: dict[str, Any]   # Conformant to FastMCP ToolResult
```
This forces the Agentic caller to handle suspension and resumption of state.

### 3.2 Resolving Context Schema and Graph Emission
`context` demands strict adherence to the `tool_result.schema.json` and expects workflow to emit `SATISFIES_PHASE` graph edges.
**Resolution:** Workflow satisfies Context by embedding the standard `tool_result` within the `PhaseStateEnvelope`. Workflow retains ownership over graph emission: its Gates are configured to emit `SATISFIES_PHASE` edges ONLY when a gate evaluates to `ok: true`. Workflow metadata (like `artefacts_produced`) is explicitly declared in `workflow/<row>/manifest.toml`.

## 4. Canonical Cell Shape

Every workflow cell (`workflow/<row>/`) MUST strictly adhere to this structure:

```text
workflow/<row>/
├── manifest.toml         # Declares entry verbs, phases, and artefacts_produced.
├── README.md
├── phases/
│   ├── 01-first.md       # Lazy-loaded via progressive disclosure.
│   └── 02-second.md
├── gates/
│   └── review-gate.yaml  # Contains policy checks and `on_success: emit_edge` logic.
└── handoffs/
    └── envelope.yaml     # Defines PhaseStateEnvelope.
```

The strict cell manifest allows the central harness to derive the fully qualified names without bloating the cold-boot payload.

## 5. Owned & Co-Owned Gherkin Scenarios

The workflow column governs or co-governs the following behaviors in the system:

### Scenario 3: New row plug-in
```gherkin
Given a developer adds a new row "podcast"
When they invoke the meta-row scaffolding pipeline with row name "podcast"
Then the meta-row generates the new workflow cell structures
And no base file is modified
And the central MCP picks up the new tools on next boot
And the central routing skill picks up the new skills automatically
```

### Scenario 9: Lesson-learned link-back
```gherkin
Given a skill execution produces a lesson
When the lesson is written by the active workflow phase
Then its frontmatter cites the originating workflow phase and spec
And the graph records a lesson→spec edge
```

### Scenario 10: Harness-in-harness (cross-row dispatch)
```gherkin
Given an agentic cell from row R1 dispatches into a workflow cell from row R2
When the cross-row dispatch occurs targeting a specific workflow phase
Then the dispatching handler uses the SAME four-verb contract as a leaf cell
And the workflow handoff envelope correctly traverses the row boundary
And the graph records the cross-row dispatch edge with both row identities
```

### Scenario 11: Cold-boot budget
```gherkin
Given a fresh session loads the plugin
When token-usage is measured by a documented method during MCP boot
Then the `manifest.toml` of every workflow row is efficiently parsed
And the cold-boot total is below a documented numeric budget
And the budget is enforced by a CI check
```

### Scenario 14: Column isomorphism (workflow)
```gherkin
Given any two rows R1 and R2
When their workflow cells are inspected by the validation tool
Then both cells expose the canonical `manifest.toml`, `phases/`, `gates/`, and `handoffs/`
And both cells satisfy the workflow-cell schema
```

### Scenario 17: Workflow-of-creating-a-workflow (meta-row recursion)
```gherkin
Given a developer invokes the meta-row with row name "podcast"
When the meta-workflow executes its scaffold phase
Then it creates `agentic/podcast`, `workflow/podcast`, `context/podcast` from canonical templates
And all three new cells pass column-isomorphism on the first commit
```

### Scenario 18: Workflow-owned MCP tools registered in Code Mode
```gherkin
Given a workflow row defines MCP tools in its agentic cell via its workflow phase definitions
When the central MCP boots
Then those tools are registered under the namespace `<row>_*`
And they are exposed in Code Mode by default
```

### Scenario 4: Typed envelope
```gherkin
Given a workflow phase yields execution state
When the wire payload is inspected
Then it must successfully validate the inner tool_result against `tool_result.schema.json`
And wrap it in a PhaseStateEnvelope
```

### Scenario 5: Cross-column reference via graph
```gherkin
Given a workflow cell cites a context cell in its frontmatter
When the graph is queried for cells adjacent to that context node
Then the workflow cell appears in the result
```

### Scenario 8: Graph auto-ingest
```gherkin
Given a workflow gate succeeds
When the phase transitions
Then a SATISFIES_PHASE edge is emitted and automatically ingested by the SQLite graph store
```
