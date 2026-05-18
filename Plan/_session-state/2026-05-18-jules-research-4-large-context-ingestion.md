## Summary

The highest-leverage pattern for handling large contexts in the agency-system is **Ephemeral Subagent Distillation** (as seen in Spec 106 and superpowers). Instead of streaming massive payloads (e.g., 50KB GitHub PRs or deep codebase reads) into the orchestrator’s main context window, a subagent is dispatched into an isolated environment with a strict max-token limit. The subagent processes the large artifact and returns a condensed, strongly-typed summary. For file-based tasks, this pairs perfectly with the **Disk/Stats-Only Extractor** pattern (from `jules-patch-extract.py`), keeping heavy bodies entirely on disk while only structural metadata enters the LLM context.

## Source repos surveyed

| Repository | Commit SHA | Key Files Cited |
|---|---|---|
| `claude-context` | `f794b8cae6b1e2f03fc105547f2785a7c9f6dc06` | `README.md` |
| `SuperClaude_Framework` | `22ad3f483a6fe6c626834e1c9a3573126644a058` | `KNOWLEDGE.md`, `PROJECT_INDEX.md` |
| `superpowers` | `b9e16498b9b6b06defa34cf0d6d345cd2c13ad31` | `subagent-driven-development/SKILL.md` |
| `agency` | `867453e49065e16b9298b960a22fd34746985572` | `AGENTS.md`, `ADR-0006` |

## Patterns found

1. **Ephemeral Subagent Distillation (Summary Wrappers)**
   - *Source:* `Plan/106-github-mcp-summary-wrappers/spec.md`, `superpowers` (Review Subagents)
   - *Description:* Dispatching a temporary, isolated subagent to process a massive payload (like a 40k-token PR) and return a small, typed Pydantic proto (e.g., `PRSummary`). The main session never sees the raw string.
   - *Applicability:* Paging through a 200-comment PR thread or summarizing a 50-page spec PDF.
   - *Token impact:* Massive reduction (e.g., 40k+ tokens reduced to ≤2,000 output tokens).
   - *Leverage:* High. It protects the primary agent's reasoning loop from being derailed by noisy, unrelated details.

2. **Disk-Bound / Stats-Only Extractor**
   - *Source:* `tools/jules-patch-extract.py`, `context-safe-patch-handling/SKILL.md`
   - *Description:* External artifacts are processed line-by-line via Python directly on disk. Only metadata (e.g., file counts, diff filenames, bytes) is returned to the orchestrator stdout.
   - *Applicability:* Inspecting large diffs or huge log files without using `cat`, `head`, or `grep` from the main context.
   - *Token impact:* Reduces multi-megabyte files to a few hundred tokens of JSON metadata.
   - *Leverage:* High. Safely allows the orchestrator to decide *whether* to act on a large file without reading its contents.

3. **Database-Backed Event Streams (SQLite Pagination)**
   - *Source:* `Plan/100-session-log-mcp/spec.md`
   - *Description:* Storing large operational event streams in a structured SQLite database. Tools expose explicit filtering and aggregation (e.g., `session_log_query`, `session_log_summary`) rather than raw dumps.
   - *Applicability:* Reading long session logs, telemetry dumps, or multi-day activity histories.
   - *Token impact:* Zero baseline token cost; bounded impact per query.
   - *Leverage:* Medium-High. Enables fast debugging without scrolling through history.

4. **Static Context Indexing**
   - *Source:* `SuperClaude_Framework` (`PROJECT_INDEX.md`)
   - *Description:* Creating a highly condensed `PROJECT_INDEX.md` document that maps the codebase structure and rules. The agent reads this ~3,000-token file to understand the project architecture instead of grep-ing the entire source tree.
   - *Applicability:* Bootstrapping the context for new agents or fresh sessions entering a mature repository.
   - *Token impact:* Fixed ~3k token cost up front, preventing 10k-50k token exploratory code reads.
   - *Leverage:* Medium. Excellent ROI ("25-250x savings") but requires index freshness maintenance.

5. **Frontmatter Summarization & Auto-Load Exemptions**
   - *Source:* `agency` (`AGENTS.md`, `ADR-0006`)
   - *Description:* Mandating a strict `summary:` YAML key for all large specs. Agents read just the summary field. Large corpora are explicitly exempted from auto-loading to prevent accidental budget blowouts.
   - *Applicability:* Navigating 50KB+ files like `AGENTS.md` or large reference materials.
   - *Token impact:* Reduces file ingestion from 50KB to just the length of the summary string (often < 100 tokens).
   - *Leverage:* Low implementation cost, high discipline payoff.

6. **Semantic Search / "Think-in-Code" Handoff**
   - *Source:* `claude-context`, `Plan/108-context-mode-integration/spec.md`
   - *Description:* A vector database or HTTP `/ctx-insight` bridge serves relevant snippets based on embeddings. When a tool expects to return >2KB, it hands execution over to `ctx_execute` instead of printing directly.
   - *Applicability:* Searching multi-million line repos or massive documentation sets.
   - *Token impact:* Bounded token usage based on search thresholds.
   - *Leverage:* Medium. Requires robust backend infrastructure.

## Concrete shortfalls of the current plugin

1. **PR-Body Paging in the Main Thread:** `mcp__github__pull_request_read` currently streams full PR bodies, diffs, and comments into the orchestrator context, resulting in massive context inflation (cited as the "#1 token sink" in Spec 106).
2. **Full Activity Dumps:** Before Spec 100, post-mortems relied on `jules_activities` dumps which "blow the token budget every time" (cited in `Plan/100-session-log-mcp/spec.md`). The plugin lacks cheap, queryable event slicing.
3. **Missing "Think-in-Code" Handoff:** For standard shell ops (`find`, `grep`), the orchestrator is prone to running commands that inadvertently echo 50KB+ output payloads into the loop. The "Think-in-Code" pattern (Spec 108) is not uniformly enforced across all system tools.

## Proposed follow-up spec slots

- `114-project-index-generator` (For automating a `PROJECT_INDEX.md` builder similar to SuperClaude_Framework)
- `115-frontmatter-summary-enforcer` (Linter to ensure `summary:` keys exist and are < 200 tokens across all `.md` files)

## Out of scope / questions for the orchestrator

- How aggressive should we be with purging the main context? (E.g., should we enforce the "Think-in-Code" handoff pattern universally for all read operations, or only those exceeding a predefined token threshold?)
- Is there a long-term plan to integrate a persistent vector DB (like `claude-context`), or are we committing solely to the sqlite/disk-based ephemeral subagent patterns for Wave C?
