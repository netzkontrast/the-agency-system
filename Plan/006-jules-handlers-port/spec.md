---
spec_id: 006
slug: jules-handlers-port
status: ready
owner: jules
depends_on: [003]
affects:
  - servers/agency-mcp/src/agency_mcp/handlers/jules/__init__.py
  - servers/agency-mcp/src/agency_mcp/handlers/jules/_shared.py
  - servers/agency-mcp/src/agency_mcp/handlers/jules/source.py
  - servers/agency-mcp/src/agency_mcp/handlers/jules/trim.py
  - servers/agency-mcp/src/agency_mcp/handlers/jules/lifecycle.py
  - servers/agency-mcp/src/agency_mcp/handlers/jules/info.py
  - servers/agency-mcp/src/agency_mcp/handlers/jules/actions.py
  - servers/agency-mcp/src/agency_mcp/handlers/jules/patches.py
  - servers/agency-mcp/src/agency_mcp/server.py
  - jules-plugin/CHANGELOG.md
  - tests/unit/jules/__init__.py
  - tests/unit/jules/test_handlers_smoke.py
  - tests/unit/jules/test_watcher_quota.py
source-repos: []
estimated_jules_sessions: 1
domain: jules
wave: A
---

> **Jules: read `Plan/JULES_PROTOCOL.md` before starting.** Run gates 1→4 in order:
> (1) Confidence ≥ 0.90, (2) TDD Red-Green-Refactor, (3) Evidence pasted under `## Evidence`, (4) Self-Review answered.
> Branch: `claude/agency-plugin-refactor-PgMQ4`. Only modify paths under `affects:` below.
> Source repos under `source-repos:` are clone-and-read-only into `~/work/vendor/`; never commit them.
> If anything is ambiguous, open a draft PR labelled `[BLOCKED: clarification]` and stop — do not guess.

# Spec 006 — Jules Handlers Port

## Why

The existing `jules-plugin/mcp-server/src/jules_mcp/tools/` package ships 12 working tools (`create`, `list`, `get`, `start_watcher`, `stop_watcher`, `send_message`, `approve_plan`, `patch_summary`, etc.) that the human already relies on for asynchronous Jules orchestration. They are battle-tested, but live in the wrong server (the standalone `jules-plugin` MCP), so today the user has to install two plugins side-by-side. Moving the four tool modules into `handlers/jules/` and re-registering them on the unified `agency-system` FastMCP collapses that to one plugin while preserving every behaviour — including the watcher quota semantics, the patch-summary diff aggregator, and the `jules_*_status` poll companions that `008-codemode-registry` will mark as `background`. Without this spec, Wave A cannot retire the standalone `jules-plugin/mcp-server/` (deferred to Spec 020) because the tools have no home.

## Done When

- [ ] All 12 jules tools are registered on the unified FastMCP, with names matching `jules_<verb>_<object>` (e.g. `jules_create`, `jules_list`, `jules_start_watcher`, `jules_patch_summary`).
- [ ] Every jules tool carries `tags={"domain:jules"}`.
- [ ] Watcher quota semantics preserved: `jules_start_watcher` enforces the same per-user cap as the source implementation (unit test asserts).
- [ ] Background-tool companions present: `jules_start_watcher` has `jules_watcher_status`; any other long-running tool has a matching `_status` companion (overview §2.1 #5).
- [ ] `pytest -x tests/unit/jules/` exits 0.
- [ ] `python -c "from agency_mcp.server import create_mcp; m = create_mcp(); print(sum(1 for t in m._tools.values() if 'domain:jules' in (t.tags or set())))"` reports 12 (or 12 + N where N is the count of `_status` companions added).
- [ ] `jules-plugin/CHANGELOG.md` has a new entry marking the in-repo `jules-plugin/mcp-server/` as superseded by `servers/agency-mcp/handlers/jules/`, with a link forward to Spec 020 for the actual deletion.
- [ ] `jules-plugin/mcp-server/src/jules_mcp/tools/` source files remain untouched on disk (no edits, no deletions) — verified by `git status` showing no changes under that path.

## Source clones (run first)

None. This is an in-repo move. The local references are:
- `jules-plugin/mcp-server/src/jules_mcp/tools/lifecycle.py` (and the other tools modules — read but do not modify).
- `jules-plugin/mcp-server/src/jules_mcp/shared.py` (becomes `handlers/jules/_shared.py`).
- `jules-plugin/mcp-server/src/jules_mcp/server.py:4-5` (CodeMode `try/except` import pattern reference, also cited by Spec 008).

## Files

- **Create**:
  - `servers/agency-mcp/src/agency_mcp/handlers/jules/__init__.py` — exports `register_jules_handlers(mcp)`.
  - `servers/agency-mcp/src/agency_mcp/handlers/jules/_shared.py` — utilities formerly in `jules_mcp.shared` (HTTP client, auth, quota tracker).
  - `servers/agency-mcp/src/agency_mcp/handlers/jules/lifecycle.py` — `jules_create`, `jules_get`, `jules_list`, `jules_start_watcher`, `jules_stop_watcher`, `jules_watcher_status`.
  - `servers/agency-mcp/src/agency_mcp/handlers/jules/info.py` — `jules_list`, `jules_get_metadata`, `jules_list_repos` (if present in source).
  - `servers/agency-mcp/src/agency_mcp/handlers/jules/actions.py` — `jules_send_message`, `jules_approve_plan`, `jules_resume`, `jules_cancel`.
  - `servers/agency-mcp/src/agency_mcp/handlers/jules/patches.py` — `jules_patch_summary`, `jules_patch_diff`, `jules_patch_apply`.
  - `tests/unit/jules/__init__.py`.
  - `tests/unit/jules/test_handlers_smoke.py` — asserts the 12-tool count, naming convention, and tag presence.
  - `tests/unit/jules/test_watcher_quota.py` — asserts the watcher rejects beyond the quota and reports correctly via `jules_watcher_status`.
- **Modify**:
  - `servers/agency-mcp/src/agency_mcp/server.py` — call `register_jules_handlers(mcp)` inside `register_all(mcp)` after the music registration call.
  - `jules-plugin/CHANGELOG.md` — append "superseded by Spec 006 / `servers/agency-mcp/handlers/jules/`; deletion deferred to Spec 020" entry.
- **Move / Delete**: none. The old `jules-plugin/mcp-server/` stays on disk untouched; Spec 020 removes it after the unified plugin is the default.

## Approach

1. **Gate 1 — Confidence.** Read `jules-plugin/mcp-server/src/jules_mcp/tools/*.py` to enumerate the actual modules (Explore notes 5 modules; final count is whatever `ls` returns — cite the listing in Confidence). Verify Spec 003 has shipped `StateCache`. Verify the existing jules-plugin tools still register cleanly today (`python -c "from jules_mcp.server import create_mcp; print(len(create_mcp()._tools))"`). Cite the count.
2. **Map source → target.** Build a mapping table in the PR draft: `source_module | target_module | tools_count | renamed_tools`. Source modules are spread across (probably) `lifecycle.py`, `info.py`, `actions.py`, `patches.py` already; if the actual layout differs, use the source's layout and only collapse into the four-module shape listed in `affects:` if it falls out cleanly. If it does not, open `[BLOCKED: clarification]`.
3. **Copy + rewrite imports.** For each source module: copy the file content into the target, rewrite imports `from jules_mcp.shared` → `from agency_mcp.handlers.jules._shared`. Do not modify business logic.
4. **Rename tools.** Every `@mcp.tool()`-decorated function gets the `jules_` prefix and snake_case verb_object form. Examples: `create` → `jules_create`, `list` → `jules_list`, `start_watcher` → `jules_start_watcher`, `patch_summary` → `jules_patch_summary`. Add `tags={"domain:jules"}` to every tool decoration.
5. **Add `_status` companions for background tools.** Per overview §2.1 #5, every long-running tool registers a `<name>_status` poll companion that returns `{running: bool, progress: float|None, quota_remaining: int|None, started_at: iso8601}`. `jules_start_watcher` → `jules_watcher_status`. Any other long-running tool identified in source gets the same treatment. Document the list in the PR.
6. **Watcher quota.** Preserve the existing quota implementation byte-for-byte inside `_shared.py`. Cite the source file + line range in the PR. Spec 008 will key off this for Code Mode classification.
7. **Wire registration.** Each module exposes `register(mcp)`. `handlers/jules/__init__.py` defines `register_jules_handlers(mcp)` that imports the four modules and calls each `register(mcp)` deterministically. In `server.py`, call it from `register_all(mcp)` after music.
8. **TDD — Gate 2.** RED: `test_handlers_smoke.py` asserts 12 + N tools registered, all with `domain:jules` tag, all matching `^jules_[a-z]+(_[a-z0-9]+)+$`. `test_watcher_quota.py` mocks the quota tracker, calls `jules_start_watcher` N+1 times, asserts the (N+1)th call returns `{ok: False, reason: 'quota_exceeded'}` and `jules_watcher_status` reports `quota_remaining: 0`. Both tests must fail before code is written. GREEN: implement. REFACTOR: extract any per-module boilerplate.
9. **CHANGELOG entry.** Append a short entry under a `## Superseded` heading in `jules-plugin/CHANGELOG.md`. Do not edit any other line of any other file in `jules-plugin/`.
10. **Gate 3 — Evidence.** Paste `pytest -x tests/unit/jules/` output (both files), the tool-count `python -c …` output, and `git status jules-plugin/mcp-server/` showing zero changes under that path. **Gate 4 — Self-Review.** Confirm no business-logic drift; list any tool intentionally omitted (e.g. if source has a dead-code `_internal_*` helper exposed as a tool).

## Acceptance (Gherkin)

```gherkin
# anchor: 006.1
Scenario: 12 jules tools register on the unified FastMCP with the jules_ prefix
  Given Spec 003 has shipped agency_mcp.state.cache.StateCache
  And the jules handlers have been ported per this spec
  When the operator runs "python -c \"from agency_mcp.server import create_mcp; m=create_mcp(); print(sum(1 for t in m._tools.values() if 'domain:jules' in (t.tags or set())))\""
  Then the process exits with status 0
  And stdout reports an integer ≥ 12

# anchor: 006.2
Scenario: jules_start_watcher and jules_watcher_status preserve quota semantics
  Given the watcher quota tracker is mocked at N concurrent watchers max
  And N watchers have already been started via jules_start_watcher
  When the operator calls jules_start_watcher one more time
  Then the call returns {ok: false, reason: "quota_exceeded"}
  And jules_watcher_status returns {running: true, quota_remaining: 0}

# anchor: 006.3
Scenario: The legacy jules-plugin source tree is untouched by this spec
  Given the in-repo move has been performed per this spec
  When the operator runs "git status jules-plugin/mcp-server/src/jules_mcp/tools/"
  Then no files are listed as modified, added, or deleted under that path
  And jules-plugin/CHANGELOG.md is the only file under jules-plugin/ marked as modified
```

## Out of scope

- Porting the `skills/jules/` skill or `tools/researcher/` (Spec 007).
- Deleting `jules-plugin/mcp-server/` (Spec 020).
- Wiring Code Mode `defer_schema=True` for these tools (Spec 008 — keys off the tags set here).
- Porting music, novel, agentic, shared handlers (Specs 004, 011, 016, 009).
- Updating CLAUDE.md `/jules-orchestrator:*` references (Spec 020).

## References

- `Plan/JULES_PROTOCOL.md` (gates 1–4, §5 anti-pattern #6 on files-outside-affects)
- `Plan/000-overview.md` §1 (handlers/jules/ location), §2.1 #1, #2, #5 (`*_status` companions for background tools)
- Spec dependency: `Plan/003-unified-statecache-port/spec.md`
- Spec downstream: `Plan/007-jules-skills-and-commands-port/spec.md`, `Plan/008-codemode-registry/spec.md`, `Plan/020-bitwize-deprecation-and-docs/spec.md` (deletion)
- Local references: `jules-plugin/mcp-server/src/jules_mcp/tools/`, `jules-plugin/mcp-server/src/jules_mcp/shared.py`, `jules-plugin/mcp-server/src/jules_mcp/server.py:4-5`
