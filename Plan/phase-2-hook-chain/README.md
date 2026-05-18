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

See [Plan/000-overview.md §4](../000-overview.md#4-dependency-dag-updated-2026-05-18) for the phase map and integration points.
