---
spec_id: 022
slug: dev-mode-install
status: ready
owner: jules
depends_on: [002, 005, 007, 008]
affects:
  - .claude-plugin/plugin.json
  - .mcp.json
  - servers/agency-mcp/pyproject.toml
  - servers/agency-mcp/run.py
  - servers/agency-mcp/README.md
  - docs/dev-setup.md
  - bin/agency-dev-install
  - tests/smoke/test_dev_install.py
source-repos: []
estimated_jules_sessions: 1
domain: cross
wave: A
---

> **Jules: read `Plan/JULES_PROTOCOL.md` before starting.** Run gates 1→4 in order:
> (1) Confidence ≥ 0.90, (2) TDD Red-Green-Refactor, (3) Evidence pasted under `## Evidence`, (4) Self-Review answered.
> Branch: `Master` (default base for fresh specs post-Wave-A; see JULES_PROTOCOL.md §3). Only modify paths under `affects:` below.
> Source repos under `source-repos:` are clone-and-read-only into `~/work/vendor/`; never commit them.
> If anything is ambiguous, open a draft PR labelled `[BLOCKED: clarification]` and stop — do not guess.

# Spec 022 — Dev-mode Plugin Install

## Why

The whole orchestration value-prop collapses if we cannot USE the plugin we're building. Today the orchestrator writes specs that produce code, the code lands in Master, but no live Claude Code session can actually load `agency-system` to invoke its skills + MCP tools — the plugin only becomes loadable after a final marketplace install + manifest publication. That gap forces the orchestrator into a "build-but-don't-eat-the-dogfood" mode: spec quality is judged from spec text alone, never from the live plugin's behaviour.

This spec closes that gap. It defines a single command — `claude --plugin-dir /path/to/the-agency-system` — that loads the plugin in dev mode directly from the working tree, with all 113+ tools, ~80+ skills, ~5+ commands accessible immediately. No marketplace round-trip. The orchestrator can then test specs against the actual running plugin in the next session, fix what breaks, and ship higher-quality follow-ups.

This unblocks the entire Wave B + Wave C workflow described in the next-session goal. It is the single most leveraged spec remaining in Wave A.

## Done When

- [ ] `claude --plugin-dir /home/user/the-agency-system` (or any absolute path to a checkout) boots Claude Code WITHOUT errors. Evidence: `claude --plugin-dir <path> /help 2>&1 | head -50` shows the agency-system plugin listed with non-zero skill count.
- [ ] At least 3 distinct domain prefixes are visible under `/agency-system:*` in `/help` output: `/agency-system:music-*` (54 skills), `/agency-system:jules-*` (1 skill + 5 commands), at least one of `/agency-system:novel-*` if Wave B has landed at session-test time (else skipped with note).
- [ ] The unified MCP server is connected and reports the full tool surface: `claude --plugin-dir <path> /mcp list 2>&1 | grep "agency-system"` shows the server, AND `claude --plugin-dir <path> /mcp tools agency-system 2>&1 | wc -l` returns ≥113.
- [ ] `servers/agency-mcp/run.py` is the canonical FastMCP entry point: `python -m agency_mcp.server` AND `python servers/agency-mcp/run.py` both boot without exception (the latter is what `.mcp.json` invokes).
- [ ] `bin/agency-dev-install` is an idempotent bootstrap script that handles the three known dev-install pitfalls:
  1. `uv pip install -e servers/agency-mcp/` for the editable Python install (handles tiktoken + audio deps).
  2. Verifies `.mcp.json` paths resolve under `${CLAUDE_PLUGIN_ROOT}`.
  3. Verifies skill auto-namespace (re-greps `skills/*/SKILL.md` frontmatter `name:` for `agency-system:` discoverability).
- [ ] `tests/smoke/test_dev_install.py` spawns `claude --plugin-dir <tempdir-with-checkout> --help` in a subprocess and asserts exit-zero + agency-system plugin appears in the listing. Skipped with reason if `claude` CLI is not on PATH in the test runner environment.
- [ ] `docs/dev-setup.md` describes the dev-install flow end-to-end: clone → `bin/agency-dev-install` → `claude --plugin-dir <path>` → invoke first skill. ≤80 lines.
- [ ] `servers/agency-mcp/README.md` is updated with the editable-install command + the `run.py` entrypoint contract.
- [ ] `.claude-plugin/plugin.json` carries the correct `version: 0.1.0-dev` (per Spec 002) plus a `description` that mentions the dev-install path.

## Source clones (run first)

```bash
# No external source clones — this spec works on the existing the-agency-system tree.
# Reference reading:
# - https://code.claude.com/docs/en/plugins (canonical Claude Code plugin docs)
# - https://code.claude.com/docs/en/plugins-reference (manifest schema)
```

## Files

- **Create**:
  - `servers/agency-mcp/run.py` — thin `__main__` entrypoint that calls `agency_mcp.server.create_mcp().run()`. Keep ≤20 lines; the bulk is in the package.
  - `bin/agency-dev-install` — bash script, executable (`chmod +x`). Bootstrap flow described in Done-When item 5.
  - `docs/dev-setup.md` — the end-to-end dev install runbook.
  - `tests/smoke/test_dev_install.py` — subprocess-driven smoke that exercises `claude --plugin-dir`.
- **Modify**:
  - `.claude-plugin/plugin.json` — version + description.
  - `.mcp.json` — verify the `mcpServers.agency-system.command` resolves correctly under `${CLAUDE_PLUGIN_ROOT}/servers/agency-mcp/run.py`.
  - `servers/agency-mcp/pyproject.toml` — add `[project.scripts]` entry for `agency-mcp = "agency_mcp.server:cli"` if a CLI shim is needed. Optional; skip if `run.py` is sufficient.
  - `servers/agency-mcp/README.md` — editable-install + entrypoint docs.
- **Move / Delete**: none.

## Approach

1. **Gate 1 — Confidence.** Verify the merged Specs 002, 005, 007, 008 produce a plugin manifest + skills tree + MCP server skeleton that COULD load if wired correctly. Cite `find skills/ -name SKILL.md | wc -l`, `cat .claude-plugin/plugin.json | jq .name`, `cat .mcp.json | jq '.mcpServers | keys'`.
2. **Audit current state.** Run `claude --plugin-dir /home/user/the-agency-system 2>&1 | head -50` (or wherever a dev machine has the repo) — capture the actual current failure modes. Likely candidates: missing `run.py`, mismatched mcpServers command, missing editable install, ImportError on `from agency_mcp.server import create_mcp` because the package isn't installed.
3. **Write `run.py`.** Three lines: `from agency_mcp.server import create_mcp`, `if __name__ == "__main__":`, `create_mcp().run()`. The `create_mcp` factory already exists per Spec 008.
4. **Write `bin/agency-dev-install`.** Bash, ≤60 lines. Steps:
   - Detect repo root via `git rev-parse --show-toplevel` or argv[1].
   - `cd $REPO_ROOT/servers/agency-mcp && uv pip install -e .` (handles editable install).
   - Verify `python -c "from agency_mcp.server import create_mcp; print(create_mcp())"` exits 0.
   - Verify `.mcp.json` parses + each command resolves under `${CLAUDE_PLUGIN_ROOT}`.
   - Print the next-step command: `claude --plugin-dir $REPO_ROOT`.
   - Exit 0 on success, 1 with structured error message on any failure.
5. **TDD — Gate 2.** Write `tests/smoke/test_dev_install.py` first. RED: assert that `subprocess.run(["claude", "--plugin-dir", repo_root, "--help"], capture_output=True, timeout=30)` returns exit 0 AND `b"agency-system" in result.stdout`. The test skips with `pytest.skip("claude CLI not on PATH")` if the binary is missing, so CI without Claude Code installed still passes. Watch the test fail (because `run.py` doesn't exist yet). GREEN: ship `run.py` + the `.mcp.json` fix + the editable install.
6. **Write `docs/dev-setup.md`.** Sections: Prerequisites (uv, Python 3.11+, claude CLI), Install (`bin/agency-dev-install`), Verify (`claude --plugin-dir <repo> /help`), Troubleshoot (5 most likely failure modes — missing tiktoken, mismatched FastMCP version, stale `.mcp.json` path, missing CLAUDE_PLUGIN_ROOT, audio-dep import failures). ≤80 lines.
7. **Update `servers/agency-mcp/README.md`** with one new section: `## Dev Install`, mirroring the docs/dev-setup.md flow but server-scoped (editable install + entrypoint).
8. **Gate 3 — Evidence.** Paste `pytest -x tests/smoke/test_dev_install.py -v` (with `claude` CLI on PATH the test runs; without it, the skip note appears). Paste `bin/agency-dev-install` output. Paste `claude --plugin-dir <repo> /mcp list` output showing agency-system + its tool count.
9. **Gate 4 — Self-Review.** Answer the 3 questions. Specifically flag any pitfall that the bootstrap script does NOT handle (e.g. proxy environments, Python venv conflicts, multi-version uv) so a future spec can patch them.

## Acceptance (Gherkin)

```gherkin
# anchor: 022.1
Scenario: Dev-mode boot loads the plugin
  Given the repo is checked out at /path/to/the-agency-system
  And `bin/agency-dev-install` has been run successfully
  When the operator runs `claude --plugin-dir /path/to/the-agency-system /help`
  Then the process exits 0
  And the output contains "agency-system"
  And the output lists at least 3 distinct /agency-system:<prefix>-* command families

# anchor: 022.2
Scenario: MCP server reports the unified tool surface
  Given the dev install has succeeded
  When the operator runs `claude --plugin-dir <repo> /mcp tools agency-system`
  Then the tool count is ≥113
  And the listing includes `health_check`, `plugin_help`, and at least one `music_*` tool

# anchor: 022.3
Scenario: Bootstrap script is idempotent
  Given `bin/agency-dev-install` has been run once
  When the operator runs `bin/agency-dev-install` a second time on the same checkout
  Then the script exits 0 with "already installed, all checks pass" output
  And no file in the repo is modified by the second run

# anchor: 022.4
Scenario: Bootstrap script fails loudly on broken state
  Given `.mcp.json` has been hand-corrupted to point at a nonexistent server path
  When the operator runs `bin/agency-dev-install`
  Then the script exits 1
  And the stderr contains the resolved-but-missing path
  And no other side effect occurs (no half-install)
```

## Out of scope

- Final marketplace publication of the plugin (Spec 020 / Spec 002 cutover territory).
- Auto-restart of Claude Code sessions on plugin file changes (hot-reload). The dev install is "install + restart manually" — a hot-reload spec can follow if needed.
- Distribution of the plugin via pip / npm. Editable Python install is sufficient for dev; release packaging is a separate spec.
- CI installation runner that boots `claude --plugin-dir` on every PR. Possible future spec; not needed for v1.0.
- Windows compatibility for `bin/agency-dev-install`. Bash script is POSIX-only; Windows devs use WSL.

## References

- `Plan/JULES_PROTOCOL.md` §3 (branch / publish discipline) and §8 (silent-fail recovery — read before dispatching a session for this spec)
- `Plan/000-overview.md` §1 (target tree), §2.1 (FastMCP conventions)
- `Plan/002-manifest-and-marketplace/spec.md` — plugin.json + marketplace.json contracts this spec extends
- `Plan/008-codemode-registry/spec.md` — `create_mcp()` factory that `run.py` invokes
- `Plan/_session-state/2026-05-18-next-session-goal.md` — explains why this spec must land first in the next session
- [Claude Code Plugins — official docs](https://code.claude.com/docs/en/plugins)
- [Claude Code Plugins Reference — manifest schema](https://code.claude.com/docs/en/plugins-reference)
- [FastMCP — Code Mode docs](https://gofastmcp.com/servers/transforms/code-mode)
- [uv editable installs](https://docs.astral.sh/uv/pip/install/#editable-installs)
