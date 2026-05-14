# the-agency-system — Claude Code instructions

This repository is the working tree for the [bitwize-music](https://github.com/bitwize-music-studio/claude-ai-music-skills)
plugin. All album work — concepts, lyrics, mastered audio, research
documents — is stored here so it lives in git alongside the rest of the
configuration.

## Repository layout

```
the-agency-system/
├── CLAUDE.md                 # this file
├── README.md                 # short repo title
├── IDEAS.md                  # album brainstorming (auto-created on first use)
├── artists/                  # album content (auto-created by the plugin)
│   └── the-agency-system/
│       └── albums/
│           └── <genre>/
│               └── <album-slug>/
│                   ├── README.md
│                   └── tracks/
├── audio/                    # mastered audio (Git LFS)
├── documents/                # research PDFs and references (Git LFS)
├── overrides/                # per-skill preference files the plugin loads
│   ├── pronunciation-guide.md
│   ├── lyric-writing-guide.md
│   ├── suno-preferences.md
│   ├── research-preferences.md
│   └── ...
├── .claude/
│   ├── settings.json                          # plugin + SessionStart hook
│   ├── bitwize-music.config.template.yaml     # versioned config template
│   └── scripts/
│       └── setup-bitwize-music.sh             # bootstraps venv + config
└── .gitattributes            # Git LFS tracking for audio/** and documents/**
```

## How the plugin is wired up

- `.claude/settings.json` enables `bitwize-music@bitwize-music` and registers
  a `SessionStart` hook that runs `.claude/scripts/setup-bitwize-music.sh`
  on every session start.
- The setup script creates `~/.bitwize-music/venv`, installs the plugin's
  Python dependencies, and renders the config template into
  `~/.bitwize-music/config.yaml` on first run. `${REPO}` is substituted
  with this repository's absolute path.
- The rendered config points `content_root` at the repo root itself, so
  the plugin writes albums to `./artists/<artist>/albums/<genre>/<slug>/`.
- The plugin's MCP server (`bitwize-music-mcp`) auto-starts in each
  session and exposes 89 tools for album, lyric, mastering, and release
  workflows.
- Plugin skills appear as `/bitwize-music:<name>` slash commands
  (50+ skills: `album-conceptualizer`, `lyric-writer`,
  `mastering-engineer`, `suno-engineer`, `release-director`, …).

## Overrides

`overrides/` holds the user-preference files the plugin reads through
its `load_override` MCP tool. Twelve filenames are recognised; each one
is additive to the plugin's defaults. Four of them are pre-filled from
[netzkontrast/agency:skills/suno-lyric-writer](https://github.com/netzkontrast/agency/tree/main/skills/suno-lyric-writer)
and carry a provenance HTML comment at the top:

- `pronunciation-guide.md` — phonetic spellings for Suno
- `lyric-writing-guide.md` — lyric craft reference
- `suno-preferences.md` — Suno prompt + genre practices
- `research-preferences.md` — documentary research standards

The remaining files (`album-art-preferences.md`, `album-planning-guide.md`,
`explicit-words.md`, `mastering-presets.yaml`, `promotion-preferences.md`,
`release-preferences.md`, `sheet-music-preferences.md`) are stubs ready
for editing.

## Heavy binaries are versioned via Git LFS

`audio/` (`.wav`, `.flac`, `.mp3`, `.aiff`, `.aif`, `.ogg`, `.m4a`) and
`documents/` (`.pdf`, `.epub`, `.docx`) go through [Git LFS](https://git-lfs.com).
Before cloning or pushing on a new machine, install LFS and run
`git lfs install` once. Patterns are declared in the repo's `.gitattributes`.

## Working in the repo

- After cloning on a fresh machine, start a Claude Code session in the
  repo root. The `SessionStart` hook will provision the venv and render
  the config automatically — first run takes a few minutes for the pip
  install, subsequent runs are instant.
- If the local config drifts (e.g. paths point at a different repo
  location), delete `~/.bitwize-music/config.yaml` and start a new
  session; the template will re-render with the current `$CLAUDE_PROJECT_DIR`.
- Use `/bitwize-music:configure show` inside Claude Code to inspect the
  active configuration, and `/bitwize-music:health-check` for a full
  plugin diagnostic.
