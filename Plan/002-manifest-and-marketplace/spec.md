---
spec_id: 002
slug: manifest-and-marketplace
status: ready
owner: jules
depends_on: [001]
affects:
  - .claude-plugin/plugin.json
  - .claude-plugin/marketplace.json
  - jules-plugin/.claude-plugin/plugin.json
  - README.md
estimated_jules_sessions: 1
domain: scaffold
wave: A
---

> **Jules: read `Plan/JULES_PROTOCOL.md` before starting.** Run gates 1→4 in order:
> (1) Confidence ≥ 0.90, (2) TDD Red-Green-Refactor, (3) Evidence pasted under `## Evidence`, (4) Self-Review answered.
> Branch: `claude/agency-plugin-refactor-PgMQ4`. Only modify paths under `affects:` below.
> Source repos under `source-repos:` are clone-and-read-only into `~/work/vendor/`; never commit them.
> If anything is ambiguous, open a draft PR labelled `[BLOCKED: clarification]` and stop — do not guess.

# Spec 002 — Manifest and Marketplace

## Why

Claude Code resolves a plugin by reading `.claude-plugin/plugin.json` at the repo root; without a valid manifest the plugin does not appear in `/plugin install`, `/plugin list`, or `/help`. The existing `jules-plugin/.claude-plugin/plugin.json` would collide with the new root manifest at install time, so it must be marked deprecated in the same change. A `marketplace.json` single-plugin descriptor gives the human a one-line URL install path for downstream waves. This spec is the minimum for `claude --plugin-dir .` to recognise `agency-system` as an installable plugin.

## Done When

- [ ] `.claude-plugin/plugin.json` exists with required keys `name: "agency-system"`, `version: "0.1.0"`, `description`, `author`, `homepage`, `mcpServers` referencing the root `.mcp.json` entry from Spec 001.
- [ ] Manifest validates against the Claude Code plugin schema (run `python -m json.tool .claude-plugin/plugin.json` exit 0 + smoke test below).
- [ ] `.claude-plugin/marketplace.json` exists as a single-plugin shape per Claude Code Plugins Reference.
- [ ] `jules-plugin/.claude-plugin/plugin.json` has `"deprecated": true` and a `description` suffix `"DEPRECATED — superseded by agency-system at repo root."`.
- [ ] `README.md` contains a "Plugin install" section showing both `claude --plugin-dir .` (local dev) and the marketplace URL form.
- [ ] Smoke test `tests/smoke/test_manifest.py` parses both manifests and asserts the keys above.

## Source clones (run first)

None. Read Claude Code documentation via WebFetch only — see References.

## Files

- **Create**:
  - `.claude-plugin/plugin.json`
  - `.claude-plugin/marketplace.json`
  - `tests/smoke/test_manifest.py`
- **Modify**:
  - `jules-plugin/.claude-plugin/plugin.json` (add `"deprecated": true`, append deprecation notice to `description`)
  - `README.md` (add Plugin install section)
- **Move / Delete**: none. Do not delete `jules-plugin/` — Spec 020 owns retirement.

## Approach

1. WebFetch https://code.claude.com/docs/en/plugins-reference and confirm the current required-keys list and `marketplace.json` shape (single-plugin form). Record the doc revision in the PR Confidence block.
2. Read the existing `jules-plugin/.claude-plugin/plugin.json` to mirror author/license fields and avoid drift from the project's known-good metadata.
3. Author `.claude-plugin/plugin.json` per §2.3 of `Plan/000-overview.md`: `name: "agency-system"`, `version: "0.1.0"`, `description`, `author`, `homepage: "https://github.com/netzkontrast/the-agency-system"`, `mcpServers.agency-system` pointing at the entry created in Spec 001 (`${CLAUDE_PLUGIN_ROOT}/servers/agency-mcp/run.py`). Reference `.mcp.json` only — do not duplicate the command line.
4. Author `.claude-plugin/marketplace.json` as a single-plugin marketplace descriptor (name, owner, plugin entry pointing to this repo) so the human can `/plugin install <url>` without cloning first.
5. Edit `jules-plugin/.claude-plugin/plugin.json`: add top-level `"deprecated": true`, append `" — DEPRECATED: superseded by agency-system at repo root; will be removed in Spec 020."` to its `description`. Leave every other field untouched — Spec 020 deletes the file outright.
6. Edit `README.md`: add a `## Plugin install` H2 with two fenced blocks — `claude --plugin-dir .` for local dev and `/plugin install agency-system@netzkontrast` for marketplace. Cite spec 002 by path in a footer comment.
7. RED: write `tests/smoke/test_manifest.py` with `test_root_manifest_has_required_keys`, `test_marketplace_descriptor_is_single_plugin_shape`, and `test_jules_plugin_manifest_is_deprecated`. Watch them fail before edits, then green.
8. Verify the boot path end-to-end manually: from a clean shell run `claude --plugin-dir .` then `/plugin list` — agency-system v0.1.0 must appear. Paste the listing under `## Evidence`.

## Acceptance (Gherkin)

```gherkin
# anchor: 002.1
Scenario: Root manifest exposes agency-system to Claude Code
  Given the file .claude-plugin/plugin.json exists at repo root
  When a developer runs "claude --plugin-dir ." in the repo
  And then runs the "/plugin list" slash command
  Then the output contains a row "agency-system v0.1.0"
  And the row's MCP-server count is at least 1

# anchor: 002.2
Scenario: Marketplace descriptor is single-plugin shape
  Given the file .claude-plugin/marketplace.json exists at repo root
  When the operator runs "python -m json.tool .claude-plugin/marketplace.json"
  Then the process exits with status 0
  And the parsed JSON has a top-level "plugins" array with exactly one entry
  And that entry's "name" field equals "agency-system"

# anchor: 002.3
Scenario: Legacy jules-plugin manifest is flagged deprecated
  Given jules-plugin/.claude-plugin/plugin.json exists from a prior wave
  When the operator parses the file as JSON
  Then the top-level key "deprecated" is true
  And the "description" field ends with the substring "superseded by agency-system at repo root"
```

## Out of scope

- Removing `jules-plugin/` from the working tree (Spec 020).
- Adding any skill or command to the manifest (Specs 005, 007, 015, 016 add per-domain skills; `/help` will be empty in this spec).
- Publishing the plugin to a public marketplace registry (out of scope for the entire wave A).
- Wiring CI to validate the manifest on push (deferred; smoke test in `tests/smoke/` is the gate for now).

## References

- `Plan/JULES_PROTOCOL.md` (gates 1–4, §7 plugin conventions)
- `Plan/000-overview.md` §2.3 (`plugin.json` is sole file under `.claude-plugin/`)
- `Plan/SOURCES.md` (Claude Code Plugins Reference + Guide URLs)
- Spec 001 (`.mcp.json` and `servers/agency-mcp/run.py` entry point)
