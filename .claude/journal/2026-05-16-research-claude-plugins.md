# Research: Claude Code Plugins (2026-05-16)

## Plugin layout (mandatory)

```
plugin-root/
├── .claude-plugin/plugin.json   # ONLY file in this dir
├── skills/<name>/SKILL.md       # auto-namespaced as <plugin>:<skill>
├── commands/<name>.md           # legacy flat-file form
├── hooks/hooks.json
├── .mcp.json                    # MCP servers
├── bin/                         # added to PATH while plugin is active
└── README.md                    # recommended
```

`plugin.json` minimum: `{ "name": "kebab-case", "version": "1.0.0" }`.

## MCP server inside a plugin — critical substitution variables

- `${CLAUDE_PLUGIN_ROOT}` — install dir, **ephemeral** across updates
- `${CLAUDE_PLUGIN_DATA}` — persistent state, survives updates (venvs go here)
- `${CLAUDE_PROJECT_DIR}` — user's working tree
- `${ENV_VAR}` — passthrough from caller's env
- `${user_config.KEY}` — interactive config

**Bash defaults like `${VAR:-default}` are NOT documented as supported.** Use a wrapper script for defaults, or expose via `userConfig`.

## Skills inside a plugin

Frontmatter keys: `name`, `description` (drives auto-invoke; combined ≤1536 chars), `argument-hint`, `model`, `allowed-tools`, `disable-model-invocation`, `user-invocable`, `context: fork` + `agent: Explore` (run in subagent).

Installed namespace: `/plugin-name:skill-name`.

## Hooks

`hooks/hooks.json` schema identical to `settings.json`. 30+ events. Types: `command`, `http`, `mcp_tool`, `prompt`, `agent`.

## Installation

```
/plugin marketplace add owner/repo
/plugin install plugin-name@marketplace-name
claude --plugin-dir ./local-plugin       # dev/test
```

`/reload-plugins` picks up edits live.

## Current jules-plugin/ scaffold — what's broken

1. **`.mcp.json` uses `${PWD}`** — must be `${CLAUDE_PLUGIN_ROOT}`. Current:
   ```json
   "env": { "PYTHONPATH": "${PWD}/mcp-server/src" }
   ```
2. **Skill in wrong location**: `skills/jules.md` should be `skills/jules/SKILL.md`.
3. **Skill body is a stub** (`(Body to be implemented in Phase 4f)`).
4. **No `marketplace.json`** for distribution.
5. **No `README.md`** at plugin root.
6. **No venv bootstrap hook** — MCP server uses bare `python3`.
7. **`commands/` has only a README placeholder.**
