# Research Patterns: Context

## 1. Inventory

### This Repo (`the-agency-system`)
- `context/workflow/templates/`: Cell-shape templates (Agentic/Workflow/Context). *(`vision/context/INTERFACE-TO-WORKFLOW.md:15`)*
- `context/_shared/schemas/`: `agentic-cell.schema.json`, `skill-frontmatter.schema.json`, `tool_result.schema.json`. *(`vision/context/INTERFACE-TO-AGENTIC.md:16`)*
- `context/music/`, `context/novel/`: Empty or implicit cell implementations based on matrix rules.

### Legacy Repo (`agency`)
- `templates/`: Skeletons for tasks, prompts, research, notes, and skills (e.g. `templates/task.md`, `templates/skill.md`). *(`README.md:95`)*
- `tools/legacy/validate-frontmatter.py`: Linter that checks L1/L2 YAML keys, max depth 1, and missing `REPLACE` tokens. *(`tools/readme.md:18`)*
- `tools/check-audit-graph-consistency.py`: Asserts that frontmatter linkage keys match body links (dual-surface drift). *(`FOLDERS.md:68`)*
- `schemas/`: Includes `header-ontology.json` defining L1/L2 frontmatter structures, e.g. for ADRs. *(`FOLDERS.md:126`)*
- `research/token-efficiency-tool-suite/workspace/repo-context-engine.md`: Details an MCP agentic context compression suite to trim context before models see it. *(`repo-context-engine.md:1`)*
- `research/token-efficiency-tool-suite/workspace/repo-contextgate.md`: Details a pre-invocation context-pruning middleware. *(`repo-contextgate.md:1`)*

## 2. Vital Patterns to Preserve
- **Flat YAML Frontmatter:** Restricting YAML depth to 1. Nested state gets hidden; flat keys (`adr_status`, `task_uses_prompts`) make parsing and cross-referencing cheap. *(agency: `tools/legacy/validate-frontmatter.py:34`)*
- **Dual-Surface Consistency (Frontmatter vs Body):** Frontmatter is the canonical graph linkage; prose body links are informational. Inconsistencies emit warnings, not errors. *(agency: `FOLDERS.md:68`)*
- **Scaffold Templates via Replacements:** `templates/skill.md` copies using simple `REPLACE` tokens which tooling blocks from surviving into committed state. *(agency: `prompts/author-skills-root-spec/prompt.md:157`)*
- **Exempt Storage Vaults:** The `FOLDERS.md §8` exemption pattern protects specific output folders from operational governance (e.g., separating user outputs like `albums/` from orchestration code). *(agency: `FOLDERS.md:105`)*
- **Pre-invocation Validation:** Gatekeeping execution based on static JSON Schema validation of the target artefact. *(agency: `PRE_COMMIT.md:9`)*

## 3. Anti-Patterns to Avoid
- **Deeply Nested Frontmatter:** Do not put complex JSON structures in Markdown headers. Exile heavy structures to sidecar `.meta.json` files or pure JSON schemas. *(agency: `tools/readme.md:18` limit YAML nesting ≤ 1)*
- **In-Memory Only Graph:** Relying purely on AST or networkx means a high cold-start cost every boot. The graph must be persistently serialized (e.g., SQLite/JSON). *(agency `tools/legacy/validate-frontmatter.py` requires walking files every time vs SQLite ingest hook)*
- **Ad-Hoc Directory Creation:** Generating top-level folders arbitrarily. Everything must fit inside the `<col>/<row>/<vault>` schema enforced by the manifest. *(agency: `README.md:103`)*

## 4. Constraints from Other Columns
- **Agentic Constraint:** `agentic` dynamic discovery relies on sub-millisecond query latency; thus context ingest MUST happen via `PostToolUse` synchronously, and queries MUST support standard Cypher/SQL. *(`vision/agentic/INTERFACE-TO-CONTEXT.md:39`)*
- **Agentic Constraint:** Binary artifacts (e.g., `.mp3`) cannot contain frontmatter, forcing Context to maintain metadata nodes that point to raw vault paths. *(`vision/agentic/INTERFACE-TO-CONTEXT.md:46`)*
- **Workflow Constraint:** Complex cross-row dispatch obscures origins if not explicitly carried in the envelope. `context` must map the `audit_trail` envelope fields to create a robust provenance edge (`DERIVED_FROM`, `SATISFIES_PHASE`). *(`vision/workflow/INTERFACE-TO-CONTEXT.md:31`)*

## 5. Recommendations for COLUMN.md
1. **Sidecar Metadata:** Explicitly require `.meta.json` sidecars for any node payload that exceeds the max YAML depth of 1, especially binary Vault output proxies.
2. **Context Compression Middleware:** Formalize a "context prune" or "compression" step as a native part of the Context query surface (referencing `ContextGate` / `Context-Engine`).
3. **Vault Mapping Spec:** Define exactly how `manifest.toml [storage]` maps external absolute paths to internal graph nodes for binary files.
4. **Envelope Alignment:** Clarify that Context owns the `tool_result.schema.json` which both Agentic and Workflow must inherit as their execution primitive.
