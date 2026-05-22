---
lesson_id: 01
slug: scratch-files-on-pr-body-composition
severity: high
seen_in: [spec-002, spec-004-first, spec-004a-retry]
applies_to:
  - jules-protocol
  - spec-template
captured_at: 2026-05-17
---

# Scratch files on PR-body composition

## Pattern (3 strikes in one wave)

- **Spec 002**: Jules committed `pr_description.md` (cleaned up after first review).
- **Spec 004 first attempt**: Jules committed `dummy_tools.py`, `fix_test.py`, `fix_tools_inline.py` — one contained the literal comment `"Wait, he said DO NOT GUESS"`.
- **Spec 004a retry**: Jules committed `pr_body.md` (the duplicate of the PR body that already lives on GitHub).

Every time Jules composes a PR body, it tends to draft into a tracked file first instead of using the submit tool directly. Anti-pattern #6 catches it after the fact, but the pattern reliably recurs.

## What to change

### JULES_PROTOCOL §5 anti-pattern #6 should add a sub-bullet:

> **Never compose PR body content into a tracked file.** The PR body goes into the PR via the submit tool, not into `pr_body.md`, `pr_description.md`, or any other markdown/text file at the repo root. If you need scratch space, use `/tmp/` — never commit it.

### Dispatch prompt language

Every dispatch prompt in this wave that mentioned "do not commit scratch files" worked for spec 019 and spec 004a retry — Jules ABSORBED the warning. Specs 002 and 004 first attempt were dispatched BEFORE this language was in the prompt template. So: bake the no-scratch-files line into the dispatch-prompt template, not just into JULES_PROTOCOL.md.

## Concrete deliverable for the meta-spec

Patch `Plan/JULES_PROTOCOL.md` §5 anti-pattern #6 with the sub-bullet above. Add an explicit "scratch files = files outside `affects:`" sentence in §3 (commits) too, so the rule appears both in the gate context and in the anti-pattern list.
