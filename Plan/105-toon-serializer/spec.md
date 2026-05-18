---
spec_id: 105
slug: toon-serializer
status: ready
owner: jules
depends_on: [008]
affects:
  - servers/agency-mcp/src/agency_mcp/lib/codemode/toon.py
  - servers/agency-mcp/src/agency_mcp/lib/codemode/serializer_middleware.py
  - servers/agency-mcp/pyproject.toml
  - tests/unit/codemode/test_toon.py
source-repos: []
estimated_jules_sessions: 1
domain: cross
wave: B
---

> **Jules: read `Plan/JULES_PROTOCOL.md` before starting.** Run gates 1→4 in order:
> (1) Confidence ≥ 0.90, (2) TDD Red-Green-Refactor, (3) Evidence pasted under `## Evidence`, (4) Self-Review answered.
> Branch: `Master` (default base for fresh specs post-Wave-A; see JULES_PROTOCOL.md §3). Only modify paths under `affects:` below.
> Source repos under `source-repos:` are clone-and-read-only into `~/work/vendor/`; never commit them.
> If anything is ambiguous, open a draft PR labelled `[BLOCKED: clarification]` and stop — do not guess.

# Spec 105 — TOON Serializer Middleware for Uniform Array Returns

## Why

Paginated list tools (`music_album_list`, `jules_session_list`, `skill_list`, `search_tools`) return homogeneous arrays where every element shares the same Pydantic schema. Encoding these as JSON re-emits the same key names on every row, which dominates the payload — measured at ~62% redundant bytes across the top-10 list returns in `Plan/_lessons-learned/14-token-consumption-postmortem.md`. TOON (Token-Oriented Object Notation) emits the schema once as a header row and then dense `|`-separated values per record. Wiring TOON as opt-in middleware (triggered when `n ≥ 3` and rows are schema-homogeneous) cuts list-shape token cost by **40-60%** with zero handler-side changes.

## Done When

- [ ] `agency_mcp.lib.codemode.toon.encode(rows: list[dict]) -> str` produces a valid TOON document (header + body) per the reference grammar.
- [ ] `agency_mcp.lib.codemode.toon.decode(doc: str) -> list[dict]` round-trips losslessly for all primitives present in our Pydantic models (`str`, `int`, `float`, `bool`, `None`, ISO-8601 datetime strings).
- [ ] `serializer_middleware.maybe_toon(result)` returns the TOON-encoded string when (a) `result` is a `list[dict]` with `len >= 3`, (b) every row has identical key set, (c) every value type is TOON-representable; otherwise returns the original `result`.
- [ ] The middleware is installed as a FastMCP post-serialisation hook in the codemode registry's response pipeline (added by Spec 008's hook point — this spec only registers the function).
- [ ] `pyproject.toml` declares `toon-py >= 0.3` as a runtime dependency.
- [ ] `pytest -x tests/unit/codemode/test_toon.py` exits 0.
- [ ] Token-budget regression: smoke test asserts `len(encode(sample_rows)) <= 0.60 * len(json.dumps(sample_rows))` for a 10-row sample.

## Source clones (run first)

```bash
git clone --depth=1 https://github.com/toon-format/toon.git \
  ~/work/vendor/toon
```

Read-only reference for the TOON grammar + canonical edge cases. Never commit.

## Files

- **Create**:
  - `servers/agency-mcp/src/agency_mcp/lib/codemode/toon.py` — `encode` + `decode` + grammar constants.
  - `servers/agency-mcp/src/agency_mcp/lib/codemode/serializer_middleware.py` — `maybe_toon(result)` gate function + registry hook plumbing.
  - `tests/unit/codemode/test_toon.py` — encode/decode round-trip + gate-function + token-budget regression.
- **Modify**:
  - `servers/agency-mcp/pyproject.toml` — append `toon-py >= 0.3` to runtime dependencies.
- **Move / Delete**: none.

## Approach

1. **Gate 1 — Confidence.** Verify Spec 008 (`lib/codemode/__init__.py`, `lib/codemode/registry.py`) has shipped and exposes a post-serialisation hook point. Clone the upstream TOON repo and skim `spec/grammar.md` to confirm header + body grammar. Confirm `toon-py` is on PyPI and supports the primitive set we need; if not, fall back to a hand-rolled encoder/decoder (note this in PR Confidence table).
2. **Implement `encode`.** Walk the first row to derive header `key1|key2|...|keyN`. For each row, emit `value1|value2|...|valueN` with the TOON escape rules (`|` → `\|`, `\n` → `\n` literal, `None` → empty cell). Preserve declaration order from the first row; validate every subsequent row has the same key set (raise `TOONShapeError` on mismatch).
3. **Implement `decode`.** Split into lines, parse the header, parse each body line by un-escaping cells, zip into dicts. Coerce primitive types via best-effort heuristics (`"true"`/`"false"` → bool, integer regex → int, ISO-8601 regex → string passthrough). Round-trip lossless for our model field types.
4. **Implement the gate.** `maybe_toon(result)` short-circuits when `result` is not a list, when `len(result) < 3`, when any row is not a dict, when row key sets differ, or when any value is a nested object (dict / list). Otherwise call `encode(result)` and return as a string; FastMCP will ship it as the tool response body with `content_type="text/toon"` (per Spec 008's hook contract).
5. **Wire the hook.** In `serializer_middleware.py`, expose `register_serializer_middleware(registry)` that the codemode registry calls at startup. Idempotent — safe to call twice.
6. **TDD — Gate 2.** RED: write `test_toon.py` with five tests: encode header order, encode escape rules, decode round-trip, `maybe_toon` accepts uniform list ≥ 3, `maybe_toon` rejects nested / heterogeneous / short input. Add the byte-size regression. Run — must fail.
7. **GREEN.** Implement `toon.py` + `serializer_middleware.py`. Re-run; tests pass.
8. **REFACTOR.** Extract `_escape_cell` / `_unescape_cell` as pure helpers; document the type-coercion table in the module docstring. Confirm no other module imports `toon-py` directly (`rg 'import toon' servers/`).
9. **Gate 3 — Evidence.** Paste pytest output, the byte-size assertion delta (JSON vs TOON for the 10-row sample), and an example TOON document fragment into PR `## Evidence`. **Gate 4 — Self-Review.** Flag any tool whose list return is intentionally excluded (e.g. mixed-schema search results that combine music + jules rows).

## Acceptance (Gherkin)

```gherkin
# anchor: 105.1
Scenario: maybe_toon encodes uniform list of three or more dicts as TOON
  Given a list of 10 dicts each with keys {"id", "name", "state"}
  When the middleware processes the result via maybe_toon(result)
  Then the response is a string starting with "id|name|state\n"
  And the response has exactly 11 lines (1 header + 10 rows)

# anchor: 105.2
Scenario: maybe_toon rejects short lists and passes JSON through
  Given a list of 2 dicts
  When the middleware processes the result via maybe_toon(result)
  Then the response is the original list (not a string)

# anchor: 105.3
Scenario: maybe_toon rejects heterogeneous row shapes
  Given a list of 5 dicts where row[3] is missing the "state" key
  When the middleware processes the result via maybe_toon(result)
  Then the response is the original list (not a string)

# anchor: 105.4
Scenario: encode then decode round-trips losslessly for primitive cells
  Given a list of 5 dicts with str / int / bool / None values
  When the test calls decode(encode(rows))
  Then the result equals the original rows element-by-element

# anchor: 105.5
Scenario: TOON payload is at most 60% the byte-size of equivalent JSON
  Given a list of 10 dicts each with 6 string fields
  When the test computes len(encode(rows)) and len(json.dumps(rows))
  Then len(encode(rows)) <= 0.60 * len(json.dumps(rows))
```

## Out of scope

- Encoding nested objects or arrays inside cells (the gate rejects these; no flattening attempted in Wave B).
- Negotiating `content_type` with the MCP client — Spec 008's hook contract handles the response envelope.
- Migrating individual handlers to call `encode` directly — the middleware is the single integration point.
- Replacing JSON for non-list returns or for `view="full"` single-object reads (Spec 103's territory).

## References

- TOON specification: https://github.com/toon-format/toon
- `Plan/_lessons-learned/14-token-consumption-postmortem.md` §4 (list-shape redundancy)
- `Plan/JULES_PROTOCOL.md` (gates 1–4)
- `Plan/000-overview.md` §2.4 (Code Mode classification + serialisation hook)
- Spec dependency: `Plan/008-codemode-registry/spec.md` (registry hook point)
- Spec sibling: `Plan/103-view-fields-projection/spec.md` (composes — `view="summary"` rows feed TOON encoder optimally)
