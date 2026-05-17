---
spec_id: 113
slug: context-cache-and-subscriptions
status: ready
owner: jules
depends_on: [008, 104, 111, 112]
affects:
  - servers/agency-mcp/src/agency_mcp/lib/codemode/__init__.py
  - servers/agency-mcp/src/agency_mcp/lib/codemode/context_cache.py
  - servers/agency-mcp/src/agency_mcp/lib/codemode/context_watcher.py
  - servers/agency-mcp/src/agency_mcp/handlers/context/resources.py
  - servers/agency-mcp/src/agency_mcp/handlers/context/anchors.py
  - servers/agency-mcp/src/agency_mcp/codemode/context_manifest.json
  - servers/agency-mcp/src/agency_mcp/server.py
  - servers/agency-mcp/pyproject.toml
  - tests/unit/context/test_context_cache.py
  - tests/unit/context/test_context_watcher.py
  - tests/integration/test_context_subscriptions.py
source-repos: []
estimated_jules_sessions: 2
domain: cross
wave: B
---

> **Jules: read `Plan/JULES_PROTOCOL.md` before starting.** Run gates 1→4 in order:
> (1) Confidence ≥ 0.90, (2) TDD Red-Green-Refactor, (3) Evidence pasted under `## Evidence`, (4) Self-Review answered.
> Branch: `claude/agency-plugin-refactor-PgMQ4`. Only modify paths under `affects:` below.
> Source repos under `source-repos:` are clone-and-read-only into `~/work/vendor/`; never commit them.
> If anything is ambiguous, open a draft PR labelled `[BLOCKED: clarification]` and stop — do not guess.

# Spec 113 — Context Cache & Subscriptions

## Why

Specs 108 + 109 make Context Mode functional but naïve: `context_read` re-loads files from disk on every call, the manifest is read once at boot and never re-checked, and MCP `resources/subscribe` is unwired so clients can't be told when a spec, lesson, or override changes mid-session. Three concrete failure modes follow: (1) a Jules session that edits `Plan/108-…/spec.md` keeps reading the stale cached body until restart; (2) every `context_read("plan:000-overview:spec", view="summary")` call burns a disk read for content that hasn't changed in days; (3) when overrides are migrated (Spec 018) mid-session, downstream skills consume the pre-migration content silently. The MCP `Resources` primitive defines `resources/subscribe` + `notifications/resources/updated` (modelcontextprotocol.io/specification/2025-06-18/server/resources §Subscriptions) — Spec 112 stops short of wiring it. This spec closes the loop: a TTL'd LRU cache fronted by sha256 ETags, a file-system watcher that invalidates entries and emits change notifications to subscribed clients, and a manifest-rebuild trigger so renaming or adding a file doesn't require a full server restart. The deliverable is the *change* axis of Context Mode — the manifest tells the model *what exists*; this spec tells it *when something changed*.

## Done When

- [ ] `lib/codemode/context_cache.py` exports `ContextCache(maxsize=128, default_ttl_s=300)` with `get(id, view) -> ContextBody | None` and `put(id, view, body) -> None`. Cache key is `(id, view, sha256)` — invalidation on sha256 mismatch is automatic.
- [ ] `ContextCache.get` returns `None` on miss, on TTL expiry, OR when the on-disk file's current sha256 differs from the cached entry's sha256 (the cache ALWAYS re-stats the underlying file before returning a hit; this is the "ETag" check).
- [ ] `context_read` (from Spec 109) is rewired to consult `ContextCache` first; on miss, it reads from disk, populates the cache, and returns. Cache hits MUST be byte-identical to fresh reads (asserted in a test).
- [ ] `lib/codemode/context_watcher.py` exports `ContextWatcher(manifest, on_change: Callable[[ChangeEvent], None])` that polls the manifest's tracked paths once per `poll_interval_s` (default 5 s) and emits `ChangeEvent(id, kind: Literal["modified","deleted","added"], old_sha256, new_sha256)` for every file whose sha256 differs from the manifest's recorded sha256. `added`/`deleted` are detected by comparing the tree against the manifest's path set.
- [ ] The watcher runs as a daemon thread started inside `register_context_handlers(mcp)` and is gracefully stopped when `mcp` shuts down (registers an `atexit` handler).
- [ ] On every `ChangeEvent`, the watcher (a) invalidates the cache entries for that ID, (b) emits an MCP `notifications/resources/updated` for `context://<id>` if any client has subscribed via `resources/subscribe`, (c) appends a `ContextChangeLog` entry (in-memory ring buffer, capacity 256) accessible via a new eager tool `context_changes(since: str | None = None, limit: int = 50)`.
- [ ] `context_changes` is the **fourth** eager context anchor (added to `always_eager`); it returns `[{id, kind, old_sha256, new_sha256, observed_at}]` ordered newest-first. With `since` (ISO-8601), it returns only events strictly after that timestamp.
- [ ] Manifest auto-rebuild: when the watcher detects `added` or `deleted` files (path-set delta), it triggers `ContextManifest.rebuild_in_place(manifest_path)` which calls back into Spec 108's `build_context_manifest.py` as a subprocess; the rebuilt manifest is hot-swapped into `register_context_handlers`'s module-scope cache without restart. If the subprocess exits non-zero, the in-memory manifest is NOT replaced and the failure is logged via `mcp.logger.warning`.
- [ ] `pytest -x tests/unit/context/test_context_cache.py` and `pytest -x tests/unit/context/test_context_watcher.py` both exit 0.
- [ ] `pytest -x tests/integration/test_context_subscriptions.py` exits 0 — covers (a) cache hit / miss / TTL expiry, (b) sha256-mismatch auto-invalidation, (c) file-mutation → ChangeEvent → `notifications/resources/updated` round-trip via a mock MCP client subscription, (d) added-file → manifest rebuild → new entry visible via `context_search`.
- [ ] Token-budget regression (extending Spec 109's test): `tools/list` after adding `context_changes` is ≤ 1.07× the pre-Context-Mode baseline (four eager anchors now, not three).
- [ ] The watcher's CPU cost is bounded: with default `poll_interval_s=5`, a manifest of 100 entries triggers ≤ 100 `os.stat` calls per poll and 0 file reads when no file has changed (verified by patching `os.stat` and asserting call count in a unit test).

## Source clones (run first)

None.

Reference docs to consult via WebFetch:
- https://modelcontextprotocol.io/specification/2025-06-18/server/resources — §Subscriptions for the `resources/subscribe` / `notifications/resources/updated` wire format.
- https://gofastmcp.com/servers/resources — FastMCP's exposed API for emitting resource-update notifications (look for `mcp.notify_resource_updated(uri)` or equivalent; if the helper does not exist on this FastMCP version, fall back to constructing the JSON-RPC notification directly per the MCP spec — document the fallback in the PR).

## Files

- **Create**:
  - `servers/agency-mcp/src/agency_mcp/lib/codemode/context_cache.py` — TTL + LRU cache with sha256 ETag check.
  - `servers/agency-mcp/src/agency_mcp/lib/codemode/context_watcher.py` — polling watcher, ChangeEvent emitter, manifest rebuild trigger.
  - `tests/unit/context/test_context_cache.py` — cache hit/miss/TTL/etag-invalidation unit tests.
  - `tests/unit/context/test_context_watcher.py` — watcher state-machine unit tests with mocked filesystem.
  - `tests/integration/test_context_subscriptions.py` — end-to-end: subscribe → mutate → observe notification.
- **Modify**:
  - `servers/agency-mcp/src/agency_mcp/lib/codemode/__init__.py` — re-export `ContextCache`, `ContextWatcher`, `ChangeEvent`.
  - `servers/agency-mcp/src/agency_mcp/handlers/context/anchors.py` — wire `context_read` through `ContextCache`; add the new `context_changes` tool.
  - `servers/agency-mcp/src/agency_mcp/handlers/context/resources.py` — emit `notifications/resources/updated` on ChangeEvent.
  - `servers/agency-mcp/src/agency_mcp/codemode/context_manifest.json` — note: this file is rewritten by the watcher on add/delete; the spec does not edit it by hand.
  - `servers/agency-mcp/src/agency_mcp/codemode/manifest.json` — add `context_changes` to `always_eager` with `classification: "eager"`, `domain: "cross"`, `anchor_kind: "context"`.
  - `servers/agency-mcp/src/agency_mcp/server.py` — start the watcher inside `register_context_handlers(mcp)`; register `atexit` shutdown.
  - `servers/agency-mcp/pyproject.toml` — no new runtime deps (use stdlib `threading`, `time`, `hashlib`, `subprocess`); add `pytest-timeout` to dev-deps if not already present so watcher tests can't hang.

## Approach

1. **Gate 1 — Confidence.** Verify Specs 108 + 109 have shipped (`context_manifest.json` exists with ≥ 40 entries; `context_search`/`context_describe`/`context_read` are registered eager). Verify FastMCP's resource-notification API on the pinned version — call `python -c "import fastmcp; print(dir(fastmcp.FastMCP))"` and grep for `notify_resource_updated` or `resource_updated`. If absent, plan the JSON-RPC fallback explicitly in the Confidence section, citing modelcontextprotocol.io's `notifications/resources/updated` shape `{method: "notifications/resources/updated", params: {uri: "context://..."}}`.
2. **Implement `ContextCache`.** OrderedDict-backed LRU. `put(id, view, body)` stores `(body, sha256, inserted_at)`. `get(id, view)`: (a) miss if absent; (b) `os.stat` the entry's path from the manifest, compute current sha256 (use `entry.last_modified` + `entry.size_bytes` as a fast-path: if both unchanged from cached values, skip the hash); (c) compare to cached sha256, return `None` on mismatch; (d) miss if `time.monotonic() - inserted_at > ttl_s`; (e) hit: move to OrderedDict end, return body. Edge: `last_modified` granularity is 1 s on some filesystems — always fall back to sha256 if size matches but mtime is within 1 s of insertion time.
3. **Implement `ContextWatcher`.** Daemon thread loop:
   - Compute the manifest's current path-set (manifest IDs and their paths).
   - For each entry, `os.stat` → compare `size_bytes` + `last_modified` against the manifest record; if either changed, compute fresh sha256; if sha256 changed, emit `ChangeEvent(id, "modified", old_sha256, new_sha256)`.
   - Compute the filesystem path-set (re-glob the same roots Spec 108's builder used).
   - For paths in FS but not manifest → `ChangeEvent(id=<derived>, "added", None, new_sha256)`.
   - For paths in manifest but not FS → `ChangeEvent(id, "deleted", old_sha256, None)`.
   - For every event: (a) invalidate matching cache entries via `cache.invalidate(id)`, (b) append to the in-memory `ChangeLog` ring buffer, (c) call `mcp.notify_resource_updated(f"context://{id}")` (or JSON-RPC fallback), (d) if event kind is `added` or `deleted`, schedule a manifest rebuild (subprocess: `python bin/build_context_manifest.py --out <manifest_path>`); on rebuild success, swap the in-memory manifest atomically.
   - Sleep `poll_interval_s`. The loop is interruptible via a `threading.Event` cancellation flag (so shutdown is fast).
4. **Wire `context_read` through the cache.** In `handlers/context/anchors.py`, before reading from disk, call `cache.get(id, view)`; on miss, read + populate + return. Preserve all existing behaviour (truncation marker, fields projection, view fallback).
5. **Implement `context_changes`.** New eager tool. Read from the `ChangeLog` ring buffer (a `collections.deque(maxlen=256)`). Filter by `since` if provided (ISO-8601 timestamp parsed via `datetime.fromisoformat`). Return up to `limit` (default 50, max 256) most-recent events. Tool description: `"List recent additions/modifications/deletions in the context manifest. Use after a long pause to detect changes."`.
6. **Wire `server.py`.** Inside `register_context_handlers(mcp)`, after registering the four anchors and resources, instantiate `ContextWatcher(manifest, on_change=…)` and start its thread. Register `atexit.register(watcher.stop)`. The `on_change` callback closes over `(cache, change_log, mcp)`.
7. **TDD — Gate 2.** RED tests:
   - **Cache (`test_context_cache.py`):** `test_get_miss_returns_none`, `test_put_then_get_hit`, `test_ttl_expiry_returns_none`, `test_sha256_mismatch_invalidates`, `test_lru_eviction_when_maxsize_exceeded`, `test_get_does_not_burn_read_when_size_and_mtime_match`.
   - **Watcher (`test_context_watcher.py`):** `test_no_change_emits_no_events`, `test_modified_file_emits_modified_event`, `test_added_file_emits_added_and_schedules_rebuild`, `test_deleted_file_emits_deleted_event`, `test_stat_call_count_bounded_at_one_per_entry_per_poll`, `test_rebuild_subprocess_failure_does_not_swap_manifest`.
   - **Integration (`test_context_subscriptions.py`):** `test_subscribe_then_mutate_yields_notification`, `test_added_file_visible_via_context_search_after_rebuild`, `test_cache_hit_byte_identical_to_fresh_read`, `test_context_changes_returns_recent_events_newest_first`.
   All tests RED. GREEN: implement. REFACTOR: extract the `manifest entry → fresh-sha256` step into a pure helper testable in isolation.
8. **Token-budget regression.** Extend `tests/integration/test_boot_token_budget.py` (originally extended in Spec 109) with: `tools_list_tokens_after_context_changes <= ceil(tools_list_tokens_before_context_mode * 1.07)`. If this trips, do not loosen the threshold — minify the `context_changes` description first.
9. **Threading discipline.** The watcher MUST NOT hold any lock during the on_change callbacks for longer than needed to update the cache and log; resource-update notifications and subprocess rebuilds happen outside the polling lock to avoid deadlocking subscribers. Document this in a docstring on `ContextWatcher._on_change`. Use `pytest-timeout` (5 s default) on the watcher tests so a deadlock bug fails fast in CI rather than hanging.
10. **Gate 3 — Evidence.** Paste: (a) all three pytest outputs. (b) `python -c "from agency_mcp.server import create_mcp; m=create_mcp(); print(sorted([t for t in m._tools if t.startswith('context_')]))"` showing all four anchors. (c) Boot-token-budget test stdout including the new ≤ 1.07× assertion. (d) A 5-line transcript demonstrating the end-to-end loop: subscribe → `touch Plan/000-overview.md` → notification arrives in the mock client (paste the JSON-RPC notification body). **Gate 4 — Self-Review.** Confirm: (i) no `os.stat` storm on idle (watcher quiescent CPU < 1% on the test host — paste `top` output or `time.monotonic()` deltas); (ii) the watcher cleanly shuts down on `atexit` (no zombie thread on second `create_mcp()` call); (iii) if FastMCP's notification helper was unavailable, the JSON-RPC fallback is cited.

## Acceptance (Gherkin)

```gherkin
# anchor: 110.1
Scenario: Cache hit returns byte-identical body to a fresh disk read
  Given context_read has been called once for id="plan:008-codemode-registry:spec", view="preview"
  And the underlying file has not changed
  When context_read is called again with the same arguments
  Then the cache reports a hit (test asserts via mock counter)
  And the returned body is bytes-equal to a direct file read of the same byte window

# anchor: 110.2
Scenario: Modifying a tracked file invalidates the cache and emits a notification
  Given a mock MCP client has subscribed to "context://plan:000-overview:spec" via resources/subscribe
  And context_read has populated the cache for that id
  When the file Plan/000-overview.md is modified on disk
  And the watcher polls within poll_interval_s + 1 seconds
  Then the cache no longer reports a hit for that id
  And the mock client receives a "notifications/resources/updated" message with uri "context://plan:000-overview:spec"
  And context_changes(limit=10) lists that id at index 0 with kind="modified"

# anchor: 110.3
Scenario: Adding a new spec file rebuilds the manifest in place
  Given the manifest does NOT contain id "plan:999-test-spec:spec"
  When the file Plan/999-test-spec/spec.md is created
  And the watcher polls
  Then a ChangeEvent with kind="added" is logged
  And the manifest is rebuilt via subprocess
  And after the rebuild, context_search(query="999-test-spec") returns the new entry
  And the new resource "context://plan:999-test-spec:spec" appears in resources/list

# anchor: 110.4
Scenario: Quiescent watcher does not perform file reads, only stats
  Given the manifest contains N entries
  And no file in the indexed tree has changed since last poll
  When the watcher completes one poll cycle
  Then the os.stat call count is ≤ N + path_set_size
  And the file-read call count for indexed content is exactly 0

# anchor: 110.5
Scenario: Manifest rebuild failure does not corrupt the in-memory manifest
  Given the watcher detects an added file
  And the subprocess "python bin/build_context_manifest.py" exits with status 1
  When the watcher's on_change handler returns
  Then the in-memory manifest is unchanged
  And a warning has been logged via mcp.logger.warning
  And context_search continues to return results from the pre-rebuild manifest

# anchor: 110.6
Scenario: Four context anchors stay within the 1.07× tools/list budget
  Given the boot-token-budget integration test has captured tools_list_tokens_before
  When context_search, context_describe, context_read, AND context_changes are all eager
  Then tools_list_tokens_after_context_mode ≤ ceil(tools_list_tokens_before * 1.07)
```

## Out of scope

- Replacing the polling watcher with an inotify/FSEvents/ReadDirectoryChangesW backend — polling is portable and 5 s latency is acceptable for documentation content. Native watchers are a future spec if needed.
- Persisting the cache across server restarts — in-memory only; restart re-populates lazily.
- Persisting the ChangeLog across restarts — in-memory ring buffer only.
- Diffing file contents between revisions — only the change *kind* is reported, not a content diff. Clients call `context_read` to fetch the new body.
- Adding embeddings / re-ranking on changed entries — Wave B BM25 is still sufficient.
- Wiring CI to run the watcher tests against a real filesystem — the integration test uses a tmpdir-rooted fixture manifest.
- Modifying the manifest schema (Spec 111 owns that) or the anchor-triad API (Spec 112 owns that).

## References

- `Plan/JULES_PROTOCOL.md` (gates 1–4)
- `Plan/000-overview.md` §2.4 (Code Mode classification — the eager-anchor budget stays narrow)
- `Plan/_lessons-learned/14-token-consumption-postmortem.md` §1 (`pull_request_read` lack of cache-coherent reads is analogous to what this spec fixes for context)
- Spec dependency: `Plan/008-codemode-registry/spec.md` (`always_eager` classification)
- Spec dependency: `Plan/104-tool-search-anchor-triad/spec.md` (the hidden-by-default filter that lets `context_changes` ride free)
- Spec dependency: `Plan/111-context-mode-manifest/spec.md` (manifest with sha256 + last_modified — the watcher's input)
- Spec dependency: `Plan/112-context-anchor-triad/spec.md` (the `context_read` path being cached + the resource URIs being notified)
- Spec sibling: `Plan/107-cache-breakpoint-ordering/spec.md` (prompt-cache breakpoint placement; this spec's eager-tool overhead is the constraint)
- MCP Resources subscriptions: https://modelcontextprotocol.io/specification/2025-06-18/server/resources
- FastMCP resource API: https://gofastmcp.com/servers/resources
