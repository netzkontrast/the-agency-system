---
type: adr
status: draft
slug: token-budget-invariants
summary: "Token budget invariants (tools/list < 4KB, boot context < 500 tokens, result <= 4KB) are gating requirements."
created: 2026-05-19
updated: 2026-05-19
owner: jules
adr_id: ADR-0009
adr_status: Proposed
adr_owner: jules
adr_tags: [domain:cross, topic:performance]
adr_supersedes: null
adr_superseded_by: null
---

# ADR-0009 — Token budget invariants are gating

## Context and Problem Statement

The entire premise of the plugin refactor is token efficiency (`Plan/000-overview.md:16`). We must formalise the specific numerical limits as hard gating invariants for all changes.

## Decision Drivers

- Preventing gradual context window bloat.
- Ensuring model latency remains low on cold starts.
- Forcing developers to use Code Mode deferral and archive mechanics.

## Considered Options

1. **Strict Numerical Limits** — Enforce specific byte/token counts.
2. **Soft Guidelines** — Encourage "efficiency" without hard limits. Rejected because soft limits inevitably drift upward as features are added.

## Decision Outcome

Chosen option: **Strict Numerical Limits**. The following token budgets are gating invariants:
- `tools/list` cold payload must be < 4 KB.
- Total boot context must be < 500 tokens.
- Per-tool execution result must be ≤ 4 KB (excess is archived/truncated).

## Consequences (Positive / Negative / Neutral)

- **Positive:** Guarantees long-term token efficiency.
- **Negative:** Adds friction to adding new capabilities; forces complex pagination/archiving logic.

## Falsifier triggers

This ADR must be reconsidered and superseded if:
1. Any phase merges a change that demonstrably requires raising these limits (e.g., the baseline schema size exceeds 4 KB).
2. The context window sizes of target models increase to the point where these micro-optimisations are deemed obsolete and removed.
