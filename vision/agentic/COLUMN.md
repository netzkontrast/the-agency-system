# Canonical Shape: agentic/<row>

This document defines the canonical isomorphism for any agentic cell (`agentic/<row>`). The agentic cell owns the "who" and "how" of the row: the skills, the MCP tools, the handlers, and the cross-row dispatch capabilities.

## 1. Cell Layout

Every `agentic/<row>` MUST follow this strict file tree:

```
agentic/<row>/
├── manifest.toml         # Canonical manifest for the cell
├── handlers/             # Python modules implementing FastMCP handlers
│   ├── __init__.py       # Must exist for module resolution
│   ├── <group_1>.py      # Handlers grouped logically (e.g. core.py, publish.py)
│   └── <group_n>.py
├── skills/               # Markdown files invoked via slash commands
│   ├── <slug>/
│   │   ├── SKILL.md      # The skill definition (frontmatter + trigger body)
│   │   └── references/   # T3 deep-dive references (optional)
```

**Naming Rules:**
- Handler files are `snake_case.py`.
- Skill directories are `kebab-case`.
- Tools defined in handlers MUST use the `mcp__<row>_<verb>` namespace.
- No other top-level directories are permitted.

## 2. Manifest Schema (`manifest.toml`)

The manifest is the unified registry for the cell.

```toml
[cell]
row = "<row>"
column = "agentic"

[routing]
namespace_prefix = "<row>_"

[skills]
# List of skill slugs exported by this cell
exports = ["<slug_1>", "<slug_2>"]

[tools]
# List of FastMCP tool groups exposed
exports = ["<group_1>", "<group_2>"]

[dependencies]
# Contracts required from other rows/cells
requires = [
  "workflow/<row>",  # Typically depends on its own row's workflow
  "context/<other>"  # Explicitly declare cross-row context usage
]
```

## 3. Skill Shape

Based on the MVP `jules-plugin/skills/jules/SKILL.md`, every skill MUST adhere to the slim-SKILL pattern.

- **Frontmatter:**
  - `name`: the slash command name (e.g., `music-producer`).
  - `description`: < 120 chars, concise trigger text.
  - `argument-hint`: slash command arguments.
  - `prefers_codemode`: boolean (if true, opens inside FastMCP Code Mode).
  - `allowed-tools`: List of allowed MCP tools.

- **Body Length Budget:** T2 (Body) MUST NOT exceed 100 lines (or ~5 KB). The body is purely the intent-to-action translation layer.
- **Reference Folder:** Any domain-specific deep logic, prompt patterns, or state machines MUST be exiled to `references/<topic>.md` (T3). The body merely lists available tools and links to references.

## 4. Handler Shape

Handlers are Python modules that back MCP tools. They do NOT contain orchestrator pipelines (which belong in `workflow`).

- Tools are decorated with `@mcp.tool(tags={"domain:<row>"})`.
- The entry point for the central MCP boot loop MUST be `register_<row>_<group>(mcp)`.
- Tools MUST return the standard typed envelope: `{"ok": bool, "data": Any, "warnings": list, "next_suggested_tools": list}`.
- Handlers MUST be stateless or write to explicitly passed cache namespaces.

## 5. The Central Routing Skill (`/agency`)

The `/agency` central routing skill lives in **`agentic/_router/`**.

**Justification:** It is a meta-cell within the `agentic` column. It does not belong in `workflow/workflow` because it is not a pipeline for scaffolding; it is the intent-surveyor that helps an agent discover which row and cell to enter. It leverages the `context` graph to map user intent to a specific row's skill, fulfilling the "Name-driven discovery" rule.

## 6. Codemode Opt-in

To utilize FastMCP Code Mode, a skill MUST declare `prefers_codemode: true` in its YAML frontmatter.

When true:
- The central MCP server wires the sandbox execution transform.
- The `allowed-tools` list implicitly gains `execute` and `search` (the Code Mode core tools).
- Handlers executed under this skill will intercept artifacts inside the sandbox.

## 7. Harness-in-Harness (Cross-row Dispatch)

When an agentic cell in Row R1 needs to trigger a pipeline in Row R2, it uses the standard harness cross-row dispatch contract.

- **Verb:** It calls the `dispatch_skill` (or `mcp__workflow_dispatch`) tool.
- **Envelope:** The payload MUST specify `{"row": "<row_2>", "phase": "<target_phase>", "context_refs": [...]}`.
- **Graph Edge:** The routing handler automatically writes a `DispatchedTo` edge in the graph from the R1 skill node to the R2 workflow node.
- **Execution:** The R1 handler awaits the typed envelope result from the R2 workflow gate before continuing.
