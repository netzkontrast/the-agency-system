# Integrated Draft: Workflow Synthesis

## 1. Diff of Incoming Expectations

### From Agentic:
- Demands `execute_pipeline(row, phase, inputs) -> ToolResult`.
- Demands synchronous execution tracking.
- Expects to map state/context across `dispatch_skill` boundaries.
- **Agree:** Central MCP bootloader, four-verb contract.
- **Conflict:** Synchronous `ToolResult` expectation vs. Workflow's stateful, async, multi-gate nature.

### From Context:
- Demands `artefacts_produced` declarations in `manifest.toml`.
- Demands Workflow emits `SATISFIES_PHASE` graph edges.
- Demands strict adherence to `tool_result.schema.json` for handoff envelopes.
- **Agree:** Template sourcing, artefact validation.
- **Conflict:** Schema rigidity rejecting opaque Workflow state; Graph edge emission ownership (Workflow vs Agentic).

## 2. Integration Strategy & Signatures

### Resolving Agentic Control Flow (C1, C2, C3)
Workflow accepts being called by Agentic via `execute_pipeline`, but redefines the return shape. It will not return a final execution result, but a `PhaseStateEnvelope` indicating the action required by Agentic (e.g., `yield_for_user`, `dispatch_to_worker`).

```python
class PhaseStateEnvelope(TypedDict):
    status: Literal["running", "blocked_on_gate", "completed"]
    phase_id: str
    opaque_state: dict[str, Any]  # Unvalidated state token
    tool_result: dict[str, Any]   # Conformant to FastMCP ToolResult
```

### Resolving Context Schema & Graph Ownership (C4, C5, C6)
Workflow asserts that the Envelope contains a `tool_result` conforming to `tool_result.schema.json`, satisfying Context, but wraps it in `PhaseStateEnvelope` to handle its own opaque state.
For graph emission, Workflow's Gates emit the `SATISFIES_PHASE` edge ONLY when the gate evaluates `ok: true`.

```yaml
# workflow/<row>/gates/<gate>.yaml
type: hard-blocking
on_success:
  emit_edge: SATISFIES_PHASE
  target_ontology: "context.artefacts_produced"
```

## 3. What Workflow Cedes vs. Retains

- **Cedes to Agentic:** Exposes `execute_pipeline` as the entry point, allowing Agentic's `/agency` skill to act as the primary intent router.
- **Retains against Agentic:** Refuses to treat pipelines as synchronous functions. Enforces that Agentic must handle `PhaseStateEnvelope` yields.
- **Cedes to Context:** Agrees to strictly declare `artefacts_produced` and rely exclusively on Context templates.
- **Retains against Context:** Refuses to flatten phase handoffs into a raw `ToolResult`. Insists on wrapping it to carry execution state. Claims ownership over evaluating `SATISFIES_PHASE` condition before emission.

## 4. Updated Cell-Shape Sketch

```text
workflow/<row>/
├── manifest.toml         # Declares entry verbs, phases, AND artefacts_produced.
├── README.md
├── phases/
│   ├── 01-first.md       # Lazy-loaded via progressive disclosure.
│   └── 02-second.md
├── gates/
│   └── review-gate.yaml  # Contains `on_success: emit_edge` logic.
└── handoffs/
    └── envelope.yaml     # Defines PhaseStateEnvelope mapping to Context's ToolResult.
```

## 5. Open Questions for Harness
- **Handoff Interruption:** When `execute_pipeline` yields `blocked_on_gate` to ask the user a question, how does the harness serialize the `PhaseStateEnvelope` so the session can resume cleanly after the user replies?
- **Graph Transactionality:** If a gate succeeds and writes a `SATISFIES_PHASE` edge, but the subsequent Agentic dispatch fails, does the harness provide rollback for graph edges?
