# Integrated Draft: Context

## 1. Diff of Incoming Expectations

**Where `agentic` and `workflow` agree:**
- Both require Context to own and enforce the `ToolResult` envelope schema (`tool_result.schema.json`).
- Both demand Graph query support to fetch relationships (`agentic` for discovery, `workflow` for scaffolding and pipeline transitions).
- Both require a standard Vault resolution mechanism (`get_vault_path`) to handle file persistence outside the operational matrix.

**Where they conflict (or present friction):**
- **Schema Locality vs Global:** `workflow` wants to define `handoffs/envelope.yaml` locally in its column (`vision/workflow/COLUMN.md:52`), but `agentic` relies on `context/_shared/schemas/tool_result.schema.json`. If left unintegrated, the handoff envelope will drift from the tool execution envelope.
- **Binary/External Path Validation:** `agentic` flags friction writing MP3s directly because they lack frontmatter. `workflow` flags friction writing to user external vaults (like `albums/`) because external paths break graph validation. They both push the burden to Context to map external, frontmatter-less files into the Audit Graph.
- **Graph Updates:** `agentic` warns that dynamic manifest parsing requires a boot-cycle delay for new skills. It expects the graph query to instantly catch updates post-write via the `PostToolUse` hook.

## 2. Integration Strategy

**For Schema Locality Conflict (The Envelope):**
Context will enforce the `context/_shared/schemas/tool_result.schema.json` as the absolute law.
`workflow` cells MAY define a local `handoffs/envelope.yaml`, but Context's `workflow-cell.schema.json` will enforce that the local envelope MUST extend (via `$ref`) the global `tool_result` schema. The local schema is only allowed to tighten constraints (e.g., specifying exact data types inside the `data` object), not redefine the base envelope.

**For Binary / External Vault Conflict:**
Context introduces the **Sidecar Metadata Pattern**.
When `agentic` or `workflow` writes to an external vault (e.g., `albums/track.mp3`), they cannot write frontmatter into it. Therefore, Context requires the writer to also write a sidecar file: `albums/.meta/track.mp3.meta.json`.
The `PostToolUse` hook will scan for these sidecars. The sidecar acts as the Graph Node proxy, holding the `audit_trail` (Template, Schema, Skill, Phase origins) and the `SATISFIES_PHASE` edges, bridging the external binary into the internal matrix graph.

**For Dynamic Graph Discovery Delay:**
Context will manage a SQLite Backing Store. The `PostToolUse` hook triggers an immediate `UPSERT` into the SQLite database. The `query_graph()` function issued by `/agency` will strictly read from SQLite, not from in-memory FastMCP state, guaranteeing 0-delay discovery of newly written skills or artifacts.

## 3. What Context Cedes / Does Not Cede

- **ACCEPTED:** Context accepts the burden of `get_vault_path()` and managing external paths via the new Sidecar Metadata Pattern.
- **ACCEPTED:** Context accepts providing the `PreToolUse` and `PostToolUse` logic for the graph and schema validations.
- **REJECTED:** Context REJECTS the idea of a purely in-memory graph (NetworkX) or scanning files per query. SQLite is mandatory to satisfy Agentic's sub-millisecond query constraints and zero-delay discovery.
- **ADAPTED:** Context adapts Workflow's `handoffs/envelope.yaml` by enforcing that it MUST inherit from the shared Context ToolResult schema.

## 4. Updated Cell-Shape Sketch

```text
context/<row>/
├── manifest.toml           # Defines schemas, templates, AND [storage] Vault resolution paths.
├── README.md
├── templates/              # Jinja templates used by workflow scaffolding & pandoc.
├── schemas/
│   ├── handoff-extensions/ # Where workflow local envelopes map to shared envelopes.
│   └── partials/
└── references/             # T3 conceptual docs.
```
*Note: `context/_shared/schemas/tool_result.schema.json` remains the root for both Agentic tools and Workflow handoffs.*

## 5. Open Questions for the Harness

1. **Vault Sidecar Write Permissions:** Does FastMCP's filesystem sandbox allow writing to a `.meta/` subdirectory inside a user-defined external vault (like `albums/`) without triggering sandbox violations?
2. **Hook Execution Layer:** Should `PreToolUse` and `PostToolUse` run as literal MCP middleware, or as Python decorators inside the `agentic` module that wrap the FastMCP tool execution? If MCP lacks native middleware, the harness must explicitly decorate every tool.
