---
lesson_id: 14
slug: token-consumption-postmortem
severity: high
seen_in: [orchestrator-session]
applies_to:
  - orchestrator-patterns
  - jules-mcp
  - github-mcp
  - mcp-tooling
captured_at: 2026-05-17
---

# What consumed the most tokens in this orchestration session

## Symptom

By the time the user asked "purge unneeded messages", the context was at **692k / 1M (69%)** with **666k in Messages** — 96% of token spend was conversation history. The session was still functional but headroom for further work was thin.

## Top consumers (ranked by cumulative token spend across the session)

### 1. `mcp__github__pull_request_read` — single biggest sink

Every call dumps the FULL body of every PR/comment requested. There is no `summary_only` or `preview` flag. Sample call costs:
- `get` on PR #36 (15k-line PR with 4-section body): ~4k tokens.
- `get_review_comments` on PR #30 (40 review threads): ~25k tokens in ONE call.
- `list_pull_requests` (perPage=5): ~10k tokens (full body of every PR in the page, even merged unrelated ones like #29, #22, #23).

I called these ~15 times across the session. Estimated cumulative: **~150-200k tokens**, ~25-30% of total message spend.

### 2. Reading vendor / large files inline

- `bitwize-music v0.91.0` plugins-reference docs (`WebFetch`, 63KB cached): ~16k tokens (read partially, but the cache excerpt counted toward context).
- Spec 015 / 020 / Codex review excerpts when surveying `affects:`.
- The Plan PR (#30) body itself appearing in every `list_pull_requests` page.

Estimated cumulative: **~80-100k tokens**.

### 3. Jules activity-stream pagination

- `jules_activities` returns full payloads by default (`summary_only=False`). I sometimes paginated through 100+ activities to find an agent message.
- Per-call ~3-5k tokens; called ~10 times.

Estimated cumulative: **~40-50k tokens**.

### 4. Bash heredocs with large stdout

- `git pull_request_read get_diff` on PR #36 (~15k lines patch): ~12k tokens.
- `jules_patch_summary` on multi-file PRs: dumps full file list each time.

Estimated cumulative: **~30-40k tokens**.

### 5. Repeatedly inlining the same Plan PR body

The `mcp__github__list_pull_requests` tool returned the full PR #30 body (~3k tokens) in EVERY paginated call. I called it ~6 times. That's ~18k tokens of pure duplication.

## What to change

### Orchestrator policy

1. **Default to subagents for any tool call expected to return >2KB.** Pull_request_read, jules_activities, get_review_comments, list_pull_requests — all should be wrapped in `Agent({ subagent_type: "general-purpose", prompt: "Call <tool>, return ONLY <specific fact>" })`. The agent absorbs the token cost; I get the summary.
2. **Cache PR-body snapshots in lessons or scratch files.** Re-fetching the same PR body 6 times wastes ~15k tokens. A `Plan/_session-cache/pr-30-body.md` would let me grep locally for ~zero cost.
3. **Use `summary_only=True` for jules_activities** unless I genuinely need full message text. I forgot this most of the time.
4. **Use `mcp__github__pull_request_read method=get_files` instead of `get_diff` for size assessment.** `get_files` returns metadata only by default; `get_diff` dumps the full patch.

### GitHub MCP — request features

The single biggest improvement to MCP tool design would be:

- **`mcp__github__list_pull_requests` needs a `body_preview_chars` parameter** (default ~500 or 0) so the full body isn't dumped on every page.
- **`mcp__github__pull_request_read get_review_comments` needs a `summary_only` mode** that returns `[{thread_id, path, line, author, severity, title}]` without the full body of each comment. Then a follow-up `get_thread(id)` for the one you care about.
- **`jules_patch_summary` is already concise — keep it.** But add a `mode="filenames_only"` for the cheapest possible call.

### Jules MCP — request features

- **`jules_session_summary(sid)` returning {state, title, last_5_activities, pr_url, patch_size_lines}** in one call. Currently I make 3 calls (get + activities + patch_summary) each costing ~2-5k tokens.
- **`jules_pr_url(sid)` quick lookup** (mentioned in lesson 12) — saves a `list_branches` call (~3k tokens).

### Process-level: trim my own verbosity

- Long explanatory paragraphs in user-facing messages added up. The user is watching the workflow; they don't need 5-paragraph status reports after every dispatch.
- The "thinking" sections (internal monologue) before tool calls may have been verbose. (I can't see them post-hoc, but should aim for tight reasoning.)
- Markdown tables in status reports are token-heavy. Plain bullets cost ~30% less for the same information.

## Concrete deliverable for the meta-spec

Two items:
1. **Patch the Jules MCP** with `jules_session_summary` and `jules_pr_url` per lesson 08 + this lesson.
2. **Document orchestrator-pattern best practices** as a new `skills/agentic/orchestrator-discipline/SKILL.md`:
   - Default-to-subagent for >2KB tool calls.
   - Cache PR bodies locally after first fetch.
   - Always `summary_only=True` on activity streams.
   - Markdown tables only when comparison density is justified.

The session-log MCP (lesson 11) becomes the obvious place to record token-spend metrics per-tool — adding `tokens_used` to each event would let `session_log_summary` answer "where did the budget go?" automatically next time.

## Single biggest takeaway

**GitHub MCP tools have no concept of "preview" or "summary" mode.** Every read is a full body dump. For orchestrator-pattern workloads (poll many PRs, read many comments), this is the dominant cost. The fix is either (a) request the upstream MCP tools add preview modes, or (b) always wrap them in subagent calls. Until (a), do (b).
