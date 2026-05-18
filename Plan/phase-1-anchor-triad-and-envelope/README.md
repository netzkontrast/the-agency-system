# Phase 1: Anchor triad + envelope

This phase executes the critical path for token-efficiency in the agency system by migrating the plugin to a deferred-schema architecture. The scope encapsulates four interdependent specs:

- **104 (tool-search anchor triad)**: Eagerly registers `agency_tool_search`, `agency_tool_describe`, and `agency_tool_invoke`.
- **107 (cache-breakpoint ordering)**: Positions the prompt-cache breakpoint optimally between the anchor triad and deferred bulk tools.
- **130 (shared ToolResult envelope)**: Unifies domain responses under the `@wrap_envelope` decorator to return structured outcomes.
- **131 (manifest-coverage lint)**: Adds build-time drift detection to ensure all CodeMode tools explicitly declare their load mode in `manifest.json`.

This combination drastically reduces the orchestrator's boot footprint. By deferring bulk tool schemas until explicitly searched or invoked, the `tools/list` payload is crushed from 38 KB down to < 4 KB, and the cold boot context drops from ~34,000 to < 500 tokens.

For the execution position of this phase in the master DAG, refer to [Plan/000-overview.md §4](.../000-overview.md).
