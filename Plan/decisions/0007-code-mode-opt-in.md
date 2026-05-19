---
slug: 0007-code-mode-opt-in
type: adr
status: ready
owner: claude
created: 2026-05-19
updated: 2026-05-19
domain: shared
wave: A
adr_id: ADR-0007
adr_status: Proposed
adr_supersedes: []
adr_superseded_by: []
related:
  - 2026-05-19-agency-base-canvas
  - harness-vocabulary
  - 008-codemode-registry
  - 117-tool-result-archive
  - 0001-single-central-routing-skill
  - 0005-shared-toolresult-envelope
summary: Code Mode is default OFF; skills opt in via `prefers_codemode: true` frontmatter. Re-open to default ON only after the spec-117 archive is verified to intercept in-sandbox calls.
---

# ADR-0007 — Code Mode opt-in (per-skill `prefers_codemode`)

## Context and Problem Statement

Code Mode (the `_AnchorAwareCodeMode`-driven path where the model writes Python that calls MCP tools directly inside a sandbox, rather than invoking MCP tools one-by-one) is a significant context-saver for long pipelines — but it has a measured failure mode. Lesson 14 (`14-token-consumption-postmortem.md`) documents the pattern where oversize MCP results were the top token sink; spec 117 (`117-tool-result-archive`) is the structural fix. In Code Mode, MCP calls happen *inside* the sandbox; until the spec-117 archive is verified to intercept sandboxed calls, every Code Mode MCP call risks dumping the full body into the agent's context as part of the sandbox's stdout — re-introducing the lesson-14 leak class.

Canvas v1 recommended Code Mode default ON. The reviewer flagged this explicitly: spec 117's archive interception path is not yet verified for in-sandbox MCP calls, so default-ON re-opens the lesson-14 failure class. Canvas v2 (D-05) flips to default OFF with per-skill opt-in via `prefers_codemode: true` frontmatter.

This ADR ratifies the default-OFF, per-skill-opt-in stance and explicitly carves out the re-open path: once spec 117's archive is verified inside the sandbox, a successor ADR re-opens the default.

## Decision Drivers

- Canvas §4 ("The central MCP — Code Mode default OFF") — explicit destination.
- Canvas D-05 (v2 flip) — names the lesson-14 risk that drove the flip.
- Lesson 14 — measured top-3 token-spend sink; the failure mode is concrete and recent.
- Spec 117 (`117-tool-result-archive`) — the structural fix; not yet verified in-sandbox.
- ADR-0005 — the `@domain_tool` decorator routes oversize bodies to the spec-117 archive *outside* the sandbox; the in-sandbox path is the gap.
- ADR-0001 — the router emits a one-line code-mode nudge when a skill's frontmatter declares `prefers_codemode: true`. The nudge is informational; the user decides.

## Considered Options

### Option A — Default OFF; per-skill opt-in via `prefers_codemode: true` (RECOMMENDED)

Code Mode is off by default. A skill that benefits from Code Mode (long pipelines with many small MCP calls) sets `prefers_codemode: true` in its frontmatter. The router emits a one-line nudge when an opted-in skill is dispatched. The user / agent decides whether to take the nudge.

### Option B — Default ON now (canvas v1)

Code Mode is on by default. Skills can opt out via `prefers_codemode: false`. Maximises token savings for long pipelines; re-opens lesson 14 risk until spec 117 is verified in-sandbox.

### Option C — Default OFF permanent

Never default-ON, even after spec 117 verification. Forfeits the structural token savings Code Mode offers. Conservative; loses the upside permanently.

### Option D — Per-tool opt-in (not per-skill)

Each MCP tool declares whether it is safe to call in Code Mode. Finer-grained; loses skill-level workflow context. Combinatorial: a skill orchestrates many tools, and per-tool opt-in fragments the decision.

## Decision Outcome

**Chosen: Option A — Default OFF; per-skill `prefers_codemode: true` opt-in.**

- Frontmatter key `prefers_codemode: bool` is part of the skill-type `extra:` schema (ADR-0006 `$defs/skill-extra`).
- Default value when absent: `false`.
- The router (ADR-0001 step 6) emits a one-line nudge — *"this skill prefers Code Mode; consider toggling"* — when dispatching an opted-in skill. It does **not** auto-toggle.
- The `@domain_tool` decorator (ADR-0005) records the code-mode opt-in status as a Wave D graph node attribute (`:Skill { prefers_codemode: true }`), enabling `agency_skill_search` to filter on it.
- **Re-open condition:** when spec 117's archive is verified to intercept in-sandbox MCP calls (test fixture: a Code Mode invocation returning a 100 KB body lands in the archive, not in the agent context), a successor ADR re-opens the default. The successor cites this ADR in `adr_supersedes:`; this ADR's `adr_superseded_by:` is updated reciprocally per VOCABULARY §6B.

## Consequences

### Positive

- Closes the lesson-14 in-sandbox risk for the conservative default. Cold-boot context contains no Code-Mode-pulled bodies unless a skill explicitly opts in.
- Per-skill opt-in surfaces the token-savings intent in the skill's own frontmatter — discoverable, not buried in a global config.
- The re-open path is explicit, not implicit — a successor ADR can flip the default without renaming or removing the `prefers_codemode` key (which stays as the override surface).
- Graph-queryable: `agency_skill_search` can rank Code-Mode skills for users who want long pipelines.

### Negative

- Skills that *would* benefit from Code Mode but whose authors didn't add `prefers_codemode: true` get the slower default. This is a discovery cost — surfaced only when an author measures.
- The one-line router nudge is easy to ignore. Skills that need Code Mode for token-feasibility may run out-of-context before the user notices the nudge.
- Default-OFF means the default token cost for a long-pipeline session is higher than the Code-Mode-on case — the conservative default is structurally more expensive on the inner-loop.
- The re-open dance (successor ADR after spec 117 verification) is two coordination steps where one would suffice if we just defaulted ON.

### Neutral

- No skill currently in the corpus opts in; the migration is incremental as authors discover the flag.
- Code Mode's underlying `_AnchorAwareCodeMode` classifier is unchanged — only its default activation is.

## Falsifier triggers

- If spec 117 is verified to intercept in-sandbox MCP calls (test fixture passes) and no successor ADR re-opens default-ON within one release cycle, the re-open path is being routed around — successor ADR.
- If a measurable fraction of long-pipeline skills (say >25%) carry `prefers_codemode: true` after one release cycle, the per-skill opt-in is the de-facto default and the global flag should flip — successor ADR.
- If a lesson-14-class leak is measured in a Code-Mode session in `main` after spec 117 is verified, the verification regime is insufficient — successor ADR re-tightens.
