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

Chosen option: **Strict Numerical Limits with one documented exception**. The following token budgets are gating invariants:
- `tools/list` cold payload must be < 4 KB.
- Total boot context must be < 500 tokens.
- Per-tool execution result must be ≤ 4 KB (excess is archived/truncated **by the Spec 117 PostToolUse `archive_hook.py`**, the runtime mechanism the cap applies to).

**Documented exception — Context Mode reads.** `context_read(view="full")` is explicitly exempt from the 4 KB result cap. The shipped reader (`_context_read` in `servers/agency-mcp/src/agency_mcp/handlers/context/`) sizes the response off the manifest entry's `byte_length` field and truncates only when `token_estimate > 4000` (not bytes > 4096). This means `context_read(view="full")` can legitimately return documents larger than 4 KB — e.g. `docs/superpowers/specs/2026-05-16-jules-suite-refactor-design.md` at ~14 KB / ~3.7k tokens — without violating the invariant. The rationale: the 4 KB cap was authored for the Spec 117 archive-and-truncate path, which handles *opaque* tool outputs. `context_read` returns *known artefacts* the caller explicitly requested by ID and view (`summary`/`preview`/`full`); applying the 4 KB cap there would truncate legitimate full reads and force callers into multi-call dances that defeat the manifest's point. The token-based truncation in `_context_read` is the right boundary for that surface.

## Consequences (Positive / Negative / Neutral)

- **Positive:** Guarantees long-term token efficiency for opaque tool returns (Spec 117 archive path).
- **Positive:** Preserves the usefulness of `context_read(view="full")` for documents legitimately larger than 4 KB.
- **Negative:** Adds friction to adding new capabilities; forces complex pagination/archiving logic for tools outside the context-read surface.
- **Neutral:** The exception is narrow — it applies *only* to `context_read` (and any future read surface that returns caller-requested artefacts by ID + view). All other tool returns remain subject to the 4 KB cap.

## Falsifier triggers

This ADR must be reconsidered and superseded if:
1. Any phase merges a change that demonstrably requires raising these limits (e.g., the baseline schema size exceeds 4 KB).
2. The context window sizes of target models increase to the point where these micro-optimisations are deemed obsolete and removed.
