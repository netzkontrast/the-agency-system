---
spec_id: 012
slug: dramatica-and-ncp-libs
status: done
owner: jules
depends_on: [010]
affects:
  - reference/novel/dramatica/ontology.json
  - reference/novel/dramatica/scenarios.json
  - reference/novel/dramatica/ontology.schema.json
  - reference/novel/dramatica/scenarios.schema.json
  - reference/novel/dramatica/term-frontmatter.schema.json
  - reference/novel/dramatica/theory-chunk.schema.json
  - reference/novel/dramatica/terms/
  - reference/novel/ncp/ncp-spec-v1.3.0.md
  - state/schema/ncp.schema.json
  - servers/agency-mcp/src/agency_mcp/lib/dramatica/__init__.py
  - servers/agency-mcp/src/agency_mcp/lib/dramatica/navigator.py
  - servers/agency-mcp/src/agency_mcp/lib/ncp/__init__.py
  - servers/agency-mcp/src/agency_mcp/lib/ncp/compiler.py
  - servers/agency-mcp/src/agency_mcp/lib/ncp/validator.py
  - tests/unit/lib/__init__.py
  - tests/unit/lib/test_dramatica_nav.py
  - tests/unit/lib/test_ncp_validator.py
estimated_jules_sessions: 2
domain: novel
wave: B
deps:
  - jsonschema>=4.21.0
---

> **Jules: read `Plan/JULES_PROTOCOL.md` before starting.** Run gates 1→4 in order:
> (1) Confidence ≥ 0.90, (2) TDD Red-Green-Refactor, (3) Evidence pasted under `## Evidence`, (4) Self-Review answered.
> Branch: `claude/agency-plugin-refactor-PgMQ4`. Only modify paths under `affects:` below.
> Source repos under `source-repos:` are clone-and-read-only into `~/work/vendor/`; never commit them.
> If anything is ambiguous, open a draft PR labelled `[BLOCKED: clarification]` and stop — do not guess.

# Spec 012 — Dramatica + NCP Libraries

## Why

The novel coherence checks (spec 013 structural ops, spec 014 6-gate pre-drafting validator) need two foundations: a navigable Dramatica ontology and an NCP-v1.3.0 compiler + validator. The Dramatica ontology (304 entries: 4 Classes, 16 Types, 64 Variations, 64 Elements, plus 156 supporting term entries) plus 12 scenario archetypes is the theoretical backbone of every storyform decision; downstream gates check storyform consistency by looking up element relationships and verifying the 75 canonical dynamic-pair reciprocities. The NCP (Narrative Context Protocol) schema v1.3.0 is the canonical JSON shape into which a work's storyform, players, perspectives, motivations, and scenes serialise — `novel_create_work` (spec 011) ships an empty skeleton, and this spec ships the compiler that fills it and the validator that gates it. Without spec 012, the novel side has prose but no structural truth.

## Done When

- [ ] `reference/novel/dramatica/ontology.json` exists, parses as JSON, contains 304 entries.
- [ ] `reference/novel/dramatica/scenarios.json` exists, parses as JSON, contains 12 entries.
- [ ] All 4 dramatica schema files (`ontology.schema.json`, `scenarios.schema.json`, `term-frontmatter.schema.json`, `theory-chunk.schema.json`) exist and parse as valid JSON Schema (draft 2020-12).
- [ ] `reference/novel/dramatica/terms/` contains 17 type-bucket markdown files (one per dramatica Type) copied from the agency vendor and stripped of any agency-internal frontmatter that does not parse.
- [ ] `reference/novel/ncp/ncp-spec-v1.3.0.md` exists and reproduces the human-readable NCP v1.3.0 spec.
- [ ] `state/schema/ncp.schema.json` exists, parses as JSON Schema (draft 2020-12), is pinned to v1.3.0, and includes a header comment with the upstream SHA.
- [ ] `dramatica.navigator.by_id("element-resolve")` returns the Resolve element entry (a dict with `id`, `class`, `type`, `variation`, `dynamic_pair`).
- [ ] `dramatica.navigator.by_dynamic_pair("Resolve", "Process")` returns both ends `{a: <Resolve entry>, b: <Process entry>, ok: true}`.
- [ ] `dramatica.navigator.check_dynamic_pair_reciprocity({"a": "knowledge", "b": "thought"})` returns `{ok: true}` (canonical pair).
- [ ] `dramatica.navigator.check_dynamic_pair_reciprocity({"a": "knowledge", "b": "memory"})` returns `{ok: false, reason: "..."}` (not a canonical pair — memory pairs with conceptualizing).
- [ ] `ncp.compiler.compile(work_dir=...)` reads a work's `dramatica.md` + `cast.md` + `premise.md` + scene files and writes a `.ncp.json` that passes `ncp.validator.validate(...)` against the pinned v1.3.0 schema.
- [ ] `ncp.validator.validate(invalid_doc)` returns `{ok: false, errors: [...]}` listing each JSON-Schema violation; never raises.
- [ ] Tests cover **all 75** canonical dynamic-pair reciprocities (parametrised) and at least 3 known non-pairs.
- [ ] `pytest -x tests/unit/lib/` exits 0.
- [ ] `ruff check servers/agency-mcp/src/agency_mcp/lib/dramatica/ servers/agency-mcp/src/agency_mcp/lib/ncp/` exits 0.

## Source clones (run first)

```bash
git clone --depth=1 --branch=claude/agency-plugin-refactor-PgMQ4 \
  https://github.com/netzkontrast/agency.git \
  ~/work/vendor/agency
```

## Files

- **Create — vendored data** (copied from agency; record SHA in each file's header comment):
  - `reference/novel/dramatica/ontology.json` ← `~/work/vendor/agency/maintenance/schemas/narrative-ontology/ontology.json`
  - `reference/novel/dramatica/scenarios.json` ← `~/work/vendor/agency/maintenance/schemas/narrative-ontology/scenarios.json`
  - `reference/novel/dramatica/ontology.schema.json` ← agency same dir
  - `reference/novel/dramatica/scenarios.schema.json` ← agency same dir
  - `reference/novel/dramatica/term-frontmatter.schema.json` ← agency same dir
  - `reference/novel/dramatica/theory-chunk.schema.json` ← agency same dir
  - `reference/novel/dramatica/terms/{class,type,variation,element,...}-*.md` ← `~/work/vendor/agency/skills/dramatica-vocabulary/references/*.md` (17 type-bucket files).
- **Create — NCP**:
  - `reference/novel/ncp/ncp-spec-v1.3.0.md` ← `~/work/vendor/agency/skills/ncp-author/upstream/spec/ncp-spec-v1.3.0.md` (or equivalent path; rename if upstream uses a different file name).
  - `state/schema/ncp.schema.json` ← `~/work/vendor/agency/skills/ncp-author/upstream/schema/ncp-schema.json` (pinned SHA in header comment).
- **Create — Python libs**:
  - `servers/agency-mcp/src/agency_mcp/lib/dramatica/__init__.py` (re-exports `navigator`)
  - `servers/agency-mcp/src/agency_mcp/lib/dramatica/navigator.py` (the ported navigator)
  - `servers/agency-mcp/src/agency_mcp/lib/ncp/__init__.py` (re-exports `compiler`, `validator`)
  - `servers/agency-mcp/src/agency_mcp/lib/ncp/compiler.py`
  - `servers/agency-mcp/src/agency_mcp/lib/ncp/validator.py`
- **Create — tests**:
  - `tests/unit/lib/__init__.py`
  - `tests/unit/lib/test_dramatica_nav.py`
  - `tests/unit/lib/test_ncp_validator.py`
- **Modify**: none. (No handler registration in this spec — these are pure libraries. Spec 013 wires them into `novel_ncp_compile` and `novel_ncp_validate` tools.)

## Approach

1. Read `Plan/000-overview.md` §6 (research briefs — dramatica decidability matrix referenced) and the layout-spec.md from spec 010.
2. Clone agency. Locate the canonical paths:
   - `~/work/vendor/agency/maintenance/schemas/narrative-ontology/{ontology,scenarios,ontology.schema,scenarios.schema,term-frontmatter.schema,theory-chunk.schema}.json`
   - `~/work/vendor/agency/skills/dramatica-vocabulary/references/*.md` (the 17 type-bucket files)
   - `~/work/vendor/agency/skills/ncp-author/upstream/schema/ncp-schema.json`
   - `~/work/vendor/agency/skills/ncp-author/upstream/spec/` (or wherever the v1.3.0 human-readable spec lives)
   - `~/work/vendor/agency/tools/dramatica-nav/{nav,validate}.py` (existing Python; read for the navigator port)
   If any path differs in the actual agency tree, record the discovered path + SHA in the PR body and reconcile under `## Self-Review`.
3. Copy the 6 dramatica JSON files and the 17 term `.md` files into `reference/novel/dramatica/`. Each copied file gets a top-of-file comment recording the upstream path + SHA. JSON files cannot host comments — embed the SHA inside a `"_source": {"repo": "...", "sha": "...", "path": "..."}` key at the document root, but only if that key is permitted by the corresponding schema. For files where the schema forbids extra keys, ship the provenance in a sibling `.sha` file (e.g. `ontology.json.sha`).
4. Copy `ncp-schema.json` to `state/schema/ncp.schema.json` and `ncp-spec-v1.3.0.md` to `reference/novel/ncp/`. Both must carry SHA provenance.
5. Port `dramatica/navigator.py` from agency `tools/dramatica-nav/nav.py`. Required public API:
   - `class DramaticaNavigator` constructed with optional `ontology_path` + `scenarios_path` (defaults to repo paths).
   - `by_id(id: str) -> dict | None` — direct lookup.
   - `by_class(name: str) -> list[dict]`, `by_type(name: str) -> list[dict]`, `by_variation(name: str) -> list[dict]`, `by_element(name: str) -> list[dict]`.
   - `by_dynamic_pair(a: str, b: str) -> dict` — returns `{ok, a_entry, b_entry, reason?}`.
   - `check_dynamic_pair_reciprocity(pair: dict[str, str]) -> dict` — returns `{ok: bool, reason?: str}`; uses the ontology's `dynamic_pair` field of each entry.
   - `scenarios() -> list[dict]` — returns the 12 scenarios.
   - Lazy-load JSON on first call; cache in-process.
6. Build `lib/ncp/validator.py`:
   - `validate(doc: dict | str | pathlib.Path, schema_path: pathlib.Path | None = None) -> dict` returning `{ok: bool, errors: list[str]}`.
   - Uses `jsonschema` (Draft 2020-12); if `jsonschema` is not yet in `pyproject.toml`, declare it in the PR body and propose the add — do NOT add it silently (JULES_PROTOCOL.md §5 anti-pattern 5).
   - Defaults `schema_path` to `state/schema/ncp.schema.json`.
   - Never raises on validation failure; raises only on unreadable file or malformed JSON.
7. Build `lib/ncp/compiler.py`:
   - `compile(work_dir: pathlib.Path, write: bool = True) -> dict` returning the compiled NCP doc.
   - Reads `dramatica.md` (storyform: resolve/growth/approach/mental_sex + OS/MC/IC/RS class assignments), `cast.md` (players + perspectives + motivations), `premise.md` (logline, central question), and any scene files under `scenes/`.
   - Uses `DramaticaNavigator` to expand short identifiers (`"resolve"` → element entry) into full NCP-shaped objects.
   - If `write=True`, writes the result to `{work_dir}/ncp.json` (overwriting the skeleton from spec 010).
   - Validates the result against the pinned schema before returning; if invalid, returns `{ok: false, errors: [...], partial: <doc>}`.
8. RED: write `tests/unit/lib/test_dramatica_nav.py` and `tests/unit/lib/test_ncp_validator.py`. The reciprocity test is **parametrised over all 75 canonical dynamic pairs** (extract from the ontology at test-collection time, not hard-coded). Add at least 3 hand-picked non-pairs that must return `ok=false`. Watch the suite fail.
9. GREEN: implement the navigator, validator, compiler. Use a fixture work_dir built from `templates/novel/` (spec 010) with a hand-filled `dramatica.md` to exercise the compiler.
10. REFACTOR: extract a `_load_json_with_sha_header(path)` helper used by both navigator and validator. Ensure every JSON load goes through it for consistent error handling.
11. Verify with `pytest -x tests/unit/lib/`, `ruff check ...`, and a manual `python -c "from agency_mcp.lib.dramatica.navigator import DramaticaNavigator; n = DramaticaNavigator(); print(len(n._load_ontology()))"` → expect 304.

## Acceptance (Gherkin)

```gherkin
# anchor: 012.1
Scenario: DramaticaNavigator loads the 304-entry ontology and resolves Resolve
  Given reference/novel/dramatica/ontology.json contains the vendored 304 entries
  When the caller instantiates DramaticaNavigator and calls by_id("element-resolve")
  Then the result is a dict
  And the result has keys "id", "class", "type", "variation", "dynamic_pair"
  And the result.id equals "element-resolve"

# anchor: 012.2
Scenario: check_dynamic_pair_reciprocity accepts a canonical pair
  Given the ontology is loaded
  When the caller invokes check_dynamic_pair_reciprocity({"a": "knowledge", "b": "thought"})
  Then the result is {"ok": true}

# anchor: 012.3
Scenario: check_dynamic_pair_reciprocity rejects a non-pair with a reason
  Given the ontology is loaded
  When the caller invokes check_dynamic_pair_reciprocity({"a": "knowledge", "b": "memory"})
  Then the result.ok is false
  And the result.reason is a non-empty string explaining the mismatch

# anchor: 012.4
Scenario: All 75 canonical dynamic pairs round-trip through reciprocity
  Given the ontology is loaded
  When the test extracts every (a, b) where ontology[a].dynamic_pair == b
  Then for every such pair, check_dynamic_pair_reciprocity({"a": a, "b": b}) returns {"ok": true}
  And the parametrised case count is exactly 75

# anchor: 012.5
Scenario: ncp.compiler.compile produces a doc that ncp.validator.validate accepts
  Given a work_dir scaffolded from templates/novel/ with a hand-filled dramatica.md, cast.md, premise.md
  When the caller invokes ncp.compiler.compile(work_dir, write=False)
  Then the returned doc has top-level keys "storyform", "players", "scenes", "metadata"
  And ncp.validator.validate(doc) returns {"ok": true, "errors": []}

# anchor: 012.6
Scenario: ncp.validator.validate reports errors without raising
  Given a hand-crafted doc that omits the required "storyform" key
  When the caller invokes ncp.validator.validate(doc)
  Then the result.ok is false
  And result.errors is a non-empty list of human-readable JSON-Schema violations
  And no exception is raised
```

## Out of scope

- Wiring `novel_ncp_compile` / `novel_ncp_validate` MCP tools (spec 013).
- The 6-gate pre-drafting validator (spec 014).
- Authoring Dramatica tutorial skills (spec 015 — dramatica-vocabulary and dramatica-theory skill ports).
- The prompt-builder family that consumes NCP output (spec 021).
- Updating the dramatica ontology beyond v1.3.0 / 304 entries (out — pinned snapshot).
- Adding `jsonschema` to `pyproject.toml` silently — must be proposed in the PR body for human ack (JULES_PROTOCOL.md §5 anti-pattern 5).

## References

- `Plan/JULES_PROTOCOL.md` (gates 1–4; §4 vendor rules; §5 anti-pattern 5 on adding deps)
- `Plan/000-overview.md` §1 (lib/ tree under servers/agency-mcp), §6 (dramatica decidability matrix brief)
- `Plan/SOURCES.md` (agency branch; NCP schema and dramatica ontology entries)
- Vendor reference (read-only): `~/work/vendor/agency/maintenance/schemas/narrative-ontology/`
- Vendor reference (read-only): `~/work/vendor/agency/skills/ncp-author/upstream/schema/ncp-schema.json`
- Vendor reference (read-only): `~/work/vendor/agency/skills/dramatica-vocabulary/references/`
- Vendor reference (read-only): `~/work/vendor/agency/tools/dramatica-nav/{nav,validate}.py`
- Local: `templates/novel/dramatica.md`, `templates/novel/cast.md`, `templates/novel/premise.md`, `templates/novel/ncp.json` (delivered by spec 010)
