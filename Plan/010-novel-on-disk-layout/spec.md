---
spec_id: 010
slug: novel-on-disk-layout
status: done
owner: jules
depends_on: [002]
affects:
  - templates/novel/work.md
  - templates/novel/chapter.md
  - templates/novel/scene.md
  - templates/novel/outline.md
  - templates/novel/character.md
  - templates/novel/world.md
  - templates/novel/ncp.json
  - templates/novel/premise.md
  - templates/novel/cast.md
  - templates/novel/dramatica.md
  - templates/novel/README.md
  - Plan/010-novel-on-disk-layout/references/layout-spec.md
estimated_jules_sessions: 1
domain: novel
wave: B
---

> **Jules: read `Plan/JULES_PROTOCOL.md` before starting.** Run gates 1→4 in order:
> (1) Confidence ≥ 0.90, (2) TDD Red-Green-Refactor, (3) Evidence pasted under `## Evidence`, (4) Self-Review answered.
> Branch: `claude/agency-plugin-refactor-PgMQ4`. Only modify paths under `affects:` below.
> Source repos under `source-repos:` are clone-and-read-only into `~/work/vendor/`; never commit them.
> If anything is ambiguous, open a draft PR labelled `[BLOCKED: clarification]` and stop — do not guess.

# Spec 010 — Novel On-Disk Layout

## Why

Novel work must mirror the music side's `artists/{name}/albums/{genre}/{album}/` shape so a single mental model serves both domains (overview §1). The novel equivalent is `novels/{author-slug}/works/{genre-slug}/{work-slug}/`, and every new work must be scaffolded from the same set of templates so downstream handlers (spec 011 `novel_create_work`, spec 013 structural ops, spec 014 gates) can rely on a known skeleton — NCP file present, premise present, cast present, dramatica notes present, world bible present, chapters/scenes/revisions/art folders present. Without templates each work would grow ad-hoc, the indexer (spec 003 → 011) would have no canonical files to walk, and the 6-gate (spec 014) would have nothing to validate against. This spec freezes the layout and the templates before any handler writes them.

## Done When

- [ ] All 11 template files exist under `templates/novel/` with placeholder frontmatter (`{{author_slug}}`, `{{work_title}}`, `{{premise_logline}}`, `{{genre_slug}}`, `{{work_slug}}`, `{{created}}`).
- [ ] Each `.md` template parses as valid YAML frontmatter + markdown body (no broken `---` fences).
- [ ] `templates/novel/ncp.json` parses as valid JSON and contains the v1.3.0 top-level keys `storyform`, `players`, `scenes`, `metadata` (placeholders allowed).
- [ ] `Plan/010-novel-on-disk-layout/references/layout-spec.md` exists and documents the `novels/{author-slug}/works/{genre-slug}/{work-slug}/` shape, the full file inventory a work folder must contain, and the slug rules (kebab-case, ASCII, ≤ 64 chars).
- [ ] `python -c "import yaml, pathlib; [yaml.safe_load(p.read_text().split('---')[1]) for p in pathlib.Path('templates/novel').glob('*.md')]"` exits 0.
- [ ] `python -c "import json; json.load(open('templates/novel/ncp.json'))"` exits 0.

## Source clones (run first)

```bash
git clone --depth=1 --branch=claude/agency-plugin-refactor-PgMQ4 \
  https://github.com/netzkontrast/agency.git \
  ~/work/vendor/agency
```

(See `Plan/SOURCES.md` for the canonical entry.)

## Files

- **Create — templates (11)**:
  - `templates/novel/work.md` — top-level work descriptor (title, author, genre, logline, status, target_word_count, created).
  - `templates/novel/chapter.md` — chapter shell (chapter_number, title, pov, status, scene_refs).
  - `templates/novel/scene.md` — scene shell (scene_number, chapter, pov, throughline, beat, status).
  - `templates/novel/outline.md` — work-level outline (act_structure, plot_points, signposts).
  - `templates/novel/character.md` — single-character file (name, role, archetype, big_five, enneagram, ifs_parts).
  - `templates/novel/world.md` — single world-element file (name, type, description, sources).
  - `templates/novel/ncp.json` — NCP v1.3.0 skeleton (will be filled by `ncp.compiler` in spec 012).
  - `templates/novel/premise.md` — premise + logline + central question.
  - `templates/novel/cast.md` — roster of player slots with throughline assignments.
  - `templates/novel/dramatica.md` — storyform notes (resolve, growth, approach, mental_sex, OS/MC/IC/RS classes).
  - `templates/novel/README.md` — the per-work README explaining file layout for downstream agents/humans.
- **Create — reference (1)**:
  - `Plan/010-novel-on-disk-layout/references/layout-spec.md` — the canonical directory-shape doc downstream specs (011, 013, 014, 015) cite.
- **Modify**: none.

## Approach

1. Read `Plan/000-overview.md` §1 (target tree — confirms `novels/` lives at repo root and the per-work layout mirrors `artists/`).
2. Clone agency per SOURCES.md. Read `~/work/vendor/agency/skills/novel-architect/phases/phase0-bootstrap.md` for the existing novel-architect bootstrap conventions, and `~/work/vendor/agency/skills/novel-architect/references/ncp-integration-contract.md` for how NCP files interlock with prose files. Do **not** copy these vendor files into the plugin — cite them by URL + SHA in `layout-spec.md`.
3. Draft `layout-spec.md` first. It must specify:
   - **Slug rules**: kebab-case, ASCII, `[a-z0-9-]+`, ≤ 64 chars; collisions resolved by trailing `-2`, `-3`.
   - **Directory shape**: `novels/{author-slug}/works/{genre-slug}/{work-slug}/` plus required subfolders `chapters/`, `scenes/`, `characters/`, `world/`, `revisions/`, `art/`, `research/`.
   - **Required files per work**: `work.md`, `premise.md`, `cast.md`, `dramatica.md`, `outline.md`, `ncp.json`, `README.md` (the 7 files at the work root) — chapters/scenes/characters/world live under their subfolders.
   - **Placeholder set**: enumerate the `{{...}}` tokens every template uses.
   - **Cite-don't-copy rule**: vendor inspection only; cite agency at the relevant SHA.
4. Author each template. Frontmatter uses `---` fences; placeholders use `{{snake_case}}` and are documented in `layout-spec.md`. Minimum frontmatter on every `.md`:
   ```yaml
   ---
   type: novel.<file_kind>
   author_slug: {{author_slug}}
   work_slug: {{work_slug}}
   created: {{created}}
   status: draft
   ---
   ```
   Bodies stay short — placeholders + section headings only. No prose.
5. Author `ncp.json` as a literal JSON document with the v1.3.0 top-level keys present and `null` / `[]` placeholders. The schema itself is pinned in spec 012; this spec only ships a parseable skeleton.
6. Author `README.md` for the per-work folder — a human-and-agent-facing map of the 7 root files + 7 subfolders, plus a one-line "edit me last" hint.
7. RED-equivalent: the verification commands under **Done When** act as the test surface (templates have no behaviour, so per JULES_PROTOCOL.md §2 Gate 2 ("When NOT to TDD"), this counts as a "scaffold-only change, verified by parser commands"). State this explicitly in the PR body and run the YAML-parse and JSON-parse one-liners as evidence.
8. Verify by running the YAML/JSON parse commands from **Done When** and pasting their output under `## Evidence`.

## Acceptance (Gherkin)

```gherkin
# anchor: 010.1
Scenario: All 11 novel templates exist and parse
  Given the novel templates have been authored under templates/novel/
  When the operator runs the YAML-parse one-liner over every templates/novel/*.md
  Then the command exits with status 0
  And the operator runs the JSON-parse one-liner over templates/novel/ncp.json
  Then the command exits with status 0

# anchor: 010.2
Scenario: layout-spec.md documents the canonical directory shape
  Given Plan/010-novel-on-disk-layout/references/layout-spec.md exists
  When a reader greps for "novels/{author-slug}/works/{genre-slug}/{work-slug}/"
  Then at least one occurrence is found
  And the file lists the 7 required root files of a work folder
  And the file lists the 7 required subfolders of a work folder
  And the file enumerates the {{placeholder}} tokens used across the templates

# anchor: 010.3
Scenario: Templates are instantiable by a downstream handler
  Given the templates exist under templates/novel/
  When a downstream call (spec 011 novel_create_work) loads each template
  And substitutes {{author_slug}}, {{work_slug}}, {{work_title}}, {{premise_logline}}, {{genre_slug}}, {{created}}
  Then the resulting files have no remaining {{...}} tokens
  And each instantiated .md still parses as YAML frontmatter + markdown
  And the instantiated ncp.json still parses as JSON

# anchor: 010.4
Scenario: Slug rule rejects collisions and non-kebab input
  Given layout-spec.md specifies kebab-case ASCII slugs
  When a downstream handler is asked to scaffold a work with slug "My Work!"
  Then the handler is expected (per layout-spec.md) to normalise it to "my-work" or reject the request
```

## Out of scope

- Implementing `novel_create_work` — that is spec 011's job. This spec ships only the templates the handler will copy.
- Authoring the NCP v1.3.0 JSON Schema (spec 012 pins it under `state/schema/ncp.schema.json`).
- Authoring the dramatica ontology files (spec 012 vendors them under `reference/novel/dramatica/`).
- Writing any prose into the templates beyond placeholders and section headings.
- Touching `novels/.gitkeep` (already in place from spec 001).

## References

- `Plan/JULES_PROTOCOL.md` (gates 1–4; §4 vendor-clone rules; §2 Gate 2 "When NOT to TDD" clause)
- `Plan/000-overview.md` §1 (target tree — `novels/{author}/works/{genre}/{slug}/`)
- `Plan/SOURCES.md` (agency repo, branch `claude/agency-plugin-refactor-PgMQ4`)
- Vendor reference (read-only): `~/work/vendor/agency/skills/novel-architect/phases/phase0-bootstrap.md`
- Vendor reference (read-only): `~/work/vendor/agency/skills/novel-architect/references/ncp-integration-contract.md`
