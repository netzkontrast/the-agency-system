---
slug: 0004-anchor-triad-as-wire-form
type: adr
status: ready
owner: claude
created: 2026-05-19
updated: 2026-05-19
domain: shared
wave: A
adr_id: ADR-0004
adr_status: Proposed
adr_supersedes: []
adr_superseded_by: []
related:
  - 2026-05-19-agency-base-canvas
  - harness-vocabulary
  - 104-tool-search-anchor-triad
  - 112-context-anchor-triad
  - 0002-single-codemode-mcp-server
  - 0008-wave-d-ontology-graph
summary: Adopt twin anchor triads — `agency_tool_search/describe/invoke` and `agency_skill_search/describe/dispatch` — as the wire-form of the canonical four-verb contract.
---

# ADR-0004 — Anchor triads as wire form of the four-verb contract

## Context and Problem Statement

VOCABULARY §3 names a canonical four-verb harness contract: `list_tools`, `call_tool`, `list_skills`, `dispatch_skill`. These are L1 abstract verbs — they describe *what* the harness must offer, not *how* the names appear on the MCP wire. Canvas §0 records the half-built state: the tool-side anchor triad (`agency_tool_*`) is **unbuilt**; the closest thing on the skill side is `shared_list_skills`/`shared_get_skill` (wrong names, no `dispatch`).

Two disagreements have lived implicitly in the corpus:
1. **Naming**: should the four verbs ship under their canonical L1 names, or under wire-form names that group them by surface?
2. **Triad shape**: spec 104 (`tool-search-anchor-triad`) and the canvas both want a *describe* verb between `search` and `invoke/dispatch` — i.e. a triad, not a pair. The canonical four-verb list has no such verb.

This ADR ratifies the wire-form decision plus the triad shape.

## Decision Drivers

- Canvas §4 ("The central MCP — eager tools") — fixes the wire names verbatim.
- Canvas §0 — names the missing `agency_tool_*` triad and the misnamed `shared_list_skills` family as concrete half-built pieces.
- Spec 104 (`104-tool-search-anchor-triad`) — pre-existing spec that wires the tool-side triad; canvas §4 promotes it.
- Spec 112 (`112-context-anchor-triad`) — parallel spec for the context-mode side.
- VOCABULARY §3 — the canonical L1 four-verb list; this ADR adds the *describe* facet as a footnote, not as a fifth row.
- Lesson 06 (`06-spec-vs-schema-drift.md`) — wire names need a single source-of-truth surface; the triads' three-word grammar makes that explicit.

## Considered Options

### Option A — Twin anchor triads as wire form (RECOMMENDED)

Six eager tools, two triads:

| Verb | Tool-side | Skill-side |
|---|---|---|
| `search` | `agency_tool_search(intent)` | `agency_skill_search(intent)` |
| `describe` | `agency_tool_describe(name)` | `agency_skill_describe(name)` |
| `run` | `agency_tool_invoke(name, params)` | `agency_skill_dispatch(name, args)` |

`describe` is new — it is the *read schema before invoking* verb that VOCABULARY left implicit. VOCABULARY §3 gains a footnote rather than a fifth row.

### Option B — Rename L1 fixtures to wire names

Push the wire names back into VOCABULARY §3 (e.g. drop `list_tools`, rename to `agency_tool_search`). Forces every existing reference to L1 verbs to update. Loses the abstraction layer between harness contract and wire shape.

### Option C — Single triad covering both tools and skills

Merge tools and skills under one triad (`agency_search`, `agency_describe`, `agency_dispatch`) with a `kind: "tool" | "skill"` parameter. Smaller surface (3 eager tools, not 6). Loses the discoverability of paired triads — autocomplete on `agency_tool_*` shows you the whole tool surface; `agency_*` does not separate them.

## Decision Outcome

**Chosen: Option A — twin anchor triads.**

- Six eager tools total, three per side (`agency_tool_{search,describe,invoke}`, `agency_skill_{search,describe,dispatch}`).
- All six live in `domains/shared/handlers/anchors.py` (per canvas §13 specs 003 + 004).
- Eager-vs-deferred classification is owned by `_AnchorAwareCodeMode` (spec 008); these six are always eager.
- `agency_skill_dispatch` is the L1 `dispatch_skill` verb's wire form. `agency_tool_invoke` is the L1 `call_tool` verb's wire form. The mapping is documented in VOCABULARY §3 as a footnote.
- `describe` is **new** relative to the canonical four-verb list and is permitted because it is the schema-reading half of the existing `list_*` verbs — readers MUST be able to consult schema before invocation per ADR-0005's schema-authority clause.

## Consequences

### Positive

- The wire-form three-verb grammar (`search/describe/invoke`) matches the natural agent workflow: search → describe → run. Autocomplete narrows on each step.
- Twin triads give clean discoverability: an agent that wants only tools never sees skill-surface noise, and vice versa.
- Spec 104 and spec 112 can ship in parallel — they share no Python surface.
- VOCABULARY §3 stays at four canonical verbs; the footnote is the only mutation.

### Negative

- Six eager tools is twice the per-side count VOCABULARY §3 implies. The cold-load token cost for the six descriptions is ~600 tokens (canvas §3 estimate) — small but non-zero, and added permanently to the floor.
- The `describe` verb is genuinely new; VOCABULARY §3's "four-verb contract" claim becomes a "four-verbs-plus-describe" reality. The footnote convention papers over this, but a strict reader can correctly note that the corpus now names five verbs.
- Two triads means two places to maintain consistent intent-matching semantics (`search`) and result-shape semantics (`describe`). Drift between the tool-side and skill-side triad is a new failure class.

### Neutral

- L3 sidecar mode (spec 023) gets the same six-tool eager surface — there is no skill-only or tool-only variant of the triads.
- The triads' eager-status is a property of `_AnchorAwareCodeMode`'s classifier, not of the tools themselves — future ADRs could re-classify without renaming.

## Falsifier triggers

- If a third triad lands (e.g. `agency_reference_*`), the "twin" claim is broken — successor ADR re-evaluates the per-surface partitioning.
- If `agency_skill_dispatch` drifts in semantics from VOCABULARY §3's `dispatch_skill` (e.g. starts accepting batched args), the wire-form-mirrors-L1 claim is falsified — successor ADR.
- If `describe` is renamed or merged into `search` (e.g. `search` returns the schema), the three-verb-per-triad grammar breaks — successor ADR.
