# Agentic Column Schemas

This directory contains the JSON Schema (Draft 2020-12) definitions that codify the agentic column's internal data structures and its interface payloads across the matrix.

## Domain Schemas

These schemas define the configurations and contracts owned entirely by the `agentic` column:

- `skill-frontmatter.schema.json` — Validates the frontmatter required at the top of an agentic `SKILL.md` file.
- `tool-manifest.schema.json` — Defines FastMCP tool registration metadata (e.g. derived names, `defer_schema` flags).
- `harness-bootstrap.schema.json` — Configuration payload the FastMCP harness reads at boot.

## Four-Verb Protocol Schemas

These schemas detail the request and response shapes of the core 4-verb tool call system:

- `four-verb/list-tools-response.schema.json` — Response payload for listing available FastMCP tools.
- `four-verb/call-tool-request.schema.json` — Request payload for invoking a specific tool.
- `four-verb/call-tool-response.schema.json` — Response payload for tool invocation (references the global ToolResult envelope).
- `four-verb/list-skills-response.schema.json` — Response payload for listing available skills in the routing system.
- `four-verb/dispatch-skill-request.schema.json` — Request payload to dispatch control to a specific cross-row skill.
- `four-verb/dispatch-skill-response.schema.json` — Response payload for skill dispatch (references the global ToolResult envelope).

## Interface Schemas

These schemas represent the cross-column boundaries as seen from the `agentic` column's point-of-view:

- `interface-to-workflow.schema.json` — Defines what the agentic column sends to `workflow.start`, `workflow.resume`, or `workflow.get_state`.
- `interface-to-context.schema.json` — Defines what the agentic column sends to `context.query`, `context.upsert_node`, or `context.upsert_edge`.
