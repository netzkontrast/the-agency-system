---
spec_id: 020
slug: bitwize-deprecation-and-docs
status: ready
owner: jules
depends_on: [005, 007, 015, 016, 019]
affects:
  - CLAUDE.md
  - README.md
  - CHANGELOG.md
  - docs/domain/music.md
  - docs/domain/novel.md
  - docs/domain/jules.md
  - docs/domain/agentic.md
  - docs/architecture/REFACTOR_DESIGN.md
  - .claude-plugin/plugin.json
  - jules-plugin/
  - tests/smoke/test_doctrine_and_version.py
source_repos:
  - bitwize-music @ v0.91.0
  - agency @ claude/agency-plugin-refactor-PgMQ4
estimated_jules_sessions: 1
domain: cross
wave: C
---

> **Jules: read `Plan/JULES_PROTOCOL.md` before starting.** Run gates 1→4 in order:
> (1) Confidence ≥ 0.90, (2) TDD Red-Green-Refactor, (3) Evidence pasted under `## Evidence`, (4) Self-Review answered.
> Branch: `claude/agency-plugin-refactor-PgMQ4`. Only modify paths under `affects:` below.
> Source repos under `source-repos:` are clone-and-read-only into `~/work/vendor/`; never commit them.
> If anything is ambiguous, open a draft PR labelled `[BLOCKED: clarification]` and stop — do not guess.

# Spec 020 — bitwize Deprecation and Docs

## Why

This is the final cutover. After spec 020 lands, the unified plugin is the
only thing the user needs to install — `jules-plugin/` is gone from the
repo, `bitwize-music` is marked deprecated upstream, and the doctrine /
domain documentation reflects the unified architecture rather than the
three legacy plugins. Without this spec, users see three install paths,
contradictory doctrine in three `CLAUDE.md` files, and a `jules-plugin/`
folder that has been superseded by `handlers/jules/` and `skills/jules/`
since spec 007. With it, version `1.0.0` ships clean: one plugin, one
config, one doctrine, four domain guides, one CHANGELOG.

The four domain guides matter because users entering from different
angles (musician, novelist, agent operator, spec author) need a single
authoritative page that lists the slash skills, the MCP tool catalogue,
and the workflow chain for their domain — without reading the per-spec
files in `Plan/`.

## Done When

- [ ] `CLAUDE.md` at repo root is fully rewritten — no reference to "bitwize-music" or "jules-plugin" as separate installable artefacts; covers all four domains (music, novel, jules, agentic) under one doctrine block.
- [ ] `README.md` at repo root is fully rewritten — install instructions for the unified plugin, marketplace install command, four-paragraph domain overview, link to each `docs/domain/*.md`.
- [ ] `docs/domain/music.md` exists, ≤500 lines, lists every music slash skill (`/agency-system:music-*`), every music MCP tool, the pre-generation + pre-release chains from the legacy bitwize `CLAUDE.md`.
- [ ] `docs/domain/novel.md` exists, ≤500 lines, lists every novel slash skill (`/agency-system:novel-*`), every novel MCP tool, the novel-conceptualizer → draft → 6-gate workflow chain.
- [ ] `docs/domain/jules.md` exists, ≤500 lines, lists every Jules slash skill, every Jules MCP tool, the four-gate protocol summary linking to `Plan/JULES_PROTOCOL.md`.
- [ ] `docs/domain/agentic.md` exists, ≤500 lines, lists every `/agency-system:sc-*`, `/agency-system:superpowers-*`, `/agency-system:spec-skill`, `/agency-system:ralph-skill`, etc., plus the 32-tool agentic catalogue (cross-link to `Plan/016/references/agentic-tool-catalog.md`).
- [ ] `docs/architecture/REFACTOR_DESIGN.md` exists at the new path (moved from root if `REFACTOR_DESIGN.md` was previously at root; otherwise created fresh referencing the `Plan/000-overview.md` architecture diagram).
- [ ] `CHANGELOG.md` exists at root, follows Keep-A-Changelog format, contains a `## [1.0.0] — <UTC-ISO date>` entry summarising the unified-plugin migration (Wave A music+jules parity; Wave B novel ships; Wave C agentic + migration + cutover).
- [ ] `jules-plugin/` folder is removed (`git rm -r jules-plugin/`); `git ls-files jules-plugin/` reports nothing.
- [ ] `.claude-plugin/plugin.json:version` equals `1.0.0`.
- [ ] `pytest -x tests/smoke/test_doctrine_and_version.py` exits 0, asserting: plugin.json version, four domain doc paths exist, CHANGELOG contains the 1.0.0 entry, root `CLAUDE.md` contains the four domain headings, `jules-plugin/` does not exist on disk.
- [ ] No Claude model identifier (e.g. `claude-3-*`, `claude-opus-*`, `claude-sonnet-*`) appears anywhere in `CLAUDE.md` or `README.md` — verified by `rg`.

## Source clones (run first)

```bash
git clone --depth=1 --branch=v0.91.0 \
  https://github.com/bitwize-music-studio/claude-ai-music-skills.git \
  ~/work/vendor/bitwize-music

git clone --depth=1 --branch=claude/agency-plugin-refactor-PgMQ4 \
  https://github.com/netzkontrast/agency.git \
  ~/work/vendor/agency
```

Read `vendor/bitwize-music/CLAUDE.md` and `vendor/bitwize-music/CHANGELOG.md`
for tone, structure, and the existing 0.x changelog entries to seed §1.0.0.
Read `vendor/agency/CLAUDE.md` for the doctrine voice that maps to the
agentic domain section.

## Files

- **Create**:
  - `docs/domain/music.md` — domain guide.
  - `docs/domain/novel.md` — domain guide.
  - `docs/domain/jules.md` — domain guide.
  - `docs/domain/agentic.md` — domain guide.
  - `docs/architecture/REFACTOR_DESIGN.md` — architecture overview (move from root if a `REFACTOR_DESIGN.md` exists there; otherwise create fresh).
  - `CHANGELOG.md` — Keep-A-Changelog format, seeded from `vendor/bitwize-music/CHANGELOG.md` + (if present) `jules-plugin/CHANGELOG.md` before deletion.
  - `tests/smoke/test_doctrine_and_version.py`.
- **Modify**:
  - `CLAUDE.md` — full rewrite (cross-domain doctrine).
  - `README.md` — full rewrite (install + overview).
  - `.claude-plugin/plugin.json` — bump `version` to `"1.0.0"`.
- **Move / Delete**:
  - `git rm -r jules-plugin/` — entire folder.
  - If `REFACTOR_DESIGN.md` exists at repo root, `git mv` it to `docs/architecture/REFACTOR_DESIGN.md`.

## Approach

1. **Gate 1 — Confidence.** Confirm Waves A and B have merged (`git log --oneline Master | head -30` for confirmation; cite hashes in the PR Confidence table). Confirm `jules-plugin/` still exists on disk (`ls jules-plugin/`); if it does not, this spec's deletion step is a no-op — note in PR. Confirm spec 016 has shipped the agentic skills under `skills/agentic/` (`ls skills/agentic/ | wc -l`). Confirm spec 019 has shipped the migrator (`ls state/migrators/bitwize_v091_to_agency.py`). Confirm `.claude-plugin/plugin.json` currently has a sub-1.0.0 version (`jq .version .claude-plugin/plugin.json`). Cite all five commands.
2. **Clone the source plugins.** Run both clones. Read `vendor/bitwize-music/CLAUDE.md` end-to-end. Read `vendor/agency/CLAUDE.md` end-to-end. Note the recurring doctrine threads: "skills before MCP", "tools win over handcrafting", "overrides are cross-project", "chains are recommended not mandatory", "hard gates remain binding when invoked". Plan to preserve these in the unified `CLAUDE.md`.
3. **Author the unified `CLAUDE.md`.** Structure:
   - Top block: working tree purpose (the unified plugin).
   - **MANDATORY: Use subagents for independent or context-heavy work** — port from bitwize verbatim.
   - **MANDATORY: Tools always win over handcrafting** — port verbatim (re-scope to "any domain" not "music").
   - **MANDATORY: Skills before MCP** — port verbatim.
   - **MANDATORY: Overrides are cross-project** — port verbatim, add the four novel overrides from spec 018.
   - **Recommended chains** — one section per domain: music (from bitwize), novel (from spec 015), jules (4-gate protocol summary), agentic (spec-driven loop).
   - **Domain index** — link to `docs/domain/{music,novel,jules,agentic}.md`.
   - **Most important commands & skills** — top ~12 slash commands across all four domains.
   - No Claude model identifier anywhere (this is a project rule).
4. **Author the four domain guides.** Each guide structure:
   - `# /agency-system:<domain>-* — domain guide`.
   - `## What this domain is for` (≤100 words).
   - `## Slash skills` — markdown table `| skill | purpose | links to |`.
   - `## MCP tools` — markdown table `| tool | signature | side-effect |` (deferred-schema tools marked as such).
   - `## Workflow chain` — diagram or numbered list.
   - `## Hard gates` — list of gates that block when invoked (e.g. for music: `pre-generation-check`; for novel: `novel_run_pre_drafting_gates` 6-gate; for jules: confidence ≥ 0.90; for agentic: `spec_validate` BCP-14 errors).
   - `## Where state lives` — `~/.agency-system/cache/state.json:<domain>` path.
   - `## Further reading` — link back to the relevant `Plan/NNN-*/spec.md`.
   - Hard cap each file at 500 lines (`wc -l docs/domain/*.md` in evidence).
5. **Move / author `docs/architecture/REFACTOR_DESIGN.md`.** If a root-level `REFACTOR_DESIGN.md` exists, `git mv` it. Otherwise, author a fresh file that distils `Plan/000-overview.md` §1 (target architecture) + §2 (conventions) + §3 (spec list) into a one-page architecture overview. Reference `Plan/000-overview.md` as the authoritative source.
6. **Author `CHANGELOG.md`.** Keep-A-Changelog format.
   - `## [1.0.0] — <UTC date>` entry: Added (music handlers + skills ported from bitwize-music v0.91.0; novel domain — handlers, skills, dramatica + NCP libs; jules orchestrator handlers + skills; agentic surface — 32 tools across 6 modules + ~60 skills; unified `~/.agency-system/` state; hooks/validate_chapter.py; four novel overrides; bitwize→agency migrator). Changed (single plugin install supersedes three; `~/.bitwize-music/` migrated to `~/.agency-system/`; `jules-plugin/` folder removed). Deprecated (bitwize-music plugin — install the unified plugin instead). Removed (`jules-plugin/` folder; per-plugin CLAUDE.md duplication). Fixed (state-version drift detection extended to NCP + Dramatica per spec 017).
   - Seed earlier entries from `vendor/bitwize-music/CHANGELOG.md` + `jules-plugin/CHANGELOG.md` (before deletion — capture its content under the `## [0.x]` entries first).
7. **Bump version.** Edit `.claude-plugin/plugin.json:version` to `"1.0.0"`. Do not touch other manifest fields.
8. **Delete `jules-plugin/`.** Capture its `CHANGELOG.md` first if present (paste into root CHANGELOG under appropriate 0.x entries). Then `git rm -r jules-plugin/`.
9. **Author the smoke test.** `tests/smoke/test_doctrine_and_version.py` asserts:
   - `json.load(open(".claude-plugin/plugin.json"))["version"] == "1.0.0"`.
   - All four `docs/domain/*.md` exist and are ≤500 lines each.
   - `CHANGELOG.md` contains the literal substring `## [1.0.0]`.
   - `CLAUDE.md` contains each of the four domain section markers (e.g. `### Music`, `### Novel`, `### Jules`, `### Agentic`, or equivalent — the test asserts the four domain words appear under a single doctrine block).
   - `Path("jules-plugin").exists()` is `False`.
   - `rg -q 'claude-(3|opus|sonnet|haiku)-' CLAUDE.md README.md` exits non-zero (no Claude model identifier).
10. **TDD — Gate 2.** Mostly docs/config, so the TDD discipline is the smoke test in step 9. RED: write the smoke test first, watch it fail (current `plugin.json` is sub-1.0.0; current `CLAUDE.md` is bitwize-flavoured; `jules-plugin/` still exists). GREEN: do the rewrites + deletion + version bump. REFACTOR: tighten heading consistency across the four domain guides without changing covered content. Mark the doc/config edits in PR as `TDD: smoke-test-driven (no behavioural change beyond docs+manifest)`.
11. **Gate 3 — Evidence.** Paste in PR body: `pytest -x tests/smoke/test_doctrine_and_version.py` last 20 lines, `jq .version .claude-plugin/plugin.json` showing `"1.0.0"`, `git ls-files jules-plugin/` (must be empty), `wc -l docs/domain/*.md` showing each ≤500, `grep -c '^## \[' CHANGELOG.md` showing ≥2 entries (1.0.0 + at least one 0.x), and `rg -c 'claude-(3|opus|sonnet|haiku)-' CLAUDE.md README.md` (must report 0).
12. **Gate 4 — Self-Review.** Answer the three protocol questions. Specifically flag: anything from bitwize's CLAUDE.md / agency's CLAUDE.md that was intentionally *not* carried over (with rationale); any domain doc that ran tight against the 500-line cap (so the next refactor knows where to split); whether the bitwize marketplace deprecation notice was opened as a separate PR (and if not, why not — e.g. no write access to the marketplace repo). If marketplace access is unavailable, leave a `## Open Questions` block in the PR.

## Acceptance (Gherkin)

```gherkin
# anchor: 020.1
Scenario: Plugin version is 1.0.0 and the legacy jules-plugin folder is gone
  Given Wave A and Wave B specs are merged
  And this spec has been applied
  When the operator runs `jq .version .claude-plugin/plugin.json`
  Then stdout is "1.0.0"
  When the operator runs `git ls-files jules-plugin/`
  Then stdout is empty
  When the operator runs `test -d jules-plugin`
  Then exit code is non-zero

# anchor: 020.2
Scenario: All four domain guides exist within the 500-line budget
  Given this spec has been applied
  When the operator runs `wc -l docs/domain/music.md docs/domain/novel.md docs/domain/jules.md docs/domain/agentic.md`
  Then every reported line count is ≤ 500
  And every file is non-empty

# anchor: 020.3
Scenario: CLAUDE.md covers all four domains under one doctrine block
  Given this spec has been applied
  When the operator parses CLAUDE.md
  Then it contains the heading "## Domains" (or equivalent) followed by named subsections covering music, novel, jules, agentic
  And it contains the substring "skills before MCP"
  And it contains the substring "tools always win"
  And no Claude model identifier of the form claude-(3|opus|sonnet|haiku)-* is present

# anchor: 020.4
Scenario: CHANGELOG records the 1.0.0 unified-plugin entry
  Given this spec has been applied
  When the operator reads CHANGELOG.md
  Then it contains the heading `## [1.0.0]` with a date
  And the 1.0.0 entry lists Added / Changed / Deprecated / Removed sections
  And the Deprecated section names "bitwize-music plugin"
  And the Removed section names "jules-plugin/" folder
```

## Out of scope

- Touching the upstream `bitwize-music` marketplace entry itself if the operator lacks write access — open as a separate PR (or `## Open Questions` block) per step 12; this spec does not require that PR to merge for the 1.0.0 release.
- Authoring tutorials, walkthroughs, or video scripts — README.md links to `docs/domain/*.md` for that.
- Rewriting per-spec `Plan/NNN-*/spec.md` files — those are historical artefacts, not user-facing docs.
- Creating localised (`README.de.md`, etc.) versions — single English README for 1.0.0.
- Renaming the GitHub repo or changing the marketplace install command from `/plugin install agency-system@netzkontrast` — that is plugin-manifest territory, owned by spec 002.
- Removing `~/.bitwize-music/` from the user's machine — the migrator (spec 019) writes only `DEPRECATED.md` in there; deletion is the user's call.

## References

- `Plan/JULES_PROTOCOL.md` (gates 1–4)
- `Plan/000-overview.md` §1 (target tree, including `docs/domain/{music,novel,jules,agentic}.md`), §2 (conventions to mirror in domain docs), §3 (spec list referenced by CHANGELOG 1.0.0)
- `Plan/SOURCES.md` (bitwize-music + agency clone commands)
- Spec dependencies: `Plan/005-music-skills-port/spec.md`, `Plan/007-jules-skills-and-commands-port/spec.md`, `Plan/015-novel-skills-catalogue/spec.md`, `Plan/016-agentic-handlers-and-skills/spec.md`, `Plan/019-state-migration-from-bitwize/spec.md`
- Keep-A-Changelog format: https://keepachangelog.com/en/1.1.0/
- Vendor source (read-only): `~/work/vendor/bitwize-music/{CLAUDE.md,CHANGELOG.md}`, `~/work/vendor/agency/CLAUDE.md`
