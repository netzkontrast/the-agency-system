# Phase 1: Anchor triad + envelope (cold-start)

This phase executes the critical path for token-efficiency in the agency system by migrating the plugin to a deferred-schema architecture. The scope encapsulates interdependent specs plus the harness substrate that supports them:

- **104 (tool-search anchor triad)**: Eagerly registers `agency_tool_search`, `agency_tool_describe`, and `agency_tool_invoke` — the canonical MCP-wire form of the four-verb contract's `list_tools` / `call_tool` verbs (see [Plan/harness/VOCABULARY.md §3](../harness/VOCABULARY.md)).
- **105 (TOON serializer)**: Homogeneous list serialization optimizations.
- **107 (cache-breakpoint ordering)**: Positions the prompt-cache breakpoint optimally between the anchor triad and deferred bulk tools.
- **130 (shared ToolResult envelope)**: Unifies domain responses under the `@wrap_envelope` decorator. This source-level baseline is what the future Harness Path B endgame (`Plan/harness/restructure/spec.md` lever L-ζ) formalizes as `BinaryEnvelope`.
- **131 (manifest-coverage lint)**: Adds build-time drift detection to ensure all CodeMode tools explicitly declare their load mode in `manifest.json`.
- **L1 in-process harness + L2 subprocess probe** — shipped (PR #127). Substrate for Spec 131's `tests/smoke/test_boot_budget.py` and Spec 105's `tests/smoke/test_toon_gate.py`. See [Plan/harness/design.md §3 (L1)](../harness/design.md) and §4 (L2).

This combination drastically reduces the orchestrator's boot footprint. By deferring bulk tool schemas until explicitly searched or invoked, the `tools/list` payload is crushed from 38 KB down to < 4 KB, and the cold boot context drops from ~34,000 to < 500 tokens.

Canonical naming for terms used in this phase lives in [Plan/harness/VOCABULARY.md](../harness/VOCABULARY.md). For the execution position of this phase in the master DAG, refer to [Plan/000-overview.md §4 and §9](../000-overview.md).