---
description: Distill scattered journal entries on a topic into a [STARTUP] brief
argument-hint: <topic>
---

Run the journaling skill's distillation flow for the topic provided as argument.

Steps:

1. Execute `bash .claude/skills/journaling/scripts/journal-distill.sh "$ARGUMENTS"` and read the output.

2. Inspect the results:
   - **If fewer than 3 entries matched:** report the count to the user and stop. Not enough material to distill yet — the threshold for a `[STARTUP]` is 3+ scattered tagged entries.
   - **If a `[STARTUP]` brief for this topic already exists and is <30 days old:** report its path, summarize its TL;DR, and ask whether to refresh or skip.
   - **If 3+ entries exist and no fresh `[STARTUP]`:** proceed to step 3.

3. Author a `[STARTUP]` brief following the template in `.claude/skills/journaling/SKILL.md` (search for `### Template`). Pull `Do` / `Don't` / `Key commands` / `Known gotchas` / `Open questions` from the aggregated entries. Set `updated:` to today's date. If superseding a prior brief, add `supersedes: <prior date>`.

4. Write the brief via `mcp__private-journal__process_thoughts` into the `project_notes` field. Do not also write `[LEARNING]` or `[TOKEN-COST]` content in the same call — the brief is a distillation, not a new observation.

5. Report to the user: the new entry's path, the topics it consolidates, and which old entries it supersedes (if any).
