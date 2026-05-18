# Research Agent 2 — Skills + Skill-Creator + Skill-Discovery Findings

> **Date:** 2026-05-18
> **Branch:** `claude/research-integration-2-skills-CtdIJ`
> **Slot range:** 132-133
> **Reviewer:** parallel research sweep — agent 2 of 5

## Scope reviewed

| Source | Files / sections consumed |
|---|---|
| netzkontrast/agency repo (`/home/user/agency/`) | `SKILLS.md`, `CLAUDE.md` §13 + §14, `tools/hooks/_{pre,post}_tool_use.py`, `tools/hooks/_common.py`, `tools/check-hooks.py`, `tools/fm/skills_query.py`, `skills/skills-skill-bootstrap/sync.sh`, `skills/skills-skill-bootstrap/readme.md` |
| superpowers plugin (`/root/.claude/plugins/cache/superpowers-marketplace/superpowers/5.1.0/`) | `skills/writing-skills/SKILL.md`, `skills/writing-skills/testing-skills-with-subagents.md`, `skills/writing-skills/anthropic-best-practices.md`, `skills/test-driven-development/SKILL.md` |
| the-agency-system tree (Master tip) | `Plan/000-overview.md` §2.2 + §2.3, `Plan/JULES_PROTOCOL.md` §3+§7, `Plan/005-music-skills-port/spec.md`, `Plan/007-jules-skills-and-commands-port/spec.md`, `Plan/015-novel-skills-catalogue/spec.md`, `Plan/016-agentic-handlers-and-skills/spec.md`, `Plan/017-hooks-port-and-extend/spec.md`, `Plan/099-jules-orchestration-improvements/spec.md`, `Plan/118-quality-score-telemetry/spec.md`, `Plan/022-dev-mode-install/spec.md`, `Plan/098-wave-a-hardening/spec.md`, `jules-plugin/skills/jules/SKILL.md` |

## Gap-analysis matrix

| Idea surfaced in reference | Status in the-agency-system | Action |
|---|---|---|
| L1+L2 §2.2 schema (`type`, `status`, `slug`, `summary`, `skill_kind`, `skill_target_agents`, `skill_references_*`, `skill_bootstrap_required`) | **Already documented** in `Plan/000-overview.md` §2.2 and absorbed by Spec 099 (frontmatter migration extended on PR #66). | No spec. |
| `skill_qc_lint.py` (frontmatter linter, 10-item QC) | **Already owned** by Spec 015 (and referenced by Spec 005). | No spec. |
| `:embed` vs bare-slug composition signal | **Already documented** in §2.2 + Spec 015 QC item 7 | No spec. |
| Linter computes reciprocity (don't author `skill_referenced_by`) | **Already covered** in §2.2 + Spec 015 QC item 8 | No spec. |
| `plugin_help(domain)` cheat-sheet generator | **Already owned** by Spec 016 (overview §2.1 anchor) | No spec. |
| `skill_bundles_tools` (agency ADR-0007 — materialise repo tools next to synced skills) | **Out of scope** for the-agency-system in this slot range; the plugin's tools live alongside skills by virtue of being one repo. | No spec. |
| `~/.claude/skills/` sync (agency `sync.sh`) | **Out of scope** — the-agency-system is loaded via `--plugin-dir` (Spec 022); not synced to user-scope. | No spec. |
| `SessionStart` skill bootstrap | **Banned by reference** ([agency ADR-0011 §D.7](https://github.com/netzkontrast/agency/blob/main/decisions/0011-external-skill-corpora-import.md)); explicitly out of scope per §2.3 — no `SessionStart`. | No spec. |
| `tools/check-hooks.py` (governance check H.1.1 / H.1.2 / H.1.3) | **Implicit scope** of Spec 017 `hooks/install.sh`; could be a Wave-D backlog item but not a clear gap yet. | No spec. |
| Skill version / changelog convention | The §2.2 `created` / `updated` already carry the version axis. No CHANGELOG.md per skill in either reference. | No spec. |
| Skill telemetry (per-spec `skill-invocation-log.md`) | **Not covered** by any existing spec. Spec 118 measures **quality** but not skill-specific invocation. Spec 100 is session-log-mcp (different shape). | **Spec 132** — Skill-Tool Hooks. |
| Manifest verification at runtime (PreToolUse `Skill` matcher refuses unknown slugs) | **Not covered** by any existing spec. Spec 017 only ports `Write\|Edit` validators. Spec 132's manifest-verify is the runtime complement to Spec 015's commit-time `skill_qc_lint.py`. | **Spec 132** — Skill-Tool Hooks. |
| Completion-claim gating (PreToolUse advisory on "done"/"complete"/"ready") | **Not covered**. Spec 016 ships a `verification-before-completion` SKILL.md but has no runtime gate that suggests routing through it. | **Spec 132** — Skill-Tool Hooks. |
| Forward-chain suggestion from `skill_references_skills` (PostToolUse) | **Not covered**. Agency's `_post_tool_use.py` does this; no analogue in the-agency-system. | **Spec 132** — Skill-Tool Hooks. |
| Subagent pressure-test framework (TDD for skills) | **Not covered**. Spec 015 lints frontmatter; nothing tests **behaviour under pressure**. Superpowers' `writing-skills/testing-skills-with-subagents.md` is the canonical reference. | **Spec 133** — Skill Subagent-Pressure Test Framework. |
| Scenario YAML schema (pressures + compliant + violation + rationalisation lists) | **Not covered**. | **Spec 133**. |
| Dry-run rubric scoring (no LLM round-trip) | **Not covered**; needed so pytest stays LLM-free. | **Spec 133**. |

## Specs authored

- **Plan/132-skill-tool-hooks/spec.md** — Two new hooks on `Skill\|Agent` matcher (PreToolUse + PostToolUse). PreToolUse exits 2 on manifest-miss, advisory `additionalContext` on completion verbs, telemetry-append to per-spec `skill-invocation-log.md`. PostToolUse appends telemetry + emits first-3 forward-chain suggestions from `skill_references_skills`. Depends on Spec 017 (which only wires `Write\|Edit`). Wave C, 1 session.
- **Plan/133-skill-subagent-pressure-tests/spec.md** — Python CLI `tools/skill_pressure_test.py` + `skills/agentic/skill-tdd/SKILL.md` discipline-kind skill + three example scenario YAMLs for `orchestrator-discipline`, `spec-skill`, `verification-before-completion`. Pytest covers dry-run path only (LLM-free); wet-run is one-shot human evidence. Depends on Specs 015 (lint), 016 (subagent dispatch + the three skills being scenario-tested), 132 (runtime complement). Wave C, 2 sessions.

## Three key findings

1. **The §2.2 schema is documented but runtime-unverified.** Every existing spec (015, 099, 005, 007) treats `skill_references_skills` as a commit-time lint target. Nothing rejects a typo'd `/agency-system:music-lyric-wrier` at invocation. Agency repo's `tools/hooks/_pre_tool_use.py` (≈110 lines) solves this in ~1 spec-session; the-agency-system has the slot but no spec — Spec 132 fills it.

2. **Discipline-kind skills are authored but never tested for behavioural compliance.** Spec 099's `orchestrator-discipline` (L14 token-discipline), Spec 016's `verification-before-completion` and `spec-skill` all rely on the agent voluntarily following the rule. Superpowers' canonical `writing-skills/testing-skills-with-subagents.md` is the only place in any of the three reviewed sources that codifies pressure-testing skills. No existing the-agency-system spec maps to it; Spec 133 ports the pattern with a YAML scenario format and a dry-run rubric so pytest stays LLM-free.

3. **The skill-invocation telemetry signal does NOT exist yet, and Spec 118 (quality-score) implicitly depends on it.** Spec 118 measures session-wide quality via 7 weighted signals; per-skill invocation patterns (which skills fire most, which fail manifest, which trigger completion-verb suggestions) are not captured anywhere. Spec 132's per-spec `skill-invocation-log.md` is the simplest possible append-only data source — it lights up Spec 118 and Spec 099's `orchestrator-discipline` enforcement without adding a new MCP tool.

## Discipline notes

- Both specs preserve the §2.2 contract verbatim — they consume it, never re-propose it.
- Both specs cite a real reference file with a clone command. Spec 132's primary reference is agency's `tools/hooks/_pre_tool_use.py`; Spec 133's primary references are the three Superpowers `writing-skills/*` files.
- TDD-readiness: Spec 132 has 5 parametrized fixture-driven tests; Spec 133 has 6 dry-run-only pytest tests so they stay LLM-free + deterministic. Every Done-When is testable; every Gherkin scenario names a real file/command.
- No file path is invented — every referenced path either already exists in Master, is listed under the spec's `affects:`, or is in `~/work/vendor/` per a clone command.
- Both specs explicitly call out their **NOT-overlap** with adjacent specs in the `## Out of scope` section.
