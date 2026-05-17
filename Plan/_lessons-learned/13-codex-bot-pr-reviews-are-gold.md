---
lesson_id: 13
slug: codex-bot-pr-reviews-are-gold
severity: high
seen_in: [pr-30]
applies_to:
  - orchestrator-patterns
  - jules-protocol
  - review-subagent
captured_at: 2026-05-17
---

# The Codex bot review on PR #30 caught what I missed

## Pattern

PR #30 (the Plan PR against `Master`) accumulated **40 review comments** from `chatgpt-codex-connector[bot]` across 7 commits — automated, free, and shockingly high signal. A categorical breakdown of what it caught:

| Category | Count | Examples |
|---|---|---|
| Spec `affects:` drift | 7 | spec 001/002/013/014/015/020 missing test files / fixtures / git-mv source |
| Spec text contradictions | 4 | spec 002 deprecation-suffix wording vs Acceptance; spec 013 response-shape contradiction; spec 014 tool-name typo |
| Wrong CodeMode import path | 3 | spec 001 step 3, spec 008 step 76 — would silently disable Code Mode |
| Missing deps in pyproject | 2 | `jsonschema`, `pyyaml` — would fail clean-install collection |
| Code bugs in already-merged specs | 6 | StateCache swallows exceptions, no atomic write, migrator idempotency partial, `_migration` violates own schema, etc. |
| JULES_PROTOCOL contradiction | 1 | §116 "plugin.json only" vs spec 002 `marketplace.json` |
| Misc P2 (test pollution, format_checker, README typo) | 17 | mostly real, mostly fixable in one pass |

**Overlap with my manually-captured lessons:**
- Lesson 04 (affects: incompleteness) — Codex caught 7 instances; I caught 3.
- Lesson 06 (spec-vs-schema drift) — Codex caught 4 instances I'd missed.
- Lesson 01 (scratch files) — Codex didn't focus on this; I did.

The two review streams (manual lessons + Codex bot) are **complementary, not redundant**. Codex is mechanical and exhaustive on the spec text; my lessons are pattern-recognition across sessions.

## What to change

### Make Codex review a documented part of JULES_PROTOCOL

Add a §8 to JULES_PROTOCOL.md:

> **Automated review backstop.** The repository has Codex auto-review wired (see PR #30 for the comment style). Treat its comments as a free second-opinion review. Resolve P1 comments BEFORE merging the relevant spec; P2 comments become follow-up tickets. The orchestrator should poll Codex comments on the Plan PR and any spec PR via `mcp__github__pull_request_read get_review_comments` after every push.

### Orchestrator policy

- After EVERY commit to the work branch, poll PR #30 (or the spec PR) for new Codex comments via `mcp__github__pull_request_read method=get_review_comments`.
- For P1 comments on unmerged specs: patch the spec frontmatter / text in the next commit; reply to the Codex thread "addressed in commit `<sha>`".
- For P1 comments on already-merged specs: open a follow-up spec or hardening commit.
- For P2 comments: capture in a lessons-learned file or a tracked TODO; address opportunistically.

### Review-subagent prompt enhancement

The review-subagent template (lesson 05) should explicitly fetch any existing Codex comments on the same PR and consider them as input before producing its own verdict. Avoid duplicating Codex's findings; focus on what Codex couldn't catch (cross-spec consistency, JULES_PROTOCOL alignment, project-specific lore).

### Cost-benefit

Codex's 40 comments cost: $0 (already configured). My manual lessons capture: ~30 minutes of write-up. Both together caught ~95% of real issues in the wave. If I had to choose only one, **keep Codex** — it's broader and free. But the manual lessons add the "why this keeps happening" + "what to change in the meta-process" layer that Codex doesn't reach.

## Concrete deliverable for the meta-spec

- Patch `JULES_PROTOCOL.md` with §8 (automated review backstop).
- Update the review-subagent prompt template (saved in lesson 05) to fetch Codex comments first.
- Update the orchestrator-pattern documentation: poll Codex comments after every commit; resolve P1 before merge.
