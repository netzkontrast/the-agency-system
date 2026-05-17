---
spec_id: 108
slug: context-mode-integration
status: ready
owner: jules
depends_on: [002, 008, 100]
affects:
  - .claude-plugin/plugin.json
  - .mcp.json
  - servers/agency-mcp/src/agency_mcp/lib/context_mode/__init__.py
  - servers/agency-mcp/src/agency_mcp/lib/context_mode/bridge.py
  - servers/agency-mcp/src/agency_mcp/lib/context_mode/event_map.py
  - servers/agency-mcp/src/agency_mcp/handlers/shared/context_search.py
  - skills/shared/context-mode-handoff/SKILL.md
  - hooks/hooks.json
  - hooks/context_mode_sync.py
  - tests/integration/test_context_mode_bridge.py
  - tests/unit/lib/context_mode/test_event_map.py
  - docs/architecture/context-mode-integration.md
source-repos:
  - context-mode @ main  # https://github.com/mksglu/context-mode
estimated_jules_sessions: 2
domain: cross
wave: C
---

> **Jules: read `Plan/JULES_PROTOCOL.md` before starting.** Run gates 1→4 in order:
> (1) Confidence ≥ 0.90, (2) TDD Red-Green-Refactor, (3) Evidence pasted under `## Evidence`, (4) Self-Review answered.
> Branch: `claude/agency-plugin-refactor-PgMQ4`. Only modify paths under `affects:` below.
> Source repos under `source-repos:` are clone-and-read-only into `~/work/vendor/`; never commit them.
> If anything is ambiguous, open a draft PR labelled `[BLOCKED: clarification]` and stop — do not guess.

# Spec 108 — Context Mode Integration

## Why

The [`context-mode`](https://github.com/mksglu/context-mode) plugin ([context-mode.com](https://context-mode.com/)) implements a sibling pattern to FastMCP's Code Mode but at the **Claude Code hook layer**: it intercepts `PreToolUse` / `PostToolUse` / `SessionStart` / `PreCompact` / `UserPromptSubmit` events, routes large tool outputs into a sandboxed subprocess that indexes them in a local FTS5+BM25 SessionDB, and returns only summaries to the conversation. Claimed reductions: 98% on Playwright/GitHub/Access-Log dumps, 30× compression over a 50-turn session.

This is **complementary** to our Code Mode work (Spec 008) — that handles tool *schemas*; Context Mode handles tool *outputs*. Together they bracket the two largest token sinks: schema bloat at boot and payload bloat at runtime. The plugin already exists as a Claude Code marketplace install — we don't need to reimplement it; we need to wire it as a parallel layer to our `agency-system` plugin and bridge its SessionDB with Spec 100's `session-log-mcp` so we have one event canon rather than two.

## Done When

- [ ] `context-mode` plugin installed in the user's Claude Code via `/plugin marketplace add mksglu/context-mode` documented in `docs/architecture/context-mode-integration.md`.
- [ ] `hooks/hooks.json` declares the 5 hook entry points (`PreToolUse`, `PostToolUse`, `SessionStart`, `PreCompact`, `UserPromptSubmit`) and dispatches to both `context-mode` AND our `hooks/context_mode_sync.py` mirror script — both fire; ours forwards a copy of every PostToolUse event into the Spec 100 `session_log_record` MCP tool.
- [ ] `lib/context_mode/event_map.py` defines the 26 canonical event categories from context-mode's spec (prompts, tracked files, project rules, decisions, git ops, errors/fixes, environment, session mode, tool patterns, …) mapped to Spec 100's event schema. Bidirectional translation `event_map.from_context_mode(ev) -> SessionLogEvent` + `event_map.to_context_mode(ev) -> ContextModeEvent`.
- [ ] `handlers/shared/context_search` exposes `shared_context_search(query, kind?, since?)` — wrapper over the bridged SessionDB queries via `context-mode`'s `/ctx-insight` HTTP endpoint (127.0.0.1, local-only).
- [ ] `skills/shared/context-mode-handoff/SKILL.md` documents the "Think in Code" pattern: when a tool would return >2 KB, prefer `ctx_execute` over direct call. Skill includes the 4 canonical examples from context-mode.com (filesystem walk, log filter, JSON query, git log).
- [ ] `tests/integration/test_context_mode_bridge.py` verifies: (a) hooks.json schema parses, (b) `context_mode_sync.py` PostToolUse forwards an event into session-log-mcp within 500 ms, (c) round-trip `from_context_mode → to_context_mode` is identity for all 26 categories.
- [ ] `tests/unit/lib/context_mode/test_event_map.py` covers each of the 26 mappings with a fixture event.
- [ ] `docs/architecture/context-mode-integration.md` includes the lifecycle diagram showing both plugins listening to the same hooks, with arrows for which side owns which event class.
- [ ] No source code from `context-mode` is copied into our tree. We only consume its hook contract and its `/ctx-insight` HTTP surface. Vendor source under `~/work/vendor/context-mode/` per JULES_PROTOCOL §4.

## Source clones (run first)

```bash
git clone --depth=1 --branch=main \
  https://github.com/mksglu/context-mode.git \
  ~/work/vendor/context-mode
```

If the marketplace install path has changed since this spec was written, open `[BLOCKED: verify-marketplace-handle]` per `Plan/SOURCES.md` and pause. Do not guess the package handle.

## Files

- **Create**:
  - `.mcp.json` and `.claude-plugin/plugin.json` updates that declare `context-mode` as a recommended companion plugin (note in `description`; do NOT add it as a hard dep).
  - `servers/agency-mcp/src/agency_mcp/lib/context_mode/__init__.py` — re-exports `bridge` + `event_map`.
  - `servers/agency-mcp/src/agency_mcp/lib/context_mode/bridge.py` — thin HTTP client for `/ctx-insight`, retry + 200 ms timeout, returns typed `ContextModeEvent` dataclasses.
  - `servers/agency-mcp/src/agency_mcp/lib/context_mode/event_map.py` — the 26-category mapping table and the two-way translator.
  - `servers/agency-mcp/src/agency_mcp/handlers/shared/context_search.py` — the new `shared_context_search` tool (≤120-char docstring; `tags={"domain:shared"}`).
  - `skills/shared/context-mode-handoff/SKILL.md` — Think-in-Code skill with frontmatter per JULES_PROTOCOL §C.
  - `hooks/hooks.json` — 5-hook configuration.
  - `hooks/context_mode_sync.py` — the synchronous Spec-100 sink script (CLI-invokable from `hooks.json`).
  - `tests/integration/test_context_mode_bridge.py`, `tests/unit/lib/context_mode/test_event_map.py`.
  - `docs/architecture/context-mode-integration.md` — the integration diagram + the "where to add a new event category" runbook.
- **Modify**: none (Spec 100 already ships `session_log_record`).
- **Move / Delete**: none.

## Approach

1. **Gate 1 — Confidence.** Verify Spec 100 (`servers/session-log-mcp/`) has shipped and exposes `session_log_record(kind, payload, …)`. Verify context-mode's GitHub repo at the stated URL still exists and exposes the 5-hook contract documented in its README (cite SHA in PR Confidence table).
2. **Clone source.** Run the clone command above. Read `~/work/vendor/context-mode/HOOKS.md` (or equivalent) to enumerate the 26 event categories. Read `~/work/vendor/context-mode/CTX_INSIGHT.md` for the `/ctx-insight` HTTP API shape.
3. **Author `event_map.py`.** Define a `Mapping = TypedDict('Mapping', {'ctx_kind': str, 'session_log_kind': str, 'payload_transform': Callable[[dict], dict]})` and enumerate all 26 entries. Include a `mappings()` accessor returning the immutable list.
4. **Author `bridge.py`.** Pure-stdlib HTTP client (`urllib.request`) for `http://127.0.0.1:<port>/ctx-insight/events?since=…&kind=…`. Defensive: 200 ms connect timeout, on failure return empty list + log via `session_log_record(kind="bridge_error", …)`. Never let bridge failures break the orchestrator.
5. **Author `context_mode_sync.py`.** Reads a JSON event from stdin (the `hooks.json` calling convention), translates via `event_map.from_context_mode`, calls `session_log_record` via direct in-process import (the MCP server may not be live in the hook subprocess; fall back to writing to `~/.agency-system/session-log/inbox/<uuid>.json` if the import fails).
6. **Author `hooks.json`.** Wire all 5 hook entry points. Each event spawns BOTH `context-mode`'s default handler AND our `context_mode_sync.py`. Order doesn't matter — they're independent sinks.
7. **Wire `shared_context_search` tool.** Register on the unified FastMCP per overview §2.1: `tags={"domain:shared"}`, snake_case `shared_context_search`, `list_*` cap rules (overview §2.1 #6 — cap at 20 items + opaque cursor).
8. **Author the skill.** `skills/shared/context-mode-handoff/SKILL.md` with L1 Vault Core + L2 `skill_*` namespace per JULES_PROTOCOL §C. Include the four canonical Think-in-Code examples (filesystem walk, log filter, JSON query, git log) verbatim from context-mode.com with the URL cited.
9. **TDD — Gate 2.** Write the bridge + event-map tests RED first (assert each of 26 mappings round-trips identity; assert bridge gracefully returns `[]` when `/ctx-insight` is offline). Then implement until GREEN.
10. **Gate 3 — Evidence.** Paste `pytest -x tests/unit/lib/context_mode/ tests/integration/test_context_mode_bridge.py` output. Paste `python -c "from agency_mcp.lib.context_mode.event_map import mappings; print(len(mappings()))"` output (must be 26). Paste `python hooks/context_mode_sync.py < tests/fixtures/sample_post_tool_use.json` exit code (must be 0).
11. **Gate 4 — Self-Review.** Answer the 3 questions. Specifically flag any 1-of-26 event category whose mapping required inventing a new `session_log_kind` not yet in Spec 100, and propose patching Spec 100 instead of stretching the mapping.

## Acceptance (Gherkin)

```gherkin
# anchor: 108.1
Scenario: 5 hooks declared and dispatch to both sinks
  Given hooks/hooks.json is parsed
  When the operator counts hook entries by name
  Then exactly 5 hooks are declared (PreToolUse, PostToolUse, SessionStart, PreCompact, UserPromptSubmit)
  And every hook entry references at minimum two commands — context-mode's handler and hooks/context_mode_sync.py

# anchor: 108.2
Scenario: All 26 event categories map cleanly
  Given lib/context_mode/event_map.mappings() returns a list of 26 entries
  When the operator round-trips each entry through from_context_mode → to_context_mode
  Then for every category the resulting ContextModeEvent equals the input (kind preserved, payload preserved or canonically reformatted)

# anchor: 108.3
Scenario: Bridge fails gracefully when /ctx-insight is offline
  Given the /ctx-insight HTTP endpoint is unreachable
  When the agent calls shared_context_search(query="foo")
  Then the tool returns {ok: True, results: [], warnings: ["bridge_unavailable: <reason>"]}
  And an event of kind="bridge_error" is recorded in session-log via session_log_record

# anchor: 108.4
Scenario: PostToolUse hook forwards into session-log within 500 ms
  Given a fixture PostToolUse event at tests/fixtures/sample_post_tool_use.json
  When the operator pipes the fixture into hooks/context_mode_sync.py
  Then the script exits 0 within 500 ms
  And session_log_query(filters={"kind": "tool_invocation"}, limit=1) returns the new event with matching tool_name and timestamp
```

## Out of scope

- Re-implementing context-mode's sandboxed subprocess executor in Python. We integrate; we do not duplicate.
- Spec 109/110 territory: deeper Think-in-Code routing for our FastMCP tools (route `mcp__github__pull_request_read` through `ctx_execute` semantics) — that's a follow-up spec.
- Replacing Spec 106 (`gh_pr_summary` subagent wrappers). Spec 106 stays — it's the in-FastMCP version; this spec is the at-the-hook-layer version. They coexist.
- Auto-installing context-mode for users. We document the marketplace handle; the install remains opt-in.
- Forking context-mode. We are not maintaining a fork; vendor source is read-only.

## References

- `Plan/JULES_PROTOCOL.md` — gates 1–4 + §4 source-repo discipline + §C skill best practices
- `Plan/000-overview.md` §2.1 (FastMCP conventions: tool naming + tags + list-cap)
- `Plan/100-session-log-mcp/spec.md` — the SessionLog event schema this spec bridges into
- `Plan/008-codemode-registry/spec.md` — Code Mode (schema deferral). Context Mode is the complementary half.
- `Plan/106-github-mcp-summary-wrappers/spec.md` — in-process subagent wrappers; this spec is the at-the-hook-layer complement
- `Plan/_lessons-learned/14-token-consumption-postmortem.md` — `pull_request_read` as the #1 token sink, motivation for the at-the-hook layer
- Vendor source (read-only): `~/work/vendor/context-mode/`
- Canonical doc: <https://context-mode.com/>
- Source repo: <https://github.com/mksglu/context-mode>
- License note: context-mode is Elastic License 2.0 — verify compatibility with any redistribution we do; we ship neither its code nor a fork, only a config that points at it.
