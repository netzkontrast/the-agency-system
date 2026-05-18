---
type: adr
status: draft
slug: 0001-deprecate-phase-specs-mirror
summary: "Replace the Plan/phase-N-*/specs/<NNN>-*/spec.md mirror tree with a one-line index in each phase's specs.md table; canonical specs stay at Plan/<NNN>-*/spec.md. Eliminates the silent-drift class of bug surfaced during the harness-vision alignment pass."
created: 2026-05-18
updated: 2026-05-18
adr_id: ADR-0001
adr_status: Proposed
adr_owner: claude
adr_tags:
  - planning-discipline
  - reciprocity
  - duplication
  - harness-alignment
related:
  - harness/VOCABULARY
  - _research/agency-repo-analysis/findings
informs:
  - 134-plan-adr-convention
  - JULES-REVIEW-LOOP
---

# ADR-0001 — Deprecate the `Plan/phase-N-*/specs/<NNN>-*/` mirror tree

## Context and Problem Statement

`Plan/` currently has **two** locations for each sub-spec body:

1. **Canonical**: `Plan/<NNN>-<slug>/spec.md` (top-level, where every sub-spec was originally authored).
2. **Mirror**: `Plan/phase-N-<slug>/specs/<NNN>-<slug>/spec.md` (introduced by commit `9137837 plan: copy each phase's specs into Plan/phase-N-<slug>/specs/`).

The mirror was created so each phase folder would be self-contained. In practice it produced a **silent-drift class of bug**: any edit to one location must be hand-mirrored to the other, with no validator. The harness-vision alignment pass (PR #128, this branch) discovered three concrete drifts during normal edit work:

- `Plan/122-centralized-ontology/spec.md` differed from `Plan/phase-5-ontology-and-graph-wave-d/specs/122-centralized-ontology/spec.md` by three lines after a focused alignment edit, with no warning.
- Same on `Plan/123-agency-tooling-codemode/spec.md` (six lines).
- Same on `Plan/124-graphqlite-codemode/spec.md` (eight lines).

The pattern is exactly what `netzkontrast/agency` calls the **"two-source-of-truth drift"** root cause in its 8-category friction taxonomy (`Plan/_research/agency-repo-analysis/findings.md` §10, item 3). Agency **deliberately avoids** the mirror pattern; reciprocity links (`adr_supersedes`/`adr_superseded_by`, `task_supersedes`/`task_superseded_by`) keep cross-phase navigation working without duplicating the source-of-truth body.

The agency-system project already enforces a stronger version of this in code (`servers/agency-mcp/src/agency_mcp/codemode/manifest.json` is the FastMCP authoritative source; `manifest.json` files inside other handler trees are non-authoritative). The planning layer should adopt the same discipline.

## Decision Drivers

- **Mechanical correctness over manual hygiene.** The mirror cannot be validated by `tools/fm/validate.py` because both files are valid in isolation; only their *equality* is the invariant, and equality validators are slow + brittle.
- **Reviewer attention budget.** Two-location specs mean every reviewer must mentally diff both files before accepting an edit. The PR-load grows linearly with the number of phases.
- **Agency-corroborated anti-pattern.** `Plan/_research/agency-repo-analysis/findings.md` §6.5 and §10 explicitly name the mirror pattern as one of agency's eight cataloged friction-root-causes.
- **Forward-compatibility with VOCABULARY §6B reciprocity rules.** With reciprocity-as-invariant frontmatter (`supersedes` ↔ `superseded_by`), every sub-spec already declares its phase membership via its frontmatter; the mirror tree adds no information.

## Considered Options

### Option 1 — Status quo: keep both locations, ship a validator
Add `bin/agency-lint mirror-equality` that fails CI on any mismatch.

**Rejected.** Equality validators are expensive (full-text diff per spec on every CI run). Brittle to whitespace and reordering. Doesn't address the reviewer-attention cost. Symptomatic fix, not root-cause.

### Option 2 — Replace the mirror with a one-line table in each phase's `specs.md` (chosen)
Each `Plan/phase-N-*/` folder gains a `specs.md` file (NEW) containing one row per sub-spec: slug, status, link to canonical, one-line summary. The `Plan/phase-N-*/specs/<NNN>-*/spec.md` mirrors are **deleted**. The phase folder still has its own `README.md` (architecture framing) + `acceptance.feature` (Gherkin) + `specs.md` (this new index) + `_research/` (phase-scoped research if any).

**Benefits:**
- Zero duplication — canonical specs are the only source of truth.
- Each phase still self-narrates: README + acceptance.feature + specs.md is enough context.
- The `specs.md` index is mechanically validatable: every row must link to an existing canonical file; every canonical file in the phase's `affects:` membership must appear in the table.
- Migrates cleanly to VOCABULARY §6B reciprocity (phase membership is a single frontmatter field).

### Option 3 — Delete the canonical top-level specs and keep only the phase mirrors
**Rejected.** Older specs (001-099) predate the phase organisation and have no natural "home phase" (e.g., Spec 099 is split across Phase 0 stub and Phase 8 full). Forcing phase-only location would lose this nuance. Also: the top-level `Plan/<NNN>-*/` paths are heavily cited in commit messages, PR bodies, and other specs — moving them en masse would invalidate ~hundreds of references.

## Decision Outcome

**Adopt Option 2.** Concretely:

1. Author `Plan/phase-N-*/specs.md` for each of the nine phases (0-8). Each is a short markdown table:
   ```markdown
   # Phase N — sub-spec index

   | Spec | Status | Canonical | Summary |
   |---|---|---|---|
   | 104 | ready | [Plan/104-tool-search-anchor-triad/spec.md](../104-tool-search-anchor-triad/spec.md) | Eager anchor triad ... |
   | 105 | draft | [Plan/105-toon-serializer/spec.md](../105-toon-serializer/spec.md) | TOON list-shape serializer ... |
   | ... |
   ```

2. **Delete the `Plan/phase-N-*/specs/` directories** (the mirror tree). Preserve any phase-scoped `_research/` subdirectories — those are NOT mirrors, they are phase-local research outputs and have no canonical top-level twin.

3. Update `Plan/000-overview.md` §4 phase map to note: "Per-phase sub-spec index lives at `Plan/phase-N-*/specs.md`; canonical sub-spec bodies live at `Plan/<NNN>-<slug>/spec.md` (one location only)."

4. Update VOCABULARY §1 invariants: "Sub-spec authoring path: `Plan/<NNN>-<slug>/spec.md` (canonical, one location). Phase folders link via `specs.md` index — no body duplication."

5. Add to `bin/agency-lint specs-index` (Phase 8, when `bin/agency-lint` lands): every row in `Plan/phase-N-*/specs.md` MUST resolve to an existing canonical file; every spec whose frontmatter declares a phase membership MUST appear in that phase's `specs.md`.

## Consequences

### Positive
- Eliminates one entire class of silent-drift bug (the §10.3 friction-taxonomy category).
- Reviewer attention budget halved for spec edits.
- Forward-compatible with VOCABULARY §6B reciprocity-as-invariant.
- Mirrors agency's `decisions/` + `tasks/` layout convention (one canonical location per artefact, reciprocity links for cross-references).

### Negative
- One-time migration cost: ~40 mirror files to delete; ~9 `specs.md` files to author. Roughly 1 PR.
- External references to `Plan/phase-N-*/specs/<NNN>-*/spec.md` (if any exist in skills/, docs/, or hooks/) must be updated. A `grep -r 'phase-.*-/specs/'` audit is part of the migration PR.
- Loses the phase folder's "self-contained" property in the strict sense — readers must follow links to read sub-spec bodies. Mitigated by: every phase's `acceptance.feature` already inlines the gherkin scenarios (which is where readers actually go for "what does this phase verify"), and the new `specs.md` table includes one-line summaries.

### Neutral
- The migration PR is mechanical (`git rm -rf` + `git add` the new `specs.md`). T2-additive on the `specs.md` files; T3-structural overall (folder removal). Per VOCABULARY §6C, that means it lands as an opened task with a PR, not an in-place edit — which is exactly what this ADR does.
- Existing references in commit messages (immutable) remain valid as historical text, even though the mirror paths no longer resolve. Git history is T4.

## Falsifier triggers (would reopen this decision)

- **F1.** A third location for sub-spec bodies emerges (e.g., a third index format in `docs/`). The "single canonical" invariant becomes a "two-canonical" invariant — re-evaluate.
- **F2.** Phase folders gain executable scaffolding (CI hooks, generators) that needs spec bodies physically co-located. (No current plan does this; the harness L1/L2/L3 design specifically does not.)
- **F3.** The `specs.md` index format becomes a maintenance liability of its own (e.g., requires per-row YAML, sub-tables, multi-line cells). Re-evaluate vs. a generated index.

Audit cadence: nightly via `bin/agency-lint specs-index-coherent` (when shipped, Phase 8). Initial implementation: this ADR + the migration PR + the index linter together.

## Implementation

This ADR is `Proposed`. Promotion to `Accepted` happens when:
1. VOCABULARY.md §6A/B/C/D land (this PR or follow-up — §6A already done).
2. A migration PR opens that authors the nine `specs.md` files and deletes the mirror tree.
3. Phase 8 Spec 134 (plan-adr-convention) lands with the MADR 4.0.0 schema this ADR uses.

Once `Accepted`, this ADR becomes T4-immutable per VOCABULARY §6C; revisions land as a successor ADR pointing back via `adr_supersedes: ADR-0001`.
