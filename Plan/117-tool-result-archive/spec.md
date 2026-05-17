---
spec_id: 117
slug: tool-result-archive
status: ready
owner: jules
depends_on: [008, 100, 108]
affects:
  - servers/agency-mcp/src/agency_mcp/lib/codemode/result_archive.py
  - servers/agency-mcp/src/agency_mcp/handlers/shared/archive.py
  - servers/agency-mcp/src/agency_mcp/hooks/archive_hook.py
  - hooks/hooks.json
  - tests/unit/codemode/test_result_archive.py
  - tests/unit/shared/test_archive_handler.py
  - tests/integration/test_archive_posttooluse.py
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

# Spec 117 — Tool Result Archive (>4 KB outputs → disk + inline hint + `expand` retrieval)

## Why

token-optimizer's most general-purpose compression mechanism: **any tool output above 4 KB is automatically archived to disk; the conversation sees a short preview plus an inline hint `[Full result archived (12,400 chars). Use 'expand abc123' to retrieve.]`**. The model retrieves the full body on demand via an `expand <id>` command. This is **complementary** to:
- Spec 106 (per-tool subagent wrappers for GitHub) — those collapse fixed-shape PR/issue calls; this archives **anything**.
- Spec 108 (context-mode) — that re-routes large tool outputs into an FTS5 index for semantic search; archive is a simpler "store-and-pointer" pattern that doesn't require the context-mode plugin.
- Spec 113 (bash compression) — that rewrites bash output in-place; archive kicks in when the rewritten output is still >4 KB.

The result: a session-wide guardrail that nothing exceeds 4 KB in the model's context unless the model explicitly asks for it.

## Done When

- [ ] `agency_mcp.lib.codemode.result_archive.ResultArchive` exposes `store(payload: str, meta: dict) -> str` (returns short archive id, e.g. 8-char base32 like `abc12345`) and `load(archive_id: str) -> ArchiveEntry | None`.
- [ ] Archive entries persist at `~/.cache/agency-system/archive/<YYYY>/<MM>/<DD>/<id>.json` with `{id, created_at, meta: {tool_name, session_id, original_bytes}, payload}`.
- [ ] Threshold: ≥ 4 KB **after** Spec 113's bash-compress and Spec 106's subagent wrappers have had their chance. The archive hook MUST run **last** in the PostToolUse chain.
- [ ] Inline-hint replacement format mirrors token-optimizer exactly: the original `tool_result` payload is replaced with `<preview first 200 chars>...\n\n[Full result archived ({original_bytes} chars). Use 'expand {id}' to retrieve.]`.
- [ ] `shared_archive_expand(archive_id: str) -> ArchiveEntry` MCP tool returns the stored payload. Snake_case, ≤120-char docstring, `tags={"domain:shared"}`. The model uses this when it needs the body.
- [ ] `shared_archive_list(session_id: str | None = None, limit: int = 20) -> list[ArchiveStub]` lists recent archives (`limit` capped at 100). Always-eager (not deferred — the model needs to discover ids).
- [ ] `pytest -x tests/unit/codemode/test_result_archive.py tests/unit/shared/test_archive_handler.py tests/integration/test_archive_posttooluse.py` exits 0.
- [ ] Token-budget regression: integration test asserts that a 12,000-char synthetic tool result is replaced in-context with a hint ≤ 400 chars, and `shared_archive_expand` round-trips the original byte-for-byte.

## Source clones (run first)

```bash
git clone --depth=1 https://github.com/alexgreensh/token-optimizer.git \
  ~/work/vendor/token-optimizer
```

License: PolyForm Noncommercial 1.0.0. Read-only reference for the archive id format and inline-hint string. We do NOT copy source — re-implement in Python with stdlib only.

## Files

- **Create**:
  - `servers/agency-mcp/src/agency_mcp/lib/codemode/result_archive.py` — `ResultArchive`, `ArchiveEntry`, `ArchiveStub`.
  - `servers/agency-mcp/src/agency_mcp/handlers/shared/archive.py` — `shared_archive_expand`, `shared_archive_list` MCP tools.
  - `servers/agency-mcp/src/agency_mcp/hooks/archive_hook.py` — PostToolUse hook (runs last).
  - `tests/unit/codemode/test_result_archive.py`, `tests/unit/shared/test_archive_handler.py`, `tests/integration/test_archive_posttooluse.py`.
- **Modify**:
  - `hooks/hooks.json` — append archive_hook to PostToolUse chain **after** bash_compress_hook and after context-mode/agency hooks (it sees the already-compressed payload).
- **Move / Delete**: none.

## Approach

1. **Gate 1 — Confidence.** Verify Specs 008 + 100 + 108 + 113 have shipped. Confirm `hooks.json` already has a PostToolUse chain where order is honoured (it is — hooks fire in file order per Anthropic's hook contract). Note the 4 KB threshold from token-optimizer README. Cite SHA.
2. **Implement `ResultArchive`.** id generation: `base32(secrets.token_bytes(5))[:8].lower()` (40-bit space, ~10¹² collisions at session scale). On `store(payload, meta)`: ensure date-sharded directory exists, write `{id, created_at: ISO-8601, meta, payload}` as JSON, return id. On `load(id)`: glob `~/.cache/agency-system/archive/**/<id>.json`, return parsed entry or `None`.
3. **Implement the two MCP tools.** `shared_archive_expand(archive_id)` validates id format `^[a-z0-9]{8}$`, calls `ResultArchive.load`, returns the `ArchiveEntry` dict. `shared_archive_list(session_id, limit)` scans the last 7 days of archive shards, filters by session_id if provided, sorts by `created_at` desc, returns ≤ `limit` stubs (`{id, created_at, tool_name, original_bytes}`). Cap `limit` at 100. Both tools register with `tags={"domain:shared"}` and **opt out of Spec 104's hidden-by-default** (declared in `manifest.json:always_eager` so the model can discover them).
4. **Author `archive_hook.py`.** Read PostToolUse JSON event from stdin. Compute `payload_bytes`. If < 4,096 → exit 0 silently. Else: generate id, call `ResultArchive.store(payload, meta)`, emit `updatedOutput` JSON on stdout replacing the original tool result with the preview-plus-hint format. The hint format string MUST exactly equal: `f"{payload[:200]}...\n\n[Full result archived ({payload_bytes} chars). Use 'expand {id}' to retrieve.]"`.
5. **Wire hooks.json ordering.** Archive hook appears **last** in PostToolUse chain. Order: bash_compress_hook → context-mode handler → context_mode_sync (Spec 108) → archive_hook. Document this rule in the file header comment.
6. **Skip-list configuration.** Some tool names should bypass archiving (the new `shared_archive_expand` itself, `shared_archive_list`, `agency_tool_search`, `plugin_help`). Maintain `ARCHIVE_SKIP_TOOLS: frozenset[str]` in `archive_hook.py`; the hook checks `tool_name in ARCHIVE_SKIP_TOOLS` before proceeding.
7. **Garbage collection.** `ResultArchive.prune(older_than_days: int = 30)` deletes entries older than N days. Hook does NOT call this — it runs out-of-band via a future cron or a startup task. For this spec, just expose the method and unit-test it.
8. **TDD — Gate 2.** RED: write `test_result_archive.py` (round-trip store/load, id format, prune deletes only entries older than threshold), `test_archive_handler.py` (tools validate id format, list pagination, skip-list bypass), `test_archive_posttooluse.py` (synthetic PostToolUse JSON in, updatedOutput JSON out, original byte-for-byte recoverable via load). Run — must fail.
9. **GREEN + REFACTOR.** Implement minimally. Refactor: lift `archive_dir_for(now)` into a shared helper.
10. **Gate 3 — Evidence.** Paste pytest output, the byte-count delta on the 12K-char fixture, and a captured `shared_archive_expand` round-trip dump. **Gate 4 — Self-Review.** Document the interaction with Spec 108's context-mode: when both are active, context-mode-handled payloads are already short summaries by the time archive runs, so archive is a no-op for those — confirm this in the chain integration test.

## Acceptance (Gherkin)

```gherkin
# anchor: 114.1
Scenario: Tool output above 4 KB is archived and replaced with a hint
  Given a PostToolUse event where the tool result payload is 12,000 chars
  And the tool_name is not in ARCHIVE_SKIP_TOOLS
  When the archive_hook processes the event
  Then ResultArchive.store(...) is called once
  And the hook emits updatedOutput whose payload begins with the first 200 chars of the original
  And the payload contains the exact substring "[Full result archived (12000 chars). Use 'expand"
  And the payload contains an 8-char lowercase alphanumeric archive id

# anchor: 114.2
Scenario: Small outputs pass through unchanged
  Given a PostToolUse event where the tool result is 3,000 chars
  When the archive_hook processes the event
  Then the hook exits 0 with no stdout
  And ResultArchive.store(...) is NOT called

# anchor: 114.3
Scenario: shared_archive_expand round-trips the original payload
  Given the model has invoked a tool that produced a 50,000-char output
  And the archive_hook stored it as id "abc12345"
  When the model invokes shared_archive_expand(archive_id="abc12345")
  Then the tool returns ArchiveEntry with payload of length 50,000
  And the payload equals the original byte-for-byte

# anchor: 114.4
Scenario: Skip-list tools bypass archiving
  Given a PostToolUse event for tool_name="shared_archive_expand" with a 50,000-char payload
  When the archive_hook processes the event
  Then the hook exits 0 with no stdout (no recursive archiving)
```

## Out of scope

- Auto-pruning entries older than 30 days from the hook itself (runs out-of-band; spec exposes `prune()` only).
- Semantic search over archived payloads (Spec 108 owns that via context-mode's FTS5 index).
- Encrypting archive shards at rest — local-only cache; align with whatever the user's home-disk policy is.
- Replacing FastMCP's serialisation pipeline; we only mutate via the PostToolUse `updatedOutput` mechanism.
- License flag: token-optimizer is PolyForm Noncommercial 1.0.0. We re-implement the algorithm in Python; the inline-hint string format is small enough to qualify as fair-use interop API. If we ever vendor `archive.ts` verbatim, revisit.

## References

- token-optimizer README — "Large tool results (>4KB) get archived to disk automatically" and the literal `[Full result archived ...]` format: https://github.com/alexgreensh/token-optimizer/blob/main/README.md
- token-optimizer archive logic: `~/work/vendor/token-optimizer/openclaw/src/` and `~/work/vendor/token-optimizer/skills/token-optimizer/scripts/measure.py`
- `Plan/JULES_PROTOCOL.md` — gates 1–4 + §C skill best practices
- `Plan/000-overview.md` §2.1 (FastMCP conventions, list-cap)
- Spec dependency: `Plan/008-codemode-registry/spec.md`
- Spec dependency: `Plan/100-session-log-mcp/spec.md` (archive can log a session event on store/expand)
- Spec dependency: `Plan/108-context-mode-integration/spec.md` (PostToolUse chain conventions)
- Spec sibling: `Plan/116-bash-output-compression/spec.md` (runs before archive in PostToolUse chain)
- Spec sibling: `Plan/106-github-mcp-summary-wrappers/spec.md` (per-tool subagent wrappers; archive is the general fallback)
