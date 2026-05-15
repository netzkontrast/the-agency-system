# Agent Usage Guide

How to use the installed plugins and MCP servers when acting as or dispatching agents in this repository.

---

## 1. bitwize-music Plugin

**54 skills, 80+ MCP tools.** Full workflow: concept → lyrics → Suno → mastering → release.

**Invoke:** `/bitwize-music:<skill>` or `Skill("bitwize-music:<skill>")`. MCP tools (`mcp__plugin_bitwize-music_bitwize-music-mcp__<tool>`) only when a skill explicitly delegates.

| Group | Key skills |
|---|---|
| Routing | `resume`, `next-step` |
| Planning | `album-conceptualizer`, `new-album`, `album-ideas` |
| Writing | `lyric-writer`, `lyric-reviewer`, `lyric-refiner`, `voice-checker` |
| Production | `suno-engineer`, `pronunciation-specialist`, `pre-generation-check` |
| Audio | `import-audio`, `mix-engineer`, `mastering-engineer` |
| Release | `validate-album`, `explicit-checker`, `plagiarism-checker`, `release-director` |
| Promo | `promo-writer`, `promo-director`, `album-art-director` |
| Utils | `health-check`, `configure`, `clipboard`, `import-track`, `import-art` |

**Model routing (automatic):** Opus 4.7 → creative; Sonnet 4.6 → reasoning; Haiku 4.5 → mechanical.

**Critical MCP tools** (called by skills; rarely direct):

| Tool | Purpose |
|---|---|
| `update_track_field` | Update any track field — never hand-edit |
| `create_track` | Create new track scaffold |
| `rebuild_state` | Fix stale cache after bulk operations |
| `load_override` | Load cross-project preferences |
| `run_pre_generation_gates` | 6 hard gates before Suno generation |
| `get_skill` / `list_skills` | Inspect skill content |
| `find_album` / `get_album_full` | Album state lookup |
| `list_tracks` / `get_track` | Track queries |

---

## 2. private-journal MCP

**Semantic journaling with vector search.** Entries are committed and shared — collective session memory.

Invoke `Skill('journaling')` for the full discipline (tag ontology, `[STARTUP]` distillation, session lifecycle). This section is the *what*; the skill is the *how*.

| Tool | When to use |
|---|---|
| `process_thoughts` | Record observations, decisions, insights, user context |
| `search_journal` | Semantic search by concept |
| `list_recent_entries` | Browse recent entries |
| `read_recent_entries` | Read recent entries in full |
| `read_journal_entry` | Read a specific entry by path |

---

## 3. Google Drive MCP

**Tool prefix:** Session-specific UUID — discover with `ToolSearch("google drive file")` at session start.

Key tools: `read_file_content`, `create_file`, `copy_file`, `delete_file`, `download_file_content`, `get_file_metadata`, `get_file_permissions`, `list_recent_files`, `search_files`.

---

## 4. GitHub — CLI first, MCP as fallback

Check availability: `which gh && gh auth status`. If unavailable, fall back to `mcp__github__*`.

| Task | CLI (preferred) | MCP fallback |
|---|---|---|
| View PR | `gh pr view <n>` | `pull_request_read` get |
| List PRs | `gh pr list` | `list_pull_requests` |
| PR diff | `gh pr diff <n>` | `pull_request_read` get_diff |
| PR comments | `gh pr view <n> --comments` | `pull_request_read` get_comments |
| Create PR | `gh pr create` | `create_pull_request` |
| View issue | `gh issue view <n>` | `issue_read` |
| CI status | `gh pr checks <n>` | `pull_request_read` get_check_runs |

**MCP-only:** `subscribe_pr_activity`, `unsubscribe_pr_activity`, `resolve_review_thread`, `run_secret_scanning`.

---

## General dispatch rules

1. **Skills before MCP** — invoke the skill; let it call MCP tools.
2. **Subagents for parallel work** — one agent per independent domain; see `CLAUDE.md`.
3. **Explore subagent for lookups** — `subagent_type: Explore` for "where is X" or "which files reference Y".
4. **Journal for continuity** — `Skill('journaling')` at start; `process_thoughts` at end; every session.
5. **Never push to `main`** — default branch is `Master`; all PRs target `Master`.
