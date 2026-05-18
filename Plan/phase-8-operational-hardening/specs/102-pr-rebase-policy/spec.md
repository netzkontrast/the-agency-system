---
spec_id: 102
slug: pr-rebase-policy
status: ready
owner: jules
depends_on: [099]
affects:
  - Plan/JULES_PROTOCOL.md
  - Plan/_lint/check_rebase_status.py
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

# Spec 102 — PR Rebase Policy

## Why

PRs #39, #40, #41, and #42 all hit the same stale-merge-base failure pattern: after a sibling PR merged into `Master`, the remaining open spec-PRs continued to report green CI while silently sitting on a base commit that no longer represented the integration target. Codex reviewers (L13) and the merge bot both produced false greens, and the orchestrator only caught the drift when a manual `git fetch && git merge-base` check surfaced the divergence. Spec 099 §3 codifies the *policy* ("rebase all open PRs after every Master merge") at the protocol level; this spec ships the *enforcement*: a single lint script that diffs `origin/Master` against every open PR head and exits non-zero when any of them is behind. That script is the post-merge hook the orchestrator runs without thinking.

## Done When

- [ ] `Plan/JULES_PROTOCOL.md` §3 contains the verbatim recipe `git fetch origin Master && git rebase origin/Master && git push --force-with-lease` under a "Rebase after every Master merge" heading.
- [ ] `Plan/JULES_PROTOCOL.md` §3 names `mcp__github__update_pull_request_branch` as the *primary* mechanism (preferred over the shell recipe when the orchestrator drives the rebase).
- [ ] `Plan/JULES_PROTOCOL.md` §3 documents the post-merge hook contract: "after any merge into Master, run `python Plan/_lint/check_rebase_status.py` and rebase every PR it flags".
- [ ] `Plan/_lint/check_rebase_status.py` exists, accepts no required arguments, lists open PRs via `gh pr list --json number,headRefName,baseRefName --state open`, and exits 1 if any PR's head is behind `origin/Master`.
- [ ] Running the script on a tree where every open PR is up-to-date exits 0 and prints `all clear`.
- [ ] Running the script on a synthesised broken fixture (mocked `gh` output) exits 1 and prints each behind PR on a separate line.
- [ ] The script's output is plain text under 4 kB even with 50 open PRs (token-budget guard per L14).

## Source clones (run first)

None — this spec is meta-work. `source-repos:` is `[]`. Read `Plan/_lint/check_affects.py` (created by spec 099) for the lint-script conventions (entry-point shape, exit codes, mocking strategy).

## Files

- **Create**:
  - `Plan/_lint/check_rebase_status.py` — the lint script described in Done When.
- **Modify**:
  - `Plan/JULES_PROTOCOL.md` — §3 "Rebase after every Master merge" subsection (rebase recipe + tool preference + hook contract).
- **Move / Delete**: none.

## Approach

1. **Gate 1 — Confidence.** Verify spec 099 has merged (`Plan/_lint/check_affects.py` exists). Confirm `gh` CLI is on PATH and authenticated (`gh auth status` exits 0). Confirm the default branch is `Master` (capitalised — repo-level convention). Cite all three checks in the PR Confidence table.
2. **Author the script skeleton.** `check_rebase_status.py` is a single-file Python script with no external deps beyond stdlib + `subprocess` to shell out to `gh`. Top-level entry: parse `gh pr list --json number,headRefName,baseRefName,headRefOid --state open` once, then for each PR run `git merge-base --is-ancestor origin/Master <head_oid>` to decide whether the PR is behind.
3. **Wire the exit-code contract.** Walk each PR result; collect any whose `--is-ancestor` check returns non-zero (i.e. `origin/Master` is *not* an ancestor of the PR head, meaning the PR is behind). On empty list print `all clear` and exit 0. On non-empty list print one `PR #<num> (<head>): behind origin/Master` line per PR and exit 1.
4. **Cap output size.** Truncate the printed list at 50 entries and append `... (N more)` when exceeded. The script's hard ceiling stays under 4 kB so it can be pasted into the orchestrator loop without burning tokens (L14).
5. **Patch JULES_PROTOCOL.md §3.** Add a "Rebase after every Master merge" subsection. Order: (a) the shell recipe verbatim, (b) the `mcp__github__update_pull_request_branch` primary-tool note, (c) the post-merge hook contract that names the new lint script, (d) a one-line cross-reference to spec 099 §3 (policy origin).
6. **TDD — Gate 2.** RED: write `tests/unit/lint/test_rebase_status.py` (path under spec 099's lint test tree if it exists, otherwise inline-skip — script is testable via the synthesised broken fixture). The test mocks `subprocess.run` to return two PRs (one up-to-date, one behind) and asserts exit 1 + the behind PR appears in stdout. GREEN: implement step 2–4. REFACTOR: extract the `gh`-shelling helper if it grows past 15 lines.
7. **Gate 3 — Evidence.** Paste `python Plan/_lint/check_rebase_status.py` output against the live tree, `rg -n 'Rebase after every Master merge' Plan/JULES_PROTOCOL.md`, and the pytest output for the lint test. Capture under a clean shell (no shell aliases shadowing `git`).
8. **Gate 4 — Self-Review.** Answer the three Self-Review questions. Dispatch the review subagent per `Plan/_templates/review-subagent-prompt.md` (spec 099).

## Acceptance (Gherkin)

```gherkin
# anchor: 102.1
Scenario: check_rebase_status exits 0 when every open PR is up-to-date
  Given gh pr list returns three open PRs whose head_oid each has origin/Master as ancestor
  When the operator runs "python Plan/_lint/check_rebase_status.py"
  Then the process exits with status 0
  And stdout contains the string "all clear"

# anchor: 102.2
Scenario: check_rebase_status exits 1 and lists every behind PR
  Given gh pr list returns four open PRs and two of them are behind origin/Master
  When the operator runs "python Plan/_lint/check_rebase_status.py"
  Then the process exits with status 1
  And stdout contains exactly two lines matching "PR #\\d+ \\(.+\\): behind origin/Master"

# anchor: 102.3
Scenario: JULES_PROTOCOL.md §3 documents the rebase recipe and the primary tool
  Given the patched protocol file
  When the operator runs "rg -n 'git rebase origin/Master' Plan/JULES_PROTOCOL.md"
  Then at least one match is returned under a "Rebase after every Master merge" subsection
  And "mcp__github__update_pull_request_branch" appears within five lines of that match

# anchor: 102.4
Scenario: Output is capped under 4 kB even with many behind PRs
  Given gh pr list returns 100 open PRs all behind origin/Master
  When the operator runs "python Plan/_lint/check_rebase_status.py"
  Then stdout is no larger than 4096 bytes
  And the final line matches "\\.\\.\\. \\(\\d+ more\\)"
```

## Out of scope

- Automating the rebase itself (this spec only flags drift — the orchestrator or a human performs the rebase using the recipe or `mcp__github__update_pull_request_branch`).
- Handling PRs whose base branch is not `Master` (rare for spec-PRs; if encountered the script logs and skips).
- A pre-merge hook (this spec only ships the post-merge hook; pre-merge gating belongs to GitHub branch protection rules).
- Cross-repo rebase coordination — `the-agency-system` is single-repo for now.
- Codex-bot interaction with rebased PRs (L13 covers the review behaviour; not in scope here).

## References

- `Plan/JULES_PROTOCOL.md` (§3 being patched, Gate 3 evidence convention)
- `Plan/_lessons-learned/13-codex-bot-pr-reviews-are-gold.md` (false-green review trap)
- `Plan/_lessons-learned/14-token-consumption-postmortem.md` (output-size cap rationale)
- Spec dependency: `Plan/099-jules-orchestration-improvements/spec.md` (`_lint/` conventions, rebase policy origin)
- Spec sibling: `Plan/100-session-log-mcp/spec.md` (post-merge events can be queried via `session_log_query(kind='merge')` once both land)
