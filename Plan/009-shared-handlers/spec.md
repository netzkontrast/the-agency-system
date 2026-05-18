---
spec_id: 009
slug: shared-handlers
status: done
owner: jules
depends_on: [003]
affects:
  - servers/agency-mcp/src/agency_mcp/handlers/shared/search.py
  - servers/agency-mcp/src/agency_mcp/handlers/shared/skills.py
  - servers/agency-mcp/src/agency_mcp/handlers/shared/reference.py
  - servers/agency-mcp/src/agency_mcp/handlers/shared/config.py
  - servers/agency-mcp/src/agency_mcp/handlers/shared/session.py
  - servers/agency-mcp/src/agency_mcp/handlers/shared/__init__.py
  - servers/agency-mcp/src/agency_mcp/server.py
  - tests/unit/shared/test_search.py
  - tests/unit/shared/test_skills.py
  - tests/unit/shared/__init__.py
estimated_jules_sessions: 1
domain: cross
wave: B
---

> **Jules: read `Plan/JULES_PROTOCOL.md` before starting.** Run gates 1→4 in order:
> (1) Confidence ≥ 0.90, (2) TDD Red-Green-Refactor, (3) Evidence pasted under `## Evidence`, (4) Self-Review answered.
> Branch: `claude/agency-plugin-refactor-PgMQ4`. Only modify paths under `affects:` below.
> Source repos under `source-repos:` are clone-and-read-only into `~/work/vendor/`; never commit them.
> If anything is ambiguous, open a draft PR labelled `[BLOCKED: clarification]` and stop — do not guess.

# Spec 009 — Shared Handlers

## Why

Cross-domain queries (search across `music + novel + jules + agentic`, list-all-skills, get-any-reference, read shared config, persist a shared session) must not live inside a per-domain namespace. They belong in `handlers/shared/` so a caller never has to guess which domain owns a given primitive. This module is also the single home for `plugin_help(domain)`, the **one** cheat-sheet tool the plugin exposes per Code Mode best practice (overview §2.1.3: no custom `list_tools` / `search_tools`; rely on the framework's built-in discovery + this one markdown helper). Without spec 009 the novel side (specs 011–015) and the agentic side (spec 016) would each invent their own search/skill-listing helpers, breaking the single-responsibility shape the overview demands.

## Done When

- [ ] ~10 shared tools register on `create_mcp()`: `shared_search`, `shared_list_skills`, `shared_get_skill`, `shared_get_reference`, `shared_load_override`, `shared_get_config`, `shared_get_session`, `shared_update_session`, `shared_get_pending_verifications`, `plugin_help`.
- [ ] `plugin_help("music")` returns a markdown cheat-sheet ≤ 2000 tokens listing every music slash-skill + one-line summary.
- [ ] `plugin_help("novel")`, `plugin_help("jules")`, `plugin_help("agentic")`, `plugin_help("shared")` all return non-empty markdown.
- [ ] `plugin_help("does-not-exist")` returns `{ok: false, warnings: ["unknown domain: ..."]}` — never raises.
- [ ] `shared_search("dramatica")` returns hits from at least the `novel` and `agentic` namespaces of `state.json` plus any `reference/**/dramatica*` markdown.
- [ ] `shared_search("")` returns `{ok: true, data: [], warnings: ["empty query"]}` — never scans the disk.
- [ ] All stateful tools (`shared_update_session`) accept `dry_run: bool = False` and honour it (overview §2.1.7).
- [ ] All `list_*` tools cap at 20 results + opaque cursor (overview §2.1.6).
- [ ] `pytest -x tests/unit/shared/` exits 0.
- [ ] `ruff check servers/agency-mcp/src/agency_mcp/handlers/shared/` exits 0.

## Source clones (run first)

None. This spec is wholly within `the-agency-system`. The StateCache port (spec 003) already supplies the cross-namespace `state.json` shape this spec consumes.

## Files

- **Create**:
  - `servers/agency-mcp/src/agency_mcp/handlers/shared/__init__.py` (re-exports `register_shared_handlers`)
  - `servers/agency-mcp/src/agency_mcp/handlers/shared/search.py` (`shared_search`)
  - `servers/agency-mcp/src/agency_mcp/handlers/shared/skills.py` (`shared_list_skills`, `shared_get_skill`, `plugin_help`)
  - `servers/agency-mcp/src/agency_mcp/handlers/shared/reference.py` (`shared_get_reference`, `shared_load_override`)
  - `servers/agency-mcp/src/agency_mcp/handlers/shared/config.py` (`shared_get_config`)
  - `servers/agency-mcp/src/agency_mcp/handlers/shared/session.py` (`shared_get_session`, `shared_update_session`, `shared_get_pending_verifications`)
  - `tests/unit/shared/__init__.py`
  - `tests/unit/shared/test_search.py`
  - `tests/unit/shared/test_skills.py`
- **Modify**:
  - `servers/agency-mcp/src/agency_mcp/server.py` — add `from .handlers.shared import register_shared_handlers; register_shared_handlers(mcp)` inside `register_all(mcp)`.

## Approach

1. Read `Plan/000-overview.md` §2.1 (FastMCP construction, response shape rules, `dry_run`, `ToolResult` envelope) and §2.3 (skills auto-namespace under `/agency-system:<name>`).
2. Read the StateCache module shipped by spec 003 (`servers/agency-mcp/src/agency_mcp/state/cache.py`) and note the `{music, novel, jules, agentic}` top-level keys of `state.json`. All shared tools take the cache as a dependency, not the raw file path.
3. Build `shared_search(query: str, namespaces: list[str] | None = None, full: bool = False) -> ToolResult`:
   - Empty query → short-circuit with `warnings: ["empty query"]`.
   - Iterate the requested namespaces (default: all four), recursively walk JSON for string fields containing `query` (case-insensitive), yield `{namespace, path, summary}` hits.
   - Walk `reference/` for `.md` files whose name or first H1 matches; cap walk at depth 4.
   - Walk `skills/*/SKILL.md` frontmatter (`name`, `description`, `summary`).
   - Cap at 20 hits + cursor; `full=true` returns up to 200.
4. Build `shared_list_skills(domain: str | None = None) -> ToolResult` — enumerate `skills/{domain or *}/**/SKILL.md`, parse YAML frontmatter, return `[{name, summary, path}]` capped 20.
5. Build `shared_get_skill(name: str) -> ToolResult` — resolve `skills/**/{name}/SKILL.md`, return `{frontmatter, body_preview, length}`; for full body the caller uses `shared_get_reference` or the FastMCP `read_ref` resolver.
6. Build `plugin_help(domain: str) -> ToolResult`:
   - Domains: `music | novel | jules | agentic | shared`.
   - For each valid domain, render a static markdown template that pulls skill list from `shared_list_skills(domain)` and the domain's hand-authored prologue from `reference/{domain}/README.md` if present.
   - Token cap: pre-count rough tokens; if > 2000, truncate skill list and append `… (run shared_list_skills for full list)`.
   - Unknown domain → `{ok: false, warnings: ["unknown domain: <input>"]}` — do not raise.
7. Build `shared_get_reference(path: str) -> ToolResult` — resolve relative to `reference/`, deny traversal (`..`), return file body (capped 8 KB; offer `read_ref` for tails).
8. Build `shared_load_override(name: str) -> ToolResult` — resolve `overrides/{name}.md` or `.yaml`; same traversal guard.
9. Build `shared_get_config() -> ToolResult` — load `~/.agency-system/config.yaml` via StateCache (already mtime-watched after spec 003); never write.
10. Build session trio in `session.py`:
    - `shared_get_session()` → returns `state.json:_session` block.
    - `shared_update_session(patch: dict, dry_run: bool = False)` → if `dry_run`, return `{would_apply, diff}`; else write through StateCache's lock.
    - `shared_get_pending_verifications()` → returns `state.json:_session.pending_verifications` array.
11. RED: write `tests/unit/shared/test_search.py` covering empty-query, cross-namespace hit (seed a fake `state.json` with `novel: {dramatica: {note: "..."}}` and `agentic: {specs: [{title: "dramatica primer"}]}`), missing-domain. Write `tests/unit/shared/test_skills.py` covering `plugin_help("music")` returns markdown, `plugin_help("nonexistent")` returns `ok: false`, `shared_list_skills(domain="novel")` filters correctly. Watch them fail.
12. GREEN: implement modules. Wire `register_shared_handlers(mcp)` and call it from `server.py:register_all`.
13. REFACTOR: extract the markdown-render helper from `plugin_help` into a private `_render_cheatsheet(domain, skills, prologue)` for testability.
14. Verify with `pytest -x tests/unit/shared/`, `ruff check servers/agency-mcp/src/agency_mcp/handlers/shared/`, and a manual `python -c "from agency_mcp.server import create_mcp; m = create_mcp(); print(sorted(t.name for t in m._tools.values() if t.name.startswith('shared_') or t.name == 'plugin_help'))"`.

## Acceptance (Gherkin)

```gherkin
# anchor: 009.1
Scenario: plugin_help renders a markdown cheat-sheet for the novel domain
  Given the shared handlers are registered on the FastMCP instance
  And at least one skill exists under skills/novel/
  When the caller invokes plugin_help(domain="novel")
  Then the result is ok=true
  And data is a markdown string starting with "# /agency-system:novel-*"
  And data lists each skill under skills/novel/ with a one-line summary
  And the response length is at most 2000 tokens

# anchor: 009.2
Scenario: plugin_help on an unknown domain warns without raising
  Given the shared handlers are registered
  When the caller invokes plugin_help(domain="does-not-exist")
  Then the result is ok=false
  And warnings contains "unknown domain: does-not-exist"
  And no exception is raised

# anchor: 009.3
Scenario: shared_search finds hits across novel and agentic namespaces
  Given state.json contains a novel-namespace entry mentioning "dramatica"
  And state.json contains an agentic-namespace entry mentioning "dramatica"
  When the caller invokes shared_search(query="dramatica")
  Then the result is ok=true
  And data contains at least one hit with namespace="novel"
  And data contains at least one hit with namespace="agentic"
  And the data array has at most 20 items

# anchor: 009.4
Scenario: shared_search with an empty query short-circuits without scanning
  Given the shared handlers are registered
  When the caller invokes shared_search(query="")
  Then the result is ok=true
  And data is an empty list
  And warnings contains "empty query"

# anchor: 009.5
Scenario: shared_update_session honours dry_run by returning a diff only
  Given state.json:_session is {"current_album": "X"}
  When the caller invokes shared_update_session(patch={"current_album": "Y"}, dry_run=true)
  Then the result is ok=true
  And data.would_apply is true
  And data.diff shows current_album X → Y
  And state.json on disk still reads current_album="X"
```

## Out of scope

- Inventing any per-domain search variants (`music_search`, `novel_search`) — Code Mode best practice forbids that; this spec replaces them.
- Authoring the markdown prologues themselves (`reference/{domain}/README.md`). Each domain spec owns its own prologue.
- Building the cross-domain orchestration tool `agency_route_request` — that belongs in spec 016 (agentic).
- StateCache implementation (delivered by spec 003).
- Any skill `SKILL.md` authoring (specs 005, 007, 015, 016).

## References

- `Plan/JULES_PROTOCOL.md` (gates 1–4)
- `Plan/000-overview.md` §2.1.3 (no custom `list_tools` / `search_tools`; single `plugin_help`), §2.1.6 (response shape), §2.1.7 (`dry_run`), §2.1.9 (`ToolResult`), §2.1.10 (StateCache)
- `Plan/SOURCES.md` (FastMCP main docs)
- Local reference: `servers/agency-mcp/src/agency_mcp/state/cache.py` (delivered by spec 003)
