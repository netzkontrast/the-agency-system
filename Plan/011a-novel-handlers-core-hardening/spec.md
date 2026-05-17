---
spec_id: 011a
slug: novel-handlers-core-hardening
status: ready
owner: jules
depends_on: [011]
affects:
  - servers/agency-mcp/src/agency_mcp/handlers/novel/_shared.py
  - servers/agency-mcp/src/agency_mcp/handlers/novel/work_ops.py
  - servers/agency-mcp/src/agency_mcp/handlers/novel/content.py
  - servers/agency-mcp/src/agency_mcp/handlers/novel/ideas.py
  - servers/agency-mcp/src/agency_mcp/handlers/novel/status.py
  - servers/agency-mcp/src/agency_mcp/handlers/novel/novel_indexer.py
  - tests/unit/novel/test_dry_run_coverage.py
  - tests/unit/novel/test_singleton_cache.py
  - tests/unit/novel/test_indexer_atomicity.py
  - tests/unit/novel/test_transition_table.py
  - tests/unit/novel/test_list_cursor.py
source-repos: []
estimated_jules_sessions: 1
domain: novel
wave: B
---

> **Jules: read `Plan/JULES_PROTOCOL.md` before starting.** Run gates 1→4 in order:
> (1) Confidence ≥ 0.90, (2) TDD Red-Green-Refactor, (3) Evidence pasted under `## Evidence`, (4) Self-Review answered.
> Branch: `claude/agency-plugin-refactor-PgMQ4`. Only modify paths under `affects:` below.
> Source repos under `source-repos:` are clone-and-read-only into `~/work/vendor/`; never commit them.
> If anything is ambiguous, open a draft PR labelled `[BLOCKED: clarification]` and stop — do not guess.

# Spec 011a — Novel Handlers Core Hardening

## Why

PR #44 (Spec 011 novel-handlers-core) merged on Master via PR #45 but the independent review surfaced one Done-When violation (P1) and five §2.1 contract drifts (P2). They are individually small but compound badly the moment a second domain writes concurrently with novel. This spec is a single-session correctness pass that lands the missing `dry_run` coverage and refactors the StateCache instancing to a singleton accessor before Wave B specs 013/014/015/021 add to the per-domain footprint.

## Done When

- [ ] All 14 stateful novel tools accept `dry_run: bool = False` and return `{would_apply: True, diff: ..., warnings: [...]}` on True per overview §2.1.7. Specifically: `novel_rebuild_state`, `novel_create_premise_idea`, `novel_update_premise_idea`, `novel_delete_premise_idea`, `novel_promote_premise`, `novel_update_work_status`, `novel_update_chapter_status`, `novel_update_scene_status` (the 8 missing) + the 6 already compliant.
- [ ] Module-level `cache = _get_cache()` removed from every `handlers/novel/*.py`; replaced with a lazy `_shared.get_cache()` accessor returning the singleton set by `server.register_all()` per overview §2.1.10.
- [ ] `novel_indexer.rebuild()` acquires the cache write lock for the entire walk (single `async with cache._lock:` block); no read-modify-write gap.
- [ ] `novel_update_chapter_status` + `novel_update_scene_status` validate transitions against the same legal-transition table as `novel_update_work_status` (mirror bitwize's `update_track_field` rules).
- [ ] Work-level transition table tightened: `done → review` and `archived → draft` are explicitly rejected. Only `WIP → review → done → archived` and `WIP → archived` direct.
- [ ] `novel_list_*` returns `{items: [...], next_cursor: str | None}` per overview §2.1.6 when total > limit; smoke test asserts cursor is opaque (base64 or similar, not raw offset).
- [ ] `pytest -x tests/unit/novel/` passes including 5 new test files.

## Source clones (run first)

```bash
# No external clones — this spec works on the existing tree.
# Reference reading:
git log -1 --stat origin/Master -- servers/agency-mcp/src/agency_mcp/handlers/novel/
```

## Files

- **Modify**:
  - `servers/agency-mcp/src/agency_mcp/handlers/novel/_shared.py` — promote to host the `get_cache()` singleton accessor + the `STATUS_TRANSITIONS` table shared across status.py module.
  - `servers/agency-mcp/src/agency_mcp/handlers/novel/work_ops.py` — add `dry_run` to `novel_rebuild_state`; replace module-level `cache` with `_shared.get_cache()` calls; add `next_cursor` to `novel_list_works`.
  - `servers/agency-mcp/src/agency_mcp/handlers/novel/content.py` — `next_cursor` on `novel_list_chapters` + `novel_list_scenes`; replace module-level cache.
  - `servers/agency-mcp/src/agency_mcp/handlers/novel/ideas.py` — add `dry_run` to 4 tools (`create_premise_idea`, `update_premise_idea`, `delete_premise_idea`, `promote_premise`); replace module-level cache.
  - `servers/agency-mcp/src/agency_mcp/handlers/novel/status.py` — add `dry_run` to 3 status tools; pull transition table from `_shared.STATUS_TRANSITIONS`; reject `done → review` + `archived → draft` at work level; mirror table on chapter/scene granularities.
  - `servers/agency-mcp/src/agency_mcp/handlers/novel/novel_indexer.py` — wrap entire `rebuild()` walk inside `async with cache._lock:`; remove the snapshot-then-write gap.
- **Create**:
  - `tests/unit/novel/test_dry_run_coverage.py` — parametrised test asserting every stateful tool returns `{would_apply: True}` when called with `dry_run=True` and does not touch disk.
  - `tests/unit/novel/test_singleton_cache.py` — assert all handler modules share the same `StateCache` instance after `register_all()`.
  - `tests/unit/novel/test_indexer_atomicity.py` — assert that concurrent `novel_create_work` calls during a rebuild do not lose updates (use an `asyncio.gather` fixture).
  - `tests/unit/novel/test_transition_table.py` — assert legal/illegal transitions at all 3 granularities (work, chapter, scene).
  - `tests/unit/novel/test_list_cursor.py` — assert `novel_list_*` returns a `next_cursor` when results exceed the limit and resumes correctly on next call.

## Approach

1. **Gate 1 — Confidence.** Verify PR #44 review comment from Claude at `https://github.com/netzkontrast/the-agency-system/pull/44#issuecomment-4472865462` enumerates exactly these P1/P2 items; cite the comment URL in the PR Confidence table.
2. **TDD — Gate 2.** Write the 5 new test files first. RED. Then refactor handlers; each batch should drive its respective test from RED to GREEN before moving on.
3. **Singleton refactor first.** Promote `_shared.py` to define `_cache: StateCache | None = None` + `def get_cache() -> StateCache: ...` + `def set_cache(c: StateCache) -> None: ...`. Update `server.py:register_all` to call `_shared.set_cache(StateCache())` once. Update all 5 handler modules to call `_shared.get_cache()` inside each tool body (lazy), removing module-level `cache = _get_cache()` lines.
4. **`dry_run` rollout.** For each of the 8 missing tools: add `dry_run: bool = False` as the last positional kw-only arg. Compute the diff first (don't mutate). On `dry_run=True`, return `{would_apply: True, diff: <minimal structured diff>, warnings: [...]}` early. On False, perform the mutation as before.
5. **Indexer atomicity.** Wrap the entire `rebuild()` body inside `async with cache._lock:` (one acquisition). Confirm no nested locks; if `cache.write` itself acquires, restructure to call a `_write_locked` private helper.
6. **Transition table.** Define `STATUS_TRANSITIONS: dict[str, dict[str, set[str]]]` in `_shared.py` keyed by granularity (`"work"` / `"chapter"` / `"scene"`) then current state. Reject any transition not in the table; raise with `code: "illegal_transition"` in the ToolResult.
7. **List cursor.** Implement opaque cursor via `base64.urlsafe_b64encode(json.dumps({"offset": N, "limit": L}).encode()).rstrip(b"=")`. `next_cursor` set only when more results exist.
8. **Gate 3 — Evidence.** Paste `pytest -x tests/unit/novel/` output (all green, 5 new files visible in collection list). Paste `python -c "from agency_mcp.server import create_mcp; from agency_mcp.handlers.novel import _shared; m=create_mcp(); print(id(_shared.get_cache()))"` showing the same id across modules.
9. **Gate 4 — Self-Review.** Answer the 3 questions. Specifically call out which transition-table entries are inherited from bitwize's `update_track_field` table verbatim vs. which are novel-domain-specific.

## Acceptance (Gherkin)

```gherkin
# anchor: 011a.1
Scenario: dry_run honoured on every stateful tool
  Given the unified MCP is created
  When the operator calls each of the 14 stateful novel tools with dry_run=True
  Then every call returns {ok: True, would_apply: True, diff: <not-empty>}
  And no file under novels/ is modified
  And no state.json mutation is observed

# anchor: 011a.2
Scenario: Single StateCache instance across handler modules
  Given the unified MCP is created
  When the operator imports _shared.get_cache() from each of work_ops, content, core, ideas, status
  Then every import returns the same Python object identity

# anchor: 011a.3
Scenario: Indexer rebuild is atomic
  Given the cache has an existing novel state with 3 works
  And two concurrent novel_create_work calls are launched in parallel with novel_rebuild_state
  When the gather completes
  Then both new works are present in state.json
  And neither is lost due to a snapshot-then-write race

# anchor: 011a.4
Scenario: Illegal status transitions rejected
  Given a chapter is in status "done"
  When the operator calls novel_update_chapter_status(chapter_id, status="review")
  Then the tool returns {ok: False, code: "illegal_transition", from: "done", to: "review"}

# anchor: 011a.5
Scenario: novel_list_* returns next_cursor when paginating
  Given there are 35 chapters across a work
  When the operator calls novel_list_chapters(work_id, limit=20)
  Then the response contains 20 items AND a next_cursor: <opaque-string>
  And calling novel_list_chapters(work_id, limit=20, cursor=<that string>) returns the remaining 15 items + next_cursor: None
```

## Out of scope

- New novel tools. This is a correctness pass on the 25 existing tools only.
- Schema changes to `state.json` or `novels/{author}/works/{...}` directory layout.
- Spec 013 territory (structural / coherence / prose_analysis handlers).

## References

- `Plan/JULES_PROTOCOL.md`
- `Plan/000-overview.md` §2.1.6 (list_* cap + cursor), §2.1.7 (dry_run requirement), §2.1.10 (one StateCache per lifespan)
- `Plan/011-novel-handlers-core/spec.md` — the spec this hardens
- PR #44 review comment: <https://github.com/netzkontrast/the-agency-system/pull/44#issuecomment-4472865462>
- `Plan/003-unified-statecache-port/spec.md` — StateCache contract
- `Plan/_lessons-learned/04-affects-incompleteness.md` — discipline reminder
