---
spec_id: 138
slug: frustration-log-protocol
status: draft
owner: jules
depends_on: [099]
affects:
  - Plan/JULES_PROTOCOL.md
  - Plan/_templates/spec-template.md
  - Plan/_lint/check_friction_log.py
  - Plan/_lessons-learned/README.md
  - tests/unit/lint/test_friction_log.py
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

# Spec 138 — Mandatory Per-PR Frustration-Log Protocol (FL0–FL3)

## Why

`netzkontrast/agency` enforces a discipline that `the-agency-system` does not: **every session, including the ones that went perfectly, ends with a structured Frustration-Level declaration (`FL0` – `FL3`)**. The Agency spec lives in [`FRUSTRATED.md`](../../../home/user/agency/FRUSTRATED.md) (~8 KB) and is mechanically validated by `tools/check-fl-declaration.py` (one canonical line per session, plus a small set of accepted variant forms).

The rationale Agency cites — and which applies verbatim here — is **falsifiable null-baseline declaration**: absent an FL0 line, the maintenance run cannot distinguish "no friction occurred" from "the agent forgot to log". The denominator for every friction-frequency metric collapses, and recurring patterns silently disappear from longitudinal analysis. Agency's own empirical data (38 % of 60 friction logs are FL0) shows the population that vanishes when FL0 becomes optional.

`the-agency-system` currently has `Plan/_lessons-learned/` — fourteen narrative, post-hoc, curator-authored entries written **after** the orchestrator finished a wave. That corpus is valuable (and Spec 099 already absorbs its findings), but it is **not a per-session signal**: it captures what the human-orchestrator noticed, not what each Jules session reported. Successful sessions never enter it. The 099 lint-script wave codifies *content* gaps (`affects:` discipline, schema authority, dispatch-prompt hardening); it does not introduce a per-session friction signal.

This spec ports Agency's FL discipline as a small, additive layer on top of Spec 099's `Plan/_templates/spec-template.md` and `Plan/_lint/` framework. Every PR body MUST carry a `## Frustration Log` section with one canonical declaration line; a single lint script mechanically rejects PRs that ship without one. The lessons-learned corpus stays — Spec 099 still feeds from it — but the per-PR declaration adds the missing denominator.

## Done When

- [ ] `Plan/JULES_PROTOCOL.md` Gate 4 (Self-Review) gains a fourth required PR-body section: `## Frustration Log`, holding exactly one line of the form `Highest Frustration Level: FL[0-3]` immediately followed by a body of 1–6 sentences justifying the level (FL0 sentence may be a one-line acknowledgement).
- [ ] `Plan/JULES_PROTOCOL.md` §5 adds an anti-pattern: "Omitting the `## Frustration Log` section on the grounds that the session was uneventful — FL0 is mandatory and is the falsifiable null-baseline."
- [ ] `Plan/JULES_PROTOCOL.md` Appendix gains a "Frustration-Level rubric" subsection enumerating FL0 (no friction), FL1 (minor — repeated typos, one ambiguous sentence), FL2 (significant — conflicting instructions, tooling failures requiring substantial diagnostic effort), FL3 (blocker — open `[BLOCKED:]` draft PR and stop). Each level cites one concrete example from `Plan/_lessons-learned/`.
- [ ] `Plan/_templates/spec-template.md` (authored by Spec 099) is extended with a `## Frustration Log` template stub showing the canonical line and a 1-sentence placeholder body.
- [ ] `Plan/_lint/check_friction_log.py` exists and exits non-zero when run against a PR-body fixture (Markdown file) that lacks a `## Frustration Log` heading OR lacks a parseable `Highest Frustration Level: FL[0-3]` line within ten lines of that heading.
- [ ] The lint script accepts a single positional argument (path to a Markdown file containing the PR body) and emits a single diagnostic line of the form `<relpath>::ERROR:FL.1:<missing|malformed>:<details>` on failure. On success it emits one line `<relpath>::OK:FL.1:level=FL<n>` and exits 0.
- [ ] `Plan/_lessons-learned/README.md` is updated to point at the new per-PR FL section as the canonical per-session signal; the existing lesson-files (01–14) are recharacterised as "curator-authored aggregate post-mortems" so the two surfaces do not overlap or compete.
- [ ] `pytest -x tests/unit/lint/test_friction_log.py` exits 0 with three table-driven cases: (a) well-formed FL2 body passes; (b) missing `## Frustration Log` heading fails with code `FL.1:missing`; (c) heading present but `Highest Frustration Level:` line absent fails with `FL.1:malformed`.
- [ ] The lint script's stdout output is capped under 4 kB (token-budget guard per Lesson 14) regardless of input file size.

## Source clones (run first)

None — this spec is meta-work. `source-repos:` is `[]`. The behavioural model is mirrored, not imported, from `netzkontrast/agency` — read `~/agency/FRUSTRATED.md` and `~/agency/tools/check-fl-declaration.py` as reference only; do not copy the file into the worktree.

## Files

- **Create**:
  - `Plan/_lint/check_friction_log.py` — single-file Python 3.11 stdlib-only lint script (no external deps; mirrors the entry-point shape of Spec 099's `check_affects.py` and Spec 102's `check_rebase_status.py`).
  - `tests/unit/lint/test_friction_log.py` — pytest cases per Done When.
- **Modify**:
  - `Plan/JULES_PROTOCOL.md` — Gate 4 section (add `## Frustration Log` requirement), §5 (anti-pattern entry), Appendix (rubric).
  - `Plan/_templates/spec-template.md` — append the `## Frustration Log` stub (this file is created by Spec 099; this spec depends_on 099 so the file exists by the time 138 runs).
  - `Plan/_lessons-learned/README.md` — clarify the surface boundary.
- **Move / Delete**: none.

## Approach

1. **Gate 1 — Confidence.** Verify Spec 099 has merged: `Plan/_templates/spec-template.md` and `Plan/_lint/check_affects.py` both exist. Confirm `Plan/_lessons-learned/` still contains the 14 narrative lessons. Read `~/agency/FRUSTRATED.md` end-to-end (8.6 KB; one read) and `~/agency/tools/check-fl-declaration.py` (read-only reference). Cite all three in the PR Confidence table.
2. **Author the FL rubric inline.** Draft the four-level rubric (FL0–FL3) as a JULES_PROTOCOL.md Appendix subsection. Cite Lesson 02 (agentMessaged kills sessions) as the FL2 example, Lesson 12 (COMPLETED-without-PR) as the FL3 example, Lesson 04 (`affects:` incompleteness, low-disruption) as the FL1 example. FL0 cites "session that produced PRs #41 and #42 with zero rework".
3. **Patch Gate 4 in JULES_PROTOCOL.md.** Insert the `## Frustration Log` section as the **fourth** required PR-body section (after `## Self-Review`, before any optional `## Notes` block). Specify the canonical line format verbatim. Reference the rubric.
4. **Extend the spec template (Spec 099 deliverable).** Append a `## Frustration Log` stub block to `Plan/_templates/spec-template.md`. The stub contains the canonical line `Highest Frustration Level: FL0` and a one-line placeholder body explaining what to swap in.
5. **Author `check_friction_log.py`.** Single-file Python 3.11. Accepts one positional argument (path). Reads the file. Searches for the literal heading `## Frustration Log` (case-sensitive, anchored at line start). Within the next 10 lines, searches for a regex `^Highest Frustration Level: FL([0-3])$`. On match → emit `<path>::OK:FL.1:level=FL<n>` to stdout, exit 0. On missing heading → `<path>::ERROR:FL.1:missing:heading "## Frustration Log" not found`. On heading-but-no-line → `<path>::ERROR:FL.1:malformed:no "Highest Frustration Level: FL[0-3]" line within 10 lines of heading`. Cap stdout at 4 kB.
6. **TDD — Gate 2.** RED: author `tests/unit/lint/test_friction_log.py` with three subprocess-invocation cases driving the script against tempfile fixtures. Run; watch all three fail (`FileNotFoundError` because the script does not yet exist). GREEN: implement the script per step 5. REFACTOR: pull the regex constant to module top so it is unit-testable in isolation.
7. **Gate 3 — Evidence.** Paste `python Plan/_lint/check_friction_log.py Plan/_lint/fixtures/well-formed-pr-body.md` (exit 0, OK line), `python Plan/_lint/check_friction_log.py Plan/_lint/fixtures/missing-heading.md` (exit 1, ERROR:FL.1:missing), `python Plan/_lint/check_friction_log.py Plan/_lint/fixtures/heading-no-line.md` (exit 1, ERROR:FL.1:malformed), and the pytest output. Also paste `rg -n '## Frustration Log' Plan/JULES_PROTOCOL.md` to prove the protocol patch landed.
8. **Gate 4 — Self-Review.** Answer the three questions. Dispatch the Spec 099 review subagent. **Include the new `## Frustration Log` section in this very PR's body as a smoke test.**

## Acceptance (Gherkin)

```gherkin
# anchor: 138.1
Scenario: Well-formed PR body with FL2 declaration passes the lint
  Given a Markdown file containing the heading "## Frustration Log"
  And the line "Highest Frustration Level: FL2" appears within ten lines of that heading
  When the operator runs "python Plan/_lint/check_friction_log.py path/to/pr-body.md"
  Then the process exits with status 0
  And stdout contains exactly one line ending "::OK:FL.1:level=FL2"

# anchor: 138.2
Scenario: PR body without a "## Frustration Log" heading fails the lint
  Given a Markdown file that contains no "## Frustration Log" heading anywhere
  When the operator runs "python Plan/_lint/check_friction_log.py path/to/pr-body.md"
  Then the process exits with status 1
  And stdout contains exactly one line matching "::ERROR:FL.1:missing:"

# anchor: 138.3
Scenario: Heading present but malformed declaration line fails the lint
  Given a Markdown file with "## Frustration Log" but with the body line "FL2 frustration today" (non-canonical form)
  When the operator runs "python Plan/_lint/check_friction_log.py path/to/pr-body.md"
  Then the process exits with status 1
  And stdout contains exactly one line matching "::ERROR:FL.1:malformed:"

# anchor: 138.4
Scenario: JULES_PROTOCOL Gate 4 names the Frustration Log as the fourth required section
  Given the patched JULES_PROTOCOL.md
  When the operator runs "rg -n '## Frustration Log' Plan/JULES_PROTOCOL.md"
  Then at least two matches are returned
  And one match lies under the "Gate 4" subsection
  And one match lies under the "Appendix" rubric subsection
```

## Out of scope

- Importing or copying `~/agency/FRUSTRATED.md` or `tools/check-fl-declaration.py` verbatim. This spec re-authors the discipline from scratch in `the-agency-system`'s idiom (PR-body section + lint script), per ADR-0011 in Agency (no source copy from external repos).
- A maintenance-run aggregator that converts recurring FL1+ entries into Tasks. Agency's "Nightly Maintenance Run" is out of scope here; the per-PR declaration is the primitive.
- Variant forms of the declaration line (`HIGHEST FRUSTRATION LEVEL: FL2`, `Highest FL: 2`, etc.). The canonical line is the only accepted form; we deliberately do not ship Agency's 14-variant grammar.
- Retroactive FL labelling of merged PRs (#30, #36, #46, #41, #42…). The lint runs on new PRs only; historical PRs are out of scope.
- Cross-session aggregation in the `session-log MCP` (Spec 100 owns that surface; this spec only emits the per-session declaration that downstream tooling consumes).

## References

- `Plan/JULES_PROTOCOL.md` — Gate 4 + §5 anti-patterns + Appendix (the three patch points)
- `Plan/099-jules-orchestration-improvements/spec.md` — creates `Plan/_lint/` + `Plan/_templates/spec-template.md` (this spec depends on both)
- `Plan/_lessons-learned/README.md` — current curator-authored corpus (recharacterised, not replaced)
- `Plan/_lessons-learned/02-agent-messaged-and-wait-kills-sessions.md` — FL2 rubric example
- `Plan/_lessons-learned/04-affects-list-incompleteness.md` — FL1 rubric example
- `Plan/_lessons-learned/12-completed-without-pr-or-state-mismatch.md` — FL3 rubric example
- External reference (read-only): `~/agency/FRUSTRATED.md` — discipline model, variant-grammar enumeration, FL0 rationale
- External reference (read-only): `~/agency/tools/check-fl-declaration.py` — entry-point shape for the linter
- Spec sibling: `Plan/139-evidence-snapshot-helper/spec.md` — orthogonal Gate 3 evidence-capture mechanisation
- Spec downstream: `Plan/100-session-log-mcp/spec.md` — will consume the per-PR FL declaration as a structured event once both land
