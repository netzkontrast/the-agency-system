# Interfaces

This document defines the contracts that the `workflow` column exposes to and requires from the `agentic` and `context` columns.

## 1. Contracts Workflow EXPOSES

The workflow cell provides structure that the other columns consume to perform actions and persist data.

### To `agentic` (Execution & Routing)
- **`workflow_phases`**: Exposes a list of all phases in a row so that `agentic` can dispatch into them.
  - *Shape:* A JSON array extracted from `manifest.toml` `[[phases]]`.
- **`phase_prerequisites`**: Exposes the gates and upstream dependencies of a given phase, allowing the central router to answer "what next?".
  - *Shape:* A mapping of `phase_id` to `blocking_gates` list.
- **`scaffold_entry` (Meta-row only)**: Exposes the entry-point to create a new row.
  - *Shape:* `scaffold(row_name: str) -> ToolResult`

### To `context` (Persistence & Ontology)
- **`artefacts_produced`**: Declares the ontology types of artefacts generated during a phase so the context graph can index them correctly.
  - *Shape:* A list of strings (e.g., `["music:lyric", "novel:chapter"]`) declared in the `manifest.toml`.

---

## 2. Contracts Workflow REQUIRES

The workflow cell relies on the capabilities of `agentic` and `context` to actually execute work and maintain state.

### From `agentic` (Execution Engine)
- **Central MCP Server**: Required to expose the workflow tools to the LLM.
  - *Shape:* A running MCP instance handling `tools/call`.
- **Four-Verb Call Surface**: Required to maintain standard invocation syntax across all tools.
  - *Shape:* The standard `list_tools`, `call_tool`, `list_skills`, `dispatch_skill` protocol.
- **`dispatch_skill`**: Required for invoking the specific skill that drives a workflow phase.
  - *Shape:* `dispatch_skill(skill_id: str, args: dict) -> ToolResult`

### From `context` (Templates & Schemas)
- **Artefact Templates**: Required to generate the baseline output structure for a phase.
  - *Shape:* Markdown/YAML files retrieved from `context/<row>/templates/`.
- **Handoff Envelope Schema**: Required to validate the payload crossing a phase boundary.
  - *Shape:* A JSON Schema corresponding to the FastMCP `ToolResult`.
- **Cell-Shape Templates**: Required by the meta-row to scaffold new rows.
  - *Shape:* Canonical cell definition templates stored in `context/workflow/templates/`.
- **Ontology Type Names**: Required to correctly label produced artefacts in the manifest.
  - *Shape:* A standardized list of string tags (e.g., `domain:type`) provided by the context graph schema.
