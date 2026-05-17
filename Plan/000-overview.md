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

## 3. Spec list (21 specs, ~30 Jules sessions, 3 waves)

| ID | Slug | Wave | Domain | Deps | Sessions |
|---|---|---|---|---|---|
| 001 | scaffold-plugin-skeleton | A | scaffold | — | 1 |
| 002 | manifest-and-marketplace | A | scaffold | 001 | 1 |
| 003 | unified-statecache-port | A | cross | 001 | 2 |
| 004 | music-handlers-port | A | music | 003 | 2 |
| 005 | music-skills-port | A | music | 002, 004 | 1 |
| 006 | jules-handlers-port | A | jules | 003 | 1 |
| 007 | jules-skills-and-commands-port | A | jules | 002, 006 | 1 |
| 008 | codemode-registry | A | cross | 003, 004 | 1 |
| 009 | shared-handlers | B | cross | 003 | 1 |
| 010 | novel-on-disk-layout | B | novel | 002 | 1 |
| 011 | novel-handlers-core | B | novel | 003, 009, 010 | 2 |
| 012 | dramatica-and-ncp-libs | B | novel | 010 | 2 |
| 013 | novel-handlers-structural | B | novel | 011, 012 | 2 |
| 014 | novel-gates-and-revision | B | novel | 013 | 1 |
| 015 | novel-skills-catalogue | B | novel | 005, 014 | 2 |
| 016 | agentic-handlers-and-skills | C | agentic | 009 | 2 |
| 017 | hooks-port-and-extend | C | cross | 004, 013 | 1 |
| 018 | overrides-and-config-migration | C | migration | 015 | 1 |
| 019 | state-migration-from-bitwize | C | migration | 003 | 1 |
| 020 | bitwize-deprecation-and-docs | C | cross | 005, 007, 015, 016, 019 | 1 |
| 021 | novel-prompt-builder-family | B | novel | 013, 015 | 2 |

**Critical path** (longest dependency chain): 001 → 003 → 011 → 013 → 014 → 015 → 020 ≈ 11 sessions. Spec 021 runs in parallel with 014–015 once 013 is done.

**Wave A** (specs 001–008): at end, unified plugin boots, music side serves 100% bitwize parity, jules side serves 100% jules-plugin parity, Code Mode registry in place. **Bitwize-music plugin can be uninstalled.**

**Wave B** (specs 009–015, 021): novel domain ships. User can run `/agency-system:novel-work-conceptualizer`, write chapters, validate against NCP, pass the 6-gate.

**Wave C** (specs 016–020): agentic surface live, overrides merged, state migration executed, `jules-plugin/` removed, bitwize marked deprecated.

## 4. Dependency DAG

```
              001 ───┬── 002 ──┬── 005 ──┐
                     │         │         │
                     └── 003 ──┼── 004 ──┤
                               │         │
                               ├── 006 ──┼── 007 ──┐
                               │         │         │
                               └── 008   │         │
                                         │         │
   010 ── 012 ──┐                        │         │
    │           │                        │         │
    ├── 011 ────┤                        │         │
    │           │           009 ─────────┼─────────┤
    │           │                        │         │
    └── 013 ────┼── 014 ── 015 ──────────┤         │
                │           │            │         │
                ├── 021     │            │         │
                │           │            │         │
                017         │            │         │
                            │            │         │
                            └── 018 ─────┤         │
                                         │         │
                            019 ─────────┴── 020 ──┘
```

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
