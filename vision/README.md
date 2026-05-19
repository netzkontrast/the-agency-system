---
slug: vision-readme
type: vision-charter
status: ready
owner: claude
created: 2026-05-19
updated: 2026-05-19
summary: Navigation map of `vision/`. The folder holds the design for the agency-system 3×N matrix — current canon at `00.1-Overview.md`, implementation plan at `02-plan.md`, eight numbered specs under `specs/`. Phase 1-3 column drafts remain for historical context.
---

# `/vision` — design canon for the agency-system

The agency-system is a **3-column × N-row matrix**: columns are fixed (`agentic`, `workflow`, `context`); rows are domains (music, novel, jules, podcast, …). The vision folder holds the design that drives implementation. Code lives at the REPO ROOT (`agentic/`, `workflow/`, `context/`), not under `vision/`.

## The architecture in one paragraph

One engine — **FastMCP** — walks the **context graph**. Workflows are *paths* through the graph; if a path doesn't exist, the engine lazily links a new one (no fixed pipelines). The context graph has **pluggable drivers** (sqlite, filesystem, repo, S3, HTTP, Drive) — drivers map graph nodes to external substrates. Skills + MCP are the universal interface. User-facing artifacts (audio files, PDFs, reports) are graph nodes routed through whichever driver is configured; there is no special "result" layer, only nodes + drivers.

This architecture dissolves the four cross-column "ownership" tensions surfaced in Phase 3 (gate-edge execution, mid-phase block serialization, hook execution layer, sidecar sandbox). Each was a category error — mixing architecture (one engine + one graph) with user-facing concerns (which driver writes where).

## Canon (read in order)

1. **[`00.1-Overview.md`](00.1-Overview.md)** — matrix law, result registry conclusion, strict cell manifests, column-specific Code Mode contracts.
2. **[`02-plan.md`](02-plan.md)** — implementation plan; dependency graph; folder layout after base layer lands.
3. **`specs/01..05`** — foundation contracts every column honors:
   - [`specs/01-cell-manifest.md`](specs/01-cell-manifest.md) — strict `manifest.toml` + name-derivation rules.
   - [`specs/02-tool-result-envelope.md`](specs/02-tool-result-envelope.md) — frozen FastMCP envelope; extensions in `data`.
   - [`specs/03-sidecar-metadata.md`](specs/03-sidecar-metadata.md) — `.meta.json` schema for binary artifacts.
   - [`specs/04-phase-state-envelope.md`](specs/04-phase-state-envelope.md) — `PhaseStateEnvelope` (under the one-engine reframe this becomes mostly informational — state lives in the graph).
   - [`specs/05-gate-yaml.md`](specs/05-gate-yaml.md) — gate definitions as graph edge constructors.
4. **`specs/06..08`** — per-column base-layer implementation specs (Jules targets):
   - [`specs/06-agentic-base.md`](specs/06-agentic-base.md) — FastMCP harness + four-verb contract.
   - [`specs/07-workflow-base.md`](specs/07-workflow-base.md) — pipeline runner + meta-row scaffold (one-engine reframe pending: see "Reframing in flight" below).
   - [`specs/08-context-base.md`](specs/08-context-base.md) — graph store + Pre/PostToolUse hooks + shared schemas (one-engine reframe pending: drivers).

## Per-column design archive (Phase 1-3 + meta)

Each column folder under `vision/` carries the work that produced the canon above. Treat as historical reference, not active spec.

- **`agentic/`** — `BRIEF.md`, `COLUMN.md`, `INTERFACES.md`, `INTERFACE-TO-{WORKFLOW,CONTEXT}.md`, `GHERKIN-OWNED.md`, `ROW-EXAMPLES.md`, `RESEARCH-PATTERNS.md`, `REVIEW-OF-{WORKFLOW,CONTEXT}.md`, `INTEGRATED-DRAFT.md`, `Vision.md`.
- **`workflow/`** — same structure plus `META-WORKFLOW.md`; integrated draft introduces `PhaseStateEnvelope`.
- **`context/`** — same structure plus `ONTOLOGY.md`; integrated draft introduces the sidecar metadata pattern.

## Reframing in flight (post-base-layer)

The base-layer specs (06/07/08) were written under the *boundaries-between-columns* framing. The one-engine + drivers framing — articulated AFTER the specs landed — supersedes that on two specific points:

- **Workflow:** phases are not pre-declared markdown files (the `phases/<NN>-*.md` model in spec 07). Phases are graph nodes; the workflow runner is a graph traverser, not a pipeline; lazy path-creation is a first-class operation. Follow-up: rewrite spec 07 under this lens before row scaffolding starts.
- **Context:** the SQLite-only store in spec 08 is one driver. Context owns a pluggable driver registry (sqlite default; fs / repo / s3 / http / drive available). Follow-up: rewrite spec 08 to specify the driver interface; SQLite remains the default driver.

These follow-ups land as `vision/03-architecture.md` + a refactor wave after the base-layer PRs merge.

## Out of scope (will land in later passes)

- Row-specific cells (`agentic/music`, `workflow/jules`, `context/podcast`, …) — scaffolded via the meta-row after base lands.
- Cross-row dispatch (planned `specs/09-cross-row-dispatch.md`).
- Central plugin bootloader (planned `specs/10-bootloader.md`).
- Driver implementations beyond SQLite (planned in `03-architecture.md` refactor).

## Charter (superseded)

[`00-charter.md`](00-charter.md) holds the original matrix law + 18 Gherkin scenarios. Superseded by `00.1-Overview.md`; kept for traceability.
