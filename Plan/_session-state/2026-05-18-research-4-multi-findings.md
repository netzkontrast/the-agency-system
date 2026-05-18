---
type: research-findings
date: 2026-05-18
research_agent: 4-of-5
focus: multi-agent orchestration + parallel subagent patterns + cross-agent hand-off
worktree: /tmp/research-4-multi
branch: claude/research-integration-4-multi-CtdIJ
slot_range: 136-137
specs_authored: [136, 137]
status: complete
---

# Research findings — Multi-agent orchestration + cross-agent hand-off

## Comparison points read (read-only)

- `/home/user/agency/AGENTS.md` (668 lines) — the master agent contract; ratifies four agent platforms (Claude Code, Jules, Gemini, Codex) with platform-implementation notes per §"Closing Run Procedure". Key insight: AGENTS.md **codifies platform routing prose-side** but does NOT ship an executable manifest the toolchain can query.
- `/home/user/agency/CODEX.md` (52 lines) — confirms Codex is a first-class agent with a platform-native PR primitive (`make_pr`), governed by the same CR.1-CR.7 contract. CODEX.md is intentionally thin: it routes to AGENTS.md.
- `/home/user/agency/CLAUDE.md` (310 lines) — AI-assistant entry point; §13 partitions the 54 imported skills by *source* (sc-* vs superpowers-*) while AGENTS.md partitions by `skill_kind`. The two partitions cite identical skills but expose different lookup axes.
- `/home/user/agency/skills/superpowers-dispatching-parallel-agents/SKILL.md` — wraps Agency's `Agent` tool with parallel tool-use; one-shot non-overlapping subtasks.
- `/home/user/agency/skills/superpowers-using-git-worktrees/SKILL.md` — `git worktree add` safety protocol for parallel sessions on the same repo. Notably **does not** include a "lint that worktree A doesn't edit worktree B's files" — that gap is a separate research direction (left to a future spec; not slotted at 136/137 because it touches scopes Spec 099 already partly covers).
- `/home/user/agency/skills/superpowers-subagent-driven-development/SKILL.md` — the two-stage execute+review subagent pattern; the **review subagent is a separate `Agent` invocation with no shared context**. This is the canonical justification for `Plan/_templates/review-subagent-prompt.md` (Spec 099) being a *file*, not a Jinja template.
- `/home/user/agency/skills/superpowers-finishing-a-branch/SKILL.md` — three-option close decision tree (merge / PR / discard). Agency's AGENTS.md §CR contract overlaps but does NOT enumerate "discard" — the orchestrator must explicitly choose a fate.
- `/tmp/research-4-multi/Plan/JULES_PROTOCOL.md` (full, 142 lines) — §6 escalation prose says "comment on the open draft PR, prefixed `@human:`" but provides no runtime primitive to *query* the escalation target. §7 plugin specifics + §8 silent-fail recovery are excellent but Jules-specific; nothing covers Codex/Cursor/local-subagent identity.
- `/tmp/research-4-multi/Plan/023-harness-in-harness/spec.md` (199 lines) — the multi-agent epic. Builds a `bin/agency` CLI + FastMCP daemon so non-MCP agents (Jules sandbox, raw bash LLMs) become first-class consumers. **What 023 covers:** transport, anchor surface, progressive disclosure. **What 023 leaves open:** the *identity* of the calling agent (who is calling? what's their quota? what's the next hand-off?). Spec 136 fills exactly this gap.
- `/tmp/research-4-multi/Plan/099-jules-orchestration-improvements/spec.md` (149 lines) — the discipline wave. Patches `JULES_PROTOCOL.md`, creates `Plan/_lint/check_affects.py` + `check_install_consistency.py`, locks `Plan/_templates/review-subagent-prompt.md` + `spec-template.md`, codifies anti-patterns from L01-L15. **What 099 covers:** Jules-specific protocol patches, the agentMessaged ban, rebase policy, token-discipline skill. **What 099 leaves open:** anything generalising beyond Jules (Codex/Cursor/local-subagent), and any *executable* registry the orchestrator can query at runtime.
- `/tmp/research-4-multi/jules-plugin/skills/jules/references/combined_watcher.py` (107 lines) — the orchestrator's reusable poller. Three orthogonal concerns (poll, state, wake-predicate) all inlined. L09 explicitly recommends three options (A: MCP tool, B: standalone script, C: SKILL.md); current state is C-only.
- `/tmp/research-4-multi/jules-plugin/skills/jules/references/parallel-orchestration.md` (143 lines) — names the watcher as a hard reliability gate ("verify the watcher daemon is alive — a dead watcher means silent failures"). Confirms the watcher idiom is load-bearing.
- `/tmp/research-4-multi/jules-plugin/skills/jules/references/state-machine.md` (28 lines) — the Jules state vocabulary the SDK must respect.
- Eleven `Plan/_lessons-learned/*` notes (01-14). L05 (review subagent), L09 (watcher idiom), L12 (COMPLETED ≠ PR), L13 (Codex bot reviews are gold), L14 (token postmortem) directly motivate Spec 136's `closing_run_path` + `escalation_target` + Spec 137's composability.

## Promising directions evaluated

1. **Worktree-safety lint (`Plan/_lint/check_worktree.py`)** — DROPPED. Spec 099 §3 already ships rebase policy + `affects:` linting; a worktree-cross-edit lint would only fire in a multi-worktree CI environment Agency does not yet have. Adding it now is speculative.
2. **Status aggregator service** — PARTIALLY ABSORBED. Spec 100 (session-log MCP) covers Jules-side aggregation; Spec 106 (GitHub MCP summary wrappers) covers PR aggregation. A standalone `agency status` snapshot CLI would have ~30% overlap with both. **Slotted into 137's `watcher_run_until` MCP tool instead** — the orchestrator queries one tool that internally composes all sources.
3. **Per-agent role manifest (`agents.yaml`)** — AUTHORED AS SPEC 136. The gap is real: AGENTS.md routes agent classes in prose, JULES_PROTOCOL.md routes one class in prose, but the toolchain has no executable lookup. Three MCP tools (`agents_list`, `agents_describe`, `agents_handoff_plan`) + two lint scripts close the loop. The cycle check on `handoff_triggers` is the non-trivial logic — easy to TDD, easy to fail without it.
4. **Hand-off protocol formalisation** — ABSORBED into Spec 136's `handoff_triggers[]`. The "Jules → Codex review → human merge" flow becomes a declarative DAG edge in `agents.yaml`, not a prose paragraph.
5. **Watcher composability SDK** — AUTHORED AS SPEC 137. The current monolith is the orchestrator's most-reused snippet but it ships as a one-shot reference file. Extracting a `WatcherSource` protocol + `CompositeWatcher` driver makes every future source (Spec 100 session-log, Vercel deploy, GitHub-Actions check-runs) a ~30-line subclass. The snapshot test against current output is the safety net.

## Specs authored

- **`Plan/136-agents-yaml-role-manifest/spec.md`** — declarative `agents.yaml` (4 classes: jules, codex-review, local-subagent, local-orchestrator) + JSON schema + two lint scripts + three MCP tools + JULES_PROTOCOL.md §6 paragraph patch + docs/architecture page. Five Gherkin scenarios, including the `AGENTS.HANDOFF_CYCLE` cycle-detection check. Depends on Spec 099 (consumes `check_affects.py` + the review-subagent template).
- **`Plan/137-watcher-sdk-composability/spec.md`** — `jules-plugin/lib/watchers/` package (`base.py`, `jules_source.py`, `github_pr_source.py`, `composite.py`, `state.py`) + one MCP tool `watcher_run_until` + rewritten `combined_watcher.py` as a ≤30-line shim with byte-identical JSONL output (snapshot test). Five Gherkin scenarios including the legacy-state-schema migration. Depends on Spec 007 (Jules skills + commands port).

Both specs follow the four-section PR-body convention, cite Spec 099's deliverables (`Plan/_lint/check_affects.py`, `Plan/_templates/review-subagent-prompt.md`), respect the `server_py_edit: append-only` annotation, and ship TDD-first with fixture-backed `pytest` tests. Estimated 2 Jules sessions each.

## Non-overlap audit vs existing specs

| Concern | Existing spec | Overlap with 136 | Overlap with 137 |
|---|---|---|---|
| Jules protocol patches | 099 | 136 ADDS ONE paragraph to §6 (no rewrite) | none |
| Lint scripts (`Plan/_lint/`) | 099 | 136 ADDS two new lint files | none |
| Review-subagent template | 099 | 136 CONSUMES the template (no rewrite) | 137 CONSUMES the template |
| `agents.yaml` manifest | none | 136 creates it | 137 references via `agent_class` in tests' future hand-off, but does not modify |
| Session-log MCP | 100 | 136 cites the live quota counter (out-of-scope here) | 137 names `SessionLogSource` as future extension point (out-of-scope here) |
| Jules MCP tool additions | 101 | none | none (`watcher_run_until` is `domain:agentic`, not `domain:jules`) |
| PR rebase policy | 102 | none | none |
| GitHub summary wrappers | 106 | none | 137's `GithubPRSource` uses raw `gh_get` (not the summary wrapper) for low-level diffing |
| Harness-in-harness CLI | 023 | 136 formalises the agent identity behind 023's HTTP calls | 137 is the dual: in-process composability vs 023's external surface |

No content collisions. Both specs assume Spec 099 has shipped (depends_on: 099 for 136; depends_on: 100 for 137 via the extension-point note, plus 007 for the jules-plugin import path).

## Token-budget self-check

- 136's `agents_list()` is capped at ≤500 tokens for all 4 classes; `agents_handoff_plan` ≤800 tokens — respects L14.
- 137's `watcher_run_until` returns one event dict ≤1000 tokens; `Event` dataclass is JSON-serialisable; no full activity-stream dumps — respects L14.
- Both specs use the `summary_only=True` default established by Spec 101.

## What I deliberately did NOT spec

- A worktree-cross-edit lint (insufficient justification; see direction 1 above).
- A standalone `agency status` CLI (overlaps Spec 100 + 106; rolled into 137's MCP tool).
- Auto-generation of agent capabilities from runtime introspection (premature — agents.yaml is a declarative starting point; Phase 2 can introspect).
- Daemonisation of the watcher (out-of-scope per 137; lives in 023's territory).
- Multi-process state coordination (single-watcher implicit; documented in 137's out-of-scope).

## Open follow-ups for future research agents

- Spec 023's research output (`Plan/_research/023-harness-in-harness-epic-plan.md`) is still pending Subagent A/B/C synthesis. When it lands, verify Spec 136's `runtime: ide-mcp-client` enum aligns with 023's documented external-MCP-client contract.
- After Spec 100 ships, a follow-up Spec ~138 can add `SessionLogSource(WatcherSource)` and close the L09 "Option A" baked-in form for the third source.
- A `superpowers-dispatching-parallel-agents` extension that registers the parallel dispatch in `agents.yaml` (as a transient `local-subagent` row) would close the audit-graph; tabled.
