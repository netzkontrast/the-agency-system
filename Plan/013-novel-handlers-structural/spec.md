---
spec_id: 013
slug: novel-handlers-structural
status: done
owner: jules
depends_on: [011, 012]
affects:
  - servers/agency-mcp/pyproject.toml
  - servers/agency-mcp/src/agency_mcp/handlers/novel/__init__.py
  - servers/agency-mcp/src/agency_mcp/handlers/novel/structure.py
  - servers/agency-mcp/src/agency_mcp/handlers/novel/characters.py
  - servers/agency-mcp/src/agency_mcp/handlers/novel/world.py
  - servers/agency-mcp/src/agency_mcp/handlers/novel/coherence.py
  - servers/agency-mcp/src/agency_mcp/handlers/novel/prose_analysis.py
  - servers/agency-mcp/src/agency_mcp/lib/prose_processing/__init__.py
  - servers/agency-mcp/src/agency_mcp/lib/prose_processing/readability.py
  - servers/agency-mcp/src/agency_mcp/lib/prose_processing/rhythm.py
  - servers/agency-mcp/src/agency_mcp/lib/prose_processing/pov.py
  - tests/unit/novel/__init__.py
  - tests/unit/novel/test_coherence.py
  - tests/unit/novel/test_structure.py
  - tests/unit/novel/test_prose_analysis.py
  - tests/fixtures/novel/          # ENTIRE SUBTREE — coherence + structure test fixtures (good_work.ncp.json, broken_work_<check>.ncp.json, etc.)
  - Plan/013-novel-handlers-structural/references/dramatica-decidability.md
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

# Spec 013 — Novel Handlers (Structural)

## Why

Structural integrity for novels = Dramatica coherence. `novel_coherence_check` is the sibling of bitwize's `album_coherence_check` and fans out over **11 decidable checks** (dynamic-pair reciprocity, KTAD coherence, throughline uniqueness, signpost ordering, MC Resolve ↔ Outcome ↔ Judgment, etc.) per the embedded Dramatica decidability brief — *"tools assert structure, skills assert meaning"*. Spec 011 ships the novel core (CRUD on works / chapters / scenes); Spec 012 ships the Dramatica navigator + NCP schema validator; this spec is what makes a novel *structurally falsifiable*. Without it, `pre-drafting-gate` (Spec 014) has nothing to gate on, prompt-builders (Spec 021) compose against unverified storyform slots, and Wave B ships a novel domain that cannot tell a well-formed work from a malformed one. It also adds the `structure`, `characters`, `world`, and `prose_analysis` handler modules, mirroring the four content surfaces a Dramatica-grounded novel exposes (storyform, players, world, prose).

## Done When

- [ ] All 5 handler modules under `servers/agency-mcp/src/agency_mcp/handlers/novel/` exist and import cleanly: `structure.py`, `characters.py`, `world.py`, `coherence.py`, `prose_analysis.py`.
- [ ] `register_novel_structural_handlers(mcp)` registers ~30 tools tagged `domain:novel` (counted by smoke test).
- [ ] `lib/prose_processing/{readability,rhythm,pov}.py` exist and export `analyze_readability(text) -> dict`, `analyze_rhythm(text) -> dict`, `scan_pov_violations(text, declared_pov) -> list[dict]`.
- [ ] `novel_coherence_check(work_id)` returns the brief's report shape: `{ok: false, violations: [{check, severity, at, expected, got, hint}], checks: {...}}` for a deliberately broken NCP fixture.
- [ ] All **11 decidable checks** from the brief have a unit test in `tests/unit/novel/test_coherence.py` (one `test_<check_name>_pass` and one `test_<check_name>_fail` each = 22 tests minimum).
- [ ] `novel_coherence_correct(work_id, autofix={"pair_reciprocity","slot_typing"}, dry_run=False)` flips mechanical issues and re-runs cleanly; `dry_run=True` returns `{would_apply, diff, warnings}` without writing.
- [ ] `pytest -x tests/unit/novel/test_coherence.py tests/unit/novel/test_structure.py tests/unit/novel/test_prose_analysis.py` exits 0.
- [ ] `rg -n 'duplicate.*ontology' servers/agency-mcp/src/agency_mcp/handlers/novel/` returns no hits (single source of truth: `lib/dramatica/navigator` from Spec 012).
- [ ] `Plan/013-novel-handlers-structural/references/dramatica-decidability.md` exists and is cited from every coherence handler docstring.

## Source clones (run first)

```bash
git clone --depth=1 --branch=claude/agency-plugin-refactor-PgMQ4 \
  https://github.com/netzkontrast/agency.git \
  ~/work/vendor/agency
```

Read-only. Inspect `~/work/vendor/agency/maintenance/schemas/narrative-ontology/ontology.json` (304 entries) and `~/work/vendor/agency/tools/dramatica-nav/validate.py` (the validator already enforcing frontmatter ↔ ontology agreement — reuse the algorithm, do not re-derive). Do not copy files in.

## Files

- **Create**:
  - `handlers/novel/structure.py` — storyform-internal checks (`novel_check_slot_fill`, `novel_check_throughline_partition`, `novel_check_crucial_element_placement`, `novel_check_resolve_outcome_judgment`, `novel_check_approach_concern`, `novel_check_mental_sex_problem_solving`, `novel_check_signpost_permutation`, plus accessors `novel_get_storyform`, `novel_get_throughline`, `novel_get_quad_menu`).
  - `handlers/novel/characters.py` — `novel_list_players`, `novel_get_player`, `novel_update_player_field` (writes back to `cast.md` frontmatter via Spec 011's StateCache), `novel_assign_archetype`, `novel_check_relationship_graph`.
  - `handlers/novel/world.py` — `novel_get_world`, `novel_list_world_entities`, `novel_check_world_consistency` (timeline + named-entity dedup).
  - `handlers/novel/coherence.py` — `novel_coherence_check(work_id)` orchestrator + 4 referential checks (`check_dynamic_pair_reciprocity`, `check_ktad_coverage`, `check_quad_completeness`, `check_storybeat_moment_refs`) + `novel_coherence_correct(work_id, autofix, dry_run)`.
  - `handlers/novel/prose_analysis.py` — `novel_analyze_readability`, `novel_analyze_rhythm`, `novel_scan_pov_violations`, `novel_extract_distinctive_phrases` (mirrors bitwize `extract_distinctive_phrases`).
  - `lib/prose_processing/__init__.py` + `readability.py` (textstat wrapper) + `rhythm.py` (sentence-length variance + clause-count) + `pov.py` (regex + parser scanning for declared-POV violations: 3rd-limited fixture seeing 1st-person interiors, etc.).
  - `tests/unit/novel/__init__.py` and `test_coherence.py` (11 decidable-check pass/fail pairs), `test_structure.py` (slot-fill + throughline partition + crucial-element placement), `test_prose_analysis.py` (readability ranges, rhythm metrics, POV violation flags).
- **Modify**:
  - `handlers/novel/__init__.py` (from Spec 011) — extend to call `register_novel_structural_handlers(mcp)` alongside the existing core registration.
- **Do not touch**: `lib/dramatica/`, `lib/ncp/` (owned by Spec 012); `handlers/novel/core.py` etc. (owned by Spec 011); music / jules / agentic anything.

## Approach

1. **Gate 1 — Confidence (target ≥ 0.90).** Cite: `rg -l 'novel_coherence_check' servers/` returns nothing (no duplicate); `fastmcp>=3.1.0` in `pyproject.toml` (overview §2.3); `lib/dramatica/navigator` exists from Spec 012 (`python -c "from agency_mcp.lib.dramatica import navigator; print(navigator)"`); `lib/ncp/validator` exists from Spec 012; `textstat` is available or listed in Spec 011's deps (verify with `pip show textstat`). Root cause: novel domain currently has CRUD but no structural falsifiability — this spec adds it.
2. **Clone source + read the brief.** Run the clone command. Read `references/dramatica-decidability.md` (embedded matrix + recommendations). Read `~/work/vendor/agency/skills/dramatica-vocabulary/references/dynamic-pairs-index.md` (75 pairs) and `~/work/vendor/agency/skills/dramatica-vocabulary/references/element-quads.md` (KTAD + 16 Variation Quads) to verify the navigator's pre-built indexes from Spec 012 match the source.
3. **TDD — Gate 2, RED.** Author `test_coherence.py` first. For each of the 11 decidable checks, write a `test_<check>_pass` (uses a known-good NCP fixture from `tests/fixtures/novel/good_work.ncp.json`) and a `test_<check>_fail` (uses `tests/fixtures/novel/broken_work_<check>.ncp.json` with one targeted mutation). Run pytest — all 22 must fail with `ModuleNotFoundError: agency_mcp.handlers.novel.coherence`. Paste the failing tail into the PR.
4. **GREEN — implement decidable checks.** Each check is a **one-function read against `lib/dramatica/navigator`** plus a small NCP traversal. Examples:
   - `check_dynamic_pair_reciprocity`: for every Element `e` in the storyform, look up `navigator.get_dynamic_pair(e.dynamic_pair_id)`, assert that the *other* member of the pair is also present and that its `dynamic` is the antipode of `e.dynamic`.
   - `check_ktad_coverage`: group Elements by `quad_id`, assert the set of `ktad_position` values per group is exactly `{K, T, A, D}` (no missing, no duplicate).
   - `check_signpost_permutation`: read `navigator.get_allowed_signpost_permutations(class_id, driver, limit)` (precompiled table in `lib/dramatica/data/`), assert the declared signpost ordering for each throughline is in the allowed set.
   - Full list and tool signatures in the brief's matrix.
5. **`novel_coherence_check` orchestrator.** Fans out the 11 checks in parallel-by-data (they are independent reads), merges into the **token-cheap report shape** from the brief (PASS-only checks have no `items` array; FAIL checks cap each item at ~120 chars; ontology ids not labels). Cap the response: a clean PASS in ~40 tokens; a 3-violation report in ~400 tokens. Test the report shape with `test_report_shape_clean_pass` and `test_report_shape_three_violations`.
6. **`novel_coherence_correct`.** Mechanical autofixes only: `pair_reciprocity` (flip the declared partner to the navigator's `dynamic_pair_id` target), `slot_typing` (coerce a slot's value to the right `kind` if it resolves uniquely). Must accept `dry_run: bool = False` per overview §2.1 #7. Refuse to autofix anything not in the explicit `autofix={...}` set.
7. **Prose analysis (`lib/prose_processing/`).** Thin wrappers, not new algorithms:
   - `readability.py` — wrap `textstat.flesch_reading_ease`, `textstat.gunning_fog`, `textstat.smog_index`; return `{flesch, fog, smog, grade_level, avg_sentence_length}`.
   - `rhythm.py` — compute per-sentence length variance, clause-count distribution, percentage of sentences ≥30 words (Bell red flag).
   - `pov.py` — for declared POV ∈ `{1st, 3rd_limited, 3rd_omniscient, 2nd}`, scan for violations (e.g. 3rd-limited fixture text containing "he didn't know that she was thinking..." — head-hop). Use a tiny rule set; return `[{line, snippet, violation_type, hint}]`.
8. **Wire registration.** `handlers/novel/__init__.py` extends with `register_novel_structural_handlers(mcp)` that imports the 5 new modules and calls each one's `register(mcp)`. All tools tagged `tags={"domain:novel"}` per overview §2.1 #1. Docstrings ≤120 chars (overview §2.1 #2).
9. **REFACTOR.** With all 22+ coherence tests green, extract the common "load NCP + navigator handle + accumulate violation" boilerplate into a `_check_runner(work_id, check_fn)` helper. Do not weaken type-checking; do not collapse the 11 check functions into a dispatch dict (Jules-readability > clever).
10. **Gate 3 — Evidence.** Paste under `## Evidence`: (a) `pytest -x tests/unit/novel/test_coherence.py` exit-zero tail, (b) `pytest -x tests/unit/novel/test_structure.py tests/unit/novel/test_prose_analysis.py` tail, (c) `python -c "from agency_mcp.server import create_mcp; m = create_mcp(); print(sum(1 for t in m._tools.values() if 'domain:novel' in t.tags))"` output (should jump by ~30), (d) `rg 'tags=\{"domain:novel"\}' servers/agency-mcp/src/agency_mcp/handlers/novel/ -c` aggregate, (e) a sample `novel_coherence_check` output on the broken fixture (≤500 tokens, demonstrates the report shape).
11. **Gate 4 — Self-Review.** Three questions per protocol §2 Gate 4. Specifically flag: any of the 11 checks where the brief's "Decidable" verdict turned out to require LLM judgement (escalate to a `[BLOCKED: clarification]` comment, do not silently degrade to warning); any deviation from the brief's report shape (must be justified or reverted).

## Acceptance (Gherkin)

```gherkin
# anchor: 013.1
Scenario: Dynamic-pair reciprocity violation is detected and autofixable
  Given a work whose NCP storyform has throughline.os.dynamic = "knowledge"
  And the same work has throughline.mc.dynamic = "knowledge"
  And the dynamic_pair_id linking those two elements is dp.knowledge_thought
  When the operator calls novel_coherence_check(work_id)
  Then the response contains {"status": "FAIL"}
  And response.checks.pair_reciprocity.items contains an item with
    {"check": "dynamic_pair_reciprocity", "severity": "fail", "a": "throughline.os", "b": "throughline.mc", "expected": "thought", "got": "knowledge"}
  When the operator calls novel_coherence_correct(work_id, autofix={"pair_reciprocity"}, dry_run=false)
  Then exactly one of the two dynamic values is flipped to "thought"
  And a subsequent novel_coherence_check(work_id) returns {"status": "PASS"}

# anchor: 013.2
Scenario: Clean work returns a compact PASS report
  Given a known-good fixture work at tests/fixtures/novel/good_work.ncp.json
  When novel_coherence_check(work_id) runs
  Then the response equals approximately {"status":"PASS","violations":0,"checks":{<11 keys, each {"status":"PASS"}>}}
  And the serialized response is ≤ 80 tokens (no PASS-check items arrays, per the brief's token-cheap shape)

# anchor: 013.3
Scenario: All 11 decidable checks are individually addressable
  Given the coherence handler is registered
  When the operator inspects novel_coherence_check's introspection
  Then the response shape lists exactly these 11 check keys:
    pair_reciprocity, ktad_coverage, quad_completeness, slot_fill, throughline_partition,
    crucial_element_placement, resolve_outcome_judgment, approach_concern,
    mental_sex_problem_solving, signpost_permutation, storybeat_moment_refs
  And each check has a dedicated test_<name>_pass + test_<name>_fail in tests/unit/novel/test_coherence.py

# anchor: 013.4
Scenario: Prose analysis flags a third-person-limited POV head-hop
  Given a chapter draft declares pov = "3rd_limited" with viewpoint_character = "Anna"
  And the chapter contains the line "Anna sipped her coffee. Across the room, Marcus felt a pang of guilt he would never admit to."
  When novel_scan_pov_violations(chapter_text, declared_pov="3rd_limited", viewpoint_character="Anna") runs
  Then the response contains an item with {"violation_type": "head_hop", "snippet": "Marcus felt a pang of guilt..."}
```

## Out of scope

- The 6-gate `novel_run_pre_drafting_gates` orchestrator (Spec 014 — this spec only ships the `novel_coherence_check` that 014's Dramatica gate calls into).
- Authoring SKILL.md files that surface these handlers (Spec 015 — `dramatica-validator`, `manuscript-coherence-check`).
- The Q1–Q5 Scene-Level Bridge audit (judgement, lives in skill `scene-bridge-auditor` per Spec 015, not as a tool).
- Series-level (`across-book`) coherence — the parity brief splits this off as `series-coherence-check` and it is a Wave C concern.
- Modifying `lib/dramatica/` or `lib/ncp/` internals (owned by Spec 012; this spec is a *consumer* only).
- Hooks integration / `PostToolUse` validators (Spec 017).
- Prompt-builder family (Spec 021 — consumes these structural reads but adds no structural logic).

## References

- `Plan/JULES_PROTOCOL.md` (gates 1–4, §4 source-repo discipline)
- `Plan/000-overview.md` §1 (target tree, novel handler count), §2.1 #1–#2 (tool naming + tags), §2.1 #7 (`dry_run` contract), §2.1 #9 (`ToolResult` envelope)
- `Plan/SOURCES.md` (agency clone command)
- `Plan/013-novel-handlers-structural/references/dramatica-decidability.md` — **the matrix this spec implements** (embedded from agent `a78bd055cd15ef572`)
- Spec dependency: `Plan/011-novel-handlers-core/spec.md` (CRUD layer + StateCache wiring)
- Spec dependency: `Plan/012-dramatica-and-ncp-libs/spec.md` (navigator + NCP validator this spec consumes)
- Spec downstream: `Plan/014-novel-gates-and-revision/spec.md` (gates orchestrator calls `novel_coherence_check`)
- Spec downstream: `Plan/015-novel-skills-catalogue/spec.md` (`dramatica-validator` skill surfaces these tools)
- Spec downstream: `Plan/021-novel-prompt-builder-family/spec.md` (prompt-builders compose against verified storyform slots)
- Vendor source (read-only): `~/work/vendor/agency/maintenance/schemas/narrative-ontology/ontology.json`, `~/work/vendor/agency/tools/dramatica-nav/validate.py`
