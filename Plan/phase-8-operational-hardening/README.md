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
- 023 (harness-in-harness research epic)
- 099 (orchestration improvements)

**Token-budget win:** polish + bus-factor + cross-harness portability.

See the [Dependency DAG in Plan/000-overview.md §4](../000-overview.md#4-dependency-dag-updated-2026-05-18) for how this phase connects to the broader unified plugin rollout.
