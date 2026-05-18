---
spec_id: 132
slug: skill-tool-hooks
status: draft
owner: jules
depends_on: [017]
affects:
  - hooks/hooks.json
  - hooks/skill_pretooluse.py
  - hooks/skill_posttooluse.py
  - hooks/_skill_hook_common.py
  - tests/unit/hooks/__init__.py
  - tests/unit/hooks/test_skill_pretooluse.py
  - tests/unit/hooks/test_skill_posttooluse.py
  - tests/fixtures/hooks/skill_events/pretooluse_known_skill.json
  - tests/fixtures/hooks/skill_events/pretooluse_unknown_skill.json
  - tests/fixtures/hooks/skill_events/pretooluse_completion_verb.json
  - tests/fixtures/hooks/skill_events/posttooluse_known_skill.json
  - Plan/132-skill-tool-hooks/references/agency-hook-reference.md
source-repos:
  - agency @ origin/main
estimated_jules_sessions: 1
domain: cross
wave: C
---

> **Jules: read `Plan/JULES_PROTOCOL.md` before starting.** Run gates 1→4 in order:
> (1) Confidence ≥ 0.90, (2) TDD Red-Green-Refactor, (3) Evidence pasted under `## Evidence`, (4) Self-Review answered.
> Branch: `Master` (default base for fresh specs post-Wave-A; see JULES_PROTOCOL.md §3). Only modify paths under `affects:` below.
> Source repos under `source-repos:` are clone-and-read-only into `~/work/vendor/`; never commit them.
> If anything is ambiguous, open a draft PR labelled `[BLOCKED: clarification]` and stop — do not guess.

# Spec 132 — Skill-Tool Hooks (PreToolUse + PostToolUse on `Skill|Agent` matcher)

## Why

The `agency-system` plugin will ship ~140 skills once Specs 005, 007, 015, 016 land. Today there is **no mechanical guard between a `Skill` tool invocation and the skill body actually existing on disk** — a typo in the slash command (`/agency-system:music-lyric-wrier`), a stale skill reference from another skill's `skill_references_skills` list, or an LLM hallucinated slug all silently succeed-then-fail, burning a tool round-trip and an unbounded amount of model retry effort. Spec 017 ports the music/novel **artefact** validators (`validate_track.py`, `validate_chapter.py`) on the `Write|Edit` matcher, but it deliberately leaves the `Skill|Agent` matcher untouched.

The companion agency repo solved this in [ADR-0011 §D.7](https://github.com/netzkontrast/agency) + Task 094 ST-3 (`tools/hooks/_pre_tool_use.py`). The contract: a single hook on the `Skill|Agent` matcher does three things at once — (1) **manifest verification** (refuse `Skill` invocations whose slug has no `skills/<slug>/SKILL.md` backing — exit 2), (2) **completion-claim gating** (when `tool_input.prompt` contains "done"/"complete"/"ready"/"finished", emit `additionalContext` routing through a verification skill, advisory), (3) **telemetry** (append one line per invocation to the active spec's `skill-invocation-log.md` — the foundation for Spec 118's per-skill quality-score signal). A companion `PostToolUse` hook reads the just-completed skill's `skill_references_skills` and emits a forward-chain suggestion (`additionalContext` with the first three forward targets).

This spec ports the pattern. It is the **single mechanical guard** that turns the plugin's skill index from "advisory documentation" into "an enforced contract": invoking a skill that does not exist becomes a hard error, not a silent dead-letter. It also gives Spec 099's `orchestrator-discipline` skill and Spec 118's quality-score signals a real data source — the per-spec `skill-invocation-log.md` — without adding a new MCP tool or a long-lived process. Without this spec, every downstream lesson about "Jules invoked the wrong skill and we found out three tool-calls later" repeats indefinitely; the §2.2 schema's `skill_references_skills` list is *runtime-unverified* even though the linter resolves it at commit time.

## Done When

- [ ] `hooks/hooks.json` declares **two new matchers** alongside the Spec 017 `Write|Edit` matcher: `PreToolUse` with `matcher: "Skill|Agent"` pointing at `hooks/skill_pretooluse.py`, and `PostToolUse` with `matcher: "Skill|Agent"` pointing at `hooks/skill_posttooluse.py`. JSON validates against the Anthropic hook schema at `https://code.claude.com/docs/en/hooks`.
- [ ] `hooks/skill_pretooluse.py` is executable (`chmod +x`), reads the hook event from stdin, and implements **three behaviours**:
  1. **Manifest verification** — when `tool_name == "Skill"`, extract `tool_input.skill`; if the slug does NOT correspond to a `skills/**/SKILL.md` file under the repo root, write a structured error to stderr (`PreToolUse: skill slug '<slug>' has no skills/**/SKILL.md backing — refusing invocation`) and exit `2` (Anthropic hook contract: exit 2 blocks the tool call).
  2. **Completion-claim gating** — when `tool_input.prompt` contains any of `done`, `complete`, `ready`, `finished` (case-insensitive substring match), emit a JSON `hookSpecificOutput.additionalContext` line on stdout suggesting routing through `verification-before-completion` (a Spec 016 skill). NEVER blocks. Exit 0.
  3. **Telemetry** — append one line `<ISO-8601-UTC> PreToolUse <tool_name> <slug-or-(no-slug)>` to `Plan/<active-spec>/skill-invocation-log.md` (file auto-created with `# Skill Invocation Log` header; `.gitignore`d via existing `Plan/_session-state/.gitignore` pattern). Active-spec resolution: walk the current branch's most recent commit message for a `Plan/NNN-<slug>/` reference; if not found, append to `Plan/_session-state/skill-invocation-log.md` instead. Telemetry MUST NEVER block — wrap in try/except and swallow errors.
- [ ] `hooks/skill_posttooluse.py` is executable, reads the hook event from stdin, and implements **two behaviours**:
  1. **Telemetry** — append one line `<ISO-8601-UTC> PostToolUse <tool_name> <slug> ok|error` to the same log file as the PreToolUse hook (`ok` if `tool_response.error` is absent/falsy, `error` otherwise).
  2. **Forward-chain suggestion** — when `tool_name == "Skill"` AND the just-completed skill's `SKILL.md` declares `skill_references_skills` in its frontmatter, emit a `hookSpecificOutput.additionalContext` line naming the first **three** forward-chain targets, formatted: `"After <slug>, consider: <ref-1>, <ref-2>, <ref-3>"`. Truncate to three. NEVER blocks. Exit 0.
- [ ] `hooks/_skill_hook_common.py` exports the shared helpers: `read_event(stdin) -> dict`, `repo_root() -> Path`, `skill_exists(repo, slug) -> bool` (walks `skills/**/SKILL.md` and returns True iff the slug matches a `name:` frontmatter field OR the parent directory basename), `active_spec_log_path(repo) -> Path`, `emit_additional_context(stdout, text: str) -> None`, `parse_skill_references(skill_md_path: Path) -> list[str]`. Pure functions, no I/O beyond reading SKILL.md and writing the log file. Total ≤200 lines.
- [ ] `pytest -x tests/unit/hooks/test_skill_pretooluse.py tests/unit/hooks/test_skill_posttooluse.py` exits 0. Tests cover, **as parametrized cases over the four JSON fixtures**:
  - `test_unknown_slug_exits_2` — fixture `pretooluse_unknown_skill.json` ⇒ exit 2, stderr contains `'PreToolUse: skill slug'`.
  - `test_known_slug_exits_0` — fixture `pretooluse_known_skill.json` ⇒ exit 0, no stderr.
  - `test_completion_verb_emits_additional_context` — fixture `pretooluse_completion_verb.json` ⇒ exit 0, stdout JSON contains `hookSpecificOutput.additionalContext` with `verification-before-completion`.
  - `test_posttooluse_chain_suggestion` — fixture `posttooluse_known_skill.json` with a skill that declares `skill_references_skills: [a, b, c, d]` ⇒ stdout contains exactly the first three slugs.
  - `test_telemetry_never_blocks` — make the log path unwritable (chmod 000 on tempdir), run any fixture ⇒ exit code is the same as the writable case (no regression).
- [ ] No `bitwize-music` reference remains in `hooks/skill_*.py` (`rg bitwize-music hooks/` returns 0 matches).
- [ ] `hooks/hooks.json` ordering is documented in a file-header comment: `Skill|Agent` PreToolUse runs **before** the Spec 017 `Write|Edit` PreToolUse (if any) and **before** the Spec 114 read-cache hook, so manifest-miss aborts the call before any I/O happens. PostToolUse `Skill|Agent` runs **after** the Spec 118 quality-score hook so the chain suggestion sees the final response shape.

## Source clones (run first)

```bash
git clone --depth=1 https://github.com/netzkontrast/agency.git ~/work/vendor/agency
# Reference files (read-only):
#   ~/work/vendor/agency/tools/hooks/_pre_tool_use.py
#   ~/work/vendor/agency/tools/hooks/_post_tool_use.py
#   ~/work/vendor/agency/tools/hooks/_common.py
#   ~/work/vendor/agency/.claude/settings.json   (the matcher registration shape)
#   ~/work/vendor/agency/tools/check-hooks.py    (governance check that mirrors hooks ↔ settings)
```

The agency repo's `tools/hooks/_pre_tool_use.py` (≈110 lines) is the canonical reference implementation; this spec ports the **shape** (event reading, manifest verification, completion-verb regex, telemetry write) but adapts it for the plugin's `hooks/` directory layout — agency uses `tools/hooks/`, the-agency-system uses `hooks/` (per overview §2.3).

## Files

- **Create**:
  - `hooks/skill_pretooluse.py` — the PreToolUse hook (≤120 lines).
  - `hooks/skill_posttooluse.py` — the PostToolUse hook (≤80 lines).
  - `hooks/_skill_hook_common.py` — shared helpers (≤200 lines).
  - `tests/unit/hooks/test_skill_pretooluse.py` — parametrized fixture-driven tests.
  - `tests/unit/hooks/test_skill_posttooluse.py` — parametrized fixture-driven tests.
  - `tests/fixtures/hooks/skill_events/pretooluse_known_skill.json` — synthetic Skill event with a slug that resolves.
  - `tests/fixtures/hooks/skill_events/pretooluse_unknown_skill.json` — synthetic Skill event with a non-resolving slug.
  - `tests/fixtures/hooks/skill_events/pretooluse_completion_verb.json` — synthetic event whose `tool_input.prompt` contains "done".
  - `tests/fixtures/hooks/skill_events/posttooluse_known_skill.json` — synthetic PostToolUse event for a skill with `skill_references_skills`.
  - `Plan/132-skill-tool-hooks/references/agency-hook-reference.md` — pinned commit SHA + the three agency files this spec mirrors.
- **Modify**:
  - `hooks/hooks.json` — append two new `matchers` entries (PreToolUse + PostToolUse on `Skill|Agent`). Do NOT modify existing Spec 017 `Write|Edit` entries.
- **Move / Delete**: none.

## Approach

1. **Gate 1 — Confidence.** Verify Spec 017 has merged (`ls hooks/hooks.json hooks/validate_track.py` exists). Verify the agency repo is reachable for read-only reference (clone command above). Read `~/work/vendor/agency/tools/hooks/_pre_tool_use.py` end-to-end before writing a single line. Read `Plan/000-overview.md` §2.3 to confirm hooks are synchronous in current Claude Code (no async fan-out needed). Cite: count of existing `Plan/**/SKILL.md` referenced in `Plan/005-music-skills-port/`, the Anthropic hook contract URL, and the agency commit SHA being mirrored.
2. **Read the canonical reference (read-only).** Spend 10 minutes inside `~/work/vendor/agency/tools/hooks/`: study `_common.py` (helpers), `_pre_tool_use.py` (the three responsibilities), `_post_tool_use.py` (chain suggestion). Capture the SHA of `origin/main` into `Plan/132-skill-tool-hooks/references/agency-hook-reference.md` along with one-paragraph adaptation notes per file.
3. **Write `Plan/132-skill-tool-hooks/references/agency-hook-reference.md`.** ≤40 lines, pinning SHA + describing the three adaptation deltas (path layout `tools/hooks/` → `hooks/`; active-spec resolution `Plan/<NNN>-<slug>/` instead of agency's `tasks/<NNN>-<slug>/`; manifest lookup walks `skills/**/SKILL.md` not `skills/<slug>/SKILL.md` — the-agency-system uses subfolders `music/`, `novel/`, etc).
4. **TDD — Gate 2, RED.** Write the four JSON fixtures FIRST. Each fixture mirrors the Anthropic hook event shape (`{hook_event_name, tool_name, tool_input, tool_response?, session_id, transcript_path?}`). Then write the parametrized pytest tests. Run pytest — all five tests must fail (the hook scripts don't exist). Paste the RED output into the PR.
5. **Write `_skill_hook_common.py`.** Pure-function helpers, Python 3.11 stdlib only (no `pyyaml` — write a minimal frontmatter parser that handles the YAML subset SKILL.md actually uses: `key: value` and `key:\n  - item`). Cap at 200 lines. Cover: `read_event(stdin)` (parses stdin JSON with structured error on malformed input), `repo_root()` (walks up from `__file__` until a `.git/` is found), `skill_exists(repo, slug)` (walks `skills/**/SKILL.md` with a 200 ms timeout — the manifest is small enough that no caching is needed for v1; add a TODO comment naming a future Spec X manifest cache as the optimisation path), `active_spec_log_path(repo)` (git-log-message scrape + fallback), `parse_skill_references(skill_md_path)` (returns empty list if the field is absent — never raises).
6. **Write `skill_pretooluse.py`.** Three responsibilities in the order: manifest verification (block first), telemetry append (non-blocking), completion-verb gating (non-blocking emit). Exit 2 only on manifest-miss; exit 0 otherwise. Wrap telemetry in try/except — telemetry failure MUST NEVER cause a manifest-correct invocation to fail.
7. **Write `skill_posttooluse.py`.** Two responsibilities: telemetry append (always), forward-chain suggestion (only when `tool_name == "Skill"` AND the skill exists AND it declares `skill_references_skills`). Exit 0 always (PostToolUse never blocks).
8. **Wire `hooks/hooks.json`.** Append the two new matcher blocks. Add a file-header comment naming the ordering contract (PreToolUse Skill|Agent runs first; PostToolUse Skill|Agent runs after the Spec 118 quality-score hook). If Spec 118 hasn't shipped yet, the file-header comment names the ordering anyway so the next spec can honour it.
9. **Gate 2 — GREEN.** Re-run pytest. All five tests must pass. Paste the GREEN output.
10. **REFACTOR.** Look for duplication between `skill_pretooluse.py` and `skill_posttooluse.py` (likely the telemetry append). Pull into `_skill_hook_common.py` if it shortens without obscuring. Re-run pytest — must stay GREEN.
11. **Gate 3 — Evidence.** Paste: pytest RED, pytest GREEN, `cat hooks/hooks.json | jq .` (showing both old and new matchers), `python3 hooks/skill_pretooluse.py < tests/fixtures/hooks/skill_events/pretooluse_unknown_skill.json; echo $?` (must print `2` and the structured stderr), `python3 hooks/skill_pretooluse.py < tests/fixtures/hooks/skill_events/pretooluse_completion_verb.json | jq .` (must show `hookSpecificOutput.additionalContext`).
12. **Gate 4 — Self-Review.** Answer the 3 standard questions plus this spec-specific one: "What happens if a user invokes a skill by `/agency-system:novel-prose-drafter` BEFORE Spec 015 has authored the skill body? Confirm the PreToolUse hook blocks at exit 2 with the manifest-miss message — that is the **desired** failure mode, not a bug. Then state explicitly: this spec INTENTIONALLY blocks invocations of not-yet-authored skills; that is the contract. The fix is to author the skill, not to relax the hook."

## Acceptance (Gherkin)

```gherkin
# anchor: 132.1
Scenario: PreToolUse blocks invocation of a non-existent skill slug
  Given the file "skills/music/nonexistent-skill/SKILL.md" does not exist
  When Claude Code invokes the Skill tool with tool_input.skill = "nonexistent-skill"
  Then hooks/skill_pretooluse.py exits with code 2
  And the stderr contains "PreToolUse: skill slug 'nonexistent-skill' has no skills/**/SKILL.md backing"
  And no telemetry line is written for this invocation

# anchor: 132.2
Scenario: PreToolUse allows invocation of a known skill slug and writes telemetry
  Given the file "skills/music/lyric-writer/SKILL.md" exists
  When Claude Code invokes the Skill tool with tool_input.skill = "music-lyric-writer"
  Then hooks/skill_pretooluse.py exits with code 0
  And exactly one line is appended to the active-spec invocation log matching "PreToolUse Skill music-lyric-writer"

# anchor: 132.3
Scenario: PreToolUse emits a verification-before-completion suggestion on completion verbs
  Given a Skill invocation whose tool_input.prompt contains the substring "ready"
  When hooks/skill_pretooluse.py processes the event
  Then exit code is 0
  And stdout contains a JSON object with hookSpecificOutput.additionalContext mentioning "verification-before-completion"

# anchor: 132.4
Scenario: PostToolUse emits a forward-chain suggestion from skill_references_skills
  Given a Skill "music-lyric-writer" exists with skill_references_skills [lyric-reviewer, pronunciation-specialist, mastering-engineer, mix-engineer]
  When hooks/skill_posttooluse.py processes a PostToolUse event for that skill
  Then exit code is 0
  And stdout contains hookSpecificOutput.additionalContext with the EXACT first three slugs "lyric-reviewer", "pronunciation-specialist", "mastering-engineer"
  And the fourth slug "mix-engineer" is NOT emitted

# anchor: 132.5
Scenario: Telemetry failure never blocks a manifest-correct invocation
  Given the active-spec invocation log path is unwritable (permission denied)
  And a Skill invocation has a valid slug "music-lyric-writer"
  When hooks/skill_pretooluse.py processes the event
  Then exit code is 0
  And stderr is empty
  And the invocation is NOT blocked by the telemetry failure
```

## Out of scope

- A `SessionStart` skill-manifest builder. Per [ADR-0011 §D.7](https://github.com/netzkontrast/agency/blob/main/decisions/0011-external-skill-corpora-import.md), the-agency-system's bootstrap discipline does not use `SessionStart` hooks; the manifest is computed at-invocation-time by walking `skills/**/SKILL.md`. If the walk becomes slow (>200 ms) under the full skill catalogue, a separate spec (e.g. 134+) ships a JSON manifest cache.
- Reciprocity computation for `skill_references_skills`. Spec 015's `skill_qc_lint.py` already lints `skill_references_skills` at commit time; this spec only consumes the field at runtime.
- A `plugin_help` cheat-sheet generator that lists skills by `skill_kind`. Spec 016's `agentic-handlers` owns `plugin_help`; this spec stays out of that surface.
- Subagent-driven pressure testing of skills. That is Spec 133.
- The `Agent` tool's `subagent_type` slug is treated as best-effort metadata only — agency's `_pre_tool_use.py` notes the same caveat. This spec does not enforce manifest verification on the `Agent` matcher (only on `Skill`).
- A long-running daemon or shared state across invocations. Each hook invocation is a one-shot subprocess; the only persisted state is the append-only `skill-invocation-log.md` file (and that file is `.gitignore`d).

## References

- `Plan/JULES_PROTOCOL.md` §7 (plugin convention block — hooks are synchronous)
- `Plan/000-overview.md` §2.3 (Claude Code plugin specifics — `hooks/hooks.json` is the canonical location)
- `Plan/017-hooks-port-and-extend/spec.md` (the music/novel artefact validators this spec runs alongside)
- `Plan/099-jules-orchestration-improvements/spec.md` (the `orchestrator-discipline` skill this hook's completion-verb gate complements)
- `Plan/118-quality-score-telemetry/spec.md` (downstream consumer of the `skill-invocation-log.md` telemetry signal)
- `Plan/015-novel-skills-catalogue/spec.md` (`skill_qc_lint.py` — commit-time complement to this spec's runtime gate)
- Agency repo: [`tools/hooks/_pre_tool_use.py`](https://github.com/netzkontrast/agency/blob/main/tools/hooks/_pre_tool_use.py) — the canonical reference implementation (≈110 lines)
- Agency repo: [`tools/hooks/_post_tool_use.py`](https://github.com/netzkontrast/agency/blob/main/tools/hooks/_post_tool_use.py) — PostToolUse chain-suggestion pattern
- Agency repo: [`tools/check-hooks.py`](https://github.com/netzkontrast/agency/blob/main/tools/check-hooks.py) — governance check that mirrors hooks ↔ `.claude/settings.json` (Diagnostics `H.1.1`, `H.1.2`, `H.1.3`)
- Agency repo: [`decisions/0011-external-skill-corpora-import.md`](https://github.com/netzkontrast/agency/blob/main/decisions/0011-external-skill-corpora-import.md) §D.7 — the no-`SessionStart`-hook discipline that justifies the at-invocation manifest walk
- [Anthropic — Claude Code Hooks](https://code.claude.com/docs/en/hooks) — `PreToolUse` / `PostToolUse` event contract, exit-code semantics (2 blocks), `hookSpecificOutput.additionalContext` shape
