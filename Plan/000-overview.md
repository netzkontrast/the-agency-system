# Plan 000 — Agency System Plugin Refactor (Master Overview)

> **Status:** approved 2026-05-17  ·  **Owner:** human + Jules (fan-out)
> **Branch:** `claude/agency-plugin-refactor-PgMQ4`
> **Goal:** collapse `jules-plugin`, `bitwize-music`, and the agency-repo skill corpus into one token-efficient Claude Code plugin where `the-agency-system` repo *is* the plugin. Music absorbs bitwize; novel side is built spirit-isomorphic to music; agentic/spec-driven work and Jules orchestration are first-class.

This document is the **map**. Each spec is a one-Jules-session task; specs depend on each other per the DAG below. Conventions and disciplines live in `Plan/JULES_PROTOCOL.md`. Source URLs live in `Plan/SOURCES.md`.

## 1. Target architecture (at a glance)

```
the-agency-system/                              ← the plugin
├── .claude-plugin/plugin.json                  ← only file in this dir
├── .mcp.json                                   ← stdio command, ${CLAUDE_PLUGIN_ROOT}
├── CLAUDE.md / README.md / CHANGELOG.md
├── commands/                                   ← /agency-system:{music,novel,jules,agentic,spec}-* slash facades
├── servers/agency-mcp/                         ← FastMCP server (servers/ convention from bitwize)
│   ├── run.py / pyproject.toml
│   └── src/agency_mcp/
│       ├── server.py                           ← FastMCP("agency-system") + CodeMode + StateCache + register_all()
│       ├── handlers/
│       │   ├── music/      (~67 tools — port of bitwize handlers verbatim)
│       │   ├── novel/      (~73 tools — 63 domain + 10 prompt-builders)
│       │   ├── jules/      (~12 tools — ported from jules-plugin)
│       │   ├── agentic/    (~32 tools — spec/plans/workflows/research/ralph/confidence)
│       │   └── shared/     (search, skills, reference, config, session — cross-domain)
│       ├── state/cache.py + indexers/{music,novel,jules,ncp}_indexer.py
│       ├── lib/{ncp, dramatica, audio_processing, prose_processing, codemode}/
│       └── codemode/{registry.py, deferred_loader.py, manifest.json}
├── skills/{shared,music,novel,jules,agentic}/  ← ~140 skills total
├── hooks/hooks.json                            ← PostToolUse validators
├── reference/                                  ← craft guides + ontology + ncp + dramatica primers
├── templates/                                  ← album/track + work/chapter/scene/ncp
├── migrations/                                 ← music/0.40..0.91 + agency/1.0.0
├── tools/                                      ← CLI utilities
├── state/schema/                               ← state.schema.json + ncp.schema.json + migrators
├── config/agency-system.config.template.yaml
├── docs/architecture/ + domain/{music,novel,jules,agentic}.md
├── tests/{unit, integration, smoke}/
├── bin/                                        ← jules-bulk + agency-* helpers
├── artists/                                    ← KEEP music content
├── novels/                                     ← NEW novel content `{author}/works/{genre}/{slug}/`
├── audio/ documents/ genres/ overrides/ journals/   ← KEEP
└── Plan/                                       ← THIS folder
```

State on disk (single unified JSON, namespaced top-level keys):
```
~/.agency-system/cache/state.json    { music:{}, novel:{}, jules:{}, agentic:{}, _version:"1.0.0" }
~/.agency-system/config.yaml         (replaces ~/.bitwize-music/config.yaml at cutover)
~/.agency-system/agentic/{plans,workflows,specs,research,ralph,cache,locks}/
```

## 2. Core conventions (must be cited in every spec's Approach)

### 2.1 Code Mode & MCP

1. **Tool naming**: snake_case `<domain>_<verb>_<object>` (`music_list_albums`, `novel_get_chapter`). NOT dot-notation. Use FastMCP `tags={"domain:music"}` for grouping.
2. **FastMCP construction**: `FastMCP("agency-system", dereference_schemas=False)`. Shared enums in `lib/codemode/enums.py`. Tool docstrings ≤120 chars (one-line purpose, imperative mood, mention sibling tools with backticks).
3. **Code Mode discovery**: rely on built-in `search` / `get_schema` / `execute`. **No custom `list_tools` or `search_tools`** — single exception: `plugin_help(domain: str) -> Markdown` cheat-sheet.
4. **Schema deferral**: ~4 anchor tools per domain registered eagerly; bulk with `defer_schema=True`. Code Mode drops boot context ~34k → ~315 tokens.
5. **Tool classification** in `codemode/manifest.json`: `eager` | `deferred` | `background` (long-running tools register a `*_status` poll companion).
6. **Response shape**: `list_*` returns `{id, name, summary}` capped 20 + opaque cursor; large blobs as `{ref_id, length, preview}` with a `read_ref` resolver. Opt-in `full=true` flag.
7. **Stateful tools**: MUST accept `dry_run: bool = False` → `{would_apply, diff, warnings}`.
8. **Orchestration tools**: MUST accept `return_plan: bool = False` → `OrchestrationPlan` of steps.
9. **Shared `ToolResult` envelope**: `{ok, data, warnings, artefacts_written, next_suggested_tools}`.
10. **StateCache**: ONE instance per FastMCP lifespan; `asyncio.Lock` for writes; mtime-staleness on `state.json`. Not process-global.
11. **Hooks**: state invalidation MUST be synchronous inside the tool; hooks only for non-correctness side effects.

### 2.2 Skill best practices (from `skill-creator`)

L1 Vault Core frontmatter (mandatory): `type: spec`, `status`, `slug`, `summary` (≤120 chars), `created`, `updated`.

L2 `skill_*` namespace (mandatory): `skill_kind` (9-value enum: `domain|tool|orchestrator|meta|discipline|workflow|persona|analysis|agent-template`), `skill_target_agents`, `skill_references_skills`, `skill_references_research`, `skill_references_prompts`, `skill_bootstrap_required`.

Cross-refs in frontmatter only; `:embed` suffix = composition vs bare slug = invocation. Five mandatory body sections: `## What`, `## When to use`, `## How to use`, `## References`, `## Compatibility`. Linter enforces resolution + reciprocity — don't author `skill_referenced_by`.

### 2.3 Claude Code plugin specifics

- `.claude-plugin/plugin.json` is the only file in `.claude-plugin/`. Everything else at repo root.
- Skills auto-namespace to `/agency-system:<skill-name>`. Sub-folders under `skills/` (`music/`, `novel/`) are organisational only.
- `.mcp.json` uses `${CLAUDE_PLUGIN_ROOT}` for paths — never absolute.
- Hooks (`hooks/hooks.json`) are synchronous in current Claude Code.
- FastMCP ≥3.1.0 for Code Mode; `CodeMode` import wrapped in `try/except ImportError` for graceful fallback (jules-plugin's pattern).

Read `Plan/JULES_PROTOCOL.md` §7 for the full plugin convention block.

## 3. Spec list (46 specs as of 2026-05-18 — 15 done / 31 ready)

### Wave A — Scaffold + Music + Jules + Code Mode (DONE)

| ID | Slug | Domain | Deps | Status | Sessions |
|---|---|---|---|---|---|
| 001 | scaffold-plugin-skeleton | scaffold | — | ✅ done | 1 |
| 002 | manifest-and-marketplace | scaffold | 001 | ✅ done | 1 |
| 003 | unified-statecache-port | cross | 001 | ✅ done | 2 |
| 004 | music-handlers-port | music | 003, 004a | ✅ done | 2 |
| 004a | music-lib-port (subtree) | music | 003 | ✅ done | 1 |
| 005 | music-skills-port | music | 002, 004 | ✅ done | 1 |
| 006 | jules-handlers-port | jules | 003 | ✅ done | 1 |
| 006a | jules-handlers hardening (implicit) | jules | 006 | ✅ done | 1 |
| 007 | jules-skills-and-commands-port | jules | 002, 006 | ✅ done | 1 |
| 008 | codemode-registry | cross | 003, 004, 006 | ✅ done | 1 |
| 009 | shared-handlers | cross | 003 | ✅ done | 1 |
| 010 | novel-on-disk-layout | novel | 002 | ✅ done | 1 |
| 011 | novel-handlers-core (Wave B foundation) | novel | 003, 009, 010 | ✅ done | 2 |
| 012 | dramatica-and-ncp-libs | novel | 010 | ✅ done | 2 |
| 013 | novel-handlers-structural | novel | 011, 012 | ✅ done | 2 |
| 019 | state-migration-from-bitwize | migration | 003 | ✅ done | 1 |

### Wave A completion — enabler

| ID | Slug | Domain | Deps | Status | Sessions |
|---|---|---|---|---|---|
| **022** | **dev-mode-install** ⭐ first | cross | 002, 005, 007, 008 | ready | 1 |

### Wave B remaining — novel completion

| ID | Slug | Domain | Deps | Status | Sessions |
|---|---|---|---|---|---|
| 011a | novel-handlers-core hardening | novel | 011 | ready | 1 |
| 014 | novel-gates-and-revision | novel | 011, 012, 013 | ready | 1 |
| 015 | novel-skills-catalogue | novel | 005, 011, 014 | ready | 2 |
| 021 | novel-prompt-builder-family | novel | 011, 012, 013, 015 | ready | 2 |

### Wave C — agentic + cutover

| ID | Slug | Domain | Deps | Status | Sessions |
|---|---|---|---|---|---|
| 016 | agentic-handlers-and-skills | agentic | 002, 003, 008, 009 | ready | 2 |
| 017 | hooks-port-and-extend | cross | 004, 012, 013 | ready | 1 |
| 018 | overrides-and-config-migration | migration | 009, 015 | ready | 1 |
| 020 | bitwize-deprecation-and-docs | cross | 005, 007, 015, 016, 017, 018, 019 | ready | 1 |

### Wave A hardening

| ID | Slug | Domain | Deps | Status | Sessions |
|---|---|---|---|---|---|
| 098 | wave-a-hardening (Codex P1 cleanup) | cross | 002, 003, 004a, 019 | ready | 1 |

### Operational specs (from lessons + research)

| ID | Slug | Domain | Deps | Status | Sessions |
|---|---|---|---|---|---|
| 099 | jules-orchestration-improvements (meta) | agentic | — | ready | 1 |
| 100 | session-log-mcp (sidequest) | agentic | — | ready | 2 |
| 101 | jules-mcp-tool-additions | agentic | 006 | ready | 1 |
| 102 | pr-rebase-policy | cross | — | ready | 1 |

### Token-efficiency

| ID | Slug | Domain | Deps | Status | Sessions |
|---|---|---|---|---|---|
| 103 | view-fields-projection | cross | 008 | ready | 2 |
| 104 | tool-search-anchor-triad | cross | 008 | ready | 2 |
| 105 | toon-serializer | cross | 008 | ready | 1 |
| 106 | github-mcp-summary-wrappers | cross | 008 | ready | 2 |
| 107 | cache-breakpoint-ordering | cross | 008 | ready | 1 |

### Context Mode (PICK ONE PATH — mutually exclusive)

| ID | Slug | Domain | Deps | Status | Sessions |
|---|---|---|---|---|---|
| 108 | context-mode-integration (adopt mksglu) | cross | 002, 008, 100 | ready | 2 |
| 111 | context-mode-manifest (build alt) | cross | 008, 104 | ready | 2 |
| 112 | context-anchor-triad (build alt) | cross | 008, 104, 111 | ready | 2 |
| 113 | context-cache-and-subscriptions (build alt) | cross | 008, 104, 111, 112 | ready | 2 |

### Wave D — Path B content layer (extends 111-113)

| ID | Slug | Domain | Deps | Status | Sessions |
|---|---|---|---|---|---|
| 122 | centralized-ontology | cross | 111, 112, 113 | ready | 1 |
| 123 | agency-tooling-codemode | cross | 008, 111, 122 | ready | 2 |
| 124 | graphqlite-codemode | cross | 008, 100, 111, 112, 113, 122 | ready | 3 |

See `Plan/_research/_synthesis-122-123-124.md` for the interlocking design (data shape → machinery → graph layer). Three Jules research outputs landed on Master via PRs #82 / #84 / #86 with full findings docs under `Plan/_research/<slug>/`.

### Token-optimizer hook layer (orthogonal)

| ID | Slug | Domain | Deps | Status | Sessions |
|---|---|---|---|---|---|
| 114 | read-cache-delta-mode | cross | — | ready | 1 |
| 115 | structure-map-ast | cross | — | ready | 1 |
| 116 | bash-output-compression | cross | — | ready | 1 |
| 117 | tool-result-archive | cross | 009 | ready | 1 |
| 118 | quality-score-telemetry | cross | 100 | ready | 1 |
| 119 | loop-detection | cross | — | ready | 1 |
| 120 | smart-compaction-checkpoints | cross | 100 | ready | 2 |
| 121 | contextignore-hardblock | cross | — | ready | 1 |

**Wave A — DONE** (16 specs incl. 006a): unified plugin boots, 113+ tools registered, music side 100% bitwize parity, jules side 100% jules-plugin parity, Code Mode registry in place (boot context 210 tokens), novel foundation + structural layer in. **Bitwize-music plugin can be uninstalled once Spec 020 cuts over.**

**Wave A completion**: Spec 022 dev-mode-install (next-session enabler).

**Wave B remaining** (4 specs): novel domain shipping. User can run `/agency-system:novel-work-conceptualizer`, write chapters, validate against NCP, pass the 6-gate.

**Wave C** (4 specs): agentic surface live (32 tools per Spec 016), overrides merged, hooks ported, `jules-plugin/` removed, bitwize marked deprecated.

**Cross-cutting backlog** (24 specs): hardening + operational + token-efficiency + Context Mode + token-optimizer. Most depend only on 008 (✅ done) so they ship in parallel waves.

**Critical path to v1.0 cutover**: 022 → 014 → 015 → 020 ≈ **5 sessions** (down from original 11 because most of the chain is already on Master). Everything else compresses into parallel fan-out.

## 4. Dependency DAG (updated 2026-05-18)

✅ = merged on Master · ⭐ = next-session priority · ⏳ = ready, awaiting dispatch

### Critical path to v1.0 cutover (5 sessions)

```
        ┌── 022 ⭐ (enabler)
        │
✅ Wave A
        │
        ├── 014 ⏳ ── 015 ⏳ ── 020 ⏳ (v1.0)
        │              │
        │              └── 021 ⏳ (parallel)
        │
        ├── 016 ⏳ ──────────────┘
        │
        ├── 017 ⏳ ──────────────┘
        │
        ├── 018 ⏳ ──────────────┘
        │
        └── 011a ⏳ (parallel hardening, no downstream blocker)
```

### Cross-cutting (parallelizable from session start)

```
Wave A hardening   098 ⏳ (Codex P1 cleanup — orthogonal)

Token-efficiency   103 ⏳ ─┐
                   104 ⏳ ─┤
                   105 ⏳ ─┤  all depend only on 008 ✅
                   106 ⏳ ─┤
                   107 ⏳ ─┘

Operational        099 ⏳ (meta) · 100 ⏳ (session-log-mcp) ·
                   101 ⏳ (jules-mcp additions) · 102 ⏳ (rebase policy)

Context Mode       108 ⏳ (adopt mksglu plugin)        ← PICK
                          OR                             ONE
                   111 ⏳ → 112 ⏳ → 113 ⏳ (build)    ← PATH

Token-optimizer    114 ⏳ · 115 ⏳ · 116 ⏳ · 117 ⏳ ·
hook layer         118 ⏳ · 119 ⏳ · 120 ⏳ · 121 ⏳
                   (all near-orthogonal; 117 needs 009 ✅,
                   118+120 want 100 ⏳ first)
```

### Recommended dispatch order

**Session 1 (next session):**
1. Dispatch **022** alone (enabler — gates everything; 1 Jules session)
2. While waiting, invoke `sc-spec-panel` against the 31 ready specs
3. Once 022 lands, parallel-dispatch: **011a + 014 + 098 + 103** (4 sessions)

**Session 2 (post-merge of 011a/014/098/103):**
- Dispatch **015 + 016 + 017 + 018 + 106** (5 sessions parallel)
- Pick Context Mode path (108 vs 111-chain); dispatch first step
- Decide on token-optimizer first 1-2 picks (e.g. 117 archive guardrail first)

**Session 3 (cutover):**
- Dispatch **020 + 021** (final Wave-B + cutover)
- Continue token-eff backlog

After Session 3: v1.0 plugin shipped; remaining specs are continuous-improvement.

## 5. Workflow trace (end-to-end coherence proof)

See `Plan/000-overview.md` is the place; full traces live in the plan file under `Coherence reflection`. Three workflows are proven coherent:

- **Music**: `/agency-system:music-lyric-writer` → music tools → hooks/validate_track.py → StateCache refresh.
- **Novel**: `/agency-system:novel-work-conceptualizer` → novel_create_work → novel_ncp_compile → novel_run_pre_drafting_gates (6 BLOCKING) → `novel-scene-prompt-builder` composes character + world + throughline + bridge prompt-builders → chapter-writer drafts → validate_chapter.py fires.
- **Jules / spec-driven**: Jules opens spec.md → reads 80-word sticker → `Plan/JULES_PROTOCOL.md` → Gate 1 (Confidence) → clone source → Gate 2 (TDD) → Gate 3 (Evidence in PR) → Gate 4 (Self-Review).

## 6. Research briefs (embedded in spec `references/` folders)

| Brief | Embedded in spec |
|---|---|
| Novel-craft parity table (30 music↔novel role mappings, 12 craft-research citations) | 015 |
| Dramatica decidability matrix (11 decidable + 2 judgement Dramatica checks) | 012, 013 |
| FastMCP / Code Mode best practices (token budget, response shapes, lazy loading) | 008 (also cited by many) |
| Agentic-orchestration tool catalog (32 tools, ToolResult envelope) | 016 |
| Novel prompt-builder methods (10 builders, 12-source method survey) | 021 |
| Jules protocol (this doc) | `Plan/JULES_PROTOCOL.md` (master) |
| Claude Code plugin best practices | this overview §2.3 + spec 001 |
| Source-repo URLs | `Plan/SOURCES.md` |

## 7. Reading order for Jules

1. `Plan/JULES_PROTOCOL.md` — non-negotiable
2. `Plan/SOURCES.md` — clone commands for your spec
3. `Plan/000-overview.md` — this doc (§2 conventions especially)
4. Your assigned spec's `Plan/NNN-<slug>/spec.md`
5. Any embedded brief in `Plan/NNN-<slug>/references/`
6. Anthropic docs cited in `Plan/SOURCES.md` §"Reference / framework docs"
