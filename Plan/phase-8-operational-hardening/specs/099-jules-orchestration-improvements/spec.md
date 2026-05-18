---
spec_id: 099
slug: jules-orchestration-improvements
status: ready
owner: jules
depends_on: [020]
affects:
  - Plan/JULES_PROTOCOL.md
  - Plan/000-overview.md
  - Plan/_lint/check_affects.py
  - Plan/_lint/check_install_consistency.py
  - Plan/_lint/check_skill_frontmatter.py
  - Plan/_templates/review-subagent-prompt.md
  - Plan/_templates/spec-template.md
  - Plan/_templates/skill-template.md
  - skills/agentic/orchestrator-discipline/SKILL.md
  - skills/jules/SKILL.md
  - jules-plugin/skills/jules/SKILL.md
# Skill-frontmatter migration sweep (Approach §13 + Done-When item
# "§2.2 skill-frontmatter migration") covers every SKILL.md discovered
# under skill_migration_roots at session start. The currently-known
# files are listed above in `affects:`; any additional SKILL.md found
# at session start under skill_migration_roots is added to `affects:`
# by the executing session as its first edit.
skill_migration_roots:
  - skills/
  - jules-plugin/skills/
source-repos: []
estimated_jules_sessions: 2
domain: cross
wave: C
---

> **Jules: read `Plan/JULES_PROTOCOL.md` before starting.** Run gates 1→4 in order:
> (1) Confidence ≥ 0.90, (2) TDD Red-Green-Refactor, (3) Evidence pasted under `## Evidence`, (4) Self-Review answered.
> Branch: `Master` (default base for fresh specs post-Wave-A; see JULES_PROTOCOL.md §3). Only modify paths under `affects:` below.
> Source repos under `source-repos:` are clone-and-read-only into `~/work/vendor/`; never commit them.
> If anything is ambiguous, open a draft PR labelled `[BLOCKED: clarification]` and stop — do not guess.

# Spec 099 — Jules Orchestration Improvements

## Why

Wave A and Wave B surfaced ~15 distinct orchestrator-level failure modes — silent `agentMessaged` waits killing sessions (L02), evidence captured under a polluted PYTHONPATH (L03), `affects:` lists missing helper files (L04), schema/spec drift discovered only at merge (L06), Codex bot reviews arriving after merge (L13), token blow-ups from full-activity dumps (L14). Each lesson has been recorded but the protocol, lint scripts, and templates that codify them have not been updated. Without this consolidation, every future spec re-pays the same tuition. This spec folds lessons 01–15 into mechanical changes (protocol patches, lint scripts, template stickers, a new skill) so the next wave of specs cannot regress into the same traps.

A late addition (2026-05-18): the 32-spec hygiene pass and the first batch of `skills/agentic/*` authoring both demonstrated that no SKILL.md in the repository follows the L1 + L2 + 5-section schema documented in `Plan/000-overview.md` §2.2. The contract is unenforced, and authors (Jules and local subagents alike) match whatever prior skill they read first. This spec absorbs the skill-frontmatter migration alongside the spec-frontmatter lint, so the retrofit happens once, uniformly, with linter enforcement.

## Done When

- [ ] `Plan/JULES_PROTOCOL.md` §3 redefines "scratch files" to include PR body composition drafts (L01).
- [ ] `Plan/JULES_PROTOCOL.md` §6 prohibits the `agentMessaged → wait` anti-pattern and lists the escalation path (L02 + 006a silent-fail).
- [ ] `Plan/JULES_PROTOCOL.md` Gate 3 mandates a clean-install (`pip install -e . && cd /tmp`) before capturing evidence (L03).
- [ ] `Plan/JULES_PROTOCOL.md` Gate 4 contains a "dispatch independent review subagent" sub-step (L05).
- [ ] `Plan/JULES_PROTOCOL.md` §8 "Automated review backstop" exists and names Codex as primary, OSS Codex-fallback (today's rate-limit failure) as secondary (L13).
- [ ] `Plan/JULES_PROTOCOL.md` Appendix "Tool gaps & workarounds" documents: `jules_stop` unsupported, `jules_message` is input-only not control-plane (L08, L10).
- [ ] `Plan/_templates/spec-template.md` includes `server_py_edit: append-only` annotation (L07), a `## Schema authority` section (L06), and a helper-file enumeration checklist (L04).
- [ ] `Plan/_templates/spec-template.md` Acceptance section includes a README↔marketplace name-grep gate (today's drift bug).
- [ ] `Plan/_lint/check_affects.py` exists and exits non-zero when a spec's `affects:` list misses a file the Approach section names.
- [ ] `Plan/_lint/check_install_consistency.py` exists and greps README + `.claude-plugin/marketplace.json` for plugin-name parity.
- [ ] `Plan/_templates/review-subagent-prompt.md` exists and is the canonical prompt body for the Gate 4 review subagent.
- [ ] `Plan/JULES_PROTOCOL.md` §5 anti-patterns lists the watcher heartbeat experiment (L15b) as forbidden.
- [ ] `Plan/JULES_PROTOCOL.md` §3 "Rebase policy" mandates rebasing all open PRs after every Master merge (L15a).
- [ ] `Plan/000-overview.md` dispatch-prompt template is hardened — explicit branch, explicit `affects:` ceiling, explicit Gate 4 reviewer dispatch.
- [ ] `skills/agentic/orchestrator-discipline/SKILL.md` exists and captures the L14 token-discipline rules (summary_only flags, no full activity dumps in the loop).
- [ ] `python Plan/_lint/check_affects.py Plan/099-jules-orchestration-improvements/spec.md` exits 0 for this spec.
- [ ] `Plan/_templates/skill-template.md` exists and is the canonical empty-skill scaffold matching `Plan/000-overview.md` §2.2 — L1 `type/status/slug/summary/created/updated`, L2 `skill_kind/skill_target_agents/skill_references_skills/skill_references_research/skill_references_prompts/skill_bootstrap_required`, and the five mandatory body sections (`## What`, `## When to use`, `## How to use`, `## References`, `## Compatibility`).
- [ ] `Plan/_lint/check_skill_frontmatter.py` exists and exits non-zero on any SKILL.md found under any path listed in `skill_migration_roots:` whose frontmatter or body sections do not conform to §2.2.
- [ ] §2.2 skill-frontmatter migration: every existing SKILL.md discovered under `skill_migration_roots:` (as of merge time) is rewritten to the §2.2 schema — L1 keys complete (per §2.2 the L1 `type:` value for a skill file is `spec`, matching the canonical L1 schema), L2 `skill_*` namespace complete, the five mandatory body sections present and ordered. Content semantics are preserved; only frontmatter shape and body-section headings move. `python Plan/_lint/check_skill_frontmatter.py` exits 0 on Master after the migration. Before the sweep begins, the executing session expands `affects:` to enumerate every SKILL.md it will rewrite (one path per line) so `check_affects.py` continues to pass.

## Source clones (run first)

None — this spec is meta-work on `the-agency-system` itself. `source-repos:` is `[]`.

## Files

- **Create**:
  - `Plan/_lint/check_affects.py` — walks each spec, parses `affects:`, grep-checks the Approach section for filenames not listed.
  - `Plan/_lint/check_install_consistency.py` — diff plugin-name strings between `README.md` and `.claude-plugin/marketplace.json`.
  - `Plan/_lint/check_skill_frontmatter.py` — walks every SKILL.md found beneath any root listed in this spec's `skill_migration_roots:` frontmatter key, parses frontmatter, asserts L1 + L2 `skill_*` keys present, asserts the five §2.2 body sections present and ordered. Exits 1 on any defect with a per-file report.
  - `Plan/_templates/review-subagent-prompt.md` — canonical Gate-4 review subagent prompt (no template-string leaks per L05).
  - `Plan/_templates/spec-template.md` — empty-spec scaffold with all required sections + L04/L06/L07 stickers.
  - `Plan/_templates/skill-template.md` — empty-skill scaffold matching §2.2: L1 + L2 frontmatter, the five mandatory body sections, and a short authoring checklist embedded as HTML comments.
  - `skills/agentic/orchestrator-discipline/SKILL.md` — orchestrator token discipline (L14).
- **Modify**:
  - `Plan/JULES_PROTOCOL.md` — §3 scratch-file expansion, §3 rebase policy, §5 watcher anti-pattern, §6 escalation, Gate 3 clean-install, Gate 4 review-subagent sub-step, §8 automated review backstop, Appendix tool-gaps.
  - `Plan/000-overview.md` — harden the dispatch-prompt template inline.
  - Every SKILL.md discovered beneath any root listed in `skill_migration_roots:` (frontmatter key above) — frontmatter + body-section migration to §2.2. Content prose is preserved; only frontmatter shape and section headings move. Enumeration step at the start of the migration sweep (Approach §13) discovers the current set via `find` and appends each discovered path to `affects:` in a preparatory commit before any SKILL rewrite lands.
- **Move / Delete**: none.

## Approach

1. **Gate 1 — Confidence.** Confirm `Plan/_lint/` and `Plan/_templates/` do not already exist (`ls Plan/_lint Plan/_templates 2>/dev/null`). Re-read lessons 01–14 to extract one verifiable rule per lesson. Cite the rule→artifact map in the PR Confidence table.
2. **Author the lint scripts first.** `check_affects.py` parses YAML frontmatter of every `Plan/*/spec.md`, extracts `affects:`, and scans the Approach + Files sections for backtick-quoted paths under `servers/`, `Plan/`, `skills/`, `tests/`. Any path mentioned but missing from `affects:` is a P1 lint error. `check_install_consistency.py` reads `README.md` and `.claude-plugin/marketplace.json`, extracts plugin-name occurrences, and exits non-zero on mismatch.
3. **Author the spec template.** `Plan/_templates/spec-template.md` is the 004-shape scaffold with three explicit additions: a `server_py_edit:` frontmatter key (default `append-only`), a `## Schema authority` body section that names which JSON Schema owns each new tool, and a helper-file checklist that the author ticks off before submitting.
4. **Author the review-subagent prompt.** `Plan/_templates/review-subagent-prompt.md` is the verbatim prompt the orchestrator pastes when dispatching the Gate-4 reviewer — no Jinja, no `{spec_id}` placeholders that previously leaked (L05). It includes a "report only verifiable findings" guard and a token cap (≤8 k output).
5. **Patch JULES_PROTOCOL.md §3 + §5 + §6.** §3 redefines "scratch file" to cover PR body drafts (L01) and adds the post-merge rebase policy (L15a). §5 adds the watcher-heartbeat anti-pattern (L15b) and the `agentMessaged-and-wait` ban (L02). §6 lists escalation paths: draft PR with `[BLOCKED:]` label, or `agent_message` once then move on — never block.
6. **Patch JULES_PROTOCOL.md Gate 3 + Gate 4.** Gate 3 now requires `pip install -e . && cd /tmp && python -c '...'` for evidence capture (L03). Gate 4 names the review-subagent dispatch as a hard sub-step and points at `Plan/_templates/review-subagent-prompt.md`.
7. **Add JULES_PROTOCOL.md §8 + Appendix.** §8 "Automated review backstop" names Codex bot as primary and the OSS Codex-CLI fallback as the rate-limit escape hatch (L13 + today). The Appendix "Tool gaps & workarounds" enumerates `jules_stop` (unsupported), `jules_message` (input only, not control plane — L08, L10), and the correct user-facing fallback for each.
8. **Patch `Plan/000-overview.md` dispatch template.** Make the example dispatch prompt name the branch, the `affects:` ceiling, and the Gate-4 reviewer dispatch explicitly. Replace any soft "you should" with hard "you MUST".
9. **Author `skills/agentic/orchestrator-discipline/SKILL.md`.** Captures L14: `summary_only=True` defaults, never paste full `jules_activities` output back into the loop, prefer `jules_session_summary` once spec 101 ships. Frontmatter declares `triggers: ["orchestrator-discipline", "token discipline"]`. Authored against the §2.2 schema from step 13 — this is the first skill written to the new contract.
10. **Gate 2 — TDD.** RED: write a tiny pytest that runs `check_affects.py` against this spec and a hand-crafted broken fixture; assert the broken fixture exits 1 and this spec exits 0. GREEN: implement the script. REFACTOR: pull common YAML-frontmatter parsing into a small helper if both lint scripts share it. **Extended:** a second TDD pair covers `check_skill_frontmatter.py` against a broken-skill fixture and a §2.2-conformant fixture.
11. **Gate 3 — Evidence.** Paste outputs of `python Plan/_lint/check_affects.py Plan/099-jules-orchestration-improvements/spec.md`, `python Plan/_lint/check_install_consistency.py`, `python Plan/_lint/check_skill_frontmatter.py`, `rg '^## ' Plan/JULES_PROTOCOL.md`, and `ls Plan/_templates/ Plan/_lint/ skills/agentic/orchestrator-discipline/` into the PR `## Evidence` block.
12. **Gate 4 — Self-Review + review-subagent dispatch.** Answer the three Self-Review questions. Dispatch the review subagent using the newly-authored prompt template; paste its findings under `## Review`.
13. **Skill-frontmatter migration (the §2.2 sweep).** After steps 2–4 ship the linter + template, enumerate every existing skill file by running `find` against each path listed in this spec's `skill_migration_roots:` frontmatter key (concretely: skills directory and jules-plugin skills directory). The session's first commit in the sweep is a frontmatter-only edit to this spec that appends each discovered SKILL.md path to the `affects:` list (so `check_affects.py` continues to pass before any SKILL is rewritten). Then, for each enumerated file: read the existing frontmatter, lift the trigger-phrase content into the §2.2 `description:` field, populate L1 (`type: spec` per the §2.2 canonical schema, `status: active`, `slug:` set to the containing directory name, `summary:` ≤120 chars, `created:` set to the first-commit date from git log, `updated: 2026-05-18`), populate L2 (`skill_kind:` selected from the 9-value enum per the skill's content, `skill_target_agents:`, `skill_references_skills:` and the other four `skill_references_*`/`skill_bootstrap_required:` keys with sensible defaults — empty arrays / `false` are valid). Rewrite the body to use the five §2.2 section headings (`## What`, `## When to use`, `## How to use`, `## References`, `## Compatibility`), preserving existing prose under the new headings. Do NOT rewrite content, only structure. Commit one skill per commit so the diff is auditable. Run `python Plan/_lint/check_skill_frontmatter.py` after each commit to confirm green-on-green progress. Stop and ask via the draft PR if any skill's content cannot be mapped cleanly to the five sections.

## Acceptance (Gherkin)

```gherkin
# anchor: 099.1
Scenario: The affects-list lint catches missing helper files
  Given a hand-crafted broken fixture spec whose Approach names "_helper.py" but whose affects: list omits it
  When the operator runs "python Plan/_lint/check_affects.py path/to/broken.md"
  Then the process exits with status 1
  And stderr contains the string "_helper.py not in affects:"

# anchor: 099.2
Scenario: README and marketplace plugin-name strings stay in lockstep
  Given README.md and .claude-plugin/marketplace.json both reference the plugin name
  When the operator runs "python Plan/_lint/check_install_consistency.py"
  Then the process exits with status 0
  And no diff is reported on the plugin-name field

# anchor: 099.3
Scenario: JULES_PROTOCOL.md codifies the agentMessaged ban and the rebase policy
  Given the patched protocol file
  When the operator runs "rg -n 'agentMessaged' Plan/JULES_PROTOCOL.md"
  Then the match appears under §5 "Anti-patterns"
  And rg -n 'rebase' Plan/JULES_PROTOCOL.md returns a match under §3

# anchor: 099.4
Scenario: The review-subagent prompt is locked at a stable path
  Given the templates directory has been authored
  When the orchestrator dispatches a Gate-4 reviewer
  Then it reads Plan/_templates/review-subagent-prompt.md verbatim
  And no Jinja placeholders remain in the prompt body

# anchor: 099.5
Scenario: Orchestrator-discipline skill exists and declares token-discipline triggers
  Given skills/agentic/orchestrator-discipline/SKILL.md has been authored
  When the operator greps for "summary_only" in the SKILL.md
  Then at least one match is returned
  And the frontmatter contains a "triggers:" key including "token discipline"

# anchor: 099.6
Scenario: Every SKILL.md on Master conforms to the §2.2 schema after migration
  Given the spec template and skill template and check_skill_frontmatter.py linter have shipped
  And the migration sweep across every root listed in skill_migration_roots has landed
  When the operator runs "python Plan/_lint/check_skill_frontmatter.py"
  Then the process exits with status 0
  And the stdout reports the count of skills checked
  And no skill file appears in the per-file defect list
```

## Out of scope

- Adding new Jules MCP tools (Spec 101 owns `jules_session_summary`, `jules_pr_url`, `jules_quota`).
- Implementing the session-log MCP server (Spec 100).
- The post-merge auto-rebase recipe and hook (Spec 102 owns the implementation; this spec only codifies the policy text).
- Codex-CLI installation automation — §8 of the protocol documents the fallback but the installer is not in scope.
- **Skill content rewriting.** The §2.2 migration sweep preserves content semantics — only frontmatter shape and body-section headings move. If a skill's prose is judged stale or wrong, that is a separate per-skill spec, not Spec 099's scope. The linter (`check_skill_frontmatter.py`) checks structure, never content quality.

## References

- `Plan/JULES_PROTOCOL.md` (gates 1–4, sections being patched)
- `Plan/000-overview.md` (dispatch template being hardened; §2.2 skill schema being enforced)
- `Plan/_lessons-learned/01-scratch-files-on-pr-body-composition.md`
- `Plan/_lessons-learned/02-agent-messaged-and-wait-kills-sessions.md`
- `Plan/_lessons-learned/03-evidence-with-polluted-pythonpath.md`
- `Plan/_lessons-learned/04-affects-list-incompleteness.md`
- `Plan/_lessons-learned/05-independent-review-subagent-is-load-bearing.md`
- `Plan/_lessons-learned/06-spec-vs-schema-drift.md`
- `Plan/_lessons-learned/07-server-py-merge-conflicts-trivial.md`
- `Plan/_lessons-learned/08-jules-mcp-tool-gaps.md`
- `Plan/_lessons-learned/09-watcher-pattern-idiom.md`
- `Plan/_lessons-learned/10-jules-message-can-revive-but-unreliable.md`
- `Plan/_lessons-learned/12-completed-without-pr-or-state-mismatch.md`
- `Plan/_lessons-learned/13-codex-bot-pr-reviews-are-gold.md`
- `Plan/_lessons-learned/14-token-consumption-postmortem.md`
- Spec dependency: `Plan/020-bitwize-deprecation-and-docs/spec.md`
- Spec downstream: `Plan/100-session-log-mcp/spec.md`, `Plan/101-jules-mcp-tool-additions/spec.md`, `Plan/102-pr-rebase-policy/spec.md`
- Session state recording the §2.2 migration scope decision: `Plan/_session-state/2026-05-18-orchestration-handoff.md`
- Skill PR that motivated the migration: `https://github.com/netzkontrast/the-agency-system/pull/64` (three `skills/agentic/*` SKILL.md files authored against the legacy `name + description` format, not §2.2)
