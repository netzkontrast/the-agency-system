# Phase 6: Quality / loop / compaction

This phase implements a self-healing context and quality-telemetry layer, composing **Specs 100, 118, 119, and 120**. It establishes a durable `session-log-mcp` server to track events across the orchestrator, and introduces fast-twitch (loop detection) and slow-twitch (aggregate quality score) signals to advise the model on its state.

The primary token-budget win is **self-healing context; saving ~47k tokens per loop-detected session** by breaking repetitive diagnostic loops early. The suite also hardens the compaction process by taking smart checkpoints based on fill and quality thresholds, ensuring critical decisions and tool result references survive context truncation.

The loop-detection and quality-score signals are **runtime advice, not gates** — they emit `additionalContext` nudges only and never block a tool call.

**Sibling-server exception:** `servers/session-log-mcp/` is an *append-only event store* consumed via PostToolUse / UserPromptSubmit / PreCompact hooks, not a tool surface visible to the model. It therefore does not violate the "one MCP server" north-star invariant in [Plan/000-overview.md](../000-overview.md) §1, which constrains the *tool surface* exposed by `agency-mcp`. See [Plan/harness/VOCABULARY.md](../harness/VOCABULARY.md) for canonical naming.

**Cross-phase data flow:** Phase 6 is the **consumer** of Phase 2's archive (Spec 117 `archive_ids` survive compaction checkpoints — see `phase-6.archive-ids-survive-compaction`) and the **producer** of Phase 8's frustration-log telemetry (Spec 138).

**Test harness hint:** the L1 in-process harness (`tests/_harness/`) boots `agency-mcp` only; Phase 6 unit tests should fixture the `session-log-mcp` event store separately rather than booting it through the L1 harness.

See [Plan/000-overview.md](../000-overview.md) §4 for the phase mapping within the broader Token-optimizer hook layer fan-out.
