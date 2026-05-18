---
spec_id: 104
slug: tool-search-anchor-triad
status: ready
owner: jules
depends_on: [008]
affects:
  - servers/agency-mcp/src/agency_mcp/lib/codemode/anchor_triad.py
  - servers/agency-mcp/src/agency_mcp/codemode/manifest.json
  - servers/agency-mcp/src/agency_mcp/server.py
  - tests/integration/test_anchor_triad.py
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

# Spec 104 — Anchor-Triad Tool Discovery (Atlassian mcp-compressor pattern)

## Why

The unified agency-mcp now exposes ~180 tools across music/jules/novel/shared/agentic domains. Every Claude turn pays the full `tools/list` payload — measured at ~38k tokens on a cold start (`Plan/_lessons-learned/14-token-consumption-postmortem.md` §3). Atlassian's mcp-compressor pattern collapses this to **three eager anchor tools** (`agency_tool_search`, `agency_tool_describe`, `agency_tool_invoke`); the bulk tools register with `defer_schema=True` AND a new `hidden=True` flag, so they're invocable via the triad but absent from `tools/list`. Expected saving: **60-90% on tools/list payload**. The triad composes naturally with Spec 008's registry (which already classifies tools by domain + lifecycle).

## Done When

- [ ] `agency_tool_search(query: str, domain: str | None = None) -> list[ToolStub]` returns ≤ 20 ranked tool stubs (name + 1-line description) matching the query.
- [ ] `agency_tool_describe(name: str) -> ToolSchema` returns the full JSON-Schema for the named tool (the schema the bulk tool would have published).
- [ ] `agency_tool_invoke(name: str, args: dict) -> Any` proxies to the underlying tool, validating args against its schema.
- [ ] The FastMCP registry honours a new `hidden: bool = False` flag on `@mcp.tool(...)`; hidden tools are excluded from `tools/list` but reachable via `agency_tool_invoke`.
- [ ] All non-anchor bulk tools register with both `defer_schema=True` and `hidden=True`.
- [ ] `tools/list` returns exactly 3 entries (the triad) plus any allow-listed always-eager tools declared in `manifest.json`.
- [ ] `pytest -x tests/integration/test_anchor_triad.py` exits 0.
- [ ] Token-budget regression: integration test asserts `len(json.dumps(tools_list))` is < 4000 bytes.

## Source clones (run first)

```bash
git clone --depth=1 https://github.com/atlassian-labs/mcp-compressor.git \
  ~/work/vendor/mcp-compressor
```

Read-only reference for the search-ranking + describe-shape contract. Never commit.

## Files

- **Create**:
  - `servers/agency-mcp/src/agency_mcp/lib/codemode/anchor_triad.py` — `register_anchor_triad(mcp)` + ranking helper.
  - `tests/integration/test_anchor_triad.py` — tools/list payload size + triad round-trip.
- **Modify**:
  - `servers/agency-mcp/src/agency_mcp/codemode/manifest.json` — add `always_eager: []` list and `hidden_by_default: true` flag.
  - `servers/agency-mcp/src/agency_mcp/server.py` — register the triad first, then iterate all other registrations with `hidden=True` defaulted on.

## Approach

1. **Gate 1 — Confidence.** Verify Spec 008 has shipped `lib/codemode/registry.py` with `defer_schema` plumbing. Clone the Atlassian repo and skim its `search.py` ranking logic (BM25 over name + description). Confirm FastMCP allows a custom `hidden` kwarg on `@mcp.tool` — if not, plan a small monkey-patch in `anchor_triad.py` that filters `mcp._tools` on list serialisation.
2. **Extend the registry with `hidden`.** In `lib/codemode/registry.py` (touch via Spec 008's facade — but no edit there; we read-only consume it), wrap registration in `anchor_triad.py`: provide `hidden_tool(mcp, **kwargs)` that calls `mcp.tool(**kwargs, defer_schema=True)` and tags the resulting tool with `_hidden=True` on its FastMCP descriptor.
3. **Implement `agency_tool_search`.** Score each registered tool by `bm25(query, tool.name + " " + tool.description)`. Filter by `domain` tag if provided (e.g. `domain=music` matches tools tagged `domain:music`). Return the top 20 as `[{"name": ..., "description": ...}]`.
4. **Implement `agency_tool_describe`.** Look up the tool by name in `mcp._tools`. Return its full JSON-Schema (the same schema the bulk tool would have shipped if it weren't deferred). Raise `ToolNotFound` if absent or if `_hidden` is set and the caller has no permission (no permission model yet — accept any caller in Wave B).
5. **Implement `agency_tool_invoke`.** Validate `args` against the schema (`jsonschema.validate`), then dispatch via FastMCP's internal `_call_tool(name, args)`. Forward the result unchanged. Errors propagate as structured `ToolInvocationError`.
6. **Patch tools/list serialisation.** In `server.py`, after `create_mcp()`, install a serialiser hook that filters out `t for t in mcp._tools.values() if getattr(t, "_hidden", False)` — except for names in `manifest.json:always_eager`.
7. **Migrate registrations.** Walk every `@mcp.tool(...)` call in `handlers/**/*.py` (do **not** edit those files in this spec — only edit `server.py`'s wrapper). In `server.py`'s `register_all(mcp)`, wrap FastMCP's `tool` decorator: default `hidden=True` and `defer_schema=True` for everything outside the always-eager list (the triad itself + `plugin_help`).
8. **TDD — Gate 2.** RED: write `test_anchor_triad.py` with five tests: tools/list returns ≤ 3 entries + `always_eager`; tools/list payload < 4000 bytes; `agency_tool_search("create_track")` returns `music_create_track` in top 5; `agency_tool_describe("music_create_track")` returns a valid JSON-Schema; `agency_tool_invoke("music_create_track", {...})` round-trips. Run — must fail.
9. **GREEN + REFACTOR.** Implement the triad and the server.py patch. Re-run; tests pass. Refactor: extract `_score_tool` into a pure function to keep the search handler testable in isolation.
10. **Gate 3 — Evidence.** Paste `pytest -x tests/integration/test_anchor_triad.py` output, `python -c "from agency_mcp.server import create_mcp; import json; m=create_mcp(); print(len(json.dumps([t.name for t in m._tools.values() if not getattr(t,'_hidden',False)])))"`, and tools/list byte-size delta (before vs after). **Gate 4 — Self-Review.** Flag any tool that had to stay always-eager (e.g. `plugin_help`) with rationale.

## Acceptance (Gherkin)

```gherkin
# anchor: 104.1
Scenario: tools/list payload contains only the anchor triad plus always-eager allowlist
  Given the unified agency-mcp is running with hidden_by_default=true
  When the operator queries the MCP tools/list endpoint
  Then the response contains the names {"agency_tool_search", "agency_tool_describe", "agency_tool_invoke"}
  And every other tool in the response is listed in manifest.json:always_eager
  And the total payload byte-size is less than 4000

# anchor: 104.2
Scenario: agency_tool_search returns matching tools by domain
  Given the music handlers are registered as hidden=True
  When the caller invokes agency_tool_search(query="create track", domain="music")
  Then the response includes a tool whose name is "music_create_track"
  And the response contains at most 20 entries
  And every entry has only the fields {"name", "description"}

# anchor: 104.3
Scenario: agency_tool_describe returns the full JSON schema of a hidden tool
  Given music_create_track is registered with hidden=True
  When the caller invokes agency_tool_describe(name="music_create_track")
  Then the response is a valid JSON Schema object
  And the response contains an "input_schema" or equivalent properties field

# anchor: 104.4
Scenario: agency_tool_invoke proxies to a hidden tool and validates args
  Given music_create_track is registered with hidden=True
  When the caller invokes agency_tool_invoke(name="music_create_track", args={...valid args...})
  Then the call dispatches to the underlying handler
  And the response is the handler's normal return value
  And invalid args raise ToolInvocationError before dispatch
```

## Out of scope

- Permission model / per-caller hidden-tool ACLs (future spec).
- Editing individual handler files to add `hidden=True` per-tool — the global wrapper in `server.py` handles this uniformly.
- Replacing FastMCP's transport / schema-publication mechanism — we only filter the published list.
- BM25 tuning / synonym expansion — naive BM25 over name+description is sufficient for Wave B.

## References

- Atlassian mcp-compressor: https://github.com/atlassian-labs/mcp-compressor
- `Plan/_lessons-learned/14-token-consumption-postmortem.md` §3 (tools/list cold-start cost)
- `Plan/JULES_PROTOCOL.md` (gates 1–4)
- `Plan/000-overview.md` §2.1 #1–#2 (tool naming + tags), §2.4 (Code Mode classification)
- Spec dependency: `Plan/008-codemode-registry/spec.md` (`defer_schema=True` plumbing)
- Spec sibling: `Plan/107-cache-breakpoint-ordering/spec.md` (cache breakpoint pinned after the triad)
