---
spec_id: 017
slug: hooks-port-and-extend
status: ready
owner: jules
depends_on: [004, 012, 013]
affects:
  - hooks/hooks.json
  - hooks/validate_track.py
  - hooks/validate_chapter.py
  - hooks/check_version_sync.py
  - hooks/install.sh
  - tests/unit/hooks/__init__.py
  - tests/unit/hooks/test_validate_track.py
  - tests/unit/hooks/test_validate_chapter.py
  - tests/unit/hooks/test_check_version_sync.py
  - tests/fixtures/hooks/tracks/valid_track.md
  - tests/fixtures/hooks/tracks/malformed_track.md
  - tests/fixtures/hooks/chapters/valid_chapter.md
  - tests/fixtures/hooks/chapters/malformed_chapter.md
  - tests/fixtures/hooks/state_versions/state_current.json
  - tests/fixtures/hooks/state_versions/state_drifted.json
source-repos:
  - bitwize-music @ v0.91.0
estimated_jules_sessions: 1
domain: cross
wave: C
---

> **Jules: read `Plan/JULES_PROTOCOL.md` before starting.** Run gates 1→4 in order:
> (1) Confidence ≥ 0.90, (2) TDD Red-Green-Refactor, (3) Evidence pasted under `## Evidence`, (4) Self-Review answered.
> Branch: `Master` (default base for fresh specs post-Wave-A; see JULES_PROTOCOL.md §3). Only modify paths under `affects:` below.
> Source repos under `source-repos:` are clone-and-read-only into `~/work/vendor/`; never commit them.
> If anything is ambiguous, open a draft PR labelled `[BLOCKED: clarification]` and stop — do not guess.

# Spec 017 — Hooks Port and Extend

## Why

bitwize-music ships PostToolUse hooks that fire on `Write`/`Edit` of track
files: `validate_track.py` enforces frontmatter shape (status, explicit, key
metadata fields), and `check_version_sync.py` warns when the on-disk
`state.json:_version` drifts from the installed plugin version. The unified
plugin must keep both behaviours for the music side or every track edit risks
silent corruption. Beyond parity, the novel domain (specs 011–015) introduces
chapter files with frontmatter shape and gate-output JSON of comparable
importance — those need a sibling `validate_chapter.py`. Finally,
`check_version_sync.py` must learn two new version axes the unified plugin
introduces: **NCP schema version** (used by spec 012) and **Dramatica
ontology version** (used by spec 013), so a state file produced under an old
schema is flagged loudly rather than silently misinterpreted.

Claude Code currently executes hooks synchronously (overview §2.3); there is
no `async` flag yet. This spec therefore assumes synchronous semantics and
designs the validators to exit fast (< 50 ms on a single-file PostToolUse).

## Done When

- [ ] `hooks/hooks.json` exists at the repo root and declares PostToolUse matchers for `Write|Edit` covering both music track files (`artists/**/tracks/*.md`) and novel chapter files (`novels/**/chapters/*.md`), plus a matcher for state.json drift.
- [ ] `hooks/validate_track.py` is a verbatim port of `vendor/bitwize-music/hooks/validate_track.py` rewritten only for import roots — running it against `tests/fixtures/hooks/tracks/valid_track.md` exits 0; against `tests/fixtures/hooks/tracks/malformed_track.md` exits non-zero.
- [ ] `hooks/validate_chapter.py` exists and validates novel-chapter frontmatter (`status`, `chapter_number`, `pov`, `scene_ids`, `ncp_link`) — running it against `tests/fixtures/hooks/chapters/valid_chapter.md` exits 0; against `tests/fixtures/hooks/chapters/malformed_chapter.md` exits non-zero with stderr naming the missing/invalid field.
- [ ] `hooks/check_version_sync.py` is ported from bitwize and extended to also compare two new keys: `state.json:_versions.ncp` against the installed `lib/ncp/__init__.py:NCP_SCHEMA_VERSION`, and `state.json:_versions.dramatica` against `lib/dramatica/__init__.py:DRAMATICA_ONTOLOGY_VERSION`. Drift on any of plugin/NCP/Dramatica exits non-zero with a structured `{drift_kind, expected, actual}` JSON message on stderr.
- [ ] `hooks/install.sh` is ported from bitwize, rewritten to install into `~/.claude/hooks/agency-system/` (not `~/.claude/hooks/bitwize-music/`).
- [ ] `pytest -x tests/unit/hooks/` exits 0.
- [ ] Every validator script's first line is `#!/usr/bin/env python3` and the file is `chmod +x`.
- [ ] No reference to `bitwize-music`, `~/.bitwize-music/`, or `BITWIZE_*` env vars remains in `hooks/` (verified by `rg`).

## Source clones (run first)

```bash
git clone --depth=1 --branch=v0.91.0 \
  https://github.com/bitwize-music-studio/claude-ai-music-skills.git \
  ~/work/vendor/bitwize-music
```

`ls ~/work/vendor/bitwize-music/hooks/` should list at minimum `hooks.json`,
`validate_track.py`, `check_version_sync.py`, `install.sh`. If a file is
missing the spec is mis-keyed against the vendor tree — open
`[BLOCKED: clarification]`.

## Files

- **Create**:
  - `hooks/hooks.json` — PostToolUse matchers for music tracks, novel chapters, and state.json drift.
  - `hooks/validate_track.py` — ported from bitwize, import roots rewritten.
  - `hooks/validate_chapter.py` — NEW, mirrors `validate_track.py` shape.
  - `hooks/check_version_sync.py` — ported and extended for NCP + Dramatica versions.
  - `hooks/install.sh` — ported, target path rewritten.
  - 6 test fixture files under `tests/fixtures/hooks/` (2 tracks, 2 chapters, 2 state-version JSONs).
  - `tests/unit/hooks/__init__.py` + 3 test modules.
- **Modify**: none. This spec is hook-local.
- **Move / Delete**: none. Vendor sources stay in `~/work/vendor/`.

## Approach

1. **Gate 1 — Confidence.** Read `Plan/000-overview.md` §2.3 (hooks are synchronous in current Claude Code; `.json` matcher syntax). Read `https://code.claude.com/docs/en/plugins-reference` for the `hooks.json` schema (PostToolUse matcher events, exit-code semantics). Confirm spec 004 has shipped track frontmatter shape (`status`, `explicit`, key metadata fields) and spec 013 has shipped chapter frontmatter shape (`status`, `chapter_number`, `pov`, `scene_ids`, `ncp_link`). Cite both spec paths plus the vendor file listing in the PR `## Confidence` table.
2. **Clone bitwize.** Run the clone command. Read `vendor/bitwize-music/hooks/hooks.json` and the three Python files end-to-end; note every import root that must be rewritten.
3. **Port `validate_track.py` verbatim.** Copy the file. Rewrite imports: `from bitwize_music.*` → `from agency_mcp.*` only if any exist (vendor file is mostly stdlib). Keep the frontmatter validation rules identical; if the script reads `~/.bitwize-music/config.yaml`, rewrite to `~/.agency-system/config.yaml`. Keep exit-code semantics: 0 = pass, non-zero = block + stderr message.
4. **Author `validate_chapter.py` as a sibling.** Same skeleton as `validate_track.py`: parse YAML frontmatter via `python-frontmatter` (already in deps per spec 011), assert presence of `status`, `chapter_number` (positive int), `pov` (non-empty string), `scene_ids` (list of strings), `ncp_link` (path-shaped string). On any missing/invalid field, exit 1 with `json.dumps({"field": <name>, "reason": <msg>}, file=sys.stderr)`. On pass, exit 0 silently.
5. **Port and extend `check_version_sync.py`.** Original compares `state.json:_version` against the installed plugin version (from `.claude-plugin/plugin.json`). Extend with two extra checks: `state.json.get("_versions", {}).get("ncp")` vs `lib/ncp/__init__.py:NCP_SCHEMA_VERSION` and `state.json.get("_versions", {}).get("dramatica")` vs `lib/dramatica/__init__.py:DRAMATICA_ONTOLOGY_VERSION`. On any drift, exit 1 with a single-line JSON `{"drift_kind": "plugin"|"ncp"|"dramatica", "expected": "...", "actual": "..."}` to stderr. If multiple axes drift, emit one JSON line per axis.
6. **Author `hooks.json`.** Use the Claude Code PostToolUse schema:
   ```json
   {
     "hooks": {
       "PostToolUse": [
         {"matcher": {"tool": "Write|Edit", "path_glob": "artists/**/tracks/*.md"}, "command": "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/validate_track.py"},
         {"matcher": {"tool": "Write|Edit", "path_glob": "novels/**/chapters/*.md"}, "command": "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/validate_chapter.py"},
         {"matcher": {"tool": "Write|Edit", "path_glob": "**/state.json"}, "command": "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/check_version_sync.py"}
       ]
     }
   }
   ```
   Verify against the Plugins Reference at the URL above; if the schema differs, conform to whatever the reference specifies (this is reference-led, not opinion-led).
7. **Port `install.sh`.** Target path becomes `~/.claude/hooks/agency-system/`. Keep idempotent `mkdir -p` + `cp` semantics; do not invent a separate uninstall flow (out of scope).
8. **TDD — Gate 2.** RED: write `test_validate_track.py` (valid fixture → exit 0; malformed fixture → non-zero + stderr names field), `test_validate_chapter.py` (same shape), `test_check_version_sync.py` (current state → exit 0; drifted state → exit 1 with structured JSON identifying drift_kind). Watch them fail. GREEN: implement validators. REFACTOR: extract the shared frontmatter-load + field-required helper into `hooks/_lib.py` ONLY if it does not introduce a new top-level path outside `affects:` — if it would, keep the duplication.
9. **Gate 3 — Evidence.** Paste in PR body: `pytest -x tests/unit/hooks/` last 20 lines, `python3 hooks/validate_chapter.py tests/fixtures/hooks/chapters/malformed_chapter.md; echo exit=$?` (must print exit=1 plus a stderr JSON), `python3 hooks/check_version_sync.py tests/fixtures/hooks/state_versions/state_drifted.json; echo exit=$?` (must print exit=1 with at least one drift JSON), `rg 'bitwize-music|~/.bitwize-music/|BITWIZE_' hooks/` (must be empty).
10. **Gate 4 — Self-Review.** Answer the three questions. Specifically flag any deviation from `hooks.json` schema discovered against the Plugins Reference (e.g. if `path_glob` is actually `paths` or another key) and any field the chapter validator does *not* check that spec 013's frontmatter contract requires (with rationale for deferral).

## Acceptance (Gherkin)

```gherkin
# anchor: 017.1
Scenario: validate_track exits zero on a well-formed track and non-zero on a malformed track
  Given the bitwize-music hooks have been ported into hooks/
  When the operator runs `python3 hooks/validate_track.py tests/fixtures/hooks/tracks/valid_track.md`
  Then the exit code is 0
  And stderr is empty
  When the operator runs `python3 hooks/validate_track.py tests/fixtures/hooks/tracks/malformed_track.md`
  Then the exit code is non-zero
  And stderr is non-empty and names the offending field

# anchor: 017.2
Scenario: validate_chapter blocks a chapter file with malformed frontmatter
  Given hooks/validate_chapter.py is installed
  And tests/fixtures/hooks/chapters/malformed_chapter.md has a missing or invalid `pov` field
  When PostToolUse fires `python3 hooks/validate_chapter.py <fixture-path>`
  Then the exit code is non-zero
  And stderr contains a JSON object whose `field` key equals "pov"

# anchor: 017.3
Scenario: check_version_sync flags drift on NCP or Dramatica versions, not only plugin version
  Given hooks/check_version_sync.py has been extended per this spec
  And tests/fixtures/hooks/state_versions/state_drifted.json declares ncp version "1.2.0" while the installed lib reports "1.3.0"
  When the operator runs `python3 hooks/check_version_sync.py tests/fixtures/hooks/state_versions/state_drifted.json`
  Then the exit code is non-zero
  And stderr contains a JSON line with `drift_kind` equal to "ncp", `expected` equal to "1.3.0", `actual` equal to "1.2.0"

# anchor: 017.4
Scenario: hooks.json declares PostToolUse matchers for both music tracks and novel chapters
  Given hooks/hooks.json exists at the repo root
  When the operator parses it as JSON
  Then the PostToolUse list contains at least one matcher whose `path_glob` (or schema-equivalent key) matches `artists/**/tracks/*.md`
  And the PostToolUse list contains at least one matcher whose `path_glob` matches `novels/**/chapters/*.md`
  And the PostToolUse list contains at least one matcher whose `path_glob` matches `**/state.json`
```

## Out of scope

- PreToolUse or Stop hooks — only PostToolUse for now (matches bitwize precedent).
- Asynchronous hook execution (not supported by Claude Code as of overview §2.3).
- Inventing new validation rules for tracks beyond what bitwize already enforces.
- NCP / Dramatica version *bump* tooling — this spec only detects drift; the bump remains a manual `lib/{ncp,dramatica}/__init__.py` edit.
- Hook uninstall flow — `install.sh` is a one-way install; the user can `rm -r ~/.claude/hooks/agency-system/` manually.
- Migrating the state file itself when drift is detected (Spec 019 owns migration).

## References

- `Plan/JULES_PROTOCOL.md` (gates 1–4, §4 source-repo discipline)
- `Plan/000-overview.md` §2.3 (hooks synchronous; `hooks.json` location at repo root; `${CLAUDE_PLUGIN_ROOT}` path convention)
- `Plan/SOURCES.md` (bitwize-music v0.91.0 clone command)
- Claude Code Plugins Reference — hooks schema: https://code.claude.com/docs/en/plugins-reference
- Spec dependency: `Plan/004-music-handlers-port/spec.md` (track frontmatter contract)
- Spec dependency: `Plan/013-novel-handlers-structural/spec.md` (chapter frontmatter contract)
- Forward link: `Plan/019-state-migration-from-bitwize/spec.md` (migration acts on the drift this hook detects)
- Vendor source (read-only): `~/work/vendor/bitwize-music/hooks/{validate_track.py,check_version_sync.py,install.sh,hooks.json}`
