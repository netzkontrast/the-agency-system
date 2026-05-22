# Phase 3 — GitHub MCP summary wrappers

This phase encompasses Spec **106 (github-mcp-summary-wrappers)**, aimed at addressing the #1 token sink in the agency system: the `mcp__github__pull_request_read` tool (40-80k tokens per call).

By wrapping GitHub read operations in ephemeral subagents (via the `superpowers:dispatching-parallel-agents` pattern) that distil the raw responses into typed Pydantic models, this phase drastically reduces the token footprint presented to the main session.

**Wrapper tools (Spec 106):** `gh_pr_summary`, `gh_issue_summary`, `gh_review_summary`. All three conform to the **shared ToolResult envelope** introduced in Phase 1 Spec 130 — the same envelope contract every other domain tool uses (see [`Plan/harness/VOCABULARY.md`](../harness/VOCABULARY.md) §1 invariants).

**Code location:** the wrappers live under `handlers/shared/` today (Harness Path A; under Harness Path B they would live under `domains/shared/`). They cross domains, so they are correctly tagged `domain:shared` per VOCABULARY §5.

**Forward compatibility:** these wrappers are one instance of the general "ephemeral-subagent offload" pattern. That pattern is forward-compatible with the L3 sidecar daemon (Phase 8) — the daemon could in principle host its own ephemeral subagent dispatcher for any high-token tool — though no current design item commits to that.

**Token-budget win:** Raw PR/issue reads dropping from 40-80k tokens down to **≤ 2.5 KB** of serialised summary data.

For canonical naming see [`Plan/harness/VOCABULARY.md`](../harness/VOCABULARY.md). For architectural context and dispatch order, see the [Overview Map §4](../000-overview.md#4-dependency-dag-updated-2026-05-18).
