## Summary
The next major architectural wave for the agency-system plugin must unify context discovery, token conservation, and agent orchestration under a single "progressive disclosure" paradigm. Currently, token sinks (like massive GitHub PR reads or eager file loads) and context blindness (lacking a global manifest) force the LLM to choose between expensive over-fetching and failure-prone under-fetching. By implementing a manifest-driven Context Mode (Specs 111-113) alongside Subagent-driven dispatch (Spec 106, Superpowers pattern) and caching layers (Spec 114, 107), we allow the orchestrator to navigate massive codebases and specs iteratively. This shift moves the plugin from a dumb proxy to a smart, stateful router that understands semantic boundaries and caching. Ultimately, this transforms large-context ingestion into a navigable graph, reducing cost per session while dramatically expanding the complexity ceiling for Spec-Driven Development.

## Source repos surveyed

| repo | commit SHA | architectural pattern observed | applicability |
|---|---|---|---|
| agency | 867453e49065e16b9298b960a22fd34746985572 | Monolithic MCP server, strict role/domain segregation. | Provides the baseline for our current `agency-system` unification. |
| SuperClaude_Framework | 22ad3f483a6fe6c626834e1c9a3573126644a058 | Extensive framework architecture built around Claude Code. | Validates the need for robust "super-framework" scaffolding for complex agentic workloads. |
| superpowers | b9e16498b9b6b06defa34cf0d6d345cd2c13ad31 | Subagent-driven development, composable skills, automated TDD loops. | Directly applicable to Spec-Driven Development and the ephemeral subagents in Spec 106. |
| claude-context | f794b8cae6b1e2f03fc105547f2785a7c9f6dc06 | Semantic search and chunked document context indexing via MCP. | High applicability for Large-Context Ingestion; validates the Context Mode manifest (Specs 111-113) and token optimizer hooks. |

## Cross-cutting themes

1. **Manifest-Driven Discovery and Progressive Disclosure**
   - **Repos**: `claude-context` (semantic indices), `superpowers` (chunked specs).
   - **Specs**: 111 (Context Mode Manifest), 103 (View Tiers & Fields Projection).
   - **Missing**: A unified search namespace that spans *both* tools (Spec 104) and context (Spec 112). Currently, tool discovery and document discovery are discrete, leading to fragmented context building.

2. **Subagent Delegation for High-Token Tasks**
   - **Repos**: `superpowers` (subagent-driven development).
   - **Specs**: 106 (GitHub MCP Summary Wrappers), 099 (Review Subagent).
   - **Missing**: A generalized primitive for yielding control. Currently, we dispatch subagents for specific wrappers, but lack a top-level `yield_to_subagent(goal, context_allowlist)` hook for arbitrary spec execution phases.

3. **Interceptors and Caching at the Tool Boundary**
   - **Repos**: `claude-context` (efficient retrieval), `SuperClaude_Framework` (context limits).
   - **Specs**: 114 (Read-Cache Delta Mode), 107 (Cache Breakpoint Ordering), 121 (.contextignore Hard Block).
   - **Missing**: Telemetry for cache hit rates and token savings (Spec 118 partially covers this, but needs to feed back into the session-log for adaptive caching strategies).

4. **Durable Audit Trails for Autonomous Orchestration**
   - **Repos**: `agency` (baseline).
   - **Specs**: 100 (Session-Log MCP), 099 (Orchestration Improvements).
   - **Missing**: Real-time observability during execution. The log is append-only for post-mortems, but active sessions lack a "what am I currently doing across all subagents" dashboard.

## Architectural recommendation

The recommended next-wave architectural focus is **Contextual Delegation via Progressive Manifests**. We should prioritize the Context Mode manifest (Specs 111-113) integrated with View Tiers (Spec 103) and Read-Cache Delta Mode (Spec 114). This enables the LLM to see a cheap, metadata-rich map of the entire workspace and request diffs or summaries instead of raw files. When tied to the v1.0 cutover (Moves 4-7 in the 2026-05-18 next-session-goal), this ensures that once all three legacy plugins are unified, the resulting monolithic plugin does not blow up the token budget. The v1.0 `agency-system` will boot with a massive tool and document surface, so progressive disclosure is the only way to maintain agility.

## Proposed follow-up spec slots

- `cross-domain-search-router`: A unified entry point that queries both the Context Manifest and the Tool Registry, returning a combined graph of relevant documents and capabilities.
- `subagent-delegation-primitive`: Generalize Spec 106's wrapper into a reusable FastMCP CodeMode decorator `@subagent(allow_list, max_tokens)` for arbitrary handler functions.
- `adaptive-cache-telemetry`: A feedback loop that adjusts TTLs and cache capacities dynamically based on Spec 100 session logs and Spec 118 quality scores.
- `workspace-diff-synthesizer`: A tool to generate a holistic session delta (combining git diffs, Spec 100 session logs, and cache invalidations) for final PR generation and review context.

## Out of scope / questions for the orchestrator

- Should this synthesis converge with the jules-research-1 through 4 findings? Yes, ideally this document serves as the capstone. We should consider scheduling a consolidation pass (e.g., `jules-research-6-final-report`) that compiles all five into a formal architectural RFC before v1.1.
- Is the HTTP JSON-RPC transport for the `agency` CLI (Spec 023) finalized, or should we evaluate stdio-multiplexing to reduce port-conflict fragility?
- How aggressively should we deprecate direct file reads (`Read` tool) in favor of forced Context Mode reads once Spec 114 (Delta Mode) is stable?
