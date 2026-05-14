# the-agency-system — Claude Code instructions

Working tree for Michael Schimmer's darkwave/industrial album triptych
and for the [bitwize-music](https://github.com/bitwize-music-studio/claude-ai-music-skills)
plugin that produces it.

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
- **Project DNA (narrative, voice, sonic identity, audit):**
  `overrides/album-planning-guide.md`,
  `overrides/lyric-writing-guide.md`,
  `overrides/suno-preferences.md`,
  `overrides/research-preferences.md`
- **Active runtime config:** `~/.bitwize-music/config.yaml`

## Repository essentials

- `artists/the-agency-system/albums/<genre>/<slug>/` — album content
- `audio/`, `documents/` — Git LFS (run `git lfs install` once per machine)
- `overrides/` — user-preference files loaded by the plugin's `load_override` tool
- `.claude/settings.json` — enables `bitwize-music@bitwize-music` + SessionStart hook
- `.claude/scripts/setup-bitwize-music.sh` — venv + config bootstrap (run manually if the hook didn't fire; see above)

If config drifts, delete `~/.bitwize-music/config.yaml` and start a new
session to re-render from the template.
