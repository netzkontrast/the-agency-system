# Phase 3 — GitHub MCP summary wrappers

This phase encompasses Spec **106 (github-mcp-summary-wrappers)**, aimed at addressing the #1 token sink in the agency system: the `mcp__github__pull_request_read` tool.

By wrapping GitHub read operations in ephemeral subagents that distil the raw responses into typed Pydantic models, this phase drastically reduces the token footprint presented to the main session.

**Token-budget win:** Raw PR/issue reads dropping from 40-80k tokens down to **≤ 2.5 KB** of serialised summary data.

For architectural context and dispatch order, see the [Overview Map §4](../000-overview.md#4-dependency-dag-updated-2026-05-18).
