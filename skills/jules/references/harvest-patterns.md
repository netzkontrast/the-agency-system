This file details how to harvest completed work from Jules sessions. Load this when a session is COMPLETED and you need to integrate its patch or pull request into the local repository.


The integrator-via-PR pattern is conceptually appealing but
**empirically unreliable on this account**: setting
`auto_create_pr=True` is silently ignored (the response shows
`automationMode: None`, no branch is pushed, no PR is opened —
verified on session `4878612101900714069`). Prompt-level
instructions to push or open PRs also fail or hallucinate
completion. The working harvest path is patches:

```python
jules_patch_summary(session_id)         # metadata only — files, line counts
jules_patch_apply(session_id, dry_run=True)   # validate cleanly
jules_patch_apply(session_id)           # apply on disk, token-cheap
```

The full unidiff is written to a tempfile, fed to `git apply`, and
discarded. Only metadata (`{applied, files, lines_added,
lines_removed, base_commit, suggested_commit_message}`) flows back
through the model — ~200 bytes vs. a diff that can be tens of KB.
This works reliably even when PR / branch publishing does not.

**The integrator-via-PR pattern remains valid in principle.** When
you confirm it works on your account (i.e. setting
`auto_create_pr=True` actually publishes a branch and opens a PR),
use it — it's strictly better than patches (richer audit trail,
multi-iteration history, cherry-pick granularity). The patch path
is the *fallback* when the publish path is unavailable. Probe with
one session before relying on either.

**The instruction template for `jules_create`:**

> "When done, make your work retrievable on the remote — your
> choice of mechanism: push to a branch named `jules/<slug>` if
> your tooling supports it, otherwise a draft PR or a regular
> PR from such a branch. Reply with the exact branch name and
> PR URL (if any). The PR is for integration, not necessarily
> for merging."

Equivalent in code: `jules_create(..., auto_create_pr=True)` is
the most reliable signal, but for some setups the prompt-level
instruction works too. When in doubt, set the flag AND include the
prompt sentence.

**The integrator flow once the branch lands:**

```
git fetch origin
git branch -r | grep jules/                                   # discover
git log --oneline <my-branch>..origin/jules/<slug>            # what's there
git diff <my-branch>...origin/jules/<slug> --stat             # scope
git diff <my-branch>...origin/jules/<slug> -- path/to/file    # only when needed
gh pr view <pr-number>                                        # PR body & metadata, if a PR was opened
```

**Then integrate at the granularity you want:**

```
git cherry-pick <commit-on-jules-branch>                # one commit
git checkout origin/jules/<slug> -- path/to/file        # one file
git merge --no-ff origin/jules/<slug>                   # the whole branch
```

If a PR was opened, **close it without merging** when you've
cherry-picked what you wanted — the closed PR is the audit
record. If no PR was opened, the branch itself is the record;
delete it from the remote once integrated, or leave it as a
historical reference.

**Why this beats both raw patches and "no PR please":**

- Zero token cost for diff inspection (git output never enters the
  model's context).
- Works with Jules's actual capabilities — no instructions Jules
  interprets the wrong way (the "don't open a PR" framing reliably
  causes some sessions to conflate it with "don't push").
- Real git history per session: blame, log, bisect, cherry-pick
  all work normally.
- The PR (when one exists) is metadata you can comment on / link
  to — useful for multi-orchestrator coordination.
- Multiple iterations on the same session push additional commits
  to the same branch — defuses the "outputs[].gitPatch is set
  only once" trap from principle #2 above.

**When to fall back to patches:**

- The target repo doesn't accept Jules's push or PR scope (rare).
- You need to transform the diff in-context before applying
  (e.g. strip unrelated changes). Use `jules_patch_summary` first,
  then `jules_patch` with explicit `max_bytes` if truly necessary.
- `jules_patch_apply(session_id, dry_run=True)` is still the
  preferred way to land a unified-diff locally when the integrator
  pattern doesn't apply.

**Two `COMPLETED` traps you must defuse:**

`Session.outputs[]` carries the **pull-request resource** when Jules opens
a PR (typically with `automationMode=AUTO_CREATE_PR`). Patches do NOT live
in `outputs` — they live as **activity artifacts**
(`activities[].artifacts[].changeSet.gitPatch.unidiffPatch`). The
`has_outputs` flag returned by `jules_get` therefore means "a PR was
attached", not "this session produced any work".

1. **`COMPLETED` with empty `outputs` AND no patch artifacts = abandoned.**
   The plan-approval gate timed out before you approved, or the agent
   produced nothing. Check via `jules_patch_summary(session_id)` — if it
   reports "no patch artifact found", the session is dead.
2. **`COMPLETED` with `has_outputs=True` may still be waiting on a
   "Create PR?" UI prompt.** The patch is real and harvestable, but
   the session is not finalized — it's sitting in the Jules web UI
   asking the human whether to open a PR. To finalize cleanly when
   you've already applied the patch locally:

   ```python
   jules_message(session_id, "Patch applied locally — no PR needed. Finalize.")
   ```

   To avoid the trap entirely on a fresh session, pass
   `auto_create_pr=True` at create time and let Jules open the PR
   without asking. Choose your default based on whether you want
   patches piped into your branch (current default) or independent
   PRs (auto mode).

