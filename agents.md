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

**As an agent:** Use `process_thoughts` to record significant decisions, architectural choices, or user preferences at the end of a session. Use `search_journal` at session start to recall relevant past context before making decisions.

---

## 3. Google Drive File Operations MCP

**What it is:** Google Drive integration — read, write, copy, search, and manage files in Google Drive.

**Tool prefix:** `mcp__02fbb94b-1aaa-4e09-bcd2-e5748743f593__`

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

## 4. GitHub MCP

**What it is:** GitHub operations scoped to `netzkontrast/the-agency-system`.

**Tool prefix:** `mcp__github__`

**Key tools by task:**

| Task | Tools |
|---|---|
| Read a PR or issue | `pull_request_read`, `issue_read` |
| Create/update a PR | `create_pull_request`, `update_pull_request` |
| Comment | `add_issue_comment`, `add_reply_to_pull_request_comment` |
| Review | `pull_request_review_write`, `resolve_review_thread` |
| Browse code | `get_file_contents`, `search_code`, `list_commits` |
| Branches | `create_branch`, `list_branches`, `update_pull_request_branch` |
| Releases | `list_releases`, `get_latest_release` |
| CI / scanning | `run_secret_scanning` |
| Watch PR events | `subscribe_pr_activity`, `unsubscribe_pr_activity` |

**As an agent:** Always use these tools instead of the `gh` CLI (not available in remote sessions). After pushing a branch, always check for an existing PR before creating one.

---

## General agent dispatch rules

1. **Skills before MCP** — invoke the skill, let it call MCP tools.
2. **Subagents for parallel work** — spawn one agent per independent domain (separate tracks, separate research topics). See `CLAUDE.md` for full rules.
3. **Explore subagent for lookups** — use `subagent_type: Explore` for "where is X" or "which files reference Y" questions.
4. **private-journal for continuity** — record key decisions so future sessions can recover context via `search_journal`.
5. **Never push to `main`** — default branch is `Master`; all PRs target `Master`.

---

## Mandatory: Journal at session end

**Every session must close with a `process_thoughts` call.** This is not optional. The private-journal is the only persistent memory across sessions — without it, context is lost and future sessions repeat the same discovery work.

### What to record

| Field | What goes there |
|---|---|
| `reflections` | What happened this session, what decisions were made, what surprised you |
| `project_notes` | Technical discoveries: tool behaviors, branch conventions, schema quirks, gotchas |
| `user_context` | How the user communicates, what they care about, patterns you noticed |
| `technical_insights` | Broader engineering learnings that apply beyond this project |
| `observations` | Short atomic noticings that don't fit elsewhere |

### When to journal
- **End of every session** — always, no exceptions
- **After a significant decision** — when a non-obvious architectural or workflow choice is made
- **After discovering a gotcha** — any surprise behavior from a tool, MCP, or skill

### Recovering context at session start
At the start of a new session on this repo, run:
```
mcp__private-journal__search_journal("the-agency-system bitwize-music workflow")
mcp__private-journal__read_recent_entries()
```
This surfaces prior decisions and prevents re-discovering known patterns.
