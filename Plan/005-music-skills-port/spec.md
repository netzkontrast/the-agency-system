---
spec_id: 005
slug: music-skills-port
status: ready
owner: jules
depends_on: [002, 004]
affects:
  - skills/music/
  - Plan/005-music-skills-port/references/skill-mapping.md
source-repos:
  - bitwize-music @ v0.91.0
estimated_jules_sessions: 1
domain: music
wave: A
---

> **Jules: read `Plan/JULES_PROTOCOL.md` before starting.** Run gates 1→4 in order:
> (1) Confidence ≥ 0.90, (2) TDD Red-Green-Refactor, (3) Evidence pasted under `## Evidence`, (4) Self-Review answered.
> Branch: `claude/agency-plugin-refactor-PgMQ4`. Only modify paths under `affects:` below.
> Source repos under `source-repos:` are clone-and-read-only into `~/work/vendor/`; never commit them.
> If anything is ambiguous, open a draft PR labelled `[BLOCKED: clarification]` and stop — do not guess.

# Spec 005 — Music Skills Port

## Why

bitwize-music ships 54 skills covering the entire music production pipeline: `lyric-writer`, `lyric-reviewer`, `pronunciation-specialist`, `mastering-engineer`, `mix-engineer`, `album-conceptualizer`, `release-director`, `suno-engineer`, the 9 `researchers-*` skills, and the import / promo / validation skills. These represent thousands of hours of craft codification and pair 1:1 with the music handlers ported in Spec 004. Moving them into `skills/music/` with `/agency-system:music-*` slash names — and rewriting only the `name:` field and the `allowed-tools:` server reference — gives the unified plugin the full bitwize skill catalogue with zero behaviour change. Without this spec, every music slash command in CLAUDE.md still points at the old `/bitwize-music:*` namespace and the new plugin is unusable for music work.

## Done When

- [ ] All 54 skill folders exist under `skills/music/<skill-slug>/` with their `SKILL.md` and any `references/` subdirs copied verbatim from bitwize.
- [ ] Every `SKILL.md` frontmatter `name:` field has the `music-` prefix (e.g. `name: music-lyric-writer`).
- [ ] No `SKILL.md` body or `references/` content has been altered (verified by `diff -r` against vendor source, excluding the renamed frontmatter line).
- [ ] Every `allowed-tools:` entry referencing `bitwize-music-mcp` / `mcp__plugin_bitwize-music_*` has been rewritten to `agency-system-mcp` / `mcp__plugin_agency-system_*`.
- [ ] `claude --plugin-dir . /help` (run from repo root) lists 54 entries matching `/agency-system:music-*`.
- [ ] `Plan/005-music-skills-port/references/skill-mapping.md` documents the old→new slug mapping for all 54 skills.
- [ ] No skill loads with a frontmatter parse error (verified by a smoke YAML-parse loop over every `SKILL.md`).

## Source clones (run first)

```bash
git clone --depth=1 --branch=v0.91.0 \
  https://github.com/bitwize-music-studio/claude-ai-music-skills.git \
  ~/work/vendor/bitwize-music
```

(Reuse the clone from Spec 004 if it is still on disk.)

## Files

- **Create**:
  - `skills/music/<slug>/SKILL.md` × 54 (copied from `~/work/vendor/bitwize-music/skills/<slug>/SKILL.md`).
  - `skills/music/<slug>/references/**` for any skill that ships them (preserve the subtree verbatim).
  - `Plan/005-music-skills-port/references/skill-mapping.md` — table of `old_slug | new_slug | bitwize_path | new_path`.
- **Modify**:
  - Each new `SKILL.md` `name:` field only (`name: <slug>` → `name: music-<slug>`).
  - Each new `SKILL.md` `allowed-tools:` entries that reference the bitwize MCP server name only.
- **Move / Delete**: none. `vendor/bitwize-music/` is read-only.

## Approach

1. **Gate 1 — Confidence.** Verify Spec 002 has shipped `.claude-plugin/plugin.json` with `name: agency-system` and that `skills/music/` exists (Spec 001 scaffold). Verify Spec 004 has registered tools with `mcp__plugin_agency-system_*` names. Cite both checks in the Confidence table.
2. **Clone & enumerate.** Run the clone. `ls ~/work/vendor/bitwize-music/skills/ | wc -l` must return 54. If it returns a different number, open `[BLOCKED: clarification]` with the actual count and stop — do not pick which 54 to port silently.
3. **Build the mapping table first.** Before copying, write `Plan/005-music-skills-port/references/skill-mapping.md` listing all 54 skills with columns `old_slug | new_slug | has_references_dir`. This is the audit trail for Gate 4.
4. **Copy verbatim.** For each entry in the mapping table: `cp -r ~/work/vendor/bitwize-music/skills/<slug>/ skills/music/<slug>/`. Do not flatten, do not rename inside the folder.
5. **Rename the frontmatter `name:` field only.** Use a careful `sed`-equivalent (or Python script) that targets exactly the YAML `name:` line. Example: `name: lyric-writer` → `name: music-lyric-writer`. Do NOT touch `description:`, `model:`, `allowed-tools:` array entries that are not server-name references, or any body content.
6. **Rewrite `allowed-tools` server names.** For each `SKILL.md`, replace `mcp__plugin_bitwize-music_bitwize-music-mcp__<tool>` with `mcp__plugin_agency-system_agency-system-mcp__music_<tool>` (note the `music_` prefix introduced by Spec 004). Tools that are not under the bitwize MCP server (built-in `Read`, `Edit`, `Bash`, `Skill`, etc.) are left untouched.
7. **Verify no body drift.** Run `diff -r --brief ~/work/vendor/bitwize-music/skills/ skills/music/` and inspect the changed files: only the renamed frontmatter line and `allowed-tools` server references may differ. Anything else is a porting bug — revert and redo.
8. **TDD — Gate 2.** This is a config-only change (per JULES_PROTOCOL §2 "When NOT to TDD"). Skip Gate 2 and state explicitly in the PR: `TDD: N/A — config-only skill copy, verified by diff + YAML-parse smoke + /help count`.
9. **Smoke checks for Gate 3.** Run: (a) `find skills/music -name SKILL.md | wc -l` → expects 54. (b) `python -c "import yaml,glob; [yaml.safe_load(open(p).read().split('---')[1]) for p in glob.glob('skills/music/*/SKILL.md')]"` exits 0. (c) `find skills/music -name SKILL.md -exec grep -l '^name: music-' {} \; | wc -l` → 54. (d) `claude --plugin-dir . /help 2>&1 | grep -c '/agency-system:music-'` → 54. Paste all four outputs under `## Evidence`.
10. **Gate 4 — Self-Review.** In particular: confirm `skill-mapping.md` lists 54 rows; flag any skill that had body content modified (should be zero); note any skill whose `allowed-tools` could not be rewritten cleanly.

## Acceptance (Gherkin)

```gherkin
# anchor: 005.1
Scenario: All 54 music skills appear in the agency-system slash menu
  Given the music skills have been copied per this spec
  And the plugin manifest from Spec 002 is in place
  When the operator runs "claude --plugin-dir . /help" from the repo root
  Then stdout contains exactly 54 lines matching the pattern "/agency-system:music-"
  And no line matches the legacy pattern "/bitwize-music:"

# anchor: 005.2
Scenario: Every ported SKILL.md parses as valid YAML frontmatter with music- prefix
  Given the music skills folder has been populated
  When a YAML parser loads every SKILL.md frontmatter block
  Then no ParseError is raised
  And every parsed "name" field starts with the literal prefix "music-"

# anchor: 005.3
Scenario: SKILL.md bodies are byte-identical to vendor source
  Given a diff -r between vendor bitwize skills/ and the new skills/music/
  When the diff is restricted to lines outside the YAML frontmatter
  Then no body-content differences are reported
  And the only frontmatter difference is the name: prefix and allowed-tools server rewrite
```

## Out of scope

- Porting music handlers / MCP tools (Spec 004 — this spec depends on its tool names existing).
- Editing skill body content (no craft revisions in this spec — that work belongs to a future "skills v2" pass).
- Porting novel, jules, agentic, or shared skills (Specs 007, 015, 016, 009).
- Deleting the bitwize-music plugin install or `bitwize-music` references in user-home overrides (Spec 020).
- Updating CLAUDE.md to use the new slash command names (cross-cutting; handled in Spec 020).
- Porting hooks (Spec 017).

## References

- `Plan/JULES_PROTOCOL.md` (gates 1–4, §2 "When NOT to TDD" clause)
- `Plan/000-overview.md` §1 (skills/music/ location), §2.2 (skill best practices — L1/L2 frontmatter), §2.3 (skills auto-namespace to `/agency-system:<name>`)
- `Plan/SOURCES.md` (bitwize-music clone command)
- Spec dependency: `Plan/002-manifest-and-marketplace/spec.md` (plugin.json `name:` field), `Plan/004-music-handlers-port/spec.md` (music_ tool prefix)
- Claude Code Plugins Guide: https://code.claude.com/docs/en/plugins
- Vendor source (read-only): `~/work/vendor/bitwize-music/skills/`
