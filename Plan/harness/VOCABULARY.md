---
slug: harness-vocabulary
status: ready
owner: claude
depends_on: [harness/design]
related: [000-overview, harness/restructure]
phase: cross-cutting
affects:
  - Plan/harness/VOCABULARY.md
domain: agentic
wave: B
spec_kind: reference
---

> **Status:** canonical naming reference for `Plan/harness/design.md`.
> All phase READMEs, acceptance features, sub-specs, and the master overview
> are expected to use these terms verbatim. When two specs disagree, this
> file wins and the diverging spec must be brought into line.

# Harness Vocabulary — canonical naming & cross-reference index

This is the single-source-of-truth lexicon for the unified `agency-system`
plugin. The harness design (`Plan/harness/design.md`) introduces the three
architectural pillars (three layers, four-verb contract, five domains plus
the agentic skill-only domain); this file extracts the terminology so every
downstream document can reference it without re-deriving the canon.

If a phase document uses a term that does not appear here, either the term
is wrong or this file is incomplete — open a PR against this file rather
than adding ad-hoc vocabulary downstream.

---

## 1. Top-line invariants

The unified plugin has **one** plugin manifest, **one** MCP server, **one**
shared four-verb contract, and **one** token budget. Every phase aligns
against these axes:

| Invariant | Value | Source |
|---|---|---|
| Plugin name (manifest + FastMCP server) | `agency-system` | `.claude-plugin/plugin.json`, `servers/agency-mcp/src/agency_mcp/server.py` (§9 evidence in `harness/design.md`) |
| Factory function | `create_mcp()` | `servers/agency-mcp/src/agency_mcp/server.py:99-106` |
| Boot context budget (cold) | < 500 tokens | `Plan/000-overview.md` §5 |
| `tools/list` cold payload | < 4 KB | `Plan/000-overview.md` §5 |
| Per-tool result max in context | ≤ 4 KB → archived | Phase 2 spec 117 |
| Doc inlining at boot | 0 (on-demand via Context Mode Path B) | Phase 4 spec 111 |
| Sub-spec authoring path | `Plan/<NNN>-<slug>/spec.md` or `Plan/<phase>/<slug>/spec.md` | this file |

---

## 2. The three-layer harness ladder

The harness is a **three-layer ladder** that exposes the same four-verb
contract via three transports at three fidelity tiers. Every phase serves
at least one layer's needs.

| Layer | Audience | Transport | Boot cost | Status |
|---|---|---|---|---|
| **L1 In-process harness** | pytest, Phase 1+ smoke tests, in-session dev iteration | FastMCP in-memory (`tests/_harness/`) | ms | **Shipped** (PR #127, merged onto Master). `tests/_harness/{__init__,mcp,skills}.py` + `tests/conftest.py` present. |
| **L2 Subprocess probe** | CI boot-fidelity backstop | `claude --bare --plugin-dir <repo> --debug plugins -p exit` | ~seconds + small API cost | **Shipped** (PR #127). `tests/smoke/test_nested_claude.py` present. |
| **L3 Sidecar daemon + CLI** | external agents (Jules, Cursor, Codex CLI, Cline, bash-only LLMs), in-session bash dogfooding | FastMCP Streamable HTTP on `127.0.0.1:7777`, fronted by `bin/agency` CLI | ~3-5s cold boot, ~100ms p50 per call | **Planned** — Phase 8 (`bin/agency` + `servers/agency-mcp/src/agency_mcp/lib/devmode/`). MVP scope absorbs Plan/023 items 2-3-5-6-7-8-basic; items 1+4 deferred to `Plan/harness/L3-progressive-disclosure.md`. |

**Cross-layer invariant:** every layer exposes the same four verbs (§3).
A test that passes on L1 must pass on L2 must pass on L3 (modulo subprocess
overhead). The L1↔L3 equivalence test is in `tests/integration/test_devmode_server.py`.

---

## 3. The four-verb contract

The four verbs are the **invariant surface** every layer exposes. The L1
implementation also ships a `load_skill(path)` parsing helper that the
`dispatch_skill` verb composes with internally — `load_skill` is not part
of the four-verb cross-layer contract.

| Verb | L1 (Python in-memory, shipped) | L3 wire (MCP JSON-RPC, planned) | L3 CLI (planned) |
|---|---|---|---|
| `list_tools(mcp)` | `tools` fixture or `tests._harness.list_tools(mcp_instance)` | `tools/list` (filtered server-side by tag) | `agency tool search [--domain X]` |
| `call_tool(mcp, name, params)` | `call_tool` fixture or `tests._harness.call_tool(mcp_instance, name, params)` | `tools/call` | `agency tool execute <name> [--param k=v ...]` |
| `list_skills()` | `tests._harness.list_skills()` — returns `list[Path]` of every `SKILL.md` under `skills/` | meta-tool `agency_skill_list` | `agency skill list [--domain X]` |
| `dispatch_skill(name)` | `dispatch_skill` fixture or `tests._harness.dispatch_skill(name)` — returns `Path \| None` | meta-tool `agency_skill_describe` | `agency skill describe <name>` |

Pytest fixtures exposed in `tests/conftest.py`: `mcp_instance`, `tools`,
`call_tool`, `load_skill`, `dispatch_skill`.

Source: `Plan/harness/design.md` §3.2 (L1), §5.3 (L3 wire + CLI).
Implementation evidence: `tests/_harness/__init__.py` (re-exports);
`tests/_harness/mcp.py:13-40` (in-memory transport); `tests/_harness/skills.py`
(SKILL.md parsing + resolver).

---

## 4. The five domains plus agentic

Every handler-bearing domain has the same five children under
`servers/agency-mcp/src/agency_mcp/handlers/<name>/` today (Harness Path A;
under Harness Path B these would live under `domains/<name>/`):

| Domain | Role | Handler modules (count) | Skills | Note |
|---|---|---|---|---|
| `music` | music projects (albums, tracks, mastering, release) | 17 | 54 in `skills/music/` | flagship domain; richest skill set |
| `novel` | novel projects (works, chapters, scenes, NCP, dramatica) | 13 | 28 planned in Phase 7 spec 015 | Phase 7 completes the skill catalogue |
| `jules` | Jules async-coding orchestration | 6 | 1 + references in `skills/jules/` | low skill surface by design |
| `context` | Context Mode Path B manifest & anchor triad | 2 | 0 (tool-only domain) | manifest schema in Phase 4 |
| `shared` | cross-domain primitives (search, reference, config, session, skills, health) | 6 | 0 (tool-only domain) | also hosts the eager `agency_*` anchor triad |
| `agentic` | meta-domain: skill-only, no handlers | 0 | ~30 skills in `skills/agentic/` | spec/plan/workflow/research/ralph/confidence skills + jules-orchestrator-discipline |

**The "five domains" count refers to handler-bearing domains only.** The
`agentic` domain is the **skill-only sixth domain**. Documents that talk
about "all domains" should explicitly say either "five handler-bearing
domains" or "five handler-bearing domains plus the agentic skill-only
domain", depending on scope.

---

## 5. Naming conventions

| Surface | Convention | Example |
|---|---|---|
| Anchor triad tools (eager) | `agency_tool_<verb>` | `agency_tool_search`, `agency_tool_describe`, `agency_tool_invoke` |
| Cross-domain meta-tools | `agency_<verb>` | `agency_skill_list`, `agency_skill_describe`, `agency_file_get` (Path B vision) |
| Domain tools | `<domain>_<verb>` | `music_find_album`, `novel_create_chapter`, `context_search` |
| FastMCP tag for a tool | `domain:<name>` | `domain:music`, `domain:novel`, `domain:context` |
| SKILL.md name (frontmatter) | bare `<name>`; Claude Code prepends namespace | `lyric-writer`, not `music-lyric-writer` (the latter is the namespaced form) |
| Slash command facade | `/agency-system:<domain>-<verb>` | `/agency-system:music-new-album`, `/agency-system:novel-write-scene` |
| State on disk | `~/.agency-system/cache/<name>.{json,sqlite}` | `state.json`, `manifest.json`, `graph.sqlite`, `sessions.json` |
| Sub-spec directory | `Plan/<NNN>-<slug>/spec.md` or `Plan/<phase>-*/specs/<NNN>-<slug>/spec.md` | `Plan/104-tool-search-anchor-triad/`, `Plan/phase-1-*/specs/104-...` |
| Gherkin anchor tags | `# anchor: <phase-or-spec>.<scenario-slug>` | `# anchor: phase-1.tools-list-payload`, `# anchor: harness.L1.1` |

---

## 6. Path A vs Path B — TWO disambiguated trajectories

The string "Path A/Path B" appears in **two different contexts** in this
codebase. They are **unrelated trajectories** and must always be qualified:

### 6.1 "Context Mode Path A / Path B" (Phase 4 only)

In `Plan/phase-4-context-mode-path-b/` and `Plan/000-overview.md` §3.1, this
refers to two competing approaches for deferring document inlining:

- **Context Mode Path A** (rejected): adopt the third-party `mksglu/context-mode`
  plugin. Spec 108 — superseded.
- **Context Mode Path B** (chosen, partially shipped): native manifest +
  anchor triad + cache. Specs 111 (manifest), 112 (anchor triad — merged
  PR #104), 113 (cache + subscriptions — merged PR #113).

Phase 4 is **"Context Mode Path B"** in full — never abbreviated to just
"Path B" without the "Context Mode" qualifier when both Path-A/B contexts
might be in scope.

### 6.2 "Harness Path A / Path B / Path C" (cross-cutting)

In `Plan/harness/design.md` §11 and `Plan/harness/restructure/spec.md`,
this refers to the trajectory of how much **structural domain restructure**
the codebase undergoes:

- **Harness Path A (current, 9/10 isomorphism)** — minimal source levers:
  L-α (unified `register(mcp)`), L-β (`@domain_tool` decorator), L-γ
  (manifest auto-sync). Ships alongside `Plan/harness/design.md`'s L1+L3
  implementation PR; backward-compat with all current handler trees.
- **Harness Path B (vision, 10/10 isomorphism)** — full restructure into
  `domains/<name>/` behind a `Domain` base class. Status: `vision`. Spec
  at `Plan/harness/restructure/spec.md`. Gates Phase 7+; not scheduled
  until Phase 2-8 surge slows enough that a 2-3 week refactor PR will not
  collide with concurrent Jules dispatches.
- **Harness Path C** — Path A plus a `git mv` of skills under each domain;
  rejected as standalone (Path B does the move anyway).

The active implementation path for the harness design's first tag is
**Harness Path A**. The Path A levers (L-α, L-β, L-γ) land alongside the
L1+L3 implementation PR; the four high-cost levers (L-δ, L-ε, L-ζ, L-η)
ship as named follow-up sub-specs.

### 6.3 Disambiguation rule

When both contexts might be in scope:
- Phase 4 docs say **"Context Mode Path B"** (never bare "Path B").
- Harness docs say **"Harness Path A"** or **"Harness Path B"** (never bare).
- Phase READMEs that talk about both contexts cite the explicit form.

---

## 7. Token-budget cross-reference (per phase)

Each phase contributes to the unified token budget. See `Plan/000-overview.md`
§5 for the master table; this section summarises the per-phase contribution
so phase documents can cite their target consistently.

| Phase | Primary win | Target | Measured by |
|---|---|---|---|
| 0 — Foundation cleanup | removes confusion; rehomes legacy artefacts | unchanged tool count; boot context < 500 | `tests/smoke/test_no_jules_plugin.py` |
| 1 — Anchor triad + envelope | cold-start triad + envelope + TOON | `tools/list` 38 KB → < 4 KB; boot 34k → < 500 tokens; TOON 40-60% reduction on list returns | `tests/smoke/test_boot_budget.py` (Spec 131); `tests/smoke/test_toon_gate.py` (Spec 105) |
| 2 — Hook chain | runtime tool-output compression | 20-30% of session input; 4 KB cap on any result | `tests/smoke/test_archive_threshold.py` |
| 3 — GitHub sink wrapper | PR/issue read collapse | 40-80k tokens → ≤ 2.5 KB envelope | manual: 3 sample PRs |
| 4 — Context Mode Path B | document deferral | ≥ 200 KB summed → 0 by default | `tests/smoke/test_path_b_defers.py` |
| 5 — Ontology + Graph (Wave D) | cross-domain queryability | 22 spec reads → 1 Cypher MATCH | `tests/smoke/test_graph_queries.py` |
| 6 — Quality / loop / compaction | self-healing context | ~47k tokens saved per loop-detected session | session-log query + loop-detection telemetry |
| 7 — Domain handler completion | feature completeness across five domains + agentic | no regression on `tools/list` cold payload | manifest-coverage lint (Spec 131) |
| 8 — Operational hardening + L3 daemon | polish + bus-factor + cross-harness portability | L3 daemon serves the four-verb contract over HTTP at ~100 ms p50 (localhost) | `tests/integration/test_devmode_server.py` |

---

## 8. Cross-document index

| Topic | Authoritative location |
|---|---|
| Master phase map and dependency DAG | `Plan/000-overview.md` §4 + §9 |
| North star (three collapses, one budget) | `Plan/000-overview.md` §1 |
| Harness three-layer design (L1 + L2 + L3) | `Plan/harness/design.md` §2, §3 (L1), §4 (L2), §5 (L3) |
| Domain isomorphism audit (six/strain analysis) | `Plan/harness/_research/05-domain-isomorphism.md` |
| Harness Path A levers (L-α, L-β, L-γ) | `Plan/harness/design.md` §11.2, §11.6.1 |
| Harness Path B endgame (`Domain` base class) | `Plan/harness/restructure/spec.md` + `Plan/harness/design.md` §11.4 |
| Jules orchestration loop | `Plan/JULES-REVIEW-LOOP.md` |
| Jules session lifecycle & recovery | `Plan/JULES_PROTOCOL.md` |
| Per-spec acceptance (Gherkin) | `Plan/phase-N-*/acceptance.feature` and `Plan/<NNN>-*/spec.md` |
| State on disk | `~/.agency-system/cache/*` — see §1 |
| Skill ledger (auto-discovery rules) | `bin/agency-dev-install` line 53 (skill namespace audit) |

---

## 9. When to update this file

Append to this file when:

1. A new top-level term enters the design (e.g., a new layer, a new domain,
   a new state file).
2. A naming collision is discovered (qualify both sides here, then fix
   downstream).
3. A phase document needs to reference a cross-cutting invariant that does
   not yet have a canonical name.

Do **not** add ephemeral terms (work-in-progress branch names, draft spec
slugs, names that exist only in a single sub-spec). The threshold is
"used by ≥ 2 phase documents or ≥ 1 phase document + the overview".
