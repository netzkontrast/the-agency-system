---
spec_id: 021
slug: novel-prompt-builder-family
status: ready
owner: jules
depends_on: [011, 012, 013, 015]
affects:
  - servers/agency-mcp/pyproject.toml
  - servers/agency-mcp/src/agency_mcp/handlers/novel/prompts.py
  - servers/agency-mcp/src/agency_mcp/handlers/novel/__init__.py
  - skills/novel/prompts/world-prompt-builder/SKILL.md
  - skills/novel/prompts/character-prompt-builder/SKILL.md
  - skills/novel/prompts/scene-prompt-builder/SKILL.md
  - skills/novel/prompts/storyform-prompt-builder/SKILL.md
  - skills/novel/prompts/throughline-prompt-builder/SKILL.md
  - skills/novel/prompts/bridge-prompt-builder/SKILL.md
  - skills/novel/prompts/chapter-prompt-builder/SKILL.md
  - skills/novel/prompts/revision-prompt-builder/SKILL.md
  - skills/novel/prompts/theme-prompt-builder/SKILL.md
  - skills/novel/prompts/relationship-prompt-builder/SKILL.md
  - Plan/021-novel-prompt-builder-family/references/prompt-builder-methods.md
  - tests/unit/novel/test_prompts.py
source-repos:
  - agency @ claude/agency-plugin-refactor-PgMQ4
estimated_jules_sessions: 2
domain: novel
wave: B
---

> **Jules: read `Plan/JULES_PROTOCOL.md` before starting.** Run gates 1→4 in order:
> (1) Confidence ≥ 0.90, (2) TDD Red-Green-Refactor, (3) Evidence pasted under `## Evidence`, (4) Self-Review answered.
> Branch: `Master` (default base for fresh specs post-Wave-A; see JULES_PROTOCOL.md §3). Only modify paths under `affects:` below.
> Source repos under `source-repos:` are clone-and-read-only into `~/work/vendor/`; never commit them.
> If anything is ambiguous, open a draft PR labelled `[BLOCKED: clarification]` and stop — do not guess.

# Spec 021 — Novel Prompt-Builder Family

## Why

Per the embedded prompt-builder methods brief (12 method families across 8 sources — Anthropic long-context, Sudowrite Beat-then-prose, NovelCrafter Entity-hydration, Lee CHI 2024 sentence-granularity, Weaver hierarchical chains, DraftSmith psycho-model serialization, K.M. Weiland Q-audit, Matt Bell three-pass discipline), novelists drafting on top of an LLM benefit from **purposeful, entity-grounded prompts derived from each project entity** (World, Character, Scene, Storyform, Throughline, Bridge, Chapter, Revision, Theme, Relationship). Hand-rolled prompts drift, miss source-of-truth fields, and degrade composition coherence over a long manuscript. This spec ships **10 MCP tools** in `handlers/novel/prompts.py` AND **10 sibling skills** in `skills/novel/prompts/` with a `composes_with:` DAG (cross-domain example: `scene-prompt-builder` composes with character + world + throughline + bridge). All 10 builders are **read-only, idempotent, source-traceable**. The Wave B novel domain is incomplete without them: Spec 015 ships `chapter-writer` but the chapter-writer needs a prompt — and the only way to make that prompt reproducible across a 90-chapter manuscript is to generate it from the entity store, not from human memory. This spec sits cleanly on top of the novel state model (Specs 010–014) — it ADDS read capability without mutating state, so it can ship independent of Spec 015's main catalogue if needed.

## Done When

- [ ] `handlers/novel/prompts.py` exists with **10 builder tools** registered, all with the uniform signature:
  ```python
  def novel_build_<entity>_prompt(
      work_id: str,
      entity_id: str,
      mode: Literal["draft", "revise", "research"] = "draft",
      dry_run: bool = False,
  ) -> dict
  ```
  returning `{prompt: str, sources: list[dict], composes_with: list[str], preview: str, mode: str}`.
- [ ] The 10 entities are exactly: `world`, `character`, `scene`, `storyform`, `throughline`, `bridge`, `chapter`, `revision`, `theme`, `relationship` (matching the brief's table).
- [ ] All 10 tools are **read-only** (do not mutate `state.json`, `.ncp.json`, or any file under `novels/`). Verified by a test that snapshots all relevant files, calls every builder, and asserts no mtime change.
- [ ] All 10 tools are **idempotent**: calling the same tool with the same `(work_id, entity_id, mode)` twice in a row returns byte-identical `prompt` and `sources` fields. Verified by `test_idempotency` per builder.
- [ ] **`preview` is ≤ 200 tokens** (per Lee CHI 2024 sentence-granularity from the brief). Verified by a test that runs `tiktoken` on `preview` and asserts ≤ 200.
- [ ] **Source traceability**: every fragment injected into `prompt` is named in `sources` as `{type, id, version}`. Verified by `test_source_traceability` — strips the prompt's XML tags, grep-asserts each fragment's id is in `sources`.
- [ ] **`composes_with` DAG resolves with no cycles**. Verified by `test_composes_with_dag_acyclic` doing a topological sort over the 10 builders' declared `composes_with` lists.
- [ ] `dry_run=True` returns `{would_apply, diff, warnings}` shape per overview §2.1 #7. Specifically `would_apply.composes_with` lists which sibling builders would be invoked, without actually invoking them.
- [ ] **10 SKILL.md files** under `skills/novel/prompts/` each pass the 10-item QC checklist (Spec 015's `tools/skill_qc_lint.py`). Each declares its `composes_with:` DAG in frontmatter — the skill DAG mirrors the tool DAG.
- [ ] `pytest -x tests/unit/novel/test_prompts.py` exits 0.
- [ ] `Plan/021-novel-prompt-builder-family/references/prompt-builder-methods.md` exists and is cited from `handlers/novel/prompts.py` module docstring and from every prompt-builder SKILL.md `skill_references_research` field.

## Source clones (run first)

```bash
git clone --depth=1 --branch=claude/agency-plugin-refactor-PgMQ4 \
  https://github.com/netzkontrast/agency.git \
  ~/work/vendor/agency
```

Read `~/work/vendor/agency/skills/novel-architect-{scene,structure,world,character}/SKILL.md` to verify the entity-shape assumptions in the brief match the data Spec 010's on-disk layout actually produces. Read `~/work/vendor/agency/skills/ncp-author/upstream/schema/ncp-schema.json v1.3.0` for the exact field names used in `<voice>`, `<world>`, `<beat>`, `<task>` block hydration.

## Files

- **Create**:
  - `handlers/novel/prompts.py` — 10 tool functions + a `_compose(parent_id, child_ids, work_id)` internal helper that calls sibling builders without infinite recursion (the topo-sorted call graph from the brief).
  - 10 SKILL.md files under `skills/novel/prompts/<entity>-prompt-builder/SKILL.md` — frontmatter declares `composes_with:` matching the tool's `composes_with` output; body documents the `mode` switch and the `<voice>` / `<world>` / `<beat>` / `<task>` XML skeleton (per Anthropic long-context, Source 1 of the brief).
  - `tests/unit/novel/test_prompts.py` — covers: byte-identical idempotency, dry-run plan-only, composition DAG acyclicity, source traceability, ≤ 200-token preview, read-only mtime invariance.
- **Modify**:
  - `handlers/novel/__init__.py` — extend to call `register_novel_prompt_handlers(mcp)`.
- **Do not touch**: any other `handlers/novel/*.py` (Specs 011/013/014); the 28+4 main catalogue skills (Spec 015); `lib/dramatica/`, `lib/ncp/` (Spec 012); music / jules / agentic anything.

## Approach

1. **Gate 1 — Confidence (target ≥ 0.90).** Cite: `rg -l 'novel_build_.*_prompt' servers/` returns nothing (no duplicate); `novel_coherence_check` from Spec 013 is importable (entity reads depend on storyform being structurally valid); Spec 015's `tools/skill_qc_lint.py` exists; `tiktoken` is in `pyproject.toml` or already used by Spec 011 (verify with `pip show tiktoken`). Root cause / contract: novel domain needs 10 reproducible prompt-generators for the entity store.
2. **Read the methods brief end-to-end.** `references/prompt-builder-methods.md` is the authority. The brief's 8-row method survey table, 10-row builder family table, signature lock, and 5-point reflection section govern every authoring decision. Authoring deviates from the brief only via `[BLOCKED: clarification]`.
3. **TDD — Gate 2, RED.** Author `tests/unit/novel/test_prompts.py` first with these tests (one per builder × 5 properties = 50 tests minimum):
   - `test_<entity>_builder_idempotent` — call twice, assert byte-identical `prompt` and `sources`.
   - `test_<entity>_builder_dry_run` — call with `dry_run=True`, assert `{would_apply, diff, warnings}` shape and that no entity file mtime changes.
   - `test_<entity>_builder_preview_token_cap` — `tiktoken` length of `preview` ≤ 200.
   - `test_<entity>_builder_source_traceability` — every id appearing in the prompt's XML blocks appears in `sources`.
   - `test_<entity>_builder_composes_with_matches_dag` — the returned `composes_with` list matches the brief's table row for this entity.
   Plus integration tests: `test_dag_acyclic` (topo-sort), `test_read_only_mtime_invariance` (snapshot all files, call all 10 builders, assert no change), `test_scene_builder_composition` (the brief's canonical example: scene composes with character + world + throughline + bridge).
   Run pytest — all must fail with `ModuleNotFoundError`. Paste tail into PR.
4. **GREEN — implement the 10 builders.** Each builder reads its entity from the appropriate source-of-truth file:
   - `world-prompt-builder` ← `world.md` + `.ncp.json::world`. Output: `<world>` block. Composes with: none (leaf).
   - `character-prompt-builder` ← `cast.md` + `.ncp.json::players[entity_id]`. Output: 3-line voice header (DraftSmith psycho-model serialization, Source 6 of the brief) wrapped in `<voice>` block. Composes with: none (leaf).
   - `storyform-prompt-builder` ← `dramatica.md` + `.ncp.json::storyform`. Output: `<storyform>` block. Composes with: none (leaf).
   - `throughline-prompt-builder` ← `.ncp.json::throughlines[entity_id]`. Output: `<throughline>` block. Composes with: `["storyform-prompt-builder"]`.
   - `theme-prompt-builder` ← `.ncp.json::theme` + `dramatica.md`. Output: `<theme>` block. Composes with: `["storyform-prompt-builder"]`.
   - `relationship-prompt-builder` ← `.ncp.json::relationships[entity_id]` + `cast.md`. Output: `<relationship>` block. Composes with: `["character-prompt-builder"]` (one call per relationship endpoint).
   - `bridge-prompt-builder` ← `.ncp.json::storybeats[entity_id]`. Output: Q1–Q5 audit (K.M. Weiland, Source 7) wrapped in `<beat>` block. Composes with: `["throughline-prompt-builder"]`.
   - `scene-prompt-builder` ← `.ncp.json::moments[entity_id]` + `scenes/{entity_id}.md`. Output: `<voice>` + `<world>` + `<beat>` + `<task>` (Anthropic long-context skeleton, Source 1). Composes with: `["character-prompt-builder", "world-prompt-builder", "throughline-prompt-builder", "bridge-prompt-builder"]`.
   - `chapter-prompt-builder` ← `chapters/{entity_id}.md` + `.ncp.json::chapters[entity_id]`. Output: scene-stack + `<chapter_arc>`. Composes with: `["scene-prompt-builder", "theme-prompt-builder"]` (variadic in scenes).
   - `revision-prompt-builder` ← existing chapter draft + diff target. Output: `<pass>` (lens-of-the-day per Matt Bell three-pass, Source 8) + `<task>` + `<diff_target>`. Composes with: `["chapter-prompt-builder", "theme-prompt-builder"]`.
5. **`mode` switch.** Each builder accepts `mode ∈ {"draft", "revise", "research"}`. `mode` flips the `<task>` block only; entity hydration is identical across modes (Matt Bell, Source 8 — one builder per entity with a mode switch, not 3× builders). `draft` task: "Write the next prose for <entity>"; `revise` task: "Revise the existing draft against the diff target"; `research` task: "List the open research questions raised by this entity for the chapter-writer to surface."
6. **Idempotency discipline.** Per the brief's reflection §5: no timestamps in `prompt`, no UUIDs, no `dict` iteration order (sort all injected lists by id). The `sources` list is sorted by `(type, id, version)`. Test: `test_<entity>_builder_idempotent` re-imports the module after the first call (to defeat any process-local randomness).
7. **`_compose` helper + DAG enforcement.** Internal helper `_compose(parent_id: str, child_builder_ids: list[str], work_id: str, mode: str) -> list[str]` calls each child builder (cached per-call to avoid recomputation) and returns the assembled XML blocks. Walk uses memoization keyed by `(child_id, work_id, mode)`. Cycle detection: maintain a per-call visiting-set; raise `BuilderCycleError` if a child is encountered twice in the same call stack — the test `test_dag_acyclic` exercises a deliberately introduced cycle and asserts the error.
8. **`dry_run=True`** — returns `{would_apply: {prompt_size_estimate, composes_with}, diff: "<no-op: read-only>", warnings: []}` per overview §2.1 #7. Does not call `_compose`; computes the DAG transitively from the builder's declared `composes_with` and reports the list. Read-only invariance is unchanged (no file mtime change).
9. **Author the 10 SKILL.md files.** Each at `skills/novel/prompts/<entity>-prompt-builder/SKILL.md`. Frontmatter includes `composes_with:` (the same list the tool returns) and `skill_references_research: ["Plan/021-novel-prompt-builder-family/references/prompt-builder-methods.md"]`. Body follows the 5 mandatory sections (overview §2.2). `## How to use` documents the tool call signature with a worked example. Run `python tools/skill_qc_lint.py skills/novel/prompts/` and fix until exit 0.
10. **Wire registration.** `handlers/novel/__init__.py` extends to call `register_novel_prompt_handlers(mcp)`. All 10 tools tagged `tags={"domain:novel"}` per overview §2.1 #1. Docstrings ≤ 120 chars (overview §2.1 #2).
11. **REFACTOR.** With all 50+ tests green, extract the XML-block assembly into a `_render_xml_block(tag: str, body: str) -> str` helper; extract the entity-load logic into a `_load_entity(work_id, entity_kind, entity_id) -> dict` helper. Do not collapse the 10 builder functions into a dispatch dict — each is a distinct contract.
12. **Gate 3 — Evidence.** Paste under `## Evidence`: (a) `pytest -x tests/unit/novel/test_prompts.py` exit-zero tail, (b) `python tools/skill_qc_lint.py skills/novel/prompts/` exit-zero output, (c) `python -c "from agency_mcp.server import create_mcp; m = create_mcp(); print(sorted(t for t in m._tools if t.startswith('novel_build_') and t.endswith('_prompt')))"` showing all 10 names, (d) a sample `novel_build_scene_prompt(...)` output (just the `composes_with` and `preview` fields — ≤ 250 tokens of evidence), (e) a sample `novel_build_scene_prompt(..., dry_run=True)` showing the `{would_apply, diff, warnings}` shape.
13. **Gate 4 — Self-Review.** Three questions. Specifically flag: any builder where the brief's declared `composes_with` list proved insufficient (e.g. revision-builder also needing storyform-builder); any deviation from the byte-identical idempotency contract (must be hard-fixed, not papered over); any builder whose `preview ≤ 200` cap forced ugly truncation (open a `[BLOCKED: clarification]` if the cap is wrong, do not silently raise it).

## Acceptance (Gherkin)

```gherkin
# anchor: 021.1
Scenario: Scene-prompt-builder composition matches the brief's DAG
  Given a work with locked storyform and a populated cast
  And a moment moment-42 exists in .ncp.json::moments[]
  When the operator calls novel_build_scene_prompt(work_id="abc", entity_id="moment-42", mode="draft")
  Then the response.composes_with equals ["character-prompt-builder", "world-prompt-builder", "throughline-prompt-builder", "bridge-prompt-builder"]
  And the response.prompt contains "<voice>", "<world>", "<beat>", "<task>" XML blocks in that order

# anchor: 021.2
Scenario: Builders are byte-identical idempotent
  Given the same work and moment as above
  When the operator calls novel_build_scene_prompt(work_id="abc", entity_id="moment-42", mode="draft") twice
  Then both invocations return byte-identical response.prompt
  And both invocations return byte-identical response.sources
  And no file under novels/{author}/works/{genre}/{slug}/ has a changed mtime

# anchor: 021.3
Scenario: dry_run returns a no-op plan
  Given any work, entity, and mode
  When the operator calls novel_build_<entity>_prompt(..., dry_run=true)
  Then the response shape is {"would_apply": {"prompt_size_estimate": <int>, "composes_with": [<sibling-builder-ids>]}, "diff": "<no-op: read-only>", "warnings": []}
  And no sibling builder's heavy computation runs
  And no file mtime changes

# anchor: 021.4
Scenario: Preview is capped at 200 tokens
  Given any builder invocation with a fully-populated entity
  When the response.preview is measured with tiktoken
  Then the token count is ≤ 200

# anchor: 021.5
Scenario: Source traceability is complete
  Given a scene-prompt-builder response
  When every {type, id, version} in response.sources is checked against the prompt body
  Then every id referenced in <voice>, <world>, <beat>, or <task> is present in response.sources
  And no source-id appears in the prompt body that is NOT in response.sources
```

## Out of scope

- Authoring or modifying the 28+4 main novel skill catalogue (Spec 015 — zero file overlap with `skills/novel/prompts/`).
- New structural checks (Spec 013).
- New gates (Spec 014).
- Hooks integration (Spec 017).
- Music or jules prompt-builders (this spec is novel-only; the prompt-builder pattern may be revisited for music in a Wave C task but is not in this spec's scope).
- Mutating state from a builder (read-only is the spec's hard contract — any builder that writes is a bug, not a feature).
- Caching builder output across MCP lifetimes (per-call memoization in `_compose` is in scope; cross-call persistence is not — that would compromise idempotency under entity-edit churn).

## References

- `Plan/JULES_PROTOCOL.md` (gates 1–4, §4 source-repo discipline)
- `Plan/000-overview.md` §1 (target tree), §2.1 #1–#2 (tool naming + tags), §2.1 #6 (response shape token discipline), §2.1 #7 (`dry_run` contract), §2.2 (skill QC for the 10 SKILL.md files)
- `Plan/SOURCES.md` (agency clone command)
- `Plan/021-novel-prompt-builder-family/references/prompt-builder-methods.md` — **the methods brief this spec implements** (synthesised from agent `aa330f5c5a8989618`'s scheduled 12-source survey; Anthropic long-context, Sudowrite Beat-then-prose, NovelCrafter Entity-hydration, Lee CHI 2024, Weaver hierarchical chains, DraftSmith psycho-model, K.M. Weiland Q-audit, Matt Bell three-pass)
- Spec dependency: `Plan/013-novel-handlers-structural/spec.md` (structural validity precondition — builders compose against verified storyform slots)
- Spec dependency: `Plan/015-novel-skills-catalogue/spec.md` (`tools/skill_qc_lint.py` reused for the 10 prompt-builder SKILL.md files)
- Spec dependency: `Plan/012-dramatica-and-ncp-libs/spec.md` (`lib/ncp/` + `lib/dramatica/` consumed by entity loaders)
- Spec dependency: `Plan/011-novel-handlers-core/spec.md` (StateCache + on-disk entity layout)
- Spec sibling: `Plan/014-novel-gates-and-revision/spec.md` (`pre-drafting-check` should pass before any builder is meaningfully usable, but this is an operator discipline, not a code dependency — builders are read-only on whatever state exists)
- Vendor source (read-only): `~/work/vendor/agency/skills/novel-architect-{scene,structure,world,character}/SKILL.md` (entity-shape verification)
