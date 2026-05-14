# the-agency-system — Claude Code instructions

Working tree for Michael Schimmer's darkwave/industrial album triptych
and for the [bitwize-music](https://github.com/bitwize-music-studio/claude-ai-music-skills)
plugin that produces it.

## Session start — required check

At the start of every session, verify the **bitwize-music MCP server**
is running. If it is not, run `/bitwize-music:health-check` and, if
needed, start a new session so the `SessionStart` hook in
`.claude/settings.json` re-provisions `~/.bitwize-music/venv` and
launches `bitwize-music-server`.

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
- `.claude/scripts/setup-bitwize-music.sh` — venv + config bootstrap

If config drifts, delete `~/.bitwize-music/config.yaml` and start a new
session to re-render from the template.
