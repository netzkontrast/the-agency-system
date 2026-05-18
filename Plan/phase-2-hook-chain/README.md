# Phase 2 — Hook chain (PreToolUse + PostToolUse + UserPromptSubmit)

This phase implements a robust token-optimizer middleware layer using Claude Code's PreToolUse and PostToolUse hooks. The scope composes five discrete specifications that together ensure agent sessions remain within strict token budgets by aggressively compressing file reads, shell command outputs, and large tool results.

**Specs composed:**
- **Spec 121 (.contextignore)**: Hard-blocks `Read`, `Glob`, and `Grep` on matching paths before caching.
- **Spec 115 (structure-map AST)**: Returns a compact AST skeleton for massive files (>800 KB / 20k lines for Python).
- **Spec 114 (read-cache delta)**: Returns a unified diff on identical mtime file re-reads.
- **Spec 116 (bash-output compression)**: Condenses CLI outputs (pytest, ls, git) while preserving credentials.
- **Spec 117 (tool-result archive)**: Hard-caps any individual tool result at 4 KB in context, offloading the rest to disk with an `expand <id>` hint.

**Token-budget win:**
Expect a 20-30% reduction in total session input tokens for code-heavy workloads, and absolute protection against single-tool context blowouts (hard-capped at 4 KB).

**Relation to the harness ladder:**
Phase 2 is orthogonal to the harness three-layer ladder — it operates at the runtime tool-output compression layer (PreToolUse/PostToolUse hooks), while the harness layers L1/L2/L3 (see [`Plan/harness/VOCABULARY.md`](../harness/VOCABULARY.md) §2) cover *how the plugin's tool surface is reached*. The 4 KB archive cap (Spec 117) is what makes the L1 harness's `call_tool` returns predictable in test fixtures — a single tool result will never blow past 4 KB into the harness's parsed JSON envelope.

**Producer for Phase 6:**
The same archive (Spec 117) and the same session-log (Spec 100, Phase 6) are the data feeds for Phase 6's quality / loop detection — Phase 2 is the *producer*, Phase 6 is the *consumer*.

**Canonical naming:** see [`Plan/harness/VOCABULARY.md`](../harness/VOCABULARY.md).
See [Plan/000-overview.md §4](../000-overview.md#4-dependency-dag-updated-2026-05-18) for the phase map and integration points.
