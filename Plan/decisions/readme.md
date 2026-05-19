---
type: reference
status: ready
slug: plan-decisions-readme
summary: "Architecture Decision Records (ADRs) for the-agency-system, MADR 4.0.0 format. Located at Plan/decisions/NNNN-<slug>.md. Accepted ADRs are T4-immutable per VOCABULARY §6C; revisions land as successor ADRs."
created: 2026-05-18
updated: 2026-05-18
related:
  - harness/VOCABULARY
  - phase-8-operational-hardening/specs/134-plan-adr-convention
---

# `Plan/decisions/` — ADR ledger

Architecture Decision Records following **MADR 4.0.0** conventions, imported from `netzkontrast/agency`'s `/decisions/` (`/tmp/agency-research/decisions/readme.md:17-46`).

## Conventions

- **File path**: `Plan/decisions/NNNN-<kebab-slug>.md` where `NNNN` is a 4-digit zero-padded sequence.
- **Frontmatter**: per `Plan/harness/VOCABULARY.md` §6A + the ADR-specific L2 keys (`adr_id`, `adr_status`, `adr_owner`, `adr_tags`, `adr_supersedes`, `adr_superseded_by`).
- **Body sections** (MADR 4.0.0): `Context and Problem Statement` · `Decision Drivers` · `Considered Options` · `Decision Outcome` · `Consequences (Positive / Negative / Neutral)` · `Falsifier triggers`.
- **Lifecycle**: `Proposed → Accepted → Superseded → Deprecated`. Accepted ADRs are **T4-immutable** per VOCABULARY §6C — amendments land as a successor ADR pointing back via `adr_supersedes`.
- **Falsifier triggers**: every Accepted ADR ships with 2-5 explicit predicates that would mandate a successor. Audited nightly when `bin/agency-lint adr-audit` ships (Phase 8 Spec 134).
- **Reciprocity**: `adr_supersedes` ↔ `adr_superseded_by` enforced by frontmatter validator (Phase 8 Spec 134).

## Index

| ADR ID | Status | Title |
|---|---|---|
| [ADR-0001](0001-master-default-branch.md) | Proposed | Master is the default branch, not main |
| [ADR-0002](0002-sub-spec-zero-padding.md) | Proposed | Plan/ uses zero-padded NNN-<slug>/spec.md for sub-specs |
| [ADR-0003](0003-single-mcp-server.md) | Proposed | One MCP server (agency-system); session-log-mcp is a sibling event store |
| [ADR-0004](0004-five-handler-domains.md) | Proposed | Five handler-bearing domains + agentic skill-only |
| [ADR-0005](0005-four-verb-contract.md) | Proposed | Four-verb harness contract |
| [ADR-0006](0006-code-mode-anchor-triad.md) | Proposed | Code Mode anchor triad is eager; bulk tools are deferred |
| [ADR-0007](0007-context-mode-path-b.md) | Proposed | Context Mode Path B (native manifest) chosen over Path A |
| [ADR-0008](0008-harness-path-a.md) | Proposed | Harness Path A levers ship now; Path B is vision |
| [ADR-0009](0009-token-budget-invariants.md) | Proposed | Token budget invariants are gating |
| [ADR-0010](0010-single-delegate-pre-commit.md) | Proposed | Single delegate pre-commit hook (bin/agency-lint) |
| [ADR-0011](0011-repair-authority-tiers.md) | Proposed | Repair-authority tiers (T1/T2/T3/T4) on every change |
| [ADR-0012](0012-content-tier-ladder.md) | Proposed | Three-tier content ladder |

## When to file an ADR

File an ADR when **all three** apply:

1. The decision affects multiple phases or files (cross-cutting). One-phase decisions live in that phase's README or sub-spec.
2. The decision will be hard to reverse once landed (T3 repair tier per VOCABULARY §6C, or any T4-touching change).
3. The decision has at least one rejected alternative worth documenting — i.e. someone could legitimately disagree.

If only one or two apply: write it inline in the affected spec; if zero: just edit the file.

## Cross-references

- VOCABULARY §6A — frontmatter conventions canon
- VOCABULARY §6C — T1/T2/T3/T4 repair-authority tiers
- Phase 8 Spec 134 — `plan-adr-convention` (the spec that codifies and ships the linter)
- Agency reference: `/tmp/agency-research/decisions/readme.md` (analysed in `Plan/_research/agency-repo-analysis/findings.md` §7)
