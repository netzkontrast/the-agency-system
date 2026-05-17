# Audit: Current Jules Suite + jules-plugin Scaffold (2026-05-16)

## Current suite (the .claude/ paths)

| File | Lines | Role |
|---|---:|---|
| `.claude/mcp/jules-mcp/server.py` | 1,023 | FastMCP server, 16 tools |
| `.claude/skills/jules/SKILL.md` | ~900+ | Documentation + recipes + state machine + worked examples |
| `.claude/skills/jules/watch_jules.py` | 518 | Background poller, JSON-lines log |
| `.claude/skills/jules/sessions_state.py` | 218 | Alias registry, fcntl-locked JSON |
| `.claude/skills/jules/jules_bulk.sh` | ~250 | fan-out / dashboard / approve-awaiting |
| `.mcp.json` (project) | 1 entry | `jules` server registration |
| `.claude/settings.json` | — | `enabledMcpjsonServers: ["jules"]` + `mcp__jules` allow |

## jules-plugin/ scaffold (the empty shell)

```
jules-plugin/
├── .claude-plugin/plugin.json   (8 lines, well-formed metadata)
├── .mcp.json                    (11 lines — BUG: uses ${PWD} instead of ${CLAUDE_PLUGIN_ROOT})
├── README.md                    (9 lines, placeholder)
├── commands/README.md           (1 line — placeholder)
├── mcp-server/
│   ├── pyproject.toml          (8 lines, fastmcp dep only)
│   └── src/jules_mcp/
│       ├── __init__.py         (1 line)
│       ├── server.py           (12 lines — STUB, no tools)
│       └── tools/__init__.py    (1 line)
├── skills/jules.md             (13 lines — STUB body)
├── tools/researcher/
│   ├── research.py             (272 lines — standalone, no integration with Jules)
│   └── ...
└── tests/.gitkeep
```

**Status: 0% functional. Structural skeleton only.**

## Token-bloat hotspots (top 5)

| # | Location | Tokens (est.) | Issue |
|---|---|---:|---|
| 1 | `SKILL.md:195–620` (state machine + errors + examples) | ~5,500 | Skill body loads every invocation |
| 2 | `SKILL.md:706–903` (parallel + caveats + harvest) | ~4,000 | Dense wiki-style prose |
| 3 | `server.py` `_paginate()` ~525 + raw passthrough | ~525+ | Returns full upstream JSON pre-filter |
| 4 | `server.py` `_summarize_activity_payload()` ~575 | ~575 | Full payload in, 1-line out |
| 5 | `server.py` `_fetch_patch()` ~450 | ~450 + diff body | Materialises 60KB diff even when caller only wants metadata |

## Critical-path port for plugin completion

1. Copy 16 tools from `.claude/mcp/jules-mcp/server.py` into plugin's `mcp-server/src/jules_mcp/server.py`
2. Port full `SKILL.md` into `skills/jules/SKILL.md` (note: **directory** `skills/jules/`, not flat file `skills/jules.md`)
3. Port `jules_bulk.sh` → `commands/` or `bin/`
4. Port `sessions_state.py` + `watch_jules.py`
5. Fix `.mcp.json` to use `${CLAUDE_PLUGIN_ROOT}`
6. Add `marketplace.json` for distribution
7. Add proper `README.md`

## Implications for the refactor

The current suite is a *project-private* installation (`.claude/`). The plugin is the **future shape**. Refactoring directly into the plugin (and gutting the `.claude/` copies, OR keeping them as a thin proxy that imports the plugin) lets us:

- Apply Code Mode to the plugin's MCP server (one line)
- Slim SKILL.md to ~300 lines, push reference into separate `references/` files Claude only loads on demand
- Remove duplication (the .claude/ + plugin/ copies are diverging already)
- Make the plugin installable to other repos
