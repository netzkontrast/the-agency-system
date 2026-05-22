---
spec_id: 011
slug: novel-handlers-core
status: done
owner: jules
depends_on: [003, 009, 010]
affects:
  - servers/agency-mcp/src/agency_mcp/handlers/novel/__init__.py
  - servers/agency-mcp/src/agency_mcp/handlers/novel/work_ops.py
  - servers/agency-mcp/src/agency_mcp/handlers/novel/content.py
  - servers/agency-mcp/src/agency_mcp/handlers/novel/core.py
  - servers/agency-mcp/src/agency_mcp/handlers/novel/ideas.py
  - servers/agency-mcp/src/agency_mcp/handlers/novel/status.py
  - servers/agency-mcp/src/agency_mcp/state/indexers/novel_indexer.py
  - servers/agency-mcp/src/agency_mcp/server.py
  - tests/unit/novel/__init__.py
  - tests/unit/novel/test_work_ops.py
  - tests/unit/novel/test_content.py
  - tests/unit/novel/test_indexer.py
estimated_jules_sessions: 2
domain: novel
wave: B
---

> **Jules: read `Plan/JULES_PROTOCOL.md` before starting.** Run gates 1→4 in order:
> (1) Confidence ≥ 0.90, (2) TDD Red-Green-Refactor, (3) Evidence pasted under `## Evidence`, (4) Self-Review answered.
> Branch: `claude/agency-plugin-refactor-PgMQ4`. Only modify paths under `affects:` below.
> Source repos under `source-repos:` are clone-and-read-only into `~/work/vendor/`; never commit them.
> If anything is ambiguous, open a draft PR labelled `[BLOCKED: clarification]` and stop — do not guess.

# Spec 011 — Novel Handlers Core

## Why

The novel domain needs the spirit-isomorphic equivalent of bitwize's `album_ops + content + ideas + status` handlers: CRUD over works, chapters, scenes, characters, and premises, plus a lifecycle for premise-ideas (draft → promote → work). Music maps author↔artist, work↔album, chapter↔track-section, scene↔track-bar; this spec lays the same shape on the novel side so downstream specs (013 structural, 014 gates, 015 skills, 021 prompt-builders) can rely on a stable surface. It also ships the real `novel_indexer` to replace the stub left by spec 003, so `state.json:novel.authors.{slug}.works.{slug}` is populated by walking disk — the search/list handlers in spec 009 depend on it.

## Done When

- [ ] ~25 novel core tools register under names `novel_<verb>_<object>` (e.g. `novel_create_work`, `novel_find_novel`, `novel_list_novels`, `novel_get_work_full`, `novel_create_chapter`, `novel_get_chapter`, `novel_list_chapters`, `novel_create_scene`, `novel_get_scene`, `novel_list_scenes`, `novel_create_character`, `novel_get_character`, `novel_list_characters`, `novel_create_premise_idea`, `novel_list_premise_ideas`, `novel_get_premise_idea`, `novel_update_premise_idea`, `novel_promote_premise`, `novel_update_work_status`, `novel_update_chapter_status`, `novel_update_scene_status`, `novel_rename_work`, `novel_rename_chapter`, `novel_delete_premise_idea`, `novel_rebuild_state`).
- [ ] Every stateful tool accepts `dry_run: bool = False` and returns `{would_apply, diff, warnings}` when set (overview §2.1.7).
- [ ] `novel_create_work(author="ms", genre="darkwave", slug="test", dry_run=False)` instantiates the 11 templates from spec 010 into `novels/ms/works/darkwave/test/` with placeholders substituted; the 7 required subfolders are created.
- [ ] `novel_create_work` is idempotent: a second call with the same args returns `ok=true` with `warnings: ["work already exists"]` and does not overwrite files.
- [ ] `novel_indexer` walks `novels/` and writes `state.json:novel.authors.{author_slug}.works.{work_slug}` entries (one per work, with `genre`, `created`, `status`, `chapter_count`).
- [ ] `novel_rebuild_state` reruns the indexer synchronously and bumps `state.json:novel._indexed_at`.
- [ ] `novel_promote_premise(idea_id=..., author=..., genre=..., slug=...)` consumes the premise idea, calls `novel_create_work`, and sets `state.json:novel.premise_ideas.{id}.status = "promoted"`.
- [ ] Tools are namespace-isolated: nothing under `novel_*` writes outside `novels/` or the `novel` key of `state.json`.
- [ ] `pytest -x tests/unit/novel/` exits 0 with ≥ 90% coverage of the 5 handler modules.
- [ ] `ruff check servers/agency-mcp/src/agency_mcp/handlers/novel/ servers/agency-mcp/src/agency_mcp/state/indexers/novel_indexer.py` exits 0.

## Source clones (run first)

```bash
git clone --depth=1 --branch=v0.91.0 \
  https://github.com/bitwize-music-studio/claude-ai-music-skills.git \
  ~/work/vendor/bitwize-music

git clone --depth=1 --branch=claude/agency-plugin-refactor-PgMQ4 \
  https://github.com/netzkontrast/agency.git \
  ~/work/vendor/agency
```

## Files

- **Create — handlers (6)**:
  - `servers/agency-mcp/src/agency_mcp/handlers/novel/__init__.py` (re-exports `register_novel_core_handlers`)
  - `servers/agency-mcp/src/agency_mcp/handlers/novel/work_ops.py` — `novel_create_work`, `novel_find_novel`, `novel_list_novels`, `novel_get_work_full`, `novel_rename_work`, `novel_rebuild_state`.
  - `servers/agency-mcp/src/agency_mcp/handlers/novel/content.py` — `novel_create_chapter`, `novel_get_chapter`, `novel_list_chapters`, `novel_create_scene`, `novel_get_scene`, `novel_list_scenes`, `novel_rename_chapter`.
  - `servers/agency-mcp/src/agency_mcp/handlers/novel/core.py` — `novel_create_character`, `novel_get_character`, `novel_list_characters` (character CRUD; the "core entities" beside the work itself).
  - `servers/agency-mcp/src/agency_mcp/handlers/novel/ideas.py` — `novel_create_premise_idea`, `novel_list_premise_ideas`, `novel_get_premise_idea`, `novel_update_premise_idea`, `novel_delete_premise_idea`, `novel_promote_premise`.
  - `servers/agency-mcp/src/agency_mcp/handlers/novel/status.py` — `novel_update_work_status`, `novel_update_chapter_status`, `novel_update_scene_status` (with legal-transition table mirroring bitwize's `update_track_field` rules).
- **Create — indexer (1)**:
  - `servers/agency-mcp/src/agency_mcp/state/indexers/novel_indexer.py` — replaces the stub left by spec 003.
- **Create — tests (4)**:
  - `tests/unit/novel/__init__.py`
  - `tests/unit/novel/test_work_ops.py`
  - `tests/unit/novel/test_content.py`
  - `tests/unit/novel/test_indexer.py`
- **Modify**:
  - `servers/agency-mcp/src/agency_mcp/server.py` — add `from .handlers.novel import register_novel_core_handlers; register_novel_core_handlers(mcp)` inside `register_all(mcp)`.

## Approach

1. Read `Plan/000-overview.md` §2.1 (tool naming `<domain>_<verb>_<object>`, `dry_run`, `ToolResult`, StateCache contract).
2. Clone both vendor repos. Read these bitwize handler modules in `~/work/vendor/bitwize-music/servers/bitwize-music-server/handlers/`:
   - `album_ops.py` → maps to `work_ops.py` (artist↔author, album↔work).
   - `content.py` → maps to `content.py` (track↔chapter, bar↔scene).
   - `core.py` → maps to `core.py` (track-character↔character).
   - `ideas.py` → maps to `ideas.py` (album-idea↔premise-idea).
   - `status.py` → maps to `status.py` (track-status↔scene/chapter/work status, with the same legal-transition table shape).
   Cite the bitwize SHA in the PR body. Do **not** copy code; port idioms.
3. Read `~/work/vendor/agency/skills/novel-architect/references/ncp-integration-contract.md` so the file shape `novel_create_work` produces is compatible with what spec 012's NCP compiler expects.
4. Read the spec-010 templates under `templates/novel/` and `Plan/010-novel-on-disk-layout/references/layout-spec.md`. The exhaustive placeholder list and slug rules are authoritative.
5. Build `work_ops.py`:
   - `novel_create_work(author, genre, slug, title=None, logline=None, dry_run=False)`:
     - Normalise slugs per layout-spec.
     - Compute target dir `novels/{author}/works/{genre}/{slug}/`.
     - If exists → idempotent return with `warnings: ["work already exists"]`.
     - If `dry_run=True` → return `{would_apply: true, diff: [list of files to create]}` without touching disk.
     - Else: `mkdir -p` target + 7 subfolders, copy each template from `templates/novel/`, substitute placeholders (`{{author_slug}}`, `{{work_slug}}`, `{{work_title}}`, `{{premise_logline}}`, `{{genre_slug}}`, `{{created}}`), invoke the indexer to refresh state.
   - `novel_find_novel(query)`: fuzzy match against `state.json:novel.authors` and work slugs/titles. Cap 20.
   - `novel_list_novels(author=None)`: cap 20 + cursor (overview §2.1.6).
   - `novel_get_work_full(author, slug, full=False)`: returns work descriptor + counts; `full=true` adds the chapter/scene/character lists.
   - `novel_rename_work(author, old_slug, new_slug, dry_run=False)`: rename dir, update internal refs, refresh state.
   - `novel_rebuild_state()`: thin wrapper that calls the indexer.
6. Build `content.py`:
   - `novel_create_chapter(author, work_slug, chapter_number, title, dry_run=False)`: scaffold `chapters/chXX-title.md` from the chapter template.
   - `novel_create_scene(author, work_slug, chapter_number, scene_number, dry_run=False)`: scaffold `scenes/chXX-sNN.md`.
   - Read/list/rename siblings mirror the music handler shapes.
7. Build `core.py` for character CRUD against `characters/`.
8. Build `ideas.py`:
   - Premise ideas live in `state.json:novel.premise_ideas` (no file representation until promoted).
   - `novel_promote_premise(idea_id, author, genre, slug)` calls `novel_create_work` then sets the idea's `status="promoted"` and `promoted_to="{author}/{genre}/{slug}"`.
9. Build `status.py` with a legal-transition table for `draft → in_progress → review → done → archived` at all three granularities; reject illegal transitions with `{ok: false, warnings: [...]}` — never raise.
10. Build `novel_indexer.py`:
    - Walk `novels/*/works/*/*/work.md`.
    - Parse frontmatter, count chapters and scenes by counting matching files under `chapters/` and `scenes/`.
    - Write `state.json:novel.authors.{author_slug} = {name, works: {work_slug: {genre, created, status, chapter_count, scene_count}}}`.
    - Bump `state.json:novel._indexed_at` to the current ISO timestamp.
    - Acquire the StateCache write lock for the whole walk; single fsync at the end.
11. RED: write the three test files. Use a `tmp_path` fixture that copies `templates/novel/` into the temp `novels/` root.
    - `test_work_ops.py`: dry_run returns diff, real run creates 11 files + 7 subfolders, second run is idempotent, namespace isolation (`state.json:music` untouched).
    - `test_content.py`: chapter/scene scaffolding, list cap 20.
    - `test_indexer.py`: walks fixture, populates state correctly, repeated runs are stable.
12. GREEN: implement modules; wire `register_novel_core_handlers(mcp)` into `server.py:register_all`.
13. REFACTOR: extract a `_substitute_placeholders(text: str, ctx: dict) -> str` helper shared across `work_ops` and `content`; ensure all handlers go through the StateCache lock for writes.
14. Verify `pytest -x tests/unit/novel/`, `ruff check ...`, and a manual `python -c "from agency_mcp.server import create_mcp; m = create_mcp(); print(len([t for t in m._tools.values() if t.name.startswith('novel_')]))"` → expect ≥ 25.

## Acceptance (Gherkin)

```gherkin
# anchor: 011.1
Scenario: novel_create_work scaffolds the 11-template skeleton and indexes it
  Given the templates exist under templates/novel/
  And novels/ is empty
  When the caller invokes novel_create_work(author="ms", genre="darkwave", slug="test", dry_run=False)
  Then novels/ms/works/darkwave/test/ exists
  And the 7 root files (work.md, premise.md, cast.md, dramatica.md, outline.md, ncp.json, README.md) are present
  And the 7 subfolders (chapters/, scenes/, characters/, world/, revisions/, art/, research/) are present
  And no remaining {{...}} placeholder tokens exist in any instantiated file
  And state.json:novel.authors.ms.works.test exists with genre="darkwave" and status="draft"

# anchor: 011.2
Scenario: novel_create_work is idempotent
  Given novels/ms/works/darkwave/test/ already exists from a prior call
  When the caller invokes novel_create_work(author="ms", genre="darkwave", slug="test") again
  Then the result is ok=true
  And warnings contains "work already exists"
  And no file under novels/ms/works/darkwave/test/ was modified (mtimes unchanged)

# anchor: 011.3
Scenario: dry_run reports the diff without touching disk
  Given novels/ is empty
  When the caller invokes novel_create_work(author="ms", genre="darkwave", slug="dryrun", dry_run=True)
  Then the result is ok=true
  And data.would_apply is true
  And data.diff lists the 11 files and 7 subfolders that would be created
  And novels/ms/works/darkwave/dryrun/ does NOT exist on disk
  And state.json:novel.authors does not contain "ms" (unless prior calls added it)

# anchor: 011.4
Scenario: novel_indexer populates state from disk and respects namespace isolation
  Given novels/ms/works/darkwave/test/ and novels/ms/works/darkwave/test2/ exist on disk
  And state.json:music is {"some": "value"}
  When the caller invokes novel_rebuild_state()
  Then state.json:novel.authors.ms.works contains both "test" and "test2"
  And state.json:novel._indexed_at is a recent ISO timestamp
  And state.json:music is still {"some": "value"} (unmodified)

# anchor: 011.5
Scenario: novel_promote_premise turns an idea into a scaffolded work
  Given state.json:novel.premise_ideas.{id} exists with status="draft"
  When the caller invokes novel_promote_premise(idea_id={id}, author="ms", genre="darkwave", slug="promoted")
  Then novels/ms/works/darkwave/promoted/ exists with the full skeleton
  And state.json:novel.premise_ideas.{id}.status is "promoted"
  And state.json:novel.premise_ideas.{id}.promoted_to is "ms/darkwave/promoted"
```

## Out of scope

- Structural ops (signposts, journeys, throughline assignment, NCP-aware chapter validation) — spec 013.
- The 6-gate pre-drafting validator — spec 014.
- NCP compile/validate libraries — spec 012.
- Authoring novel skills (`SKILL.md` files) — spec 015.
- Prompt-builder family (scene, character, world, throughline, bridge) — spec 021.
- Hooks for novel-side PostToolUse validation — spec 017.

## References

- `Plan/JULES_PROTOCOL.md` (gates 1–4)
- `Plan/000-overview.md` §2.1 (tool naming, `dry_run`, response shape, StateCache)
- `Plan/SOURCES.md` (bitwize-music v0.91.0; agency branch `claude/agency-plugin-refactor-PgMQ4`)
- Vendor reference (read-only): `~/work/vendor/bitwize-music/servers/bitwize-music-server/handlers/{album_ops,content,core,ideas,status}.py`
- Vendor reference (read-only): `~/work/vendor/agency/skills/novel-architect/references/ncp-integration-contract.md`
- Local: `templates/novel/` (delivered by spec 010), `Plan/010-novel-on-disk-layout/references/layout-spec.md`
- Local: `servers/agency-mcp/src/agency_mcp/state/cache.py` (delivered by spec 003)
- Local: `servers/agency-mcp/src/agency_mcp/handlers/shared/` (delivered by spec 009 — for the cross-domain `shared_search` to discover novel entities)
