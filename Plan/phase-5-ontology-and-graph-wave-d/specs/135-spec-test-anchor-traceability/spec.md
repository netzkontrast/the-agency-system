---
spec_id: 135
slug: spec-test-anchor-traceability
status: draft
owner: jules
depends_on: [099]
affects:
  - Plan/JULES_PROTOCOL.md
  - Plan/_lint/check_anchor_coverage.py
  - tests/unit/lint/test_check_anchor_coverage.py
  - Plan/_templates/spec-template.md
source-repos: []
estimated_jules_sessions: 1
domain: cross
wave: C
---

> **Jules: read `Plan/JULES_PROTOCOL.md` before starting.** Run gates 1→4 in order:
> (1) Confidence ≥ 0.90, (2) TDD Red-Green-Refactor, (3) Evidence pasted under `## Evidence`, (4) Self-Review answered.
> Branch: `Master` (default base for fresh specs post-Wave-A; see JULES_PROTOCOL.md §3). Only modify paths under `affects:` below.
> Source repos under `source-repos:` are clone-and-read-only into `~/work/vendor/`; never commit them.
> If anything is ambiguous, open a draft PR labelled `[BLOCKED: clarification]` and stop — do not guess.

# Spec 135 — Spec ↔ Test Anchor Traceability Lint

## Why

Every shipped spec carries Gherkin `Scenario:` blocks tagged with `# anchor: <spec_id>.<n>` (e.g. `# anchor: 099.1` through `# anchor: 099.5`). The anchors are intended as the bridge between a normative scenario and a concrete pytest case: a test for `099.3` is supposed to declare its bound anchor so a human or linter can prove every Done-When acceptance is exercised by code. Today that bridge is purely social — no script verifies that `# anchor: 099.3` has a matching test, and no convention names *how* the test cites the anchor. As Wave C ships ~25 more specs (slots 100–121, 134–135), the coverage gap will become uninspectable.

The sister repo `netzkontrast/agency` solves this with `tests/<dir>/test_*.py` modules that carry a per-test docstring or comment of the form `# anchor: <SPEC>.A.<aspect>.<stmt>` matched against the Gherkin scenarios in the corresponding research SPEC. The mechanism is lightweight (no new test framework, just a docstring convention) but binding (`tools/check-governance.sh` is the gating linter in that repo). This spec ports the convention to the-agency-system at a scope appropriate to the Plan/ layer: a single `check_anchor_coverage.py` script that builds the anchor-to-test map by scanning Gherkin blocks and pytest files, then exits non-zero if any anchor lacks a citing test. Spec 099 ships the spec template + general lint scripts but does NOT enforce anchor coverage — this spec fills that gap.

## Done When

- [ ] `Plan/_lint/check_anchor_coverage.py` exists and (i) walks every `Plan/<NNN>-<slug>/spec.md`, (ii) parses Gherkin code-fences extracting `# anchor: <id>` lines, (iii) walks `tests/` for pytest modules, (iv) extracts `# anchor: <id>` comments and `@pytest.mark.anchor("<id>")` markers, (v) reports any spec anchor that lacks a citing test, (vi) reports any test anchor that does not map to a known spec anchor.
- [ ] The script accepts `--mode=strict` (anchors without tests → exit 1; default) and `--mode=advisory` (same scan, exit 0 with stdout report — for in-progress specs that have not yet been implemented).
- [ ] The script accepts a `--spec=<id>` filter so the orchestrator can scope verification to one spec during Gate 3 evidence capture.
- [ ] `tests/unit/lint/test_check_anchor_coverage.py` exists with at least four scenarios: clean fixture (every anchor has a test) exits 0; missing-test fixture exits 1 with the orphan anchor in stderr; orphan-test fixture (test cites unknown anchor) exits 1 with the orphan test path in stderr; advisory-mode on a missing-test fixture exits 0.
- [ ] `Plan/_templates/spec-template.md` (the scaffold authored by spec 099) gains a "Test traceability" note above the Gherkin block stating that every `# anchor:` MUST be paired with a citing test under `tests/`.
- [ ] `Plan/JULES_PROTOCOL.md` Gate 3 mentions the new lint by name — adding one bullet under the evidence-form table: "Anchor coverage: `python Plan/_lint/check_anchor_coverage.py --spec=NNN` exit-zero output".
- [ ] Running the script against the current tree with `--mode=advisory` exits 0 and prints an honest coverage report (expected: most anchors have NO test yet because most specs are `status: ready`, not `status: done`).

## Source clones (run first)

None. Reference reading only: [`netzkontrast/agency/tests/adr/`](https://github.com/netzkontrast/agency/tree/main/tests/adr) for the anchor-citation convention being ported.

## Files

- **Create**:
  - `Plan/_lint/check_anchor_coverage.py` — the lint script described above.
  - `tests/unit/lint/test_check_anchor_coverage.py` — pytest coverage with the four scenarios.
- **Modify**:
  - `Plan/_templates/spec-template.md` — add the "Test traceability" note.
  - `Plan/JULES_PROTOCOL.md` — Gate 3 evidence-form table gains the anchor-coverage line.
- **Move / Delete**: none.

## Approach

1. **Gate 1 — Confidence.** Verify spec 099 has shipped `Plan/_templates/spec-template.md` and `Plan/_lint/`. Verify the convention is present: `rg -nE '^\s*# anchor: [0-9]{3}\.' Plan/ | wc -l` returns ≥ 10 (proves Gherkin anchors already exist across multiple specs). Decide the test-citation form. **Chosen form**: a top-of-file or per-test comment of shape `# anchor: <id>` on the line above the test function `def` line, *or* a `@pytest.mark.anchor("<id>")` decorator. Both are recognised by the linter so the team can pick the more pythonic option per file.
2. **Author the parser (TDD first).** RED: write `tests/unit/lint/test_check_anchor_coverage.py` with four fixtures under `tests/fixtures/anchor-coverage/`. Each fixture is a tiny `spec.md` + a tiny `test_*.py`. The clean fixture has one Gherkin anchor `# anchor: 999.1` and one matching `# anchor: 999.1` line in the test. The missing-test fixture has the anchor but no test. The orphan-test fixture has a test citing `# anchor: 999.99` with no matching anchor in the spec. The advisory fixture is identical to missing-test but the test invokes the script with `--mode=advisory`. Run pytest, watch four failures. GREEN: implement `Plan/_lint/check_anchor_coverage.py`.
3. **Implement the script.** Single-file Python, stdlib only, ≤ 250 lines. Algorithm:
   - **Index spec anchors.** `pathlib.Path("Plan").glob("*/spec.md")` → for each file, extract every fenced Gherkin block, regex `# anchor: ([\w.]+)` per line, build `dict[anchor_id, spec_path]`.
   - **Index test anchors.** `pathlib.Path("tests").rglob("test_*.py")` → for each file, scan for both `# anchor: ([\w.]+)` lines and `@pytest\.mark\.anchor\(['\"]([\w.]+)['\"]\)` decorators. Build `dict[anchor_id, list[test_path]]`.
   - **Diff.** Orphan spec anchors = spec keys not in test keys → strict-mode error. Orphan test anchors = test keys not in spec keys → always an error (a test citing a non-existent anchor is a fast-path indicator of typos).
   - **Output.** On clean: `stdout="<N> anchors / <M> tests / 0 orphans"` exit 0. On error: per-orphan line on stderr, format `ORPHAN_SPEC: <anchor> (declared in <spec_path>)` or `ORPHAN_TEST: <anchor> (cited in <test_path>)`. Cap output at 200 entries with `... (N more)` per L14.
4. **Modes.** `--mode=strict` (default) — orphan-spec-anchor → exit 1. `--mode=advisory` — orphan-spec-anchor → stderr report, exit 0. Orphan-test-anchor is ALWAYS a non-zero exit (typo-detection is non-negotiable). `--spec=NNN` filters the spec index to the matching `spec_id` frontmatter value, but the test index is still scanned in full (so an orphan-test pointing at the filtered spec still surfaces).
5. **Patch the spec template.** Add a 2-line note above the `## Acceptance (Gherkin)` heading in `Plan/_templates/spec-template.md`:
   > **Test traceability.** Every `# anchor: <id>` below MUST be paired with a citing test under `tests/` (`# anchor: <id>` on the line above `def test_*` OR `@pytest.mark.anchor("<id>")` decorator). Run `python Plan/_lint/check_anchor_coverage.py --spec=<id>` to verify before declaring `status: done`.
6. **Patch JULES_PROTOCOL.md Gate 3.** Add one row to the evidence-form table:
   | Anchor coverage | `python Plan/_lint/check_anchor_coverage.py --spec=NNN` exit-zero output, last 5 lines |
7. **Gate 3 — Evidence.** Run `--mode=advisory` against the full tree, paste the honest coverage report. Run `--mode=strict --spec=135` (this spec) once the tests are written and verify exit 0. Paste pytest output.
8. **Gate 4 — Self-Review + reviewer dispatch.** Answer the three Self-Review questions. Specifically flag two follow-up candidates: (a) integrating the script into a pre-commit hook (today the-agency-system has no hook infrastructure — would be a separate spec), (b) extending the script to verify anchor uniqueness across all specs (no two specs share `135.1`, etc.) — easy to add but out of scope here.

## Acceptance (Gherkin)

> **Test traceability.** Every `# anchor: <id>` below MUST be paired with a citing test under `tests/unit/lint/test_check_anchor_coverage.py`. Run `python Plan/_lint/check_anchor_coverage.py --spec=135` to verify before declaring `status: done`.

```gherkin
# anchor: 135.1
Scenario: Clean corpus has zero orphans
  Given a fixture spec with "# anchor: 999.1" in a Gherkin block
  And a fixture test "tests/fixtures/anchor-coverage/clean/test_smoke.py" with "# anchor: 999.1" on the line above def test_one
  When the operator runs "python Plan/_lint/check_anchor_coverage.py tests/fixtures/anchor-coverage/clean/"
  Then the process exits with status 0
  And stdout contains "0 orphans"

# anchor: 135.2
Scenario: Strict mode catches a spec anchor lacking a citing test
  Given a fixture spec with "# anchor: 999.2" in a Gherkin block
  And no test file under the fixture root cites anchor 999.2
  When the operator runs "python Plan/_lint/check_anchor_coverage.py --mode=strict tests/fixtures/anchor-coverage/missing-test/"
  Then the process exits with status 1
  And stderr contains "ORPHAN_SPEC: 999.2"

# anchor: 135.3
Scenario: Orphan-test detection works regardless of mode
  Given a fixture test that cites "# anchor: 999.99" via pytest.mark.anchor
  And no spec under the fixture root declares 999.99
  When the operator runs "python Plan/_lint/check_anchor_coverage.py --mode=advisory tests/fixtures/anchor-coverage/orphan-test/"
  Then the process exits with status 1
  And stderr contains "ORPHAN_TEST: 999.99"

# anchor: 135.4
Scenario: Advisory mode passes a missing-test fixture but still reports it
  Given a fixture spec with "# anchor: 999.4" lacking a citing test
  When the operator runs "python Plan/_lint/check_anchor_coverage.py --mode=advisory tests/fixtures/anchor-coverage/missing-test/"
  Then the process exits with status 0
  And stderr contains "ORPHAN_SPEC: 999.4"

# anchor: 135.5
Scenario: The --spec filter scopes the report to one spec
  Given Plan/134-plan-adr-convention/spec.md declares anchors 134.1 through 134.5
  And Plan/135-spec-test-anchor-traceability/spec.md declares anchors 135.1 through 135.5
  When the operator runs "python Plan/_lint/check_anchor_coverage.py --spec=134 --mode=advisory"
  Then stderr only mentions 134.* anchors
  And no 135.* anchor appears in stderr

# anchor: 135.6
Scenario: Both citation forms are recognised
  Given a test file with "# anchor: 999.6" comment above one test
  And the same file has @pytest.mark.anchor("999.7") on another test
  And a fixture spec declares both 999.6 and 999.7
  When the operator runs "python Plan/_lint/check_anchor_coverage.py tests/fixtures/anchor-coverage/both-forms/"
  Then the process exits with status 0
  And stdout reports "2 tests cited"
```

## Out of scope

- Pre-commit hook integration. The-agency-system has no hook infrastructure today (`.githooks/` is empty); wiring this script into a hook would require a separate spec ratifying the hook surface.
- Anchor-uniqueness enforcement (no two specs declare `135.1`). Useful but additive — a follow-up.
- Bi-directional sync to a coverage badge or status page. The script is a CLI; reporting UI is out.
- Promoting `--mode=strict` to default for every spec on Master. Today most specs are `status: ready` with no tests yet — advisory mode is the realistic default until Wave C lands.
- Backfilling tests for the ~30 specs already on Master. Each spec's `status: done` transition is the right moment to add coverage; bulk backfill is a separate Task.

## References

- `Plan/JULES_PROTOCOL.md` Gate 3 (evidence-form table being extended)
- `Plan/099-jules-orchestration-improvements/spec.md` — ships `Plan/_lint/` + the spec template this spec extends
- `Plan/134-plan-adr-convention/spec.md` — companion governance spec; both author validators that share the `Plan/_lint/` conventions
- `Plan/_session-state/2026-05-18-research-3-spec-findings.md` — findings doc that motivates this spec
- Reference implementation: `netzkontrast/agency/tests/adr/` (anchor-citation pattern) + `netzkontrast/agency/tools/adr/extract.py` (anchor extraction logic)
