---
spec_id: 016
slug: agentic-handlers-and-skills
status: ready
owner: jules
depends_on: [002, 003, 008, 009]
affects:
  - servers/agency-mcp/src/agency_mcp/handlers/agentic/__init__.py
  - servers/agency-mcp/src/agency_mcp/handlers/agentic/specs.py
  - servers/agency-mcp/src/agency_mcp/handlers/agentic/plans.py
  - servers/agency-mcp/src/agency_mcp/handlers/agentic/workflows.py
  - servers/agency-mcp/src/agency_mcp/handlers/agentic/research.py
  - servers/agency-mcp/src/agency_mcp/handlers/agentic/ralph.py
  - servers/agency-mcp/src/agency_mcp/handlers/agentic/confidence.py
  - servers/agency-mcp/src/agency_mcp/handlers/agentic/_state.py
  - servers/agency-mcp/src/agency_mcp/handlers/agentic/_envelope.py
  - servers/agency-mcp/src/agency_mcp/server.py
  - skills/agentic/
  - tests/unit/agentic/__init__.py
  - tests/unit/agentic/test_specs_validate.py
  - tests/unit/agentic/test_envelope.py
  - tests/unit/agentic/test_dry_run.py
  - tests/unit/agentic/test_return_plan.py
  - tests/unit/agentic/test_skills_present.py
  - Plan/016-agentic-handlers-and-skills/references/agentic-tool-catalog.md
source-repos:
  - agency @ claude/agency-plugin-refactor-PgMQ4
  - superpowers-marketplace @ main
estimated_jules_sessions: 2
domain: agentic
wave: C
---

> **Jules: read `Plan/JULES_PROTOCOL.md` before starting.** Run gates 1→4 in order:
> (1) Confidence ≥ 0.90, (2) TDD Red-Green-Refactor, (3) Evidence pasted under `## Evidence`, (4) Self-Review answered.
> Branch: `Master` (default base for fresh specs post-Wave-A; see JULES_PROTOCOL.md §3). Only modify paths under `affects:` below.
> Source repos under `source-repos:` are clone-and-read-only into `~/work/vendor/`; never commit them.
> If anything is ambiguous, open a draft PR labelled `[BLOCKED: clarification]` and stop — do not guess.

# Spec 016 — Agentic Handlers and Skills

## Why

The plugin's spec-driven workflow only works if its operational primitives —
spec validation, plan tracking, workflow decomposition, research brief
rendering, Ralph file generation, and pre-implementation confidence gating —
are first-class MCP tools, not ad-hoc skill prose. The embedded
agentic-orchestration brief (`references/agentic-tool-catalog.md`, distilled from
upstream agent `acee154f8dd7033bf`) enumerates **32 tools across 6 modules**
(`specs`, `plans`, `workflows`, `research`, `ralph`, `confidence`) that
constitute the agentic surface. Each tool is either decidable (no LLM) or
schema-bounded, which is what lets the agentic loop run unattended.

Alongside the tools, the unified plugin must ship the corresponding **skill
catalogue** Jules and the human reach for from the slash menu: the full
`sc-*` (~39), `superpowers-*` (~15), `spec-skill`, `ralph-skill`,
`prompt-optimizer`, and `research-prompt-optimizer` skills already curated in
the `agency` source repo. Without spec 016 the tools have no UI and the
spec-driven workflow stays prose-bound. With spec 016 the bitwize-music
"skills are the UI; tools are decidable primitives" precedent generalises to
agentic work.

## Done When

- [ ] All 32 agentic tools enumerated in `references/agentic-tool-catalog.md` §1 are registered on `create_mcp()` and tagged `tags={"domain:agentic"}`.
- [ ] `python -c "from agency_mcp.server import create_mcp; m=create_mcp(); print(sorted(t.name for t in m._tools.values() if 'domain:agentic' in (t.tags or set())))"` lists exactly 32 names.
- [ ] Every **stateful** agentic tool (per catalog §3.1) accepts `dry_run: bool = False`. When `dry_run=True` it returns `{ok: true, data: {would_apply, diff, warnings}, artefacts_written: []}` — no filesystem mutation, no SQLite write, no lock acquisition.
- [ ] Every **orchestration** tool (per catalog §3.2 — `workflow_decompose`, `ralph_render`, `research_brief_render`, `spec_derive_artifact`) accepts `return_plan: bool = False` and, when `True`, returns an `OrchestrationPlan = {steps:[{tool, args, expected_artefacts}], cost_estimate, side_effects}`.
- [ ] Every agentic tool returns the shared `ToolResult` envelope `{ok, data, warnings, artefacts_written, next_suggested_tools}` (catalog §3.3) — verified by a smoke test that instantiates each tool with sentinel args and asserts the response shape.
- [ ] `spec_validate("Plan/004-music-handlers-port/spec.md")` returns `{ok: true, data: {findings: [...]}}` with BCP-14 and Gherkin findings classified by rule.
- [ ] Roughly 60 agentic skills live under `skills/agentic/` — at minimum: `spec-skill`, `ralph-skill`, `prompt-optimizer`, `research-prompt-optimizer`, every `sc-*` skill from `agency`, every `superpowers-*` skill from `agency` (which is the superset of `superpowers-marketplace`). Each `SKILL.md` has its `name:` frontmatter rewritten to drop any vendor prefix.
- [ ] `pytest -x tests/unit/agentic/` exits 0.
- [ ] `ruff check servers/agency-mcp/src/agency_mcp/handlers/agentic/` exits 0.
- [ ] No reference to upstream paths (`~/.claude/`, `vendor/`, `agency/skills/`) remains in skill bodies under `skills/agentic/` — verified by `rg`.

## Source clones (run first)

```bash
git clone --depth=1 --branch=claude/agency-plugin-refactor-PgMQ4 \
  https://github.com/netzkontrast/agency.git \
  ~/work/vendor/agency

git clone --depth=1 \
  https://github.com/obra/superpowers-marketplace.git \
  ~/work/vendor/superpowers-marketplace
```

If either clone fails: open draft PR `[BLOCKED: verify-source-url]` per
`Plan/SOURCES.md`. Per Explore the 15 `superpowers-*` skills in
`superpowers-marketplace` are already a subset of those in `agency`, so the
marketplace clone is for cross-verification only — no skill should be copied
out of it.

## Files

- **Create**:
  - `servers/agency-mcp/src/agency_mcp/handlers/agentic/__init__.py` — exports `register_agentic_handlers(mcp)`.
  - `servers/agency-mcp/src/agency_mcp/handlers/agentic/specs.py` (6 tools per catalog §1.1).
  - `servers/agency-mcp/src/agency_mcp/handlers/agentic/plans.py` (7 tools per §1.2).
  - `servers/agency-mcp/src/agency_mcp/handlers/agentic/workflows.py` (5 tools per §1.3).
  - `servers/agency-mcp/src/agency_mcp/handlers/agentic/research.py` (5 tools per §1.4).
  - `servers/agency-mcp/src/agency_mcp/handlers/agentic/ralph.py` (5 tools per §1.5).
  - `servers/agency-mcp/src/agency_mcp/handlers/agentic/confidence.py` (4 tools per §1.6).
  - `servers/agency-mcp/src/agency_mcp/handlers/agentic/_envelope.py` — shared `ToolResult`, `OrchestrationPlan`, `Statement`, `GherkinScenario`, `ValidationReport`, `FindingsReport`, `ConfidenceScore` Pydantic models.
  - `servers/agency-mcp/src/agency_mcp/handlers/agentic/_state.py` — SQLite cache helpers + file-lock primitives mirroring `tools/fm/edit.py`.
  - `skills/agentic/<~60 skill folders>/SKILL.md` — ported from `vendor/agency/skills/{spec-skill,ralph-skill,prompt-optimizer,research-prompt-optimizer,sc-*,superpowers-*}`.
  - `tests/unit/agentic/__init__.py` + 5 test modules listed in `affects:`.
- **Modify**:
  - `servers/agency-mcp/src/agency_mcp/server.py` — add `from .handlers.agentic import register_agentic_handlers; register_agentic_handlers(mcp)` inside `register_all(mcp)`.
- **Move / Delete**: none. Vendor sources stay in `~/work/vendor/`.

## Approach

1. **Gate 1 — Confidence.** Read `Plan/000-overview.md` §2.1 (FastMCP construction, snake_case naming, response shape, `dry_run`, `ToolResult`), §2.2 (skill frontmatter), §2.3 (skill auto-namespacing). Read `references/agentic-tool-catalog.md` end-to-end — that file is the authoritative tool catalog. Confirm no `handlers/agentic/` modules already exist (`rg -l 'domain:agentic' servers/`). Confirm spec 009 has shipped `handlers/shared/` (this spec depends on `shared_load_override` for skill body resolution and on the `ToolResult` envelope convention). Cite the commands in the PR `## Confidence` table.
2. **Clone sources.** Run both clone commands. `ls ~/work/vendor/agency/skills/ | wc -l` should report ≥120; `ls ~/work/vendor/superpowers-marketplace/skills/ | wc -l` should report 15.
3. **Build the envelope first.** Author `_envelope.py` with Pydantic models. Every model used by the catalog (`ToolResult`, `OrchestrationPlan`, `ValidationReport`, `FindingsReport`, `Statement`, `GherkinScenario`, `Plan`, `Task`, `WorkflowPlan`, `IntentYAML`, `AuditReport`, `ConfidenceScore`, `Hit`, `Ref`) is defined here so the 6 handler modules import them rather than redefining.
4. **Author 6 handler modules per catalog §1.1–§1.6.** Tool names verbatim from the catalog (already snake_case `<domain>_<verb>_<object>` because the catalog uses the `agentic` domain prefix implicitly — register them with the literal names in the catalog, prefixed `agentic_` ONLY where the catalog name would collide with a shared/music/novel tool; per cross-check, none collide, so keep the catalog names verbatim: `spec_validate`, `plan_init`, `workflow_decompose`, `research_brief_render`, `ralph_render`, `confidence_check`, …). Every `@mcp.tool(...)` decoration carries `tags={"domain:agentic"}` and a docstring ≤120 chars (overview §2.1.2).
5. **Honour `dry_run` and `return_plan`.** Wire `dry_run` on every stateful tool (catalog §3.1 list); wire `return_plan` on the four orchestration tools (catalog §3.2). The smoke test in step 8 below asserts both.
6. **State persistence.** `_state.py` initialises `~/.agency-system/agentic/{plans,workflows,specs,research,ralph,cache,locks}/`. Markdown + frontmatter is the source of truth; `cache/index.db` is rebuildable. Schemas per catalog §2.
7. **Port skills.** From `vendor/agency/skills/`, copy each of these folders verbatim into `skills/agentic/<same-folder-name>/` — preserve `SKILL.md`, any `references/`, any nested files:
   - `spec-skill`, `ralph-skill`, `prompt-optimizer`, `research-prompt-optimizer`.
   - All `sc-*` folders (~39: `sc-analyze`, `sc-brainstorm`, `sc-build`, …, `sc-workflow`).
   - All `superpowers-*` folders (~15: `superpowers-tdd`, `superpowers-writing-plans`, …, `superpowers-using-superpowers`).
   For each ported `SKILL.md`, rewrite the `name:` frontmatter field to the bare skill slug (drop any vendor namespace) so the auto-namespacing rule in overview §2.3 makes it `/agency-system:<slug>`. Run `rg '~/.claude/|vendor/|agency/skills/' skills/agentic/` afterwards and rewrite or remove any hits.
8. **Embed the brief.** Commit `references/agentic-tool-catalog.md` (already authored alongside this spec). It is the single source agency-mcp implementers cite — do not paraphrase it elsewhere.
9. **TDD — Gate 2.** RED: write `test_envelope.py` (every tool returns `ToolResult` shape), `test_dry_run.py` (every stateful tool short-circuits with `dry_run=true`), `test_return_plan.py` (every orchestration tool returns `OrchestrationPlan` with `return_plan=true`), `test_specs_validate.py` (`spec_validate` on `Plan/004-music-handlers-port/spec.md` returns `ok=true` with structured findings), `test_skills_present.py` (`skills/agentic/spec-skill/SKILL.md`, `skills/agentic/sc-implement/SKILL.md`, `skills/agentic/superpowers-tdd/SKILL.md` all exist with parseable frontmatter). Watch each fail before implementing. GREEN: implement modules + port skills. REFACTOR: extract per-module `register(mcp)` boilerplate into a small helper if it does not weaken type-checking.
10. **Gate 3 — Evidence.** Paste in PR body: `pytest -x tests/unit/agentic/`, the tool-count `python -c ...` output, `ls skills/agentic/ | wc -l`, `rg '~/.claude/|vendor/' skills/agentic/` (must be empty), and a transcript of `spec_validate("Plan/004-music-handlers-port/spec.md", dry_run=true)` returning `ok=true`.
11. **Gate 4 — Self-Review.** Answer the three protocol questions. Specifically flag any tool kept out of scope (e.g. catalog §1.4 `research_brief_audit` if LLM unavailable — note `warnings: ["model_unavailable"]` per catalog §3.4 is acceptable) and any skill that did not port cleanly (with rationale).

## Acceptance (Gherkin)

```gherkin
# anchor: 016.1
Scenario: spec_validate returns structured findings under dry_run
  Given the agentic surface is registered on the FastMCP instance
  And the file Plan/004-music-handlers-port/spec.md exists
  When the caller invokes spec_validate(path="Plan/004-music-handlers-port/spec.md", dry_run=true)
  Then the result envelope has ok=true
  And data.would_apply is false
  And data.findings is a list of {rule, locator, msg} objects
  And warnings is an empty list
  And artefacts_written is an empty list

# anchor: 016.2
Scenario: Every agentic tool carries the domain:agentic tag and the ToolResult envelope
  Given the agentic handlers are registered
  When the smoke test iterates mcp._tools.values() filtered by "domain:agentic" in tags
  Then the count equals 32
  And every tool's awaitable return value validates against the ToolResult Pydantic model

# anchor: 016.3
Scenario: Stateful agentic tools honour dry_run
  Given the agentic handlers are registered
  And a stateful tool listed in references/agentic-tool-catalog.md §3.1
  When the caller invokes the tool with dry_run=true and otherwise-mutating arguments
  Then no file under ~/.agency-system/agentic/ is created or modified
  And the response data contains a "would_apply" key and a "diff" key

# anchor: 016.4
Scenario: Orchestration tools return an OrchestrationPlan under return_plan
  Given the agentic handlers are registered
  When the caller invokes workflow_decompose(prd_path="...", strategy="systematic", depth="normal", return_plan=true)
  Then the response data validates against the OrchestrationPlan Pydantic model
  And data.steps is a non-empty list of {tool, args, expected_artefacts}
  And no workflow markdown file is written

# anchor: 016.5
Scenario: The full agentic skill catalogue is ported under skills/agentic/
  Given the source repos have been cloned read-only into ~/work/vendor/
  When the operator runs `ls skills/agentic/`
  Then the listing includes "spec-skill", "ralph-skill", "prompt-optimizer", "research-prompt-optimizer"
  And the listing includes "sc-implement", "sc-workflow", "sc-confidence-check"
  And the listing includes "superpowers-tdd", "superpowers-writing-plans", "superpowers-using-superpowers"
  And no SKILL.md body under skills/agentic/ contains the substring "vendor/" or "~/.claude/"
```

## Out of scope

- Authoring novel domain prose for the agentic skills (the ported `SKILL.md` bodies stay as-is from `agency`).
- Wiring the agentic tool classifications (`eager` / `deferred` / `background`) into `codemode/manifest.json` — that belongs to spec 008.
- Building cross-domain orchestration (`agency_route_request`) — out of scope; if/when needed it becomes a new spec.
- Implementing the SQLite migrations for `cache/index.db` beyond initial schema + drop-and-rebuild — full migration tooling is a follow-up if needed.
- Hooks integration for agentic write-paths (spec 017 owns hook policy).
- State migration of any legacy agentic artefacts (none exist pre-1.0.0).

## References

- `Plan/JULES_PROTOCOL.md` (gates 1–4, §4 source-repo discipline)
- `Plan/000-overview.md` §2.1.1 (snake_case tool naming), §2.1.6 (response shape cap 20), §2.1.7 (`dry_run`), §2.1.8 (`return_plan`), §2.1.9 (`ToolResult`), §2.2 (skill frontmatter L1/L2), §2.3 (skill auto-namespacing)
- `Plan/SOURCES.md` (agency + superpowers-marketplace clone commands)
- `Plan/016-agentic-handlers-and-skills/references/agentic-tool-catalog.md` (32-tool catalog — authoritative; embedded from upstream agent `acee154f8dd7033bf`)
- Spec dependency: `Plan/009-shared-handlers/spec.md` (`shared_load_override`, `ToolResult` shape precedent)
- Vendor source (read-only): `~/work/vendor/agency/skills/{spec-skill,ralph-skill,prompt-optimizer,research-prompt-optimizer,sc-*,superpowers-*}/SKILL.md`
