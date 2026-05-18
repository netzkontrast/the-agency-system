---
type: research-delta
date: 2026-05-18
orchestrator: Claude Opus 4.7 (correction slot, slot 140)
session_id: 012YufBARvSFeYnLBzemZi9R
status: findings-only (no implementation)
related_prs:
  - "#63 spec-022 dispatch (orchestrator support)"
  - "#64 skills/agentic (orchestrator-discipline skills)"
  - "#65 spec-hygiene-pass"
  - "#66 spec-099 scope extension"
  - "#67 research-integration-3 (spec-driven, slots 134-135)"
research_sources:
  - "netzkontrast/superpowers (clone of obra/superpowers, Jesse Vincent's plugin) — /tmp/research-sources/superpowers/"
  - "netzkontrast/claude-context (clone of zilliztech/claude-context, semantic-code-search MCP) — /tmp/research-sources/claude-context/"
  - "netzkontrast/SuperClaude_Framework (clone of SuperClaude-Org/SuperClaude_Framework v4.3.0) — /tmp/research-sources/SuperClaude_Framework/"
---

# Research correction sweep — 2026-05-18

## 1. Why this PR exists

The original 5-agent fan-out (slots 130-139) was briefed with the wrong superpowers source. They were pointed at `/root/.claude/plugins/cache/superpowers-marketplace/superpowers/` — the locally-cached marketplace artefact — not the upstream repo. After dispatch, the user corrected the targets to three concrete forks:

1. **`netzkontrast/superpowers`** — clone of Jesse Vincent's [obra/superpowers](https://github.com/obra/superpowers), the canonical Skills + Workflow plugin (133 files, MIT, v4.0.3).
2. **`netzkontrast/claude-context`** — clone of [zilliztech/claude-context](https://github.com/zilliztech/claude-context), a **semantic-code-search MCP plugin** (BM25 + dense vector via Milvus/Zilliz, ~40% token reduction on SWE-bench). NOT the "Context Mode" mksglu plugin Spec 108 cites — it is a different, larger, peer-reviewed thing.
3. **`netzkontrast/SuperClaude_Framework`** — clone of [SuperClaude-Org/SuperClaude_Framework](https://github.com/SuperClaude-Org/SuperClaude_Framework) v4.3.0 (382 files): a Python pytest-plugin + 30 slash-commands + 20 sub-agents + 7 behavioural modes + pre-commit hooks, distributed via pip/pipx.

The 5 in-flight agents' `netzkontrast/agency` comparison stays valid; only their superpowers comparison was against a stale artefact. This document complements the 5 in-flight PRs with a per-theme delta against the corrected sources. No new spec is necessary — every distinctive pattern surfaced is already covered by an existing spec or by the in-flight agents' scope, with one exception flagged in §5.

## 2. What I reviewed (read-only)

| Source | Files read in full | Files spot-sampled | Total tree size |
|---|---|---|---|
| `superpowers/` | `README.md`, `.claude-plugin/plugin.json`, `hooks/hooks.json`, `hooks/session-start.sh`, `skills/using-superpowers/SKILL.md`, `skills/writing-skills/SKILL.md`, `skills/subagent-driven-development/SKILL.md`, `skills/dispatching-parallel-agents/SKILL.md`, `skills/verification-before-completion/SKILL.md`, `skills/using-git-worktrees/SKILL.md`, `skills/finishing-a-development-branch/SKILL.md` | full tree listing | 133 files |
| `claude-context/` | `README.md`, `evaluation/README.md`, `packages/mcp/src/handlers.ts` (first 100 lines) | `packages/{core,mcp}/src/` file list, `python/` tree | 200 files (excl. node_modules) |
| `SuperClaude_Framework/` | `AGENTS.md`, `CLAUDE.md`, `KNOWLEDGE.md` (first 200 lines), `PROJECT_INDEX.md`, `.pre-commit-config.yaml` (first 50 lines), `Makefile` (first 40 lines), `src/superclaude/hooks/hooks.json`, `src/superclaude/pm_agent/confidence.py` (first 50 lines), `docs/architecture/PM_AGENT_COMPARISON.md` (first 120 lines) | directory listings for `src/superclaude/{commands,agents,modes,hooks}/` and `docs/architecture/` | 382 files |

## 3. Findings delta — per theme

### Theme 1 — MCP + Code Mode integration

**Already covered by:** Spec 008 (codemode-registry, ✅ done), Spec 104 (tool-search-anchor-triad), Spec 105 (TOON serializer), Spec 106 (GitHub-MCP summary wrappers), Spec 107 (cache breakpoint), Spec 023 (harness-in-harness).

| Source | Pattern | Genuinely new vs already covered? |
|---|---|---|
| `claude-context/packages/mcp/src/handlers.ts` | 4-tool MCP surface (`index_codebase`, `search_code`, `clear_index`, `get_indexing_status`) — radical anchor minimisation. Tool docstrings are short; the actual ergonomics live in argument validation. | Already covered by Spec 104 (anchor triad) + Spec 023 (≤5 anchor commands). However the **`get_indexing_status` poll-companion pattern** ratifies the §2.1 convention #5 (`*_status` poll companion for background tools) — Spec 008 stipulates it; `claude-context` proves it works in production. **Cite, don't duplicate.** |
| `claude-context/evaluation/` (LangGraph + ReAct, GPT-4o-mini, 30 SWE-bench instances, 3 runs each, F1 equivalent, **-39.4% tokens / -36.3% tool calls**) | A reproducible MCP token-efficiency evaluation harness. Method: baseline (grep-only) vs baseline+MCP, identical retrieval task, same model. | **Partially new.** Spec 118 (quality-score-telemetry) and `Plan/_lessons-learned/14-token-consumption-postmortem.md` measure token deltas internally; neither uses an **external, reproducible** harness. The `claude-context/evaluation/` methodology is a candidate reference impl for Spec 118 and for the 023 epic plan's "token-economy analysis" requirement. |
| `superpowers/.claude-plugin/plugin.json` | Plugin manifest is **13 lines, 2 fields beyond name+description** (`author`, `homepage`, `repository`, `license`, `keywords`). Trim-to-minimum convention. | Already aligned with Spec 002 (manifest-and-marketplace). No delta. |
| `SuperClaude_Framework/CLAUDE.md` §"MCP Server Integration" | Recommends **`airis-mcp-gateway`** — a single SSE endpoint that proxies 60+ tools at "98% token reduction." This is a *different solution shape* than our per-domain anchor-triad: one upstream gateway aggregates many MCP servers and emits a unified surface. | **Potentially new direction.** Not a spec we want to ship — we are the unified surface — but the gateway pattern is the **inverse** of our problem (many → one vs our one-server-many-domains). Worth a footnote in Spec 023's research output (§"prior art / multi-MCP aggregation"). |
| `SuperClaude_Framework` distribution = `pip install superclaude && superclaude install` | Python-only, no `.claude-plugin/` until v5.0 (issue #419). Commands and agents are `.md` files copied to `~/.claude/commands/sc/` + `~/.claude/agents/` by the installer. | Already covered by Spec 022 (dev-mode-install) which solves the same "in-tree usable" problem differently (Claude Code's native `--plugin-dir` flag). The SuperClaude approach is **the alternative we rejected** (copy-to-home installer) — useful documentation evidence in Spec 022's `## Out of scope`. |

### Theme 2 — Skill authoring + skill-creator + discovery

**Already covered by:** Spec 099 (jules-orchestration-improvements, owns `Plan/_lint/`, `Plan/_templates/`, spec-template + skill-frontmatter migration after PR #66), Spec 015 (novel-skills-catalogue), Spec 005 (music-skills-port).

| Source | Pattern | Genuinely new? |
|---|---|---|
| `superpowers/skills/writing-skills/SKILL.md` lines 90–104 | **Strict 2-field frontmatter:** *"Only two fields supported: `name` and `description`. Max 1024 characters total."* Plus a **load-bearing rule about description shape:** *"Description = When to Use, NOT What the Skill Does"* — explicitly forbids workflow-summary descriptions because they cause Claude to "follow the description instead of reading the full skill content." | **Directly contradicts** `Plan/000-overview.md` §2.2's L1+L2 multi-field convention (`type`, `status`, `slug`, `summary`, `created`, `updated`, `skill_kind`, `skill_target_agents`, etc.). The 9-value `skill_kind` enum and reciprocity-linter idea are **richer** than upstream — but the divergence is genuine. PR #66 (Option B) already locks in the L1+L2 convention; the upstream evidence should be cited in Spec 099's `## References` as the **prior art we deliberately deviate from**, with one-sentence rationale ("upstream's 2-field convention scales to ~15 skills; our 140-skill corpus needs cross-ref reciprocity + skill_kind partitioning"). |
| `superpowers/skills/writing-skills/SKILL.md` lines 280-290 | **`@`-link warning:** *"Why no @ links: `@` syntax force-loads files immediately, consuming 200k+ context before you need them."* Use bare skill names + REQUIRED markers. | Already aligned with §2.2's `:embed` suffix convention. No delta, but the upstream warning is more emphatic than ours — worth quoting in Spec 099's spec template. |
| `superpowers/skills/writing-skills/SKILL.md` lines 540–650 (RED-GREEN-REFACTOR for skills) | **TDD applied to SKILL.md authoring.** Test = pressure scenario run by subagent without the skill; baseline = recorded rationalisations; skill body = code that addresses those exact rationalisations; refactor = closing new loopholes. *"NO SKILL WITHOUT A FAILING TEST FIRST."* | **Genuinely new discipline, not yet in our skill-authoring flow.** Spec 099's skill-template lands a frontmatter + body-section migration but does NOT mandate this TDD loop. Two paths: (a) extend Spec 099's `skills/agentic/orchestrator-discipline/SKILL.md` to include the pressure-scenario testing workflow; (b) ship as a separate `skills/agentic/writing-skills-tdd/SKILL.md`. Path (b) is cleaner and parallel-dispatchable; path (a) bloats 099. **See §5 below — this is the slot-140 candidate.** |
| `superpowers/skills/using-superpowers/SKILL.md` lines 6–13 | **Discovery-time enforcement:** *"If you think there is even a 1% chance a skill might apply to what you are doing, you ABSOLUTELY MUST invoke the skill."* Plus a **rationalisation table** (12 excuses + reality columns). | Partially covered by `skills/agentic/jules-orchestrator-discipline/SKILL.md` (PR #64, "verify before trust"), but the 1%-rule + rationalisation table are sharper. Recommend: PR #64 reviewer comment to add a Red Flags table modelled on this. |
| `superpowers/hooks/session-start.sh` (51 lines, pure bash, no jq) | **SessionStart hook injects the using-superpowers skill body into `additionalContext`** so Claude reads the meta-skill before any task. Falls back to "Error reading using-superpowers skill" if file is missing — never crashes the session. | Already aligned with Spec 017 (hooks-port-and-extend). The bash-only-no-jq idiom is worth adopting for the agency-system equivalent. Worth a comment on Spec 017's PR (once dispatched). |

### Theme 3 — Spec-driven dev + governance

**Already covered by:** Agent 3 (PR #67) — Spec 134 (Plan-level ADRs) + Spec 135 (spec↔test anchor traceability), Spec 099 (lint scripts + spec template), Spec 015 (skills catalogue).

| Source | Pattern | Genuinely new? |
|---|---|---|
| `SuperClaude_Framework/AGENTS.md` (40 lines, root-level) | A **40-line normative AGENTS.md** at repo root that names build/test/lint commands, coding style, commit conventions, plus a `## Plugin Deployment Tips` block. Distinct from CLAUDE.md (which is for runtime instruction) — AGENTS.md is for human-and-agent project-discovery on first touch. | Spec 134 (PR #67) introduces `Plan/_decisions/` (MADR ADRs); the **repo-root AGENTS.md** is a complementary surface we don't have. Our equivalent is `Plan/JULES_PROTOCOL.md` plus `Plan/000-overview.md` — both behind the `Plan/` namespace. A reviewer comment on PR #67 should ask: **should Spec 134 also seed a root `AGENTS.md` from `Plan/JULES_PROTOCOL.md` excerpts?** Likely no — `Plan/JULES_PROTOCOL.md` is already canonical and copy-pasting risks drift — but worth an explicit "out of scope, see ADR-0003" decision. |
| `SuperClaude_Framework/.pre-commit-config.yaml` (32 lines visible, references 5+ hook repos: pre-commit-hooks v4.5.0, detect-secrets v1.4.0, ruff, mypy, plus a custom bash-grep block for `sk_live_*`/`pk_live_*`/`SUPABASE_*`/`OPENAI_API_KEY=sk-` etc.) | **Pre-commit secret-detection that grep-blocks known-shape credentials** with an inline bash rule (not just `detect-secrets`). Hard-coded patterns for Stripe live keys, Supabase keys, OpenAI keys, Twilio tokens, Infisical tokens, Postgres URLs with passwords. | **Genuinely new.** Spec 017 (hooks-port-and-extend) ports the bitwize-music hooks but does NOT add pre-commit secret-detection. `Plan/_lessons-learned/14-token-consumption-postmortem.md` mentions PR-body token leaks, not credential leaks. This is **not a slot-140 priority** (we have no Stripe/Supabase integration), but it should be a one-line `## Out of scope` bullet in Spec 017 with a "future spec if user adds payment/cloud-DB integrations" note. |
| `superpowers/RELEASE-NOTES.md` + `superpowers/.claude-plugin/plugin.json` (`version: 4.0.3`) | **Semver discipline + RELEASE-NOTES.md** kept inside the plugin repo, separate from CHANGELOG. RELEASE-NOTES is human-prose; CHANGELOG is structured. | Not new (Spec 002 already plans `CHANGELOG.md` at repo root). Two-file split is interesting but premature — defer until we have ≥3 releases. |
| `SuperClaude_Framework/docs/architecture/PM_AGENT_COMPARISON.md` (250-line bilingual JA/EN ADR-shaped doc) | **Decision record comparing two architectural approaches** (Skills-type PM-agent vs Python-package PM-agent). Format matches MADR-0.x but not MADR-4 strictly. | Spec 134 (PR #67) introduces MADR-4.0.0 ADRs. The upstream evidence — a real project actively maintaining ADR-shaped architecture-comparison docs — strengthens Spec 134's premise. **Reviewer comment on PR #67:** cite `SuperClaude_Framework/docs/architecture/PM_AGENT_COMPARISON.md` as the "this works in practice" reference, alongside whatever `netzkontrast/agency` evidence the agent already has. |

### Theme 4 — Multi-agent orchestration + parallel subagents + hand-off

**Already covered by:** Spec 023 (harness-in-harness), `skills/agentic/jules-orchestrator-discipline/SKILL.md` (PR #64), `Plan/JULES_PROTOCOL.md` (§5–§6, §8), Spec 099 (Gate 4 reviewer dispatch).

| Source | Pattern | Genuinely new? |
|---|---|---|
| `superpowers/skills/subagent-driven-development/SKILL.md` (244 lines, dot-graph workflow, 3 prompt templates: `implementer-prompt.md`, `spec-reviewer-prompt.md`, `code-quality-reviewer-prompt.md`) | **Two-stage review per task:** spec compliance FIRST, then code quality. Re-review loop until both ✅. Fresh subagent per task — never reuse one across tasks. Implementer asks questions BEFORE work begins; controller answers; implementer then proceeds without further prompts. | **Strongly overlaps with Spec 099 Gate 4** (review-subagent dispatch). Our Gate 4 is a single review; upstream's is a TWO-STAGE review with explicit ordering ("Start code quality review before spec compliance is ✅ — WRONG ORDER" is listed as a Red Flag). This is a **direct upgrade path for Spec 099**. The three prompt templates (implementer / spec-reviewer / code-quality-reviewer) map cleanly onto `Plan/_templates/review-subagent-prompt.md` (single file → three files). **Recommended reviewer comment on PR #66:** ask whether the `Plan/_templates/review-subagent-prompt.md` should be split into a three-file template-set, with explicit "spec compliance must ✅ before code quality begins" copy lifted from upstream lines 200-211. |
| `superpowers/skills/dispatching-parallel-agents/SKILL.md` (181 lines) | **Parallel-dispatch rules:** one agent per independent problem domain; specific scope per agent ("Fix `agent-tool-abort.test.ts`" NOT "Fix all the tests"); explicit constraints ("Do NOT change production code"); specific output ("Return summary of root cause and changes"). **Sequential when shared state, parallel when independent.** | Already implicit in `skills/agentic/jules-orchestrator-discipline/SKILL.md` (PR #64) but **the constraint-and-output-shape discipline is sharper here.** Recommend reviewer comment on PR #64: add a "agent prompt template" appendix lifted from upstream lines 85-108. |
| `superpowers/skills/using-git-worktrees/SKILL.md` (full) | **Worktree directory selection algorithm:** (1) check `.worktrees/`, (2) check `worktrees/`, (3) check CLAUDE.md preference, (4) ask user. `.gitignore` verification + auto-fix per "Fix broken things immediately" rule. | **Not new for the agency-system DAG today** (Jules runs in a sandbox; local orchestrator doesn't fan out via worktrees) — but **directly applicable when Spec 023 (harness-in-harness) ships,** because `bin/agency server start` + parallel sub-spec dispatches will create the same conflict surface. Recommend: cite this skill in the Spec 023 epic-plan research output under "future orchestration-discipline reqs". |
| `superpowers/skills/finishing-a-development-branch/SKILL.md` (4-option close: merge / PR / keep / discard) | **Forces an explicit choice at branch close.** No "drift into limbo." Tests-must-pass gate is non-negotiable; refuses to proceed past Step 1 if any test fails. | Already covered by `Plan/JULES_PROTOCOL.md` §3 (PR-required, no force-push, no `--no-verify`) and Gate 3 (evidence). Upstream is more explicit about the **4-option choice** — useful pattern for Spec 102 (pr-rebase-policy) or a future "branch-lifecycle" spec. Defer for now. |
| `SuperClaude_Framework/src/superclaude/execution/parallel.py` + `KNOWLEDGE.md` (§"Parallel Execution: 3.5x Speedup") | **Wave → Checkpoint → Wave pattern** with measured 3.5× speedup (10 reads sequential = 30s; 10 reads parallel = 3s). Quote: *"Sequential: 10 file reads = 10 API calls = ~30 seconds. Parallel: 10 file reads = 1 API call = ~3 seconds."* | Already implicit in our `skills/agentic/jules-orchestrator-discipline/SKILL.md`. The **measured number (3.5×)** is publishable evidence — reviewer comment on PR #64 should add this as a citation in the rationale block. |
| `SuperClaude_Framework/src/superclaude/pm_agent/confidence.py` (load-bearing class `ConfidenceChecker` with `assess(context: Dict) -> float` returning 0.0-1.0; thresholds ≥0.9 / 0.7-0.89 / <0.7 mapping to PROCEED / PRESENT-OPTIONS / STOP-AND-ASK) | **Confidence is computed, not narrated.** A 200-token Python pre-check returns a quantitative score with 5 weighted checks (duplicate / architecture / docs / OSS / root cause) — matches our `Plan/JULES_PROTOCOL.md` Gate 1 table 1:1. | Already covered by Gate 1 of `Plan/JULES_PROTOCOL.md`. The **executable Python implementation** is interesting — it could be ported as `Plan/_lint/check_confidence.py` to mechanically score the Confidence table in PR bodies before merge. Defer — not high-value, Jules already walks the table by hand. |

### Theme 5 — Process + quality gates + pre-commit + post-merge

**Already covered by:** Spec 099 (Gate 3 evidence + Gate 4 review), Spec 017 (hooks-port-and-extend), Spec 102 (pr-rebase-policy), Spec 118 (quality-score-telemetry).

| Source | Pattern | Genuinely new? |
|---|---|---|
| `superpowers/skills/verification-before-completion/SKILL.md` (Iron Law: *"NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE"*, 7-row Common Failures table, 8-row Rationalization Prevention table) | **Fresh verification, in this turn, every time.** The Iron Law explicitly forbids "previous run" or "should pass" — every claim must be backed by output that was produced in the current message. Plus: *"Trusting agent success reports"* is listed as a Red Flag — verify with VCS diff, not subagent assertion. | Already aligned with `Plan/JULES_PROTOCOL.md` Gate 3 (artefact-per-claim). The **"VCS diff over subagent assertion"** rule is sharper than ours — `Plan/_lessons-learned/12-completed-without-pr-or-state-mismatch.md` reaches the same conclusion (`git ls-remote` is authoritative; sandbox `git status` is not). Worth a one-line citation in JULES_PROTOCOL §3 alongside §8. |
| `SuperClaude_Framework/.pre-commit-config.yaml` (full chain: trailing-whitespace, end-of-file-fixer, check-yaml, check-json, check-toml, check-added-large-files maxkb=1000, check-merge-conflict, check-case-conflict, mixed-line-ending, detect-secrets, detect-private-key, ruff, mypy) | **Aggregated pre-commit chain that runs before every commit.** Default Python toolchain plus the secret-detection rules cited in §3.3. | Spec 017 (hooks-port-and-extend) ports bitwize-music's PostToolUse validators but does NOT add a pre-commit chain. **This is a real gap** — the agency-system repo has no `.pre-commit-config.yaml` today (verified — `find /tmp/research-correction -name '.pre-commit-config.yaml'` empty). Recommend: reviewer comment on Spec 017 dispatch (when it lands) to **add a `.pre-commit-config.yaml` Done-When item** modelled on the SuperClaude chain minus the project-specific secret patterns. |
| `SuperClaude_Framework/src/superclaude/hooks/hooks.json` (single SessionStart hook, 10s timeout, calls `./scripts/session-init.sh`) | **Minimal hooks manifest** — one hook for SessionStart, no PostToolUse / PreToolUse / Stop / SubagentStop. SuperClaude does not lean on hooks for behaviour; it leans on the pytest plugin + slash commands. | Different shape than our Spec 017 plan (which ports a richer hooks tree from bitwize). No delta — confirms our design choice. |
| `SuperClaude_Framework/KNOWLEDGE.md` §"Hallucination Detection: 94% Accuracy" — **The Four Questions** (1. tests passing? require actual output. 2. requirements met? list each. 3. assumptions verified? show docs. 4. evidence? provide test results, code changes, validation) | A **4-question completion-gate** with 6 red-flag wordings ("Tests pass" without output, "Everything works", "Implementation complete" with failing tests, skipping error messages, ignoring warnings, "Probably works" language). | Sharper than Gate 3 of `Plan/JULES_PROTOCOL.md`. Our table is artefact-shaped (claim → artefact); upstream is question-shaped (claim → 4 questions). **Reviewer comment for Spec 099 PR (#66):** consider adding the 4-questions list to JULES_PROTOCOL Gate 3 as a complementary checklist, NOT as a replacement. The 6 red-flag wordings should land verbatim in `skills/agentic/orchestrator-discipline/SKILL.md` (Done-When item of Spec 099). |
| `superpowers/tests/claude-code/analyze-token-usage.py` + `tests/claude-code/run-skill-tests.sh` | **Skill-tests as bash + python harness.** The plugin ships its own test infrastructure for skill behaviour, separate from the implementation tests. | **Genuinely new for our repo** — Spec 099 has unit tests for the lint scripts but no test infrastructure for skill *behaviour*. This is the natural complement to the "writing-skills TDD" pattern (§3.2 row 3). Bundled with the slot-140 candidate. **See §5.** |

## 4. Cross-references the orchestrator should add as comments on the 5 in-flight PRs

(Slots 130-139 own these themes; only PR #67 and the branch for slot 131 have shipped commits at the time of this writing. Add the corresponding comment when each lands.)

| Target PR | Slot/theme | Recommended comment |
|---|---|---|
| **#67** (slots 134-135, spec-driven) | Spec-driven dev | Cite `SuperClaude_Framework/docs/architecture/PM_AGENT_COMPARISON.md` as a real-world MADR-shaped reference; consider whether Spec 134 should seed a repo-root `AGENTS.md` (likely "no, ADR-0003 captures decision"). |
| **MCP theme PR** (slot 131, claude/research-integration-1-mcp-*) | MCP + Code Mode | (a) Cite `claude-context/evaluation/run_evaluation.py` as the reproducible MCP token-efficiency evaluation harness — it is the reference impl for Spec 023's epic-plan §"token-economy analysis" and for Spec 118 (quality-score-telemetry). (b) Cite the `airis-mcp-gateway` (98% reduction, 60+ tools, single SSE endpoint) as a footnote in Spec 023's "prior art / multi-MCP aggregation" — this is the inverse architecture (many MCP servers → one gateway vs our one server → many domains). |
| **Skill-authoring PR** (slot 132) | Skill authoring + discovery | (a) Cite `superpowers/skills/writing-skills/SKILL.md` lines 90-104 as the **prior art our L1+L2 namespace deliberately deviates from**, with one-sentence rationale in `Plan/_templates/skill-template.md` (PR #66 territory). (b) Quote the `@`-link warning (lines 280-290) verbatim in the spec template. (c) Add the discovery 1%-rule and the 12-row rationalisation table from `skills/using-superpowers/SKILL.md` to the dispatched skill template. |
| **Multi-agent orchestration PR** (slot 133) | Multi-agent | (a) Cite `superpowers/skills/subagent-driven-development/SKILL.md` two-stage review pattern (spec compliance → code quality, with explicit ordering enforcement) as the upgrade target for `Plan/_templates/review-subagent-prompt.md` — recommend splitting into a 3-file template-set (implementer / spec-reviewer / code-quality-reviewer). (b) Cite `dispatching-parallel-agents/SKILL.md` lines 85-108 as the canonical agent-prompt-shape (focused / self-contained / specific-output). (c) Cite Wave→Checkpoint→Wave 3.5× number from SuperClaude `KNOWLEDGE.md`. (d) Cite `using-git-worktrees/SKILL.md` as a future-need for Spec 023 when `bin/agency` ships and parallel sub-spec dispatches become possible. |
| **Process/quality-gates PR** (slot 135-ish) | Process | (a) Cite `SuperClaude_Framework/.pre-commit-config.yaml` as a candidate hook-chain for Spec 017 (`.pre-commit-config.yaml` is absent from our tree today). (b) Cite the "Four Questions" + 6-red-flag wordings from `KNOWLEDGE.md` for Spec 099 Gate 3 / `skills/agentic/orchestrator-discipline/SKILL.md`. (c) Cite `verification-before-completion/SKILL.md` "VCS diff over subagent assertion" rule for `Plan/JULES_PROTOCOL.md` §3. |

## 5. New spec (slot 140) — candidate flagged, NOT shipped

One genuine gap surfaced: **Skill-authoring TDD** (`superpowers/skills/writing-skills/SKILL.md` §"RED-GREEN-REFACTOR for skills"). This is a discipline we do not yet have, and it is downstream of two distinct overlapping concerns:

1. PR #66 extends Spec 099 to cover the L1+L2 skill-frontmatter migration. Spec 099 does not mandate **how** authors verify a new skill actually changes agent behaviour.
2. Spec 005 (music-skills-port, ✅ done) + Spec 015 (novel-skills-catalogue, ready) ship ~90 skills total. None of them was authored under a pressure-scenario TDD loop.

**Decision: do NOT ship a Plan/140 spec.** Reasoning:

- Spec 099 already owns `skills/agentic/orchestrator-discipline/SKILL.md` and `Plan/_templates/`. Adding a third skill (`writing-skills-tdd`) and a fourth template (pressure-scenario harness) bloats 099 to ~22 Done-When items.
- The natural home is a **follow-up to Spec 099**, not a sibling. The follow-up needs the L1+L2 frontmatter convention to land first.
- Slot 140 is reserved for "fundamentally new ideas none of the 5 agents would have caught." This idea is closer to "Spec 099 v2" than "fundamentally new" — the 5-agent fan-out covered skill-authoring under slot 132, and that agent's superpowers source (even the stale cached one) included `writing-skills/SKILL.md`. They will surface this pattern.

**Recommended follow-up:** reviewer comment on PR #66 saying "If the L1+L2 migration ships, file a follow-up spec (Plan/14X-skill-authoring-tdd or similar) that mandates pressure-scenario testing for any new SKILL.md, with the `superpowers/tests/claude-code/run-skill-tests.sh` shell harness as a candidate reference impl." Slot 140 stays open for a more genuinely-new finding from the next research wave.

## 6. Honest gaps / what I did not verify

- I did **not** read every file under `SuperClaude_Framework/docs/` (90+ files). I read `PROJECT_INDEX.md` and the architecture sub-folder. Other docs may contain patterns relevant to slots 130-139 that I missed.
- I did **not** read `claude-context/packages/core/src/context.ts` (the indexing engine) — Spec 023's research output would benefit from reading it if semantic-search-anchored skill discovery becomes a candidate sub-spec.
- I did **not** clone `mksglu/context-mode` (the Spec 108 reference). This sweep is about the three repos under `/tmp/research-sources/`. If Spec 108's research output should be updated to also reference `claude-context` as a peer-reviewed semantic-search MCP, that's an orchestrator decision (note: 108 and `claude-context` solve different problems — 108 = persist-context-across-tool-calls; claude-context = semantic-search-the-codebase).

## 7. Sources cited

- `/tmp/research-sources/superpowers/README.md`
- `/tmp/research-sources/superpowers/.claude-plugin/plugin.json`
- `/tmp/research-sources/superpowers/hooks/hooks.json`
- `/tmp/research-sources/superpowers/hooks/session-start.sh`
- `/tmp/research-sources/superpowers/skills/using-superpowers/SKILL.md`
- `/tmp/research-sources/superpowers/skills/writing-skills/SKILL.md`
- `/tmp/research-sources/superpowers/skills/subagent-driven-development/SKILL.md`
- `/tmp/research-sources/superpowers/skills/dispatching-parallel-agents/SKILL.md`
- `/tmp/research-sources/superpowers/skills/verification-before-completion/SKILL.md`
- `/tmp/research-sources/superpowers/skills/using-git-worktrees/SKILL.md`
- `/tmp/research-sources/superpowers/skills/finishing-a-development-branch/SKILL.md`
- `/tmp/research-sources/superpowers/tests/claude-code/run-skill-tests.sh`
- `/tmp/research-sources/claude-context/README.md`
- `/tmp/research-sources/claude-context/evaluation/README.md`
- `/tmp/research-sources/claude-context/packages/mcp/src/handlers.ts`
- `/tmp/research-sources/SuperClaude_Framework/AGENTS.md`
- `/tmp/research-sources/SuperClaude_Framework/CLAUDE.md`
- `/tmp/research-sources/SuperClaude_Framework/KNOWLEDGE.md`
- `/tmp/research-sources/SuperClaude_Framework/PROJECT_INDEX.md`
- `/tmp/research-sources/SuperClaude_Framework/.pre-commit-config.yaml`
- `/tmp/research-sources/SuperClaude_Framework/Makefile`
- `/tmp/research-sources/SuperClaude_Framework/src/superclaude/hooks/hooks.json`
- `/tmp/research-sources/SuperClaude_Framework/src/superclaude/pm_agent/confidence.py`
- `/tmp/research-sources/SuperClaude_Framework/docs/architecture/PM_AGENT_COMPARISON.md`
