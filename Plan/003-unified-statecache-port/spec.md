---
spec_id: 003
slug: unified-statecache-port
status: ready
owner: jules
depends_on: [001]
affects:
  - servers/agency-mcp/src/agency_mcp/state/__init__.py
  - servers/agency-mcp/src/agency_mcp/state/cache.py
  - servers/agency-mcp/src/agency_mcp/state/unified_indexer.py
  - servers/agency-mcp/src/agency_mcp/state/indexers/__init__.py
  - servers/agency-mcp/src/agency_mcp/state/indexers/music_indexer.py
  - servers/agency-mcp/src/agency_mcp/state/indexers/novel_indexer.py
  - servers/agency-mcp/src/agency_mcp/state/indexers/jules_indexer.py
  - servers/agency-mcp/src/agency_mcp/state/indexers/ncp_indexer.py
  - state/schema/state.schema.json
  - tests/unit/state/__init__.py
  - tests/unit/state/test_cache.py
source-repos:
  - bitwize-music: v0.91.0
estimated_jules_sessions: 2
domain: cross
wave: A
---

> **Jules: read `Plan/JULES_PROTOCOL.md` before starting.** Run gates 1→4 in order:
> (1) Confidence ≥ 0.90, (2) TDD Red-Green-Refactor, (3) Evidence pasted under `## Evidence`, (4) Self-Review answered.
> Branch: `claude/agency-plugin-refactor-PgMQ4`. Only modify paths under `affects:` below.
> Source repos under `source-repos:` are clone-and-read-only into `~/work/vendor/`; never commit them.
> If anything is ambiguous, open a draft PR labelled `[BLOCKED: clarification]` and stop — do not guess.

# Spec 003 — Unified StateCache Port

## Why

bitwize's thread-safe `StateCache` is the lynchpin that lets handlers share a single in-memory state without re-parsing markdown on every tool call. Porting it with namespaced top-level keys (`music`, `novel`, `jules`, `agentic`) gives all four domains one cache, one `asyncio.Lock`, and one mtime-staleness check against `~/.agency-system/cache/state.json`. Without this spec, every domain handler in waves A–C would invent its own cache layer and the Code Mode token budget would regress past its 315-token target (§2.1.4 of the overview). Per-domain indexer stubs are wired here so Specs 004 (music), 011 (novel), 006 (jules), and 016 (agentic) can populate them without touching the cache.

## Done When

- [ ] `StateCache` class exists at `servers/agency-mcp/src/agency_mcp/state/cache.py`, gates writes through `asyncio.Lock`, and refreshes on mtime change of `~/.agency-system/cache/state.json`.
- [ ] Top-level state shape is exactly `{music: {}, novel: {}, jules: {}, agentic: {}, _version: "1.0.0"}` and matches `state/schema/state.schema.json`.
- [ ] Per-domain indexer stub files exist and each `build()` returns `{"_generated": None}` until populated by downstream specs.
- [ ] Writes to one namespace do not bump the `_generated` timestamp of any other namespace (namespace isolation).
- [ ] `pytest -x tests/unit/state/` exits 0 with at least these tests green: concurrent-write race, mtime invalidation, namespace isolation, schema-conformance.
- [ ] `jsonschema` validates a freshly-built state dict against `state/schema/state.schema.json` (asserted in test).

## Source clones (run first)

```bash
git clone --depth=1 --branch=v0.91.0 \
  https://github.com/bitwize-music-studio/claude-ai-music-skills.git \
  ~/work/vendor/bitwize-music
```

If clone fails per the `Plan/SOURCES.md` verification flag, stop and open `[BLOCKED: verify-source-url]`.

## Files

- **Create**:
  - `servers/agency-mcp/src/agency_mcp/state/__init__.py`
  - `servers/agency-mcp/src/agency_mcp/state/cache.py`
  - `servers/agency-mcp/src/agency_mcp/state/unified_indexer.py`
  - `servers/agency-mcp/src/agency_mcp/state/indexers/__init__.py`
  - `servers/agency-mcp/src/agency_mcp/state/indexers/music_indexer.py`
  - `servers/agency-mcp/src/agency_mcp/state/indexers/novel_indexer.py`
  - `servers/agency-mcp/src/agency_mcp/state/indexers/jules_indexer.py`
  - `servers/agency-mcp/src/agency_mcp/state/indexers/ncp_indexer.py`
  - `state/schema/state.schema.json`
  - `tests/unit/state/__init__.py`
  - `tests/unit/state/test_cache.py`
- **Modify**: none (Spec 001's `server.py` will gain a `StateCache` lifespan binding in Spec 008, not here).
- **Move / Delete**: none.

## Approach

1. Clone bitwize-music v0.91.0 to `~/work/vendor/bitwize-music` (read-only). Confirm `git status` in the work tree shows no `vendor/` entries (Protocol §4).
2. Read `vendor/bitwize-music/tools/state/indexer.py` and `vendor/bitwize-music/servers/bitwize-music-server/server.py:114-288` to study the existing `StateCache` lock + mtime pattern. Cite specific line ranges in the PR Confidence block (Gate 1 Check 4).
3. Port the cache to `servers/agency-mcp/src/agency_mcp/state/cache.py`. Replace bitwize's flat shape with the namespaced shape `{music, novel, jules, agentic, _version}`; keep the `asyncio.Lock` and `mtime` semantics intact. Cache path is `Path.home() / ".agency-system" / "cache" / "state.json"` (overview §1 — single unified JSON).
4. Define `state/schema/state.schema.json` (JSON Schema draft-07) with the four required namespace properties (each an object), a required `_version` string pinned to `"1.0.0"`, and `additionalProperties: false` at the top level. Each namespace allows an optional `_generated` ISO-8601 timestamp.
5. Build `unified_indexer.py` with a `build_unified_state(domains: list[str]) -> dict` function that calls each per-domain stub and assembles the top-level dict. Per-domain stubs (`music_indexer.py`, `novel_indexer.py`, `jules_indexer.py`, `ncp_indexer.py`) each export `build() -> dict` returning `{"_generated": None}` so downstream specs only need to fill in the body.
6. RED — write `tests/unit/state/test_cache.py` covering: (a) `test_concurrent_writes_do_not_deadlock` — two `asyncio.gather` writes to `music` and `novel`; (b) `test_mtime_change_triggers_reload` — touch the cache file, assert next read sees the new value; (c) `test_namespace_isolation` — write to `music`, assert `novel._generated` unchanged; (d) `test_state_dict_validates_against_schema` — load `state.schema.json`, validate `await cache.snapshot()`. Watch all four fail before implementation.
7. GREEN — implement the cache to make tests pass, no extras. Use `asyncio.Lock` per the spec; do NOT introduce `threading.Lock` (the runtime is async-only — overview §2.1.10).
8. REFACTOR — extract the mtime-check into a small `_is_stale()` helper if the lock body grows past ~25 lines; otherwise leave inline. Re-run `pytest -x tests/unit/state/` and paste the exit-zero tail under `## Evidence`.

## Acceptance (Gherkin)

```gherkin
# anchor: 003.1
Scenario: Concurrent writes to disjoint namespaces both succeed
  Given a fresh StateCache backed by ~/.agency-system/cache/state.json
  When the test issues asyncio.gather of cache.write("music", {...}) and cache.write("novel", {...})
  Then both writes complete without deadlock
  And the resulting snapshot has both namespaces populated
  And no asyncio.TimeoutError is raised within 2 seconds

# anchor: 003.2
Scenario: mtime change on the backing file triggers a reload
  Given a StateCache that has already loaded the on-disk state once
  When a separate process (simulated via os.utime) bumps the file mtime
  And the test calls cache.snapshot() again
  Then the cache re-reads the file
  And the returned dict reflects the on-disk change

# anchor: 003.3
Scenario: Writing one namespace does not bump another namespace's _generated
  Given a StateCache with music._generated="T0" and novel._generated="T0"
  When the test writes to the "music" namespace at time T1 > T0
  Then snapshot()["music"]["_generated"] equals T1
  And snapshot()["novel"]["_generated"] still equals T0

# anchor: 003.4
Scenario: Snapshot validates against state.schema.json
  Given the file state/schema/state.schema.json is loaded as a jsonschema validator
  When the test calls validator.validate(await cache.snapshot())
  Then no jsonschema.ValidationError is raised
  And the snapshot contains exactly the keys music, novel, jules, agentic, _version
```

## Out of scope

- Wiring `StateCache` into the FastMCP lifespan (Spec 008 owns Code Mode registry + lifespan).
- Populating any indexer beyond the `{"_generated": None}` stub (Spec 004 fills music; Spec 011 fills novel; Spec 006 fills jules; Spec 016 fills agentic).
- Migrating data from `~/.bitwize-music/cache/state.json` into the new shape (Spec 019 owns migration).
- Hook-based cache invalidation (overview §2.1.11 — hooks are non-correctness side effects only).
- Process-global singletons; cache is per-FastMCP-lifespan only (overview §2.1.10).

## References

- `Plan/JULES_PROTOCOL.md` (gates 1–4, §4 source-repo rules)
- `Plan/000-overview.md` §1 (state on disk), §2.1.10 (StateCache convention), §2.1.11 (hook rule)
- `Plan/SOURCES.md` (bitwize-music v0.91.0 clone command)
- Spec 001 (server skeleton this cache plugs into)
- Spec 008 (Code Mode registry — consumer of this cache, downstream)
- Vendor refs: `vendor/bitwize-music/tools/state/indexer.py`, `vendor/bitwize-music/servers/bitwize-music-server/server.py:114-288`
