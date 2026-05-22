---
spec_id: 001
slug: scaffold-plugin-skeleton
status: done
owner: jules
depends_on: []
affects:
  - .claude-plugin/
  - .mcp.json
  - servers/agency-mcp/
  - skills/shared/.gitkeep
  - skills/music/.gitkeep
  - skills/novel/.gitkeep
  - skills/jules/.gitkeep
  - skills/agentic/.gitkeep
  - hooks/.gitkeep
  - reference/.gitkeep
  - templates/.gitkeep
  - tools/.gitkeep
  - state/schema/.gitkeep
  - config/.gitkeep
  - docs/architecture/.gitkeep
  - tests/unit/.gitkeep
  - tests/integration/.gitkeep
  - tests/smoke/.gitkeep
  - bin/.gitkeep
  - migrations/.gitkeep
  - novels/.gitkeep
  - commands/.gitkeep
estimated_jules_sessions: 1
domain: scaffold
wave: A
---

> **Jules: read `Plan/JULES_PROTOCOL.md` before starting.** Run gates 1→4 in order:
> (1) Confidence ≥ 0.90, (2) TDD Red-Green-Refactor, (3) Evidence pasted under `## Evidence`, (4) Self-Review answered.
> Branch: `claude/agency-plugin-refactor-PgMQ4`. Only modify paths under `affects:` below.
> Source repos under `source-repos:` are clone-and-read-only into `~/work/vendor/`; never commit them.
> If anything is ambiguous, open a draft PR labelled `[BLOCKED: clarification]` and stop — do not guess.

# Spec 001 — Scaffold Plugin Skeleton

## Why

The unified plugin needs a clean root layout before any handler, skill, or state work can begin. The existing `jules-plugin/` already wires FastMCP + Code Mode but is the wrong shape — the manifest must move to repo root per Claude Code plugin conventions (`.claude-plugin/` only holds `plugin.json`). This spec lays down the entire directory tree from §1 of `Plan/000-overview.md`, stands up a bootable `agency-mcp` FastMCP server stub with a health-check tool, and unblocks every downstream wave-A spec (002 manifest, 003 statecache, 004 music handlers).

## Done When

- [ ] Directory tree matches §1 of `Plan/000-overview.md` (verified by `tree -L 3 -a`).
- [ ] `python servers/agency-mcp/run.py --check` exits 0 and prints `agency-system v0.0.1 healthy`.
- [ ] `python -c "from agency_mcp.server import create_mcp; print(create_mcp())"` exits 0.
- [ ] `pyproject.toml` declares `fastmcp[code-mode]>=3.1.0`.
- [ ] Smoke test `tests/smoke/test_boot.py` passes (`pytest -x tests/smoke/test_boot.py`).

## Source clones (run first)

None. Work on the existing repo only. The `jules-plugin/mcp-server/src/jules_mcp/server.py` file in the work tree is the local reference for the FastMCP + CodeMode try/except pattern.

## Files

- **Create**:
  - `.mcp.json` (root, uses `${CLAUDE_PLUGIN_ROOT}`)
  - `servers/agency-mcp/run.py`
  - `servers/agency-mcp/pyproject.toml`
  - `servers/agency-mcp/src/agency_mcp/__init__.py`
  - `servers/agency-mcp/src/agency_mcp/server.py`
  - `servers/agency-mcp/src/agency_mcp/handlers/__init__.py`
  - `servers/agency-mcp/src/agency_mcp/handlers/shared/__init__.py`
  - `servers/agency-mcp/src/agency_mcp/handlers/shared/health.py`
  - `tests/smoke/test_boot.py`
  - `.gitkeep` files in each empty dir under `affects:`
- **Modify**: none.
- **Move / Delete**: none (Spec 020 retires `jules-plugin/`; do not touch it here).

## Approach

1. Read `Plan/000-overview.md` §1 (architecture tree) and §2.3 (Claude Code plugin specifics) to confirm the layout. Read `jules-plugin/mcp-server/src/jules_mcp/server.py:1-21` for the CodeMode try/except pattern.
2. `mkdir -p` every directory from the architecture tree; drop `.gitkeep` in each leaf that has no other tracked file so the empty dirs survive `git add`.
3. Write `servers/agency-mcp/src/agency_mcp/server.py` with `create_mcp()` returning `FastMCP("agency-system", dereference_schemas=False)`; wrap `from fastmcp.experimental import CodeMode` in `try/except ImportError` (mirror lines 1-21 of the jules-plugin reference). Register a `register_all(mcp)` stub that imports nothing yet but exists for spec 004+ to extend.
4. Write `servers/agency-mcp/src/agency_mcp/handlers/shared/health.py` exposing a `health_check()` tool returning `{"ok": True, "version": "0.0.1", "name": "agency-system"}`; register it inside `register_all()`.
5. Write `servers/agency-mcp/run.py` with an `argparse` `--check` flag: when set, instantiate the MCP via `create_mcp()`, call the health tool synchronously, print `agency-system v0.0.1 healthy`, exit 0. When unset, run `mcp.run()` over stdio.
6. Write `servers/agency-mcp/pyproject.toml` pinning `fastmcp[code-mode]>=3.1.0` and `python>=3.11`; declare the `agency_mcp` package with src-layout. No other runtime deps in this spec.
7. Write `.mcp.json` at repo root with one server `agency-system` running `python ${CLAUDE_PLUGIN_ROOT}/servers/agency-mcp/run.py` over stdio — never absolute paths (§2.3).
8. RED: write `tests/smoke/test_boot.py::test_create_mcp_returns_fastmcp_instance` and `::test_health_check_returns_ok` — confirm they fail before any source exists, then implement to green.
9. Verify `pytest -x tests/smoke/test_boot.py` exits 0 and `python servers/agency-mcp/run.py --check` prints the expected line.

## Acceptance (Gherkin)

```gherkin
# anchor: 001.1
Scenario: Server boots and reports healthy via CLI check
  Given the new directory layout from Plan/000-overview.md §1 exists
  And servers/agency-mcp/pyproject.toml declares fastmcp[code-mode]>=3.1.0
  When the operator runs "python servers/agency-mcp/run.py --check"
  Then the process exits with status 0
  And stdout contains the line "agency-system v0.0.1 healthy"

# anchor: 001.2
Scenario: create_mcp() returns a FastMCP instance importable from agency_mcp.server
  Given the agency_mcp package is installed in editable mode
  When the operator runs "python -c \"from agency_mcp.server import create_mcp; print(type(create_mcp()).__name__)\""
  Then the process exits with status 0
  And stdout contains "FastMCP"

# anchor: 001.3
Scenario: CodeMode import failure does not break boot
  Given the optional fastmcp.experimental.CodeMode import raises ImportError
  When create_mcp() is invoked
  Then no exception propagates
  And the returned FastMCP instance still has the health_check tool registered
```

## Out of scope

- Authoring any plugin manifest (Spec 002).
- Porting the StateCache or any indexer (Spec 003).
- Porting any music, novel, jules, or agentic handler (Specs 004–016).
- Touching `jules-plugin/` or `bitwize-music` install state (Spec 020).
- Writing any skill `SKILL.md` (Specs 005, 007, 015, 016).

## References

- `Plan/JULES_PROTOCOL.md` (gates 1–4, §7 plugin conventions)
- `Plan/000-overview.md` §1 (target tree), §2.1 (FastMCP construction), §2.3 (plugin specifics)
- `Plan/SOURCES.md` (Claude Code Plugins Guide, FastMCP main docs)
- Local reference: `jules-plugin/mcp-server/src/jules_mcp/server.py:1-21`
