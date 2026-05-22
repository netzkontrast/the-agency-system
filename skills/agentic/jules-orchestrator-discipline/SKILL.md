---
name: jules-orchestrator-discipline
description: >
  Six hard-won orchestrator rules for dispatching, watching, and harvesting
  Google Jules sessions — derived from the 2026-05-17 silent-fail incidents.
  Use when the user says "dispatch Jules", "Jules session", "fan out specs",
  "orchestrate Jules", "Jules COMPLETED", "verify branch on remote", or
  "Codex bot review", or whenever a fresh Claude Code session begins
  coordinating any Jules-side work for `the-agency-system`.
---

## The rule (one sentence)

When you orchestrate Jules, verify every COMPLETED state on the remote
*before* trusting it, and never burn a third session on a spec that has
silently failed twice.

## Why this exists

On 2026-05-17 a single orchestration session burned ~15 Jules slots
because the model trusted the `COMPLETED` lifecycle event without
checking whether a branch actually landed on `origin`. The Jules backend
has a real silent-fail mode (see `Plan/JULES_PROTOCOL.md §8`) — the
session reports COMPLETED, the sandbox `git status` is clean, but no
branch ever materialises on the remote. Re-dispatching a fresh session
for the same spec wastes quota; the work already exists on the original
session's API record and only needs extraction.

This skill encodes the six rules so any future session inherits them
without having to re-learn the lesson.

## The six rules

1. **Verify before trust.** After every Jules `COMPLETED`, confirm the
   branch exists on `origin` BEFORE acting on the state:
   ```bash
   git ls-remote origin | grep <sid-or-branch-fragment>
   ```
   If the branch is missing, the session silently failed. Recover via
   `tools/jules-patch-extract.py <sid>` (see the
   `silent-fail-recovery` skill). NEVER re-dispatch a fresh Jules
   session on the same spec for the same work.

2. **2 silent-fails → switch.** If two Jules sessions on the same spec
   end in silent-fail, do NOT dispatch a third. Spawn a local subagent
   (Agent tool) and have it apply the API-extracted patch instead. The
   third Jules slot will almost certainly fail the same way and the
   quota is more valuable elsewhere.

3. **Patches > 2 KB never `head`/`grep`/`cat`-ed.** Always go through
   `tools/jules-patch-extract.py` — it writes the patch to
   `/tmp/jules-patches/<sid>-out{i}.patch` and emits only
   `{bytes, files, first_files[]}` stats. See the
   `context-safe-patch-handling` skill for the rationale.

4. **Wrap every `mcp__github__pull_request_read` in a focused subagent.**
   The main thread must never page through PR bodies — they routinely
   exceed 20 KB and pollute context. Dispatch a subagent whose only job
   is to read the PR and return a structured summary. Spec 106
   documents the permanent fix; until it ships, wrap manually.

5. **Wait for Codex bot review before merging non-trivial PRs.** On
   2026-05-17 the Codex bot caught 7 P1s that the spec-writing subagent
   missed. Non-trivial = touches >3 files OR changes any plugin
   surface (skills, MCP, hooks, manifests). Trivial doc/config tweaks
   may merge without waiting.

6. **`git rebase origin/Master` before publishing a PR.** Stale
   merge-base produces phantom-files in the diff — files the PR did
   not actually change appear as deletions. Rebase first, then
   `git push --force-with-lease`. The default branch is `Master`
   (capitalised); PRs targeting `main` are rejected with HTTP 422.

## Red flags

| Symptom | What it means | Action |
|---|---|---|
| `jules_get` returns `COMPLETED` but `git ls-remote` shows no branch | Silent-fail (Rule 1) | Run `tools/jules-patch-extract.py <sid>` |
| Two sessions on the same spec both silent-failed | Spec or backend is hostile (Rule 2) | Stop. Dispatch a local subagent. |
| About to `cat` a `.patch` file from `/tmp/jules-patches/` | Context poisoning risk (Rule 3) | Stop. Use the extractor's stats output instead. |
| Main thread is calling `mcp__github__pull_request_read` directly | Context bloat (Rule 4) | Wrap the call in a subagent via Agent tool. |
| PR has no `@codex` review yet, planning to merge | Quality regression risk (Rule 5) | Wait for the review unless the diff is trivial. |
| PR diff shows files you didn't touch | Stale base (Rule 6) | `git rebase origin/Master` + `git push --force-with-lease` |
| Creating a PR with `base: main` | Wrong default branch | Use `base: Master`. |

## Decision flow

```
Jules session reports COMPLETED
        │
        ▼
git ls-remote origin | grep <sid>
        │
   ┌────┴────┐
   │         │
 branch    branch
 present   missing
   │         │
   │         ▼
   │   tools/jules-patch-extract.py <sid>
   │         │
   │         ▼
   │   Was this the 2nd silent-fail on this spec?
   │         │
   │     ┌───┴───┐
   │     │       │
   │    yes      no
   │     │       │
   │     ▼       ▼
   │  local   apply patch,
   │ subagent push, open PR
   │     │       │
   ▼     ▼       ▼
       rebase origin/Master
              │
              ▼
       wait for Codex review (if non-trivial)
              │
              ▼
              merge
```

## References

- `Plan/JULES_PROTOCOL.md §8` — canonical recovery flow for silent-fail
- `Plan/_session-state/2026-05-18-next-session-goal.md` — origin of these
  six rules (the lessons-learned section)
- `skills/agentic/silent-fail-recovery/SKILL.md` — the recovery runbook
- `skills/agentic/context-safe-patch-handling/SKILL.md` — extractor usage
- `tools/jules-patch-extract.py` — the extractor script itself
- `jules-plugin/skills/jules/references/combined_watcher.py` — the
  multi-session polling pattern; use it when ≥2 sessions are in flight
