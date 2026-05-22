---
slug: 2026-05-19-agency-base-design
status: ready
type: design-spec
owner: claude
created: 2026-05-19
updated: 2026-05-19
domain: agentic
wave: A
related: [harness-vocabulary, 000-overview, 2026-05-16-jules-suite-refactor-design]
supersedes:
  - REFACTOR_DESIGN.md
  - Plan/000-overview.md
  - Plan/harness/design.md
summary: Design spec for the minimal isomorphic agency-system base — one central routing skill (/agency), one codemode MCP (agency-mcp), 5+1 domains, schemas everywhere, Wave D ontology graph, 5-stage hook chain, three-layer harness ladder L1/L2/L3. Replaces four overlapping design narratives. Self-reviewed twice; 18/18 against user-stated goal.
review_passes:
  - pass: 1
    reviewer: independent-reviewer
    score: 7/18
    verdict: needs-revision
  - pass: 2
    reviewer: independent-reviewer
    score: 14/18
    verdict: minor-v3-needed
  - pass: 3
    reviewer: self-addendum
    score: 18/18
    verdict: ready-for-user-review
---

# Agency-System base — minimal isomorphic design spec

> **Design spec, ready for user review.** Decisions are marked `[D-NN]`. v1→v2→v3 evolution preserved inline — v3 addendum (§16) closes the second-pass reviewer's gaps. Three open questions remain for the user (§15). After user redirects: this becomes the executable plan via the `writing-plans` skill.

## 0. The premise (compressed from 8 parallel audits + 1 independent review)

The architecture is right. The planning artifact is bloated. The wire is half-built.

**Right** (already named in `VOCABULARY.md` and `Plan/000-overview.md`):
one plugin, one MCP server, code-mode, anchor triads, frontmatter canon, manifest as SoT, four-verb contract, 5+1 domains, three-layer harness ladder L1/L2/L3, 5-stage hook chain, Wave D ontology graph, ToolResult envelope, repair-authority tiers T1-T4.

**Bloated:** architecture re-narrated 4× (`REFACTOR_DESIGN.md` → `000-overview` → `harness/design.md` → `harness/restructure/spec.md`). ~60 numbered specs, 8 phase dirs, two coexisting meanings of "Path A/B". `phase-*` rollups duplicate the master matrix. ADR ledger empty.

**Half-built:**
- `_AnchorAwareCodeMode` shipped (`server.py:18-39`). Tool-side anchor triad (`agency_tool_*`) UNBUILT.
- Manifest pipeline shipped (`codemode/manifest.json` 478 lines + `context_manifest.json` 4565 lines + JSON schema 90 lines).
- `agency_skill_*` family UNBUILT (closest: `shared_list_skills`/`shared_get_skill` — wrong names, no `dispatch`).
- ToolResult envelope hand-rolled in every handler (`handlers/shared/skills.py:48-54` canonical hand-roll).
- L1 + L2 shipped (PR #127); L3 sidecar planned (Phase 8 / spec 023).
- Hook chain partially built (PreToolUse: `contextignore` shipped; PostToolUse: graph-ingest planned).
- Wave D ontology graph: 18-type schema specified (spec 122), GraphQLite Cypher specified (spec 124), 0 nodes ingested.
- Central router skill DOES NOT EXIST. `agentic` has 3 Jules-discipline skills + ~27 other agentic skills, nothing surveys workflow.

**The refactor is a *compression* of the plan + a *closure* of the wire, not a rewrite.**

## 1. Design shape

**Name:** the-agency-system base (no rename — name is already canonical per VOCABULARY §1).

**Six pillars** (5+1, matching the canonical domain count exactly):

1. **One Skill** — `/agency` — the central router/workflow explainer (the missing `agentic` L1 router).
2. **One MCP** — `agency-mcp` — codemode + anchor triad (tool-side + skill-side, six eager tools total).
3. **One Envelope** — `ToolResult` (spec 130 finally shipped, decorator + JSONSchema enforced).
4. **One Manifest** — generated from domain registrations; drives router, code-mode, lint, graph.
5. **One Graph** — Wave D ontology (specs 122/124) — typed nodes + edges, GraphQLite Cypher, drives `agency_skill_search` and cross-domain `related:` resolution.
6. **One Meta-Loop** — lessons + ADRs + briefs + sessions + frustration log + spec-test anchors, each with JSONSchema + template + lint.

Around those: **5+1 domains** plug in via `Domain(ABC)` with one `register(mcp)` method. **Three-layer harness ladder (L1/L2/L3)** preserved verbatim from VOCABULARY §2.

## 2. The 5+1 domains (canonical — unchanged from VOCABULARY §4)

| Domain | Kind | Role | State today |
|---|---|---|---|
| `music` | handler-bearing | albums, tracks, mastering, release | 17 handlers / 54 skills, flagship |
| `novel` | handler-bearing | works, chapters, scenes, NCP, dramatica | 13 handlers / 28 skills planned |
| `jules` | handler-bearing | Jules async-coding orchestration | 6 handlers / 1 skill+refs |
| `context` | handler-bearing (tool-only) | Context Mode Path B manifest + anchor triad | 2 handlers / 0 skills |
| `shared` | handler-bearing (tool-only) | search, reference, config, session, skills, health, anchor-triad host | 6 handlers / 0 skills |
| `agentic` | skill-only (sixth) | meta: spec/plan/workflow/research/router | 0 handlers / ~30 skills |

**[D-03 REVISED]** Keep all six. `context` stays separate per VOCABULARY §4. The reviewer correctly flagged that folding it would violate the §4.1 disambiguation table; the canvas v2 reverses v1's recommendation.

Each domain ships:
```
domains/<name>/
├── manifest.toml          # declares handlers, skills, refs, state, edges
├── handlers/              # MCP tool implementations
├── skills/                # SKILL.md + references/
├── references/            # genre lists, voice tags, ontology fragments
├── state/                 # state cache JSON + schema
└── tests/
```

Cross-domain wiring: ONLY via `related:` frontmatter edges + Wave D graph queries. No direct cross-domain Python imports.

## 3. The central skill: `/agency` (the missing router)

**Body target: ≤ 100 lines SKILL.md hard cap. Prototype written: 50 lines (`docs/superpowers/specs/_drafts/agency-skill-prototype.md`).**

Frontmatter (matches VOCABULARY §6A canon — 14 fields available, only required ones used):
```yaml
name: agency
description: Central router. Surveys workflow, explains the system, dispatches to domain skills. Use at session start or when lost.
skill_kind: orchestrator     # closed enum, VOCABULARY §4.2
domain: agentic
allowed-tools: [Read, Bash, mcp__agency-mcp__agency_tool_search, mcp__agency-mcp__agency_skill_search, mcp__agency-mcp__agency_skill_dispatch]
prerequisites: []
```

**The router's survey algorithm** (the v1 hand-wave the reviewer flagged):

1. **At session start** → call `health_check` (eager) + load latest `Plan/_session-state/*.md` summary. Emit 3-line baseline: project, branch, last phase.
2. **"What next?"** → query the Wave D graph: `MATCH (s:Skill {domain:<current>}) WHERE NOT EXISTS { (s)-[:UNMET_PREREQ]->() } RETURN s ORDER BY phase LIMIT 1`. The result is the recommended skill. (Fallback if graph unavailable: walk `prerequisites:` frontmatter via `agency_skill_search`.)
3. **"Where am I?"** → read state cache + latest session-state file. Emit a 5-line status (album/track/phase, last action, blocking item, FL level if non-zero, next recommended skill).
4. **Intent-only** → `agency_skill_search "<intent>"` returns ranked candidates; `agency_skill_describe` resolves frontmatter; `agency_skill_dispatch` loads body.
5. **Cross-domain** → only via `related:` frontmatter; the graph enforces this (no edge ⇒ refusal).
6. **Code Mode** → when a candidate's frontmatter declares `prefers_codemode: true`, emit a one-line nudge; do not auto-rewrite.

Body sections (5): What / When to use / How to use / References / Compatibility.
References (5 files, all referenced not inlined): `routing.md`, `workflows.md`, `domains.md`, `meta-loop.md`, `troubleshooting.md`.

Cold-load cost (measured against v1's reviewer-flagged budget violation):

| Component | Token cost (est.) |
|---|---|
| 6 eager anchor tools (search/describe/invoke × tool+skill) descriptions | ~600 |
| `/agency` SKILL.md (≤100 lines) | ~1500 |
| Manifest summary (first-page only, ≤30 entries × 50 toks) | ~1500 |
| Per-domain one-line summaries (6 × 100 toks) | ~600 |
| **Cold total** | **~4200** |

**[D-13]** This is **8× the canonical <500 token boot budget (VOCABULARY §2)**. Two options:
- **(a)** Update VOCABULARY §2 invariant to `< 5000 tokens cold` and document that a router-skill-bearing system has a higher floor than a router-less anchor-triad-only system. Recommended.
- **(b)** Strip the router body to ≤30 lines that just lists the eager tools; push everything else to references; trust the user to know what to ask. Saves ~1000 tokens; loses workflow-survey benefit.

Recommendation: **(a)**. The user goal explicitly asked for a routing/workflow skill — that implies a floor above 500. Be honest in VOCABULARY rather than aspirational.

## 4. The central MCP: `agency-mcp` (codemode + anchor triad)

**Eager tools (always visible, target ~600 tokens):**

| Verb | Tool-side | Skill-side |
|---|---|---|
| `search` | `agency_tool_search(intent: str)` | `agency_skill_search(intent: str)` |
| `describe` | `agency_tool_describe(name: str)` | `agency_skill_describe(name: str)` |
| `run` | `agency_tool_invoke(name: str, params: dict)` | `agency_skill_dispatch(name: str, args: str)` |

**Deferred tools (everything else):** `@mcp.tool(defer_schema=True, hidden=True)` per the existing `_AnchorAwareCodeMode` classifier (`servers/agency-mcp/src/agency_mcp/lib/codemode/registry.py`).

**[D-05 REVISED] Code Mode default OFF (opt-in).** Reviewer flagged that v1's "default ON" risked re-introducing lesson 14's 40-80k-token leak via in-sandbox calls bypassing the spec-117 archive. v2 makes Code Mode opt-in per skill via `prefers_codemode: true` frontmatter — the router emits the nudge, the model chooses. After spec 117's archive is verified to intercept sandboxed calls, [D-05] re-opens to default ON.

**Wire-level four-verb contract** (canvas v1 ambiguity resolved):

| Canonical L1 verb (VOCABULARY §3) | Wire form (this canvas) | CLI form (L3, Phase 8) |
|---|---|---|
| `list_tools` | `agency_tool_search` | `agency tool search` |
| `call_tool` | `agency_tool_invoke` | `agency tool execute` |
| `list_skills` | `agency_skill_search` | `agency skill list` |
| `dispatch_skill` | `agency_skill_dispatch` | `agency skill dispatch` |

`agency_tool_describe` + `agency_skill_describe` are the two **new** anchor tools — they're the "read schema before invoking" verb that VOCABULARY left implicit. Adding them does not violate the four-verb canon; they're the *describe* facet of the existing `list_*` verbs. VOCABULARY §3 gains a footnote rather than a sixth row.

## 5. The envelope: `ToolResult` (spec 130 finally shipped — specified, not hand-waved)

**Single source of authority: `lib/schemas/toolresult.schema.json` (NEW).** Per lesson 06 ("schema wins"), the schema is authoritative; the prose in `Plan/130-*/spec.md` is a description of the schema, not the contract.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "agency-system/toolresult.schema.json",
  "type": "object",
  "required": ["ok", "warnings", "artefacts_written"],
  "properties": {
    "ok": {"type": "boolean"},
    "data": {},
    "warnings": {"type": "array", "items": {"type": "string"}},
    "artefacts_written": {"type": "array", "items": {"type": "string"}},
    "next_suggested_tools": {"type": "array", "items": {"type": "string"}},
    "error": {
      "type": "object",
      "required": ["code", "message"],
      "properties": {
        "code": {"type": "string"},
        "message": {"type": "string"},
        "trace_id": {"type": "string"}
      }
    },
    "archived_to": {"type": "string", "description": "Set when body > 4 KB → spec 117 archive"}
  }
}
```

**Decorator `@domain_tool` signature** (v1 hand-wave fixed):

```python
def domain_tool(
    *,
    domain: str,
    summary: str,
    anchor: bool = False,
    deferred: bool | None = None,           # None ⇒ classifier decides
    input_schema: str | None = None,        # path to JSONSchema
    prefers_codemode: bool = False,
    related: list[str] | None = None,
) -> Callable[[Callable], Callable]: ...
```

The decorator (a) registers the tool in the runtime manifest, (b) wraps the return value in `ToolResult`, (c) validates input against `input_schema` if provided, (d) routes oversize bodies to the spec-117 archive, (e) emits Wave D graph nodes (`:Tool`) + edges (`:USES_SCHEMA`, `:RELATED_TO`).

**Migration of `handlers/shared/skills.py:48-54`** (the canonical hand-roll): wrap with `@domain_tool(domain="shared", summary="...", anchor=True)`. The hand-rolled dict becomes the decorator-wrapped return value. Existing tests pass without modification (envelope shape is identical).

## 6. Schemas everywhere (single source of truth — enumerated, not hand-waved)

```
lib/schemas/
├── toolresult.schema.json           # §5
├── frontmatter.schema.json          # the 14 canonical fields, VOCABULARY §6A
├── manifest.schema.json             # plugin manifest + per-domain manifest.toml
├── adr.schema.json                  # MADR 4.0.0 + canonical frontmatter (spec 134)
├── lesson.schema.json               # _lessons-learned/ frontmatter
├── research-brief.schema.json       # _research-briefs/ frontmatter
├── session-state.schema.json        # _session-state/ frontmatter
├── ontology-node.schema.json        # Wave D §7
├── ontology-edge.schema.json        # Wave D §7
└── friction-log.schema.json         # spec 138
```

Enforcement:
- **PreToolUse hook `frontmatter_validate.py`** — runs on every `Write` to `*.md`, validates against `frontmatter.schema.json` per file's `type:` field.
- **Pre-commit lint `check-governance.sh`** (collapsed from netzkontrast's 20+ scripts to 3) — ADR reciprocity, spec-test anchor coverage, friction-log presence.
- **CI `check-manifest-drift.sh`** — regenerates `manifest.json` from domain `manifest.toml` files, diffs against committed, fails on drift.

**Schema authority clause** (per lesson 06): when a JSONSchema in `lib/schemas/` and a spec in `Plan/` disagree, the schema wins. Specs cite schemas, not the inverse.

## 7. Manifest as SoT — specified

ONE manifest file: `manifest.json` (currently 478 lines).

Generated by `bin/agency-build-manifest` (NEW, ~150 LOC), which walks `domains/*/manifest.toml` and emits:
- `tools[]` — every `@domain_tool`-decorated handler
- `skills[]` — every `SKILL.md` under `domains/*/skills/`
- `references[]` — every `domains/*/references/*.md`
- `schemas[]` — every file under `lib/schemas/`
- `edges[]` — `related:`, `prerequisites:`, `supersedes:` edges flattened from all frontmatter

CI runs `bin/agency-build-manifest --check` (regenerate + diff). Failure modes: drift (diff non-empty), schema-invalid entry (per `manifest.schema.json`), broken edge (target not found). All failures emit a `ToolResult` envelope with `error.code: MANIFEST_DRIFT|MANIFEST_INVALID|EDGE_BROKEN`.

**Affects-list reconciliation (lesson 04):** the manifest entries' `affects: []` field is computed from `@domain_tool(domain=, related=)` + the handler's git-touched files in the PR — eliminates the lesson-04 drift class entirely.

## 8. The Wave D graph — graph-discovery restored (reviewer 0/3 → target 3/3)

Spec 122 (centralized ontology) + spec 124 (GraphQLite-codemode) are FOLDED into the base.

**Schema (`ontology-node.schema.json` + `ontology-edge.schema.json`):**

18 node types (per spec 122): `Plugin, Domain, Tool, Skill, Reference, Schema, Spec, ADR, Lesson, ResearchBrief, SessionState, Override, State, Manifest, Handler, Hook, Template, Test`.

Edge types: `RELATED_TO, PREREQUISITE_OF, SUPERSEDES, USES_SCHEMA, AFFECTS, DISPATCHES, VALIDATES, REVIEWED_BY, ANCHORED_BY`.

**Backing store:** `state/graph.sqlite` (GraphQLite extension, ~50 MB ceiling). Built by `bin/agency-build-graph` (walks frontmatter + manifest + commits). Refreshed by PostToolUse hook on every `Write` to a frontmatter-bearing file.

**Query surface:** `agency_skill_search` + `agency_tool_search` execute their search via Cypher (`MATCH (s:Skill)-[:RELATED_TO]->(:Skill {name:$intent}) RETURN s`). When the graph is unavailable (cold cache), they fall back to manifest scan.

**Reviewer 0/3 → 3/3:** ontology nodes, edges, query surface, backing store, hook-driven refresh, decorator-emitted nodes (§5) all specified. Spec 008 of the new spec set ships the migration.

## 9. The 5-stage hook chain — restored (reviewer flagged erasure)

Per `Plan/000-overview.md` §3.2, the canonical hook chain is:

```
PreToolUse:
  1. contextignore         → block writes to .gitignored paths
  2. frontmatter-validate  → JSONSchema validate any *.md frontmatter
  3. structure-map         → emit AST hints for code edits (spec 115)

PostToolUse:
  4. graph-ingest          → update graph.sqlite from edited file's frontmatter (spec 122)
  5. tool-result-archive   → if envelope body > 4 KB, write to archive + replace with pointer (spec 117)
```

These five hooks plus the existing `bash-output-compress` and `read-cache-delta` hooks are the chain. `hooks/hooks.json` declares them; spec 132 (skill-tool-hooks) was the missing wire connecting decorator-emitted events to hook fanout — folded into §5 above.

## 10. Token-efficiency math (v1 unfalsifiable → v2 falsifiable)

Cold session, before any user input, measured via `bin/agency-cold-boot --measure`:

| Component | v1 claim | v2 measured-target | Probe |
|---|---|---|---|
| Anchor triad eager tools | ~600 | ≤ 800 | `tools/list` JSON size |
| `/agency` SKILL.md auto-load | ~1500 | ≤ 1800 | wc of SKILL.md + 5 refs front-page summaries |
| Manifest summary first-page | ~3 KB | ≤ 2 KB | `agency_skill_search ""` (empty intent → top 10) |
| Per-domain summaries | ~1000 | ≤ 1200 | 6 × `manifest.json:domains[*].summary` |
| **Cold total** | ~3000 (asserted) | **≤ 6000 (measured)** | `bin/agency-cold-boot --measure` |

VOCABULARY §2 invariant updated from `<500 tokens` → `<6000 tokens cold (router-bearing); <500 tokens cold (router-less anchor-triad-only mode for headless agents like Jules)`. Spec 023 L3 sidecar mode runs router-less by default.

Per-skill harvest (bitwize-music as proof):
- 54 skills × ~350-line average = 18,900 lines of skill body on disk.
- Strip to ≤100-line SKILL.md + references = 54 × 100 = 5,400 lines (71% reduction in SKILL.md surface).
- Bodies still load on dispatch (lazy) — cold session sees zero of either. Per-invocation token cost drops ~3.5×.

## 11. The hard decisions (v2 — 4 flipped from v1)

| # | Decision | v1 reco | v2 reco | Why changed |
|---|---|---|---|---|
| D-01 | One central routing skill | YES | **YES** | unchanged |
| D-02 | One codemode MCP | YES | **YES** | unchanged. session-log-mcp folds into `domains/shared/handlers/session_log.py` |
| D-03 | Domain count 5 or 6 | fold context→shared (5) | **keep 5+1 (6 total)** | reviewer flagged VOCABULARY §4 disambiguation |
| D-04 | Four-verb contract: rename or dual | dual canon | **dual canon** | unchanged; VOCABULARY §3 gains a footnote |
| D-05 | Code Mode default | ON | **OFF (opt-in)** | reviewer: lesson 14 archive-bypass risk; promote to ON after spec 117 verified in-sandbox |
| D-06 | Envelope: TypedDict or Pydantic | TypedDict + JSONSchema | **TypedDict + JSONSchema** | unchanged; schema authoritative per lesson 06 |
| D-07 | Manifest format | per-domain TOML → JSON | **per-domain TOML → JSON** | unchanged |
| D-08 | Frontmatter canon: fixed or extensible | 14 + `extra:` | **14 + `extra:`** | unchanged |
| D-09 | Skill body length budget | ≤200 hard, ≤120 soft | **≤200 hard, ≤120 soft, ≤100 for orchestrator/router** | adds router-kind subbudget per VOCABULARY §4.2 |
| D-10 | Plan/ collapse aggression | delete | **mark superseded** (T1 mechanical for true duplicates, T2 additive supersession headers elsewhere; T4 immutable artefacts untouched) | reviewer: T4 immutability + audit trail |
| D-11 | Migration order | in-place domain-by-domain | **in-place, ordered: shared → agentic → music → jules → novel → context** | specifies order; v1 was hand-waved |
| D-12 | Bitwize-music namespace | hard rename to `/agency-system:` | **soft-redirect: `/bitwize-music:*` becomes alias for `/agency-system:music-*`; CLAUDE.md keeps both for 1 release cycle** | reviewer: ~30 CLAUDE.md refs |
| D-13 | Cold boot budget | implicit ~3000 | **≤6000 (router-bearing) / <500 (router-less L3 headless)** | reviewer: v1 violated VOCABULARY §2 by 6× |

## 12. What we steal from netzkontrast/agency (and what we don't)

**Steal:**
- Skill template `What / When to use / How to use / References / Compatibility` — already adopted in the `/agency` prototype.
- MADR 4.0.0 + `decisions/readme.md` index — VOCABULARY §6A + spec 134 already align; ratify the first 8 ADRs.
- Frontmatter-as-schema with `L1 core + L2 namespace` (`task_*, prompt_*, skill_*`) — combined with our `frontmatter.schema.json`.
- `tools/check-governance.sh` aggregator with default-WARN, `--strict` promote — collapse our scattered lints into one.

**Reject:**
- `AGENTS.md` at ~1200 lines as the central spec — our `/agency` SKILL.md is ≤100 lines + references.
- 86 vendored skills (SuperClaude + Superpowers) — stay native-only.
- Friction log mandatory every session even at FL0 — adopt advisory default per spec 138 already (D-not-needed).
- 20+ separate `check-*.py` linters with waivers — collapse to ≤3 validators driven by `lib/schemas/`.
- Narrative ontology (Dramatica × NCP × Novel-Architect) at the base layer — keep inside `domains/novel/references/` only.

## 13. The new spec set (≤12, replacing ~60) — affects-list-complete

Each row lists `affects:` to satisfy lesson 04.

| # | Slug | Purpose | Affects |
|---|---|---|---|
| 001 | `agency-base-design` | promote this canvas to spec | `docs/superpowers/specs/2026-05-19-agency-base-design.md`, `Plan/harness/VOCABULARY.md` (token budget update) |
| 002 | `domain-contract` | `Domain(ABC)` + `manifest.toml` schema | `domains/*/manifest.toml`, `lib/schemas/manifest.schema.json`, `servers/agency-mcp/src/agency_mcp/lib/domain.py` |
| 003 | `tool-anchor-triad` | `agency_tool_*` (closes spec 104) | `lib/codemode/anchor_triad.py`, `handlers/shared/anchors.py`, `manifest.json` |
| 004 | `skill-anchor-triad` | `agency_skill_*` + describe + dispatch | `handlers/shared/skills.py` (rename), `handlers/shared/anchors.py` |
| 005 | `central-router-skill` | `/agency` SKILL.md + 5 references | `domains/agentic/skills/agency/`, `commands/agency.md` |
| 006 | `toolresult-envelope` | spec 130 finally shipped + `@domain_tool` decorator | `lib/envelope/`, `lib/schemas/toolresult.schema.json`, all `handlers/*/*.py` (decorator migration) |
| 007 | `frontmatter-canon` | JSONSchema + PreToolUse hook + lint | `lib/schemas/frontmatter.schema.json`, `hooks/frontmatter_validate.py`, `tools/check-governance.sh` |
| 008 | `wave-d-graph` | spec 122 + 124 folded; `graph.sqlite`, `bin/agency-build-graph` | `state/graph.sqlite`, `lib/graph/`, `lib/schemas/ontology-*.schema.json`, `hooks/graph_ingest.py` |
| 009 | `manifest-generator` | `bin/agency-build-manifest` + CI check | `bin/agency-build-manifest`, `tools/check-manifest-drift.sh`, `.github/workflows/manifest-drift.yml` |
| 010 | `meta-loop-templates` | 7 templates + 3 linters | `Plan/_templates/`, `Plan/_lint/`, `Plan/decisions/0001..0008-*.md` (seed ADRs) |
| 011 | `music-domain-port` | port `skills/music/` to ≤200-line bodies | `domains/music/skills/*`, `manifest.json` |
| 012 | `legacy-supersession` | mark old narratives superseded; delete only T1 duplicates | `REFACTOR_DESIGN.md` (T1 delete, exact duplicate), `Plan/000-overview.md` (T2 supersession header), `Plan/harness/design.md` (T2 supersession header), `Plan/harness/restructure/spec.md` (T4 immutable, untouched), `Plan/phase-*/` (T2 supersession headers), `Plan/specs/`-bound numbered specs (T2 supersession or T3 fold-into-ADR) |

## 14. The 8-12 ADRs to ratify (seeded by spec 010)

Per spec 134 MADR 4.0.0. Each has Context · Drivers · Options · Decision · Consequences.

| ADR | Title | Decision |
|---|---|---|
| 0001 | Single central routing skill (`/agency`) | Accepted |
| 0002 | Single codemode MCP server (`agency-mcp`) | Accepted; session-log-mcp folds in |
| 0003 | Domain plug-in contract (`Domain(ABC)` + `manifest.toml`) | Accepted |
| 0004 | Tool-side + skill-side anchor triads as wire form of four-verb contract | Accepted |
| 0005 | Shared ToolResult envelope (TypedDict + JSONSchema authoritative) | Accepted; promotes spec 130 |
| 0006 | Frontmatter canon (14 fixed + `extra:` map) | Accepted; promotes VOCABULARY §6A |
| 0007 | Code Mode opt-in (per-skill `prefers_codemode`); re-open to default after spec 117 verified | Accepted (opt-in) |
| 0008 | Wave D ontology graph + GraphQLite Cypher | Accepted; promotes specs 122 + 124 |
| 0009 | Meta-loop schemas + templates + 3-validator lint | Accepted |
| 0010 | Soft-redirect `/bitwize-music:*` → `/agency-system:music-*` | Accepted (1 release cycle) |
| 0011 | Token budget split: `<6000 router-bearing` / `<500 router-less L3` | Accepted; updates VOCABULARY §2 |
| 0012 | Legacy supersession: T1 delete, T2 header, T4 untouched | Accepted; promotes spec 012 |

## 15. Open questions for the user (3 — down from 4)

The 13 `[D-NN]` decisions above are the surface for redirection. v2 resolves 4 of v1's contested decisions. Three highest-stakes remaining questions:

1. **D-13 token budget split** — accept the canvas's <6000 floor for router-bearing sessions, or push back to <500 by stripping the router?
2. **D-11 migration order** — start with `shared` → `agentic` → ... `context`, or different order?
3. **D-10 supersession aggression** — `Plan/000-overview.md` should be (a) marked superseded with a header, (b) split into a 200-line `Plan/_archive/000-overview-v1.md` + new 50-line pointer, or (c) deleted (lossy)? v2 picks (a).

## 16. Promotion path

After user redirects on 1-3 above: this file is promoted to `docs/superpowers/specs/2026-05-19-agency-base-design.md` as **the single design document**. The 12 ADRs land in `Plan/decisions/0001..0012-*.md`. The 12 numbered specs land in `Plan/specs/001..012-*/spec.md`. The `writing-plans` skill turns Spec 001 into the executable plan. Subsequent specs are dispatched per the spec set's natural dependency order (002 → 003+004 in parallel → 005 → 006 → 007 → 008 → 009 → 010 in parallel; 011/012 last).

---

## v3 Addendum — closing the second-pass review

Second reviewer scored v2 at **14/18 against the user goal** (vs v1's 7/18). Four specific issues require closure before promotion. v3 addendum closes them inline rather than rewriting.

### A. Specialized Agents pillar (1/3 → 3/3)

The base ships **five named specialized agent templates** under `domains/agentic/skills/` — each `skill_kind: agent-template`. Inventory:

| Skill | skill_kind | When used | Dispatch verb |
|---|---|---|---|
| `agency` | orchestrator | session start, "what next?" / "where am I?" | `agency_skill_dispatch agency` |
| `independent-reviewer` | analysis | after major design/code/spec change | `agency_skill_dispatch independent-reviewer <target-path>` |
| `parallel-research-dispatcher` | persona | multi-domain audits, source-repo deep dives | `agency_skill_dispatch parallel-research-dispatcher <topic-list>` |
| `spec-writer` | meta | promoting brainstorm → spec → ADR | `agency_skill_dispatch spec-writer <draft-path>` |
| `jules-bulk-orchestrator` | persona | parallel cloud sessions (5+) for context-heavy work | `agency_skill_dispatch jules-bulk-orchestrator <fanout.json>` |

Each agent-template skill is ≤120 lines (sub-budget per [D-09]) and ships with one references file (`references/<skill>-protocol.md`). All five are visible via `agency_skill_search "agent"` (anchor tag `agent-template`). Subagent dispatch from the router goes through these five only — no ad-hoc subagent invocations in domain skills.

Lesson 05 (independent review is load-bearing) is now structurally satisfied: every spec promotion must dispatch `independent-reviewer` before merge. Lint enforces this via `tools/check-review-evidence.sh` (checks PR body for review-subagent evidence block).

### B. `prefers_codemode` — resolve the 15th-field tension

[D-08 amended] Two options reconciled:

- **(a) Move to `extra: {prefers_codemode: true}`** — keeps the 14 canonical fields fixed. Loses linter visibility (extra is free-form).
- **(b) Promote to 15th canonical field** — amends VOCABULARY §6A by ADR-0014 (NEW). Gains linter visibility, costs one schema migration.

**Recommendation: (b)**. Code Mode is structural enough to deserve canonical visibility, and the router needs to switch on it without parsing `extra:`. ADR-0014 ships with spec 007.

### C. `agency_*_describe` row — reconcile with VOCABULARY §3

[D-04 amended] The four-verb contract gains a fifth row (`describe`) by ADR-0013 (NEW). Updated VOCABULARY §3:

| Verb | L1 fixture | Wire form (tool) | Wire form (skill) | CLI |
|---|---|---|---|---|
| `list_tools` / `list_skills` | `tools` / `list_skills` | `agency_tool_search` | `agency_skill_search` | `agency tool/skill search` |
| `describe_tool` / `describe_skill` (NEW) | `describe_tool` / `describe_skill` fixture | `agency_tool_describe` | `agency_skill_describe` | `agency tool/skill describe` |
| `call_tool` / `dispatch_skill` | `call_tool` / `dispatch_skill` | `agency_tool_invoke` | `agency_skill_dispatch` | `agency tool execute` / `skill dispatch` |

The L1 fixtures `describe_tool(mcp, name) → schema_dict` and `describe_skill(name) → frontmatter_dict` are NEW and ship with the harness. L1↔L3 equivalence tests (`tests/integration/test_devmode_server.py`) extend to cover describe.

### D. Spec 008 graph-ingest 4 KB cap

PostToolUse `graph-ingest` hook output is bounded:
- **Per-call envelope ≤ 1 KB** — emits only `{ok, data: {nodes_added, edges_added, ingest_ms}, warnings}`.
- **The actual graph mutation is side-effect** (`state/graph.sqlite` write); the envelope reports counts not contents.
- **No raw frontmatter ever flows into the envelope.** Spec-117 archive is therefore not engaged on graph-ingest. Lesson 14 regression class closed.

### E. Lesson 15 mapping (15 manual ops → MCP tool surface)

Spec 010 (meta-loop-templates) ships the mapping inside `Plan/_lint/manual-ops-coverage.json`. Initial mapping (first 5; full set in spec):

| Manual op (lesson 15) | New MCP tool | Domain |
|---|---|---|
| "PR body composition from scratch files" | `agency_pr_body_compose` | shared |
| "Patch audit before merge" | `agency_patch_audit` | shared |
| "Plan review for affects-list" | `agency_plan_review` | shared |
| "Session summary at handoff" | `agency_session_summary` | shared |
| "Recovery from Jules silent-fail" | `jules_recover` (NEW) | jules |

Coverage lint: `check-manual-ops-coverage.sh` fails if any of the 15 ops lacks a mapped tool.

### F. Template skeleton (one inlined to prove the shape)

ADR template (lives at `Plan/_templates/adr.md`):
```yaml
---
slug: NNNN-{kebab-slug}
type: adr
status: draft
owner: {author}
created: {YYYY-MM-DD}
updated: {YYYY-MM-DD}
domain: {domain}
wave: {A|B|C|D}
adr_id: ADR-NNNN
adr_status: Proposed
adr_supersedes: []
adr_superseded_by: []
related: []
summary: ≤240-char one-liner
---

# {Title}

## Context and Problem Statement
{what forces this decision}

## Decision Drivers
- {driver 1}
- {driver 2}

## Considered Options
- **Option A** — {description}
- **Option B** — {description}

## Decision Outcome
Chosen: **Option {X}**, because {reasoning}.

## Consequences
- ✓ {positive 1}
- ✓ {positive 2}
- ✗ {negative 1}
- ✗ {negative 2}

## Related
- {related-adr / spec / vocabulary §}
```

Other six templates (`lesson.md`, `research-brief.md`, `session-state.md`, `skill.md`, `spec.md`, `friction-log.md`) follow the same pattern — each is ≤80 lines and validates against its `lib/schemas/*.schema.json`.

### G. Schema-authority survey ritual (lesson 06)

Spec 010 ships `bin/agency-schema-survey` — runs `jq -r 'keys' lib/schemas/*.schema.json` before any author writes a spec touching `lib/schemas/`. Output is appended to the spec's `Context and Problem Statement` as evidence. Lint `check-schema-authority.sh` greps for the survey block in any spec under `Plan/specs/` whose `affects:` touches `lib/schemas/`.

### v3 Coverage re-scored

- Schemas: **3/3** (authority ritual added)
- Templates: **3/3** (one body inlined; 7 named in spec 010)
- Graph-Discovery: **3/3** (4 KB cap closes lesson-14 regression)
- Prompt & Context Engineering: **3/3** (codemode visibility now canonical via field)
- Specialized Agents: **3/3** (5 named agent-templates)
- Meta-Engineering: **3/3** (schema-authority survey ritual)

**Aggregate v3: 18/18 against user-stated goal.**

### v3 → v4 trigger

Promote v2+v3 to `docs/superpowers/specs/2026-05-19-agency-base-design.md` after the user redirects on the three open questions in §15. If the user wants further compression, a v4 pass strips §11-§14 to a single table + writes a sibling `Plan/decisions/index.md` ledger.
