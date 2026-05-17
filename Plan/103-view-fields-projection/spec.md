---
spec_id: 103
slug: view-fields-projection
status: ready
owner: jules
depends_on: [008]
affects:
  - servers/agency-mcp/src/agency_mcp/lib/codemode/views.py
  - servers/agency-mcp/src/agency_mcp/lib/codemode/projection.py
  - servers/agency-mcp/src/agency_mcp/handlers/music/__init__.py
  - servers/agency-mcp/src/agency_mcp/handlers/music/album_ops.py
  - servers/agency-mcp/src/agency_mcp/handlers/music/core.py
  - servers/agency-mcp/src/agency_mcp/handlers/jules/lifecycle.py
  - servers/agency-mcp/src/agency_mcp/handlers/shared/skills.py
  - servers/agency-mcp/src/agency_mcp/handlers/shared/search.py
  - tests/unit/codemode/__init__.py
  - tests/unit/codemode/test_views.py
  - tests/unit/codemode/test_projection.py
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

# Spec 103 — View Tiers & Fields Projection on Read Tools

## Why

Per the `Plan/_lessons-learned/14-token-consumption-postmortem.md` analysis, every `*_get` / `*_read` / `*_list` MCP tool currently returns the full Pydantic object — even when the caller only needs the `id`. A single `music_album_get` round-trip can burn 3-5k tokens when the caller is just resolving a foreign key. Adopting Pydantic's recommended `view=` enum + `fields=` projection contract (see reference) lets the caller request `view="id"` (just the primary key), `view="summary"` (id+name+state), `view="preview"` (summary + body truncated to `body_preview_chars`, default 400, with a `truncated_marker` field), or `view="full"` (legacy behaviour). Expected saving: **70-85% on heavy reads**. This is the single highest-leverage Wave-B token reduction.

## Done When

- [ ] `agency_mcp.lib.codemode.views.View` enum exists with values `id`, `summary`, `preview`, `full` (default `summary`).
- [ ] `agency_mcp.lib.codemode.projection.project(obj, view, fields)` returns the projected dict per the contract in §Approach.
- [ ] Every `*_get` / `*_read` / `*_list` tool in `handlers/music/`, `handlers/jules/lifecycle.py`, `handlers/shared/skills.py`, `handlers/shared/search.py` accepts optional `view: View = View.summary` and `fields: list[str] | None = None`.
- [ ] `view="preview"` truncates any `body` / `content` / `lyrics` field to `body_preview_chars` (default 400) and appends `truncated_marker: bool = True` when truncated.
- [ ] `pytest -x tests/unit/codemode/test_views.py tests/unit/codemode/test_projection.py` exits 0.
- [ ] Token-budget regression: smoke test in `test_projection.py` asserts `len(json.dumps(project(sample_album, view="summary")))` is ≤ 25% of `len(json.dumps(project(sample_album, view="full")))`.

## Source clones (run first)

None — this spec implements a contract documented in the Pydantic blog post (see References) but does not vendor third-party code.

## Files

- **Create**:
  - `servers/agency-mcp/src/agency_mcp/lib/codemode/views.py` — `View` enum + `BODY_PREVIEW_CHARS` constant.
  - `servers/agency-mcp/src/agency_mcp/lib/codemode/projection.py` — `project(obj, view, fields)` helper + `apply_view(model_cls)` decorator for handlers.
  - `tests/unit/codemode/__init__.py`.
  - `tests/unit/codemode/test_views.py` — enum + default contract.
  - `tests/unit/codemode/test_projection.py` — projection correctness + token-budget regression.
- **Modify**: every read/list tool listed in `affects:` to accept `view` + `fields` and call `project(...)` on the return value before serialisation.
- **Move / Delete**: none.

## Approach

1. **Gate 1 — Confidence.** Verify Spec 008 (`lib/codemode/__init__.py`, `lib/codemode/registry.py`) has shipped. Confirm `pydantic>=2.6` is in `pyproject.toml`. List the existing read/list tools via `rg '@mcp\.tool' servers/agency-mcp/src/agency_mcp/handlers/{music,jules,shared}/ -l` and cross-check against `affects:`.
2. **Define the view enum.** In `views.py`, declare `View = StrEnum("id", "summary", "preview", "full")` and `BODY_PREVIEW_CHARS = 400`. Document the four tiers in the module docstring: `id` → only the primary key; `summary` → id + name + state; `preview` → summary + truncated body + `truncated_marker`; `full` → all fields.
3. **Implement projection.** `project(obj, view, fields)` accepts a Pydantic model or dict and returns a `dict`. Resolution order: if `fields` is set, return the explicit field subset (validate names against the model schema, raise on unknown). Else, dispatch on `view`. For `preview`, walk the model's fields and truncate any `str` field named `body`, `content`, `lyrics`, `description` to `BODY_PREVIEW_CHARS`, setting `truncated_marker=True` at the dict root if any truncation occurred.
4. **Decorate handlers.** Add a tiny `@apply_view` decorator in `projection.py` that takes a handler returning a Pydantic model and wraps it to accept `view: View = View.summary, fields: list[str] | None = None`, projecting the return value. Handlers retain their original signatures otherwise.
5. **Wire the music handlers.** Apply `@apply_view` to `music_album_get`, `music_album_list`, `music_track_get`, `music_track_list` in `handlers/music/album_ops.py` and `handlers/music/core.py`. Re-export via `handlers/music/__init__.py` registration order.
6. **Wire the jules + shared handlers.** Apply to `jules_session_get`, `jules_session_list` (lifecycle.py), `skill_get`, `skill_list` (shared/skills.py), `search_skills`, `search_tools` (shared/search.py).
7. **TDD — Gate 2.** RED: write `test_views.py` (enum members, default value) and `test_projection.py` (six scenarios: id-view, summary-view, preview-view with long body, preview-view with short body, full-view, explicit fields). Add the token-budget regression test. Run — they must fail.
8. **GREEN.** Implement `views.py` + `projection.py` minimally. Wire the decorators. Re-run; tests pass.
9. **REFACTOR.** Pull repeated truncation logic into `_truncate_body_fields(...)`. Confirm no handler bypasses the decorator (`rg '@apply_view' servers/agency-mcp/src/agency_mcp/handlers/ -c`).
10. **Gate 3 — Evidence.** Paste pytest output, the token-budget assertion delta (full vs summary byte counts), and the `rg '@apply_view' -c` aggregate count into PR `## Evidence`. **Gate 4 — Self-Review.** Answer the three protocol questions and flag any read tool intentionally left un-decorated (e.g. tools whose entire output is already < 200 tokens).

## Acceptance (Gherkin)

```gherkin
# anchor: 103.1
Scenario: Default view returns summary projection
  Given an album with id="a1", name="Together We Confide", state="released", body="(2000 chars)"
  When the caller invokes music_album_get(id="a1") with no view argument
  Then the response dict contains exactly the keys {"id", "name", "state"}
  And no truncated_marker field is present

# anchor: 103.2
Scenario: Preview view truncates body and sets truncated_marker
  Given an album whose body field is 2000 chars long
  When the caller invokes music_album_get(id="a1", view="preview")
  Then the response.body has length 400
  And the response.truncated_marker is True
  And the response keys include {"id", "name", "state", "body", "truncated_marker"}

# anchor: 103.3
Scenario: Explicit fields override view tier
  Given an album with id="a1"
  When the caller invokes music_album_get(id="a1", view="full", fields=["id", "state"])
  Then the response dict contains exactly the keys {"id", "state"}

# anchor: 103.4
Scenario: Token-budget regression — summary is ≤25% of full
  Given a sample album with a 2000-char body and 12 nested fields
  When the test serialises project(album, view="summary") and project(album, view="full")
  Then len(json.dumps(summary_dict)) <= 0.25 * len(json.dumps(full_dict))
```

## Out of scope

- Pagination / cursor support on list tools (Spec 105 covers list-shape compression via TOON).
- Streaming / chunked responses for `view="full"` on very large objects.
- Auto-tuning `BODY_PREVIEW_CHARS` per tool — global constant is sufficient for Wave B.
- Changing the on-disk model schema; this spec is read-side projection only.

## References

- Pydantic blog — "Engineering MCP Tools for Token Efficiency": https://pydantic.dev/articles/engineering-mcp-tools-for-token-efficiency
- `Plan/_lessons-learned/14-token-consumption-postmortem.md` (heavy-read sink ranking)
- `Plan/JULES_PROTOCOL.md` (gates 1–4)
- `Plan/000-overview.md` §2.1 #1–#2 (tool naming + tags)
- Spec dependency: `Plan/008-codemode-registry/spec.md` (`lib/codemode/` package root)
- Spec sibling: `Plan/105-toon-serializer/spec.md` (list-shape compression — composes with this spec's `view="summary"`)
