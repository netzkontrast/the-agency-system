---
slug: 0001-single-central-routing-skill
type: adr
status: ready
owner: claude
created: 2026-05-19
updated: 2026-05-19
domain: agentic
wave: A
adr_id: ADR-0001
adr_status: Proposed
adr_supersedes: []
adr_superseded_by: []
related:
  - 2026-05-19-agency-base-canvas
  - harness-vocabulary
  - 005-central-router-skill
  - 023-harness-in-harness
summary: Adopt a single `/agency` SKILL.md as the system's central router/workflow-survey skill, replacing the current router-less stance where ~30 agentic skills exist with no surveyor.
---

# ADR-0001 — Single central routing skill (`/agency`)

## Context and Problem Statement

The `agentic` domain hosts ~30 skills (plan-writers, researchers, jules-discipline, brainstorming, etc.) but no skill surveys workflow, answers "what next?", or dispatches across domains. Users entering a fresh session see no orientation surface: they must either know a skill's exact name, or grep `/help` output and guess. Canvas §0 calls this out — *"Central router skill DOES NOT EXIST"* — alongside the broken anchor-triad and missing graph as the three "half-built" pillars.

The reviewer's critique in canvas v2 made the gap concrete: a router-bearing system has a higher cold-load floor than a router-less anchor-triad-only system, and that cost is worth paying *iff* the router earns it by surveying workflow and converting intent → skill. Today there is no such surface.

## Decision Drivers

- Canvas §3 ("The central skill: `/agency`") — explicit design target: ≤100-line SKILL.md, six-step survey algorithm, five references.
- Canvas §0 — names the missing router as one of three "half-built" wire pillars.
- VOCABULARY §4.2 `skill_kind` enum already provides `orchestrator` — the router slot was reserved but never filled.
- The user goal explicitly asked for routing/workflow surfacing — implies the floor must be above the canonical <500-token boot budget for headless agents.
- Lesson 05 (`05-independent-review-subagent-is-load-bearing.md`) — the reviewer flagged that v1's "default ON for code mode" + missing router compounded into a measurable cold-boot blowup. The router is the fix that earns the budget.

## Considered Options

### Option A — Single central `/agency` router skill (RECOMMENDED)

One SKILL.md at `domains/agentic/skills/agency/SKILL.md`. ≤100-line hard cap (per VOCABULARY §4.2 router subbudget, D-09 v2). References split across `routing.md`, `workflows.md`, `domains.md`, `meta-loop.md`, `troubleshooting.md`. Algorithm spelled out in canvas §3 (session-start probe, "what next?" via Wave D graph, "where am I?", intent search, cross-domain via `related:`, code-mode nudge). Cold cost ~4200 tokens (canvas §3 table).

### Option B — Per-domain routers (one per domain)

Each domain ships its own `<domain>-router` skill (e.g. `/music-router`, `/novel-router`). No central surveyor. Familiar pattern (matches how bitwize-music's `/bitwize-music:help` works today). Lower per-router complexity but no cross-domain answer to "what next?".

### Option C — No router (status quo, router-less anchor-triad only)

Keep the current state. Users discover skills via `agency_skill_search` directly. Cold floor stays at the canonical <500-token boot budget. The system is functional for users who know what they want but fails the "where am I / what next?" surface entirely.

## Decision Outcome

**Chosen: Option A — single `/agency` router skill.**

Per canvas §3, the router lives at `domains/agentic/skills/agency/SKILL.md` with `skill_kind: orchestrator`, declares the eager anchor-triad tools in `allowed-tools`, and runs the 6-step survey algorithm. References live alongside (5 files, never inlined). The router is `T4-immutable` once Accepted per VOCABULARY §6C — successor ADRs land if the algorithm changes.

The cold-boot budget rises from `<500` to `<6000` tokens — accepted explicitly in canvas D-13 and tracked as a separate ADR-0011 (out of scope here, second wave).

Code-Mode integration: when a downstream skill's frontmatter declares `prefers_codemode: true`, the router emits a one-line nudge — it does not auto-rewrite (per ADR-0007).

## Consequences

### Positive

- Closes the canvas §0 "router DOES NOT EXIST" gap — fresh sessions get a baseline orientation.
- The router becomes the single intent surface; downstream skills can stay short (≤200 lines, ≤120 for non-router) because the router carries cross-domain context.
- `agency_skill_search` gets a natural caller: the router walks the Wave D graph (ADR-0008) and surfaces ranked candidates rather than every skill being equally exposed.
- One file to audit for routing logic, one body to keep ≤100 lines — easier to detect drift than a per-domain-router web.

### Negative

- Cold-load cost rises ~8× from `<500` → `<6000` tokens (canvas §3 table). Headless agents (Jules in L3 sidecar mode) need a router-less path — spec 023 already plans it, but ADR-0011 must ratify the budget split.
- The router becomes a single point of failure: if its references go stale or the graph query path breaks, every session's "what next?" surface degrades.
- Authoring discipline becomes load-bearing — the ≤100-line cap is strict; any drift bleeds tokens into every cold load.

### Neutral

- No change to per-domain skill bodies; their references stay where they are.
- The router is one more T4-immutable artefact under VOCABULARY §6C — successor ADRs are the only route to mutate it.

## Falsifier triggers

- If two distinct router skills land in `agentic/` (e.g. `/agency` + `/agency-light`), the singleness invariant is broken — successor ADR.
- If the router body exceeds 100 lines in `main` for two consecutive PR cycles, the budget assumption is falsified — successor ADR re-opens D-09.
- If cold-boot measurement (per canvas §10) consistently exceeds 6000 tokens, the budget assumption breaks — joint successor with ADR-0011.
