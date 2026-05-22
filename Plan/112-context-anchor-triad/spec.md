---
spec_id: 112
slug: context-anchor-triad
status: ready
owner: jules
depends_on: [008, 104, 111]
affects:
  - servers/agency-mcp/src/agency_mcp/lib/codemode/__init__.py
  - servers/agency-mcp/src/agency_mcp/lib/codemode/context_anchor_triad.py
  - servers/agency-mcp/src/agency_mcp/handlers/context/__init__.py
  - servers/agency-mcp/src/agency_mcp/handlers/context/anchors.py
  - servers/agency-mcp/src/agency_mcp/handlers/context/resources.py
  - servers/agency-mcp/src/agency_mcp/codemode/manifest.json
  - servers/agency-mcp/src/agency_mcp/server.py
  - tests/unit/context/__init__.py
  - tests/unit/context/test_context_anchors.py
  - tests/integration/test_context_anchor_triad.py
  - tests/integration/test_boot_token_budget.py
source-repos: []
estimated_jules_sessions: 2
domain: cross
wave: B
---

> **Jules: read `Plan/JULES_PROTOCOL.md` before starting.** Run gates 1→4 in order:
> (1) Confidence ≥ 0.90, (2) TDD Red-Green-Refactor, (3) Evidence pasted under `## Evidence`, (4) Self-Review answered.
> Branch: `Master` (default base for fresh specs post-Wave-A; see JULES_PROTOCOL.md §3). Only modify paths under `affects:` below.
> Source repos under `source-repos:` are clone-and-read-only into `~/work/vendor/`; never commit them.
> If anything is ambiguous, open a draft PR labelled `[BLOCKED: clarification]` and stop — do not guess.

# Spec 112 — Context Anchor-Triad (`context_search` / `context_describe` / `context_read`)

## Why

Spec 111 ships the `context_manifest.json` catalogue (≥40 entries, ≥200k deferred tokens). This spec exposes that catalogue to the model through **three eager MCP tools**, mirroring Spec 104's tool-side triad (`agency_tool_search` / `agency_tool_describe` / `agency_tool_invoke`). Without this layer, the manifest is dead data: clients have no way to discover, preview, or fetch a context entry. With it, the model can stop preemptively reading 22 Plan specs + 14 lessons + the Dramatica ontology and instead `context_search("dramatica throughline") → context_describe(id) → context_read(id, view="preview")` on demand — replicating the token win Spec 008 achieved for tools, on the much larger document corpus. The triad also publishes each manifest entry as an MCP `Resource` (URI scheme `context://<id>`, MIME from the manifest) so that MCP clients which prefer the native `resources/list` + `resources/read` flow can consume the same catalogue without the wrapper. The cache-key surface is intentionally narrow: only the three anchor tools' schemas are eager, so Spec 107's cache breakpoint stays valid and prompt-cache prefixes remain stable across context fetches.

## Done When

- [ ] `context_search(query: str, *, domain: str | None = None, tags: list[str] | None = None, limit: int = 10) -> list[ContextStub]` returns ≤ `limit` (default 10, max 20) ranked entries; each stub has exactly `{id, title, summary, tags, score}`.
- [ ] `context_describe(id: str) -> ContextDescription` returns `{id, title, summary, tags, path, mime, size_bytes, last_modified, sha256, views: {summary, preview, full}}` — the full manifest entry minus the body.
- [ ] `context_read(id: str, *, view: Literal["summary","preview","full"] = "summary", fields: list[str] | None = None) -> ContextBody` returns `{id, view, mime, body, token_estimate, truncated: bool}`. For JSON manifests, `fields` projects sub-keys (e.g. `fields=["title","description"]` on `dramatica:ontology` returns only those keys) using the same projection grammar as Spec 103.
- [ ] All three tools are registered as **eager** anchors with `tags={"domain:cross", "anchor:context"}` and appear in `codemode/manifest.json:always_eager` so Spec 104's hidden-by-default filter does not strip them.
- [ ] Each manifest entry is also published as an MCP `Resource` with URI `context://<id>`, `mimeType` from the manifest, and `name`/`description` from `title`/`summary`. `resources/list` returns ≤ 4 KB of metadata per entry (no body).
- [ ] `context_read` honours the manifest's `views` byte windows exactly — `view="summary"` returns the pre-computed summary (≤ ~120 tokens), `view="preview"` returns bytes `[0, views.preview.byte_length)` of the raw file (≤ ~800 tokens), `view="full"` returns the whole file. If the requested view's token estimate would exceed 4000 tokens, the tool truncates AND sets `truncated=True` with a tail line `… [truncated; ask for fields= or read direct file]`.
- [ ] Field-projection on JSON content uses RFC-6901 JSON pointers OR dotted-key syntax (`a.b.c`), matching Spec 103's existing projection helper; reuse that helper, do not re-implement.
- [ ] `pytest -x tests/unit/context/test_context_anchors.py` exits 0.
- [ ] `pytest -x tests/integration/test_context_anchor_triad.py` exits 0 — covers round-trip search → describe → read for at least one spec, one lesson, one override, one JSON ontology entry.
- [ ] Token-budget regression: `tests/integration/test_boot_token_budget.py` is extended so `tools/list` payload AFTER Context Mode registration is **at most 1.05×** its pre-Context-Mode size (i.e. the three context anchor tools add ≤ 5% overhead) AND the integration test logs the *deferred-document* total token cost (sum of `views.full.token_estimate` across manifest entries) — the headline savings number.
- [ ] `context_read` on an unknown ID raises `ContextNotFound`; on a view that doesn't exist for that entry (e.g. asking for `preview` on a 60-byte file) returns the smaller of the next-larger or next-smaller available view and sets `view` accordingly in the response.

## Source clones (run first)

None.

Reference docs to consult via WebFetch:
- https://modelcontextprotocol.io/specification/2025-06-18/server/resources — for `resources/list`, `resources/read`, and the `Resource`/`ResourceContents` shapes.
- https://gofastmcp.com/servers/resources — for FastMCP's `@mcp.resource(uri_template)` decorator, used to publish manifest entries.

## Files

- **Create**:
  - `servers/agency-mcp/src/agency_mcp/lib/codemode/context_anchor_triad.py` — `register_context_anchor_triad(mcp, manifest)` + the three tool handlers + the BM25 ranker call into `ContextManifest.search`.
  - `servers/agency-mcp/src/agency_mcp/handlers/context/__init__.py` — exports `register_context_handlers(mcp)`.
  - `servers/agency-mcp/src/agency_mcp/handlers/context/anchors.py` — wires the three eager tools to FastMCP via `@mcp.tool` (with `tags={"domain:cross","anchor:context"}`).
  - `servers/agency-mcp/src/agency_mcp/handlers/context/resources.py` — publishes each manifest entry as an MCP resource via `@mcp.resource("context://{id}")`; `resources/list` enumerates from the manifest.
  - `tests/unit/context/__init__.py`.
  - `tests/unit/context/test_context_anchors.py` — unit tests for the three handlers in isolation, mocking the manifest.
  - `tests/integration/test_context_anchor_triad.py` — end-to-end search → describe → read across the live manifest, including the JSON-pointer projection on a JSON entry.
- **Modify**:
  - `servers/agency-mcp/src/agency_mcp/lib/codemode/__init__.py` — re-export `register_context_anchor_triad`.
  - `servers/agency-mcp/src/agency_mcp/codemode/manifest.json` — add `context_search`, `context_describe`, `context_read` to `always_eager`; classify all three with `classification: "eager"`, `domain: "cross"`, `anchor_kind: "context"`.
  - `servers/agency-mcp/src/agency_mcp/server.py` — after `register_all(mcp)` and after `apply_codemode_manifest(mcp, …)`, call `register_context_handlers(mcp)` (which internally loads `context_manifest.json` and registers both the triad and the resources). Wire BEFORE Spec 104's `register_anchor_triad(mcp)` so the context anchors are also picked up by the hidden-by-default filter.
  - `tests/integration/test_boot_token_budget.py` — extend with the ≤ 1.05× regression assertion and the deferred-document-tokens log line.

## Approach

1. **Gate 1 — Confidence.** Verify Spec 111 has shipped `lib/codemode/context_manifest.py` and a committed `context_manifest.json` with ≥ 40 entries. Verify Spec 104 has shipped `lib/codemode/anchor_triad.py` and the `hidden=True` filter on `tools/list`. Verify Spec 103's field-projection helper is importable (`agency_mcp.lib.projection.project(obj, fields)` or equivalent — read the actual export path before relying on it; if the path differs, cite it). WebFetch the two reference URLs and paste the FastMCP `@mcp.resource` signature into the PR Confidence section.
2. **Implement `context_search`.** Thin wrapper over `ContextManifest.search(query, domain=domain, tags=tags, limit=min(limit, 20))`. Return the BM25 result list unchanged. Tool description: ≤ 120 chars, single sentence, e.g. `"Search the deferred-context manifest (specs, lessons, overrides, references) by query, optionally filtered by domain or tag."`.
3. **Implement `context_describe`.** Look up by ID in `manifest.by_id`. Return the entry minus `body`/raw content — i.e. the JSON record itself. Raise `ContextNotFound` (a subclass of `ValueError` with a structured message) on unknown ID.
4. **Implement `context_read`.** Three responsibilities:
   - **View resolution.** Map `view` → byte window from `entry.views`. If the requested view is absent (small file, only `full` exists), pick the next available view and update the response's `view` field to reflect what was actually returned (do not silently lie).
   - **Body loading.** Read the file from `entry.path` (always relative to repo root; absolute paths are rejected). Slice to the byte window. For Markdown, return as a string. For JSON/YAML with `fields` set, parse, project via the Spec 103 helper, re-serialise with `indent=2`. For JSON/YAML without `fields`, return the raw bytes (sliced to the view window).
   - **Token-cap enforcement.** Estimate tokens (`tiktoken` if available, else `ceil(bytes / 4)`). If estimate > 4000, truncate the body on the nearest line boundary, append `\n\n… [truncated; ask for fields= or read direct file]`, set `truncated=True`.
   Return shape: `{"id": ..., "view": ..., "mime": ..., "body": ..., "token_estimate": int, "truncated": bool}`.
5. **Publish resources.** In `handlers/context/resources.py`, iterate the manifest at startup; for each entry register `@mcp.resource(f"context://{entry.id}", mime_type=entry.mime, name=entry.title, description=entry.summary)`. The handler body reads the file (full view) and returns its contents — clients calling `resources/read` on `context://plan:008-codemode-registry:spec` get the full file. `resources/list` MUST return only metadata (no body); FastMCP's default behaviour already does this — verify in the integration test.
6. **Update the codemode manifest.** Add the three tools to `always_eager`. Mark them `classification: "eager"`, `domain: "cross"`, `anchor_kind: "context"`. Confirm Spec 104's `hidden=True` filter passes them through (it should, because they're in `always_eager`).
7. **Wire `server.py`.** After `register_all(mcp)` and `apply_codemode_manifest(mcp, …)`, before `register_anchor_triad(mcp)`, call `register_context_handlers(mcp)`. The handlers package loads `context_manifest.json` at registration time and caches the parsed manifest in module scope (re-reading on each tool invocation would burn disk I/O; Spec 113 will add invalidation).
8. **TDD — Gate 2.** RED: write the unit tests first.
   - `test_search_returns_at_most_limit_entries` — search with `limit=3` returns ≤ 3.
   - `test_describe_includes_views_block` — describe response has `views.summary`, `views.preview`, `views.full`.
   - `test_read_summary_view_under_120_tokens` — read with `view="summary"` returns ≤ 120 estimated tokens.
   - `test_read_full_truncates_when_over_4000_tokens` — read of a large entry sets `truncated=True` and ends with the truncation marker.
   - `test_read_with_fields_projects_json` — read of a JSON entry with `fields=["meta.version"]` returns only that key.
   - `test_read_unknown_id_raises_context_not_found` — unknown ID raises.
   - `test_read_missing_view_falls_back_gracefully` — small file requested as `preview` returns whatever view is available with the response's `view` field updated.
   Then write the integration test asserting search → describe → read round-trips end-to-end and that `tools/list` payload stays within 1.05× of pre-Context-Mode size. All tests RED before implementation. GREEN: implement. REFACTOR: extract the truncation marker into a constant.
9. **Token-budget acceptance.** Extend `tests/integration/test_boot_token_budget.py` with two new assertions:
   (a) `tools_list_tokens_after_context_mode <= ceil(tools_list_tokens_before_context_mode * 1.05)` — proves the three anchors add minimal overhead.
   (b) Log line `deferred_document_tokens=<N>` where `N` = sum of `views.full.token_estimate` across manifest entries; assert `N >= 200_000` (i.e. we are actually deferring meaningful content).
10. **Gate 3 — Evidence.** Paste: (a) both pytest outputs. (b) `python -c "from agency_mcp.server import create_mcp; m=create_mcp(); print([t for t in m._tools if t.startswith('context_')])"` showing the three anchors are present. (c) `python -c "from agency_mcp.server import create_mcp; m=create_mcp(); print(len([r for r in m._resources.values() if r.uri.startswith('context://')]))"` showing ≥ 40 resources. (d) The boot-token-budget test stdout including both the `tools_list_tokens=` and `deferred_document_tokens=` lines. **Gate 4 — Self-Review.** Confirm no custom `list_tools`/`search_tools` was added (§2.1 #3 still applies; this spec adds `context_search`, NOT `tool_search`). Flag any manifest entry whose `view="preview"` slice landed mid-word — describe how the indexer in Spec 111 should be adjusted (file an issue, do not amend Spec 108).

## Acceptance (Gherkin)

```gherkin
# anchor: 109.1
Scenario: Three context anchor tools are eager and present in tools/list
  Given the unified agency-mcp is booted with Context Mode active
  When the operator queries tools/list
  Then the response contains the names {"context_search", "context_describe", "context_read"}
  And each of those three tools has the tag "anchor:context"
  And each of those three tools has the tag "domain:cross"
  And none of those three tools is filtered out by the hidden-by-default rule

# anchor: 109.2
Scenario: context_search round-trips into context_describe and context_read
  Given the context manifest contains the entry "plan:012-dramatica-and-ncp-libs:spec"
  When the caller invokes context_search(query="dramatica ontology", limit=5)
  And takes the top result id
  And invokes context_describe(id=that_id)
  And invokes context_read(id=that_id, view="summary")
  Then context_search returns at least one entry
  And context_describe returns a record with the keys {id, title, summary, tags, path, mime, size_bytes, last_modified, sha256, views}
  And context_read returns body whose token_estimate is ≤ 120
  And context_read returns truncated=false

# anchor: 109.3
Scenario: context_read enforces the 4000-token cap on the full view
  Given the manifest contains an entry whose views.full.token_estimate is > 4000
  When the caller invokes context_read(id=that_id, view="full")
  Then the response truncated field is true
  And the body ends with "… [truncated; ask for fields= or read direct file]"
  And the response token_estimate is ≤ 4100

# anchor: 109.4
Scenario: context_read with fields projects a JSON entry
  Given the manifest contains a JSON entry "reference:dramatica:ontology"
  And the underlying file has top-level keys including "version" and "classes"
  When the caller invokes context_read(id="reference:dramatica:ontology", fields=["version"])
  Then the response body parses as JSON
  And the parsed body has exactly one top-level key "version"
  And the response token_estimate is far smaller than views.full.token_estimate

# anchor: 109.5
Scenario: Manifest entries are also exposed as MCP resources
  Given the manifest contains N entries
  When the operator queries resources/list
  Then the response contains at least N entries with URIs of the form "context://<id>"
  And each entry has mimeType matching the manifest's mime field
  And resources/list payload contains no entry body content

# anchor: 109.6
Scenario: tools/list overhead from Context Mode is ≤ 5% of pre-Context-Mode size
  Given the boot-token-budget integration test has captured tools_list_tokens_before
  When Context Mode is registered and the test captures tools_list_tokens_after
  Then tools_list_tokens_after ≤ ceil(tools_list_tokens_before * 1.05)
  And the test logs "deferred_document_tokens=<N>" with N ≥ 200000
```

## Out of scope

- Building the manifest itself — Spec 111 owns that.
- TTLs, change notifications, or `resources/subscribe` wiring — Spec 110.
- Embeddings, vector search, or any non-BM25 ranking — Wave B sticks with BM25 (matching Spec 104).
- Per-caller permission/ACL filtering — no permission model in Wave B.
- Editing handler files outside `handlers/context/` to import context tools — handlers remain unaware of the context layer; only the model uses it.
- Replacing FastMCP's built-in `resources/list` / `resources/read` mechanism — we register entries via the standard decorator and trust the framework's transport.

## References

- `Plan/JULES_PROTOCOL.md` (gates 1–4)
- `Plan/000-overview.md` §2.1 #3 (no custom list_tools/search_tools — the *tool* meta-tools; this spec adds *context* anchors which are distinct), §2.4 (Code Mode classification)
- `Plan/_lessons-learned/14-token-consumption-postmortem.md` §2 (vendor/spec inlining is the problem this spec closes)
- Spec dependency: `Plan/008-codemode-registry/spec.md` (eager/deferred plumbing)
- Spec dependency: `Plan/104-tool-search-anchor-triad/spec.md` (the parallel triad pattern this spec mirrors for context)
- Spec dependency: `Plan/111-context-mode-manifest/spec.md` (the manifest this spec consumes)
- Spec dependency: `Plan/103-view-fields-projection/spec.md` (the projection helper reused for `fields=`)
- Spec sibling: `Plan/107-cache-breakpoint-ordering/spec.md` (cache breakpoint stays after the anchors)
- Spec downstream: `Plan/113-context-cache-and-subscriptions/spec.md` (adds invalidation + TTLs to this layer)
- MCP Resources spec: https://modelcontextprotocol.io/specification/2025-06-18/server/resources
- FastMCP Resource decorator: https://gofastmcp.com/servers/resources
