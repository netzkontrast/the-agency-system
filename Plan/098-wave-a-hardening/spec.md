---
spec_id: 098
slug: wave-a-hardening
status: ready
owner: jules
depends_on: [003, 019, 004a, 002]
affects:
  - servers/agency-mcp/src/agency_mcp/state/cache.py
  - servers/agency-mcp/src/agency_mcp/state/migrators/bitwize_v091_to_agency.py
  - servers/agency-mcp/src/agency_mcp/tools/validate_help_completeness.py
  - servers/agency-mcp/src/agency_mcp/tools/state/indexer.py
  - servers/agency-mcp/src/agency_mcp/tools/cloud/upload_to_cloud.py
  - servers/agency-mcp/pyproject.toml
  - .claude-plugin/marketplace.json
  - README.md
  - state/schema/state.schema.json
  - tests/unit/state/test_cache.py
  - tests/unit/tools/test_imports_smoke.py
  - tests/integration/test_migration.py
source-repos: []
estimated_jules_sessions: 1
domain: cross
wave: A
---

> **Jules: read `Plan/JULES_PROTOCOL.md` before starting.** Run gates 1→4 in order:
> (1) Confidence ≥ 0.90, (2) TDD Red-Green-Refactor, (3) Evidence pasted under `## Evidence`, (4) Self-Review answered.
> Branch: `claude/agency-plugin-refactor-PgMQ4`. Only modify paths under `affects:` below.
> If anything is ambiguous, open a draft PR labelled `[BLOCKED: clarification]` and stop — do not guess.

# Spec 098 — Wave A Hardening (Codex Bot P1 Cleanup)

## Why

The Codex bot reviewed PRs #34 (Spec 003 StateCache), #37 (Spec 019 migration), #38 (Spec 004a tools port), and #32 (Spec 002 manifest) and flagged **~17 P1 findings** that landed unfixed because the PRs merged before the comments arrived (Codex review is async). These are the kind of correctness bugs that downstream specs (011, 013, 014, ...) will hit during invocation — *if the smoke test doesn't catch it now, the first real call does*.

This spec is the consolidated cleanup pass. It does NOT add features; it makes the merged-in-haste Wave-A code actually correct. Every change is justified by a specific Codex review comment cited in the **References** section.

## Done When

- [ ] `tests/unit/state/test_cache.py` no longer imports `jsonschema` without the dep being declared in `pyproject.toml` (PR #34 P1).
- [ ] `state/cache.py::_write_to_disk` propagates IO errors (does not silently swallow); test added that asserts `write()` raises on disk-full simulation (PR #34 P1).
- [ ] `state/cache.py` reload rejects `_version != "1.0.0"` with a clear error (PR #34 P1).
- [ ] `state/cache.py::update` removes keys absent from the patch (or documents non-removal as deliberate) (PR #34 P2 → P1 if you find drift bug).
- [ ] `state/cache.py` reload strips unknown top-level keys per `additionalProperties: false` (PR #34 P2).
- [ ] `state/migrators/bitwize_v091_to_agency.py` does NOT add a `_migration` top-level key to migrated state (PR #37 P1). If migration metadata is needed, store it in a sibling file `.migration-receipt.json` inside `~/.agency-system/`.
- [ ] `bitwize_v091_to_agency.py` does NOT silently skip `config.yaml` write when PyYAML is missing — fail loudly with structured error (PR #37 P1).
- [ ] Idempotency check uses hash of `{state, config, deprecated_marker}` triple, not just state hash, so partial runs are re-runnable (PR #37 P1).
- [ ] All untyped paths in `bitwize_v091_to_agency.py` (lines 46, 48, 77, 85, 97, 128, 143, 152, 161, 170, 195) are wrapped in structured error contracts — no uncaught `AttributeError`/`TypeError`/`PermissionError` leak as raw stack traces (PR #37 P1 ×6).
- [ ] `tools/validate_help_completeness.py:17` sys.path bootstrap uses `Path(__file__).resolve().parents[N]` correctly to land at repo root (PR #38 P1).
- [ ] `tools/validate_help_completeness.py:101` `plugin_root` resolves to repo root, not `tools/` (PR #38 P1).
- [ ] `tools/state/indexer.py:400` `_PROJECT_ROOT` resolves to repo root so `skills/` + `.claude-plugin/` are indexable (PR #38 P1). After fix: `python -c "from agency_mcp.tools.state.indexer import rebuild; r=rebuild(); print(r['skills']['count'])"` reports ≥1.
- [ ] `tools/state/indexer.py:47` sys.path bootstrap matches the validate_help fix above (PR #38 P1).
- [ ] `tests/unit/tools/test_imports_smoke.py:3` adds sys.path setup OR uses `pytest` rootdir conftest, so the smoke test collects on a fresh checkout (PR #38 P1).
- [ ] `tools/cloud/upload_to_cloud.py:53` replaces `sys.exit(1)` with `raise ImportError(...)` or wraps in `try/except` so missing optional dep doesn't kill the smoke importer (PR #38 P2).
- [ ] `tests/unit/tools/test_imports_smoke.py:9` catches `SystemExit` in addition to `Exception` (PR #38 P2).
- [ ] `.claude-plugin/marketplace.json`: `name` field changed from `agency-marketplace` to `netzkontrast` to match the install instruction `agency-system@netzkontrast` documented in `README.md` (PR #32 P1).
- [ ] All tests pass: `pytest -x tests/unit/state/ tests/unit/tools/ tests/integration/test_migration.py`.
- [ ] No new runtime dependencies added without spec amendment (Anti-Pattern #5 discipline).

## Source clones (run first)

```bash
# No external clones required — this spec works entirely on the agency-system tree.
# Reference: review threads on closed PRs #32, #34, #37, #38 via:
# gh pr view 34 --comments  # (or use MCP)
```

## Files

- **Modify**:
  - `servers/agency-mcp/src/agency_mcp/state/cache.py` — error propagation + version check + key removal + additionalProperties strip
  - `servers/agency-mcp/src/agency_mcp/state/migrators/bitwize_v091_to_agency.py` — schema-compliant output + structured errors + full-artifact idempotency
  - `servers/agency-mcp/src/agency_mcp/tools/validate_help_completeness.py` — sys.path + plugin_root fix
  - `servers/agency-mcp/src/agency_mcp/tools/state/indexer.py` — sys.path + _PROJECT_ROOT fix
  - `servers/agency-mcp/src/agency_mcp/tools/cloud/upload_to_cloud.py` — `sys.exit` → `ImportError`
  - `servers/agency-mcp/pyproject.toml` — declare `jsonschema>=4.21.0` if not present (already added in spec 012; re-verify) and `PyYAML>=6.0` (already added in spec 012)
  - `.claude-plugin/marketplace.json` — `name: "netzkontrast"`
  - `README.md` — install instruction sentence verified consistent with marketplace name
  - `state/schema/state.schema.json` — verify `additionalProperties: false` still holds; no change expected
  - `tests/unit/state/test_cache.py` — add error-propagation + version-check tests
  - `tests/unit/tools/test_imports_smoke.py` — sys.path fix + `SystemExit` catch
  - `tests/integration/test_migration.py` — test for `_migration` key absence + partial-run idempotency
- **Create**: none.
- **Move / Delete**: none.

## Approach

1. **Gate 1 — Confidence.** Run `mcp__github__pull_request_read get_review_comments` against PRs #34, #37, #38, #32 to confirm each Codex P1 is still applicable on `claude/agency-plugin-refactor-PgMQ4` HEAD. Cite each in the PR Confidence table.
2. **TDD ordering.** Write the failing tests FIRST in this order: cache-error-propagation, migration-no-`_migration`-key, indexer-skills-count, marketplace-name. RED. Then fix the code one P1 at a time, watching each test go GREEN.
3. **StateCache hardening** (`state/cache.py`):
   - Wrap `_write_to_disk` write call in `try/except` that **re-raises** with context; never swallow `IOError`/`OSError`.
   - In `_load_from_disk`, check `data.get("_version")` against the schema constant; raise `ValueError` if mismatch.
   - In `_load_from_disk`, strip keys not in `{music, novel, jules, agentic, _version}` (i.e. enforce `additionalProperties: false` at read time, not just at write time).
   - In `update(namespace, patch)`, define semantics: "patch replaces namespace dict entirely" (current behavior is partial-merge). Document in docstring.
4. **Migration hardening** (`bitwize_v091_to_agency.py`):
   - Remove the `_migration` key write from `migrated_state`. Move that metadata to a separate JSON file `dest_dir/.migration-receipt.json` containing `{input_hash, completed_at, source_files, dest_files}`.
   - For PyYAML missing: raise `RuntimeError("PyYAML required for config.yaml migration; install with: uv pip install pyyaml")` BEFORE writing state, so partial migrations don't happen.
   - Change idempotency check to hash `(state_hash, config_hash, deprecated_marker_present)` so partial runs are recoverable.
   - Wrap each of: backup `mkdir`+`copy2`, parent `mkdir`, `merge_config` mapping check, `config.yaml` parse — in structured error returns `{ok: False, error_type, message, partial_state: {...}}`.
5. **Tools-bootstrap hardening** (`tools/validate_help_completeness.py` + `tools/state/indexer.py`):
   - At top of each file:
     ```python
     from pathlib import Path
     _REPO_ROOT = Path(__file__).resolve().parents[5]  # tools/X/file.py → repo root (verify the parent count!)
     import sys
     if str(_REPO_ROOT / "servers" / "agency-mcp" / "src") not in sys.path:
         sys.path.insert(0, str(_REPO_ROOT / "servers" / "agency-mcp" / "src"))
     ```
   - In `indexer.py`, change `_PROJECT_ROOT = ...` to point to `_REPO_ROOT`, then verify `_REPO_ROOT / "skills"` and `_REPO_ROOT / ".claude-plugin"` exist.
   - Add a regression test that runs `rebuild()` and asserts `result["skills"]["count"] >= 1`.
6. **Cloud upload hardening** (`tools/cloud/upload_to_cloud.py`):
   - Replace `sys.exit(1)` at module load with `raise ImportError("rclone not available — install before using cloud tools")`.
   - In smoke test, wrap each import in `try/except (ImportError, SystemExit)`.
7. **Manifest hardening** (`.claude-plugin/marketplace.json` + `README.md`):
   - `name`: `"netzkontrast"` (was `"agency-marketplace"`).
   - Re-verify `README.md` install sentence reads `claude plugin install agency-system@netzkontrast`.
8. **Gate 3 — Evidence.** Paste `pytest -x tests/unit/state/ tests/unit/tools/ tests/integration/test_migration.py` output, the indexer skills count, and the marketplace-name check into the PR `## Evidence`.
9. **Gate 4 — Self-Review.** Answer the 3 questions. Specifically flag any Codex P1 you decided NOT to fix and why (e.g. if cache `update()` semantics are intentionally partial-merge per Spec 003 contract).

## Acceptance (Gherkin)

```gherkin
# anchor: 098.1
Scenario: StateCache propagates write errors instead of swallowing them
  Given the disk is read-only
  When the operator calls `cache.write(namespace="music", data={...})`
  Then an OSError is raised
  And the in-memory state remains unmodified

# anchor: 098.2
Scenario: Migrator does not emit _migration key in state output
  Given a clean bitwize state at ~/.bitwize-music/cache/state.json
  When the operator runs the migrator to completion
  Then the resulting ~/.agency-system/cache/state.json has top-level keys only in {music, novel, jules, agentic, _version}
  And the migration receipt lives in ~/.agency-system/.migration-receipt.json

# anchor: 098.3
Scenario: indexer.rebuild() finds the skills folder
  Given the agency-system repo is checked out at /repo
  When `from agency_mcp.tools.state.indexer import rebuild; r = rebuild()` is executed
  Then r["skills"]["count"] is ≥ 1
  And r["claude_plugin"]["manifest_present"] is True

# anchor: 098.4
Scenario: marketplace install instruction matches manifest name
  Given the .claude-plugin/marketplace.json is parsed
  And README.md is read
  When the operator extracts the install instruction "agency-system@<name>"
  Then <name> matches the marketplace.json "name" field exactly
```

## Out of scope

- PR #41 (Spec 004) Codex findings — those are in-flight on the open PR and are tracked there, not here.
- PR #40 (Spec 012) Codex findings — same as above.
- Adding new features. This is correctness-only.
- Refactoring beyond what each Codex P1 requires.
- Renaming any tools, modules, or directories.

## References

- `Plan/JULES_PROTOCOL.md` — working protocol (especially Anti-Pattern #5 "silent dep adds" and Gate 3 evidence)
- `Plan/000-overview.md` §1 (target tree), §2.1 (FastMCP conventions)
- PR #34 review comments (Codex bot, 5 inline P1/P2 threads on `state/cache.py`)
- PR #37 review comments (Codex bot, 13 inline P1/P2 threads on `bitwize_v091_to_agency.py`)
- PR #38 review comments (Codex bot, 7 inline P1/P2 threads on `tools/validate_help_completeness.py`, `tools/state/indexer.py`, `tools/cloud/upload_to_cloud.py`)
- PR #32 review comments (Codex bot, 1 inline P1 thread on `marketplace.json`)
- Spec 003 (`Plan/003-unified-statecache-port/spec.md`) — StateCache contract
- Spec 019 (`Plan/019-state-migration-from-bitwize/spec.md`) — migrator contract
- Spec 004a (`Plan/004a-music-lib-port/spec.md`) — tools/ subtree port contract
- Spec 002 (`Plan/002-manifest-and-marketplace/spec.md`) — marketplace name contract
- `Plan/_lessons-learned/13-codex-bot-pr-reviews-are-gold.md` — why this spec exists
