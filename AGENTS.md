# Agent Usage Guide

How to use the installed plugins and MCP servers when acting as or dispatching agents in this repository.

---

## 1. bitwize-music Plugin

**What it is:** Full music production workflow — concept → lyrics → Suno → mastering → release. 54 skills, 80+ MCP tools, multi-model routing.

**How to invoke:**
- Via slash command: `/bitwize-music:<skill-name>`
- Via Skill tool: `Skill("bitwize-music:<skill-name>")`
- MCP tools directly (only when a skill delegates to them): `mcp__plugin_bitwize-music_bitwize-music-mcp__<tool>`

**Rule:** Always invoke the skill first. Use MCP tools only when a skill explicitly asks for them or no skill covers the operation.

### Key skill groups

| Group | Skills | When to use |
|---|---|---|
| **Routing** | `resume`, `next-step` | Don't know what's next — invoke these instead of guessing |
| **Planning** | `album-conceptualizer`, `new-album`, `album-ideas`, `promote-idea` | Starting or planning an album |
| **Writing** | `lyric-writer`, `lyric-reviewer`, `lyric-refiner`, `voice-checker` | Drafting and polishing lyrics |
| **Production** | `suno-engineer`, `pronunciation-specialist`, `pre-generation-check` | Before Suno generation |
| **Audio** | `import-audio`, `mix-engineer`, `mastering-engineer` | After Suno output arrives |
| **Release** | `validate-album`, `explicit-checker`, `plagiarism-checker`, `release-director` | Pre-release QA |
| **Promo** | `promo-writer`, `promo-director`, `album-art-director` | Promotion and artwork |
| **Research** | `researcher`, `researchers-gov/financial/legal/tech/security/journalism/biographical/historical` | Sourcing documentary content |
| **Utils** | `health-check`, `configure`, `clipboard`, `import-track`, `import-art` | Maintenance and import |

### Model routing (automatic)
- **Opus 4.7** — creative work: lyrics, Suno prompts, album concepts, deep research
- **Sonnet 4.6** — reasoning: research coordination, pronunciation, workflow orchestration
- **Haiku 4.5** — mechanical: imports, validation, clipboard, health checks

### Critical MCP tools (used by skills, rarely called directly)

| Tool | Purpose |
|---|---|
| `update_track_field` | Update any track field — never hand-edit track files |
| `create_track` | Create a new track scaffold |
| `rebuild_state` | Fix stale cache after bulk operations |
| `load_override` | Load cross-project preferences |
| `run_pre_generation_gates` | Run the 6 hard gates before Suno generation |
| `get_skill` | Read a skill's full content |
| `list_skills` | List all registered skills |
| `find_album` / `get_album_full` | Look up album state |
| `list_tracks` / `get_track` | Query tracks |

---

## 2. private-journal MCP

**What it is:** Local, private journaling with semantic vector search. All data stays on-device — no external API calls.

**Storage:**
- Project notes: `.private-journal/` in repo root
- Personal thoughts: `~/.private-journal/`

**Tools:**

| Tool | When to use |
|---|---|
| `process_thoughts` | Record observations, decisions, technical insights, or user context mid-session |
| `search_journal` | Semantic search — find past decisions or context by concept, not just keywords |
| `list_recent_entries` | Browse what was recorded recently |
| `read_recent_entries` | Read recent entries in full |
| `read_journal_entry` | Read a specific entry by path |

**Journal entries are committed and shared** — they form the collective memory of all sessions working in this repo. Treat them as a living log, not throwaway scratch notes.

---

## Journal Workflow

Use the private-journal **frequently and deliberately** — not just at session end. Every meaningful moment in a session is worth capturing while it's fresh.

### Session Start — always

Before doing any work, recover context from prior sessions:

```
search_journal("learnings <task topic>")   # ALWAYS first — pick up prior learnings for this task
search_journal("the-agency-system")        # broad context recall
search_journal("bitwize-music workflow")   # plugin-specific patterns
read_recent_entries()                      # what happened last time
```

The `learnings` search is mandatory — it surfaces accumulated workflow improvements so you don't repeat solved problems. Replace `<task topic>` with the actual task at hand (e.g. `learnings lyric writing`, `learnings github PR`, `learnings mastering`).

### During the session — use often

Call `process_thoughts` whenever something noteworthy happens. Don't batch everything to the end — capture it while it's vivid.

| Moment | Field to use | Example |
|---|---|---|
| Something surprises you | `reflections` | "Didn't expect rebuild_state to be required after create_track" |
| You notice a recurring pattern | `observations` | "User always wants lyrics reviewed before Suno, even when skipping lyric-reviewer" |
| You discover a codebase/tool quirk | `project_notes` | "update_track_field rejects In Progress → In Progress; use force=true only for cache recovery" |
| A broader engineering insight clicks | `technical_insights` | "Parallel subagent dispatch keeps main context clean — use it aggressively for research" |
| You learn something about the user | `user_context` | "User communicates in short bursts; prefers action over clarifying questions" |
| You learn domain knowledge | `world_knowledge` | "Suno metatags use descriptive voice form, never character names" |
| You compare two approaches for token cost | `technical_insights` | "[TOKEN-COST] gh pr view ~200 tok vs mcp pull_request_read ~800 — prefer CLI for reads" |
| You find a better way to do something | `technical_insights` | "[LEARNING] ToolSearch before any MCP call — schemas not loaded until fetched" |

**Use multiple fields in a single call** — they're independent spaces. One `process_thoughts` call can write to all six at once.

> **Note:** The `process_thoughts` tool has fixed fields. `token_consumption` and `learnings` are not native parameters — they live inside `technical_insights` with a tag prefix (`[TOKEN-COST]` and `[LEARNING]`). This makes them retrievable via semantic search.

### [TOKEN-COST] — track and compare

Prefix entries in `technical_insights` with `[TOKEN-COST]` when comparing two approaches. Over time this builds a data-driven picture of what's expensive.

What to capture:
- The two options compared (`gh pr list` vs `mcp__github__list_pull_requests`)
- Relative cost (cheaper / more expensive / ~same)
- Which you chose and why
- Any quality difference (did one return more useful output?)

Search later: `search_journal("TOKEN-COST github")`, `search_journal("TOKEN-COST CLI MCP")`

### [LEARNING] — workflow improvements

Prefix entries in `technical_insights` with `[LEARNING]` for anything that makes future sessions faster or better. Think of it as a growing ops runbook.

What belongs here:
- A shortcut or pattern discovered ("always run rebuild_state after bulk create_track")
- A mistake to avoid ("don't pass base: main to create_pull_request — use Master")
- A better sequencing ("search_journal before research avoids duplicate work")
- Non-obvious tool behavior

Search at session start: `search_journal("learnings <topic>")` — the tag is lowercase-searchable via semantic matching.

### Session End — mandatory

Every session closes with a `process_thoughts` call. No exceptions.

Minimum at close:
- `reflections` — what happened, what was decided, what surprised you
- `project_notes` — any technical gotchas, tool behaviors, or workflow discoveries
- `user_context` — anything learned about the user's preferences or communication style
- `technical_insights` — use `[LEARNING]` prefix for workflow improvements, `[TOKEN-COST]` prefix for CLI-vs-MCP comparisons

### Searching past entries

The journal has **semantic search** — use natural language, not exact keywords:

```
search_journal("album workflow decisions")
search_journal("track status errors")
search_journal("user preferences for lyrics")
search_journal("bitwize-music plugin gotchas")
```

Also use for specific lookups:
```
list_recent_entries()          # most recent N entries
read_journal_entry("<path>")   # read a specific entry by path
read_recent_entries()          # full text of recent entries
```

### What makes a good entry

- **Be honest and direct** — this is private working memory, not a report
- **Capture the WHY** — not just what happened, but why a decision was made
- **Short and atomic is fine** — one sentence in `observations` is worth writing
- **Don't wait for "enough"** — three lines mid-session beats a rushed paragraph at close

---

## 3. Google Drive File Operations MCP

**What it is:** Google Drive integration — read, write, copy, search, and manage files in Google Drive.

**Tool prefix:** Session-specific UUID — not pinned in repo config, changes per environment. Discover at session start with `ToolSearch("google drive file")` — all matching tools share a common UUID prefix safe to use for that session.

**Tools:**

| Tool | Purpose |
|---|---|
| `read_file_content` | Read a Drive file's content |
| `create_file` | Create a new file in Drive |
| `copy_file` | Copy a file within Drive |
| `delete_file` | Delete a Drive file |
| `download_file_content` | Download binary/export content |
| `get_file_metadata` | Get file name, type, size, dates |
| `get_file_permissions` | Check sharing permissions |
| `list_recent_files` | List recently modified files |
| `search_files` | Search Drive by query string |

**As an agent:** Use when a task involves reading from or writing to shared Drive documents (e.g., uploading mastered audio, reading reference docs, exporting release assets).

---

## 4. GitHub — CLI first, MCP as fallback

**Prefer `gh` CLI over MCP tools whenever it is available** — CLI calls are cheaper on tokens than MCP round-trips and produce more compact output. Use MCP only when `gh` is unavailable (remote/web sessions) or when a specific operation has no CLI equivalent.

**Check availability at session start:**
```bash
which gh && gh auth status   # CLI available → use gh
```
If that fails, fall back to the MCP tools below.

**CLI equivalents for common tasks:**

| Task | CLI (preferred) | MCP fallback |
|---|---|---|
| View PR | `gh pr view <n>` | `pull_request_read` get |
| List PRs | `gh pr list` | `list_pull_requests` |
| PR diff | `gh pr diff <n>` | `pull_request_read` get_diff |
| PR comments | `gh pr view <n> --comments` | `pull_request_read` get_comments |
| Review comments | `gh api /repos/:owner/:repo/pulls/<n>/comments` | `pull_request_read` get_review_comments |
| Create PR | `gh pr create` | `create_pull_request` |
| View issue | `gh issue view <n>` | `issue_read` |
| List issues | `gh issue list` | `list_issues` |
| CI status | `gh pr checks <n>` | `pull_request_read` get_check_runs |
| Browse file | `gh api /repos/:owner/:repo/contents/<path>` | `get_file_contents` |

**MCP-only operations** (no CLI equivalent in this environment):
- `subscribe_pr_activity` / `unsubscribe_pr_activity` — event-driven PR watching
- `resolve_review_thread` / `unresolve_review_thread`
- `run_secret_scanning`

**Tool prefix:** `mcp__github__`

**As an agent:** After pushing a branch, always check for an existing PR before creating one. Track CLI-vs-MCP token cost in the journal under `token_consumption`.

---

## General agent dispatch rules

1. **Skills before MCP** — invoke the skill, let it call MCP tools.
2. **Subagents for parallel work** — spawn one agent per independent domain (separate tracks, separate research topics). See `CLAUDE.md` for full rules.
3. **Explore subagent for lookups** — use `subagent_type: Explore` for "where is X" or "which files reference Y" questions.
4. **private-journal for continuity** — record key decisions so future sessions can recover context via `search_journal`.
5. **Never push to `main`** — default branch is `Master`; all PRs target `Master`.

---

## Mandatory: Journal at session end

**Every session must close with a `process_thoughts` call.** This is not optional. The private-journal is the shared memory of all sessions working in this repo — without it, context is lost and future sessions repeat the same discovery work.

See the **Journal Workflow** section above for the full field-by-field guide, when to call during the session, and how to search past entries.
