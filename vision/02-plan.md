---
slug: vision-implementation-plan
type: implementation-plan
status: complete
owner: claude
created: 2026-05-19
updated: 2026-05-19
summary: Implementation plan for the base layer — COMPLETE. Foundation specs 01-05 and per-column specs 06-08 landed in PR #146. Three Jules sessions implemented 06/07/08 in parallel (PR #148/#149/#150). Architecture clarification landed in PR #147 (`03-architecture.md`). Two integration gaps (W5/C5) tracked in `04-nextsteps.md`. Next milestone: v0.1 running `agency` MCP plugin.
affects:
  - vision/02-plan.md
  - vision/specs/01-cell-manifest.md
  - vision/specs/02-tool-result-envelope.md
  - vision/specs/03-sidecar-metadata.md
  - vision/specs/04-phase-state-envelope.md
  - vision/specs/05-gate-yaml.md
  - vision/specs/06-agentic-base.md
  - vision/specs/07-workflow-base.md
  - vision/specs/08-context-base.md
---

# 02-plan — Implementation Plan for the 3×N Matrix Base Layer

> **STATUS — 2026-05-19**: Plan complete. All nine planned spec files landed in PR #146. All three column base layers shipped (PR #148 agentic, PR #149 context, PR #150 workflow). Architecture clarification merged in PR #147 (`vision/03-architecture.md`). Two integration gaps (W5 meta-scaffolder → graph; C5 hooks → FastMCP) tracked in `04-nextsteps.md` for the next session. The history below is preserved for traceability.

This plan converts the design in `vision/00.1-Overview.md` + the Phase 3 INTEGRATED-DRAFTs into eight concrete spec files and a Jules fan-out. No code lands in this PR — only the specs that drive the next PR.

## What "base layer" means here

The **base layer** is the per-column infrastructure — harness, runner, store, hooks — that lets ANY row plug in without modifying base files. It does NOT include any row-specific cell (`agentic/music`, `workflow/jules`, etc.). Rows scaffold into the base via the meta-row pipeline in a follow-up PR.

Base layer per column:

- **`agentic/`** — central FastMCP harness, cell loader, four-verb contract, `prefers_codemode` plumbing.
- **`workflow/`** — pipeline runner, phase lazy-loader, gate evaluator, envelope yield+resume, meta-row scaffold pipeline.
- **`context/`** — SQLite ontology store, Pre/PostToolUse hooks, sidecar ingestion, the shared `_shared/schemas/` directory holding the cross-cutting JSON Schemas.

## Strategy

1. Land all nine files (this plan + 8 specs) as ONE PR onto Master. Spec-only — no executable code.
2. After merge, dispatch THREE Jules sessions in parallel — one per column — each implementing its base layer in its own folder at the repo root. Each session reads its column's impl spec (06/07/08) and references the five foundation specs (01-05).
3. After the three base PRs merge, a follow-up plan handles cross-row dispatch and the central bootloader (specs 09-10 — out of scope here).

## Read order (top→down)

Foundation contracts — read these BEFORE any column impl spec:

1. **`specs/01-cell-manifest.md`** — the strict `manifest.toml` schema every cell honors. Derivation rules for skill/tool names from `(row, column)`.
2. **`specs/02-tool-result-envelope.md`** — the canonical `tool_result.schema.json`. Pure FastMCP envelope; column extensions go inside `data`.
3. **`specs/03-sidecar-metadata.md`** — `.meta.json` schema for binary artifacts that live outside the context graph.
4. **`specs/04-phase-state-envelope.md`** — workflow's `PhaseStateEnvelope` TypedDict and its serialization format.
5. **`specs/05-gate-yaml.md`** — `<column>/<row>/gates/<gate>.yaml` shape. Includes `on_success: emit_edge` for graph emission.

Per-column base implementations (Jules fan-out targets):

6. **`specs/06-agentic-base.md`** — FastMCP harness + cell loading + four-verb contract.
7. **`specs/07-workflow-base.md`** — pipeline runner + envelope yield/resume + meta-row scaffolding.
8. **`specs/08-context-base.md`** — SQLite ontology store + Pre/PostToolUse hooks + shared schema directory.

## Dependency graph

```
01 cell-manifest ──┬─→ 06 agentic-base
                   ├─→ 07 workflow-base
                   └─→ 08 context-base

02 tool-result ────┬─→ 06 agentic-base   (envelope = tool return)
                   ├─→ 04 phase-state    (wraps tool_result)
                   └─→ 08 context-base   (validation owner)

03 sidecar ────────┬─→ 07 workflow-base  (workflow emits artifacts → sidecar)
                   └─→ 08 context-base   (ingest sidecars on PostToolUse)

04 phase-state ────┬─→ 06 agentic-base   (agentic handles yields)
                   └─→ 07 workflow-base  (workflow produces yields)

05 gate-yaml ──────┴─→ 07 workflow-base  (gate evaluator owner)
```

## Why this order

The five foundation specs define **cross-column contracts**. If they don't land first, the three column implementations will independently invent overlapping shapes for `ToolResult`, sidecars, gates, etc., and drift. Landing 01-05 fixes the wire format before any code touches it.

The three column impl specs (06-08) each scope their `affects:` allow-list to ONE folder, so the three Jules sessions are non-overlapping and can run in parallel without merge conflicts.

## Folder layout after the base PRs land

```
the-agency-system/
├── vision/                          # design specs (this folder)
│
├── agentic/                         # base layer — Jules session A
│   ├── _harness/
│   │   ├── __init__.py
│   │   ├── fastmcp_boot.py          # FastMCP server + four-verb contract
│   │   ├── cell_loader.py           # scans <col>/<row>/manifest.toml
│   │   └── codemode.py              # prefers_codemode handling
│   └── _bootloader.py               # plugin entrypoint
│
├── workflow/                        # base layer — Jules session B
│   ├── _runner/
│   │   ├── __init__.py
│   │   ├── pipeline.py              # phase walker, lazy load
│   │   ├── gate.py                  # gate evaluator
│   │   └── envelope.py              # PhaseStateEnvelope
│   ├── _state/                      # opaque state JSON files
│   │   └── README.md                # store layout, no .py code
│   └── meta/                        # the meta-row: scaffold pipeline
│       ├── manifest.toml
│       └── phases/01-scaffold.md
│
└── context/                         # base layer — Jules session C
    ├── _store/
    │   ├── __init__.py
    │   ├── sqlite.py                # SQLite ontology + Cypher-compat query
    │   └── schema.sql
    ├── _hooks/
    │   ├── __init__.py
    │   ├── pre_tool_use.py          # validate frontmatter
    │   └── post_tool_use.py         # graph upsert + sidecar ingest
    └── _shared/
        └── schemas/
            ├── tool_result.schema.json
            ├── agentic-cell.schema.json
            ├── workflow-cell.schema.json
            ├── context-cell.schema.json
            ├── sidecar.schema.json
            └── gate.schema.json
```

NOTE: `_shared/schemas/` lives under `context/` because context owns schema validation (per `00.1-Overview.md`). The agentic and workflow implementations import schemas from there; they do not re-define them.

## Open questions deferred to harness pass

These four open questions from the Phase 3 drafts are NOT resolved in this base-layer plan. They become tractable AFTER the base layer exists:

- **Agentic Q1** — dynamic skill reload vs server reboot. Default: cold reboot. Hot-reload is a follow-up.
- **Workflow Q1** — `PhaseStateEnvelope` serialization across user-input pauses. Default: JSON file in `workflow/_state/<session_id>/<phase_id>.json`. Atomic write. Detail in spec 04.
- **Context Q2** — hook execution layer (MCP middleware vs Python decorators). Default: Python decorators on FastMCP tool handlers. Detail in spec 08.
- **Context Q1** — sidecar sandbox permission in external vaults. Default: sidecar lives next to the artifact (`.meta/` subdir). If sandboxed, fall back to a centralized registry path. Detail in spec 03.

The base layer makes minimal assumptions on these (documented per-spec). The harness pass will revisit.

## Acceptance for this PR (spec-only)

- All nine files present at the paths above.
- Each spec uses the canonical frontmatter (slug, type, status, owner, created, updated, summary, affects).
- Each spec includes: `## Purpose`, `## Schema / Contract`, `## Worked example`, `## Acceptance criteria` (Gherkin), `## Dependencies` (links to other specs).
- `affects:` allow-list strictly = nine files. No other tree changes.
- Self-review (placeholder scan, internal consistency, scope, ambiguity) per `superpowers:brainstorming` skill.

## Acceptance for the three Jules fan-out PRs (one per column)

- **Agentic PR**: ships `agentic/_harness/` + `agentic/_bootloader.py`. Cold-boot under 500 tokens. `pytest` proves the four-verb contract.
- **Workflow PR**: ships `workflow/_runner/` + `workflow/meta/`. `PhaseStateEnvelope` round-trips. Gate eval emits `SATISFIES_PHASE` on success.
- **Context PR**: ships `context/_store/`, `context/_hooks/`, `context/_shared/schemas/`. SQLite store round-trips. Pre/PostToolUse hooks fire on a synthetic write.

Each Jules session writes ONLY in its column's folder. Cross-column changes are out of scope; if Jules feels the urge to edit another column, it must reply with a friction note and stop.

## What happens after the three base PRs merge

Specs 09 and 10 (out of scope here):

- `specs/09-cross-row-dispatch.md` — harness-in-harness. The four-verb contract crossing rows. Tests the music→jules dispatch path.
- `specs/10-bootloader.md` — central plugin entry that glob-scans `<col>/<row>/manifest.toml`, registers tools under derived namespaces, wires the hooks.

Then row scaffolding (`agentic/music`, `workflow/jules`, etc.) becomes a meta-row invocation: one command produces all three cells from templates.

## Out of scope

- Row-specific cells (`agentic/music`, `workflow/jules`, `context/podcast`, …).
- Any logic that depends on a row being present.
- The `result/<row>/` artifact registry implementation (spec written in 03, impl follows base layer).
- The central plugin entry (spec 10).
- Hot reload of skills (defer per Agentic Q1).
