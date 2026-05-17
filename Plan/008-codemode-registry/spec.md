---
spec_id: 008
slug: codemode-registry
status: ready
owner: jules
depends_on: [003, 004]
affects:
  - servers/agency-mcp/src/agency_mcp/lib/codemode/__init__.py
  - servers/agency-mcp/src/agency_mcp/lib/codemode/registry.py
  - servers/agency-mcp/src/agency_mcp/lib/codemode/deferred_loader.py
  - servers/agency-mcp/src/agency_mcp/codemode/manifest.json
  - servers/agency-mcp/src/agency_mcp/server.py
  - tests/unit/codemode/__init__.py
  - tests/unit/codemode/test_registry.py
  - tests/integration/__init__.py
  - tests/integration/test_boot_token_budget.py
source_repos: []
estimated_jules_sessions: 1
domain: cross
wave: A
---

> **Jules: read `Plan/JULES_PROTOCOL.md` before starting.** Run gates 1→4 in order:
> (1) Confidence ≥ 0.90, (2) TDD Red-Green-Refactor, (3) Evidence pasted under `## Evidence`, (4) Self-Review answered.
> Branch: `claude/agency-plugin-refactor-PgMQ4`. Only modify paths under `affects:` below.
> Source repos under `source-repos:` are clone-and-read-only into `~/work/vendor/`; never commit them.
> If anything is ambiguous, open a draft PR labelled `[BLOCKED: clarification]` and stop — do not guess.

# Spec 008 — Code Mode Registry

## Why

Once all four domains are registered, the unified plugin will expose ~180 tools (~67 music + ~73 novel + ~12 jules + ~32 agentic). Without intervention, every `tools/list` MCP call dumps every tool schema into the model's context — measured at ~34k tokens in the bitwize baseline. Code Mode + `defer_schema=True` is the FastMCP feature that solves this: ~4 anchor tools per domain register eagerly (their schemas always loaded), the rest register deferred (schema fetched on demand via `tool_search` / `get_schema` / `execute` meta-tools). The bitwize baseline target is ~315 tokens. This spec ships the classification manifest, the registry helper that decorates tools per the manifest, the graceful-fallback CodeMode import (mirroring the jules-plugin pattern), and the integration test that asserts the boot token budget. It is the single most token-impactful spec in Wave A — without it, the plugin is unusable at scale.

## Done When

- [ ] `lib/codemode/registry.py` exports `apply_codemode_manifest(mcp, manifest_path)` that decorates each registered tool per its manifest classification (`eager` / `deferred` / `background`).
- [ ] `lib/codemode/deferred_loader.py` exposes a helper that wraps a `@mcp.tool()` call with `defer_schema=True` when the classification is `deferred`.
- [ ] `codemode/manifest.json` classifies every music tool (from Spec 004) and every jules tool (from Spec 006) explicitly, plus stub `null`-classified entries for the still-unbuilt novel/agentic tool names (so missing-entry validation is meaningful).
- [ ] Anchor tools (eager): per domain, ~4 — `music_list_albums`, `music_find_album`, `music_get_track`, `music_health_check`; `jules_list`, `jules_get`, `jules_watcher_status`, `plugin_help`. The exact eager set is listed in the manifest and ≤16 total.
- [ ] Background tools (`music_master_album`, `music_polish_album`, `music_generate_promo_videos`, `jules_start_watcher`, any other long-runner) each have a `<name>_status` poll companion registered as eager.
- [ ] `server.py` calls `apply_codemode_manifest(mcp, …)` after `register_all(mcp)` and wraps the CodeMode import in `try/except ImportError` per the jules-plugin pattern (graceful fallback: if Code Mode is unavailable, all tools register eagerly with a `warnings.warn` once).
- [ ] `pytest -x tests/unit/codemode/test_registry.py` exits 0.
- [ ] `pytest -x tests/integration/test_boot_token_budget.py` exits 0 with the assertion `tools_list_tokens <= 500`.
- [ ] Code Mode meta-tools `search`, `get_schema`, `execute` are present in `mcp._tools` (asserted by the integration test) — the spec does NOT add a custom `list_tools` or `search_tools` (overview §2.1 #3).

## Source clones (run first)

None. The local reference is `jules-plugin/mcp-server/src/jules_mcp/server.py:4-5` for the CodeMode try/except import pattern. Cite that file+line range in the PR Confidence section.

Reference docs to read via WebFetch (do not clone):
- https://gofastmcp.com/servers/transforms/code-mode — for the `defer_schema` API contract and the `search` / `get_schema` / `execute` meta-tool wiring.

## Files

- **Create**:
  - `servers/agency-mcp/src/agency_mcp/lib/codemode/__init__.py` — re-exports `apply_codemode_manifest`.
  - `servers/agency-mcp/src/agency_mcp/lib/codemode/registry.py` — manifest loader + decorator application.
  - `servers/agency-mcp/src/agency_mcp/lib/codemode/deferred_loader.py` — the `defer_schema=True` wrapping helper.
  - `servers/agency-mcp/src/agency_mcp/codemode/manifest.json` — `{tool_name: {classification: "eager"|"deferred"|"background", domain: str, status_companion?: str}}` for every known tool.
  - `tests/unit/codemode/__init__.py`.
  - `tests/unit/codemode/test_registry.py` — unit tests for manifest parsing, classification, and missing-entry detection.
  - `tests/integration/__init__.py`.
  - `tests/integration/test_boot_token_budget.py` — boots the server, calls `tools/list`, asserts the JSON length-in-tokens ≤ 500.
- **Modify**:
  - `servers/agency-mcp/src/agency_mcp/server.py` — graceful CodeMode import (try/except ImportError), call `apply_codemode_manifest(mcp, …)` after `register_all(mcp)`.
- **Move / Delete**: none.

## Approach

1. **Gate 1 — Confidence.** Verify Spec 003 (StateCache) and Spec 004 (music handlers + tags) have shipped — `python -c "from agency_mcp.server import create_mcp; m=create_mcp(); print(len([t for t in m._tools if 'domain:music' in (m._tools[t].tags or set())]))"` returns ≥60. Verify `fastmcp[code-mode]>=3.1.0` is pinned (Spec 001). Read `jules-plugin/mcp-server/src/jules_mcp/server.py:4-5` and paste the import pattern into Confidence. Cite the WebFetch of the Code Mode docs (paste the `defer_schema` signature line).
2. **WebFetch Code Mode docs.** `WebFetch https://gofastmcp.com/servers/transforms/code-mode` with the prompt "Return: (a) the exact import path for CodeMode in fastmcp 3.1.x, (b) the `defer_schema` parameter signature on `@mcp.tool`, (c) the names and signatures of the auto-registered meta-tools (`search`, `get_schema`, `execute`)." Paste the answer into the PR Confidence section as the verified reference.
3. **Author the manifest.** Build `codemode/manifest.json` with entries for: (a) all music tools from Spec 004 — classify ~4 as `eager` (`music_list_albums`, `music_find_album`, `music_get_track`, `music_health_check`), known long-runners as `background` with `status_companion` pointers (`music_master_album` → `music_master_album_status`), rest as `deferred`; (b) all jules tools from Spec 006 — `jules_list`, `jules_get`, `jules_watcher_status`, `plugin_help` as `eager`; `jules_start_watcher` as `background`; rest `deferred`; (c) stub `null` entries (or `{classification: "TBD"}`) for the planned novel/agentic anchor tools (`novel_list_works`, `novel_find_work`, `agentic_list_specs`, …) so future specs only need to flip the field.
4. **Implement `registry.py`.** Function `apply_codemode_manifest(mcp, manifest_path)` reads the JSON, walks `mcp._tools`, and for each registered tool: if classification is `deferred`, re-register with `defer_schema=True`; if `background`, ensure a `<name>_status` companion is present (raise `ValueError` if missing — this catches Spec 006 / future-spec drift); if `eager`, leave as-is. For tools registered on `mcp._tools` that have no manifest entry, raise `ValueError("unclassified tool: <name>")` so missing entries fail the boot rather than silently load eagerly.
5. **Implement `deferred_loader.py`.** The helper that handles the actual `defer_schema=True` wrap. Keep it 1 function, ≤25 lines.
6. **Wire `server.py`.** Wrap `from fastmcp.experimental import CodeMode` in `try/except ImportError as e: CodeMode = None; warnings.warn(f"CodeMode unavailable: {e}; all tools eager")`. After `register_all(mcp)`, call `apply_codemode_manifest(mcp, Path(__file__).parent / "codemode" / "manifest.json")` only when `CodeMode is not None`.
7. **TDD — Gate 2.** RED: `test_registry.py` has 4 tests — `test_manifest_loads`, `test_eager_tools_keep_schema`, `test_deferred_tools_drop_schema`, `test_background_requires_status_companion`, `test_unclassified_tool_raises_value_error`. `test_boot_token_budget.py` boots the MCP, JSON-encodes the `tools/list` response, asserts `len(json_blob.encode("utf-8")) <= 2000` AND uses `tiktoken` (or a 1-char≈0.25-token heuristic if tiktoken not in deps) to assert ≤500 tokens. All tests must fail before the registry exists. GREEN: implement. REFACTOR: extract the manifest schema into a `TypedDict` if it clarifies.
8. **Token-budget enforcement.** The integration test is the single source of truth for "did we meet the ~315-token bitwize baseline target". The ≤500 token threshold is the explicit budget from Done When; if measured >500, do not raise the threshold — instead, move more tools from `eager` to `deferred` and re-run. Document any tool that was moved into the PR Self-Review.
9. **Gate 3 — Evidence.** Paste: (a) `pytest -x tests/unit/codemode/test_registry.py` output. (b) `pytest -x tests/integration/test_boot_token_budget.py` output including the printed `tools_list_tokens=<N>` line. (c) `python -c "from agency_mcp.server import create_mcp; m=create_mcp(); print([t for t in m._tools if t in ('search','get_schema','execute')])"` showing all three meta-tools present. **Gate 4 — Self-Review.** Confirm no custom `list_tools` / `search_tools` was added (§2.1 #3). List any tool whose classification was guessed without an explicit downstream-spec confirmation; flag them as `TBD` in the manifest.

## Acceptance (Gherkin)

```gherkin
# anchor: 008.1
Scenario: Boot token budget stays under 500 tokens with Code Mode active
  Given the music and jules handlers are registered per Specs 004 and 006
  And the codemode manifest classifies tools per this spec
  When the operator boots the server and inspects the tools/list response
  Then the response JSON serializes to ≤ 500 tokens (measured via tiktoken or 0.25-tokens-per-char heuristic)
  And the meta-tools "search", "get_schema", and "execute" are present in mcp._tools

# anchor: 008.2
Scenario: Every background tool has a registered _status poll companion
  Given the manifest marks N tools with classification "background"
  When apply_codemode_manifest walks the registered tool set
  Then for every background tool there exists a sibling tool named "<tool>_status"
  And if any background tool is missing its companion, apply_codemode_manifest raises ValueError

# anchor: 008.3
Scenario: CodeMode import failure falls back gracefully to eager registration
  Given the fastmcp.experimental.CodeMode import raises ImportError
  When create_mcp() is invoked
  Then no exception propagates
  And a UserWarning is emitted containing "CodeMode unavailable"
  And every tool is registered with its full schema (no defer_schema applied)
```

## Out of scope

- Adding novel or agentic handlers (Specs 011, 013, 016 — their tools will be classified by extending `manifest.json` in those specs).
- Authoring the `plugin_help` slash-cheat-sheet content (Spec 002 ships the tool; this spec only marks it eager).
- Replacing FastMCP's built-in `search` / `get_schema` / `execute` meta-tools with custom variants — explicitly forbidden by overview §2.1 #3.
- Adding telemetry / token-usage tracking beyond the integration-test assertion (future work).
- Migrating user state, overrides, or config (Specs 018, 019).

## References

- `Plan/JULES_PROTOCOL.md` (gates 1–4, §7 plugin specifics — FastMCP ≥3.1.0 + CodeMode try/except)
- `Plan/000-overview.md` §2.1 #3 (no custom list_tools/search_tools), #4 (anchor tools + defer_schema), #5 (classification + `_status` companions), §2.3 (graceful CodeMode fallback)
- `Plan/SOURCES.md` (FastMCP Code Mode doc URL)
- Spec dependencies: `Plan/003-unified-statecache-port/spec.md`, `Plan/004-music-handlers-port/spec.md`
- Spec downstream consumers: `Plan/006-jules-handlers-port/spec.md` (classified here), `Plan/011-novel-handlers-core/spec.md` and `Plan/016-agentic-handlers-and-skills/spec.md` (extend the manifest)
- Local reference: `jules-plugin/mcp-server/src/jules_mcp/server.py:4-5` (CodeMode try/except pattern)
- FastMCP Code Mode docs: https://gofastmcp.com/servers/transforms/code-mode
