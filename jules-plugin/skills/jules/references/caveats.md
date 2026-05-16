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
