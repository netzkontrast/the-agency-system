# Phase 6: Quality / loop / compaction

This phase implements a self-healing context and quality-telemetry layer, composing **Specs 100, 118, 119, and 120**. It establishes a durable `session-log-mcp` server to track events across the orchestrator, and introduces fast-twitch (loop detection) and slow-twitch (aggregate quality score) signals to advise the model on its state.

The primary token-budget win is **self-healing context; saving ~47k tokens per loop-detected session** by breaking repetitive diagnostic loops early. The suite also hardens the compaction process by taking smart checkpoints based on fill and quality thresholds, ensuring critical decisions and tool result references survive context truncation.

See [Plan/000-overview.md](../000-overview.md) §4 for the phase mapping within the broader Token-optimizer hook layer fan-out.
