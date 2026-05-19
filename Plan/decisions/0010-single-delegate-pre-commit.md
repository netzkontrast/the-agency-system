---
type: adr
status: draft
slug: single-delegate-pre-commit
summary: "The pre-commit hook delegates to a single tool (bin/agency-lint) with sub-commands, avoiding script sprawl."
created: 2026-05-19
updated: 2026-05-19
owner: jules
adr_id: ADR-0010
adr_status: Proposed
adr_owner: jules
adr_tags: [domain:cross, topic:tooling]
adr_supersedes: null
adr_superseded_by: null
---

# ADR-0010 — Single delegate pre-commit hook (bin/agency-lint)

## Context and Problem Statement

The repository needs automated governance checks (manifest coverage, frontmatter validation, etc.). Previous implementations (as researched in `Plan/_research/agency-repo-analysis/findings.md` §2.1 and §8.1-8.2 (e.g., `Plan/_research/agency-repo-analysis/findings.md:10-50`)) suffered from script sprawl, where dozens of separate bash scripts were executed by `pre-commit`, causing maintenance burden and slow execution.

## Decision Drivers

- Execution speed of pre-commit hooks.
- Centralising validation logic into a testable Python module rather than fragile bash scripts.
- Avoiding the "30 separate scripts" anti-pattern.

## Considered Options

1. **Single Delegate (`bin/agency-lint`)** — The `pre-commit` hook calls one Python CLI with sub-commands.
2. **Multiple Independent Scripts** — One script per check. Rejected due to the historical anti-pattern of script sprawl and slow startup times.
3. **Third-Party Framework** — Use `pre-commit.com` framework. Rejected because it introduces external dependencies and Python environment complexities that break the bare `bin/agency-dev-install` flow.

## Decision Outcome

Chosen option: **Single Delegate (`bin/agency-lint`)**. When Phase 8 ships, the `.githooks/pre-commit` file will delegate entirely to a single tool, `bin/agency-lint`, which handles all checks via sub-commands (e.g., `manifest-coverage`, `adr-validate`).

## Consequences (Positive / Negative / Neutral)

- **Positive:** Faster execution due to a single Python interpreter startup.
- **Positive:** Easier to test validation logic using standard `pytest`.
- **Negative:** The single script can become a bottleneck if not modularised properly internally.

## Falsifier triggers

This ADR must be reconsidered and superseded if:
1. The number of sub-commands in `bin/agency-lint` grows past ~10, necessitating a split.
2. A third-party linting framework is adopted repo-wide.
