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

- **Branch:** the spec assigns it. **Default for fresh specs:** target `Master` directly. Never push to `main`, never force-push, never use `--no-verify`.
- **Spatial awareness first.** Before any change, call `list_files(<dir>)` and `read_file(<target>)` on every file you intend to touch. Editing a file you have not read is a Gate-1 violation; the model hallucinates surrounding context when it has not seen the current bytes.
- **Edits:** prefer `replace_with_git_merge_diff` over `write_file` for partial changes — it scopes the diff to the affected lines and avoids whole-file rewrites that bloat the patch and risk silent omissions. Use `write_file` only for new files or genuine full-file rewrites.
- **Shell work:** `run_in_bash_session` shares a single persistent bash state across calls — exported env vars, activated venvs, and CWD all carry over. Use it for `pytest`, `ruff`, `mypy`, `pip install`, `git status`, and any tooling not exposed as a standard tool. Append `&` and redirect logs (`cmd > log.txt 2>&1 &`) for long-running servers; surface their output with `read_file log.txt`.
- **`AGENTS.md` is binding.** This protocol lives at `Plan/JULES_PROTOCOL.md`, but any `AGENTS.md` you find while exploring the directory tree of your target paths is a localised system-prompt overlay (nested files override parents). Read and obey them before finalising your plan.
- **Commits:** present tense, imperative, ≤ 72-char subject. Reference the spec ID in the body: `Spec: Plan/NNN-slug/spec.md`. Prefer many small commits over one large one; do not `--amend` someone else's commit.
- **Pre-submit check:** call `pre_commit_instructions()` before `submit()`. It returns the dynamic linting / testing checklist the sandbox expects; satisfy each item in `run_in_bash_session` before submitting.
- **Critic pass:** after Gate 2 is green, call `request_code_review()` to invoke the Jules Critic. Its findings are a free Gate-4 dry-run — address them before flipping the PR to ready.
- **UI changes:** call `frontend_verification_instructions()` to get the Playwright boilerplate, run the script in `run_in_bash_session`, then call `frontend_verification_complete(screenshot_path=...)` so the screenshot is attached to the session for human review.
- **Publish:** invoke `submit(branch_name, commit_message, title, description)` when all gates are green and `pre_commit_instructions()` is satisfied. PRs open as **ready** (not draft), targeting the spec-assigned base (usually `Master`). Required PR-body sections: `## Spec`, `## Confidence`, `## Evidence`, `## Self-Review`. Cite the spec path. Do **not** use `run_in_bash_session` to run `git push` or `gh pr create` — `submit()` owns remote writes; improvised pushes break the session.
- **After publish:** `submit()` is the terminal call. Stop. Do not poll, do not re-query, do not message the user. The orchestrator owns post-publish verification.
- **Ambiguous spec?** Call `request_user_input(message)` once with the ambiguity verbatim and two proposed interpretations, then stop. Do not interpret silently.

## 4. Source-repo conventions

Some specs reference external source repos (libraries, reference implementations) that Jules must read but not modify. See `Plan/SOURCES.md` for the canonical URL + branch table.

- Clone via `run_in_bash_session`: `git clone --depth=1 --branch=<tag> <url> ~/work/vendor/<repo>`. Never inside `the-agency-system/`. Do not configure a push remote.
- Do **not** copy vendor source files into `the-agency-system` to "make them easier to find". Cite by URL + commit SHA in the spec or PR instead.
- Vendor sources are not part of the PR diff. If `git status` shows files under `vendor/`, you have made a mistake — back out before submitting.

## 5. Anti-patterns (Jules MUST NOT)

1. Target `main` as the PR base or force-push any branch.
2. Skip the TDD gate because "the change is small". Smallness is exactly when bugs hide.
3. Claim `Done When` complete without pasting an artefact under `## Evidence`.
4. Amend or rebase commits authored by another agent or by the human.
5. Add a runtime or build dependency the spec did not list under `deps:`.
6. Create, move, or delete files outside the spec's `affects:` allow-list.
7. Decline to call `submit()` because of perceived sandbox limits. `submit(branch_name, commit_message, title, description)` IS the publication primitive; calling it is your final required action. The orchestrator handles verification on remote — your job ends at the submit call.
8. Treat `state=COMPLETED` (your own session state, visible to the orchestrator) as a deliverable. It means "idle, awaiting input" — not "done". The deliverable is the `submit()` call plus the PR it produces.

Each of these is a stop-the-line event. If Jules notices it post-hoc, revert the offending commit in a new commit and note it in the friction log.

## 6. Escalation

Jules has no synchronous user. Two escalation primitives, used for different cases:

- **Blocking, pre-PR:** `request_user_input(message)` — pauses the session until the human answers. Use for ambiguity that prevents progress before any PR exists.
- **Non-blocking / post-PR:** `message_user(message, continue_working=False)` or a comment on the open PR prefixed `@human:` and labelled `[BLOCKED: <reason>]`. Use to surface status the human should see at next check-in.

Stop work and escalate when any of these occur:

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

**Jules: this is your terminal step.** When gates 1–4 are green and all `Done When` items are evidence-backed:

1. Call `pre_commit_instructions()`. Run every checklist item it returns in `run_in_bash_session` and capture the output for `## Evidence`.
2. (Optional but recommended) call `request_code_review()` and address Critic findings.
3. Call `submit(branch_name, commit_message, title, description)`. That call opens the PR.

After `submit()` returns, you are done. Stop. Do not re-verify, do not query GitHub, do not poll.

If `submit()` returns an error, call `request_user_input` with the error verbatim and stop. Do not retry via `run_in_bash_session` `git push` or `gh pr create` — `submit()` owns remote writes and improvised pushes corrupt the session.

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
