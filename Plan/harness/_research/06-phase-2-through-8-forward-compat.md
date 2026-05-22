# Research 06 — Phase 2-8 forward-compat audit (2026-05-18)

> **Question.** Does the harness design paint Phases 2-8 of Plan/000-v2 into a corner? Should L2's implementation be dropped, deferred, or kept in the first ship?
> **Answer.** Design is forward-compatible. L2's **implementation** can be deferred to Phase 2 (post-design-tag); L2's **design** stays in the doc because Spec 022's real-boot regression coverage requires it. Phase 2-8's testing needs are satisfied by L1 alone.

This research file captures the parallel sub-agent audit done on 2026-05-18 against `Plan/000-overview.md` v2 (PR #111 branch).

## 1. Phase summary (one line each)

| Phase | Theme | Status |
|---|---|---|
| **0** | Foundation cleanup (delete `jules-plugin/`, re-home helpers) | implementation-ready |
| **1** | Anchor triad + envelope + smoke tests (104, 107, 130, 131, 105) — and this design's L1+L3 | in flight |
| **2** | Hook chain (121, 115, 114, 116, 117) | scaffolded |
| **3** | GitHub sink wrapper (106) | scaffolded |
| **4** | Context Mode Path B — manifest only (111); 112+113 already merged | partial |
| **5** | Ontology + Graph (122, 123, 124, 135) | scaffolded |
| **6** | Quality / loop / compaction (100, 118, 119, 120) | scaffolded |
| **7** | Domain handler completion (015, 016, 018, 021); 014 already merged | partial |
| **8** | Operational hardening (102, 132-139, 023 — absorbed by this design, 099-full) | scaffolded |

## 2. Per-phase harness requirements

### Phase 2 — Hook chain (121, 115, 114, 116, 117)

Each hook spec authors a Python script under `hooks/*_hook.py` invoked by Claude Code's hook system. **Tests are unit-level**: synthetic `PreToolUse` / `PostToolUse` JSON events fed to the hook script as stdin. No live `--plugin-dir` boot needed. The chain order is enforced by `hooks.json` registration (a config concern, not a test concern).

**L1 dependency.** None — hook scripts run as standalone subprocesses fed JSON. **L2 dependency.** None.

### Phase 3 — GitHub sink wrapper (106)

`mcp__github__pull_request_read` returns 40-80k tokens; spec 106 wraps it in a subagent-driven distillation that returns ≤2.5 KB. The wrapper is a tool registered like any other; the subagent dispatch reuses Spec 016's existing pattern.

**L1 dependency.** Yes — `call_tool("github_pr_summarise", ...)` to assert the ≤2.5 KB budget. **L2 dependency.** None.

### Phase 4 — Context Mode (111)

Spec 111 ships `context_manifest.json` + schema. Specs 112 + 113 already merged (anchor triad + cache + watcher). This phase is purely additive — `context_search()` queries the new manifest entries.

**L1 dependency.** Yes — `call_tool("context_search", query=..., limit=N)` to verify manifest population. **L2 dependency.** None.

### Phase 5 — Ontology + Graph (122, 123, 124, 135)

GraphQLite + Cypher extension over `~/.agency-system/cache/graph.sqlite`. Tools like `graph_cypher(query="MATCH (s:Spec) ...")`. The PostToolUse hook (Spec 124) ingests changed Markdown into the graph.

**L1 dependency.** Yes — `call_tool("graph_cypher", ...)` to verify query semantics. **L2 dependency.** None.

### Phase 6 — Quality / loop / compaction (100, 118, 119, 120)

Spec 100 is a **separate FastMCP server** (`session-log-mcp`) — not part of agency-system. Specs 118/119/120 are hooks (quality score, loop detect, compaction checkpoint). Same pattern as Phase 2.

**L1 dependency.** Spec 100's tools are exercisable via the same L1 pattern but against a different MCP instance. The harness's `harness_mcp()` would need a `name` parameter to support multi-server scenarios — out of scope for v1 (single agency-system instance). **L2 dependency.** None.

### Phase 7 — Domain handler completion (015, 016, 018, 021)

Additive handler work (novel skills catalogue, agentic handlers, overrides migration, novel prompt-builders). Pure L1.

**L1 dependency.** Yes — every new tool ships with a `tests/unit/<domain>/test_*.py` using L1 fixtures. **L2 dependency.** None.

### Phase 8 — Operational hardening (102, 132-139, 023, 099-full)

- 102: PR-rebase policy — Git CLI, no harness need.
- 132: Skill-tool hooks (PreToolUse/PostToolUse on `Skill|Agent` matcher) — synthetic-JSON tests, no L2.
- 133: Skill-subagent pressure tests — a CLI framework (`tools/skill_pressure_test.py`) that dispatches via Spec 016's existing `dispatching-parallel-agents` tool. Reuses existing infrastructure.
- 023: **This design absorbs Plan/023's MVP scope.** No additional Phase 8 work beyond what's in `Plan/harness/design.md` §5.
- 134-139: Process / discipline / documentation. No code dependencies.

**L1 dependency.** Spec 132's hooks need synthetic JSON tests. **L2 dependency.** None.

## 3. The L2 drop / defer / keep question

### Where does L2 add coverage L1 cannot?

| What L2 proves | What L1 proves | Gap |
|---|---|---|
| `claude --plugin-dir <repo>` boots end-to-end | `from agency_mcp.server import create_mcp` succeeds | L1 misses: manifest parsing by claude CLI, `.mcp.json` wiring, skill auto-discovery from claude CLI's perspective |
| Cold-boot token budget for `tools/list` | Warm-cache token budget after `harness_mcp()` singleton | L1 can't measure cold; Spec 131 needs cold |
| Slash-command registration in claude CLI | None | L1 can't see what `/agency-system:*` commands look like in a live session |

### Which specs name `claude --plugin-dir` as a requirement?

Searched all `Plan/*/spec.md`:

- **Spec 022 (dev-mode-install).** Wave A. EXPLICITLY requires `claude --plugin-dir <path> /help` end-to-end coverage in its Gherkin scenario 022.1. **This is L2's reason for being.**
- **Spec 023 (harness-in-harness research epic).** Absorbed by this design.
- **No other Plan/*/spec.md mentions `--plugin-dir` as a test requirement.**

### Cold-boot measurement for Spec 131

Spec 131's `test_boot_budget.py` measures `tools/list` payload size. If `harness_mcp()` is session-cached, the second test invocation pulls a warm instance, which may differ from cold (FastMCP may lazy-load schemas on first list).

**Mitigation options:**

1. **Reset hook.** `harness_mcp.cache_clear()` before the cold-boot measurement test, so the next call rebuilds from scratch.
2. **Subprocess probe.** `subprocess.run([sys.executable, "-c", "from agency_mcp.server import create_mcp; mcp = create_mcp(); print(len(asyncio.run(mcp.list_tools())))"], …)` — this IS effectively L2 (or a degenerate form of it).
3. **Two-fixture design.** `harness_mcp()` (warm) + `cold_mcp()` (fresh per test).

**Verdict.** Option 1 (`cache_clear()`) is sufficient for L1's purposes. Option 2 is the L2-deferred fallback. Document both in §3.6 of the design.

### Verdict on L2

**Defer L2 implementation, keep L2 design.**

- Phase 2-8 specs do **not** need L2.
- Spec 022 (Wave A) **does** need L2 — but Spec 022 is already merged with a non-L2 smoke test that's been hardened in PR #115. The Codex P1 critique on PR #115 is satisfied once L1's `harness_mcp()` lands (test asserts `len(tools) >= 113` via in-process).
- L1's warm-singleton risk is mitigated by `cache_clear()` for cold-boot tests; L2 is the heavier fallback if that proves insufficient.
- **Tagging the design without L2 implementation is safe** — L1 + L3 cover the immediate dogfooding + external-agent needs. L2 ships in Phase 2 alongside the hook-chain specs as part of CI hardening.

## 4. External-agent specs (Phase 8)

Specs 132, 133, 137 were checked for hidden L3 requirements:

- **132 (skill-tool hooks).** PreToolUse/PostToolUse hooks gated on `Skill|Agent` matcher. Local to the in-Claude-Code plugin. No L3 surface needed.
- **133 (skill-subagent pressure tests).** CLI framework that dispatches subagents via existing Spec 016 toolkit. No new harness layer.
- **137 (watcher SDK + composable polling).** A polling SDK that external agents could use. L3's `agency tool execute` already exposes any watch tools; L3 design covers this.

**No Phase 8 spec expands L3's surface beyond the current design.**

## 5. Forward-compat checklist

The design is forward-compatible if and only if these invariants hold:

- [x] `create_mcp()` remains the single source of truth for tool registration. (Verified by Phase 1's anchor triad work — Plan/023 §Approach.)
- [x] The four-verb contract has no implicit assumptions about specific domains beyond their existence as a `domain:*` tag. (Verified by isomorphism audit, `_research/05.md`.)
- [x] L1's pytest fixtures are domain-agnostic — adding Phase 7's new domain handlers requires no harness change. (By design.)
- [x] L3's `agency tool execute` works against any tool registered by `create_mcp()` — no per-tool wrappers. (By design.)
- [x] L3's HTTP transport is the same FastMCP transport other MCP clients (Cursor, Continue, Cline) speak — no protocol bifurcation. (Plan/023 §Approach transport lock.)
- [x] No Phase 2-8 spec introduces a tool whose schema breaks JSON serialisation in `ToolResult.content[0].text`. (Verified by handler-pattern audit — all tools return `str` or `dict`.)

All six invariants hold. **Design is tag-ready.**

## References

- `Plan/000-overview.md` v2 (PR #111 branch)
- `Plan/JULES-REVIEW-LOOP.md` (PR #111 branch)
- All `Plan/0NN-*/spec.md` and `Plan/1NN-*/spec.md` files referenced in §2
- `Plan/_research/_synthesis-122-123-124.md` (if present)
- Parallel sub-agent verdict 2026-05-18 (this branch)
