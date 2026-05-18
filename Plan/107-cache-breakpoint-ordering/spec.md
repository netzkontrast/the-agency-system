---
spec_id: 107
slug: cache-breakpoint-ordering
status: ready
owner: jules
depends_on: [008]
affects:
  - servers/agency-mcp/src/agency_mcp/server.py
  - servers/agency-mcp/src/agency_mcp/lib/codemode/cache.py
  - tests/integration/test_cache_breakpoint.py
  - Plan/000-overview.md
source-repos: []
estimated_jules_sessions: 1
domain: cross
wave: C
---

> **Jules: read `Plan/JULES_PROTOCOL.md` before starting.** Run gates 1→4 in order:
> (1) Confidence ≥ 0.90, (2) TDD Red-Green-Refactor, (3) Evidence pasted under `## Evidence`, (4) Self-Review answered.
> Branch: `claude/agency-plugin-refactor-PgMQ4`. Only modify paths under `affects:` below.
> Source repos under `source-repos:` are clone-and-read-only into `~/work/vendor/`; never commit them.
> If anything is ambiguous, open a draft PR labelled `[BLOCKED: clarification]` and stop — do not guess.

# Spec 107 — Cache Breakpoint Ordering & TTL Pinning

## Why

Anthropic's prompt caching for tool definitions dropped its **default TTL from 1 hour to 5 minutes in January 2026** (see reference). Our watcher cadence (`jules-bulk` poll, lyric-reviewer auto-rerun, mastering qc loops) routinely exceeds 5 minutes between turns, so we are silently re-paying the full tools-schema prefix on every turn. The fix is two-fold: (1) **pin** `ttl: "1h"` on the cache breakpoint that sits between the stable anchor tools and the deferred bulk tools, and (2) **reorder** FastMCP registration so the breakpoint lands at the exact boundary `anchor tools → plugin_help → [CACHE BREAKPOINT, ttl=1h] → deferred bulk tools`. Expected saving: **30-50% on watcher-loop turns**.

## Done When

- [ ] `agency_mcp.lib.codemode.cache.CACHE_BREAKPOINT` constant declares `{"type": "cache_control", "ttl": "1h"}` per Anthropic's documented schema.
- [ ] `agency_mcp.lib.codemode.cache.install_breakpoint(mcp, after_tools: list[str])` mutates the MCP server's tool-publication order so the breakpoint follows the named tools.
- [ ] In `server.py`'s `register_all(mcp)`, the call ordering is: anchor triad → `plugin_help` → `install_breakpoint(mcp, after_tools=["agency_tool_search","agency_tool_describe","agency_tool_invoke","plugin_help"])` → deferred bulk handlers.
- [ ] `Plan/000-overview.md` §2.4 (or new §2.6) documents the registration ordering rule and the 1h TTL choice with a sentence linking to the Jan-2026 default change.
- [ ] `pytest -x tests/integration/test_cache_breakpoint.py` exits 0.
- [ ] Token-budget regression: integration test asserts the breakpoint metadata appears exactly once and that its `ttl` field equals `"1h"`.

## Source clones (run first)

None — this spec configures Anthropic's documented caching protocol. The reference URL is authoritative; no vendor source to clone.

## Files

- **Create**:
  - `servers/agency-mcp/src/agency_mcp/lib/codemode/cache.py` — `CACHE_BREAKPOINT` constant + `install_breakpoint(mcp, after_tools)` helper.
  - `tests/integration/test_cache_breakpoint.py` — breakpoint placement + TTL value + idempotency.
- **Modify**:
  - `servers/agency-mcp/src/agency_mcp/server.py` — reorder `register_all(mcp)` per the §Done When ordering.
  - `Plan/000-overview.md` — add a short subsection documenting the ordering rule and the Jan-2026 TTL default change.

## Approach

1. **Gate 1 — Confidence.** Read Anthropic's prompt-caching docs at the reference URL; confirm the `cache_control` schema accepts `ttl: "1h"` (it does, as of Jan 2026 — values `"5m"` and `"1h"` are both supported). Confirm Spec 008 has shipped `lib/codemode/registry.py` and Spec 104 has shipped `lib/codemode/anchor_triad.py`. List the current `register_all(mcp)` body in `server.py` to confirm the current (incorrect) ordering.
2. **Author the constant + helper.** In `cache.py`, declare `CACHE_BREAKPOINT: dict = {"type": "cache_control", "ttl": "1h"}`. Implement `install_breakpoint(mcp, after_tools: list[str]) -> None` that locates each named tool in `mcp._tools`, asserts they exist (raise `BreakpointError` listing any missing), and inserts the breakpoint metadata into the tool-publication pipeline at the right position. The exact insertion mechanism depends on Spec 008's registry surface — use its `add_cache_breakpoint(after=...)` hook if present, otherwise wrap `mcp._serialize_tools()` to splice the breakpoint into the emitted JSON list at the correct index.
3. **Reorder `register_all`.** In `server.py`, restructure `register_all(mcp)` to call, in order: (a) `register_anchor_triad(mcp)` from Spec 104, (b) `register_plugin_help(mcp)` (existing — leave untouched), (c) `install_breakpoint(mcp, after_tools=["agency_tool_search","agency_tool_describe","agency_tool_invoke","plugin_help"])`, (d) all other `register_*_handlers(mcp)` calls (music, jules, shared, novel, agentic). Add a one-line comment above the breakpoint call explaining the ordering rationale.
4. **Document the rule.** Add a subsection to `Plan/000-overview.md` (§2.6 "Cache Breakpoint Ordering") with three sentences: (1) the breakpoint sits after stable anchor tools so prefix-cache hits cover them; (2) `ttl="1h"` is pinned because the Anthropic default dropped to 5m in Jan 2026 and our watcher cadence exceeds that; (3) deferred bulk tools live *after* the breakpoint so churn in their schemas does not invalidate the anchor cache.
5. **TDD — Gate 2.** RED: write `test_cache_breakpoint.py` with four tests: `CACHE_BREAKPOINT` has `ttl == "1h"`; `install_breakpoint` raises `BreakpointError` when an `after_tools` entry is missing; the emitted tools-list contains exactly one cache-control marker and it appears after the anchor triad + plugin_help; `install_breakpoint` is idempotent (calling twice does not double-insert). Run — must fail.
6. **GREEN.** Implement `cache.py` + reorder `server.py`. Re-run; tests pass.
7. **REFACTOR.** Extract the "find index of last named tool" lookup into `_find_insertion_index(mcp, after_tools)` as a pure function for direct unit testing. Confirm no other module hard-codes `"5m"` or `"1h"` TTL values (`rg '"5m"|"1h"' servers/agency-mcp/src/agency_mcp/`).
8. **Gate 3 — Evidence.** Paste pytest output, a `python -c "from agency_mcp.server import create_mcp; m=create_mcp(); print([t.name for t in m._tools.values()][:8])"` showing the first 8 tools in order, and the breakpoint metadata excerpt from the serialised tools list into PR `## Evidence`. **Gate 4 — Self-Review.** Confirm no tool whose schema is volatile (e.g. handlers under active iteration) was placed before the breakpoint.

## Acceptance (Gherkin)

```gherkin
# anchor: 107.1
Scenario: Cache breakpoint declares ttl=1h
  Given the cache module is importable
  When the test reads agency_mcp.lib.codemode.cache.CACHE_BREAKPOINT
  Then the dict has key "type" with value "cache_control"
  And the dict has key "ttl" with value "1h"

# anchor: 107.2
Scenario: install_breakpoint places marker after the anchor triad and plugin_help
  Given a FastMCP instance with the anchor triad and plugin_help registered
  When install_breakpoint(mcp, after_tools=["agency_tool_search","agency_tool_describe","agency_tool_invoke","plugin_help"]) is called
  And the resulting tools list is serialised
  Then exactly one cache-control marker appears in the serialised output
  And the marker appears at index 4 (immediately after plugin_help)
  And every tool at index >= 5 is a deferred bulk tool

# anchor: 107.3
Scenario: install_breakpoint raises when a named anchor tool is missing
  Given a FastMCP instance missing the plugin_help tool
  When install_breakpoint(mcp, after_tools=["agency_tool_search","plugin_help"]) is called
  Then a BreakpointError is raised
  And the error message names "plugin_help" as the missing tool

# anchor: 107.4
Scenario: install_breakpoint is idempotent under double invocation
  Given install_breakpoint has already been called once
  When install_breakpoint is called a second time with the same after_tools
  Then the serialised tools list still contains exactly one cache-control marker
  And the marker position is unchanged
```

## Out of scope

- Adding a *second* cache breakpoint deeper in the tool list (e.g. per-domain) — single breakpoint is sufficient for Wave C.
- Per-caller TTL customisation — the 1h pin is global.
- Migrating any handler schema to stabilise it — Specs 103–106 cover schema-side savings; this spec only optimises caching of whatever schemas exist.
- Measuring cache hit-rate in production — that telemetry belongs to a future observability spec.

## References

- Anthropic — Tool use with prompt caching: https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-use-with-prompt-caching
- `Plan/_lessons-learned/14-token-consumption-postmortem.md` §5 (watcher-loop turn cost)
- `Plan/JULES_PROTOCOL.md` (gates 1–4)
- `Plan/000-overview.md` §2.4 (Code Mode classification — to be extended with §2.6 by this spec)
- Spec dependency: `Plan/008-codemode-registry/spec.md` (registry surface for breakpoint insertion)
- Spec sibling: `Plan/104-tool-search-anchor-triad/spec.md` (anchor tools that the breakpoint follows)
