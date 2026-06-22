---
slug: agency-plugin-extraction-design
type: migration-task-spec
status: ready
owner: claude
created: 2026-05-21
updated: 2026-05-21
home: the-agency-system (source repo — this is a TASK spec, not a repo artifact)
summary: TASK spec for extracting the `agency` Claude Code plugin (3-column matrix engine + materialized `jules` row + Vision canon) from `the-agency-system` into the fresh `agency` repo. Approach A (lean Vision engine), jules tools row-native via the four-verb contract. The Vision always wins over prototype code. This document lives in the SOURCE repo on purpose — it describes the one-time migration job and keeps the new repo clean.
---

# Migration TASK spec — extract the `agency` plugin

> **This is a task/migration document, not a repo artifact.** It describes
> the one-time job of carving the plugin out of `the-agency-system`. It lives
> in the **source** repo. The new `agency` repo stays clean: it carries only
> canonical, forward-looking artifacts written from the perspective of the
> agent who will develop the plugin next (Vision canon + clean specs/plans +
> a lean `CLAUDE.md`). See §0.1.

## 0. Governing principle

**The prototype code is inspiration; the Vision is authoritative.** The
working implementation in `the-agency-system` (the matrix base layer + the
`jules` row + the standalone `jules-plugin` orchestrator) is the starting
point and proof that the architecture runs. Wherever the prototype diverges
from the design canon (the `vision/` tree, which becomes `docs/vision/` in the
new repo), **follow the Vision** and finish the engine + jules row to match it.
A half-port is not acceptable: the engine and the `jules` row must work
end-to-end and be Vision-faithful.

## 0.1 Two artifact categories — keep them apart

This effort produces two kinds of documents. Conflating them pollutes the new
repo. They have different perspectives and different homes.

| Category | Perspective | Examples | Home |
|---|---|---|---|
| **Task / migration** | "I am migrating code OUT of `the-agency-system`" | this spec; the migration implementation plan; what-not-to-port lists; source-repo cleanup/deletion notes | **`the-agency-system`** (`docs/superpowers/specs/`) |
| **Agency repo (clean)** | "I am the agent who will DEVELOP the agency plugin going forward" | `docs/vision/` canon; clean forward-looking specs (cell-manifest, tool-result-envelope, gate, agentic/workflow/context base); a clean roadmap; lean `CLAUDE.md` | **`agency`** repo |

Rules:

- Task/migration docs **never** land in the `agency` repo. The new repo must
  read as if it were always a clean plugin project — no "ported from",
  "retired wrapper", "do not port" language anywhere in its tracked files.
- Agency-repo docs are written from the **consumer/maintainer** perspective and
  must be clear, **token-efficient**, and **roundtrip-efficient** (an agent can
  understand each file without chasing many others).
- A recurring **SuperClaude review agent** audits every agency-repo artifact
  from that consumer perspective before it is finalized (see §9).

## 1. Goal & end state (of the `agency` repo)

A fresh `agency` repository that **is** a Claude Code plugin (points at itself
as plugin source), containing:

1. The **3×N matrix engine** — the three base columns (`agentic`, `workflow`,
   `context`) with the FastMCP four-verb harness, GraphQLite-backed context
   graph, pre/post-tool hooks, artifact drivers, and the workflow runner.
2. The **`jules` row** — materialized across all three columns, backed by the
   *real* working orchestrator (lifecycle / patches / bulk / source / trim /
   aliases), exposed row-native through the four-verb contract.
3. The **Vision design canon** — consolidated under `docs/vision/`, the single
   source of truth that drives ongoing implementation.
4. **Clean forward-looking specs/plans** for continued work, written from the
   maintainer-agent perspective.
5. A **self-hosting dev environment** — `CLAUDE.md` + `.claude/settings.json`
   wiring superpowers, superclaude (`sc`), and the plugin-writing plugin
   (`superpowers-developing-for-claude-code`), with the MCP server booting at
   session start.

Out of this effort's scope (later, on explicit go-ahead): wiring `agency` as a
plugin source in `the-agency-system` and deleting the moved/cruft directories
there.

## 2. Approach (decided)

- **Approach A — lean Vision engine.** MCP entry is `agentic/_bootloader.py`
  (the four-verb contract). The heavy unified server `servers/agency-mcp`
  (entangled with music/novel) is **left behind entirely**.
- **Jules tools row-native via four-verb.** The real orchestrator's tools are
  exposed as the `jules` row's MCP tools (`mcp__jules_*`) discovered through
  `agentic/jules/manifest.toml` and routed via the harness. The standalone
  `create_mcp()` factory is retired; a small loader adapter registers a
  handler module's functions as tools.

## 3. Target repo layout (clean `agency` repo)

```
agency/
├── .claude-plugin/{plugin.json (name: "agency"), marketplace.json (source ./)}
├── .mcp.json                  # agency → agentic/_bootloader; + context7; + sequential-thinking
├── .claude/settings.json      # enable superpowers/sc/plugin-writing plugin; SessionStart hook
├── CLAUDE.md                  # token-efficient dev instructions + overall goal
├── README.md
├── pyproject.toml             # single dependency manifest
├── requirements-dev.txt
├── agentic/
│   ├── _bootloader.py + _harness/{cell_loader,fastmcp_boot,name_deriver,codemode}.py
│   └── jules/{manifest.toml, handlers/*, lib/*, skills/<export>/SKILL.md}
├── workflow/{_runner/*, meta/*, jules/*}
├── context/{_store/sqlite.py, _hooks/*, _drivers/*, _shared/schemas/*, jules/*}
├── bin/{agency-dev-install, jules-bulk}
├── tools/jules-patch-extract.py
├── tests/{agentic,workflow,context,jules}/
└── docs/
    ├── vision/                # consolidated design canon (authoritative)
    └── specs/ (or plans/)     # clean forward-looking specs/roadmap for the maintainer agent
```

> Note: the migration's own design + implementation plan do **not** appear in
> the tree above — they live in `the-agency-system` per §0.1.

## 4. Component plan — port + finish to Vision

### 4.1 `agentic/` — the engine surface

Port `_bootloader.py` + `_harness/{cell_loader,fastmcp_boot,name_deriver,codemode}.py`.
**Finish to Vision:**

- `boot()` registers exactly the four verbs (`mcp__list_tools`,
  `mcp__call_tool`, `mcp__list_skills`, `mcp__dispatch_skill`) and wraps every
  derived tool with the pre/post hooks (C5 closed in the prototype — preserve).
- Honor the `FastMCP 2.x add_tool` signature (no `name=` kwarg; no `**kwargs`
  wrappers) — bind tool name/func as defaults.
- Cold-boot payload stays under the 500-token budget; port the enforcing test.
- Name derivation follows the canonical convention: handlers at
  `<col>/<row>/handlers/<export>.py`, skills at
  `<col>/<row>/skills/<export>/SKILL.md` (Vision/deriver paths win over any
  prototype shortcut).

### 4.2 `workflow/` — path walking

Port `_runner/{pipeline,envelope,gate,manifest}.py` + `evaluators/` + `meta/`.
**Finish to Vision:**

- Pipeline walks `Phase` graph nodes; Continuation is a graph node (no
  `workflow/_state/` JSON files).
- Meta-row scaffolder emits `Cell`/`Phase`/`Row` graph nodes (W5 closed —
  preserve).
- **Phase-node seeder** (retrospective follow-up #1): add a `pipeline.boot()`
  step or `bin/agency-seed-phases` that upserts `Phase` nodes from
  `workflow/<row>/phases/*.md` so a hand-rolled row (jules) runs end to end.
  Required for Vision fidelity → in scope.

### 4.3 `context/` — graph + drivers

Port `_store/sqlite.py`, `_hooks/{pre,post}_tool_use.py`, `_drivers/{protocol,fs}.py`,
`_shared/schemas/*.schema.json`. **Finish to Vision:**

- GraphQLite is the substrate; keep the raw-SQLite fallback for now but isolate
  it so it is easy to delete later (dropping it is post-v0.1).
- `artefact-node.schema.json` (renamed from sidecar) carries `artifact_driver`
  + `driver_pointer`; no `.meta.json` sidecars to user storage.
- Canonicalize runtime schemas from the vision drafts where the prototype stub
  disagrees (context owns graph schemas).

### 4.4 `jules` row — first materialized row, backed by the real orchestrator

Headline deliverable ("the Jules code, the first thing we need").

- **Fold the real orchestrator** (`jules_mcp.{api,source}` +
  `jules_mcp.tools.{lifecycle,patches,bulk,aliases,trim}`) into
  `agentic/jules/handlers/` (+ shared logic in `agentic/jules/lib/`).
- `agentic/jules/manifest.toml` exports the tool set → harness derives
  `mcp__jules_*`. A loader adapter lets `cell_loader` register a handler
  module's public functions as tools (the "glue").
- **Skills:** existing `/agency:jules:research`, plus the three discipline
  skills (`context-safe-patch-handling`, `jules-orchestrator-discipline`,
  `silent-fail-recovery`) become jules-row skills/references.
- **Workflow cells:** `workflow/jules/{phases/01-research.md,02-synthesize.md,
  gates/research-complete.yaml}` — the gate is a placeholder; keep it honest in
  prose, do not overstate behavior.
- **Context cells:** `context/jules/{manifest.toml, schemas/research-topic +
  finding, templates/research-brief.md.jinja}`.
- **CLI clients:** `bin/jules-bulk` + `lib/watch_jules.py` stay as thin clients
  over the same row lib. Fix the `jules_create` import path (retrospective #7).

### 4.5 Retired / not ported

- `servers/agency-mcp` (music/novel unified server) + all music/novel handlers,
  tools, tests.
- `skills/music/*` (54), `artists/`, `genres/`, `audio/`, `novels/`,
  `documents/`, `overrides/`, `state/`, `migrations/`, `index.html`.
- The `jules-plugin/` wrapper directory — its **code folds into the row**; the
  wrapper (own `.claude-plugin`, `.mcp.json`, `create_mcp()`) is retired.
- bitwize-music `.claude` setup, `IDEAS.md`, `REFACTOR_DESIGN.md`.

## 5. Vision canon consolidation

- Port `the-agency-system/vision/` → `agency/docs/vision/` as authoritative
  canon (Overview, architecture, nextsteps, retrospective, `specs/`,
  `specs/schemas/`).
- **Mine** `the-agency-system/Plan/` for durable material that *expands* the
  Vision without contradicting it — primarily `Plan/harness/VOCABULARY.md`
  (glossary) and `Plan/decisions/readme.md` (ADR index). Fold durable bits into
  `agency/docs/vision/`; do **not** port `Plan/` wholesale.
- During consolidation, rewrite anything that carries migration/legacy framing
  into clean maintainer-perspective prose (per §0.1).

## 6. Self-hosting dev environment

### 6.1 `.claude-plugin/`
- `plugin.json` — `name: "agency"`, description, homepage `netzkontrast/agency`.
- `marketplace.json` — single plugin, `source: "./"`.

### 6.2 `.mcp.json`
```json
{
  "mcpServers": {
    "agency": { "type": "stdio", "command": "python",
                "args": ["-m", "agentic._bootloader"] },
    "context7": { "type": "stdio", "command": "npx",
                  "args": ["-y", "@upstash/context7-mcp"] },
    "sequential-thinking": { "type": "stdio", "command": "npx",
                  "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"] }
  }
}
```

### 6.3 `.claude/settings.json`
- `extraKnownMarketplaces`: `superpowers-marketplace` (obra), `superclaude`
  (SuperClaude-Org), `superpowers-developing-for-claude-code` (obra),
  `agency-marketplace` (this repo).
- `enabledPlugins`: `superpowers`, `sc`, `superpowers-developing-for-claude-code`,
  `agency@agency-marketplace`.
- `enabledMcpjsonServers`: `agency`, `context7`, `sequential-thinking`.
- `hooks.SessionStart`: run `bin/agency-dev-install` (idempotent) so deps exist
  and the MCP server boots each session.

### 6.4 `CLAUDE.md` (token-efficient, maintainer perspective)
Overall goal; governing principle (Vision wins); matrix law in ~5 lines;
canonical paths/naming; skill order (brainstorm → writing-plans →
executing-plans; `writing-skills`; `sc:`; the plugin-writing plugin); dev
commands; dev-branch convention. Links to `docs/vision` instead of inlining.

## 7. Validation gate (before reporting to the user)

| # | Check |
|---|---|
| 1 | `python -m agentic._bootloader --emit-cold-boot` lists the four verbs |
| 2 | `pytest tests/{agentic,workflow,context,jules}` green |
| 3 | `discover()` finds `mcp__jules_*` + `/agency:jules:*` |
| 4 | Cold-boot payload under 500 tokens |
| 5 | jules lifecycle smoke (mocked API) round-trips through a derived tool |
| 6 | jules workflow phase 01 reaches `_walk_phase` and returns a typed envelope |
| 7 | No music/novel imports leak into the ported tree (grep guard) |
| 8 | No `*.meta.json` sidecars; `workflow/_state/` does not exist |
| 9 | Every clean agency-repo doc passes the SuperClaude consumer-perspective review (§9) |

## 8. Deferred (post-extraction)

- Cross-row dispatch (vision spec 09), drivers beyond `fs`, additional rows
  (music/novel/podcast), hot-reload, dropping the raw-SQLite fallback,
  centralizing the inline error-code catalogue (unless it blocks the jules row).
- Wiring `agency` as a plugin source in `the-agency-system` and deleting the
  moved/cruft directories there — only after the port is validated and the user
  gives explicit go-ahead.

## 9. Recurring SuperClaude consumer-perspective review

A SuperClaude review agent (e.g., `sc:sc-spec-panel` / `sc:sc-analyze`) audits
every clean agency-repo artifact **from the perspective of the agent who will
work in the repo next**. It answers, per file:

- **Clarity:** Can a cold reader understand this file's purpose and contract
  without external context?
- **Token efficiency:** Is anything redundant, verbose, or duplicated across
  files? Could it be shorter without losing meaning?
- **Roundtrip efficiency:** How many other files must be opened to act on this
  one? Are cross-references minimal and explicit?
- **Leakage check:** Does any tracked file carry migration/legacy/"ported-from"
  framing that breaks the clean-repo illusion (§0.1)?

The review runs repeatedly — after each artifact is drafted and again before
finalization — and its findings are applied before commit.

## 10. Process / skill order

Brainstorming (this spec) → `superpowers:writing-plans` (sharpened with
`sc:sc-design` / `sc:sc-spec-panel`) → `superpowers:executing-plans` /
`superpowers:subagent-driven-development` → `superpowers:verification-before-completion`
before reporting. Jules fan-out and parallel subagents used where columns are
independent. The §9 review agent runs throughout.
