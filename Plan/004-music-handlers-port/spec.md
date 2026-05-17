---
spec_id: 004
slug: music-handlers-port
status: ready
owner: jules
depends_on: [003]
affects:
  - servers/agency-mcp/src/agency_mcp/handlers/music/__init__.py
  - servers/agency-mcp/src/agency_mcp/handlers/music/core.py
  - servers/agency-mcp/src/agency_mcp/handlers/music/audio.py
  - servers/agency-mcp/src/agency_mcp/handlers/music/mixing.py
  - servers/agency-mcp/src/agency_mcp/handlers/music/sheet_music.py
  - servers/agency-mcp/src/agency_mcp/handlers/music/video.py
  - servers/agency-mcp/src/agency_mcp/handlers/music/lyrics_analysis.py
  - servers/agency-mcp/src/agency_mcp/handlers/music/text_analysis.py
  - servers/agency-mcp/src/agency_mcp/handlers/music/album_ops.py
  - servers/agency-mcp/src/agency_mcp/handlers/music/gates.py
  - servers/agency-mcp/src/agency_mcp/handlers/music/database.py
  - servers/agency-mcp/src/agency_mcp/handlers/music/ideas.py
  - servers/agency-mcp/src/agency_mcp/handlers/music/streaming.py
  - servers/agency-mcp/src/agency_mcp/handlers/music/content.py
  - servers/agency-mcp/src/agency_mcp/handlers/music/health.py
  - servers/agency-mcp/src/agency_mcp/handlers/music/maintenance.py
  - servers/agency-mcp/src/agency_mcp/handlers/music/promo.py
  - servers/agency-mcp/src/agency_mcp/server.py
  - tests/unit/music/__init__.py
  - tests/unit/music/test_handlers_smoke.py
source_repos:
  - bitwize-music @ v0.91.0
estimated_jules_sessions: 2
domain: music
wave: A
---

> **Jules: read `Plan/JULES_PROTOCOL.md` before starting.** Run gates 1→4 in order:
> (1) Confidence ≥ 0.90, (2) TDD Red-Green-Refactor, (3) Evidence pasted under `## Evidence`, (4) Self-Review answered.
> Branch: `claude/agency-plugin-refactor-PgMQ4`. Only modify paths under `affects:` below.
> Source repos under `source-repos:` are clone-and-read-only into `~/work/vendor/`; never commit them.
> If anything is ambiguous, open a draft PR labelled `[BLOCKED: clarification]` and stop — do not guess.

# Spec 004 — Music Handlers Port

## Why

bitwize-music ships 14 handler modules totalling ~67 tools (`find_album`, `create_track`, `master_album`, `qc_audio`, `analyze_rhyme_scheme`, `db_search_tweets`, etc.) that are battle-tested across the existing music corpus. Re-implementing them from scratch inside the unified `agency-mcp` would burn 4+ Jules sessions and risk silent behavioural drift. Porting them verbatim into `handlers/music/`, rewriting only the import roots and registration glue, gives us 100% music parity on day one of Wave A and unblocks `005-music-skills-port` (which expects the new tool names). The `domain:music` FastMCP tag set in this spec is the foundation that `008-codemode-registry` keys against when classifying tools as `eager` / `deferred` / `background`.

## Done When

- [ ] All 16 handler files under `servers/agency-mcp/src/agency_mcp/handlers/music/` exist and import cleanly.
- [ ] `pytest -x tests/unit/music/test_handlers_smoke.py` exits 0.
- [ ] `python -c "from agency_mcp.server import create_mcp; m = create_mcp(); print(len(m._tools))"` reports ≥60 tools after music registration.
- [ ] Every music tool is registered with `tags={"domain:music"}` (verified by the smoke test scanning `mcp._tools[name].tags`).
- [ ] Every music tool name matches the regex `^music_[a-z]+(_[a-z0-9]+)+$` (snake_case `music_<verb>_<object>`).
- [ ] `register_music_handlers(mcp)` is called from `register_all(mcp)` in `server.py`.
- [ ] No reference to `bitwize-music` or `~/.bitwize-music/` remains in `handlers/music/` (verified by `rg`).

## Source clones (run first)

```bash
git clone --depth=1 --branch=v0.91.0 \
  https://github.com/bitwize-music-studio/claude-ai-music-skills.git \
  ~/work/vendor/bitwize-music
```

If clone fails: open draft PR `[BLOCKED: verify-source-url]` per `Plan/SOURCES.md` verification flag. Do not guess an alternate URL.

## Files

- **Create**:
  - `servers/agency-mcp/src/agency_mcp/handlers/music/__init__.py` — exports `register_music_handlers(mcp)`.
  - 16 handler modules under `handlers/music/`: `core.py`, `audio.py`, `mixing.py`, `sheet_music.py`, `video.py`, `lyrics_analysis.py`, `text_analysis.py`, `album_ops.py`, `gates.py`, `database.py`, `ideas.py`, `streaming.py`, `content.py`, `health.py`, `maintenance.py`, `promo.py`.
  - `tests/unit/music/__init__.py`.
  - `tests/unit/music/test_handlers_smoke.py` — asserts each module exposes ≥1 `@mcp.tool()` registration and the aggregate count is ≥60.
- **Modify**:
  - `servers/agency-mcp/src/agency_mcp/server.py` — call `register_music_handlers(mcp)` inside `register_all(mcp)`.
- **Move / Delete**: none. `vendor/bitwize-music/` is read-only and never committed.

## Approach

1. **Gate 1 — Confidence.** Confirm no `handlers/music/` modules already exist (`rg -l 'domain:music' servers/`). Verify `fastmcp[code-mode]>=3.1.0` is in `servers/agency-mcp/pyproject.toml` (Spec 001). Verify `agency_mcp.state.cache.StateCache` exists (Spec 003). Cite the commands in the PR Confidence table.
2. **Clone source.** Run the clone command above. `ls ~/work/vendor/bitwize-music/servers/bitwize-music-server/handlers/` should list 14 `.py` files. Read each to enumerate its tool functions and dependencies on `lib/audio_processing/`, `state/cache.py`, and `lib/codemode/`.
3. **Port skeleton.** For each source module, create the matching `handlers/music/<module>.py`. Copy the function bodies verbatim. Rewrite imports: `from bitwize_music.lib.audio_processing` → `from agency_mcp.lib.audio_processing`; `from bitwize_music.state.cache` → `from agency_mcp.state.cache`; `from bitwize_music.lib.codemode` → `from agency_mcp.lib.codemode`.
4. **Rename tools.** Every `@mcp.tool()`-decorated function gets renamed to `music_<verb>_<object>`. Examples: `find_album` → `music_find_album`, `create_track` → `music_create_track`, `master_album` → `music_master_album`, `analyze_rhyme_scheme` → `music_analyze_rhyme_scheme`, `db_search_tweets` → `music_db_search_tweets`. Keep the docstring ≤120 chars (overview §2.1 #2). Add `tags={"domain:music"}` to every `@mcp.tool(...)` decoration.
5. **Split modules where source mixes domains.** Source `core.py` mixes album + track operations; if so split as listed in `affects:` (`album_ops.py`, `core.py` for tracks). Source `tools_audio.py` → `audio.py`. Source `tools_mixing.py` → `mixing.py`. Match the 16-module layout listed in `affects:` exactly.
6. **Wire registration.** Each module exposes `def register(mcp): ...` that does the `@mcp.tool` registrations. `handlers/music/__init__.py` defines `register_music_handlers(mcp)` that imports all 16 modules and calls each `register(mcp)` in deterministic order.
7. **Server hookup.** In `server.py`, inside `register_all(mcp)`, add `from agency_mcp.handlers.music import register_music_handlers; register_music_handlers(mcp)`. Keep the call idempotent (the smoke test will call `create_mcp()` twice).
8. **TDD — Gate 2.** RED: write `tests/unit/music/test_handlers_smoke.py` with three tests: `test_all_modules_register_at_least_one_tool`, `test_tool_count_at_least_60`, `test_every_music_tool_has_domain_tag`, `test_tool_names_match_naming_convention`. Run them — they must fail before the handlers are wired. GREEN: wire the handlers. REFACTOR: deduplicate the per-module `register(mcp)` boilerplate via a small helper if it does not weaken type-checking.
9. **Gate 3 — Evidence.** Paste `pytest -x tests/unit/music/test_handlers_smoke.py` output, `python -c "from agency_mcp.server import create_mcp; print(len(create_mcp()._tools))"` output, and `rg 'tags=\{"domain:music"\}' servers/agency-mcp/src/agency_mcp/handlers/music/ -c` aggregate count into PR `## Evidence`.
10. **Gate 4 — Self-Review.** Answer the three questions in the PR body. Specifically flag any tools intentionally omitted from the port (e.g. dead-code branches in the source) and the rationale.

## Acceptance (Gherkin)

```gherkin
# anchor: 004.1
Scenario: All 16 music handler modules register tools on the unified FastMCP
  Given Spec 003 has shipped agency_mcp.state.cache.StateCache
  And the music handlers package has been ported per this spec
  When the operator runs "python -c \"from agency_mcp.server import create_mcp; m = create_mcp(); print(len(m._tools))\""
  Then the process exits with status 0
  And stdout reports an integer ≥ 60

# anchor: 004.2
Scenario: Every music tool carries the domain:music tag and a music_ prefix
  Given the music handlers are registered on a FastMCP instance
  When the smoke test iterates mcp._tools.values()
  Then every tool whose name starts with "music_" has "domain:music" in its tags set
  And no tool with "domain:music" in its tags has a name not starting with "music_"

# anchor: 004.3
Scenario: Music tool names follow snake_case music_<verb>_<object>
  Given the music handlers package is importable
  When the smoke test inspects each registered music tool name
  Then every name matches the regex ^music_[a-z]+(_[a-z0-9]+)+$
  And the legacy names find_album, create_track, master_album are NOT present
```

## Out of scope

- Porting music skills / `SKILL.md` files (Spec 005).
- Wiring Code Mode `defer_schema=True` classification (Spec 008 — this spec only sets tags so 008 can key off them).
- Porting `hooks/validate_track.py` and related PostToolUse hooks (Spec 017).
- Porting / migrating `~/.bitwize-music/config.yaml` (Specs 018, 019).
- Deleting or deprecating the bitwize-music plugin install (Spec 020).
- Novel, jules, agentic handlers (Specs 006, 011, 013, 016).

## References

- `Plan/JULES_PROTOCOL.md` (gates 1–4, §4 source-repo discipline)
- `Plan/000-overview.md` §1 (target tree), §2.1 #1–#2 (tool naming + tags), §2.1 #10 (StateCache singleton)
- `Plan/SOURCES.md` (bitwize-music v0.91.0 clone command + verification flag)
- Spec dependency: `Plan/003-unified-statecache-port/spec.md` (StateCache contract)
- Spec downstream: `Plan/005-music-skills-port/spec.md` (depends on these tool names)
- Vendor source (read-only): `~/work/vendor/bitwize-music/servers/bitwize-music-server/handlers/*.py`
