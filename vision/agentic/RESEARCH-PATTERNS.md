# Research Patterns: Agentic

This document surveys the `agency` and `agency-system` (this repo) repositories for patterns relevant to the `agentic` column.

## 1. Inventory

### Repo: `netzkontrast/the-agency-system` (This Repo)
- `jules-plugin/skills/jules/SKILL.md`: The canonical "Jules orchestrator" skill. Contains the `name`, `description`, `allowed-tools`, and `prefers_codemode` concepts. Acts as an asynchronous remote worker orchestrator.
- `skills/novel-architect/SKILL.md`: A complex, stateful skill defining an end-to-end process (7 phases). Shows heavy use of YAML frontmatter, phase dispatching (`/sc:` commands), and integration with other skills (`ncp-author`, `memory-sync`).
- `vision/agentic/COLUMN.md`: Defines the canonical shape of the agentic cell (`manifest.toml`, `handlers/`, `skills/`).
- `vision/agentic/INTERFACES.md`, `vision/agentic/INTERFACE-TO-*.md`: Defines how `agentic` talks to `workflow` and `context`.

### Repo: `netzkontrast/agency`
- `skills/ralph-skill/SKILL.md`: Demonstrates a multi-modal skill ("Generate", "Customize", "Extend", "Audit"). Exposes cross-cutting concerns and complex prompt assembly logic.
- `skills/ralph-skill/references/ralph-spec.md`: Contains normative rules (e.g., `R.2.1` main agent context must act as a scheduler only, delegating to subagents). Highlights the "Staff Engineer" subagent pattern.
- `skills/ralph-skill/references/loop-variants.md`: Shows `loop.sh` implementation (the agentic coding loop).

## 2. Vital Patterns

1. **The Scheduler Pattern (`ralph-spec.md` R.2.1)**: The main agent context must act as a scheduler/orchestrator only. It must not perform file-reading or build operations directly; these must be delegated to subagents. *Why preserve:* Prevents token bloat and context degradation in the main loop.
2. **Phase Routing via Intent (`novel-architect/SKILL.md`)**: The use of phase definitions (`phase1-intent-capture.md`, etc.) mapped to slash commands. *Why preserve:* Allows progressive disclosure of state and context without loading the entire pipeline into memory.
3. **The `SKILL.md` Frontmatter (`jules-plugin/skills/jules/SKILL.md`)**: The declarative approach to skills (name, description, argument-hint, allowed-tools, prefers_codemode). *Why preserve:* Allows the central MCP server to dynamically build namespaces and tools without hardcoding.
4. **State Persistence via Disk (`ralph-spec.md` R.2.2)**: State persistence between iterations must occur exclusively through files on disk (e.g., `IMPLEMENTATION_PLAN.md`, `AGENTS.md`). *Why preserve:* Enables cold-restarts and prevents hallucination of state.
5. **Typed Envelopes (`vision/00-charter.md`)**: The strict `ToolResult` return shape (ok, data, warnings, etc.). *Why preserve:* Guarantees predictability across the matrix rows.

## 3. Anti-Patterns to Avoid

1. **Context Bloat (`ralph-spec.md` R.2.6)**: Keeping operational files (like `AGENTS.md`) large or filling them with status updates. *Why avoid:* Degrades LLM reasoning capabilities.
2. **Direct Schema Mutation (`novel-architect/SKILL.md`)**: Direct hand-edits to canonical ontology files (e.g., `.ncp.json`). *Why avoid:* Causes schema drift. Mutations must go through dedicated tools.
3. **Quarantined Material Reading (`vision/00-charter.md`)**: Do not read `_drafts` or legacy files. *Why avoid:* Contaminates the canonical implementation.
4. **Assume Not Implemented (`ralph-spec.md` R.3.5)**: Agentic logic assuming a capability is missing without code search. *Why avoid:* Duplicates existing logic.

## 4. Constraints from Other Columns

- **From Context**: Agentic *must* strictly validate frontmatter against `context/_shared/schemas/` before writing (PreToolUse) and *must* emit graph events after writing (PostToolUse) (`vision/context/INTERFACE-TO-AGENTIC.md`).
- **From Workflow**: Agentic *must* execute phases in strict order, adhering to blocking gates defined in `workflow/<row>/manifest.toml`, and handle the `audit_trail` extension to `ToolResult` (`vision/workflow/INTERFACE-TO-AGENTIC.md`).
- **Token Budget (`vision/00-charter.md`)**: Boot context < 500 tokens, per-tool results ≤ 4 KB.

## 5. Recommendations for `agentic/COLUMN.md`

1. **Codify the Scheduler Pattern**: Formally define that complex handlers should dispatch to subagents rather than processing locally, adopting `ralph-spec.md` R.2.1.
2. **Adopt the Envelope Extension**: Update the required typed envelope shape in the agentic manifesto to include `audit_trail` to satisfy workflow demands, or define a specific extension mechanism.
3. **Mandate Pre/Post Hooks**: Explicitly add the `PreToolUse` (schema validation) and `PostToolUse` (graph ingest) hook requirements to the handler contract in `agentic/COLUMN.md`.
4. **Formalize State Persistence**: State explicitly that skill state *must* reside in disk-backed graph nodes, not memory loops.