---
type: research-findings
date: 2026-05-18
researcher: claude-opus-4-7 (research-agent 3 of 5)
focus: spec-driven development + spec governance
worktree: /tmp/research-3-spec
branch: claude/research-integration-3-spec-CtdIJ
slot_allocation: [134, 135]
new_specs:
  - 134-plan-adr-convention
  - 135-spec-test-anchor-traceability
---

# Research Findings — Spec-driven development + spec governance (2026-05-18)

## Scope

Compare `netzkontrast/agency`'s task/decision/template surface (TASK.md 516 lines, 95 tasks under `/tasks/`, 12 ADRs under `/decisions/`, validated by `tools/adr/cli.py`) and the Superpowers writing-plans / executing-plans discipline against the-agency-system's current Plan/ model (47 specs, `Plan/JULES_PROTOCOL.md` as the four-gate contract, `_lessons-learned/` and `_session-state/` as informal substrates). Identify gaps Spec 099 does NOT cover and propose narrow, TDD-ready specs in slot range 134–135.

## What the-agency-system already has

- **Spec template + lint scripts** — Spec 099 ships `Plan/_templates/spec-template.md`, `Plan/_lint/check_affects.py` (path-mention validator), `Plan/_lint/check_install_consistency.py` (README↔marketplace name parity), and the review-subagent prompt.
- **PR rebase enforcement** — Spec 102 ships `Plan/_lint/check_rebase_status.py`.
- **Four-gate contract** — `Plan/JULES_PROTOCOL.md` defines Gate 1 (confidence ≥ 0.90), Gate 2 (TDD red→green→refactor), Gate 3 (evidence-form table), Gate 4 (self-review). Strong RFC-2119-adjacent prose; Gherkin Scenarios with `# anchor: <id>` already canonical across all 47 specs.
- **Lessons-learned discipline** — 14 numbered `Plan/_lessons-learned/NN-*.md` files capturing per-failure-mode observations. Advisory, not normative.

## Gaps versus `netzkontrast/agency`

| Gap | Agency mechanism | the-agency-system today | Owned by |
|---|---|---|---|
| ADR / decision-record substrate | `/decisions/` MADR 4.0.0 + `tools/adr/cli.py` validate (12 ADRs) | Implicit only — defaults like "branch = `Master`" live in `<!-- comment -->` blocks of JULES_PROTOCOL.md | **NEW spec 134** |
| Spec ↔ test traceability | `# anchor: <SPEC>.A.<aspect>.<stmt>` in pytest modules; validator scans `tests/` | Gherkin anchors exist in specs (`# anchor: 099.1` etc.) but no test convention, no linter | **NEW spec 135** |
| Spec template enforcement | `templates/task.md` + `tools/fm/validate.py` + `tools/lint-structure.py` | `Plan/_templates/spec-template.md` (post-099) | Spec 099 (existing) |
| Frontmatter validation | `tools/fm/validate.py` (layered L0/L1/L2 + body-schema) | `Plan/_lint/check_affects.py` (path-only) | Spec 099 (existing) |
| Helper-file enumeration | `task_affects_paths` audit | Spec 099's `check_affects.py` | Spec 099 (existing) |
| Synthesis to root spec | `tools/adr/cli.py synthesize` rewrites guarded section of AGENTS.md | No AGENTS.md equivalent → out of scope | Deferred |
| Append-only ADR (T4-immutable) | MADR 4.0.0 + `adr_status: Accepted` lifecycle | None | **Slot 134** |

## Specs authored

### Spec 134 — `Plan/_decisions/` MADR-shaped ADRs

Adds an append-only decision-record substrate under `Plan/_decisions/`. Mirrors `netzkontrast/agency/decisions/` at narrower scope (no synthesis pipeline, no MDL compression, no AGENTS.md-equivalent rewriter). Ships:

- `Plan/_decisions/readme.md` (index + lifecycle contract)
- Two seed ADRs that ratify already-implicit decisions: ADR-0001 codifies `Master` (capitalised) as the default branch; ADR-0002 codifies the `Plan/NNN-slug/spec.md` numbering convention used across all 47 specs.
- `Plan/_templates/adr-template.md` (MADR 4.0.0 scaffold)
- `Plan/_lint/check_adr.py` enforcing: `adr_id` ↔ filename, closed-vocabulary `adr_status`, reciprocal `adr_supersedes` / `adr_superseded_by`, acyclic supersession graph (Kahn's algorithm)
- `tests/unit/lint/test_check_adr.py` with three fixtures (clean, broken-reciprocity, cyclic)
- JULES_PROTOCOL.md §3 patch routing architecture decisions through ADRs rather than inline edits to the protocol file

The two seed ADRs deliver immediate value: every future session that disagrees about the base branch or the spec-folder shape has a binding artefact to cite or supersede.

### Spec 135 — Spec ↔ Test anchor traceability lint

Adds `Plan/_lint/check_anchor_coverage.py` that builds the bidirectional anchor map between Gherkin scenarios in `Plan/*/spec.md` and pytest cases under `tests/`. Two citation forms accepted:

- `# anchor: <id>` comment on the line above `def test_*`
- `@pytest.mark.anchor("<id>")` decorator

Two operating modes: `--mode=strict` (orphan spec anchor → exit 1; default) and `--mode=advisory` (exit 0, stderr report only — realistic default for the current tree where most specs are `status: ready` with no tests yet). `--spec=<id>` filters the report. Orphan-test detection (test cites anchor that no spec declares) is non-negotiable across modes — typo guard.

Companion patches:
- Spec template gains a "Test traceability" note above the Gherkin block
- JULES_PROTOCOL.md Gate 3 evidence-form table gains one row for anchor coverage

## Specs intentionally NOT authored

- **Auto-generate Jules dispatch prompts from spec frontmatter.** `Plan/000-overview.md` already carries the dispatch template, and Spec 099 hardens it. A generator script is a token-saver but would compete with existing tooling rather than fill a gap.
- **Plan-state schema for `Plan/_session-state/`.** The folder is intentionally lightweight (only 2 files today). A schema lint here would constrain the orchestrator's notebook for marginal benefit.
- **BCP-14 keyword-density linter on JULES_PROTOCOL.md.** Agency's `tools/check-rfc2119-polarity.py` is WARN-tier on a much larger root-spec corpus. The-agency-system has a single short protocol file; manual review is sufficient at this scale.
- **Backfilling existing `_lessons-learned/NN-*.md` as ADRs.** Lessons are advisory observations; ADRs are normative decisions. Conversion is per-file judgement, not bulk-mechanical.

## Cross-references to sibling research agents

- Research agent 1/2/4/5 outputs land at `Plan/_session-state/2026-05-18-research-N-*.md`. Slot collisions are prevented by the per-agent slot range (this agent: 134–135).
- Spec 134 depends on Spec 099 (`Plan/_lint/`, `Plan/_templates/` directories) — already merged before Wave C dispatch.
- Spec 135 depends on Spec 099 (same reason).
- Neither spec depends on the other; both can dispatch in parallel.

## Key takeaways

1. **The biggest delta from `netzkontrast/agency` is the missing ADR substrate.** Two repo-wide decisions (`Master` as default branch, `Plan/NNN-slug/` numbering) live only as `<!-- comment -->` or implicit convention. Spec 134 ratifies them in a binding, supersession-aware ledger.
2. **Gherkin anchors are 50%-built.** Every spec uses `# anchor: NNN.M`; no test uses them. Spec 135 ships the validator + dual-citation convention to close the loop without imposing a new test framework.
3. **Spec 099 is the right home for spec-template and frontmatter-lint work — do not re-litigate it.** All findings here are deliberately downstream / orthogonal to 099's scope.

## Frustration Log

- **FL0** — Research-only sweep. No blockers; the agency repo at `/home/user/agency/` is well-organised and the MADR pattern transferred cleanly. The Plan/ tree's existing convention discipline (frontmatter, Gherkin anchors, the four-gate contract) made it easy to identify the two narrow gaps spec 099 leaves open.
