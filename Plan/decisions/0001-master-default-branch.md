---
type: adr
status: draft
slug: master-default-branch
summary: "Master is the default branch (not main) across the-agency-system repository."
created: 2026-05-19
updated: 2026-05-19
owner: jules
adr_id: ADR-0001
adr_status: Proposed
adr_owner: jules
adr_tags: [domain:cross, topic:git]
adr_supersedes: null
adr_superseded_by: null
---

# ADR-0001 — Master is the default branch, not main

## Context and Problem Statement

The repository's default branch for all PRs and fresh specs needs to be consistent to avoid merge conflicts and lost work. Historically, the repository has used `Master` (capitalised) as the default branch, as documented in a comment within `Plan/JULES_PROTOCOL.md:68`. We need a formal decision to solidify this convention across all operations.

## Decision Drivers

- Minimising Git checkout/merge friction.
- Backward compatibility with existing branch histories.
- Aligning with the existing GitHub default branch configuration.

## Considered Options

1. **`Master`** — Keep the existing, capitalised default branch name.
2. **`main`** — Migrate to the modern standard `main`. This was rejected because the migration cost is high, it requires updating all internal tool configurations, and `Master` is already entrenched in the CI/CD and repository settings.
3. **`master`** — Use the lowercase form. Rejected because the repository was initialised with the capitalised form and changing case often causes issues on case-insensitive filesystems (like macOS default).

## Decision Outcome

Chosen option: **`Master`**. We continue to use the capitalised `Master` branch as the default target for all Pull Requests, new specs, and continuous integration pipelines.

## Consequences (Positive / Negative / Neutral)

- **Positive:** No migration effort required; existing workflows and scripts (like those generating PRs) remain unbroken.
- **Negative:** Deviates from the broader open-source ecosystem trend towards `main`, causing minor friction for new developers.
- **Neutral:** The name is arbitrary as long as it is consistently applied.

## Falsifier triggers

This ADR must be reconsidered and superseded if:
1. The GitHub repository default branch is administratively changed to `main` or another name.
2. A mandate is issued to align all company/project repositories to `main`.
