This file lists caveats and constraints of the Jules skill. Load this to understand what the skill does NOT do, and specific pitfalls to avoid during parallel work.


- **Approve quickly.** The Jules backend appears to discard sessions
  that sit in `AWAITING_PLAN_APPROVAL` for too long — they end up in
  `COMPLETED` state with no patch artifacts. Treat `COMPLETED` with no
  artifacts (verify via `jules_patch_summary`) as `AWAITING_PLAN_APPROVAL`:
  fetch the plan and approve, or the work is lost.
- **Scope tasks to disjoint files.** Parallel sessions branch from the
  same base commit, so patches that touch the same file will conflict
  on apply.
- **Use aliases.** 19-digit ids are unusable in conversation; aliases
  scale to dozens of sessions without confusion.
- **Watch out for stale `list` responses.** `jules_list` can show a
  session as `IN_PROGRESS` for a few seconds after `jules_get` reports
  the real state. Use `jules_get` (per-session) as the authoritative
  state, not `jules_list`.
- **No more than 4 concurrent approves.** `jules_bulk.sh
  approve-awaiting` uses `xargs -P 4`. Higher concurrency risks 429s.

## What This Skill Does NOT Do

- **Does not edit local files.** Jules works on its own VM and pushes to
  the user's GitHub via the Jules GitHub app. The skill never modifies the
  local working tree on the user's behalf as part of a Jules session.
- **Does not commit or push.** The output is a Jules-generated PR URL.
- **Does not poll in the background.** Each status check is initiated by
  a fresh user prompt.
- **Does not cache the API key.** It is read live from `JULES_API_KEY`
  every invocation.
- **Does not retry destructive failures automatically.** A failed
  `approve` or `message` is reported, not silently re-attempted.
- **Does not cancel sessions.** The Jules API does not expose a
  cancel/delete/stop method, so `stop` requests are reported as
  unsupported instead of issuing doomed HTTP requests.

## Empirically observed traps (from PR #27 refactor)

1. **COMPLETED without artifacts ≠ dead.** A session can show state
   COMPLETED with no patch artifact and no PR output, yet still be
   paused waiting on a UI gate (e.g. a "Create PR?" prompt). Do NOT
   assume the work is lost. Recovery: send a jules_message asking the
   agent to continue ("Please continue and complete the brief…"); the
   state will transition to AWAITING_USER_FEEDBACK and the work
   resumes. Only respawn if a nudge produces no transition within
   ~10 minutes.
2. **jules_message during plan-approval can kill the session.** When
   a session is in AWAITING_PLAN_APPROVAL and you want to request
   changes, sending jules_message instead of jules_approve sometimes
   causes the session to interpret the message as a stop signal and
   transition to COMPLETED with no plan and no work. Safer pattern:
   if the plan is acceptable, jules_approve; if not, jules_message
   with the change request AND then verify the next state is
   PLANNING (re-plan in progress), not COMPLETED.
3. **Patch artifacts are retrievable while state is IN_PROGRESS.**
   jules_patch_summary and jules_patch_apply walk activities[]
   artifacts; they do not require the session to be COMPLETED. If a
   session is stuck IN_PROGRESS for >30 minutes but the latest
   progressUpdated activity shows artifacts written, fetch and
   integrate the patch immediately — don't wait for COMPLETED.
4. **Watcher liveness is not free.** watch_jules.py is a separate
   process; if it dies, state transitions stop being written to
   notifications.jsonl and any monitor that tails the log goes
   silent. Verify with `ps -p $(cat .claude/skills/jules/watcher.pid)`
   or `claude/journal` log lines before assuming a session is
   stalled. Restart with --daemonize.
