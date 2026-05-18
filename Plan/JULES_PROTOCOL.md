# JULES_PROTOCOL.md

> **Audience:** Jules (Google's asynchronous cloud coding agent) working on `the-agency-system`. This document is the contract. Every spec in `Plan/` defers to it.

## 1. Mission

Jules ships changes to `the-agency-system` while a human is offline. Because the human cannot interrupt a wrong turn in real time, **disciplined work outranks fast work**. A small, correct, well-evidenced commit landing in eight hours is worth more than a sprawling, plausible-looking commit landing in two — the second one will be reverted, the first one will be merged. The four gates below are not theatre; they are the only reason the human can leave Jules unattended. If a gate cannot be satisfied, Jules stops and asks via the PR rather than guessing forward.

## 2. The four gates

Run them in order. Do not collapse, skip, or reorder.

### Gate 1 — Confidence Check (before any code change)

Jules has no MCP scorer; the score is computed by walking the checklist honestly and assigning the weights below. Aim for **Total ≥ 0.90** before the first `Edit`. Render the table in the PR description (as a draft if needed) so the human can audit the reasoning later.

| # | Check | Weight | Pass when… |
|---|---|---|---|
| 1 | No duplicate implementation | 0.25 | `rg`, `grep -r`, or `git grep` finds no existing function/module already solving this. Cite the exact command. |
| 2 | Architecture compliance | 0.25 | The change uses the stack already in `pyproject.toml` / `package.json` / `AGENTS.md`. No new dependency unless the spec lists it under `deps:`. |
| 3 | Official docs verified | 0.20 | The library version actually installed (`pip show`, `npm ls`) matches the docs you read. Paste the version line. |
| 4 | Working OSS reference | 0.15 | At least one public repo or canonical example shows the pattern working. Paste the URL. |
| 5 | Root cause identified | 0.15 | For bug fixes: name the cause, not the symptom. For features: name the contract being added. One sentence. |

- **≥ 0.90** → proceed to Gate 2.
- **0.70 – 0.89** → write a `## Open Questions` block in the PR body, proceed only on the checks that passed, leave a `[BLOCKED:]` label on anything below 0.70.
- **< 0.70** → STOP. Open a draft PR labelled `[BLOCKED: confidence]` and wait. Do not write code.

### Gate 2 — TDD Loop (Red → Green → Refactor)

For every behavioural change:

1. **RED.** Write the failing test first. Run it and **watch it fail with the expected message**.
   - Python: `pytest -x path/to/test_file.py::test_name`
   - Node/TS: `npm test -- --runInBand path/to/file.test.ts`
   - Paste the failing output into the PR thread or commit body. A test that does not fail when expected is a broken test, not a victory.
2. **GREEN.** Write the *minimum* code to make the test pass. Resist adding adjacent fixes, refactors, or "while I'm here" tidy-ups.
3. **REFACTOR.** Restructure with the test green throughout. If the test breaks mid-refactor, you broke the implementation — revert, do not "fix" the test.

**When NOT to TDD (be honest):** pure config edits (`.toml`, `.yaml`, `.env.example`), documentation-only changes, dependency bumps with no code surface change, file renames with no semantic change, generated-file regeneration. For these, skip Gate 2 and state explicitly in the PR: `TDD: N/A — config-only change, verified by <command>`.

### Gate 3 — Verification Before Completion

Every `[x]` Jules ticks in a spec's `Done When:` list must be backed by an artefact pasted into the PR body. Assertion alone is not evidence.

| Claim form | Required artefact |
|---|---|
| "Tests pass" | `pytest -x` (or `npm test`) exit-zero output, last 20 lines |
| "Lint clean" | `ruff check .` / `eslint .` exit-zero output |
| "Type-check clean" | `mypy .` / `tsc --noEmit` exit-zero output |
| "Build works" | `python -m build` / `npm run build` final line |
| "Server boots" | `python -c "from agency_mcp.server import create_mcp; print(create_mcp())"` |
| "Endpoint returns X" | `curl -i` invocation + response |
| "File contains Y" | `rg 'Y' path/file` hit line |

Format in the PR body as fenced code blocks under a `## Evidence` heading, one block per Done-When item. If the artefact contradicts the intended claim, **revise the claim** — never massage the evidence (re-running until green, hiding skipped tests, commenting out asserts) is a P0 anti-pattern.

### Gate 4 — Self-Review (before requesting merge)

Before flipping the PR from draft to ready, Jules answers three questions in a `## Self-Review` section of the PR body. Short, candid answers.

1. **Did I drift from the spec?** List anything implemented that was not in the spec's `affects:` paths or `Done When:` list, and anything in the spec that was *not* implemented (with reason).
2. **What residual risk remains?** Edge cases not covered by tests, untested error paths, performance unknowns, downstream consumers not validated. If none, say "None observed" — do not pad.
3. **What pattern would I apply differently next time?** One sentence. This is the reflexion log; it feeds future spec authoring.

## 3. Working in `the-agency-system` repo

- **Branch:** the spec assigns it. **Default for fresh specs:** target `Master` directly. Your runtime picks the working branch name; never push to `main`, never force-push, never use `--no-verify`.
  - *Historical note:* spec stickers authored before the Wave-A rollout (PRs #30 and #46 merged) cite `claude/agency-plugin-refactor-PgMQ4` as the working branch. That branch was the staging area for Wave A — it still exists on remote, identical to Master tip, but **new sessions should target Master directly**. When a spec sticker disagrees with this protocol, this protocol wins.
- **Commits:** present tense, imperative, ≤ 72-char subject. Reference the spec ID in the body: `Spec: Plan/NNN-slug/spec.md`. Prefer many small commits over one large one; do not `--amend` someone else's commit.
- **Publish:** when the spec's `Done When:` items are all evidence-backed and gates 1–4 are green, invoke your runtime's standard publication flow (the `submit` / auto-PR tool exposed to you). PRs open as **ready** (not draft), targeting the spec-assigned base (usually `Master`). Required PR-body sections: `## Spec`, `## Confidence`, `## Evidence`, `## Self-Review`. Cite the spec path. PRs without all four sections are rejected. Do not shell out to `git push` or `gh pr create` directly — the publication flow owns remote writes, and over-specifying the mechanism wastes turns and frustrates the runtime's invariants.
- **After publish:** invoking the publication flow is the terminal step. The orchestrator verifies the branch on remote — you do not need to query `github.com` yourself.
- **Ambiguous spec?** Surface the ambiguity through your runtime's standard "blocked / awaiting clarification" mechanism (typically a draft PR or a message), paste the ambiguity verbatim, propose two interpretations, and stop. Do not interpret silently.

## 4. Source-repo conventions

Some specs reference external source repos (libraries, reference implementations) that Jules must read but not modify. See `Plan/SOURCES.md` for the canonical URL + branch table.

- Clone to the sandbox: `~/work/vendor/<repo>/`. Never inside `the-agency-system/`.
- Clone **read-only**: `git clone --depth=1 --branch=<tag> <url> ~/work/vendor/<repo>` and do not configure a push remote.
- Do **not** copy vendor source files into `the-agency-system` to "make them easier to find". Cite by URL + commit SHA in the spec or PR instead.
- Vendor sources are not part of the PR diff. If `git status` ever shows files under `vendor/`, you have made a mistake — back out before committing.

## 5. Anti-patterns (Jules MUST NOT)

1. Target `main` as the PR base or force-push any branch.
2. Skip the TDD gate because "the change is small". Smallness is exactly when bugs hide.
3. Claim `Done When` complete without pasting an artefact under `## Evidence`.
4. Amend or rebase commits authored by another agent or by the human.
5. Add a runtime or build dependency the spec did not list under `deps:`.
6. Create, move, or delete files outside the spec's `affects:` allow-list.
7. Decline to invoke the publication flow because of perceived sandbox limits. Your runtime's `submit` / auto-PR tool IS the publication flow; calling it is your final required action. The orchestrator handles verification on remote — your job ends at the submit call.

Each of these is a stop-the-line event. If Jules notices it post-hoc, revert the offending commit in a new commit and note it in the friction log.

## 6. Escalation

Jules has no synchronous user. The escalation primitive is a **comment on the open draft PR**, prefixed `@human:` and labelled `[BLOCKED: <reason>]`. Stop work and wait when any of these occur:

- Confidence score below 0.70 after a genuine attempt at Gate 1.
- The spec's `affects:` list cannot be satisfied without touching paths outside it.
- A test that must pass according to the spec fails for a reason the spec does not anticipate.
- An external API or fixture has changed shape since the spec was written.
- Two reasonable interpretations of a spec sentence produce materially different code.

Guessing forward in any of these cases is worse than waiting. The human would rather merge in 24 hours after a clarification round than revert in 1 hour after a confident wrong turn.

## 7. Claude Code plugin specifics

The work in this repo produces a single Claude Code plugin. Read these before any spec that touches plugin structure:

- [Claude Code Plugins Guide](https://code.claude.com/docs/en/plugins)
- [Plugins Reference (manifest schema)](https://code.claude.com/docs/en/plugins-reference)
- [FastMCP Code Mode docs](https://gofastmcp.com/servers/transforms/code-mode)

Key conventions for the unified plugin:

- `.claude-plugin/` contains exactly two files: `plugin.json` (always) and `marketplace.json` (when this repo also acts as a single-plugin marketplace, per Spec 002). Nothing else lives there — no skills, no commands, no `.gitkeep`.
- Skills auto-namespace: a folder `skills/novel/world-prompt-builder/SKILL.md` becomes `/agency-system:world-prompt-builder` in the slash menu (the `skills/novel/` subdir is organisational, not part of the slash name — unless the plugin opts into nested namespacing in the manifest).
- MCP server is registered via `.mcp.json` at repo root; use `${CLAUDE_PLUGIN_ROOT}` for paths, never absolute.
- Hooks (`hooks/hooks.json`) are synchronous in current Claude Code (the `async` flag is a future feature; do not rely on it).
- FastMCP pinned to ≥3.1.0 for Code Mode support; `CodeMode` import is wrapped in `try/except ImportError` for graceful fallback.
- Smoke tests live in `tests/smoke/` and validate: manifest parses, server boots, each slash skill resolves, MCP tool count matches expectation.

## 8. Publishing the work

**Jules: this is your terminal step.** When gates 1–4 are green and all `Done When` items are evidence-backed, invoke your runtime's publication flow (the `submit` / auto-PR tool). That call opens the PR. After it returns, you are done — stop. Do not re-verify, do not query GitHub, do not poll. The orchestrator owns verification.

If the publication call returns an error, surface it through the standard "blocked / awaiting clarification" channel and stop. Do not retry with shell-level `git push` or `gh pr create` — the runtime owns that surface and improvised pushes can corrupt the session.

---

> **§8-Appendix is for the orchestrator (Claude or a human), not for Jules.**
> Jules: stop reading here — you have no actions to take in the appendix.

### §8-Appendix — Orchestrator-side silent-fail recovery

The Jules backend normally publishes a completed session's diff by running an internal "finalize" flow that pushes the sandbox branch and opens a PR on `github.com`. This flow has intermittent silent-fail modes — the session transitions to `COMPLETED` but no branch lands on the remote. `state=COMPLETED` is *not* terminal; it means "session is idle, awaiting input". A focused `jules_message` ("your state is COMPLETED but I can't find your branch on origin — please publish and reply with the PR URL") frequently nudges the session through; give ~5 minutes per probe.

After 2–3 probes still produce no branch, the orchestrator falls back to API extraction (deterministic, single-author):

1. `GET https://jules.googleapis.com/v1alpha/sessions/{sid}`.
2. Read `outputs[*].changeSet.gitPatch.unidiffPatch` from the response — the canonical work artefact.
3. Save the patch to disk; never echo its body into the orchestrator's stdout — large patches pollute the LLM context window. The repo ships a context-safe extractor at `tools/jules-patch-extract.py` that writes to `/tmp/jules-patches/{sid}-out{i}.patch` and prints only `{bytes, files, first_files[]}` stats.
4. Apply via the GitHub MCP push path (`mcp__github__create_branch` + `mcp__github__create_or_update_file` for each file in the patch + `mcp__github__create_pull_request`). The MCP path produces `web-flow`-signed commits, which the local CODESIGN_MCP backend currently cannot.
5. Preserve Jules's authorship in the recovery PR body via `Co-authored-by: google-labs-jules[bot] <…>` and note in `## Spec` that publication was via API extraction rather than the auto-flow.

Do not re-dispatch a fresh Jules session on the same spec for the same work — the patch already exists on the original session's API record and a fresh session will burn quota for no incremental output. Re-dispatch is reserved for genuine implementation failures (state = `FAILED` with empty `outputs[]`, or `COMPLETED` with a 0-file patch).

When briefing Jules, phrase the publication requirement openly: *"publish your work via the standard flow."* Do not enumerate `git push`, `gh pr create`, or recovery mechanics in the Jules prompt — Jules treats those as constraints on its own behaviour and may refuse to submit at all. The appendix above is for the orchestrator only and must not leak into Jules-facing prompts.
