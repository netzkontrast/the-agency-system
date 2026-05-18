# Research Agent 5 of 5 — Process & Quality-Gate Findings (2026-05-18)

## Mandate

Survey `netzkontrast/agency` (`PRE_COMMIT.md`, `MAINTENANCE.md`, `FRUSTRATED.md`, `.githooks/`) and the relevant Superpowers discipline skills (`verification-before-completion`, `receiving-code-review`, `requesting-code-review`, `finishing-a-development-branch`) for process disciplines that `the-agency-system` does not yet absorb. Slot range: 138–139.

## What is already absorbed (do not duplicate)

| Discipline | Owner spec | What it ships |
|---|---|---|
| `affects:` lint, README↔marketplace name-grep | **099** | `Plan/_lint/check_affects.py`, `Plan/_lint/check_install_consistency.py` |
| Spec template hardening (`server_py_edit`, schema-authority, helper-file checklist) | **099** | `Plan/_templates/spec-template.md` |
| Dispatch-prompt hardening (branch, `affects:` ceiling, reviewer dispatch) | **099** | `Plan/000-overview.md` patches |
| Review-subagent template (no Jinja placeholder leaks per L05) | **099** | `Plan/_templates/review-subagent-prompt.md` |
| `agentMessaged → wait` anti-pattern, watcher-heartbeat ban | **099** | `Plan/JULES_PROTOCOL.md` §5 patches |
| Clean-install evidence Gate 3 *policy text* | **099** | Protocol patch only (the *tool* is gap #2 below) |
| Codex bot review backstop policy | **099** | `Plan/JULES_PROTOCOL.md` §8 |
| Post-merge rebase **policy text** | **099** | Protocol patch |
| Post-merge rebase **drift-detection lint** | **102** | `Plan/_lint/check_rebase_status.py` |
| Orchestrator token discipline | **099** | `skills/agentic/orchestrator-discipline/SKILL.md` |
| `_lessons-learned/` curator-authored corpus (14 entries) | (existing) | Narrative, post-hoc, human-curated. **Not** per-session. |

## Orthogonal gaps identified

After cross-checking the 099 + 102 specs and the existing `Plan/_lessons-learned/` corpus against the Agency three-file process suite (`PRE_COMMIT.md` 22 KB + `MAINTENANCE.md` 53 KB + `FRUSTRATED.md` 8 KB), three orthogonal gaps remain:

### Gap A — Mandatory per-session friction declaration (FL0–FL3) → **Spec 138**

`_lessons-learned/` captures what the **curator** noticed *after* a wave. Successful sessions (FL0) and per-session signals never enter the corpus.

Agency mechanises a **per-session falsifiable null baseline** via `FRUSTRATED.md` + `tools/check-fl-declaration.py`. The rationale Agency cites empirically (38 % of 60 friction logs are FL0; absent FL0 the denominator for friction-frequency metrics collapses) applies verbatim. Spec 138 ports the discipline as a small additive layer on top of 099's `_lint/` + `_templates/` framework: every PR body MUST carry a `## Frustration Log` section with one canonical declaration line; a Python 3.11 stdlib-only lint script enforces the contract. We deliberately do **not** ship Agency's 14-variant grammar — one canonical line only.

### Gap B — Mechanical clean-install evidence capture for Gate 3 → **Spec 139**

JULES_PROTOCOL Gate 3 requires every `[x]` claim to be backed by an artefact in `## Evidence`. Today the capture is **manual**: Jules eyeballs `pytest` output and pastes it. Two failure modes already burned PRs:
- **L03 (PR #36, "evidence theatre")**: Green pytest ran under `PYTHONPATH=$PWD/src:$HOME/work/vendor/bitwize-music` — masked the missing `tools/` package. Production import would have failed on a clean clone.
- **L14**: Re-fetching the same PR body to read its `## Evidence` block costs 3–5 kB per call; the orchestrator did this ≥ 6 times in one wave (~25 kB of pure duplication).

099 hardens the *policy text* ("clean-install verification required") but ships **no tool** that produces the evidence by construction. Spec 139 ships `tools/agency-evidence-snapshot.py`: a single-file Python 3.11 stdlib script that runs pytest / ruff / mypy / build / import-smoke, asserts `PYTHONPATH` contains no entries outside the repo root, caps output under 32 KB, and emits a Markdown-fenced `## Evidence` block. Critically, **import-smoke runs from `cwd=/tmp`** so an editable install — not a `sys.path` happy accident — is what answers the import. This is the direct mitigation for Lesson 03.

### Gap C — Pre-commit framework + post-merge auto-rebase implementation (DEFERRED)

Agency runs a 26-step unified pre-commit suite via `tools/check-governance.sh` invoked from `.githooks/pre-commit`. `the-agency-system` has no analogous framework — `hooks/` exists but is empty (`.gitkeep`). Three reasons to defer:

1. **Out of slot range.** Two slots only (138 + 139); a pre-commit framework is a multi-spec wave on its own.
2. **Premature.** Until 099 + 138 + 139 + 102 land, there's no critical mass of governance scripts to wrap.
3. **102 already ships the rebase *detection*.** The implementation of post-merge auto-rebase (vs detection) is naturally a Spec 102 follow-up, not a fresh slot.

Recommend a future Wave-D spec (slot 14x or 15x) named `pre-commit-framework` that wraps `Plan/_lint/check_affects.py`, `check_install_consistency.py`, `check_rebase_status.py`, `check_friction_log.py` (Spec 138), and `tools/agency-evidence-snapshot.py` (Spec 139) under a single `tools/check-governance.sh`-style entry point. The Spec 102 follow-up should ship `tools/post-merge-rebase.sh` that consumes `check_rebase_status.py` output and drives `mcp__github__update_pull_request_branch` per flagged PR.

## Specs authored

| Slot | Slug | Status | Wave | Lines |
|---|---|---|---|---|
| 138 | `frustration-log-protocol` | `draft` | C | ~110 |
| 139 | `evidence-snapshot-helper` | `draft` | C | ~140 |

Both depend_on Spec 099 (need `Plan/_lint/` + `Plan/_templates/`), are 1-Jules-session each, and ship single-file Python 3.11 stdlib-only scripts with TDD-ready acceptance criteria.

## Discipline check

- All paths cited in either spec exist on the worktree OR are produced by an upstream merged spec (verified: 099 ships `Plan/_lint/` and `Plan/_templates/`).
- No idea overlaps with 099 / 102 (checked all 14 Done-When items in 099 and all 7 in 102).
- TDD-ready Done-When in both specs: each spec ships at least one failing-test → green-implementation → refactor cycle.
- External references (`~/agency/FRUSTRATED.md`, `~/agency/tools/check-governance.sh`) cited read-only; no source copy per ADR-0011-style discipline.

## Frustration Log

**Highest Frustration Level: FL0**

Both spec ideas surfaced cleanly from a single read of the comparison points. The pre-existing 099 / 102 cluster narrowed the orthogonal-gap surface to exactly two items — both well-defended by load-bearing lessons (FL0–FL3 rationale ↔ falsifiable null baseline; `PYTHONPATH` validation ↔ Lesson 03's PR #36 "evidence theatre"). No backtracking. (Self-test: the Spec 138 lint script applied to this very findings document would emit `OK:FL.1:level=FL0`.)
