# Meta-Workflow: The Workflow-of-Creating-a-Workflow

This document specifies `workflow/workflow`, the meta-row pipeline responsible for extending the 3×N matrix. By invoking this pipeline, a new row is scaffolded with strict structural isomorphism.

## Phases of the Meta-Row

The scaffolding process follows a strict linear pipeline.

### Phase 1: Name & Intent
- **Goal:** Gather the row name and its primary domain/purpose.
- **Action:** Validates that the requested name (e.g., `podcast`) does not already exist in the central manifest.

### Phase 2: Rendering
- **Goal:** Load canonical templates from the context column and populate them with the new row's identity.
- **Action:** Reads from `context/workflow/templates/` and injects variables like `{{row_name}}` and `{{domain}}`.

### Phase 3: Scaffolding
- **Goal:** Write the rendered files to the filesystem.
- **Action:** Creates the exact folder structures for:
  - `agentic/<new_row>/`
  - `workflow/<new_row>/`
  - `context/<new_row>/`

### Phase 4: Validation
- **Goal:** Ensure the newly created cells conform to the rules of the matrix.
- **Action:** Runs the column-isomorphism invariants against the newly generated `agentic`, `workflow`, and `context` cells.

### Phase 5: Registration
- **Goal:** Make the new row discoverable to the rest of the system.
- **Action:** Updates the central MCP manifest and registers new edges in the graph store.

## Context Templates

The meta-row relies on the following templates (provided by the context column) living in `context/workflow/templates/`:

1. `agentic-cell.template.md`: Defines the base SKILL and MCP tool registration boilerplate.
2. `workflow-cell-manifest.template.toml`: The standard `manifest.toml` shape.
3. `workflow-phase.template.md`: A stub for the row's first phase.
4. `context-schema.template.yaml`: The baseline ontology and schema definitions.

## Invariants Enforced

During Phase 4 (Validation), the meta-row checks:
1. **Directory Structure:** All three cells must have their exact, canonical folders (e.g., `workflow/<row>/phases/`).
2. **File Presence:** Required files (`manifest.toml`, `README.md`) must exist in all three cells.
3. **Graph Integrity:** The new row must be accessible via ontology edges, not string matching.

## Worked Example: Scaffolding `podcast`

When a developer invokes `scaffold("podcast")`:

1. **Input:** `{ row_name: "podcast", intent: "Manage audio episode creation" }`
2. **Render & Scaffold:** The meta-row outputs:
   ```text
   agentic/podcast/
   ├── skills/
   │   └── podcast-manager.md
   └── tools/

   workflow/podcast/
   ├── manifest.toml
   ├── phases/
   │   └── 01-record.md
   ├── gates/
   └── handoffs/
       └── envelope.yaml

   context/podcast/
   ├── schemas/
   │   └── episode.yaml
   └── templates/
   ```
3. **Validation:** Checks that `workflow/podcast/manifest.toml` adheres to the schema.
4. **Registration:** Adds `podcast` to the central routing surface.

## Bootstrapping `workflow/workflow`

Because scaffolding requires the meta-workflow to exist, `workflow/workflow` cannot scaffold itself.

**The Bootstrap Path:**
The human maintainer must manually author `workflow/workflow`, `agentic/workflow`, and `context/workflow` **once**. These baseline cells are hard-coded in the repository. From that point forward, all new rows (including `music`, `novel`, etc.) are generated using the meta-row pipeline, ensuring the matrix extends organically and consistently.
