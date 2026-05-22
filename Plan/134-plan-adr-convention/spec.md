---
spec_id: 134
slug: plan-adr-convention
status: draft
owner: jules
depends_on: [099]
affects:
  - Plan/JULES_PROTOCOL.md
  - Plan/decisions/readme.md
  - Plan/decisions/0001-master-default-branch.md
  - Plan/decisions/0002-plan-folder-numbering.md
  - Plan/_templates/adr-template.md
  - Plan/_lint/check_adr.py
  - tests/unit/lint/test_check_adr.py
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

# Spec 134 — Plan-level ADR Convention (MADR-shaped Decision Records)

## Why

Three repo-wide decisions made during Wave A live nowhere binding: (a) "default base branch is `Master`, not `main`" (cited only as a `<!-- comment -->` in JULES_PROTOCOL.md §8 step 4), (b) "Plan/ uses zero-padded `NNN-slug/` folders, not flat files" (only implicit in the existing tree), (c) "lessons-learned files are advisory, not normative; specs are normative" (no statement anywhere). Every future session that tries to alter any of these has nothing stable to cite and nothing to supersede. The result is silent drift — exactly what `netzkontrast/agency/decisions/` (12 ADRs, MADR 4.0.0, validated by `tools/adr/cli.py`) prevents in the sister repo.

Spec 099 ships the spec template + lint scripts but does NOT define a decision-record substrate. This spec adds the missing layer: a `Plan/decisions/` directory with MADR-shaped append-only ADRs, frontmatter, a status lifecycle (`Proposed → Accepted → Superseded → Deprecated`), a `check_adr.py` validator, and two seed ADRs that ratify the two decisions named above. The validator is deliberately scoped narrower than agency's full `tools/adr/` package: no synthesis into a root spec (the-agency-system has no AGENTS.md equivalent today), no MDL compression — only schema + supersession-DAG checks. Synthesis can follow in a successor spec if the corpus grows past ~10 ADRs.

## Done When

- [ ] `Plan/decisions/` directory exists with a `readme.md` (frontmatter `type: index`) that explains the MADR section contract, the four-state lifecycle, and points at the validator.
- [ ] `Plan/decisions/readme.md` documents the **T4-immutable** rule: an `adr_status: Accepted` ADR MUST NOT be edited; supersede by authoring a successor that names the predecessor in `adr_supersedes:`.
- [ ] `Plan/_templates/adr-template.md` exists with the canonical MADR 4.0.0 sections (`Context and Problem Statement`, `Decision Drivers`, `Considered Options`, `Decision Outcome`, `Consequences`) and the L1+L2 frontmatter scaffold (`adr_id`, `adr_status`, `adr_supersedes`, `adr_superseded_by`).
- [ ] `Plan/decisions/0001-master-default-branch.md` is `adr_status: Accepted` and ratifies the verified-via-`git remote show origin` finding from JULES_PROTOCOL.md §8 step 4 (HEAD branch is `Master`, capitalised).
- [ ] `Plan/decisions/0002-plan-folder-numbering.md` is `adr_status: Accepted` and codifies the `Plan/NNN-slug/spec.md` convention used by all 47 existing specs, with a worked example.
- [ ] `Plan/_lint/check_adr.py` exists and enforces: (i) `adr_id` matches filename prefix, (ii) frontmatter has `adr_id`, `adr_status`, `created`, `updated`, (iii) `adr_status` is in the closed vocabulary `{Proposed, Accepted, Superseded, Deprecated}`, (iv) `adr_supersedes` / `adr_superseded_by` form a reciprocal pair (predecessor MUST cite successor and vice-versa), (v) the supersession graph is acyclic (Kahn's algorithm).
- [ ] `tests/unit/lint/test_check_adr.py` exists with at least three scenarios: clean corpus exits 0, broken-reciprocity fixture exits 1 with stderr containing the offending `adr_id` pair, cyclic-supersession fixture exits 1 with stderr containing the cycle.
- [ ] `Plan/JULES_PROTOCOL.md` §3 gains a one-paragraph "Plan-level decision records" subsection pointing at `Plan/decisions/readme.md` and stating the rule "decisions that change repo-architecture conventions land as ADRs, not as edits to JULES_PROTOCOL.md".
- [ ] `python Plan/_lint/check_adr.py` exits 0 against the two seed ADRs.

## Source clones (run first)

None. Read-only reference: [`netzkontrast/agency/decisions/readme.md`](https://github.com/netzkontrast/agency/blob/main/decisions/readme.md) and [`netzkontrast/agency/tools/adr/`](https://github.com/netzkontrast/agency/tree/main/tools/adr) for the MADR conventions being mirrored. Do NOT clone the agency repo into the working tree.

## Files

- **Create**:
  - `Plan/decisions/readme.md` — directory index + MADR + lifecycle contract.
  - `Plan/decisions/0001-master-default-branch.md` — ratifies the `Master` (capitalised) default branch finding.
  - `Plan/decisions/0002-plan-folder-numbering.md` — codifies the `Plan/NNN-slug/spec.md` convention.
  - `Plan/_templates/adr-template.md` — empty MADR scaffold for future ADRs.
  - `Plan/_lint/check_adr.py` — validator described in Done-When item 6.
  - `tests/unit/lint/test_check_adr.py` — pytest coverage for the validator.
- **Modify**:
  - `Plan/JULES_PROTOCOL.md` — §3 gains "Plan-level decision records" subsection.
- **Move / Delete**: none.

## Approach

1. **Gate 1 — Confidence.** Verify `Plan/decisions/` and `Plan/_templates/adr-template.md` do not exist (`ls Plan/_decisions Plan/_templates/adr-template.md 2>&1 | grep -i "no such file"`). Confirm `Plan/_lint/check_affects.py` exists (spec 099 prerequisite). Confirm `tests/unit/lint/` exists (created by spec 099). Read the agency repo's `decisions/readme.md` and `tools/adr/schema.py` once for the MADR shape; cite both reads in the Confidence table.
2. **Author the MADR template.** `Plan/_templates/adr-template.md` is a copy of the agency template with the L1 frontmatter (`type: adr`, `status: draft`, `slug`, `summary`, `created`, `updated`) plus the L2 ADR namespace (`adr_id: ADR-NNNN`, `adr_status: Proposed`, `adr_supersedes: []`, `adr_superseded_by: []`). The body section headings are fixed: `Context and Problem Statement`, `Decision Drivers`, `Considered Options`, `Decision Outcome`, `Consequences`. Each section carries one `REPLACE — …` instruction line.
3. **Author the validator (TDD first).** RED: write `tests/unit/lint/test_check_adr.py` with three fixtures under `tests/fixtures/adr/`: `clean/0001-foo.md` + `clean/0002-bar.md` (one Accepted, one Proposed); `broken-reciprocity/0001-foo.md` (cites `0002-bar` in `adr_superseded_by` but `0002-bar.md` does not cite back); `cyclic/0001-a.md` ↔ `0002-b.md` (mutual supersession). Each test asserts the expected exit code and a stable substring in stderr. Run pytest, watch all three fail (script does not exist). GREEN: implement `Plan/_lint/check_adr.py` — single-file Python, stdlib only, ≤ 200 lines. Reuses the YAML-frontmatter parser from `Plan/_lint/check_affects.py` (spec 099) if it has been factored into a `Plan/_lint/_frontmatter.py` helper; otherwise inline a 20-line parser and refactor in a follow-up.
4. **Wire the supersession-DAG check.** Build a directed graph `{adr_id → [adr_supersedes ids]}` from the corpus. Run Kahn's algorithm: queue all nodes with in-degree zero; repeatedly pop and decrement neighbours; if any node remains when the queue empties, a cycle exists — emit `ERROR:ADR.CYCLE: <node_a> ↔ <node_b>` and exit 1. Reciprocity: for every `A.adr_supersedes` entry pointing to `B`, assert `B.adr_superseded_by` contains `A`; same for the reverse direction.
5. **Author the two seed ADRs.** `0001-master-default-branch.md`: ratifies the verified finding from JULES_PROTOCOL.md §8 step 4. The Context cites the `git remote show origin` evidence + the dismissed Codex flag. The Decision is verbatim: "the canonical base branch is `Master` (capitalised); `main` is not used in this repo". Status `Accepted`. `0002-plan-folder-numbering.md`: codifies the existing 47-spec convention. The Context names the audit: `find Plan -maxdepth 1 -type d | grep -cE '/[0-9]{3}-' = 47`. The Decision: every spec MUST live in `Plan/<NNN>-<slug>/spec.md`; flat `Plan/<slug>.md` files are forbidden. Status `Accepted`.
6. **Patch `Plan/JULES_PROTOCOL.md` §3.** Add a "Plan-level decision records" subsection (≤ 200 words) after the rebase policy. Three sentences: (a) what ADRs are for, (b) where they live (`Plan/decisions/`), (c) the supersession-not-edit rule for Accepted ADRs. Cross-link the validator.
7. **Gate 2 — TDD.** Already covered in step 3. Confirm RED before GREEN. Pytest output captured under `## Evidence`.
8. **Gate 3 — Evidence.** Paste `python Plan/_lint/check_adr.py` against the live tree, `pytest -x tests/unit/lint/test_check_adr.py -v`, `ls Plan/decisions/`, `rg -n 'Plan-level decision records' Plan/JULES_PROTOCOL.md`.
9. **Gate 4 — Self-Review + reviewer dispatch.** Answer the three Self-Review questions. Specifically flag whether the validator should grow a `--strict` mode (promote WARN → ERROR for missing optional fields) — out of scope here but a candidate follow-up. Dispatch the review subagent per `Plan/_templates/review-subagent-prompt.md`.

## Acceptance (Gherkin)

```gherkin
# anchor: 134.1
Scenario: The ADR validator passes on a clean corpus
  Given Plan/decisions/0001-master-default-branch.md and 0002-plan-folder-numbering.md exist
  And both carry frontmatter adr_id matching their filename prefix
  And both carry adr_status in {Proposed, Accepted, Superseded, Deprecated}
  When the operator runs "python Plan/_lint/check_adr.py"
  Then the process exits with status 0
  And stdout contains "2 ADRs validated"

# anchor: 134.2
Scenario: The validator catches a broken reciprocal supersession
  Given a fixture corpus where 0001-foo.md has adr_superseded_by [ADR-0002]
  And 0002-bar.md's adr_supersedes list does not contain ADR-0001
  When the operator runs "python Plan/_lint/check_adr.py tests/fixtures/adr/broken-reciprocity/"
  Then the process exits with status 1
  And stderr contains "ERROR:ADR.RECIPROCITY"
  And stderr names both ADR-0001 and ADR-0002

# anchor: 134.3
Scenario: The validator detects a cycle in the supersession graph
  Given a fixture corpus where 0001-a.md supersedes 0002-b.md
  And 0002-b.md also supersedes 0001-a.md
  When the operator runs "python Plan/_lint/check_adr.py tests/fixtures/adr/cyclic/"
  Then the process exits with status 1
  And stderr contains "ERROR:ADR.CYCLE"
  And stderr names ADR-0001 and ADR-0002

# anchor: 134.4
Scenario: JULES_PROTOCOL.md §3 routes architecture decisions through ADRs
  Given Plan/JULES_PROTOCOL.md has been patched
  When the operator runs "rg -n 'Plan-level decision records' Plan/JULES_PROTOCOL.md"
  Then exactly one match is returned
  And the match falls within the §3 "Working in the-agency-system repo" section

# anchor: 134.5
Scenario: The MADR template ships with all five required body sections
  Given Plan/_templates/adr-template.md exists
  When the operator runs "rg -nE '^## (Context and Problem Statement|Decision Drivers|Considered Options|Decision Outcome|Consequences)$' Plan/_templates/adr-template.md"
  Then exactly five matches are returned
```

## Out of scope

- Synthesising Accepted ADRs into a root spec (the-agency-system has no AGENTS.md equivalent; if one lands, a successor spec wires the synthesis).
- MDL compression / token-budget enforcement on the rendered synthesis (agency's `tools/adr/compress.py` is the reference; not needed at corpus size 2).
- Backfilling lessons-learned files as ADRs. Lessons remain advisory observations; ADRs are normative decisions. Conversion is per-file, judgement-driven, and not in this spec's scope.
- ADR `Accepted` mutation through a pre-commit hook (no hook infrastructure exists in this repo yet; the validator runs on-demand).
- Cross-repo ADR import (agency's ADR-0011 imports skills from external corpora; not applicable to Plan/).

## References

- `Plan/JULES_PROTOCOL.md` §3 (rebase policy) and §8 (silent-fail recovery — the `<!-- comment -->` ratified by ADR-0001 lives here)
- `Plan/099-jules-orchestration-improvements/spec.md` — ships `Plan/_lint/` and `Plan/_templates/` directories this spec extends
- `Plan/102-pr-rebase-policy/spec.md` — companion lint-script convention
- `Plan/_session-state/2026-05-18-research-3-spec-findings.md` — findings doc that motivates this spec
- [MADR 4.0.0 template](https://adr.github.io/madr/)
- Reference implementation: `netzkontrast/agency/decisions/` (12 ADRs) and `netzkontrast/agency/tools/adr/` (validate + synthesize CLI)
