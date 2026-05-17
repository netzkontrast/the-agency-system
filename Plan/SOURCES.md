# SOURCES.md — Canonical Source Repositories

All Plan/ specs that read from external sources cite this table. Jules clones into `~/work/vendor/<name>/` (read-only) and never commits vendor files into `the-agency-system`.

## Repository table

| Name | Canonical GitHub URL | Branch / Tag | Used by specs |
|---|---|---|---|
| `bitwize-music` | `https://github.com/bitwize-music-studio/claude-ai-music-skills` | `v0.91.0` | 004, 005, 008, 017, 019 |
| `agency` | `https://github.com/netzkontrast/agency` | `claude/agency-plugin-refactor-PgMQ4` | 010, 012, 013, 015, 016, 021 |
| `superpowers-marketplace` | `https://github.com/obra/superpowers-marketplace` | `main` (no semver tags yet) | 016 |
| `the-agency-system` (work repo) | `https://github.com/netzkontrast/the-agency-system` | `claude/agency-plugin-refactor-PgMQ4` | All specs |

> **⚠️ Verification flag**: the `bitwize-music` URL was inferred from the installed plugin's `.claude-plugin/plugin.json`. If Spec 004 fails at clone, open `[BLOCKED: verify-source-url]` and request the correct URL from the human.

## Canonical clone commands

Paste these verbatim into the Jules sandbox. The `--depth=1` keeps clones small; `--branch` pins a reproducible revision.

### bitwize-music (music handlers + skills source)

```bash
git clone --depth=1 --branch=v0.91.0 \
  https://github.com/bitwize-music-studio/claude-ai-music-skills.git \
  ~/work/vendor/bitwize-music
```

### agency (novel-architect, dramatica, ncp, sc-*, superpowers-* skills source)

```bash
git clone --depth=1 --branch=claude/agency-plugin-refactor-PgMQ4 \
  https://github.com/netzkontrast/agency.git \
  ~/work/vendor/agency
```

### superpowers-marketplace (15 superpowers-* skills)

```bash
git clone --depth=1 \
  https://github.com/obra/superpowers-marketplace.git \
  ~/work/vendor/superpowers-marketplace
```

### the-agency-system (work repo — Jules clones this to commit into)

```bash
git clone --branch=claude/agency-plugin-refactor-PgMQ4 \
  https://github.com/netzkontrast/the-agency-system.git \
  ~/work/the-agency-system
```

## Reference / framework docs (not cloned; read via WebFetch)

| Doc | URL | Pinned version | Used by specs |
|---|---|---|---|
| Claude Code Plugins Guide | https://code.claude.com/docs/en/plugins | current | 001, 002, 005, 007, 015, 017, 020 |
| Claude Code Plugins Reference | https://code.claude.com/docs/en/plugins-reference | current | 001, 002, 005, 017, 020 |
| FastMCP main docs | https://gofastmcp.com | 3.1.0+ | 001, 003, 004, 006, 008, 009, 011, 013, 014, 016, 021 |
| FastMCP Code Mode | https://gofastmcp.com/servers/transforms/code-mode | 3.1.0+ (experimental) | 008, 018 |
| NCP schema v1.3.0 | (vendored from `agency` repo at `skills/ncp-author/upstream/schema/ncp-schema.json`) | 1.3.0 | 012 |
| Dramatica ontology | (vendored from `agency` repo at `maintenance/schemas/narrative-ontology/`) | 304 entries | 012, 013, 021 |
