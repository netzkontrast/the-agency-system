---
lesson_id: 05
slug: independent-review-subagent-is-load-bearing
severity: high
seen_in: [pr-34, pr-35, pr-36, pr-37, pr-38]
applies_to:
  - review-subagent
  - jules-protocol
captured_at: 2026-05-17
---

# Independent code-review subagent is load-bearing — keep it

## Pattern

Every PR in this wave got an independent code-review subagent pass before merge. Verdicts:

| PR | Spec | Subagent verdict | Blockers it caught |
|---|---|---|---|
| #34 | 003 statecache | APPROVE WITH FOLLOW-UP | 7 minor concerns (docstring shadow, cwd-relative path, vacuous conditional, missing confidence table, etc.) |
| #35 | 010 novel-layout | REQUEST CHANGES | 2 blockers: duplicate `type:` key in `world.md` (silently empty discriminator); README missing frontmatter (forced modified spec command) |
| #36 | 004 first attempt | REQUEST CHANGES | 5 blockers: broken imports, unwired StateCache, dead status.py, spec-012 revert, 3 scratch files |
| #37 | 019 migration | REQUEST CHANGES | 1 blocker: empty runbook (Git blob `e69de29`) |
| #38 | 004a music-lib-port | APPROVE | None — clean port; 2 minor doc-thinness concerns |

**Without the review subagent, all 5 would have merged silently.** Jules' own Self-Review #1 ("did I drift?") consistently said "no" even when the actual diff had drift. The independent eyes were not redundant.

## What to change

### Bake the review-subagent step into JULES_PROTOCOL

JULES_PROTOCOL §3 (working in the repo) should add a "Review" sub-step: "After Jules opens the PR, the orchestrator dispatches an independent code-review subagent before merging." Currently the review step is informal. Make it explicit.

### Standardise the review template

The 5 reviews used similar but ad-hoc structure. Lock the template:

```markdown
@jules — review of PR #NN.

## Independent review — Spec NNN (PR #NN)

### ✅ What's right
- ...

### ⚠️ Concerns (non-blocking)
- ... (cite file:line)

### ❌ Blockers (must fix before merge)
- ... (cite file:line)

### Verdict
APPROVE / APPROVE WITH FOLLOW-UP / REQUEST CHANGES — one-sentence rationale.
```

Save as `Plan/_templates/review-subagent-prompt.md` so future dispatches can reference it.

### Always include `@jules` in the review body

The human asked for this mid-session. Bake it into the template — every review starts with `@jules — review of PR #NN.` so the bot account receives a notification and engages with the comment thread (not just sees a passive review).

## Concrete deliverable for the meta-spec

Lock the review-subagent prompt as `Plan/_templates/review-subagent.md`. Update JULES_PROTOCOL.md to formalise the review step. Update the dispatch prompt template to remind the orchestrator to run a review pass per PR.
