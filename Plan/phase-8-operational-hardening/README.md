# Phase 8 — Operational hardening

Phase 8 encompasses the operational hardening and cross-harness portability layer of the Agency-System unified plugin. This phase implements robust quality gates, architectural disciplines, and integration tests to ensure that the unified plugin is stable, easily extensible by non-authors, and portable to alternative agent harnesses.

This phase composes the following specs:
- 102 (pr-rebase policy)
- 132 (skill-tool hooks)
- 133 (skill-subagent pressure tests)
- 134 (plan-ADR convention)
- 136 (agents.yaml role manifest)
- 137 (watcher SDK composability)
- 138 (frustration-log protocol)
- 139 (evidence-snapshot helper)
- **L3 sidecar daemon + CLI** (per `Plan/harness/design.md` §5; absorbs Spec 023 items 2-3-5-6-7-8-basic) — ships `bin/agency` + `servers/agency-mcp/src/agency_mcp/lib/devmode/` + `tests/integration/test_devmode_server.py` + `docs/architecture/harness-in-harness.md`. Spec 023 retains items 1 (≥1500-word prior-art survey) + 4 (progressive-disclosure 4-tier ladder) as a research-remainder, with follow-up at `Plan/harness/L3-progressive-disclosure.md`.
- 099 (orchestration improvements)

**L3 is the third layer of the harness ladder.** L1 (in-process FastMCP) and L2 (subprocess `claude --bare` probe) shipped in Phase 1 (PR #127); L3 (sidecar daemon + `bin/agency` CLI) is the Phase 8 deliverable. See `Plan/harness/VOCABULARY.md` §2 for the canonical layer table.

**agents.yaml (Spec 136) is the discoverability layer** for the L3 daemon's `agency agent list` / `agency agent describe` CLI verbs — forward-compat with the L3 surface.

**Token-budget win:** polish + bus-factor + cross-harness portability.

Canonical naming for this phase (layer names, verb names, file paths) lives in [`Plan/harness/VOCABULARY.md`](../harness/VOCABULARY.md). See the [Dependency DAG in Plan/000-overview.md §4](../000-overview.md#4-dependency-dag-updated-2026-05-18) for how this phase connects to the broader unified plugin rollout.
