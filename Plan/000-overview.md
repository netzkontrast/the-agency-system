# Plan 000 — Agency-System Unified Plugin (Master Overview, v2)

> **Status:** drafted 2026-05-18 by orchestrator audit · supersedes v1 of 2026-05-17
> **Branch:** `claude/check-installed-plugins-1rf3k` (this PR), thereafter target `Master`
> **Goal:** Drive the-agency-system to a single token-efficient Claude Code plugin built around **one MCP (Code Mode anchor triads), graph-based context mapping (Path B docs + Wave D ontology graph), and a closed-loop hook chain**. Orchestrate the remaining implementation work over Jules with up to 60 parallel sessions and a PR review loop that runs Jules-against-Jules until no relevant feedback surfaces.

This document is the **map and sequencing authority**. Existing sub-spec directories (`001/` … `139/`) remain the source of truth for per-task acceptance criteria; this file decides which specs run, in what order, why, and how Jules drives them.

---

## 1. North star (recovered from drift)

The architecture has not changed. Three collapses, one budget:

1. **One plugin** — `the-agency-system/` repo *is* the plugin. `.claude-plugin/plugin.json` at root, `.mcp.json` mounts a single MCP server, skills live under `skills/{shared,music,novel,jules,agentic}/`, hooks at `hooks/`. No nested plugins, no sibling plugins. `jules-plugin/` is the legacy artefact and is removed in Phase 0.

2. **One MCP, Code Mode native** — `servers/agency-mcp/` with `FastMCP("agency-system", dereference_schemas=False)` wrapping an `AnchorAwareCodeMode` transform. Per domain: ~4 eager anchor tools (`*_search`, `*_describe`, `*_invoke` / `*_query`); all bulk tools registered `hidden=True, defer_schema=True`. Boot tool surface target: `tools/list` < 4 KB, total boot context < 500 tokens (was ~34 k).

3. **Graph-based context** — two complementary layers sharing one manifest schema:
   - **Path B (documents)**: `context_manifest.json` catalogues every spec/lesson/override/reference with `{id, title, summary, sha256, tags, views:{summary|preview|full}}`. Exposed via `context_search` / `context_describe` / `context_read` + a polling watcher emitting `notifications/resources/updated`. Defers ≥ 200 k tokens of preemptively-inlined docs.
   - **Wave D (ontology graph)**: an 18-type frontmatter ontology + GraphQLite Cypher extension over `~/.agency-system/cache/graph.sqlite`. Exposes `graph_cypher` / `graph_describe_node` / `graph_run_algorithm`. The same manifest entries from Path B carry a `graph_id`, so document discovery and structural queries reinforce each other.

The unifying constraint everywhere is **token efficiency**. Every spec sized by what it saves; every hook ordered to maximise prefix-cache hits.

---

## 2. Audit of current state (2026-05-18)

The repository is **further along than v1 of this overview implied**. Sub-agent audit results:

### 2.1 Done (~20 specs, mostly Wave A + B)

| Spec | Title | Evidence |
|---|---|---|
| 001 | scaffold-plugin-skeleton | `.claude-plugin/`, `servers/agency-mcp/`, `skills/` all present at repo root |
| 002 | manifest-and-marketplace | `.claude-plugin/plugin.json` + `marketplace.json` present |
| 003 | unified-statecache-port | `servers/agency-mcp/src/agency_mcp/state/cache.py` present |
| 004 / 004a | music handlers + lib port | `handlers/music/` populated, lib subtree imported |
| 005 | music skills port | `skills/music/` populated |
| 006 | jules handlers port | `handlers/jules/{lifecycle,patches,bulk,aliases,source}.py` present |
| 007 | jules skills + commands | `skills/jules/`, `commands/jules-*.md` present |
| 008 | codemode-registry | `server.py` has `_AnchorAwareCodeMode` subclass wired; `codemode/manifest.json` present (**but anchor triad tools — Spec 104 — still missing**, see drift §3.5) |
| 009 | shared-handlers | `handlers/shared/{search,reference,config,session,skills,health}.py` present |
| 010 / 011 / 011a / 012 / 013 | novel layout + handlers + libs + structural | all populated under `handlers/novel/` |
| 017 | hooks-port-and-extend | `hooks/{validate_chapter,validate_track,check_version_sync}.py` + `hooks.json` |
| 019 | state-migration-from-bitwize | migrator landed |
| 098 | wave-a-hardening | merged via PRs #34/#37/#38/#32 |
| 101 | jules-mcp-tool-additions | session_summary / pr_url / quota added |
| 103 | view-fields-projection | wired (PR #100 merged per recent git log) |
| 022 | dev-mode-install | merged via PR #73 (commit `cd15d09`); `bin/agency-dev-install` present |
| 112 | context-anchor-triad | merged via PR #104 (commit `85a8e51`); `servers/agency-mcp/src/agency_mcp/lib/codemode/context_anchor_triad.py` present |
| 113 | context-cache-and-subscriptions | merged via PR #113 (commit `883eb45`) during this PR's review-loop; Phase 4 spec count drops further |
| 014 | novel-gates-and-revision | merged via PR #108 (commit `5954832`) during this PR's review-loop; §2.2 now empty |

### 2.2 In-progress (0)

(empty — Spec 014 merged during this PR's review loop)

### 2.3 Scaffolded specs without implementation (~40)

Phases 1-8 below assign each of these to a phase or mark them superseded:

- **Token efficiency**: 104, 105, 106, 107, 114, 115, 116, 117, 121 (all assigned: Phase 1 → 104/105/107/130/131; Phase 2 → 114/115/116/117/121; Phase 3 → 106)
- **Context layer (Path B)**: 111 only (112 and 113 already done — see §2.1) — competing with 108 (see drift §3.1)
- **Token-optimiser hook layer**: 114-121 (composes with Path B)
- **Quality / loop / compaction**: 118, 119, 120
- **Ontology + graph (Wave D)**: 122, 123, 124
- **Operational discipline drafts**: 130, 131, 132, 133, 134, 135, 136, 137, 138, 139
- **Other**: 015, 016, 018, 020, 021, 023, 099, 100, 102

### 2.4 Legacy artefact

`jules-plugin/` is fully implemented (16 MCP tools, 1 skill, 8 reference docs, 8 pytest files, 2 CLI helpers) — and **already marked `"deprecated": true`** in `jules-plugin/.claude-plugin/plugin.json`. Its content was ported to `servers/agency-mcp/handlers/jules/*` (Spec 006/007). Phase 0 deletes it.

---

## 3. Drift analysis — where the design wandered

Five concrete drifts, each with a resolution:

### 3.1 Two-path indecision on Context Mode

**Drift:** Spec 108 (adopt third-party `mksglu/context-mode` plugin) and the Path B trio — Specs 111 (manifest), 112 (anchor-triad), 113 (cache + subscriptions) — were mutually-exclusive in v1 ("PICK ONE PATH" but never picked one). Specs 112 and 113 have since landed under Path B's design (PRs #104, #113), confirming the direction empirically; only 111 (manifest) plus the 108 supersession marker remain.

**Resolution — D1: ADOPT PATH B (111 + 112 + 113). SUPERSEDE 108.** (112 and 113 already merged; 111 + 108-stub still to land — see Phase 4.)

Reasons:
1. Path B's manifest schema is the same shape Wave D's graph ingests — sharing `{id, sha256, tags, views}` means one watcher serves both, one cache invalidates both, one `graph_id` field on every manifest entry is enough to bridge.
2. We control the truncation cap, the tag taxonomy, the BM25 ranker — third-party `mksglu/context-mode` is a hook-layer adapter and would force a translation shim.
3. Spec 108 lists 5 hook entry points and 26 event categories that don't map cleanly to our existing PostToolUse chain (`bash-compress → context-mode-sync → graph-ingest → archive`). The sync overhead exceeds the win.

Spec 108 is **rewritten in Phase 4 as a superseded stub** that points to 111/112/113.

### 3.2 Token-optimiser hook layer (114-121) bolted on without overlap analysis

**Drift:** Specs 114-121 were copied from an external token-optimiser project (see lesson `14-token-consumption-postmortem.md`) without explicit overlap analysis against Path B. Result: drafted-but-orphaned hook specs.

**Resolution — D2: KEEP all of 114-121 — they are *orthogonal* to Path B and compose with it.**

Path B handles **document deferral** (200 k+ tokens of specs/lessons/overrides). The hook layer handles **runtime tool-output compression**. Both feed the same archive (117) and the same session-log (100). Wired in this canonical PreToolUse → PostToolUse order:

```
PreToolUse:        contextignore (121) → structure-map (115) → read-cache-delta (114) → context-mode-sync
PostToolUse:       bash-compress (116) → context-mode-sync → graph-ingest (124) → archive (117)
UserPromptSubmit:  quality-score (118) + loop-detect (119)
PreCompact:        checkpoint snapshot (120)
CompactionEnd:     checkpoint restore (120)
```

This chain ordering is **the contract** Phase 2 implements.

### 3.3 Operational discipline drafts (130-139) queued behind 099

**Drift:** Ten "discipline" specs were authored in the 2026-05-18 research sweep, all marked `draft`, all chaining off 099 (jules-orchestration-improvements) which itself is scaffolded. They are the polish layer, but they're stalling the architectural phases.

**Resolution — D3: Defer 130-139 to Phase 8 (Operational Hardening). Three exceptions:**

- **130 (shared-toolresult-envelope)** is a contract every other phase depends on — **moves up to Phase 1**, locking the envelope before any new handler tool ships.
- **131 (manifest-coverage-lint)** prevents regressions on the anchor triad — **moves up to Phase 1**, runs in the smoke test.
- **135 (spec-test-anchor-traceability)** is needed to verify Wave D acceptance — **moves up to Phase 5**.

All others stay deferred; the bus-factor cost of not having them yet is acceptable while the architectural spine is finishing.

### 3.4 jules-plugin/ on disk after being marked deprecated

**Drift:** Spec 020 (bitwize-deprecation-and-docs) was scoped for the bitwize plugin and the jules-plugin together but only the bitwize side was executed.

**Resolution — D4: Phase 0 deletes `jules-plugin/` in full** (under Spec 020). Smoke test asserts the directory no longer exists. CLAUDE.md is updated to drop the "Jules orchestration plugin" section's `--plugin-dir ./jules-plugin` install path. The CLI helpers (`bin/jules-bulk`, `bin/jules-dev-install`) and reference docs are re-homed:

- `bin/jules-bulk` and `bin/jules-dev-install` → `bin/` at repo root.
- `skills/jules/SKILL.md` + 9 references → already mirrored at `skills/jules/` at repo root via Spec 007; the duplicates inside `jules-plugin/` are deleted.
- `tools/researcher/` → moves to `tools/researcher/` at repo root (it was tangentially placed inside `jules-plugin/` and is plugin-agnostic).
- All `jules-plugin/tests/` are merged into `tests/jules/`.
- **`skills/agentic/jules-orchestrator-discipline/SKILL.md:131` references `jules-plugin/skills/jules/references/combined_watcher.py`.** Phase 0 MUST update this reference to point at the new home (`skills/jules/references/combined_watcher.py`, already present from Spec 007), OR remove the reference if the discipline skill no longer needs it. A grep for `jules-plugin/` across `skills/`, `commands/`, `hooks/`, `docs/`, and `CLAUDE.md` is part of the Phase 0 smoke test; any surviving hit fails the build.

### 3.5 Anchor triad (104) missing despite registry (008) marked done

**Drift:** Spec 008 created `_AnchorAwareCodeMode` and wires the anchor list from a registry, but the registry currently returns an empty/near-empty set because Spec 104's three eager tools (`agency_tool_search` / `agency_tool_describe` / `agency_tool_invoke`) were never authored. Result: every backend tool is still hidden, and the model has no discovery path — the optimisation is half-deployed.

**Resolution — D5: Phase 1 ships Spec 104 alongside the cache-breakpoint reorder (107) and the envelope (130). These three land as a single coordinated PR-set so the prompt-cache invariant holds from the moment the triad ships.**

---

## 4. Phase map

Eight phases. Each phase is one PR-set (1-N PRs depending on independence). Each PR maps to exactly one sub-spec. Dispatch order respects deps; within a phase, parallel where independent.

| Phase | Name | Specs (existing sub-spec dirs) | Token-budget win | Blocking deps |
|---|---|---|---|---|
| **0** | Foundation cleanup | 020 (extended), 099 stub | none directly; removes confusion | none |
| **1** | Anchor triad + envelope (cold-start) | 104, 107, 130, 131, 105 | tools/list 38k → <4k tokens + 40-60% on list returns (TOON) | Phase 0 |
| **2** | Hook chain | 121, 115, 114, 116, 117 | 20-30% of session input | Phase 1 (envelope) |
| **3** | GitHub sink wrapper | 106 | 40-80k → <2.5k per PR/issue read | Phase 1 (envelope), Phase 2 (archive) |
| **4** | Context Mode (Path B) | 111 + 108-stub (Specs 112 + 113 already merged — PRs #104, #113) | defers ≥200k of inline docs | Phase 1 (anchors) |
| **5** | Ontology + Graph (Wave D) | 122, 123, 124, 135 | cross-domain queryability | Phase 4 (manifest schema sharing) |
| **6** | Quality / loop / compaction | 118, 119, 120, 100 | self-healing context, ~47k saved per loop | Phase 2 (session-log canon) |
| **7** | Domain handler completion | 014, 015, 016, 018, 021 | feature completeness | Phase 1 (envelope), Phase 5 (ontology) |
| **8** | Operational hardening | 102, 132, 133, 134, 136, 137, 138, 139, 023, 099-full | polish + bus-factor | optional / continuous |

### 4.1 Highest-leverage order (the "ship-first 6", per token-efficiency audit)

When phase work is parallelised, this ordering preserves the most token savings per Jules-session-hour:

1. **104 + 107 + 130** (Phase 1) — cold-start triad + breakpoint + envelope. Single biggest one-shot win; prerequisite for every later phase's measured boot budget.
2. **103** — already done; verify wired and projected.
3. **121 + 115 + 114** (Phase 2 first half) — PreToolUse chain. Lands the 20-30% of session input from re-reads.
4. **117** (Phase 2 second half) — universal 4 KB archive guardrail. Final-net for anything that escapes upstream compression.
5. **106** (Phase 3) — GitHub PR/issue subagent wrapper. Single largest measured leak (40-80k tokens/call).
6. **111** (Phase 4) — Path B documents (manifest only; 112 + 113 already merged via PRs #104, #113).

Phase 5 (Wave D), Phase 6 (quality/loop/compact), and Phase 7 (domain completion) multiply the above value but assume the spine is wired.

---

## 5. Token budget — measured targets

Every phase's PR must paste these counters into `## Evidence`:

| Metric | Baseline (current) | Target | Measured by |
|---|---|---|---|
| `tools/list` payload (cold) | ~38 KB | < 4 KB | `tests/smoke/test_boot_budget.py` (Phase 1) |
| Boot context tokens | ~34 000 | < 500 | same |
| Average `mcp__github__pull_request_read` cost | 40-80 k tokens | ≤ 2.5 KB envelope | manual: 3 sample PRs (Phase 3) |
| Per-tool result max in context | unbounded | ≤ 4 KB → archived | `tests/smoke/test_archive_threshold.py` (Phase 2) |
| Doc inlining (specs + lessons + overrides) | ≥ 200 KB summed | 0 by default; triad + on-demand | `tests/smoke/test_path_b_defers.py` (Phase 4) |
| Cross-domain query (e.g. `spec → spec`) | 22 spec reads | 1 Cypher MATCH | `tests/smoke/test_graph_queries.py` (Phase 5) |

A phase is **not done** until its row(s) are evidence-backed in the merging PR. This replaces the soft "Done When:" checklists with hard counters.

---

## 6. The Jules-orchestrated implementation loop

See `Plan/JULES-REVIEW-LOOP.md` for the full mechanics. The summary:

```
For each phase:
  1. Read existing sub-spec(s); update `affects:` + `done_when:` if drift since v1
  2. Fanout: dispatch 1 Jules session per spec (parallel, capped 60 in-flight)
  3. Watch: poll jules_status_all every 3 minutes via persistent Monitor
  4. On COMPLETED:
       - Verify branch on remote (mcp__github__list_branches)
       - If absent → JULES_PROTOCOL §8-Appendix recovery (probe → API extract → mcp__github__create_branch + create_or_update_file (adds/modifies) + delete_file (deletes/rename-source) + create_pull_request — see JULES-REVIEW-LOOP.md §5 for the exact routing on file_change.op)
       - If present → PR is open against Master
  5. Review loop (the back-and-forth requested in this plan's goal):
       a. Dispatch a Jules-driven review session against the open PR:
            jules_create(prompt = REVIEW_PROMPT_TEMPLATE, source = PR_BASE)
       b. When review COMPLETES, fetch the PR review comments
       c. Triage with the orchestrator:
            - Cosmetic / out-of-scope → resolve thread, no action
            - Substantive → spawn a follow-up Jules session targeting the same branch
              with a focused fix prompt; OR if trivial, fix locally
       d. Iterate until a review session returns < 1 substantive comment
            ("no relevant feedback surfaces")
  6. Merge phase PR(s) via mcp__github__merge_pull_request
  7. Update this overview's "Done" table (§2.1) with the new specs
```

The loop is **idempotent under crashes**: session state lives in `~/.agency-system/sessions.json` (Spec 006's `sessions_state.py`), and the watcher (`lib/watch_jules.py`) resumes from there.

---

## 7. Target file structure (unchanged from v1; reproduced for orientation)

```
the-agency-system/                              ← the plugin
├── .claude-plugin/plugin.json                  ← only file in this dir (per JULES_PROTOCOL §7)
├── .mcp.json                                   ← stdio command, ${CLAUDE_PLUGIN_ROOT}
├── CLAUDE.md / README.md / CHANGELOG.md
├── commands/                                   ← /agency-system:{music,novel,jules,agentic,spec}-* slash facades
├── servers/agency-mcp/
│   ├── run.py / pyproject.toml
│   └── src/agency_mcp/
│       ├── server.py                           ← FastMCP + AnchorAwareCodeMode + StateCache + register_all()
│       ├── handlers/{music,novel,jules,agentic,shared,context,ontology,graph}/
│       ├── state/cache.py + indexers/{music,novel,jules,ncp}_indexer.py
│       ├── lib/{ncp, dramatica, audio_processing, prose_processing, codemode, envelope}/
│       └── codemode/
│           ├── manifest.json                   ← tools eager|deferred|background classification
│           ├── context_manifest.json           ← Path B documents (Phase 4)
│           ├── context_manifest.schema.json
│           └── registry.py / deferred_loader.py
├── skills/{shared,music,novel,jules,agentic}/  ← ~140 skills total, auto-namespaced
├── hooks/
│   ├── hooks.json                              ← PostToolUse + PreToolUse + UserPromptSubmit + PreCompact
│   ├── contextignore_hook.py                   ← Phase 2
│   ├── structure_map_hook.py                   ← Phase 2
│   ├── read_cache_hook.py                      ← Phase 2
│   ├── bash_compress_hook.py                   ← Phase 2
│   ├── archive_hook.py                         ← Phase 2
│   ├── quality_score_hook.py                   ← Phase 6
│   ├── loop_detect_hook.py                     ← Phase 6
│   ├── compaction_checkpoint_hook.py           ← Phase 6
│   ├── graph_ingest_hook.py                    ← Phase 5
│   └── validate_{track,chapter}.py + check_version_sync.py  ← Phase 0 (kept)
├── reference/                                  ← craft guides + ontology + ncp + dramatica primers
├── templates/                                  ← album/track + work/chapter/scene/ncp
├── migrations/                                 ← music/0.40..0.91 + agency/1.0.0
├── tools/                                      ← CLI utilities (researcher/, jules-patch-extract.py, fm/, check-*)
├── state/schema/                               ← state.schema.json + ncp.schema.json + migrators + ontology
├── config/agency-system.config.template.yaml
├── docs/architecture/ + domain/{music,novel,jules,agentic}.md
├── tests/{unit, integration, smoke}/
├── bin/                                        ← jules-bulk + jules-dev-install + agency-* helpers (re-homed from jules-plugin/ in Phase 0)
├── artists/                                    ← KEEP music content
├── novels/                                     ← NEW novel content `{author}/works/{genre}/{slug}/`
├── audio/ documents/ genres/ overrides/ journals/   ← KEEP
└── Plan/                                       ← THIS folder
```

State on disk:

```
~/.agency-system/cache/state.json       { music:{}, novel:{}, jules:{}, agentic:{}, _version:"1.0.0" }
~/.agency-system/cache/manifest.json    Path B document manifest (Phase 4)
~/.agency-system/cache/graph.sqlite     Wave D ontology graph (Phase 5)
~/.agency-system/cache/sessions.json    Jules session registry
~/.agency-system/config.yaml
```

---

## 8. Phase 0 — Foundation cleanup (executable now)

Phase 0 is the only phase this overview implements directly (the rest are dispatched via Jules per `JULES-REVIEW-LOOP.md`). It is also the first PR review-cycle the orchestrator drives to demonstrate the workflow.

**Files this phase touches:**

- DELETE: `jules-plugin/` (entire subdir)
- CREATE: `bin/jules-bulk`, `bin/jules-dev-install` (moves from `jules-plugin/bin/`)
- CREATE: `tests/jules/test_*.py` (moves from `jules-plugin/tests/`)
- CREATE: `tools/researcher/` (moves from `jules-plugin/tools/researcher/`)
- MODIFY: `CLAUDE.md` (drop the "Jules orchestration plugin" section's `--plugin-dir ./jules-plugin` install path)
- MODIFY: `Plan/000-overview.md` (this file — also marks 020 done)
- CREATE: `Plan/JULES-REVIEW-LOOP.md` (the orchestration spec)

**Phase 0 tasks:**

- [ ] **Task 0.1** — Sub-spec audit (this overview) lands as PR #1 against `Master`. Jules-review-loop runs against PR #1 to validate the plan before any code moves.
- [ ] **Task 0.2** — Phase 0 implementation PR (`Master ← phase-0-cleanup`):
  - Move `jules-plugin/bin/*` → `bin/`; chmod +x preserved.
  - Move `jules-plugin/tools/researcher/` → `tools/researcher/`.
  - Move `jules-plugin/tests/*` → `tests/jules/` (rename to avoid collision with handler tests).
  - Update `skills/agentic/jules-orchestrator-discipline/SKILL.md:131` to reference `skills/jules/references/combined_watcher.py` (already present at the new home via Spec 007) instead of the soon-to-be-deleted `jules-plugin/` path.
  - `rm -rf jules-plugin/`.
  - Update `CLAUDE.md` install instructions.
  - Smoke test: `python -c "from agency_mcp.server import create_mcp; print(len(create_mcp().tools))"` returns same count as before deletion (the Jules tools live in `handlers/jules/` already).
  - `tests/smoke/test_no_jules_plugin.py` asserts `jules-plugin/` is absent AND `grep -rln 'jules-plugin/' skills/ commands/ hooks/ docs/ CLAUDE.md` returns no matches.
- [ ] **Task 0.3** — `Plan/000-overview.md` updates §2.1 to add 020 as **PARTIAL** Done (jules-plugin cleanup only) with PR# evidence. Spec 020's full `Done When:` (per `Plan/020-bitwize-deprecation-and-docs/spec.md`) also requires: README/domain docs refresh, CHANGELOG entry, plugin `version` bump to `1.0.0`, and `tests/smoke/test_doctrine_and_version.py`. Those remaining items move to **Phase 0b — Spec 020 finish** (sequenced AFTER Phase 1 anchor-triad lands so the version bump aligns with the first observable token-budget win), tracked separately to avoid silently dropping the unified-plugin doctrine work.
- [ ] **Task 0.4** — Run JULES-REVIEW-LOOP §3 against Phase 0 PR — single Jules review session, iterate until clean, merge.

Phase 0 is also the smoke test for the entire orchestration mechanism. If the review-loop doesn't work on a 4-task cleanup PR, fix the loop before attempting Phase 1.

---

## 9. Phase 1-8 dispatch matrices

For each phase below: `Specs` lists the sub-spec directories Jules will work from; `Parallel-safe` lists which specs can be dispatched simultaneously (no file-overlap); `Sequential` lists ordering constraints.

### Phase 1 — Anchor triad + envelope + TOON

- **Specs:** `Plan/104-tool-search-anchor-triad/`, `Plan/107-cache-breakpoint-ordering/`, `Plan/130-shared-toolresult-envelope/`, `Plan/131-manifest-coverage-lint/`, `Plan/105-toon-serializer/`
- **Parallel-safe:** 130 + 131 + 105 (envelope, lint, and TOON middleware touch different files); then 104 (uses envelope); 107 must land after 104 (reorders registration around the triad).
- **Token win:** boot context 34k → <500 + 40-60% on list-shape returns via TOON middleware (gates on homogeneous list[dict] with len≥3).
- **PR strategy:** 5 PRs, dispatched as one fanout. 130 + 131 + 105 open first; 104 opens after either of 130/131 merges; 107 opens last.
- **Smoke test:** `tests/smoke/test_boot_budget.py` (Spec 131 ships it; runs in CI); `tests/smoke/test_toon_gate.py` (Spec 105).
- **Cross-PR coordination (added 2026-05-18 mid-loop):** the smoke tests above need an in-process harness that boots `create_mcp()` via FastMCP's in-memory transport — separate from any single Spec 131/105 PR. **PR #115** (branch `claude/fix-pr-merge-issues-sn1CS`) is the working reference point for that harness. Two layers are scoped IN Phase 1 alongside it:
  - **L1 — In-process harness module**: `tests/_harness/` + `conftest.py` exposing `mcp_instance`, `call_tool(name, **kwargs)`, `load_skill(path)`, `dispatch_skill(name)` fixtures. Substrate for Spec 131 and Spec 105 smoke tests.
  - **L2 — Subprocess probe**: `tests/smoke/test_nested_claude.py` spawning `claude --bare --plugin-dir <repo> -p ...` to assert end-to-end boot. Replaces the manifest-only `claude plugin validate` check (per the Codex P1 critique on PR #115).
  - **L3 — Sidecar daemon for non-Claude-Code harnesses** = Spec 023 stays in Phase 8; unchanged.
  - Coordination protocol: Jules/Codex/Claude sessions touching Phase 1 smoke tests in the next 24h MUST rebase onto PR #115's branch rather than authoring a parallel harness; the in-flight design doc is at `docs/superpowers/specs/2026-05-18-harness-in-harness-design.md`.

### Phase 2 — Hook chain

- **Specs:** 121 (contextignore), 115 (structure-map), 114 (read-cache-delta), 116 (bash-compress), 117 (archive)
- **Shared file:** all five specs need to register an entry in `hooks/hooks.json` in the canonical chain order from §3.2. Concurrent edits race; parallel dispatch is unsafe.
- **Strategy: sequential dispatch (one Jules session at a time).** Order: **114 → 121 → 115 → 116 → 117**. Note: this dispatch order differs from the runtime *chain* order (§3.2: `contextignore (121) → structure-map (115) → read-cache-delta (114) → …`). Why: `Plan/121-contextignore-hardblock/spec.md` and `Plan/115-structure-map-ast/spec.md` both declare a `deps:` on Spec 114 (the read-cache-delta primitives both hooks build on). Dispatch order respects dependency frontmatter; runtime order is what `hooks/hooks.json` encodes. Each session writes its own `hooks/*_hook.py` AND appends/reorders its `hooks.json` entry to match the canonical chain. The next session is only dispatched after the prior has merged; new session's `starting_branch=Master` so it sees the prior merge.
- This obeys the JULES-REVIEW-LOOP.md §1 rule that "the orchestrator never edits Jules's branches itself except via the recovery path" — Jules itself owns every `hooks.json` edit. The trade-off is wall-clock time (5 serial review cycles instead of 1 parallel cycle); the win is contract-purity and no race.
- **Token win:** 20-30% of session input + 4 KB cap on any single result.
- **PR strategy:** 5 sequential PRs (one fanout entry at a time, gated on prior merge).

### Phase 3 — GitHub sink wrapper

- **Specs:** 106 (github-mcp-summary-wrappers)
- **Token win:** PR/issue reads collapse from 40-80k → ≤ 2.5 KB.
- **Implementation note:** uses subagent dispatch pattern from `superpowers:dispatching-parallel-agents`. The wrapper tool spawns an ephemeral subagent with `mcp__github__pull_request_read` access; distils to a typed Pydantic proto; the main session never sees the raw body.
- **PR strategy:** 1 PR.

### Phase 4 — Context Mode (Path B)

- **Specs:** 111 (manifest), 108-stub (supersession marker). **Spec 112 (anchor-triad) is already merged** via PR #104 (commit `85a8e51`); **Spec 113 (cache + subscriptions) is already merged** via PR #113 (commit `883eb45`); only the manifest remains.
- **Sequential:** 111 first; 108-stub in parallel.
- **Token win:** 200 k+ deferred (anchor triad + cache already shipping; manifest closes the loop).
- **PR strategy:** 2 PRs as one fanout. Audit: re-verify post-merge that `context_search` / `context_describe` / `context_read` actually consult a *populated* manifest — if 113 was merged before 111, the cache may be subscribing to an empty index.

### Phase 5 — Ontology + Graph (Wave D)

- **Specs:** 122 (centralized-ontology), 123 (agency-tooling-codemode), 124 (graphqlite-codemode), 135 (spec-test-anchor-traceability)
- **Sequential:** 122 → 123 → 124 (schema → enforcement → graph). 135 in parallel.
- **Token win:** cross-domain queries collapse to single Cypher MATCH.
- **PR strategy:** 4 PRs over ~3 fanouts.

### Phase 6 — Quality / loop / compaction

- **Specs:** 100 (session-log-mcp), 118 (quality-score), 119 (loop-detect), 120 (compaction-checkpoints)
- **Sequential:** 100 first (session-log is the data store the other three append to). 118 / 119 / 120 parallel.
- **PR strategy:** 4 PRs over 2 fanouts.

### Phase 7 — Domain handler completion

- **Specs:** 015 (novel skills catalogue), 016 (agentic handlers + skills), 018 (overrides migration), 021 (novel prompt-builders). **Spec 014 (novel gates + revision) already merged** via PR #108 (commit `5954832`).
- **Parallel-safe:** all four (different handler subdirs).
- **PR strategy:** 4 PRs as one fanout.

### Phase 8 — Operational hardening

- **Specs:** 102 (pr-rebase-policy), 132 (skill-tool-hooks), 133 (skill-subagent-pressure-tests), 134 (plan-adr-convention), 136 (agents-yaml-role-manifest), 137 (watcher-sdk-composability), 138 (frustration-log-protocol), 139 (evidence-snapshot-helper), 023 (harness-in-harness), 099-full (jules-orchestration-improvements remainder)
- **Parallel-safe:** all (orthogonal subsystems).
- **PR strategy:** up to 10 PRs as one fanout — this phase is where the 60-session quota is most relevant.

---

## 10. Done when (whole plan)

This master plan is **complete** when:

1. All eight phases have at least one merged PR each, and each phase's smoke test row (§5) passes in CI.
2. `tools/list` payload measured at < 4 KB on a fresh boot — captured in CI gate.
3. `jules-plugin/` does not exist; `Plan/_lessons-learned/` has at least one new lesson per phase (the reflexion contract).
4. The unified plugin loads via `/plugin install agency-system@netzkontrast` (marketplace path verified by Spec 022, already merged via PR #73).
5. `Plan/000-overview.md` §2.1 lists every spec from §2.2 and §2.3 as Done with a merged PR number, OR explicitly marked superseded with a pointer.

---

## 11. Pointers

- **JULES_PROTOCOL.md** — the contract for any Jules session (4 gates, recovery, anti-patterns).
- **JULES-REVIEW-LOOP.md** *(new in this plan)* — the orchestration loop mechanics (dispatch, watch, review, iterate).
- **SOURCES.md** — vendor source repos referenced by specs.
- **_lessons-learned/** — reflexion log; every phase appends one entry.
- **_research/_synthesis-122-123-124.md** — the Wave D braid (already authored).
- **docs/superpowers/specs/2026-05-16-jules-suite-refactor-design.md** — the predecessor spec; still useful for Phase 0/1 historical context.
