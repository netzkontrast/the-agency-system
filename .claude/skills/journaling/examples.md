# Journaling — Example Entries (one per tag)

Each example shows a realistic entry as it would be passed to `process_thoughts`. The tag prefix is part of the value of the named field — there are no custom fields.

---

## `[LEARNING]` — field: `technical_insights`

```
[LEARNING] Run rebuild_state after any bulk create_track call, or list_tracks
returns stale cache and update_track_field fails with "track not found". Adding
the rebuild_state step turned a 30-minute debug into a no-op.
```

When to use: a workflow/sequencing improvement that future sessions should adopt. Always actionable.

---

## `[TOKEN-COST]` — field: `technical_insights`

```
[TOKEN-COST] PR comment retrieval: `gh api /repos/:o/:r/pulls/22/comments`
≈150 tokens, returns JSON. `mcp__github__pull_request_read get_review_comments`
≈600 tokens, returns wrapped object. Use gh api for reads; same data, 4× cheaper.
```

When to use: comparing two paths to the same answer. Include rough token estimates and the chosen winner.

---

## `[GOTCHA]` — field: `project_notes`

```
[GOTCHA] update_track_field rejects same-status transitions ("In Progress" →
"In Progress") and returns illegal_transition. Use force=true ONLY for cache
recovery, not to bypass workflow rules. Bit me when retrying after a network
blip; the first call had succeeded silently.
```

When to use: a non-obvious tool or codebase behavior that bit you once and will bite again. Include the reproducer.

---

## `[DECISION]` — field: `reflections`

```
[DECISION] Chose Haiku 4.5 for explicit-checker over Sonnet 4.6. Reasoning:
pure pattern match, no semantic reasoning required, runs 8× per album. Flip
this choice if the false-negative rate goes above 5% in routine QA. Reviewed
against last 20 runs: 0 false negatives, decision stands.
```

When to use: a path-not-taken worth recording. Include the alternative, why this option won, and the trigger that would flip the choice.

---

## `[USER-PREF]` — field: `user_context`

```
[USER-PREF] User wants opinionated recommendations, not menus of options.
"Just decide" is a frequent ask. When listing choices, lead with the
recommendation and label trade-offs explicitly — don't present options as
equally valid.
```

When to use: a durable user preference (style, cadence, vetoes). One sentence is fine; expand only if the preference has multiple facets.

---

## `[STARTUP]` — field: `project_notes`

```
[STARTUP] github-cli-vs-mcp            updated: 2026-05-15  supersedes: —

TL;DR (1 sentence): Use `gh` CLI for all GitHub reads in this repo; only fall
back to mcp__github__* when gh is unavailable (web/remote sessions) or for the
3 operations gh can't do.

Do:
- Check `which gh && gh auth status` at session start
- Use gh pr view / gh pr list / gh pr diff / gh pr checks for inspection
- Use `gh api /repos/:o/:r/pulls/<n>/comments` for structured comment access
- Track CLI-vs-MCP token cost in [TOKEN-COST] entries when comparing

Don't:
- Pass `base: main` to create_pull_request — default branch is `Master`, returns 422
- Use mcp__github__pull_request_read for routine reads (~4× the tokens)
- Skip the auth check; remote sessions silently lack gh CLI

Key commands:
- `gh pr view <n> --comments`  # ~200 tok, formatted markdown
- `gh api /repos/:o/:r/pulls/<n>/comments`  # ~150 tok, structured JSON
- `gh pr checks <n>`  # CI status

Known gotchas:
- gh CLI not present in code.claude.com web sessions → MCP fallback required
- subscribe_pr_activity / resolve_review_thread / run_secret_scanning have no gh equivalent → use MCP

Open questions:
- Is there a cheaper way to bulk-read CI logs than mcp__github__get_check_runs?

Source entries: 2026-05-15 (CLI table draft), 2026-05-15 (PR #22 review session), 2026-05-15 (token cost comparison)
```

When to use: 3+ scattered entries on a topic, OR a session reconstructed knowledge that should have been at hand. **Never written from a single session.**

---

## `[BLOCKER]` — field: `reflections`

```
[BLOCKER] mastering-engineer crashes on 96kHz/32-bit float WAV input with
SoX format-detection error. Tried: (1) resample to 48kHz/24-bit — works,
(2) explicit --rate flag — ignored, (3) chain through ffmpeg first — works
but adds 40s/track. Next session: file upstream issue on bitwize-music repo
with reproducer, decide whether to bake ffmpeg pre-step into skill.
```

When to use: an unresolved obstacle handed off to the next session. Must include the reproducer and what was tried — otherwise the next session repeats the work.

---

## What does NOT belong as a tagged entry

- **Prose narrative of what you did** — that's `reflections` (untagged), not `[LEARNING]`.
- **Questions to ask the user** — ask in chat; if unanswered, leave it as a `[BLOCKER]`.
- **External reference links** — semantic search finds them already; tagging adds nothing.
- **One-line observations with no actionable content** — use `observations` field (untagged); reserve tags for entries future-you will retrieve and act on.
