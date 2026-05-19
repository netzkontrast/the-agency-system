# Review of Context from Workflow's Perspective

## 1. Verdict on `context/COLUMN.md`
**Does it preserve column isomorphism?**
Yes. Context firmly owns schemas, templates, and reference files (`context/COLUMN.md:12`).
**Where does it break?**
Context assumes it governs `SATISFIES_PHASE` edges via ontology tags, but it lacks visibility into the *execution state* of a phase. Context cannot unilaterally declare a phase "satisfied" just because an artefact matches a schema; only the workflow's Gates can determine satisfaction.

## 2. Verdict on `context/INTERFACE-TO-WORKFLOW.md`
**What they expect:**
- Manifests MUST declare `artefacts_produced: list[str]` (`context/INTERFACE-TO-WORKFLOW.md:21`).
- Workflow MUST emit a graph event mapping `Artefact -> SATISFIES_PHASE -> Phase` (`context/INTERFACE-TO-WORKFLOW.md:22`).
- Workflow MUST ONLY source templates from `context/` (`context/INTERFACE-TO-WORKFLOW.md:24`).
**Is it satisfiable while preserving invariants?**
Yes, mostly. Declaring artefacts and using context templates perfectly aligns with workflow. Emitting graph events is slightly problematic because workflow relies on `agentic` to execute tools. Workflow must instruct `agentic` (via `dispatch_skill` arguments) to emit these graph edges, or workflow's envelope schema must implicitly handle it upon successful gate passing.

## 3. Verdict on Ontology / Pipeline / Dispatch Model
**Conflict:**
Context assumes the envelope traversing phase boundaries strictly maps to `tool_result.schema.json` (`context/INTERFACE-TO-WORKFLOW.md:12`). However, as noted in the Agentic review, phase envelopes must carry opaque state (e.g., `context_refs` and gate conditions) that might extend beyond a simple ToolResult. Context's schema validation might reject valid stateful workflow envelopes.

## 4. Conflicts List
- **C4. Graph Edge Emission Ownership:** Context expects workflow to emit graph events (`vision/context/INTERFACE-TO-WORKFLOW.md:22`), but workflow's execution is deferred to agentic handlers.
- **C5. Envelope Schema Rigidity:** Context strictly validates phase handoffs against `tool_result.schema.json` (`vision/context/INTERFACE-TO-WORKFLOW.md:41`), which limits workflow's ability to embed opaque continuation state or sub-gate tracking data.
- **C6. Template Resolution vs. Progressive Disclosure:** Context provides static templates (`vision/context/COLUMN.md:38`). Workflow needs a way to request templates progressively based on edge cases (e.g., asking for a different act structure dynamically, as seen in `skills/novel-architect/phases/phase5-scene-matrix.md`), requiring a dynamic lookup rather than static manifest declarations.
