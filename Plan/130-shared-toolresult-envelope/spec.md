---
spec_id: 130
slug: shared-toolresult-envelope
status: draft
owner: jules
depends_on: [008, 009]
affects:
  - servers/agency-mcp/src/agency_mcp/lib/envelope/__init__.py
  - servers/agency-mcp/src/agency_mcp/lib/envelope/models.py
  - servers/agency-mcp/src/agency_mcp/lib/envelope/wrap.py
  - servers/agency-mcp/src/agency_mcp/handlers/shared/config.py
  - servers/agency-mcp/src/agency_mcp/handlers/shared/reference.py
  - servers/agency-mcp/src/agency_mcp/handlers/shared/session.py
  - tests/unit/envelope/__init__.py
  - tests/unit/envelope/test_models.py
  - tests/unit/envelope/test_wrap.py
  - tests/integration/test_envelope_conformance.py
source-repos: []
estimated_jules_sessions: 2
domain: cross
wave: C
---

> **Jules: read `Plan/JULES_PROTOCOL.md` before starting.** Run gates 1→4 in order:
> (1) Confidence ≥ 0.90, (2) TDD Red-Green-Refactor, (3) Evidence pasted under `## Evidence`, (4) Self-Review answered.
> Branch: `Master` (default base for fresh specs post-Wave-A; see JULES_PROTOCOL.md §3). Only modify paths under `affects:` below.
> Source repos under `source-repos:` are clone-and-read-only into `~/work/vendor/`; never commit them.
> If anything is ambiguous, open a draft PR labelled `[BLOCKED: clarification]` and stop — do not guess.

# Spec 130 — Shared `ToolResult` Envelope + Conformance Gate

## Why

Overview §2.1 #9 declares the plugin-wide response envelope `{ok, data, warnings, artefacts_written, next_suggested_tools}` as a non-negotiable contract. Today the contract is hand-rolled per handler: `servers/agency-mcp/src/agency_mcp/handlers/shared/config.py:13-19` and `handlers/shared/reference.py:24-25` build the dict literal manually with no type checking; many other tools (e.g. every `handlers/music/core.py` query tool, every `handlers/jules/lifecycle.py` getter) return raw dicts or lists with no envelope at all. Spec 016 plans `handlers/agentic/_envelope.py` but scopes the model to the agentic domain only, so the four other domains continue to drift. The result is three pathologies the orchestrator already hit in `Plan/_lessons-learned/14-token-consumption-postmortem.md`: (1) callers can't reliably check `result.ok` because half the tools omit it; (2) `next_suggested_tools` discovery hints — the lowest-cost way to thread the model through a workflow without re-fetching the tools list — exist on 4 tools and on no others; (3) tool exceptions propagate as raw MCP error frames the model interprets as opaque failure, defeating the `warnings` accumulation pattern. This spec promotes the envelope to a shared Pydantic model under `lib/envelope/`, ships a `@wrap_envelope` decorator that handlers opt into, and adds an integration test that enumerates every registered `@mcp.tool` and asserts envelope conformance. Distinct from Spec 103 (`view`/`fields` is a *projection* of `data`, orthogonal to envelope shape) and Spec 105 (TOON encodes list-shape `data`, downstream of envelope). Distinct from Spec 016 (`_envelope.py` scoped to agentic; this spec hoists it to `lib/`).

## Done When

- [ ] `agency_mcp.lib.envelope.models.ToolResult` is a Pydantic v2 model with fields `ok: bool`, `data: Any`, `warnings: list[str] = []`, `artefacts_written: list[str] = []`, `next_suggested_tools: list[str] = []`, plus optional `error: ErrorInfo | None = None` (where `ErrorInfo` has `code: str`, `message: str`, `details: dict[str, Any] = {}`).
- [ ] `agency_mcp.lib.envelope.wrap.wrap_envelope(fn)` is an async-aware decorator that: (a) calls `fn(...)`, (b) if the return is already a `ToolResult` or a dict with key `ok`, passes it through after validation; (c) otherwise wraps the return as `ToolResult(ok=True, data=<return>)`; (d) on exception, catches `Exception` and returns `ToolResult(ok=False, data=None, error=ErrorInfo(code=type(e).__name__, message=str(e)))` — does NOT re-raise.
- [ ] `handlers/shared/config.py`, `handlers/shared/reference.py`, `handlers/shared/session.py` are migrated to use `ToolResult(...)` Pydantic instantiation instead of hand-rolled dicts (one-shot, ≤30 LOC delta total — these three modules are the canonical migration template the rest of the codebase will follow in follow-up specs).
- [ ] `tests/integration/test_envelope_conformance.py` boots `create_mcp()`, walks `mcp._tools`, invokes a sentinel-arg call on every tool tagged `domain:shared` (the migrated set), and asserts `ToolResult.model_validate(result)` succeeds for all of them. The test xfails for non-migrated tools with an explicit `pytest.mark.xfail(reason="not-yet-migrated")` to keep the green build honest.
- [ ] `pytest -x tests/unit/envelope/test_models.py tests/unit/envelope/test_wrap.py tests/integration/test_envelope_conformance.py` exits 0.
- [ ] `lib/envelope/__init__.py` re-exports `ToolResult`, `ErrorInfo`, `wrap_envelope` so handlers import via the package root.
- [ ] `handlers/agentic/_envelope.py` (planned by Spec 016) imports `ToolResult` from `agency_mcp.lib.envelope` rather than re-defining it — this spec documents the contract; Spec 016 consumes it. If Spec 016 has not yet landed, leave a one-line forward-reference comment in `lib/envelope/__init__.py` so the Spec-016 author wires correctly.

## Source clones (run first)

None. Local references:
- `servers/agency-mcp/src/agency_mcp/handlers/shared/config.py:8-35` — the current hand-rolled dict literal (this spec replaces it).
- `servers/agency-mcp/src/agency_mcp/handlers/shared/reference.py:24-38` — same pattern, second instance.
- `/home/user/agency/Agency-System/backend/agency_backend/mcp_server.py:33-114` — the comparison MCP server in the sibling `netzkontrast/agency` repo returns raw `list[dict]` / `dict` with no envelope at all; cite as evidence of the drift this spec prevents.

Reference docs:
- https://modelcontextprotocol.io/specification/2025-06-18/server/tools (the MCP tool-call spec defines `isError` and `content` blocks — `ToolResult.ok` MUST map to `isError = not ok` on the wire).
- https://gofastmcp.com/servers/tools (FastMCP's documented signature handling — confirm Pydantic return types are auto-serialised).

## Files

- **Create**:
  - `servers/agency-mcp/src/agency_mcp/lib/envelope/__init__.py` — re-exports `ToolResult`, `ErrorInfo`, `wrap_envelope`.
  - `servers/agency-mcp/src/agency_mcp/lib/envelope/models.py` — `ToolResult` + `ErrorInfo` Pydantic v2 models.
  - `servers/agency-mcp/src/agency_mcp/lib/envelope/wrap.py` — `wrap_envelope` decorator (async-aware, exception-catching).
  - `tests/unit/envelope/__init__.py`.
  - `tests/unit/envelope/test_models.py` — model field defaults, validation errors on unknown fields, JSON round-trip.
  - `tests/unit/envelope/test_wrap.py` — wraps sync + async fns; passes through already-wrapped results; catches exceptions to `ok=False`.
  - `tests/integration/test_envelope_conformance.py` — boots `create_mcp()`, enumerates `mcp._tools` filtered by tag `domain:shared`, asserts envelope conformance.
- **Modify**:
  - `servers/agency-mcp/src/agency_mcp/handlers/shared/config.py` — replace dict literals with `ToolResult(...)`.
  - `servers/agency-mcp/src/agency_mcp/handlers/shared/reference.py` — same.
  - `servers/agency-mcp/src/agency_mcp/handlers/shared/session.py` — same (audit current returns; `shared_update_session(dry_run=True)` should return `ToolResult(ok=True, data={"would_apply": ..., "diff": ...})`).
- **Move / Delete**: none.

## Approach

1. **Gate 1 — Confidence.** Verify Spec 008 has shipped `lib/codemode/registry.py` and Spec 009 has shipped `handlers/shared/`. Read overview §2.1 #9 verbatim and paste into PR Confidence. Run `grep -rn '"ok": *True\|"ok": *False' servers/agency-mcp/src/agency_mcp/handlers/` to enumerate every existing hand-rolled envelope site (expected count ≥4); cite the count in Confidence to scope the migration.
2. **Define the model.** In `models.py`, declare `ErrorInfo(BaseModel)` then `ToolResult(BaseModel)` with the fields listed in §Done When. Use `model_config = ConfigDict(extra="forbid")` so callers cannot quietly add fields outside the contract. Document each field in the docstring with one-sentence purpose + example value.
3. **Implement the decorator.** In `wrap.py`, write `wrap_envelope(fn)` that detects async via `inspect.iscoroutinefunction`. The wrapper logic: (a) `try: result = await fn(...) if async else fn(...)`; (b) if `isinstance(result, ToolResult)`, return its `.model_dump()` (FastMCP serialises dicts); (c) if `isinstance(result, dict) and "ok" in result`, validate via `ToolResult.model_validate(result).model_dump()`; (d) else wrap as `ToolResult(ok=True, data=result).model_dump()`; (e) `except Exception as e: return ToolResult(ok=False, data=None, error=ErrorInfo(code=type(e).__name__, message=str(e))).model_dump()`. The decorator MUST preserve `fn.__name__`, `fn.__doc__`, and the signature (use `functools.wraps`); FastMCP introspects these to build the tool schema.
4. **Migrate the three shared handlers.** For `config.py`: replace the three `return {"ok": ..., ...}` blocks with `return ToolResult(ok=..., data=..., warnings=[...]).model_dump()`. For `reference.py` + `session.py`: same. Keep behaviour identical — no functional change beyond shape.
5. **Wire conformance test.** `test_envelope_conformance.py` does: `mcp = create_mcp(); shared_tools = [t for t in mcp._tools.values() if "domain:shared" in (t.tags or set())]; for t in shared_tools: result = await t.run({}); ToolResult.model_validate(result)`. Use `pytest.parametrize` over the tool list so each tool is its own test case (failures pinpoint the misbehaving tool).
6. **TDD — Gate 2.** RED: write `test_models.py` (4 tests: defaults, extra-field rejection, JSON round-trip via `model_dump_json`, ErrorInfo nested) and `test_wrap.py` (5 tests: sync passthrough, async passthrough, already-wrapped passthrough, exception capture, signature preservation). Add the integration test. Run — all fail because `lib/envelope/` doesn't exist yet.
7. **GREEN.** Ship `models.py` + `wrap.py` + `__init__.py`. Migrate `config.py` / `reference.py` / `session.py`. Re-run; tests pass.
8. **REFACTOR.** Confirm no other module imports `ToolResult` from anywhere except `agency_mcp.lib.envelope` (`rg "import.*ToolResult" servers/`). Leave a `TODO(spec-130-followup): migrate music/jules/novel handlers` comment in `lib/envelope/__init__.py` so the follow-up scope is explicit.
9. **Gate 3 — Evidence.** Paste: (a) `pytest -x tests/unit/envelope/ tests/integration/test_envelope_conformance.py -v` output. (b) `grep -rn '"ok": *True' servers/agency-mcp/src/agency_mcp/handlers/` before-vs-after counts (the after count for `handlers/shared/` should be 0; the hand-rolled dicts have been replaced by Pydantic). (c) A redacted `shared_get_config()` response showing the typed envelope. **Gate 4 — Self-Review.** Confirm: no handler outside `handlers/shared/` was modified (out-of-scope guard); the `extra="forbid"` config is set; the decorator preserves `__doc__` (FastMCP needs it for the deferred-schema tool description).

## Acceptance (Gherkin)

```gherkin
# anchor: 130.1
Scenario: ToolResult rejects unknown fields
  Given the Pydantic model ToolResult is loaded from agency_mcp.lib.envelope
  When the test calls ToolResult.model_validate({"ok": True, "data": {}, "rogue_key": 1})
  Then a pydantic.ValidationError is raised
  And the error message names "rogue_key" as a forbidden field

# anchor: 130.2
Scenario: wrap_envelope catches handler exceptions and returns ok=False
  Given a handler fn() that raises ValueError("boom")
  When the test invokes wrap_envelope(fn)()
  Then the response is a dict with key "ok" equal to False
  And the response.error.code equals "ValueError"
  And the response.error.message equals "boom"
  And no exception propagates to the caller

# anchor: 130.3
Scenario: Shared handler config.py returns a valid ToolResult envelope
  Given the migrated shared_get_config handler
  When the test invokes shared_get_config()
  Then ToolResult.model_validate(response) succeeds
  And the response.ok is True (assuming config.yaml is readable or missing)
  And the response.data is a dict
  And the response.warnings is a list (possibly empty)

# anchor: 130.4
Scenario: Every shared-domain tool conforms to the envelope contract
  Given the agency-mcp server is booted via create_mcp()
  And every tool tagged "domain:shared" is enumerated
  When the conformance test invokes each tool with sentinel args
  Then ToolResult.model_validate(result) succeeds for every tool
  And every tool's response has the keys {"ok", "data", "warnings", "artefacts_written", "next_suggested_tools"}

# anchor: 130.5
Scenario: wrap_envelope preserves the decorated function's signature for FastMCP schema introspection
  Given a handler fn(album_id: str, *, dry_run: bool = False) -> dict
  When wrap_envelope(fn) is applied and FastMCP inspects the wrapped callable
  Then the wrapped callable's __name__ equals "fn"
  And inspect.signature(wrapped) reports parameters ["album_id", "dry_run"]
  And the wrapped callable's __doc__ matches the original
```

## Out of scope

- Migrating music / jules / novel / agentic handlers to use `ToolResult` — three are explicit out-of-scope; the agentic migration happens in Spec 016 which imports from `lib/envelope` per this spec's contract. Follow-up specs (132+) cover the other three domains.
- Wire-level mapping of `ToolResult.ok` to MCP `isError` — FastMCP already serialises Pydantic dicts faithfully; this spec does NOT touch transport. If a future inter-op spec needs `isError`, it builds on this envelope.
- Telemetry / metrics emission on `ok=False` responses (would belong in Spec 100 session-log territory).
- Adding `cursor`, `has_more`, or pagination fields to the envelope — list-shape concerns live in Spec 105 (TOON) and Spec 103 (`view`/`fields`). The envelope is response-shape-agnostic.
- Mandating `next_suggested_tools` content — handlers may leave it empty in this spec; a future spec curates per-tool suggestions.

## References

- `Plan/000-overview.md` §2.1 #6 (response shape), #7 (`dry_run`), #9 (`ToolResult` envelope — the binding contract this spec implements).
- `Plan/JULES_PROTOCOL.md` (gates 1–4).
- `Plan/_lessons-learned/14-token-consumption-postmortem.md` §2 (downstream of envelope drift — orchestrator can't rely on `result.ok` to skip retries).
- Spec dependency: `Plan/008-codemode-registry/spec.md` (`lib/codemode/` package root pattern this spec mirrors as `lib/envelope/`).
- Spec dependency: `Plan/009-shared-handlers/spec.md` (the three shared handlers this spec migrates).
- Spec consumer: `Plan/016-agentic-handlers-and-skills/spec.md` (Spec 016's `_envelope.py` imports `ToolResult` from `lib/envelope` per this spec).
- Spec sibling: `Plan/103-view-fields-projection/spec.md` (orthogonal — view/fields project `data`; envelope wraps `data`).
- Comparison reference: `/home/user/agency/Agency-System/backend/agency_backend/mcp_server.py:33-114` (sibling repo's MCP returns raw payloads — this spec is the discipline that prevents the same drift).
- MCP tool spec: https://modelcontextprotocol.io/specification/2025-06-18/server/tools
- FastMCP tools docs: https://gofastmcp.com/servers/tools