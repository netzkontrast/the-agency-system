---
spec_id: 111
slug: context-mode-manifest
status: ready
owner: jules
depends_on: [008, 104]
affects:
  - servers/agency-mcp/src/agency_mcp/lib/codemode/__init__.py
  - servers/agency-mcp/src/agency_mcp/lib/codemode/context_manifest.py
  - servers/agency-mcp/src/agency_mcp/lib/codemode/context_indexer.py
  - servers/agency-mcp/src/agency_mcp/codemode/context_manifest.json
  - servers/agency-mcp/src/agency_mcp/codemode/context_manifest.schema.json
  - servers/agency-mcp/bin/build_context_manifest.py
  - servers/agency-mcp/pyproject.toml
  - tests/unit/codemode/test_context_manifest.py
  - tests/unit/codemode/fixtures/context_corpus/plan_sample.md
  - tests/unit/codemode/fixtures/context_corpus/lesson_sample.md
  - tests/unit/codemode/fixtures/context_corpus/override_sample.md
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

# Spec 111 — Context Mode Manifest

## Why

Spec 008 solved boot-time *tool* schema bloat (~34k → ~315 tokens) via `defer_schema=True` and FastMCP's CodeMode triad. The mirror problem for *documents* remains: every session that wants to consult the 22 Plan specs, 14 lessons-learned, 304-entry Dramatica ontology, NCP schema, vendor docs, override files, audit reports, and album research preemptively reads them — Lesson 14 §2 measured ~80-100k tokens spent on inline vendor/spec reads in a single orchestrator session. The MCP `Resources` primitive (URI + MIME + subscribe; modelcontextprotocol.io/specification/2025-06-18/server/resources) supplies the transport but **no manifest, search, or summary layer** — clients still have to know URIs in advance. Anthropic's `defer_loading: true` (platform.claude.com/docs/.../tool-use-with-prompt-caching) exists only for *tools*, not documents. There is no canonical "Context Mode" feature in FastMCP 3.x or in the MCP 2025-06-18 spec; we are defining the pattern. This spec ships the **manifest** half of the pattern — the `{id, title, summary, tags, path, mime, size_bytes, last_modified, sha256}` catalogue and the crawler that builds it. Spec 112 ships the anchor-triad that consumes it; Spec 113 layers caching/subscriptions on top.

## Done When

- [ ] `codemode/context_manifest.schema.json` is a valid JSON-Schema (draft-2020-12) describing every manifest entry's required fields: `id` (slug, regex `^[a-z][a-z0-9_\-:/]+$`), `title` (≤120 chars), `summary` (≤400 chars), `tags` (array of `domain:*` / `kind:*` / freeform), `path` (relative to repo root), `mime` (`text/markdown` | `application/json` | `text/yaml` | `text/plain`), `size_bytes` (int), `last_modified` (ISO-8601), `sha256` (hex), `views` (object with optional keys `summary`/`preview`/`full`, each `{token_estimate: int, byte_offset?: int, byte_length?: int}`).
- [ ] `bin/build_context_manifest.py` crawls these roots and emits `codemode/context_manifest.json`:
  - `Plan/**/*.md` (specs + JULES_PROTOCOL + SOURCES + 000-overview)
  - `Plan/_lessons-learned/*.md`
  - `overrides/*.md` and `overrides/*.yaml`
  - `reference/**/*.md` and `reference/**/*.json`
  - `docs/**/*.md`
  - `genres/**/*.md`
  - Vendor docs under `~/work/vendor/**/*.md` (only those declared in `Plan/SOURCES.md`; absent vendor dirs do not fail the build)
- [ ] Each entry's `summary` is derived deterministically: H1 + first paragraph for `.md`, top-level `title`/`description` keys for JSON/YAML; truncated at 400 chars on a word boundary.
- [ ] Each entry's `views.summary.token_estimate` ≤ 120, `views.preview.token_estimate` ≤ 800, `views.full.token_estimate` equals the file's estimated token cost (heuristic: `ceil(bytes / 4)` if `tiktoken` is unavailable).
- [ ] `lib/codemode/context_manifest.py` exports `load_context_manifest(path) -> ContextManifest`, `ContextManifest.search(query, *, domain=None, tags=None, limit=20)` (BM25 over `title + summary + tags`), `ContextManifest.get(id)`, and `ContextManifest.validate_against_schema()`.
- [ ] `lib/codemode/context_indexer.py` exposes the deterministic summary + view-window extractor used by the builder script and the in-process indexer; both code paths share the same function so re-indexing on disk and in tests is byte-identical.
- [ ] `pytest -x tests/unit/codemode/test_context_manifest.py` exits 0 — covers schema validation, deterministic summary extraction, BM25 search, ID-collision detection, missing-file detection, and stale-sha256 detection.
- [ ] `python bin/build_context_manifest.py --check` exits 0 only when the on-disk manifest matches what a fresh crawl would emit (sha256 + size_bytes + last_modified per entry). CI can run this as a drift guard.
- [ ] Manifest is committed at `servers/agency-mcp/src/agency_mcp/codemode/context_manifest.json` and contains ≥ 40 entries (22 specs + 14 lessons + ≥4 overrides on the current tree).

## Source clones (run first)

None. The manifest builder reads files inside the working tree; vendor entries are *optional* — if the path doesn't exist on the Jules runner, the builder skips it with a `vendor-missing` log line, not an error.

Reference docs to read via WebFetch (do not clone):
- https://modelcontextprotocol.io/specification/2025-06-18/server/resources — for the URI/MIME contract this manifest must round-trip with (Spec 112 will expose entries via `resources/read`).
- https://gofastmcp.com/servers/transforms/code-mode — confirm the triad pattern this spec mirrors (search → describe → read) is consistent with the tool-side triad.
- https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-use-with-prompt-caching — for the `defer_loading` semantics we are replicating for non-tool content.

## Files

- **Create**:
  - `servers/agency-mcp/src/agency_mcp/lib/codemode/context_manifest.py` — loader + search + validator.
  - `servers/agency-mcp/src/agency_mcp/lib/codemode/context_indexer.py` — summary + view-window extraction shared by builder & loader.
  - `servers/agency-mcp/src/agency_mcp/codemode/context_manifest.json` — generated manifest (committed; CI guards drift).
  - `servers/agency-mcp/src/agency_mcp/codemode/context_manifest.schema.json` — JSON-Schema for entries.
  - `servers/agency-mcp/bin/build_context_manifest.py` — crawler CLI with `--check` mode.
  - `tests/unit/codemode/test_context_manifest.py` — full unit coverage.
  - `tests/unit/codemode/fixtures/context_corpus/plan_sample.md` — tiny Plan-style spec for deterministic-summary tests.
  - `tests/unit/codemode/fixtures/context_corpus/lesson_sample.md` — tiny lessons-style file with frontmatter for tag-extraction tests.
  - `tests/unit/codemode/fixtures/context_corpus/override_sample.md` — tiny override file for kind:override classification.
- **Modify**:
  - `servers/agency-mcp/src/agency_mcp/lib/codemode/__init__.py` — re-export `load_context_manifest`, `ContextManifest`.
  - `servers/agency-mcp/pyproject.toml` — add `pyyaml`, `jsonschema>=4.0`, `tiktoken` (already pinned for Spec 008 integration test; declare as required here too).
- **Move / Delete**: none.

## Approach

1. **Gate 1 — Confidence.** Confirm Spec 008 has shipped `lib/codemode/registry.py` (so this spec can sit beside it) and Spec 104 has defined the anchor-triad pattern this mirrors. Verify `fastmcp[code-mode]>=3.1.0` is pinned. WebFetch the three reference URLs above and paste the relevant signatures into the PR Confidence section: (a) the MCP `Resource` shape `{uri, name, mimeType, description, size}`, (b) the FastMCP CodeMode triad signatures, (c) Anthropic's `defer_loading` field. Confirm none of these supply a built-in `context_search` — this is novel work, not a re-export.
2. **Define the schema.** Author `context_manifest.schema.json` with the field set listed under Done When. Tag taxonomy is fixed: `domain:{music,novel,jules,agentic,cross}`, `kind:{spec,lesson,override,vendor-doc,reference,research,audit,prompt,ontology}`. Freeform tags MUST start with `topic:` (e.g. `topic:dramatica`, `topic:ncp`). Reject manifests with tags outside this pattern in `ContextManifest.validate_against_schema()`.
3. **Write the indexer** (`context_indexer.py`). Pure functions: `extract_summary(path, body) -> str`, `extract_views(path, body) -> dict`, `compute_sha256(body) -> str`, `infer_tags(path, frontmatter) -> list[str]`. For Markdown: summary = first H1 line (or filename if missing) + first non-empty paragraph after the H1, truncated at 400 chars on a word boundary. For YAML/JSON: pull `title` and `description` keys; if absent, fall back to filename + the first 200 chars of the serialised body. For `Plan/*/spec.md`: also extract `spec_id`, `slug`, `domain` from frontmatter and emit them as tags (`spec:008`, `domain:cross`, `slug:codemode-registry`). For `Plan/_lessons-learned/*.md`: extract `lesson_id`, `severity`, `applies_to` → tags. Views: `summary` = 0–400 bytes of the extracted summary, `preview` = 0–3200 bytes of the raw body, `full` = the whole file.
4. **Write the builder CLI** (`bin/build_context_manifest.py`). Argparse: `--root <dir>` (default repo root), `--out <file>` (default `codemode/context_manifest.json`), `--check` (compare on-disk vs. fresh crawl; exit 1 on drift), `--include-vendor / --no-include-vendor` (default include). Output is deterministic: entries sorted by `id`, JSON pretty-printed with `indent=2`, `sort_keys=True`, trailing newline. ID derivation: relative path with `/` → `:` and `.md`/`.json`/`.yaml` stripped (e.g. `Plan/008-codemode-registry/spec.md` → `plan:008-codemode-registry:spec`; `overrides/lyric-writing-guide.md` → `overrides:lyric-writing-guide`). Collision detection MUST raise on duplicate IDs (never silently overwrite).
5. **Write the loader** (`context_manifest.py`). `load_context_manifest(path)` reads JSON, runs `jsonschema.validate`, returns a `ContextManifest` dataclass with `.entries: list[ContextEntry]` and `.by_id: dict[str, ContextEntry]`. `.search(query, *, domain=None, tags=None, limit=20)` builds a BM25 index over `title + " " + summary + " " + " ".join(tags)` (use `rank_bm25.BM25Okapi` if available; otherwise a tiny inline implementation — keep the dependency optional). `domain` filter matches `f"domain:{domain}"`; `tags` filter is set-intersection (all must be present). Return value: `[{"id": ..., "title": ..., "summary": ..., "tags": [...], "score": float}]`. `.get(id)` returns the full entry including `views` and `path`.
6. **TDD — Gate 2.** RED: write `test_context_manifest.py` with at least these tests:
   - `test_schema_rejects_unknown_tag_prefix` — manifest with `tags: ["random-string"]` must fail validation.
   - `test_summary_extraction_is_deterministic` — running the indexer twice on `fixtures/context_corpus/plan_sample.md` yields byte-identical summaries.
   - `test_id_collision_raises` — two files producing the same ID raise `ContextManifestError`.
   - `test_check_mode_detects_stale_sha256` — mutate one byte of a fixture file, re-run `--check`, expect exit 1.
   - `test_search_ranks_title_match_above_body_match` — search for `dramatica` ranks `topic:dramatica` entries above incidental mentions.
   - `test_search_filters_by_domain_and_tags` — combined filters compose with set intersection.
   - `test_missing_file_in_manifest_fails_validation` — manifest referencing a deleted file fails validation with a clear error.
   - `test_view_token_budgets_are_enforced` — entries whose `views.summary.token_estimate > 120` fail validation.
   All tests RED before any implementation. GREEN: implement loader + indexer + builder. REFACTOR: collapse the indexer's per-MIME branches into a registry dict if it shortens without obscuring.
7. **Generate the initial manifest.** Run `python bin/build_context_manifest.py --root .` from repo root. Commit the resulting `codemode/context_manifest.json`. Spot-check 3 entries by hand: one spec, one lesson, one override — confirm the `summary` matches what a reader would expect.
8. **Drift guard.** Add a note in the PR description (and in Spec 110's references) recommending `python bin/build_context_manifest.py --check` as a CI step; this spec does NOT modify CI config (that's out of scope for Wave B).
9. **Gate 3 — Evidence.** Paste: (a) `pytest -x tests/unit/codemode/test_context_manifest.py` output. (b) `python bin/build_context_manifest.py --root . --check` exit-code 0 output. (c) `jq '. | length' servers/agency-mcp/src/agency_mcp/codemode/context_manifest.json` showing ≥ 40. (d) `jq '[.[] | .views.full.token_estimate] | add' servers/agency-mcp/src/agency_mcp/codemode/context_manifest.json` — the *total* token cost the manifest defers (this is the headline number for the PR; expect ≥ 200k).
10. **Gate 4 — Self-Review.** Answer the standard three questions. Specifically flag: which files were intentionally excluded (e.g. `audio/`, `documents/` LFS blobs, `state/cache.json`) and why; whether the vendor-docs branch ran on the Jules host or was skipped; any tag taxonomy edge cases (e.g. a lesson that crosses two domains).

## Acceptance (Gherkin)

```gherkin
# anchor: 108.1
Scenario: Manifest schema rejects entries with unknown tag prefixes
  Given the context_manifest.schema.json is the source of truth
  And a candidate entry has tags ["random-string"]
  When ContextManifest.validate_against_schema() runs
  Then validation fails with a JSON-Schema error citing "tags[0]"
  And the error message names the allowed prefixes domain:, kind:, topic:, spec:, slug:, lesson_id:

# anchor: 108.2
Scenario: Builder produces a deterministic manifest from a clean tree
  Given the repo working tree at HEAD with no uncommitted changes
  When the operator runs "python bin/build_context_manifest.py --root . --check"
  Then the process exits with status 0
  And running the builder a second time produces a byte-identical JSON file

# anchor: 108.3
Scenario: Search ranks topic-tagged entries above incidental body matches
  Given the manifest contains the entry "plan:012-dramatica-and-ncp-libs:spec" tagged topic:dramatica
  And a separate entry mentions "dramatica" only in the body
  When ContextManifest.search("dramatica", limit=5) runs
  Then the top result is "plan:012-dramatica-and-ncp-libs:spec"
  And the result list contains at most 5 entries
  And every entry has exactly the keys {"id", "title", "summary", "tags", "score"}

# anchor: 108.4
Scenario: Drift detection catches a file mutated after manifest generation
  Given the manifest has been generated against the current tree
  When one byte of any indexed file is changed on disk
  And the operator runs "python bin/build_context_manifest.py --check"
  Then the process exits with status 1
  And stderr names the drifted file and the expected vs actual sha256

# anchor: 108.5
Scenario: Manifest defers a measurable token cost
  Given the manifest covers Plan/, _lessons-learned/, overrides/, reference/
  When the operator sums views.full.token_estimate across all entries
  Then the total is ≥ 200,000 tokens
  And no single entry's views.summary.token_estimate exceeds 120
```

## Out of scope

- Exposing the manifest via MCP tools — that's Spec 112 (anchor-triad consumer).
- Caching, TTLs, or resource-subscription change notifications — that's Spec 110.
- Rewriting `Plan/` or `_lessons-learned/` content to fit a summary length — the indexer adapts to the existing files; do not edit corpus content.
- Generating embeddings or vector search — BM25 over title+summary+tags is sufficient for Wave B; vector search is a future spec if BM25 misses too often.
- CI wiring of the `--check` drift guard (note it in the PR; let a separate ops PR add it).
- Vendoring documents from external repos that are not already declared in `Plan/SOURCES.md`.

## References

- `Plan/JULES_PROTOCOL.md` (gates 1–4)
- `Plan/000-overview.md` §2.1 #3 (no custom list_tools/search_tools — applies to tools, NOT context: this spec adds context tools but does not duplicate the FastMCP tool meta-tools), §2.4 (Code Mode classification)
- `Plan/_lessons-learned/14-token-consumption-postmortem.md` §2 ("Reading vendor / large files inline" — the problem this spec attacks)
- `Plan/SOURCES.md` (vendor doc enumeration)
- Spec dependency: `Plan/008-codemode-registry/spec.md` (`defer_schema=True` plumbing this mirrors for documents)
- Spec dependency: `Plan/104-tool-search-anchor-triad/spec.md` (the search/describe/invoke triad pattern this spec's manifest will feed)
- Spec downstream: `Plan/112-context-anchor-triad/spec.md` (consumes this manifest)
- Spec downstream: `Plan/113-context-cache-and-subscriptions/spec.md` (adds TTLs + change notifications)
- MCP Resources spec: https://modelcontextprotocol.io/specification/2025-06-18/server/resources
- FastMCP Code Mode docs: https://gofastmcp.com/servers/transforms/code-mode
- Anthropic `defer_loading` semantics: https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-use-with-prompt-caching
- Prior-art research note: "Context Mode" as a named feature does not exist in the MCP 2025-06-18 spec, FastMCP 3.x release notes, or Anthropic's published advanced-tool-use docs (verified May 2026). The closest equivalents are the MCP `Resources` primitive (transport only, no manifest/search), FastMCP's CodeMode triad (tools only), and Anthropic's `defer_loading` (tools only). This spec defines the pattern for documents.
