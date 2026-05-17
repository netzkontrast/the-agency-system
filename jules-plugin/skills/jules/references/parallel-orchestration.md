This file explains how to orchestrate multiple Jules sessions in parallel. Load this when you are tasked with a fan-out operation or need to manage multiple sessions at once.


You can run **many Jules sessions in parallel**. This is the canonical
flow for fan-out work (e.g. apply the same change across N tracks,
review N PRs, generate N test files):

### 1. Fan out

Provide a JSON or YAML file with one entry per task (see
`.claude/skills/jules/examples/fanout-tasks.json`). Each entry has
`{alias, title, prompt}` and optionally `{branch, source}`.

**Every prompt should include the branch convention** so harvest
goes through git, not patches:

> "When done, push your work to branch `jules/<alias>` on the source
> repository. Do NOT open a pull request."

This makes the alias the link between the local registry and the
remote branch — `jules_resolve_alias("auth-fix")` returns the
session id, and `origin/jules/auth-fix` holds the work.

Then:

```bash
# Either pass the opaque source explicitly:
JULES_DEFAULT_SOURCE="sources/<id>" \
  ./.claude/skills/jules/jules_bulk.sh fanout tasks.json
# …or pass an owner/repo shorthand (resolved via sources.list at create time):
JULES_DEFAULT_SOURCE="<org>/<repo>" \
  ./.claude/skills/jules/jules_bulk.sh fanout tasks.json
# …or omit and let jules_bulk.sh detect owner/repo from the git remote.
```

Each entry creates one session and registers it in `sessions.json` with
its alias so you can refer to it by name (`auth-fix`) instead of the
19-digit id.

Equivalently in MCP: call `jules_create` once per task in a single
turn. The Jules API accepts concurrent session creation; rate limits
apply per account.

### 2. Watch all of them at once

```bash
python3 .claude/skills/jules/watch_jules.py --daemonize
```

The watcher polls every session, writes one JSON line per state
transition to `notifications.jsonl`, and pushes the latest state into
the registry so `dashboard` always has fresh data.

### 3. Use the dashboard to triage

```bash
./.claude/skills/jules/jules_bulk.sh dashboard
```

Lists every active session in a compact table: alias | id | state |
title. Sessions in `AWAITING_PLAN_APPROVAL` are highlighted — those are
the ones blocking on you.

For an in-context check during a chat turn, call `jules_status_all`
(one API request, all sessions grouped by state).

### 4. Review the plan FIRST, then approve (do not auto-approve)

**The plan-approval gate is your cheapest review point. Do not
bypass it.** A misaligned plan caught at the AWAITING_PLAN_APPROVAL
stage costs one `jules_message` to redirect; the same misalignment
caught after the patch lands costs a re-spawn (a slot) and a full
fresh planning cycle.

The workflow for every fan-out:

1. Wait for each session to reach `AWAITING_PLAN_APPROVAL` (watch
   `jules_status_all` periodically, or run the watcher daemon).
2. For each one, call `jules_plan(session_id)` and READ THE STEPS.
   Check: are the right files in scope? Are the wrong files
   excluded? Is the plan over-engineered? Under-scoped?
3. If the plan is good, call `jules_approve(session_id)` —
   manually, one at a time.
4. If the plan needs refinement, call `jules_message(session_id,
   "<specific feedback>")`. The session will replan; loop back to
   step 1.
5. **Bulk-approve (`jules_approve_awaiting`) is for the case where
   you have ALREADY individually reviewed each plan and they are
   all good.** It is not for "auto-approve everything that's
   waiting" — that pattern wastes the review opportunity.

Auto-approving drivers (`while AWAITING: approve()`) are an
antipattern: they remove your cheapest course-correction lever and
guarantee you'll integrate work you didn't actually want. Only use
them when you've explicitly decided this batch doesn't warrant
review (e.g. a known-safe templated fan-out you've validated
before).

When you have N plans waiting AND you have already inspected them
in the dashboard or via `jules_plan`, you can batch-approve:

```bash
./.claude/skills/jules/jules_bulk.sh approve-awaiting
```

Or in MCP:

```
jules_approve_awaiting(only_titles_contain="lyric-review")
```

The `only_titles_contain` filter is your safety net — restrict the
bulk-approve to a known prefix so a stray unrelated session can't be
swept in.

## Fan-out reliability checklist (from PR #27 refactor experience)

1. Before dispatching a fan-out, verify the watcher daemon is alive
   (ps -p $(cat .claude/skills/jules/watcher.pid)). A dead watcher
   means silent failures.
2. Each session prompt should include the exact branch name and the
   EXACT shape of the expected reply (5-line summary + pytest verdict).
   Vague prompts trigger more clarifying questions per session, which
   multiplies under fan-out.
3. Wave-based dispatch (groups of 3-6 sessions with no inter-wave
   dependencies) integrates better than single-session-per-task
   because review cycles batch across the wave instead of context
   thrashing one at a time.
4. When integrating multiple Jules patches that touch overlapping
   files, use jules_patch_apply with only_files= to apply just the
   in-scope subset. Letting two sessions both rewrite tools/lifecycle.py
   via blind `git apply` lets the second one silently overwrite the
   first.
5. Quota cost of fan-out is len(unique_sessions), not retries. A
   respawn or a fresh continuation each burns one slot of the
   per-account daily quota. Budget 1.3x the expected session count
   for safety (correction loops + stalled-session respawns).
6. The plan-approval gate is your cheapest steering point. Spend the
   time to read each plan before approve/correct rather than batching
   blindly — the cost of a misaligned implementation is much higher
   than the cost of one extra review pass.

