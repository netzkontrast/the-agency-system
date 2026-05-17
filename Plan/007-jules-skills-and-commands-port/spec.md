---
spec_id: 007
slug: jules-skills-and-commands-port
status: ready
owner: jules
depends_on: [002, 006]
affects:
  - skills/jules/
  - commands/jules-create.md
  - commands/jules-list.md
  - commands/jules-watch.md
  - commands/jules-bulk.md
  - commands/jules-patch-summary.md
  - tools/jules/researcher/
  - bin/jules-bulk
source_repos: []
estimated_jules_sessions: 1
domain: jules
wave: A
---

> **Jules: read `Plan/JULES_PROTOCOL.md` before starting.** Run gates 1→4 in order:
> (1) Confidence ≥ 0.90, (2) TDD Red-Green-Refactor, (3) Evidence pasted under `## Evidence`, (4) Self-Review answered.
> Branch: `claude/agency-plugin-refactor-PgMQ4`. Only modify paths under `affects:` below.
> Source repos under `source-repos:` are clone-and-read-only into `~/work/vendor/`; never commit them.
> If anything is ambiguous, open a draft PR labelled `[BLOCKED: clarification]` and stop — do not guess.

# Spec 007 — Jules Skills and Commands Port

## Why

`jules-plugin/` ships a `skills/jules/` skill (`SKILL.md` + `references/`) that codifies the Jules orchestration workflow (gate discipline, watcher patterns, bulk dispatch), plus a `tools/researcher/` helper used during research-prompt runs and a `bin/jules-bulk` CLI for fan-out. With Spec 006 having ported the MCP tools into the unified server, users still cannot invoke the workflow via `/agency-system:jules-*` slash commands — those entry points live in this spec. Moving the skill and the helper under the unified namespace, plus authoring thin command facades in `commands/jules-*.md`, gives the human one slash menu instead of two and completes Wave A for the jules domain. Without this spec, Spec 020 cannot delete `jules-plugin/` because the skill and CLI still have no home.

## Done When

- [ ] `skills/jules/` exists with the `SKILL.md` (and its `references/` subtree) copied verbatim from `jules-plugin/skills/jules/`, with the frontmatter `name:` field rewritten to a `jules-`-prefixed slug if the source slug does not already carry one (e.g. `name: jules-orchestrator`).
- [ ] At least 5 thin facade commands exist under `commands/jules-*.md` (one per primary surface: create, list, watch, bulk, patch-summary). Each facade is ≤30 lines and delegates by calling the corresponding skill or MCP tool.
- [ ] `tools/jules/researcher/` exists with the helper subtree copied from `jules-plugin/tools/researcher/`; relative imports inside the helper are rewritten if needed.
- [ ] `bin/jules-bulk` is executable (`chmod +x`) and `bin/jules-bulk --help` exits 0 with usage output.
- [ ] `claude --plugin-dir . /help` lists every facade command under the `/agency-system:jules-*` prefix.
- [ ] `jules-plugin/skills/` and `jules-plugin/tools/researcher/` remain untouched on disk (`git status` shows no changes there).

## Source clones (run first)

None. In-repo move. Local references:
- `jules-plugin/skills/jules/SKILL.md` and `jules-plugin/skills/jules/references/`.
- `jules-plugin/tools/researcher/` (helper tree).
- `jules-plugin/bin/jules-bulk` if present, else `jules-plugin/scripts/jules-bulk`.

## Files

- **Create**:
  - `skills/jules/SKILL.md` (copy of `jules-plugin/skills/jules/SKILL.md`, frontmatter `name:` rewritten).
  - `skills/jules/references/**` (copied verbatim from source).
  - `commands/jules-create.md` — facade that invokes the jules skill with intent "create a new session".
  - `commands/jules-list.md` — facade that calls `mcp__plugin_agency-system_agency-system-mcp__jules_list`.
  - `commands/jules-watch.md` — facade for `jules_start_watcher` + `jules_watcher_status` loop.
  - `commands/jules-bulk.md` — facade pointing at `bin/jules-bulk`.
  - `commands/jules-patch-summary.md` — facade for `jules_patch_summary`.
  - `tools/jules/researcher/**` (copy of source subtree).
  - `bin/jules-bulk` (copy of source CLI, executable bit set).
- **Modify**: none in this spec (CLAUDE.md slash-name updates deferred to Spec 020).
- **Move / Delete**: none. `jules-plugin/skills/` and `jules-plugin/tools/researcher/` stay; deletion in Spec 020.

## Approach

1. **Gate 1 — Confidence.** Verify Spec 002 has shipped the manifest (so `/agency-system:` is the namespace). Verify Spec 006 has registered `jules_*` tools (`python -c "from agency_mcp.server import create_mcp; m=create_mcp(); print([t for t in m._tools if t.startswith('jules_')])"`). Verify the source skill+helper exist (`ls jules-plugin/skills/jules/ jules-plugin/tools/researcher/`). Cite each in the Confidence table.
2. **Copy the skill verbatim.** `cp -r jules-plugin/skills/jules/ skills/jules/`. Inspect the frontmatter `name:` field. If it is already `jules-orchestrator` or any `jules-`-prefixed slug, leave it. Otherwise prefix it: `name: orchestrator` → `name: jules-orchestrator`. Touch only the `name:` line.
3. **Rewrite `allowed-tools` references in the skill.** If `SKILL.md` lists `mcp__plugin_jules-orchestrator_jules-mcp__<tool>` entries, rewrite them to `mcp__plugin_agency-system_agency-system-mcp__jules_<tool>` (note the `jules_` prefix introduced by Spec 006). Built-in tool entries stay untouched.
4. **Copy the researcher helper.** `cp -r jules-plugin/tools/researcher/ tools/jules/researcher/`. If the helper has Python imports `from jules_orchestrator.*`, rewrite them to `from agency_mcp.handlers.jules.*` or whatever the helper actually needs. If it has no internal imports, no rewrite is needed.
5. **Author the 5 facade commands.** Each `commands/jules-<verb>.md` is a thin Markdown file with frontmatter `description:`, `argument-hint:`, and a body that either delegates to the `jules-orchestrator` skill via `Skill` tool or to a specific MCP tool. Keep each ≤30 lines. Example body for `jules-list.md`: a 2-line instruction "List active Jules sessions via `mcp__plugin_agency-system_agency-system-mcp__jules_list`. Return the result table verbatim."
6. **Copy the CLI.** `cp jules-plugin/bin/jules-bulk bin/jules-bulk` (or whichever path source uses). `chmod +x bin/jules-bulk`. If the CLI shebangs `python` and imports from `jules_orchestrator`, rewrite the import path; otherwise leave it.
7. **TDD — Gate 2.** This is mostly a config + file-move change. The one behavioural piece (CLI) gets a smoke test: `tests/smoke/test_jules_bulk_cli.py::test_help_exits_zero` invokes `bin/jules-bulk --help` via `subprocess.run` and asserts `returncode == 0`. RED first, then make it pass by copying the CLI. For the skill copy / command facades, state `TDD: N/A — config-only, verified by /help count + diff -r` per JULES_PROTOCOL §2.
8. **Smoke for Gate 3.** Run: (a) `bin/jules-bulk --help; echo exit=$?` — expects `exit=0`. (b) `claude --plugin-dir . /help | grep -c '^/agency-system:jules-'` — expects ≥5. (c) `find skills/jules -name SKILL.md | xargs grep -l '^name: jules-'` — expects 1 match. (d) `git status jules-plugin/` showing no changes inside `jules-plugin/skills/` or `jules-plugin/tools/researcher/`.
9. **Gate 4 — Self-Review.** Confirm CLAUDE.md updates were intentionally NOT done (Spec 020 owns that). Confirm the source files in `jules-plugin/` are still in place. Note any facade that ended up >30 lines and explain why.

## Acceptance (Gherkin)

```gherkin
# anchor: 007.1
Scenario: The jules skill appears under the unified slash namespace
  Given the jules skill has been moved per this spec
  And the plugin manifest from Spec 002 is in place
  When the operator runs "claude --plugin-dir . /help" from the repo root
  Then stdout contains a line beginning with "/agency-system:jules-"
  And the SKILL.md frontmatter "name:" field starts with "jules-"

# anchor: 007.2
Scenario: jules-bulk CLI is executable and prints usage
  Given bin/jules-bulk has been copied with the executable bit set
  When the operator runs "bin/jules-bulk --help"
  Then the process exits with status 0
  And stdout contains the literal substring "usage:"

# anchor: 007.3
Scenario: At least five facade commands are present under /agency-system:jules-*
  Given the facade command files have been authored per this spec
  When the operator counts "commands/jules-*.md" entries
  Then the count is ≥ 5
  And each file is ≤ 30 lines (excluding the YAML frontmatter block)
```

## Out of scope

- Porting the jules MCP tools (Spec 006 — this spec depends on those tool names).
- Deleting `jules-plugin/skills/`, `jules-plugin/tools/researcher/`, or `jules-plugin/bin/` (Spec 020).
- Rewriting CLAUDE.md `/jules-orchestrator:*` references to the new slash names (Spec 020).
- Modifying the body content of `SKILL.md` (no craft revisions in this spec).
- Authoring agentic, novel, music skills or commands (Specs 005, 015, 016).

## References

- `Plan/JULES_PROTOCOL.md` (gates 1–4, §2 "When NOT to TDD")
- `Plan/000-overview.md` §1 (skills/jules/, commands/, tools/, bin/ locations), §2.3 (auto-namespace)
- Spec dependencies: `Plan/002-manifest-and-marketplace/spec.md`, `Plan/006-jules-handlers-port/spec.md`
- Spec downstream: `Plan/020-bitwize-deprecation-and-docs/spec.md` (jules-plugin deletion)
- Local references: `jules-plugin/skills/jules/`, `jules-plugin/tools/researcher/`, `jules-plugin/bin/jules-bulk`
- Claude Code Plugins Guide (commands section): https://code.claude.com/docs/en/plugins
