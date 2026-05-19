---
type: research
status: complete
slug: agency-repo-analysis
summary: "Concrete patterns, conventions, and anti-patterns mined from netzkontrast/agency (governance-substrate sibling repo) to inform the-agency-system's harness vision and the Path B isomorphic restructure. Findings from four parallel research agents synthesised here; downstream specs and the VOCABULARY should cite this doc."
sources:
  - https://github.com/netzkontrast/agency (cloned to /tmp/agency-research, commit da09988)
authored_at: 2026-05-18
authored_by: claude
informs:
  - Plan/harness/VOCABULARY.md
  - Plan/harness/design.md
  - Plan/harness/restructure/spec.md
  - Plan/phase-7-domain-handler-completion/specs/015-novel-skills-catalogue/spec.md
  - Plan/phase-7-domain-handler-completion/specs/016-agentic-handlers-and-skills/spec.md
  - Plan/phase-8-operational-hardening/specs/134-plan-adr-convention/spec.md
  - Plan/phase-8-operational-hardening/specs/138-frustration-log-protocol/spec.md
---

# Agency-repo analysis — patterns to port (and to avoid)

**Source:** `netzkontrast/agency` @ `da09988` (cloned via `git clone --depth=20`).
**Method:** four parallel research agents, one per facet (vision/layout, skills, tasks/research/ADRs, anti-patterns/discipline). Each agent was read-only, instructed to cite file + line for every finding, and capped at ~800-1000 words.

The agency repo is a **governance and orchestration substrate** for long-horizon AI work — *not an application or a plugin* (`/tmp/agency-research/README.md:5`). It is structurally and culturally different from the-agency-system (which is a Claude Code plugin), but the discipline patterns and naming conventions translate cleanly and several should be adopted.

The findings below map to concrete actions for `Plan/harness/`, the phase specs, and the Path B endgame.

---

## 1. Patterns worth porting (highest leverage first)

### 1.1 The `summary:` frontmatter field as the primary token-saving lever

Every Task / Prompt / Research / Skill / ADR in agency carries a `summary:` field that the manifest indexer pulls into the manifest's "skim view" — the agent reads `summary` before ever opening the body (`/tmp/agency-research/README.md:115`; `/tmp/agency-research/AGENTS.md:396`). This is the single highest-leverage convention agency enforces.

**Action for the-agency-system:**
- Add `summary:` as a **required** frontmatter field to the spec template (`Plan/<NNN>-*/spec.md`), the SKILL.md template, and the VOCABULARY's "spec frontmatter conventions" section. Manifest entries (Phase 4 Context Mode Path B + Phase 5 Wave D graph) should index on `summary` for the L1 view.
- Carry `summary:` into the L1 harness's `dispatch_skill` return value so callers get the trigger phrase without parsing the body.

### 1.2 Three-tier content ladder (T1 / T2 / T3)

Agency enforces three content tiers on skills (`/tmp/agency-research/SKILLS.md:227-235`):

| Tier | Max size | Always loaded? | Lives at |
|---|---|---|---|
| **T1** | ≤ 200 chars | Yes (in manifest) | first 200 chars of body (the "trigger phrase") |
| **T2** | ≤ 5 KB | Route-loaded (on dispatch) | full SKILL.md body |
| **T3** | unlimited | On explicit demand only | `references/` subdirectory |

This maps **exactly** to the harness ladder's progressive-disclosure goal (`Plan/harness/design.md` §5.6 item 4 — deferred to `Plan/harness/L3-progressive-disclosure.md`). Adopt verbatim.

**Action:**
- Use T1/T2/T3 as the canonical tier names in `Plan/harness/L3-progressive-disclosure.md` (the deferred follow-up sub-spec).
- Add `tier:` boundary doc to VOCABULARY § (a new sub-section).
- Phase 8 Spec 136 (agents.yaml) should emit `tier_summary` (T1), `tier_body_path` (T2), `tier_references_path` (T3) per agent role.

### 1.3 Closed `skill_kind` enum (9 values)

Agency enforces a **closed enum** on every SKILL.md's `skill_kind:` field (`/tmp/agency-research/SKILLS.md:68`; `/tmp/agency-research/tools/fm/validate.py:46-50`):

`domain | tool | orchestrator | meta | discipline | workflow | persona | analysis | agent-template`

This dimension is **orthogonal to the domain prefix** — `skills/music/lyric-writer/SKILL.md` has `domain=music` AND `skill_kind=domain`; `skills/agentic/jules-orchestrator-discipline/SKILL.md` has `domain=agentic` AND `skill_kind=discipline`.

**Action:**
- Add `skill_kind:` to VOCABULARY §4 ("Five domains plus agentic") as the orthogonal routing dimension.
- The L1 harness's `dispatch_skill` already returns `frontmatter` (`tests/_harness/skills.py:dispatch_skill`); ensure callers can route on `skill_kind` as well as `name`.
- Phase 7 Spec 015 (novel skills catalogue, 28 skills) and Spec 016 (agentic handlers + skills) should adopt the enum from day one. **Required on every skill, including imports** — agency's drift is a cautionary tale (see §2.2 below).

### 1.4 MADR 4.0.0 ADR ledger in `decisions/`

Agency maintains a small, disciplined set of ADRs under `decisions/NNNN-<slug>.md` using MADR 4.0.0 conventions (`/tmp/agency-research/decisions/0005-repair-authority-tiers.md:1-15`):

```yaml
type: adr
status: draft               # human-doc status
slug: 0005-repair-authority-tiers
summary: "Every change is classified T1/T2/T3/T4 ..."
adr_id: ADR-0005
adr_status: Proposed        # MADR lifecycle: Proposed → Accepted → Superseded
adr_owner: agency-maintainer
adr_tags: [maintenance, tier-classification, immutability]
adr_supersedes: ADR-NNNN    # forward link when applicable
```

Body sections: `## Context and Problem Statement` · `## Decision Drivers` · `## Considered Options` · `## Decision Outcome` · `## Consequences`.

Accepted ADRs are **T4-immutable**; revisions land as a successor ADR that points back via `adr_supersedes`. The ADR ledger is auto-synthesised into `AGENTS.md` via `tools/adr/cli.py synthesize` (`/tmp/agency-research/README.md:171-179`).

**Action for Phase 8 Spec 134 (plan-adr-convention):**
- Adopt MADR 4.0.0 verbatim. Frontmatter schema, body sections, and the supersession rule are all directly portable.
- Use `Plan/decisions/NNNN-<slug>.md` as the location.
- Auto-synthesise into `Plan/000-overview.md` §11 ("Pointers") guarded section, the way agency synthesises into AGENTS.md.

### 1.5 Repair-authority tier classification (T1/T2/T3/T4)

Distinct from but related to content tiers: agency classifies **every change** as T1 (mechanical), T2 (additive), T3 (structural), or T4 (research-touching) before making it (`/tmp/agency-research/decisions/0005-repair-authority-tiers.md:18-25`). T1/T2 land in-place via `tools/fm/edit.py`; T3 changes MUST be opened as Tasks; T4 is immutable.

**Action:**
- Adopt the repair-tier classification in `Plan/JULES_PROTOCOL.md` as a Gate-0 self-classification step before any Jules session opens a PR.
- The four-verb contract's `call_tool` could carry a `tier:` parameter for mutation tools (T1/T2 only — refuse T3/T4 by construction).

### 1.6 Manifest-first skill loading

Agency mandates that any agent query `.skills-manifest.json` (a single emitted JSON listing slug + `skill_kind` + bundles) **before opening any SKILL.md body** (`/tmp/agency-research/SKILLS.md:172, 195-199`). The manifest is the discovery layer; bodies load on demand.

**Action:**
- This is exactly the L1 harness's `list_skills()` → `dispatch_skill(name)` flow. VOCABULARY §3 should explicitly call out this discipline (the four-verb contract's invariant: never read a SKILL.md body without going through `dispatch_skill`).
- Add `tests/smoke/test_skill_manifest_discipline.py` (Phase 8 candidate) asserting no code path opens a SKILL.md file outside the harness's `dispatch_skill`.

### 1.7 Vendor-prefixed skill naming for imports

Agency uses `<vendor>-<bare-slug>` for imported skill corpora (`sc-*` for SuperClaude v4.3.0, `superpowers-*` for obra/superpowers v4.0.3) and reserves bare slugs for native skills (`/tmp/agency-research/AGENTS.md:612-613`; ADR-0011). Imported bodies stay verbatim in `references/upstream-<slug>.md` while SKILL.md stays slim with `skill_source: "<vendor>@v<semver>"`.

**Action:**
- the-agency-system already does this loosely (e.g. `skills/agentic/superpowers-using-superpowers/`). Formalise via VOCABULARY §5 ("Naming conventions") — vendor prefix + `skill_source:` frontmatter + upstream mirror in `references/`.
- If the-agency-system ever vendors skills from agency, use `agency-<slug>` as the prefix.

### 1.8 Skill body conventions: graphviz DOT + "Red Flags" tables

Agency's discipline skills (superpowers-*) embed Graphviz DOT diagrams in fenced code blocks for decision-flow visualization, and use "Red Flags" two-column tables mapping rationalization-thoughts → reality (`/tmp/agency-research/skills/superpowers-using-superpowers/references/upstream-superpowers-using-superpowers.md:28-67`). This is the pattern Claude Code's `Skill` tool already renders well.

**Action:**
- the-agency-system's skill template (currently varies) should adopt these as recurring sections. Phase 7 Spec 015 (novel skills catalogue, 28 skills) is the highest-leverage place to standardise.

---

## 2. Anti-patterns to avoid

### 2.1 Over-mechanised linter sprawl

Agency lists ~30 distinct linters in `README.md:123-146` (one per coherence-check rule). CLAUDE.md admits a "flexible toolchain" successor still co-exists with `tools/legacy/` (`/tmp/agency-research/CLAUDE.md:108, 218-222`). Symptom: every coherence check became its own script — slow at pre-commit time, hard to maintain.

**Action:**
- Phase 1 Spec 131 (manifest-coverage-lint) + Phase 5 Spec 135 (anchor-traceability) + the future skill-schema lint (deferred `Plan/harness/L-delta-skill-schema.md`) should be **consolidated into a single `bin/agency-lint` entry** with sub-commands, not 3+ separate scripts. Add this consolidation note to VOCABULARY §1 or a new "Discipline" section.
- Cap total lint runtime at < 5s for pre-commit; expensive checks (e.g. token-budget smoke) run in CI only.

### 2.2 Spec / reality drift on frontmatter keys

Agency's `SKILLS.md` mandates `slug:` (`SKILLS.md:59`), but **74/74 actual SKILL.md files use `name:` instead** (`/tmp/agency-research/skills/*/SKILL.md`). The validator (`tools/fm/validate.py`) and the actual files have diverged. The mechanical enforcer doesn't catch what the spec says.

**Action:**
- Pick **one** canonical frontmatter key per concept and enforce from day one. VOCABULARY §5 should be the single source of truth; `bin/agency-lint` validates against VOCABULARY.
- Phase 7 Spec 015 + 016: required-field enforcement runs on every SKILL.md, including imports — agency's drift is the cautionary tale.

### 2.3 Heavy bootstrap-before-anything mandate

Agency requires `./install.sh` + `tools/check-governance.sh` to exit 0 **before any read or write** (`/tmp/agency-research/CLAUDE.md:42-61`). For a plugin that runs on Claude Code on Web (no persistent FS, fresh clone per session), this is a non-starter.

**Action:**
- the-agency-system's L1 harness already avoids this — `from agency_mcp.server import create_mcp` is the only setup. Keep it that way. The L3 daemon (Phase 8) similarly should not require pre-flight scripts; `bin/agency server start` is the only entry point.
- Document this contrast in VOCABULARY §1 — "the-agency-system imposes no pre-flight discipline beyond Python package install."

### 2.4 35 KB self-binding README

Agency's `README.md` is **343 lines / ~35 KB** and includes a "How this README MUST be updated" §11 (`/tmp/agency-research/README.md:236-326`). Self-referential governance increases token cost on every fresh-clone session.

**Action:**
- the-agency-system's root `README.md` is short (62 lines) — keep it that way. VOCABULARY.md handles cross-cutting canon; CLAUDE.md handles session-start instructions; `Plan/000-overview.md` handles the architecture. No file should grow past ~500 lines without splitting.

### 2.5 Narrative-ontology scope creep

Agency's narrative-ontology (304-entry Dramatica + sub-trees) loads ~40k tokens and "is the dominant FL2+ token-budget regression on this corpus", requiring a dedicated WARN-tier linter (`check-narrative-ontology-load.py`) to gate non-narrative tasks (`/tmp/agency-research/README.md:330-340`).

**Action:**
- Phase 5 Wave D's 18-type ontology (Spec 122) must stay **tight**. The ontology graph is for cross-domain queryability, not for inlining domain knowledge into every session.
- VOCABULARY's "Token-budget cross-reference" table (§7) should add a line: "ontology load: per-domain on demand, never eager."

---

## 3. Concepts agency has that the-agency-system does NOT (yet)

| Agency concept | the-agency-system equivalent | Gap |
|---|---|---|
| `summary:` frontmatter (universal) | partial — `description:` on some SKILL.md, no spec-level summary | adopt §1.1 |
| T1/T2/T3 content tiers | partial — referenced in `Plan/harness/L3-progressive-disclosure.md` (deferred) | promote to canon §1.2 |
| `skill_kind` closed enum | none | adopt §1.3 |
| MADR 4.0.0 ADR ledger | Spec 134 (drafted, not yet implemented) | adopt §1.4 |
| Repair-tier (T1/T2/T3/T4) on **changes** | none | adopt §1.5 |
| `.skills-manifest.json` discovery layer | implicit (Claude Code's auto-namespace prefixing) | adopt explicitly §1.6 |
| Vendor-prefix + `skill_source:` for imports | loose convention (`superpowers-*`) | formalise §1.7 |
| Closed-research / Accepted-ADR T4-immutability | none — `Plan/_research/` is mutable | adopt §1.5 |
| MAINTENANCE.md + PRE_COMMIT.md governance | partial — CLAUDE.md only | consider §1 below |
| 9-value `skill_kind` taxonomy for index routing | implicit via folder | adopt §1.3 |

---

## 4. Concrete actions (sequenced)

Apply these in order; each is a small PR independent of the others.

1. **VOCABULARY.md additions (this PR or follow-up):**
   - §3.1 ("frontmatter conventions") — name `summary:` as required across spec / SKILL.md / ADR.
   - §4.2 ("skill_kind orthogonal dimension") — list the 9-value enum.
   - §5.1 ("vendor-prefix imports") — formalise `<vendor>-<slug>` + `skill_source:` + `references/upstream-<slug>.md`.
   - §6.1 ("repair-authority tiers") — T1/T2/T3/T4 classification.
   - §7.1 ("content tiers") — T1/T2/T3 + size caps.

2. **Phase 8 Spec 134 (plan-adr-convention) update:**
   - Frontmatter schema = MADR 4.0.0 (literal copy from agency `decisions/0005-*.md`).
   - Location = `Plan/decisions/NNNN-<slug>.md`.
   - Auto-synthesis into `Plan/000-overview.md` §11.

3. **Phase 8 Spec 138 (frustration-log-protocol) cross-check:**
   - Agency's `FRUSTRATED.md` defines FL0-FL3 with `Definition` + `Action` + `Example` triplets (`/tmp/agency-research/FRUSTRATED.md:13-30`). FL3 = halt + request human intervention, not workaround. Adopt verbatim.
   - **FL0 is mandatory and non-negotiable** — empirically backed: 23/60 (38%) of agency's historical logs are FL0 (`/tmp/agency-research/research/fl0-value-justification/output/SPEC.md:23-32`). Our Spec 138 already captures this; cite the empirical evidence.
   - **Adopt structural-bloat trigger** (automatic FL2): deeply nested folders with <3 files/folder, or per-file readme commits — agency makes these mechanical (`/tmp/agency-research/FRUSTRATED.md:32`). Our Spec 138 omits; add this trigger.
   - **Adopt WARN→STRICT mode toggle** (`FM_FL_DECLARATION_STRICT=1`): advisory first, gate after the corpus is clean (`/tmp/agency-research/FRUSTRATED.md:40`). Our Spec 138 is strict from day one — that's too aggressive for the retrofit phase.
   - Variant-form parser (~14 acceptable surface forms): agency deliberately accepts bold-canonical, list-form, bare, frontmatter-only. Our Spec 138 line 113 says "we deliberately do not ship Agency's 14-variant grammar" — keep that choice, but document the trade-off (simpler, but brittle for retrofitting onto existing logs).

4. **Phase 7 Spec 015 + 016 (skill catalogues) update:**
   - Required fields on every SKILL.md including imports: `slug`, `summary`, `skill_kind`, `skill_target_agents`.
   - Body sections: `## What`, `## When to use`, `## How to use`, `## References`, `## Compatibility`.
   - DOT graphs + Red Flags tables encouraged for discipline-kind skills.

5. **`bin/agency-lint` consolidation (deferred follow-up):**
   - Merge 131 + 135 + future skill-schema lint into one entry with sub-commands.

6. **Path B (`Plan/harness/restructure/spec.md`) note:**
   - When promoted from `vision` → `ready`, the `_base/conventions.py` module that codifies the four-verb invariants should also carry the `skill_kind` enum, the `summary` required field, and the T1/T2/T3/T4 tier classifiers — they are all source-level conventions of the same kind.

---

## 5. Side findings (out of scope but worth flagging)

- **Manifest version drift** in this repo: `.claude-plugin/plugin.json` has `version: "0.1.0-dev"`; `tests/smoke/test_manifest.py:15` asserts `"0.1.0"`. Discovered while verifying the L1 harness for the VOCABULARY work. Not part of alignment; file as a separate issue.
- The L1 harness as shipped (PR #127) works exactly as VOCABULARY §3 documents: `harness_mcp()` boots, `list_tools()` returns 172 tools, `list_skills()` returns 58 paths, `dispatch_skill('lyric-writer')` resolves to `skills/music/lyric-writer/SKILL.md`, `call_tool(mcp, 'health_check', {})` returns `ok=True`.
- Agency cloned at commit `da09988` (default branch `main`) — `Plan/SOURCES.md` lists `claude/agency-plugin-refactor-PgMQ4` as the pin; if specs 010/012/013/015/016/021 fetch from agency, ensure they use the pinned branch, not main.

---

## 6. Task framework & reciprocity invariants (Agent C deep-dive)

Agency's task framework (`/tmp/agency-research/TASK.md`, `templates/task.md`) has several patterns worth porting that are absent from `the-agency-system`'s current spec model.

### 6.1 Subtask structure (Epic / ST-N)

Subtasks live as `subtasks/0N-<slug>.md` **inside the parent Task folder** — not as separate Tasks (`/tmp/agency-research/tasks/094-skill-integration-agency-default/subtasks/04-cleanup-and-close.md:1-79`). Each subtask carries `type: note` frontmatter and stable sections: `Executor / Parallelism / Depends on / Scope / Out of scope / AC / Branch+PR shape`. Each subtask gets its own friction-log (e.g. `subtasks/02-friction-log.md`).

**Action for the-agency-system:**
- the-agency-system currently has no "Epic" pattern — `Plan/phase-N-*/specs/<NNN>-*/spec.md` are flat. For multi-PR phases (Phase 1, Phase 2), the subtask-inside-spec pattern would let us track per-PR scope without spawning new spec dirs.
- Add a `subtasks/` convention to VOCABULARY §1 (or a new §10) — when a spec produces 3+ PRs, use the agency Epic pattern.

### 6.2 Lifecycle: `updated` as closure-with-continuity

Agency has a fifth task state: `open → in_progress (↔ blocked) → done | updated | abandoned` (`/tmp/agency-research/TASK.md:158-188`). `updated` is **"closure with continuity"** — requires a reciprocal successor pair (`task_supersedes` / `task_superseded_by`) and a mandatory "Supersession Rationale" in the friction log.

**Action:**
- the-agency-system's `Plan/<NNN>-*/spec.md` files have no concept of "rolled forward into a successor". Adopt `updated` as a third terminal state alongside `done` / `abandoned`. Useful for Spec 023's split (research-remainder absorbed by `Plan/harness/design.md`; original 023 → `updated` with `superseded_by: harness/design`).

### 6.3 Reciprocity-as-invariant frontmatter

Every cross-link in agency is **reciprocal and enforced** by a single validator (`tools/fm/validate.py --type-check`):

| Forward link | Backward link |
|---|---|
| `task_supersedes` | `task_superseded_by` |
| `task_uses_prompts` | `prompt_relates_to_task` |
| `task_spawns_research` | `research_executes_prompt` |
| `adr_supersedes` | `adr_superseded_by` |

Source: `/tmp/agency-research/TASK.md:343-348, 385-403`.

**Action:**
- the-agency-system's spec frontmatter already has `depends_on`, `related`, `supersedes`, `affects` — but no backward links and no validator enforcement. Add reciprocity rules to VOCABULARY §5 and Spec 131 (manifest-coverage-lint) should enforce them.

### 6.4 Stable Gherkin anchor format: `<DOMAIN>.<aspect>.<scenario>`

Agency uses three-part anchor tags like `BR.94.2`, `T094.1.3`, `ADR.A.3.5`, `FR.B.1` — addressable from prose, linters, and PR reviews (`/tmp/agency-research/tasks/094-…/task.md:135, 144, 152, 160, 168`). Our convention is two-part `# anchor: <phase>.<scenario>` (e.g. `phase-1.tools-list-payload`).

**Action:**
- Phase 5 Spec 135 (spec-test anchor traceability) already enforces our two-part form. Extending to three-part would let us label cross-cutting clauses (`HARNESS.L1.1`, `VOCAB.4.three-enumerations`). Optional — incremental adoption is fine.

### 6.5 Anti-pattern: mirror copies inside phase folders

Agency **deliberately avoids** the mirror pattern (`Plan/phase-N-*/specs/<NNN>-*/spec.md`) that the-agency-system uses today. Reciprocity links keep cross-phase navigation working without duplicating the source-of-truth body. **Every drift in the mirror is silently wrong.**

**Action (significant):**
- the-agency-system's `Plan/phase-N-*/specs/` mirror is a maintenance liability. Pass-2 of this PR already encountered the drift (top-level `Plan/122-*/spec.md` vs `Plan/phase-5-*/specs/122-*/spec.md` differed by 3 lines until I synced them).
- **Recommendation**: in a follow-up PR, **delete the `Plan/phase-N-*/specs/` mirrors** and replace them with `Plan/phase-N-*/specs.md` (one-line table per spec linking to the canonical `Plan/<NNN>-*/spec.md`). The phase aggregator (README.md + acceptance.feature + specs.md) is enough.
- This decision is itself an ADR candidate — see §8 below.

---

## 7. ADR convention (Agent C deep-dive)

Agency maintains a small, disciplined ADR ledger at `/tmp/agency-research/decisions/NNNN-<slug>.md` (4-digit zero-pad, MADR 4.0.0).

### 7.1 Frontmatter schema (literal copy from `decisions/0005-*.md:1-15`)

```yaml
---
type: adr
status: draft               # human-doc lifecycle: draft → review → published
slug: NNNN-<kebab-slug>
summary: "≤ 240 chars one-line abstract"
created: YYYY-MM-DD
updated: YYYY-MM-DD
adr_id: ADR-NNNN
adr_status: Proposed        # MADR lifecycle: Proposed → Accepted → Superseded → Deprecated
adr_owner: <role-or-handle>
adr_tags: [tag1, tag2, ...]
adr_supersedes: ADR-MMMM    # forward link when applicable
adr_superseded_by: ADR-PPPP # backward link populated by successor
---
```

### 7.2 Body sections (MADR 4.0.0)

```
## Context and Problem Statement
## Decision Drivers
## Considered Options
## Decision Outcome
## Consequences   (Positive / Negative / Neutral sub-bullets)
```

### 7.3 Falsifier triggers and sunset clauses

Most agency ADRs ship with **2-5 explicit "falsifier triggers"** — predicates that would mandate a successor (e.g. "third corpus, force-push tag drift, native↔import name collision"). Some also have sunset clauses (ADR-0010 has a 12-month sunset). The nightly audit (`/tmp/agency-research/MAINTENANCE.md:284-303`) runs `tools/adr/audit-triggers.py`, reports `FIRED:<CODE>` per fired trigger or `ok`. **Prevents zombie ADRs.**

### 7.4 T4-immutability + successor-amendment-only

Accepted ADRs are **T4-immutable** — `tools/fm/edit.py` refuses to mutate them (`/tmp/agency-research/MAINTENANCE.md:71`). Defects spawn a successor ADR pointing back via `adr_supersedes`. ADR-0012 is the canonical example (amends ADR-0011's diagnostic codes — `/tmp/agency-research/decisions/0012-skill-source-validator-diagnostic-codes.md:46-49`).

### 7.5 Auto-synthesis into root docs

`tools/adr/cli.py synthesize` writes a guarded block into `AGENTS.md` between explicit byte markers (`<!-- BEGIN DYNAMIC -->` … `<!-- END DYNAMIC -->`). The static section is hand-maintained; the dynamic section is regenerated by the tool (`/tmp/agency-research/MAINTENANCE.md:186`).

**Action for Phase 8 Spec 134 (plan-adr-convention):**
- Adopt all of §7.1–7.5 verbatim. Use `Plan/decisions/NNNN-<slug>.md` as the location.
- Auto-synthesise into `Plan/000-overview.md` §11 ("Pointers") guarded section.
- Falsifier-trigger audit cadence (§7.3) is a free win — port directly.

---

## 8. Pre-commit and discipline mechanics (Agent D deep-dive)

### 8.1 Single delegate hook

Agency's pre-commit hook **does nothing itself** — it just runs `tools/check-governance.sh`, which fans out to ~15 sub-linters (`/tmp/agency-research/.githooks/pre-commit:24-35`). Install via `git config core.hooksPath .githooks`. `set -euo pipefail` (line 11).

**Action:**
- the-agency-system has no `.githooks/`. Create one in Phase 8 (Spec 132 — skill-tool-hooks). Delegate to `bin/agency-lint` (per §2.1 above — consolidated lint entry).

### 8.2 Six-step governance gate

The umbrella `tools/check-governance.sh` runs (in order, per `/tmp/agency-research/PRE_COMMIT.md:38-54`):
1. `tools/fm/validate.py` — frontmatter schema
2. `tools/lint-structure.py` — folder topology
3. `tools/lint-runlog.py` — maintenance run-log
4. `tools/adr/cli.py validate` — ADR schema
5. `tools/fm/index_diff.py` — index/readme.md sync
6. `tools/check-narrative-ontology-load.py` (advisory, WARN tier)

Each rule owns **one concern**; nothing duplicated.

**Action:**
- the-agency-system's planned linters (Spec 131 manifest-coverage; Spec 135 anchor-traceability; future skill-schema) should follow the same one-concern-per-rule pattern. Map them to `bin/agency-lint <rule>` sub-commands.

### 8.3 Per-rule waivers with ISO expiry

Agency uses a TSV waiver file (`/tmp/agency-research/PRE_COMMIT.md:97-117`):
```
<path-glob>\t<rule-id>\t<rationale>\t<expires>\t<tracking-task-slug>
```

Mandatory ISO expiry date; mandatory tracking-Task slug; **mandatory burn-down** ("every coherence-check run SHOULD attempt to remove at least one waiver"). Rule 1 forbids new waivers under `/research/<slug>/output/` (closed research is T4).

**Action:**
- the-agency-system has no waiver mechanism today. Adopt the per-rule TSV form when `bin/agency-lint` ships. Critical: **the expiry is mandatory** — prevents waivers becoming permanent silencing.

### 8.4 Maintenance-bypass mode (deadlock breaker)

A commit may land with **pre-existing** governance errors *iff* every error-bearing path appears in some open Task's `task_affects_paths` (`/tmp/agency-research/MAINTENANCE.md:318-322`). Solves the "can't commit a fix because the pre-existing baseline is broken" deadlock.

**Action:**
- Adopt — VOCABULARY §1 should add a "pre-existing-errors policy" line.

### 8.5 Archive modes

Agency has **three archive modes** for deprecated artefacts (`/tmp/agency-research/ARCHIVE.md:37-49`):
- **Move** — file relocated to an archive tree
- **Snapshot** — immutable copy made while original lives (for research workspaces)
- **Index-only** — frontmatter marker, no physical move (for ADR supersession)

**Trigger-based, not date-based** (`/tmp/agency-research/ARCHIVE.md:22-33`): `task_status` ∈ {done, abandoned, updated} + **7-day cooldown**; `research_phase: complete`; manual governance decision. Cooldown prevents premature archival.

**Action:**
- the-agency-system has no formal archival policy. Adopt the three-mode + 7-day-cooldown pattern in Phase 8 Spec 134 (ADRs) and a future maintenance spec.

### 8.6 Codex review patterns

Agency's reviewer skill uses a **binary severity scale** (Blocking / Advisory), not our 3-tier (BLOCKING / SUBSTANTIVE / NIT) — `/tmp/agency-research/skills/superpowers-code-reviewer/SKILL.md:42-45`. Verdict structure: "Verified / Blocking / Advisory" sections. Reviewer dispatch **must be self-contained** (diff + plan + risk areas) — "the reviewer has zero execution context. That is the point." (`/tmp/agency-research/skills/superpowers-requesting-code-review/SKILL.md:28-29`).

Reviewee discipline (`/tmp/agency-research/skills/superpowers-receiving-code-review/SKILL.md:25-32`): three outcomes per comment — correct+agreed, correct+disagreed, incorrect. **"Never make a change just to close a thread."** Counter to performative agreement.

**Action:**
- the-agency-system uses 3-tier severity in Phase 3 Spec 106 GitHub wrappers and `Plan/JULES-REVIEW-LOOP.md`. Agency's binary scale is cleaner — Substantive is rarely actually distinct from Blocking in practice. Document the trade-off in VOCABULARY (or leave as-is for now and revisit when 106 ships).
- Adopt the "self-contained dispatch" rule into the JULES-REVIEW-LOOP review prompt template — already implicit but make it explicit.

---

## 9. Concrete things agency tried and **abandoned** (worth heeding)

| Pattern | Why abandoned | Lesson for the-agency-system |
|---|---|---|
| Per-file waiver rows (one-path-per-line) | Per-file scope silenced too much; replaced by per-rule TSV with `rule-id = *` and 90-day expiry. `/tmp/agency-research/PRE_COMMIT.md:115` | Use per-rule from day one. |
| `FM_TOOLCHAIN` env var to select legacy vs flexible linter | Dual-mode created uncertainty about which tool produced gating diagnostics. Retired by Task 054 (`/tmp/agency-research/MAINTENANCE.md:86`). | Don't ship dual-mode linters. Pick one toolchain. |
| Inline T3 fixes during coherence runs | Structural changes (duplicate `task_id` resolution, section renames) touch multiple files including reciprocal references and `tasks/readme.md` — too risky inline (`/tmp/agency-research/MAINTENANCE.md:249-256`). Filed as Tasks instead. | Mechanical changes ≠ mechanical scope. Repair-tier classification (§1.5) is the gate. |

---

## 10. Friction-root-cause taxonomy (worth direct copy)

Agency's `research/friction-pattern-synthesis/output/SPEC.md:97-106` ships an **8-category root-cause taxonomy**:

1. **Spec-without-validator** — written rule, no mechanical enforcement.
2. **Reciprocity drift** — forward link present, backward link missing or stale.
3. **Two-source-of-truth drift** — same fact in two files, diverging silently.
4. **Parallel-dispatch worktree inconsistency** — concurrent branches editing the same artefact.
5. **Pre-existing baseline errors** — fix-on-top blocked by ambient governance failures (solved by maintenance-bypass §8.4).
6. **Prompt-ambiguity** — research/prompt slug equality rule violated, snapshot rule violated.
7. **Schema-contract drift** — frontmatter validator and template silently disagree.
8. **Structural-bloat tension** — readme proliferation, nested-folder syndrome.

**All eight map to the-agency-system.** Each could become an FL2 trigger or a `bin/agency-lint` rule. This taxonomy is the highest-leverage single artefact to port from agency — it's the corpus-level pattern catalogue.

**Action:**
- Quote this taxonomy verbatim in `Plan/138-frustration-log-protocol/spec.md` as the trigger-category reference.
- Add to VOCABULARY as a new section (or a `Plan/_research/friction-taxonomy.md` companion).

---

## 11. Side findings (out of scope but worth flagging)

- **Manifest version drift** in this repo: `.claude-plugin/plugin.json` has `version: "0.1.0-dev"`; `tests/smoke/test_manifest.py:15` asserts `"0.1.0"`. Discovered while verifying the L1 harness for the VOCABULARY work. Not part of alignment; file as a separate issue (Spec 020 / Phase 0b finish).
- The L1 harness as shipped (PR #127) works exactly as VOCABULARY §3 documents: `harness_mcp()` boots, `list_tools()` returns 172 tools, `list_skills()` returns 58 paths, `dispatch_skill('lyric-writer')` resolves to `skills/music/lyric-writer/SKILL.md`, `call_tool(mcp, 'health_check', {})` returns `ok=True`.
- Agency cloned at commit `da099884b23dec09fb44b6dfbcdc15f209e1b8f9` (default branch `main`, 2026-05-18). `Plan/SOURCES.md` lists `claude/agency-plugin-refactor-PgMQ4` as the pin; if specs 010/012/013/015/016/021 fetch from agency, ensure they use the pinned branch, not main.
- Agency has 74 SKILL.md files across 76 skill dirs (2 dirs missing SKILL.md). the-agency-system has 58 skills today and adds 28+10 in Phase 7 Specs 015 + 021 — landing at ~96 skills. Comparable scale.

---

## 12. Recommended PR sequence (post-current-PR)

Drafted as separate small PRs so each can be reviewed independently:

1. **PR A — VOCABULARY canon extensions** (~30 min):
   - Add §3.1 frontmatter-conventions table (cite `summary`, `slug`, `skill_kind`).
   - Add §4.2 `skill_kind` 9-value enum.
   - Add §5.1 vendor-prefix imports.
   - Add §6.1 repair-authority tiers (T1/T2/T3/T4).
   - Add §7.1 content tiers (T1/T2/T3 — distinct from §6.1).

2. **PR B — Spec 134 (plan-adr-convention) rewrite** (~1 hr):
   - Adopt MADR 4.0.0 frontmatter + body shape verbatim from `/tmp/agency-research/decisions/0005-*.md`.
   - Add falsifier-trigger audit cadence.
   - Add T4-immutability + successor-amendment rule.
   - The mirror-deprecation decision was applied directly (mirror tree removed) in lieu of seeding an ADR — Jules' implicit-ADR sweep covers the formalisation.

3. **PR C — Spec 138 (frustration-log) update** (~30 min):
   - Add §1 8-category root-cause taxonomy.
   - Add structural-bloat automatic FL2 trigger.
   - Add WARN→STRICT toggle (`FM_FL_DECLARATION_STRICT=1` analogue).

4. **PR D — Spec 015 + 016 (skill catalogues)** (~1 hr):
   - Required SKILL.md frontmatter: `slug`, `summary`, `skill_kind`, `skill_target_agents`.
   - Body sections: `## What`, `## When to use`, `## How to use`, `## References`, `## Compatibility`.
   - Adopt DOT graphs + Red Flags tables for discipline-kind skills.

5. **PR E — Delete `Plan/phase-N-*/specs/` mirrors** (~30 min, depends on PR B's ADR):
   - Replace each mirror with a one-line table linking to the canonical `Plan/<NNN>-*/spec.md`.
   - Remove duplicate files; preserve canonical specs.
   - Validate that all phase READMEs still resolve their sub-spec references.

6. **PR F — `.githooks/pre-commit` + `bin/agency-lint`** (~2 hr, Phase 8):
   - Single delegate hook (§8.1).
   - 4-6 lint sub-commands (`manifest-coverage`, `anchor-traceability`, `skill-schema`, `adr-validate`, `frontmatter-reciprocity`).
   - Per-rule waiver TSV (§8.3).
   - Maintenance-bypass mode (§8.4).

7. **PR G — Path B vision spec update** (`Plan/harness/restructure/spec.md`, ~30 min):
   - `_base/conventions.py` carries: `skill_kind` enum, `summary` required field, T1/T2/T3 content tiers, T1/T2/T3/T4 repair tiers, reciprocity rules, falsifier-trigger types.

---

## 13. Summary

**Top 5 highest-leverage adoptions:**

1. **MADR 4.0.0 ADR ledger** at `Plan/decisions/NNNN-<slug>.md` with falsifier triggers and successor-amendment-only immutability — completes Spec 134.
2. **8-category friction root-cause taxonomy** copied verbatim into Spec 138 — single most valuable single artefact in agency.
3. **`summary:` frontmatter field as universal token-saving lever** — read before opening any body.
4. **T1/T2/T3 content tier ladder** — directly maps to harness L3 progressive-disclosure goal.
5. **Delete the `Plan/phase-N-*/specs/` mirrors** — agency's "no duplication, reciprocity-by-validator" rule is the canonical answer.

**Top 3 anti-patterns to avoid:**

1. **Over-mechanised linter sprawl** (~30 separate scripts) — consolidate behind `bin/agency-lint`.
2. **Heavy bootstrap-before-anything mandate** (`install.sh + tools/check-governance.sh` before any read/write) — keeps Claude Code on Web users out.
3. **Mirror copies inside phase folders** — silently drifts (this PR already hit it on top-level vs `phase-5/specs/` 122/123/124).

**This research informs:** `Plan/harness/VOCABULARY.md` (§§3.1, 4.2, 5.1, 6.1, 7.1 additions), `Plan/phase-8-operational-hardening/specs/134-plan-adr-convention/spec.md`, `Plan/138-frustration-log-protocol/spec.md`, `Plan/phase-7-domain-handler-completion/specs/015-novel-skills-catalogue/spec.md`, `Plan/phase-7-domain-handler-completion/specs/016-agentic-handlers-and-skills/spec.md`, `Plan/harness/restructure/spec.md`. PR sequence in §12 sequences the adoptions.
