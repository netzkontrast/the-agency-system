---
spec_id: 114
slug: read-cache-delta-mode
status: ready
owner: jules
depends_on: [008, 108]
affects:
  - servers/agency-mcp/src/agency_mcp/lib/codemode/read_cache.py
  - servers/agency-mcp/src/agency_mcp/lib/codemode/delta_diff.py
  - servers/agency-mcp/src/agency_mcp/hooks/read_cache_hook.py
  - hooks/hooks.json
  - tests/unit/codemode/test_read_cache.py
  - tests/unit/codemode/test_delta_diff.py
  - tests/integration/test_read_cache_pretooluse.py
source-repos:
  - token-optimizer @ main
estimated_jules_sessions: 2
domain: cross
wave: B
---

> **Jules: read `Plan/JULES_PROTOCOL.md` before starting.** Run gates 1→4 in order:
> (1) Confidence ≥ 0.90, (2) TDD Red-Green-Refactor, (3) Evidence pasted under `## Evidence`, (4) Self-Review answered.
> Branch: `claude/agency-plugin-refactor-PgMQ4`. Only modify paths under `affects:` below.
> Source repos under `source-repos:` are clone-and-read-only into `~/work/vendor/`; never commit them.
> If anything is ambiguous, open a draft PR labelled `[BLOCKED: clarification]` and stop — do not guess.

# Spec 114 — Read-Cache Delta Mode (re-read returns diff only)

## Why

`token-optimizer` reports that **65% of Read calls in real sessions are re-reads** of the same file, and code-heavy sessions re-read identical files 3-17 times. Their fix — a PreToolUse hook that caches file content (≤50KB/file) and returns a unified diff against the cached snapshot on the next read — saves **~97% on the second-and-later read** (their example: 2,000-token file → 50-token diff). Our Specs 103 (view/fields projection) and 108-110 (context-mode integration) handle MCP **tool** outputs but do nothing for the built-in `Read` tool that drives Code/Plan/spec inspection. This spec ports the read-cache+delta pattern as a Code Mode middleware so every `Read` call after the first one for the same path-and-mtime returns a compact diff instead of the full body. Expected reduction: **20-30% of total session input tokens** for code-heavy work.

## Done When

- [ ] `agency_mcp.lib.codemode.read_cache.ReadCache` exposes `get(path, mtime, size) -> CachedFile | None` and `put(path, mtime, size, content) -> None`, with a per-file 50 KB cap and a 1,000-token minimum threshold below which caching is skipped.
- [ ] `agency_mcp.lib.codemode.delta_diff.compute_delta(old: str, new: str) -> DeltaResult` returns `{summary: "+N/-M", body: str, bytes: int, fallback: bool}`. Implementation MUST use Python `difflib.unified_diff` (stdlib, mirrors token-optimizer's Python plugin choice rather than the openclaw hand-rolled LCS).
- [ ] `compute_delta` falls back to `fallback=True` and empty body when either input exceeds 50,000 bytes or 2,000 lines, or when the unified diff body would exceed 1,500 chars (these mirror token-optimizer's published thresholds — see References).
- [ ] `hooks/read_cache_hook.py` runs on `PreToolUse` for the `Read` tool: on cache hit with unchanged mtime ≥ 1,000 tokens, returns `additionalContext` of shape `{kind: "delta", path, summary: "+N/-M", body: <unified diff>}` and **soft-blocks** the underlying Read (the caller can still request the full content via `view=full` arg per Spec 103's projection contract).
- [ ] Cache invalidates automatically when on-disk mtime differs from cached mtime (mtime is the ETag).
- [ ] `hooks/hooks.json` registers the new hook on the `PreToolUse` event with tool filter `Read` only.
- [ ] `pytest -x tests/unit/codemode/test_read_cache.py tests/unit/codemode/test_delta_diff.py tests/integration/test_read_cache_pretooluse.py` exits 0.
- [ ] Token-budget regression: integration test asserts a 2,000-line file re-read returns a body ≤ 10% of the original byte length on a single-line edit.

## Source clones (run first)

```bash
git clone --depth=1 https://github.com/alexgreensh/token-optimizer.git \
  ~/work/vendor/token-optimizer
```

Read-only reference. License is **PolyForm Noncommercial 1.0.0** — we do NOT copy source; we re-implement the algorithm idiomatically with `difflib`. Cite the file at `~/work/vendor/token-optimizer/openclaw/src/delta-diff.ts` in the PR Confidence table for thresholds.

## Files

- **Create**:
  - `servers/agency-mcp/src/agency_mcp/lib/codemode/read_cache.py` — in-memory + on-disk LRU cache (`~/.cache/agency-system/read-cache/`), per-path `(mtime, size, content)`.
  - `servers/agency-mcp/src/agency_mcp/lib/codemode/delta_diff.py` — `compute_delta` using `difflib.unified_diff`.
  - `servers/agency-mcp/src/agency_mcp/hooks/read_cache_hook.py` — PreToolUse hook script.
  - `tests/unit/codemode/test_read_cache.py`, `tests/unit/codemode/test_delta_diff.py`, `tests/integration/test_read_cache_pretooluse.py`.
- **Modify**:
  - `hooks/hooks.json` — register the new hook entry.
- **Move / Delete**: none.

## Approach

1. **Gate 1 — Confidence.** Verify Spec 008 (`lib/codemode/` package) and Spec 108 (`hooks/hooks.json` exists with PreToolUse wiring) have shipped. Read `~/work/vendor/token-optimizer/openclaw/src/delta-diff.ts` and `~/work/vendor/token-optimizer/openclaw/src/read-cache.ts` for thresholds (50KB, 2,000 lines, 1,500-char diff cap, 1,000-token minimum). Cite SHAs.
2. **Implement `read_cache.py`.** Two-tier cache: in-memory dict keyed by absolute path, on-disk JSON shards at `~/.cache/agency-system/read-cache/<sha1(path)>.json`. LRU eviction at 128 entries in-memory; on-disk pruned weekly via a `prune()` call. `get(path, mtime, size)` returns `None` on miss or mtime/size mismatch.
3. **Implement `delta_diff.py`.** Pure-stdlib `difflib.unified_diff(old.splitlines(), new.splitlines(), n=2)`. Reject inputs >50,000 bytes or >2,000 lines → `fallback=True`. After computing, truncate body to 1,500 chars and set `fallback=True` if truncation occurred. Return summary as `"+{added}/-{removed}"` counted from the diff lines.
4. **Author `read_cache_hook.py`.** Reads JSON event from stdin (PreToolUse contract). If tool name is not `Read`, exit 0 with no output. Otherwise: resolve absolute path, stat it, look up cache. On hit + unchanged mtime + body ≥ 1,000 tokens, write to stdout a JSON `{action: "additionalContext", additionalContext: {kind: "delta", path, summary, body, truncated_marker: <bool>}}` and exit 0 — the Read call still proceeds (soft block; see token-optimizer README §Smart Compaction "soft-block mode"). On miss, exit 0 with no output (lets Read proceed normally); on PostToolUse re-entry (separate hook), populate the cache.
5. **Wire hooks.json.** Add a `PreToolUse` entry filtering `Read`, command spawns `python servers/agency-mcp/src/agency_mcp/hooks/read_cache_hook.py`. Coexists with Spec 108's `context-mode` and `context_mode_sync.py` entries.
6. **Add PostToolUse companion.** A second hook entry under `PostToolUse` (same script with `--mode populate` arg) reads the captured Read result and calls `ReadCache.put(...)` so the next read sees the cached content.
7. **TDD — Gate 2.** RED: write three test files — unit tests for cache hit/miss/mtime-invalidation; unit tests for delta_diff size limits, fallback behaviour, summary counting; integration test that pipes a synthetic PreToolUse event through `read_cache_hook.py` and asserts the stdout shape. Run — must fail.
8. **GREEN.** Implement until tests pass.
9. **REFACTOR.** Extract `_ResolvedPath` dataclass to share between cache + hook. Confirm no `shell=True` and no third-party imports (token-optimizer's stdlib-only invariant).
10. **Gate 3 — Evidence.** Paste pytest output. Paste the byte-size delta on a 2,000-line fixture file before/after a single-line edit. **Gate 4 — Self-Review.** Flag any file types intentionally skipped (e.g. binary files, files <1,000 tokens, partial-range reads — match token-optimizer's documented fallback conditions).

## Acceptance (Gherkin)

```gherkin
# anchor: 111.1
Scenario: First read of a large file populates the cache
  Given a 2,000-token Python file at /tmp/foo.py
  And the read-cache is empty
  When the agent invokes the Read tool on /tmp/foo.py
  Then the PostToolUse hook stores (path, mtime, size, content) in the cache
  And the in-memory cache size increases by exactly 1

# anchor: 111.2
Scenario: Re-read returns a unified diff via additionalContext
  Given /tmp/foo.py was Read once and cached
  And /tmp/foo.py has been edited (one line changed)
  When the agent invokes the Read tool on /tmp/foo.py again
  Then the PreToolUse hook emits additionalContext of kind="delta"
  And the diff body summary matches the regex ^\+\d+/-\d+$
  And the body byte length is ≤ 10% of the file's full byte length

# anchor: 111.3
Scenario: Files below the minimum threshold bypass the cache
  Given a 50-line shell script (≤1,000 tokens) at /tmp/run.sh
  When the agent Reads /tmp/run.sh twice
  Then neither read produces additionalContext from the read-cache hook
  And the cache contains no entry for /tmp/run.sh

# anchor: 111.4
Scenario: Mtime change invalidates the cache
  Given /tmp/foo.py is cached with mtime T0
  And /tmp/foo.py has been touched (mtime advances to T1)
  When the agent Reads /tmp/foo.py again
  Then the cache lookup misses on mtime mismatch
  And the next PostToolUse repopulates the cache with the new content
```

## Out of scope

- Block-mode (refuse the full re-read entirely) — we ship soft-block only; the caller can always request full content. A future spec may add a `view=full` opt-out.
- Cross-session persistence beyond `~/.cache/agency-system/read-cache/` — no SQLite trends.db.
- Caching of MCP tool outputs (Specs 108/110 own that axis via context-mode).
- Cache prefix manipulation or interaction with the cache breakpoint (Spec 107 owns that).
- AST/skeleton extraction for very large files (Spec 112 covers that — distinct path).
- License flag: token-optimizer is PolyForm Noncommercial 1.0.0. We re-implement the algorithm with stdlib `difflib`; we do NOT copy code. If we ever vendor the file verbatim, this clause MUST be revisited.

## References

- token-optimizer README (claims): "65% of Read calls are re-reads", "97% savings on specific read" — https://github.com/alexgreensh/token-optimizer/blob/main/README.md
- token-optimizer delta algorithm: `~/work/vendor/token-optimizer/openclaw/src/delta-diff.ts` (50KB / 2,000-line / 1,500-char thresholds)
- token-optimizer read-cache: `~/work/vendor/token-optimizer/openclaw/src/read-cache.ts`
- Python stdlib: https://docs.python.org/3/library/difflib.html#difflib.unified_diff
- `Plan/JULES_PROTOCOL.md` — gates 1–4
- Spec dependency: `Plan/008-codemode-registry/spec.md` (lib/codemode/ package root)
- Spec dependency: `Plan/108-context-mode-integration/spec.md` (hooks.json wiring conventions)
- Spec sibling: `Plan/115-structure-map-ast/spec.md` (complementary AST skeleton path for >2,000-line files)
- Spec sibling: `Plan/117-tool-result-archive/spec.md` (>4KB tool outputs go to disk; this spec handles file-content reads)
