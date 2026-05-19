---
slug: 2026-05-19-agency-base-improvements
type: improvements
status: ready
owner: jules
created: 2026-05-19
summary: Ideas for making the agency-system core leaner and more isomorphic, responding to PR #133.
---

## Triad analysis — argue for (agentic / workflows / context) vs the PR's 5+1

The PR proposes a 5+1 model (`music`, `novel`, `jules`, `context`, `shared`, plus the skill-only `agentic` meta-domain). The human suggests collapsing this to THREE domains:
- `agentic` = agent infrastructure (Jules + MCP + skills + harness-in-harness)
- `workflows` = creative pipelines (music, novel)
- `context` = knowledge substrate (graph + frontmatter + search + pandoc + templates + schemas)

### Steelmanning the loser (5+1 domains)
The 5+1 structure closely mirrors the exact historical boundaries between codebases (`bitwize-music` and `jules-plugin`). Keeping `music` and `novel` separate reflects their distinct skill trees, specific routing graphs, and isolated data structures. Maintaining `shared` explicitly avoids cross-domain contamination of primitives, and isolating `jules` provides a strong boundary around remote orchestration. The `context` and `agentic` split preserves the distinction between "what the system knows" vs. "how the system operates." The 5+1 layout is extremely literal and maps 1:1 to previous plugins.

### Arguing for the Triad (agentic / workflows / context)
The Triad is vastly superior for an isomorphic system. The 5+1 model suffers from extreme fragmentation, creating unnecessary integration friction. `shared` is an anti-pattern domain; if something is truly a system primitive, it belongs in the `agentic` or `context` substrate. Splitting `music` and `novel` when they share the exact same Phase/Chain structure (pre-gen, pre-release vs structural, drafting) misses the opportunity to unify creative pipelines under a single `workflows` domain. Unifying them forces the system to abstract the *concept* of a pipeline rather than hardcoding music vs. novel specifics.

Consolidating `jules` (remote orchestration) into `agentic` (local orchestration/harness) creates a single unified control plane. The Triad explicitly separates the *Machine* (agentic), the *Work* (workflows), and the *Space* (context), cleanly matching the philosophical decoupled model pioneered by `netzkontrast/agency`. This drastically reduces the surface area, simplifies the central routing graph, and forces better abstractions.

## Top 5 ideas (ranked by impact/cost ratio)

### 1. Collapse the twin Anchor Triads into a single "Artefact Triad"
**PITCH:** Instead of 6 eager tools (`agency_tool_search/describe/invoke` and `agency_skill_search/describe/dispatch`), collapse them into 3: `agency_search`, `agency_describe`, `agency_execute` which accept an optional `type="tool" | "skill"` parameter (defaulting to searching both).
**IMPACT:** Saves ~300 tokens on every cold boot by halving the eager tool descriptions. Reduces the core mental model from 6 tools back to 3 primitives. Massive isomorphism gain.
**RISK:** Minor reduction in autocomplete discoverability for purely tool-driven agents.
**COST:** Rewriting the router logic to handle the unified `ToolResult` envelope and `type` discriminator. Very low cost.

### 2. Collapse the 8 ADRs into 3 Structural Epics
**PITCH:** The 8 ADRs in the PR are fragmented. ADRs 0002 (Single MCP), 0003 (Domain contract), and 0005 (ToolResult) should collapse into one "Unified Isomorphic Harness" epic. ADRs 0006 (Frontmatter canon) and 0008 (Wave D graph) collapse into "Context Substrate". ADRs 0001 (Router), 0004 (Triad) and 0007 (Code Mode) collapse into "Agentic Routing".
**IMPACT:** Reduces the cognitive load of reading 8 documents into reading 3 clear domain-aligned epics (Agentic, Workflows, Context).
**RISK:** We lose some granularity in tracking independent decisions.
**COST:** Medium. Requires merging markdown files and reconciling their `Falsifier triggers` into unified lists.

### 3. Unify Manifest and Graph: The Manifest IS the Graph
**PITCH:** Currently, the system builds a `manifest.toml` and then separately ingests frontmatter into a GraphQLite Cypher `graph.sqlite` (ADR-0008). We should drop the manifest entirely and make the Graph the singular source of truth. A "manifest" is just a pre-computed Cypher projection (`MATCH (n) RETURN n`) dumped to JSON at boot.
**IMPACT:** Kills the "sync drift" between manifest and graph. Eliminates an entire file format (`manifest.toml`). Simplifies `context` domain.
**RISK:** Boot time might increase slightly if the projection takes time.
**COST:** High. Requires rewriting the bootloader to read from the `.sqlite` DB or a JSON projection of it instead of parsing `toml` files.

### 4. Code Mode Opt-Out via Envelope Interceptor (Kill `prefers_codemode`)
**PITCH:** Code Mode is currently opt-in (ADR-0007) due to the risk of oversize result bodies blowing up the context. Instead of a manual flag, make Code Mode *always on* but implement a strict context-interceptor in the FastMCP `ToolResult` envelope: if a tool result > 4KB, the sandbox intercepts it, archives it to disk, and only returns a `file://` URI to the LLM. The LLM can explicitly `cat` if needed.
**IMPACT:** Kills the `prefers_codemode` frontmatter entirely. Ensures the agent always uses the most efficient mode without human configuration.
**RISK:** Agents might get confused by the URI and fail to `cat` the file, requiring slight prompt adjustments.
**COST:** Medium. Requires intercept logic in the sandbox wrapper.

### 5. Inline `/agency` SKILL.md as the Entry-Point Dispatcher
**PITCH:** Do not make the central router a separate `SKILL.md` file (ADR-0001). Instead, make the router the fundamental `prompt_hook` of the agentic MCP server. When an agent boots, the system injects the router algorithm directly into the system prompt, rather than making the agent "discover" it.
**IMPACT:** Saves the agent a full round-trip of having to call `agency_skill_dispatch` just to figure out what to do. The agent wakes up already knowing the workflow.
**RISK:** Increases the baseline system prompt size by ~100 lines.
**COST:** Low. Just move the markdown from `SKILL.md` to the agent's initialization template.

## Long tail
1. Drop `shared` entirely; distribute its primitives to `context` and `agentic`.
2. Kill `agency_tool_describe` if schema is already passed to the LLM natively via MCP.
3. Replace the `PostToolUse` ingest hook with a background filesystem watcher (like `jules-plugin` does) to decouple write latency from graph ingestion.
4. Merge `agentic` plan/workflow/research into the Triad's concept of a `Machine` (from `netzkontrast/agency`).
5. Kill the 5-stage hook chain; replace it with just 2: `PreFlight` and `PostFlight`.
6. Collapse meta-loop artifacts (ADRs, briefs, sessions, friction-logs) into a single generic `Artefact` with a `kind:` discriminator.
7. Use SQLite JSON paths instead of full GraphQLite Cypher to reduce dependency footprint.
8. Unify `music` and `novel` frontmatter into a single `CreativeWork` schema.
9. Drop the `Domain(ABC)` class requirement; just discover functions decorated with `@domain_tool`.
10. Combine `music_album_ops` and `novel_architect_structure` into generic `workflow_structure_ops`.
11. Eliminate the `jules` domain and make all async agent dispatch a core feature of the `agentic` domain.

## Should-kill
- **The 5+1 Domain Model:** It is literal legacy baggage. It should be killed and replaced by the Triad.
- **The Twin Anchor Triads (6 tools):** Bloated and redundant. Kill the split and use a single triad.
- **GraphQLite Cypher requirement:** Overkill for a repo-scoped graph. Standard SQLite with JSON1 extension is sufficient and has zero extra dependencies.
- **`prefers_codemode` flag:** Kills automation. If the system is robust, it shouldn't need a manual safety switch.
- **`manifest.toml`:** Redundant if the Wave D graph exists.

## Inspiration mining
### What to steal from `netzkontrast/agency`:
- **The Decoupled Mental Model:** Machine (orchestration), Actor (prompts), Space (research), Capability (skills). This is brilliant and maps perfectly to the Triad.
- **Strict Linting on Boundaries:** The pre-commit hooks that prevent Prompts from being inlined into Tasks.
- **Single Root Governance:** The `AGENTS.md` file that strictly routes agents on boot.

### What to explicitly REJECT:
- **Complex Folder Structures:** `netzkontrast/agency` splits things into `/tasks/`, `/prompts/`, `/research/`. We should maintain the Domain isolation (Workflows vs Context) rather than a global flat list.
- **Overbearing Task Syntax:** Their `/tasks/<NNN>-<slug>/task.md` model is too rigid. We should stick to our Markdown frontmatter graph.
- **Manual setup scripts:** Relying on agents to run `./install.sh` and `check-governance.sh` manually is prone to failure. Our system should auto-bootstrap via the MCP server boot cycle.
