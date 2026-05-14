# the-agency-system — Claude Code instructions

Working tree for **the-agency-system** music projects and for the
[bitwize-music](https://github.com/bitwize-music-studio/claude-ai-music-skills)
plugin that produces them.

## Session start — required check

At the start of every session, verify the **`bitwize-music-mcp`** MCP
server is running. Recovery, in order:

1. **Start a new session first.** Slash commands (including
   `/bitwize-music:health-check`) depend on the plugin being wired
   into the session, so a restart is the cheapest way to re-trigger
   the `SessionStart` hook in `.claude/settings.json` — it calls
   `.claude/scripts/setup-bitwize-music.sh`, which provisions
   `~/.bitwize-music/venv` and renders `~/.bitwize-music/config.yaml`.
2. Once the new session is up, run `/bitwize-music:health-check` to
   confirm `bitwize-music-mcp` is registered and healthy.
3. If the hook didn't fire (e.g. `~/.bitwize-music/setup.log` is
   missing), run the script manually, then start a new session:
   ```bash
   bash .claude/scripts/setup-bitwize-music.sh
   ```
   The script self-locates from its own path, so no env vars are
   required. Logs: `~/.bitwize-music/setup.log`.
4. If the plugin itself isn't installed (`~/.claude/plugins/installed_plugins.json`
   doesn't list `bitwize-music@bitwize-music`), the marketplace entry
   in `.claude/settings.json` hasn't been resolved — re-add the plugin
   from the marketplace before retrying.

## MANDATORY: Use subagents for independent or context-heavy work

**Default to subagents when a task is independent, parallelizable, or
context-heavy.** They protect the main session's attention budget and
return only a focused summary.

When to delegate:

- **Parallel research** (multiple topics, multiple research runs, multiple
  source dumps) → spawn one `general-purpose` subagent per topic in a
  single message; they run concurrently.
- **Locating code or content** ("where is X defined", "which files
  reference Y", "find all overrides that mention Z") → use the `Explore`
  subagent. Read-only, fast, optimised for grep-style lookups.
- **Long-form file analysis** (read 5+ files, compare, summarise) →
  delegate to a subagent so the raw content doesn't fill the main context.
- **Independent draft work** (drafting lyrics for unrelated tracks in
  parallel, generating multiple Style Box variants) → one subagent per
  draft, single message, parallel execution.
- **Audits / surveys** ("which overrides still reference project X",
  "which tracks are missing pronunciation entries") → subagent.

When to stay in main context:

- **Sequential work** where each step depends on the previous one.
- **Stateful decisions** that need the user in the loop.
- **Single file edits** with a clear target.
- **Anything the user is actively reviewing turn-by-turn.**

Brief the subagent like a colleague: state goal, list what to check, cap
the response length ("under 200 words"). Trust but verify — when an
agent edits files, check the diff before reporting work as done.

## MANDATORY: Tools always win over handcrafting

**If a tool exists for the operation, use the tool — never edit by hand.**
This applies to every layer:

- **Status / explicit / field changes** → use `update_track_field` MCP,
  not Edit on the Track Details table.
- **Creating tracks** → `create_track` MCP, not `Write` of a hand-rolled
  scaffold.
- **Cache out of sync (`track not found`)** → run `rebuild_state` MCP
  *first*, then retry the proper tool. Do not fall back to Edit.
- **Loading overrides** → `load_override` MCP, not bare `Read`.
- **Album coherence / validation / pre-generation gates** → the
  matching MCP tool, not a manual checklist.

Hand-editing is only acceptable when the tool surface genuinely doesn't
cover the operation (e.g. drafting prose inside the Concept section,
where there is no setter). Whenever you reach for `Edit` on a track or
album file, first ask: **"Is there a tool that owns this field?"** If
yes, use it.

This is mandatory and overrides any habit of "just fix it inline."

## MANDATORY: Skills before MCP

**Always prefer invoking a `/bitwize-music:<skill>` slash command (or the
`Skill` tool with the same name) over calling the underlying
`mcp__plugin_bitwize-music_*` tools directly.** Skills carry the full
workflow, the guard rails, and the project's craft conventions. MCP
tools are the low-level primitives the skills are built on — use them
directly only when:

1. A skill explicitly delegates to a specific MCP call (e.g.
   `update_track_field` for a status flip), or
2. No skill covers the operation (rare — check `/bitwize-music:help`
   first), or
3. A skill has been invoked and it has explicitly asked you to perform
   the MCP call as part of its own workflow.

If you find yourself reaching for an MCP tool, first ask: **"Which
skill should be driving this?"** That question almost always has an
answer. Document the skill choice in your reasoning before invoking
the MCP tool — that record is the evidence the right path was taken.

## MANDATORY: Overrides are cross-project — albums hold album content

**Overrides (`overrides/*.md` and `overrides/*.yaml`) hold cross-project
preferences only.** Album-specific content — alter names, character
names, narrative DNA, per-track pronunciations, specific BPM identities,
named track titles — lives in the album folder, never in `overrides/`.

If an override file starts mentioning a specific album, character, or
genre identity, that's a signal it should be migrated:

- **Voice DNA / alter fingerprints** → `<album>/the-eleven.md`,
  `<album>/cast.md`, or whatever the project's convention is.
- **Project narrative / sequence / arcs** → `<album>/README.md`.
- **Track-specific pronunciations** → the track file's
  Pronunciation Notes table.
- **Album-specific research / sources** → `<album>/RESEARCH.md`,
  `<album>/SOURCES.md`.

What lives in `overrides/`: cross-project taste, lexicon avoidances,
genre→Suno mappings, vocal-register defaults, mastering presets for
genres the artist actually uses, documentary source-priority standards,
recurring German/foreign-language terms, the no-labels rule and
descriptive-only metatag conventions.

If a session inherits overrides from a previous project (HTML header
citing a different commit / repo), audit them before using the skills
that load them — obsolete project DNA will silently steer skills toward
the wrong aesthetic.

## Workflow patterns to remember

### Session-start audit (fresh session, especially after switching projects)

1. Run `/bitwize-music:health-check` — confirm MCP server, venv, skills.
2. Skim plugin CLAUDE.md (`~/.claude/plugins/marketplaces/bitwize-music/CLAUDE.md`)
   for any workflow updates.
3. Skim `~/.claude/plugins/marketplaces/bitwize-music/reference/overrides/override-index.md`
   if you'll be touching overrides — it documents merge behaviour per file.
4. Spot-check active overrides for project-specific content not matching
   the current album. If found, flag and offer cleanup before invoking
   skills that load those overrides.

### Common pitfalls (codified from prior misses)

- **State cache stale after bulk `create_track`**: run `rebuild_state`
  MCP before `update_track_field` on freshly-created tracks, or the
  field updates will return `track not found`.
- **`Write` requires prior `Read`**: the harness blocks `Write` until
  `Read` has been called on the target path in this session. For partial
  changes, use `Edit` (no Read requirement when targeting unique strings).
- **Track frontmatter validation fires on `Write`, not `Edit`**: the
  PostToolUse hook validates frontmatter only when a full file body is
  written. If you `Write` a track file, the frontmatter must include
  `status:` or the hook blocks the operation. `Edit` modifications are
  exempt.
- **Status transitions are MCP-enforced**: `update_track_field` rejects
  illegal transitions (e.g., `In Progress → In Progress`). Use `force=true`
  only when recovering from a cache mismatch, not to bypass workflow rules.
- **Don't name alters in Suno metatags**: the descriptive form
  `[male mid-baritone, weary, dry close-mic]` is permitted; the character
  form `[Container]` is forbidden by `voice-craft-principles.md`.

## Most important commands & skills

Invoke as slash commands: `/bitwize-music:<name>`.

| Command | Purpose |
|---|---|
| `/bitwize-music:health-check` | Verify plugin + MCP server status |
| `/bitwize-music:configure` | Show / edit active config |
| `/bitwize-music:help` | List all plugin skills |
| `/bitwize-music:about` | Plugin overview |
| `/bitwize-music:tutorial` | Guided walkthrough |
| `/bitwize-music:new-album` | Start a new album |
| `/bitwize-music:album-conceptualizer` | Develop album concept |
| `/bitwize-music:lyric-writer` | Write lyrics |
| `/bitwize-music:suno-engineer` | Craft Suno prompts |
| `/bitwize-music:mastering-engineer` | Master audio |
| `/bitwize-music:release-director` | Coordinate release |

### Where to find more

- **Full skill list (54 skills):** `/bitwize-music:help` or
  `ls ~/.claude/plugins/marketplaces/bitwize-music/skills/`
- **Skill source + READMEs:** `~/.claude/plugins/marketplaces/bitwize-music/skills/<name>/`
- **Reference docs (workflows, suno, mastering, release, …):**
  `~/.claude/plugins/marketplaces/bitwize-music/reference/`
- **Cross-project preferences (lyric craft, Suno mappings, research
  standards, vocal registers, mastering presets, voice-craft principles):**
  `overrides/lyric-writing-guide.md`,
  `overrides/suno-preferences.md`,
  `overrides/research-preferences.md`,
  `overrides/pronunciation-guide.md`,
  `overrides/voice-craft-principles.md`,
  `overrides/promotion-preferences.md`,
  `overrides/mastering-presets.yaml`
- **Album-specific content** (voice DNA, narrative, sources, art direction)
  lives inside each album folder, never in `overrides/`.
- **Active runtime config:** `~/.bitwize-music/config.yaml`

## Repository essentials

- `artists/the-agency-system/albums/<genre>/<slug>/` — album content
- `audio/`, `documents/` — Git LFS (run `git lfs install` once per machine)
- `overrides/` — user-preference files loaded by the plugin's `load_override` tool
- `.claude/settings.json` — enables `bitwize-music@bitwize-music` + SessionStart hook
- `.claude/scripts/setup-bitwize-music.sh` — venv + config bootstrap (run manually if the hook didn't fire; see above)

If config drifts, delete `~/.bitwize-music/config.yaml` and start a new
session to re-render from the template.
