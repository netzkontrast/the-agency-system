# Research Findings: Token-Efficiency Patterns

## Summary

The highest-leverage token-efficiency pattern the plugin should adopt next is **Subagent-Driven Execution with Boot Context Isolation**. While the existing spec cluster does an excellent job compressing the `tools/list` payload and read caching file payloads, it does not solve the fundamental issue that the main orchestrator session retains all execution history and intermediary artifacts in its context window. By adopting the `superpowers` subagent pattern—where discrete tasks are dispatched to ephemeral agents that boot with minimal context, execute the task, and return only a typed summary—the main orchestrator can maintain a pristine context over long-horizon tasks.

## Source repos surveyed

| Repository | Commit SHA | Key files cited |
|---|---|---|
| `netzkontrast/SuperClaude_Framework` | 22ad3f4 | `PARALLEL_INDEXING_PLAN.md`, `QUALITY_COMPARISON.md` |
| `netzkontrast/superpowers` | b9e1649 | `README.md`, `skills/writing-skills/SKILL.md`, `skills/writing-skills/anthropic-best-practices.md` |
| `netzkontrast/claude-context` | f794b8c | `README.md` |
| `netzkontrast/agency` | 867453e | `AGENTS.md`, `SKILLS.md`, `TASK.md` |

## Patterns found

1. **Subagent Task Execution** (`superpowers` - `README.md`)
   - **Description:** Instead of the main agent executing every step, the main agent coordinates while ephemeral subagents execute isolated tasks (e.g., test-driven development iterations). The subagents return concise summaries, shielding the main agent's context from intermediate code variations and stdout.
   - **Differences from Plan cluster:** Specs 106 does this for a specific tool (`gh_pr_summary`), but this pattern applies to the *entire development workflow* (running bash, compiling, running tests).
   - **Impact:** High token impact. Eliminates thousands of tokens of compilation/test-runner output from the main context window.
   - **Leverage:** High.

2. **Parallel Subagent Indexing** (`SuperClaude_Framework` - `PARALLEL_INDEXING_PLAN.md`)
   - **Description:** Five subagents execute concurrently to analyze different parts of the repository (code structure, documentation, config, tests, scripts). They merge their JSON outputs into a single index.
   - **Differences from Plan cluster:** No current spec proposes parallel execution for gathering context. Spec 114 caches single reads, but doesn't parallelize broad exploration.
   - **Impact:** Medium token impact (reduces turns and wall-clock time), but primarily an orchestration efficiency play.
   - **Leverage:** High.

3. **Frontmatter Summary Pre-fetching** (`agency` - `AGENTS.md`, `TASK.md`)
   - **Description:** Every operational file requires a `summary` field in its L1 YAML frontmatter. Agents are instructed to read this `summary` field (often via a separate manifest or index tool) *before* opening the full file body.
   - **Differences from Plan cluster:** Spec 103 projects fields from API payloads, and Spec 104 summarizes tools, but this pattern applies to on-disk markdown files and prompts.
   - **Impact:** High token impact. Avoids loading 50k tokens of irrelevant research docs just to find the right one.
   - **Leverage:** Medium.

4. **Skill Context Separation** (`superpowers` - `skills/writing-skills/anthropic-best-practices.md`)
   - **Description:** Instead of loading all reference data into a skill's primary `SKILL.md`, the skill instructs the agent to use bash tools to read specific reference files (e.g., `reference/finance.md` vs `reference/sales.md`) only when needed.
   - **Differences from Plan cluster:** This is a documentation/prompt-engineering pattern, distinct from the programmatic hooks in Specs 114-121.
   - **Impact:** Medium token impact (reduces boot context).
   - **Leverage:** Medium.

5. **Strict Schema Loading Disciplines** (`agency` - `AGENTS.md` NO.5)
   - **Description:** Narrative schemas (~40k tokens) are actively blocked from loading in non-narrative tasks by a programmatic linter hook.
   - **Differences from Plan cluster:** Spec 121 (contextignore) is a path-based hardblock, whereas this is a domain-aware load gate enforced by a pre-commit check (`check-narrative-ontology-load.py`) that alerts the agent.
   - **Impact:** High token impact for non-narrative sessions.
   - **Leverage:** Low (highly specific to the domain).

6. **Abstract Syntax Tree (AST) Chunking** (`claude-context` - `README.md`)
   - **Description:** When chunking code for hybrid search/retrieval, chunks are split along AST boundaries (functions, classes) rather than arbitrary line counts, keeping semantic context intact.
   - **Differences from Plan cluster:** Spec 115 introduces AST maps, but `claude-context` utilizes this for intelligent retrieval chunking.
   - **Impact:** Medium token impact (improves retrieval quality per token).
   - **Leverage:** Medium.

7. **Token Budget Assertion Testing** (`SuperClaude_Framework` - `QUALITY_COMPARISON.md`)
   - **Description:** Test suites include assertions on token consumption (using a `TokenBudgetManager` fixture or similar) to prevent regressions during refactors.
   - **Differences from Plan cluster:** Specs 104, 105, 106, and 107 mention token-budget regressions in their "Done When" sections, but this pattern formalizes it as a generalized test fixture pattern across the suite.
   - **Impact:** Neutral on raw usage, High impact on regression prevention.
   - **Leverage:** Medium.

## Where the existing Plan/ cluster has gaps

1. **Orchestrator Context Isolation:** Specs 103-107 compress what MCP tools return, and Specs 114-121 compress what bash/read tools return. However, nothing addresses the accumulation of these compressed outputs in the *main orchestrator's* history over a 30-turn session. The subagent pattern (`superpowers`) solves this by moving execution turns to ephemeral sessions.
2. **On-Disk File Summarization Protocol:** Spec 103 solves API projections (`view="summary"`), but there is no equivalent protocol for quickly scanning the hundreds of markdown files in the repo. The `agency` pattern of enforcing `summary` fields in frontmatter and only querying those first is missing from the unified plugin tooling.
3. **Parallel Task Execution:** The current specs assume sequential tool usage. The `SuperClaude_Framework` parallel indexing pattern demonstrates significant wall-clock and token-efficiency gains by dispatching multiple read/analysis tasks simultaneously and reducing them, which is unsupported by the current linear CodeMode architecture.

## Proposed follow-up spec slots

- `122-subagent-execution-workflow`
- `123-markdown-frontmatter-index-tool`
- `124-parallel-dispatch-registry`

## Out of scope / questions for the orchestrator

- How aggressive should we be with pushing subagent architectures (e.g. `superpowers` pattern) versus optimizing within the existing Code Mode constraint model? Subagents fundamentally alter orchestration control flow.
- Should parallel indexing (pattern #2) be implemented via a new multi-threaded Python executor within `agency-mcp` or deferred entirely to the Claude-native orchestrator layer?
