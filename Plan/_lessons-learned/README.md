# Lessons Learned — Jules orchestration wave (2026-05-17)

Real-time observations captured during the multi-session Jules fanout for `the-agency-system` plugin refactor. Each lesson is one markdown file with a YAML frontmatter (severity, what it touches) and a tight body (~150–400 words).

At the end of the session, I (or whoever runs the post-mortem) reads every file in this folder and authors **Plan/099-jules-orchestration-improvements/spec.md** — a meta-spec proposing concrete changes to:

- `Plan/JULES_PROTOCOL.md` (gate text, anti-pattern list, escalation)
- The spec template (frontmatter fields, `affects:` discipline, vendor-port idioms)
- The Jules skill and MCP (any new tools / clarified tool docstrings)
- A new lightweight session-log MCP server for token-efficient post-mortem analysis (the side-quest from the human's last message)

## File naming

`NN-short-slug.md` — `NN` is the order observed (not severity). Sort numerically for chronological view, sort by `severity` frontmatter for action-priority view.

## Frontmatter schema

```yaml
---
lesson_id: NN
slug: short-kebab-case
severity: high | medium | low
seen_in: [spec-NNN, ...]     # specs that exhibited the pattern
applies_to:                    # what would absorb the fix
  - jules-protocol             # change JULES_PROTOCOL.md
  - spec-template              # change the spec template
  - jules-mcp                  # add/clarify Jules MCP tools
  - spec-author                # change my behaviour authoring specs
  - review-subagent            # change the code-review subagent template
captured_at: 2026-05-17
---
```

## Final-TODO (side-quest)

Build a small **session-log MCP server** (probably FastMCP, token-efficient, append-only JSONL or SQLite-backed) that records:

- Per-Jules-session: state transitions, agent messages, user messages, plan content, PR URL, patch summary, merge outcome.
- Per-spec: dispatch prompt, review-subagent verdict, blocker count, time-to-merge.
- Per-review: blockers found, blockers fixed.

Tools: `session_log_record`, `session_log_query`, `session_log_summary`, `session_log_export_md`.

Goal: after a wave, run `session_log_summary` to see "which specs had the most rework, which patterns recurred, where the discipline broke down" — without re-reading the entire Jules activity stream by hand.

This becomes its own spec (probably **Plan/100-session-log-mcp/spec.md**) — written from the lessons collected here.
