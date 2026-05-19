# Workflow interface to Context (`[w→c]`)

## 1. Stance

The `workflow` column sees `context` as the persistence layer, the schema authority, and the structural foundation of the matrix. Workflow relies on context for scaffolding templates, defining canonical shapes, maintaining the Storage Vaults for user-facing outputs, and managing the Graph Audit Trail. Workflow expects context to enforce structural rules and provide the rendering logic that transitions a phase's raw data into a finalized artefact.

## 2. Surface Exposed to Context

Workflow exposes strict definitions to context so it can index, validate, and store pipeline outputs properly:

- **Manifest Ontology and Storage (TOML):**
  ```toml
  [ontology]
  artefacts_produced = ["<domain>:<type>"]

  [storage]
  vaults = ["albums", "renders", "uploads"]
  log_namespaces = ["sessions", "tool-calls"]
  ```

- **Handoff Envelope Schema Validation Target:**
  ```yaml
  # Context uses this structure to map the audit trail
  audit_trail:
    template_used: "context/<row>/templates/<name>.md.jinja"
    schema_used: "context/<row>/schemas/<name>.json"
    originating_skill: "agentic/<row>/skills/<slug>.md"
  ```

## 3. Required of Target (Context)

For workflow to function and persist state, `context` MUST provide:

- **Cell-Shape Templates**: `context/workflow/templates/` containing the `agentic`, `workflow`, and `context` blueprint files required by `mcp__workflow_scaffold_row`.
- **Artefact Templates & Schemas**: `load_template(row, name, variables) -> str` to structure the payload of a completed phase.
- **Storage Vaults Allocation**: Writable mount points (e.g., `albums/`, `renders/`) to persist artefacts safely outside plugin boundaries.
- **Graph Audit Trail Ingestion**: A graph transaction that receives the `audit_trail` envelope field and correctly maps `SUPERSEDES` and `DERIVED_FROM` relations.
- **`pandoc_render(node_slug)`**: The mechanism to convert the final artefact node into user-requested output formats.

## 4. Isomorphism Map

- **Fit:** The meta-row `workflow/workflow` seamlessly relies on `context/workflow/templates/` to scaffold new rows. Artefacts produced by workflow strictly adhere to `context/<row>/schemas/`.
- **Friction:** Storage vaults (e.g., `albums/`) exist physically outside the matrix rules to protect user data limits, requiring Context to map external absolute paths to internal graph nodes. Graph Ingest hooks must cleanly resolve external paths without crashing matrix validations.

## 5. Gherkin

```gherkin
Feature: Workflow to Context integration

  # Maps to Scenario 17: Workflow-of-creating-a-workflow (meta-row recursion)
  Scenario: Scaffolding a new row uses Context templates
    Given a developer invokes the meta-row for "podcast"
    When workflow phase 2 executes `load_template()`
    Then context serves `agentic-cell.template.md` and `workflow-cell-manifest.template.toml`
    And workflow scaffolds the identical isomorphic directories

  # Relates to the Graph Audit Trail and Storage Vault addition
  Scenario: Artefact generation persists via Context
    Given a workflow phase successfully produces an artefact payload
    When the workflow hands off the envelope with the `audit_trail` mapping
    Then context validates the artefact against the defined schema
    And saves it to the declared `vault` (e.g., `albums/`)
    And the graph records the provenance edge linking back to the driving skill
```
