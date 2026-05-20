# Review of Workflow Column

## 1. Verdict on `COLUMN.md`
Workflow's layout (`phases/`, `gates/`, `handoffs/`) is extremely well-structured and aligns closely with column isomorphism. It successfully defines itself as the state machine. The use of sequential phase files (`01-first.md`) and distinct gate policies (`gates/review-gate.md`) is clean. Workflow delegates payload definitions entirely to `handoffs/envelope.yaml` (`vision/workflow/COLUMN.md:52`), which heavily mirrors the `ToolResult` defined in Context, though there is a potential duplication risk if Workflow attempts to redefine it.

## 2. Verdict on `INTERFACE-TO-CONTEXT.md`
Workflow expects a massive amount of structural enforcement from Context, which fits Context's role as the system's substrate:
- **Ontology and Storage mapping:** Workflow expects Context to parse its `manifest.toml`'s `[ontology]` and `[storage]` entries and allocate Vaults (`vision/workflow/INTERFACE-TO-CONTEXT.md:14`). Context accepts this; mapping paths is core Context behavior.
- **Audit Trail Schema:** Workflow expects to hand off an `audit_trail` object in the envelope linking templates, schemas, and skills (`vision/workflow/INTERFACE-TO-CONTEXT.md:21`). This is perfectly satisfiable and actively helps Context maintain accurate `SUPERSEDES` and `DERIVED_FROM` edges.
- **Scaffold Templates:** Workflow explicitly depends on Context's templates (`context/workflow/templates/agentic-cell.jinja`) to run its meta-row scaffolding operations (`vision/workflow/INTERFACE-TO-CONTEXT.md:32`). Context fully supports this.
- **Pandoc Rendering:** Workflow relies on Context to convert finalized artefact nodes into end-user formats (`vision/workflow/INTERFACE-TO-CONTEXT.md:37`).

## 3. Verdict on Ontology / Pipeline / Dispatch Model
Workflow's dispatch relies heavily on standard verb passing (`start_phase`, `resume_phase`) returning an envelope. It assumes Context intercepts these state transitions via hooks (or the graph handles it seamlessly) to construct the graph. This is harmonious. Workflow relies on `envelope.yaml`, and Context must ensure this maps perfectly to the `tool_result.schema.json`.

## 4. Conflicts List
- **External Storage Vaults & Graph Nodes:** Workflow notes significant friction that user Vaults (e.g., `albums/`) exist physically outside the matrix rules to protect user quotas, requiring Context to cleanly map external absolute paths to internal graph nodes without crashing matrix validations (`vision/workflow/INTERFACE-TO-CONTEXT.md:44`).
- **Handoff Envelope Schema Duplication:** Workflow defines `handoffs/envelope.yaml` locally (`vision/workflow/COLUMN.md:52`), while Agentic & Context define `tool_result.schema.json` globally in `context/_shared/schemas/` (`vision/context/INTERFACE-TO-WORKFLOW.md:15`). Context must assert that the workflow handoff MUST reference the central schema rather than redefining it locally to avoid schema drift.
- **Obscured Origins:** Cross-row dispatch can obscure the originating `SATISFIES_PHASE` edge if the workflow envelope drops the previous phase ID during the handoff (`vision/context/INTERFACE-TO-WORKFLOW.md:37`). Workflow must strongly type the phase-origin trace in its `audit_trail` dictionary.
