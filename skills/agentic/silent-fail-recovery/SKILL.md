---
name: silent-fail-recovery
description: >
  Deterministic recovery for Jules sessions that reach COMPLETED state
  without producing a remote branch (the "silent-fail" bug). Use when the
  user says "Jules completed but no branch", "session COMPLETED but
  branch missing", "silent fail", "jules-patch-extract", or "recover
  patch from completed session" — or whenever an orchestrator has
  observed the auto-publish flow misfire.
---

## The rule (one sentence)

When a Jules session is `COMPLETED` but no matching branch exists on
`origin`, recover via API patch extraction — never re-dispatch.

## Why this exists

The Jules backend's auto-finalize flow (which is supposed to push the
sandbox branch and open a PR) fails silently on an intermittent basis.
The session transitions to `COMPLETED`, the sandbox shows a clean
`git status`, but no branch ever appears on the remote. The completed
work IS preserved on the session record — `outputs[*].changeSet.gitPatch.unidiffPatch`
contains the canonical unidiff — but only direct API access can reach
it. Re-dispatching a fresh session for the same spec burns quota for
zero incremental output: the patch already exists.

The canonical procedure is documented in `Plan/JULES_PROTOCOL.md §8`.
This skill is the operational shortcut that turns that document into a
five-step runbook.

## When this skill applies (and when it does not)

Applies:
- Session state = `COMPLETED`.
- `git ls-remote origin | grep <sid-or-alias>` returns nothing.
- Session has `outputs[]` populated with `gitPatch.unidiffPatch`.

Does NOT apply:
- Session state = `FAILED` (no outputs to recover; legitimate
  re-dispatch is allowed).
- Session state = `AWAITING_PLAN_APPROVAL` (call `jules_approve`).
- Branch DOES exist on remote (auto-flow worked; nothing to recover).
- Session has empty `outputs[]` despite COMPLETED (timed-out plan
  approval; this is a different failure mode — see
  `jules-plugin/skills/jules/references/state-machine.md`).

## The five-step recovery

1. **Confirm silent-fail.** Run `git ls-remote origin | grep <sid>` (or
   the branch alias if known). Empty output = silent-fail confirmed.
   If the branch is there, this skill does not apply.

2. **Extract the patch.** Run the context-safe extractor from inside
   the worktree:
   ```bash
   AGENCY_REPO_ROOT=$(pwd) python3 tools/jules-patch-extract.py <sid>
   ```
   Output is JSON: `{sid, patches: [{path, bytes, files, first_files[], has_more}]}`.
   The patch body is written to `/tmp/jules-patches/<sid>-out{i}.patch`
   and NEVER echoed to stdout. See the `context-safe-patch-handling`
   skill for the non-negotiable handling rules.

3. **Apply on a fresh branch off `Master`.** Re-run with `--apply`
   and `--branch`:
   ```bash
   AGENCY_REPO_ROOT=$(pwd) python3 tools/jules-patch-extract.py <sid> \
     --apply --branch claude/<spec-slug>-recovered-<sid-short>
   ```
   The extractor checks out `Master`, pulls, branches, then runs
   `git apply --stat` (filenames only — no diff body) followed by
   `git apply --whitespace=nowarn`. If apply fails on any patch, the
   extractor stops and reports `skipped_after_failure`.

4. **Commit preserving Jules's authorship.** Stage the changes and
   commit with the bot trailer:
   ```bash
   git commit -m "$(cat <<'EOF'
   <imperative subject under 72 chars>

   Co-authored-by: google-labs-jules[bot] <161369871+google-labs-jules[bot]@users.noreply.github.com>
   EOF
   )"
   ```

5. **Push and open the PR manually.** Push with `-u origin <branch>`,
   then open the PR via `mcp__github__create_pull_request`. In the
   body's `## Spec` section, note that publication was via API
   extraction rather than the auto-flow, and reference the original
   session ID for forensic traceability.

## What NOT to do

- **Do NOT re-dispatch a fresh Jules session on the same spec.** The
  patch already exists on the original session's record; a new session
  burns quota for zero output. Re-dispatch is reserved for genuine
  implementation failures (state = `FAILED`, empty `outputs[]`).
- **Do NOT instruct Jules to "git push" or "verify branch on github"**
  in the original prompt. The agent's sandbox cannot directly push —
  the auto-flow owns that step. Over-specific push instructions waste
  context and turns. Phrase publication openly: *"publish your work
  via the standard flow; if publication does not occur within one
  poll cycle, the orchestrator will recover via API extraction."*
- **Do NOT `cat` the saved patch.** See `context-safe-patch-handling`.

## Red flags

| Symptom | Action |
|---|---|
| Tempted to dispatch a "fresh" Jules session on the same spec | Stop. Run the extractor instead. |
| About to read `/tmp/jules-patches/<sid>-out0.patch` with `cat`/`head`/`grep` | Stop. The extractor already emitted the stats you need. |
| `--apply` reports `base_branch_prep_failed` | The repo state is dirty or the remote is unreachable. Resolve, then re-run. Do NOT swallow the error. |
| `apply_returncode != 0` and `skipped_after_failure` is set | An earlier patch failed; later patches likely depend on it. Resolve the failure, then re-run from scratch. |
| Session has empty `outputs[]` despite COMPLETED | Not a silent-fail — plan-approval timeout. Different recovery path. |

## References

- **`Plan/JULES_PROTOCOL.md §8`** — canonical specification of this
  recovery flow. This skill is a runbook view of that section.
- `tools/jules-patch-extract.py` — the extractor implementation.
  Read the docstring for `--apply` / `--branch` / `--repo` semantics.
- `skills/agentic/context-safe-patch-handling/SKILL.md` — the
  never-echo rule for the saved patch file.
- `skills/agentic/jules-orchestrator-discipline/SKILL.md` — broader
  orchestrator rules including the 2-silent-fails-then-switch policy.
- `tools/jules-archive/` — read-only audit trail of 2026-05-17
  forensic patches; useful when sanity-checking the recovery flow.
