# Review of Agentic Column

## 1. Verdict on `COLUMN.md`
The agentic column heavily leverages the matrix layout to build a structured execution engine. It strictly adheres to `agentic/<row>/` layout with `handlers/` and `skills/`, which successfully preserves column isomorphism. It also enforces namespacing (`mcp__<row>_<verb>`) and strict length boundaries for the Skill body (T2 <= 100 lines, delegating to T3 `references/`), matching the Context column's push for lightweight structures (`vision/agentic/COLUMN.md:28`).
Where it slightly bends isomorphism is defining the central routing skill under a meta-cell `agentic/_router/` (`vision/agentic/COLUMN.md:41`), though this is justifiable given it must query the entire graph and not just a single domain row.

## 2. Verdict on `INTERFACE-TO-CONTEXT.md`
Agentic's expectations of Context are high but completely satisfiable while maintaining Context invariants:
- **`ToolResult` Envelope Structure:** Agentic expects Context to define and validate the `ToolResult` JSON envelope (`vision/agentic/INTERFACE-TO-CONTEXT.md:14`). Context already plans to host this under `context/_shared/schemas/tool_result.schema.json`.
- **Hooks (PreToolUse & PostToolUse):** Agentic expects Context to provide logic for these hooks for validation and graph ingestion (`vision/agentic/INTERFACE-TO-CONTEXT.md:18`). This matches Context's ingest path goals without violating Context boundaries, provided the hooks themselves are defined centrally.
- **Graph Edges:** Agentic commits to writing explicit edges (`DispatchedTo`, `InvokedTool`, `GeneratedArtefact`) (`vision/agentic/INTERFACE-TO-CONTEXT.md:32`). This is a huge win for Context, keeping the graph accurate during cross-row orchestrations.
- **Storage Vaults layer:** Agentic expects a `get_vault_path()` function to persist logs/binary artifacts (`vision/agentic/INTERFACE-TO-CONTEXT.md:36`). Context satisfies this through the `[storage]` block in manifests.

## 3. Verdict on Ontology / Pipeline / Dispatch Model
Agentic's dispatch model relies on FastMCP tools executing and returning identical envelopes. They heavily expect sub-millisecond query latency (`query_graph`) from Context to find skills across rows. Context's choice of SQLite accommodates this requirement well (`vision/context/ONTOLOGY.md:14`). There is no inherent conflict in the overarching ontology; both columns view the Skill as the orchestrator and the Graph as the audit log.

## 4. Conflicts List
- **Binary Metadata vs Schema Validation:** Agentic points out friction where handlers produce binary artifacts (like MP3s) which cannot be schema-validated via frontmatter (`vision/agentic/INTERFACE-TO-CONTEXT.md:46`). Context needs a defined pattern (e.g., a `.meta.json` sidecar node) to validate binary file insertions.
- **Dynamic Manifest Delays:** Agentic notes that dynamically building namespaces based on manifests causes a temporal delay between writing a skill and it surfacing (`vision/context/INTERFACE-TO-AGENTIC.md:41`). Context needs to guarantee its Graph Ingestion hook immediately exposes the newly updated nodes without requiring a hard MCP server reboot.
