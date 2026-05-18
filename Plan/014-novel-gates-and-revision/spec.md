---
spec_id: 014
slug: novel-gates-and-revision
status: ready
owner: jules
depends_on: [011, 012, 013]
affects:
  - state/schema/state.schema.json
  - servers/agency-mcp/src/agency_mcp/handlers/novel/gates.py
  - servers/agency-mcp/src/agency_mcp/handlers/novel/revision.py
  - servers/agency-mcp/src/agency_mcp/handlers/novel/promo.py
  - servers/agency-mcp/src/agency_mcp/handlers/novel/__init__.py
  - servers/agency-mcp/src/agency_mcp/handlers/novel/content.py  # spec 011's chapter handler; spec 014 injects _chapter_create_guard at top of novel_create_chapter
  - tests/unit/novel/test_gates.py
  - tests/unit/novel/test_revision.py
  - tests/unit/novel/test_promo.py
  - tests/fixtures/novel/          # ENTIRE SUBTREE — gate test fixtures (clean_work/, no_dramatica/, partial_ncp/, etc.)
source-repos:
  - bitwize-music @ v0.91.0
estimated_jules_sessions: 1
domain: novel
wave: B
---

> **Jules: read `Plan/JULES_PROTOCOL.md` before starting.** Run gates 1→4 in order:
> (1) Confidence ≥ 0.90, (2) TDD Red-Green-Refactor, (3) Evidence pasted under `## Evidence`, (4) Self-Review answered.
> Branch: `Master` (default base for fresh specs post-Wave-A; see JULES_PROTOCOL.md §3). Only modify paths under `affects:` below.
> Source repos under `source-repos:` are clone-and-read-only into `~/work/vendor/`; never commit them.
> If anything is ambiguous, open a draft PR labelled `[BLOCKED: clarification]` and stop — do not guess.

# Spec 014 — Novel Gates and Revision

## Why

bitwize-music's `pre-generation-check` blocks lyric drafting until **6 gates pass** (sources, lyrics-stats, pronunciation, explicit, style box, artist names). It is the single most load-bearing pre-flight in the music plugin — without it, generated tracks ship with mispronounced proper nouns, unverified historical claims, and missing metadata. The novel-side parallel `novel_run_pre_drafting_gates` blocks **`novel_chapter_create`** until: (1) Dramatica-confirmed (storyform locked, `novel_coherence_check` passes), (2) NCP-valid (`.ncp.json` validates against schema v1.3.0), (3) premise-locked (logline + theme + comp titles present), (4) cast-complete (every required `players[]` slot filled), (5) POV-declared (every chapter has explicit `pov` + `viewpoint_character`), (6) sources-verified-if-historical (works under `genre: historical-*` have `SOURCES.md` with status `Verified (date)` on every cited claim). This spec ships those 6 gates as a single orchestrator, plus revision-pass tracking (mirrors bitwize's revision tracking — "structural pass done", "line pass done", "copy pass done" — recorded in `state.json` so the dashboard can render progress) and book-promo authoring (blurb / log-line variants / press-kit copy). Without this spec, Spec 015's `pre-drafting-check` skill has nothing to invoke and the chain `novel-work-conceptualizer → chapter-writer` runs without guardrails.

## Done When

- [ ] `handlers/novel/gates.py`, `handlers/novel/revision.py`, `handlers/novel/promo.py` exist and import cleanly.
- [ ] `novel_run_pre_drafting_gates(work_id)` returns `{all_pass: bool, gates: [{name, pass: bool, hint: str, evidence: str}], blocking: list[str]}` with exactly 6 gates: `dramatica_confirmed`, `ncp_valid`, `premise_locked`, `cast_complete`, `pov_declared`, `sources_verified`.
- [ ] Failing any gate causes `novel_chapter_create(work_id, ...)` to refuse with `{ok: false, error: "PRE_DRAFTING_GATES_FAILED", blocking: [...]}` unless `force=true` is passed (force=true is logged to `state.json::novel.{work_id}.force_overrides[]` with timestamp + caller).
- [ ] `novel_mark_revision_pass(work_id, pass_kind)` records the pass in `state.json::novel.{work_id}.revisions[]` with `{pass_kind, marked_at, chapter_ids: [...]}`; `pass_kind ∈ {"structural", "line", "copy", "proof"}`.
- [ ] `novel_list_revision_passes(work_id)` returns the chronological list.
- [ ] `novel_build_promo_pack(work_id, kinds: list[str])` produces `{blurb, logline, jacket_flap, press_kit}` markdown chunks; `kinds` defaults to all four.
- [ ] `pytest -x tests/unit/novel/test_gates.py tests/unit/novel/test_revision.py tests/unit/novel/test_promo.py` exits 0.
- [ ] Each of the 6 gates has at least one `test_gate_<name>_pass` and one `test_gate_<name>_fail` (12 tests minimum in `test_gates.py`).
- [ ] `rg 'tags=\{"domain:novel"\}' servers/agency-mcp/src/agency_mcp/handlers/novel/gates.py servers/agency-mcp/src/agency_mcp/handlers/novel/revision.py servers/agency-mcp/src/agency_mcp/handlers/novel/promo.py -c` aggregate is ≥ 8.

## Source clones (run first)

```bash
git clone --depth=1 --branch=v0.91.0 \
  https://github.com/bitwize-music-studio/claude-ai-music-skills.git \
  ~/work/vendor/bitwize-music
```

Read `~/work/vendor/bitwize-music/servers/bitwize-music-server/handlers/gates.py` for the **6-BLOCKING pattern**: how it short-circuits on first failure vs accumulates, how it formats hints, how it integrates with the StateCache to read existing state without re-loading from disk. Read `~/work/vendor/bitwize-music/servers/bitwize-music-server/handlers/promo.py` for the promo authoring pattern (markdown templating with frontmatter-driven hydration).

## Files

- **Create**:
  - `handlers/novel/gates.py` — `novel_run_pre_drafting_gates(work_id)` orchestrator + 6 private gate functions (`_gate_dramatica_confirmed`, `_gate_ncp_valid`, `_gate_premise_locked`, `_gate_cast_complete`, `_gate_pov_declared`, `_gate_sources_verified`) + a `_chapter_create_guard(work_id, force)` helper called by `novel_chapter_create`.
  - `handlers/novel/revision.py` — `novel_mark_revision_pass(work_id, pass_kind)`, `novel_list_revision_passes(work_id)`, `novel_revert_to_pass(work_id, pass_kind, dry_run=False)` (mirrors bitwize `reset_mastering`).
  - `handlers/novel/promo.py` — `novel_build_promo_pack(work_id, kinds)`, `novel_get_promo_content(work_id, kind)`, `novel_update_promo_field(work_id, kind, field, value)`.
  - `tests/unit/novel/test_gates.py` (12+ tests: pass/fail for each of the 6 gates plus integration tests that `novel_chapter_create` refuses on gate failure).
  - `tests/unit/novel/test_revision.py` (mark + list + revert pass; verify state.json mutation; verify `dry_run=True` is no-op).
  - `tests/unit/novel/test_promo.py` (4-kind build + idempotent + frontmatter hydration).
- **Modify**:
  - `handlers/novel/__init__.py` — extend `register_novel_handlers(mcp)` (or call a new `register_novel_gates_revision_promo(mcp)`) to wire the 3 new modules.
- **Do not touch**: `novel_chapter_create` body except to add the `_chapter_create_guard(work_id, force)` call at the top — the rest of its logic is owned by Spec 011.

## Approach

1. **Gate 1 — Confidence (target ≥ 0.90).** Cite: `rg -l 'novel_run_pre_drafting_gates' servers/` returns nothing (no duplicate); `novel_coherence_check` exists from Spec 013 (`python -c "from agency_mcp.handlers.novel.coherence import novel_coherence_check; print(novel_coherence_check)"`); `lib/ncp/validator` exists from Spec 012; bitwize `gates.py` pattern is readable in `~/work/vendor/bitwize-music/`. Root cause / contract added: a 6-gate orchestrator that gates `novel_chapter_create`, mirroring bitwize.
2. **Clone source + read bitwize pattern.** Run the clone. Read `gates.py` end-to-end. Note: bitwize's pattern accumulates all gate results (does NOT short-circuit on first failure) — the user wants to see *every* failing gate at once, not fix them one at a time. Mirror this for novel.
3. **TDD — Gate 2, RED.** Author `test_gates.py` first. For each of the 6 gates, write the pass + fail test using fixture works:
   - `tests/fixtures/novel/clean_work/` — passes all 6 gates.
   - `tests/fixtures/novel/no_dramatica/` — fails `dramatica_confirmed` only.
   - `tests/fixtures/novel/bad_ncp/` — fails `ncp_valid` only.
   - `tests/fixtures/novel/missing_premise/` — fails `premise_locked` (no logline in `README.md` frontmatter).
   - `tests/fixtures/novel/incomplete_cast/` — fails `cast_complete` (a `players[]` entry missing a required field).
   - `tests/fixtures/novel/no_pov/` — fails `pov_declared` (one chapter file missing `pov:` in frontmatter).
   - `tests/fixtures/novel/historical_unverified/` — `genre: historical-fiction` with `SOURCES.md` claims at `status: Pending`.
   - Plus an integration test: `test_chapter_create_refuses_when_gates_fail` — calls `novel_chapter_create("no_dramatica", ...)` and asserts `{ok: false, error: "PRE_DRAFTING_GATES_FAILED"}`.
   - Run pytest — all must fail with `ModuleNotFoundError`.
4. **GREEN — implement the 6 gates.** Each gate is a small function returning `{name, pass, hint, evidence}`:
   - `_gate_dramatica_confirmed`: read `state.json::novel.{work_id}.dramatica_locked` flag (set by Spec 015's `work-architect` skill at end of conceptualizer phase 7) AND call `novel_coherence_check(work_id)` from Spec 013 — pass iff both are true.
   - `_gate_ncp_valid`: call `lib.ncp.validator.validate(work_path / ".ncp.json")` (Spec 012). Hint quotes the first validator error.
   - `_gate_premise_locked`: read `README.md` frontmatter; require `logline`, `theme`, `target_reader`, `comp_titles` all non-empty.
   - `_gate_cast_complete`: load `.ncp.json::players[]`; each player must have `name`, `archetype`, `motivations[]` non-empty.
   - `_gate_pov_declared`: glob `chapters/*.md`; every chapter file's frontmatter must have `pov ∈ {1st, 3rd_limited, 3rd_omniscient, 2nd}` and `viewpoint_character` (unless `pov: 3rd_omniscient`).
   - `_gate_sources_verified`: if `README.md::genre` starts with `historical-`, read `SOURCES.md` as a markdown table; every row's `status` column must be `Verified (YYYY-MM-DD)`. Non-historical works pass with `evidence: "N/A — genre is not historical-*"`.
5. **`novel_run_pre_drafting_gates` orchestrator.** Run all 6 in deterministic order. Accumulate results. Return `{all_pass: bool, gates: [...], blocking: [name for g in gates if not g.pass]}`. Cap each `hint` at ~140 chars (token discipline per overview §2.1 #6).
6. **`_chapter_create_guard`.** Called at the top of `novel_chapter_create`. If `force=True`, log to `state.json::novel.{work_id}.force_overrides[]` and proceed. Otherwise call the orchestrator; if `all_pass` is false, return `{ok: false, error: "PRE_DRAFTING_GATES_FAILED", blocking: [...], hint: "Run novel_run_pre_drafting_gates(work_id) for full report, or pass force=True to override."}`. The guard MUST be synchronous and inside the tool — per overview §2.1 #11, gates are correctness, not side-effect.
7. **Revision tracking.** `novel_mark_revision_pass(work_id, pass_kind)` appends to `state.json::novel.{work_id}.revisions[]`. Validate `pass_kind ∈ {"structural","line","copy","proof"}` (per parity brief's Matt Bell / CMOS editorial stages). `novel_revert_to_pass(work_id, pass_kind, dry_run=False)`: when `dry_run=True`, returns `{would_apply, diff, warnings}` per overview §2.1 #7; when false, truncates the revisions array after the specified pass.
8. **Promo authoring.** `novel_build_promo_pack(work_id, kinds=["blurb","logline","jacket_flap","press_kit"])` reads `README.md` + `cast.md` + `.ncp.json::theme` and emits 4 markdown chunks. Use a simple `{var}` template (no Jinja — keep deps minimal). Idempotent: same inputs → same bytes.
9. **REFACTOR.** With all tests green, extract the common `{name, pass, hint, evidence}` shape into a `GateResult` dataclass; extract the historical-genre detection into a single `_is_historical_genre(work_id) -> bool`.
10. **Gate 3 — Evidence.** Paste under `## Evidence`: (a) `pytest -x tests/unit/novel/test_gates.py tests/unit/novel/test_revision.py tests/unit/novel/test_promo.py` exit-zero tail, (b) a sample `novel_run_pre_drafting_gates` output on the clean fixture (all_pass: true), (c) a sample on `no_dramatica` fixture (all_pass: false, blocking: ["dramatica_confirmed"]), (d) the integration-test output showing `novel_chapter_create` refusing with `PRE_DRAFTING_GATES_FAILED`.
11. **Gate 4 — Self-Review.** Three questions. Flag specifically: any gate where the pass-condition turned out to be more nuanced than the spec described (e.g. `sources_verified` for partially-historical works that mix invented and real-event chapters); any new field added to `state.json` schema (must be reflected back to Spec 003's schema doc).

## Acceptance (Gherkin)

```gherkin
# anchor: 014.1
Scenario: A work with no Dramatica fill fails the dramatica_confirmed gate
  Given a work where state.json::novel.{work_id}.dramatica_locked is absent or false
  And dramatica.md is empty
  When the operator calls novel_run_pre_drafting_gates(work_id)
  Then the response contains {"all_pass": false}
  And response.gates contains an item {"name": "dramatica_confirmed", "pass": false, "hint": "<≤140-char string>"}
  And response.blocking contains "dramatica_confirmed"

# anchor: 014.2
Scenario: novel_chapter_create refuses when any gate fails
  Given a work whose pre-drafting gates do not all pass
  When the operator calls novel_chapter_create(work_id="...", title="Chapter 1", ...)
  Then the response is {"ok": false, "error": "PRE_DRAFTING_GATES_FAILED", "blocking": [<≥1 item>], "hint": "Run novel_run_pre_drafting_gates..."}
  And no chapter file is written to disk

# anchor: 014.3
Scenario: force=true overrides the gate and logs the override
  Given a work whose pre-drafting gates do not all pass
  When the operator calls novel_chapter_create(work_id="...", title="Chapter 1", force=true, ...)
  Then the chapter file is written
  And state.json::novel.{work_id}.force_overrides contains a new entry {"at": "<ISO-8601>", "blocking": [...]}

# anchor: 014.4
Scenario: Revision pass tracking
  Given a work with no revisions recorded
  When the operator calls novel_mark_revision_pass(work_id="...", pass_kind="structural")
  And then novel_mark_revision_pass(work_id="...", pass_kind="line")
  Then novel_list_revision_passes(work_id="...") returns a 2-item chronological list
  When the operator calls novel_revert_to_pass(work_id="...", pass_kind="structural", dry_run=true)
  Then the response is {"would_apply": true, "diff": "revisions[]: 2 entries → 1 entry", "warnings": []}
  And state.json::novel.{work_id}.revisions still has 2 entries
```

## Out of scope

- Authoring the `pre-drafting-check` SKILL.md that wraps this orchestrator (Spec 015).
- Adding new structural checks to `novel_coherence_check` (Spec 013).
- The 14-point QC linter (that lives in `prose-reviewer` skill per Spec 015's parity table, distinct from this 6-gate pre-flight).
- The 9-domain publication QA gate (`publication-director` skill — Spec 015, runs at release time, not drafting time).
- Hook integration (PostToolUse hooks that automatically run gates after edits — Spec 017).
- Prompt-builder integration (Spec 021 — composes against gate state but does not author gates).

## References

- `Plan/JULES_PROTOCOL.md` (gates 1–4, §4 source-repo discipline)
- `Plan/000-overview.md` §1 (target tree), §2.1 #6 (response shape token discipline), §2.1 #7 (`dry_run` contract), §2.1 #11 (synchronous state invalidation, not hooks)
- `Plan/SOURCES.md` (bitwize-music clone command + verification flag)
- Spec dependency: `Plan/013-novel-handlers-structural/spec.md` (`novel_coherence_check` consumed by `_gate_dramatica_confirmed`)
- Spec dependency: `Plan/012-dramatica-and-ncp-libs/spec.md` (NCP validator consumed by `_gate_ncp_valid`)
- Spec dependency: `Plan/011-novel-handlers-core/spec.md` (`novel_chapter_create` body — this spec adds a guard, not new logic)
- Spec downstream: `Plan/015-novel-skills-catalogue/spec.md` (`pre-drafting-check` skill wraps this orchestrator)
- Vendor source (read-only): `~/work/vendor/bitwize-music/servers/bitwize-music-server/handlers/gates.py` (6-BLOCKING pattern), `~/work/vendor/bitwize-music/servers/bitwize-music-server/handlers/promo.py` (promo authoring pattern)
- `/home/user/the-agency-system/CLAUDE.md` §"pre-generation-check" — operator-facing description of the music gate this spec mirrors
