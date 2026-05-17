---
spec_id: 004a
slug: music-lib-port
status: ready
owner: jules
depends_on: [003]
affects:
  - servers/agency-mcp/src/agency_mcp/tools/__init__.py
  - servers/agency-mcp/src/agency_mcp/tools/mastering/
  - servers/agency-mcp/src/agency_mcp/tools/shared/
  - servers/agency-mcp/src/agency_mcp/tools/state/
  - servers/agency-mcp/src/agency_mcp/tools/cloud/
  - servers/agency-mcp/src/agency_mcp/tools/sheet_music/
  - tests/unit/tools/__init__.py
  - tests/unit/tools/test_imports_smoke.py
source-repos:
  - bitwize-music @ v0.91.0
estimated_jules_sessions: 2
domain: music
wave: A
deps: []
---

> **Jules: read `Plan/JULES_PROTOCOL.md` before starting.** Run gates 1→4 in order:
> (1) Confidence ≥ 0.90, (2) TDD Red-Green-Refactor, (3) Evidence pasted under `## Evidence`, (4) Self-Review answered.
> Branch: `claude/agency-plugin-refactor-PgMQ4`. Only modify paths under `affects:` below.
> Source repos under `source-repos:` are clone-and-read-only into `~/work/vendor/`; never commit them.
> If anything is ambiguous, open a draft PR labelled `[BLOCKED: clarification]` and stop — do not guess.

# Spec 004a — Music Lib Port

## Why

Spec 004 (PR #36, currently `[BLOCKED]`) tried to port bitwize-music's 16 handler modules but those handlers import from `tools.mastering.*` (~17 submodules), `tools.shared.*` (2 submodules), `tools.state.*` (2 submodules), and dynamically from `tools.cloud.*` and `tools.sheet-music.*`. None of those packages existed on the work branch, so the resulting PR couldn't import without bitwize-music's source bleeding into `PYTHONPATH`.

This spec ports the bitwize-music `tools/` subtree verbatim into `agency_mcp/tools/`, rewriting only the import roots so handler modules can resolve their dependencies from a clean install. After this spec merges, a fresh spec 004 (handler port) can land cleanly against the new package.

Concretely: every `from tools.mastering.X` in the handler source becomes resolvable via `agency_mcp.tools.mastering.X` (and the same for `shared`, `state`, `cloud`, `sheet_music`). No behaviour change; only relocation + import-root rewrite.

## Done When

- [ ] `python -c "import agency_mcp.tools.mastering; import agency_mcp.tools.shared.config; import agency_mcp.tools.shared.text_utils; import agency_mcp.tools.state.indexer; import agency_mcp.tools.state.parsers"` exits 0 from a clean install (NO vendor on PYTHONPATH).
- [ ] `python -c "import importlib; importlib.import_module('agency_mcp.tools.cloud'); importlib.import_module('agency_mcp.tools.sheet_music')"` exits 0 (the dynamically-loaded subpackages exist as importable namespaces).
- [ ] Every `.py` file under `agency_mcp/tools/` parses (`python -m py_compile <file>` exit 0 for each).
- [ ] `rg 'from tools\.|import tools\.' servers/agency-mcp/src/agency_mcp/tools/` returns empty (all internal cross-references rewritten to absolute `agency_mcp.tools.*` form).
- [ ] `rg 'bitwize_music' servers/agency-mcp/src/agency_mcp/tools/` returns empty (no stale package-name references).
- [ ] `pytest -x tests/unit/tools/test_imports_smoke.py` exits 0 — the smoke test enumerates every submodule under `agency_mcp.tools.*` via `pkgutil.walk_packages` and asserts each one imports.
- [ ] **Vendor copy provenance:** every `.py` ported from bitwize carries a top-of-file comment recording the upstream path and the bitwize-music v0.91.0 commit SHA. Format: `# Vendored from bitwize-music@v0.91.0: <upstream/path>`.

## Source clones (run first)

```bash
git clone --depth=1 --branch=v0.91.0 \
  https://github.com/bitwize-music-studio/claude-ai-music-skills.git \
  ~/work/vendor/bitwize-music
```

The packages to port live under `~/work/vendor/bitwize-music/tools/`. Inventory them with `find ~/work/vendor/bitwize-music/tools -name '*.py' | sort` before starting — exact submodule counts matter for the smoke test.

If clone fails per `Plan/SOURCES.md` verification flag, open a draft PR labelled `[BLOCKED: verify-source-url]`. Do not guess an alternate URL.

## Files

- **Create — top-level**:
  - `servers/agency-mcp/src/agency_mcp/tools/__init__.py` — empty namespace package.
- **Create — `mastering/`** (port all .py files from `~/work/vendor/bitwize-music/tools/mastering/`):
  - `servers/agency-mcp/src/agency_mcp/tools/mastering/__init__.py`
  - `mastering/adm_validation.py`, `album_signature.py`, `analyze_tracks.py`, `anchor_selector.py`, `archival.py`, `ceiling_guard.py`, `codec_preview.py`, `coherence.py`, `config.py`, `fix_dynamic_track.py`, `layout.py`, `master_tracks.py`, `metadata.py`, `mono_fold.py`, `mono_fold_report.py`, `qc_tracks.py`, `signature_persistence.py`
  - Any other `.py` files present in the source `tools/mastering/` directory.
- **Create — `shared/`**:
  - `servers/agency-mcp/src/agency_mcp/tools/shared/__init__.py`
  - `shared/config.py`, `shared/text_utils.py`
  - Any other `.py` present in the source `tools/shared/`.
- **Create — `state/`** (NOTE: this is the bitwize handler-side state helpers, NOT the agency `state/cache.py` from Spec 003):
  - `servers/agency-mcp/src/agency_mcp/tools/state/__init__.py`
  - `state/indexer.py`, `state/parsers.py`
  - Any other `.py` present in the source `tools/state/`.
- **Create — `cloud/`** (only the package skeleton if no `.py` files exist; the handlers load it via `importlib`):
  - `servers/agency-mcp/src/agency_mcp/tools/cloud/__init__.py`
  - Any `.py` files present in the source `tools/cloud/`.
- **Create — `sheet_music/`** (rename from source `tools/sheet-music/` — Python does not allow hyphens in module names; the handlers' dynamic loader will need the rename, but that fix lives in spec 004's redo):
  - `servers/agency-mcp/src/agency_mcp/tools/sheet_music/__init__.py`
  - Any `.py` files present in the source `tools/sheet-music/`.
- **Create — tests**:
  - `tests/unit/tools/__init__.py`
  - `tests/unit/tools/test_imports_smoke.py` — uses `pkgutil.walk_packages(agency_mcp.tools.__path__, prefix='agency_mcp.tools.')` to enumerate and import every submodule.
- **Modify**: none.

## Approach

1. **Gate 1 — Confidence.** Confirm spec 003 merged (`git log claude/agency-plugin-refactor-PgMQ4 --oneline | rg 'Spec 003'`). Confirm spec 004 PR #36 is in `[BLOCKED]` state and does NOT need rebasing onto this spec's output (a fresh spec 004 will be dispatched after this one merges; PR #36 will be closed). Cite both confirmations in the Confidence table.
2. **Clone source.** Run the clone command. Capture the bitwize v0.91.0 commit SHA (`git -C ~/work/vendor/bitwize-music rev-parse HEAD`) — every ported file's header comment uses it.
3. **Inventory.** `find ~/work/vendor/bitwize-music/tools -name '*.py' | sort` — write the list into the PR Confidence block. This is the ground truth for "did I port everything?".
4. **Port `tools/mastering/`.** For each `.py` file under `~/work/vendor/bitwize-music/tools/mastering/`:
   - Copy bytes verbatim to the matching path under `servers/agency-mcp/src/agency_mcp/tools/mastering/`.
   - Prepend the provenance comment: `# Vendored from bitwize-music@v0.91.0: tools/mastering/<filename>` on line 1 (preserve any existing module docstring on line 2+).
   - Rewrite imports: every `from tools.X` → `from agency_mcp.tools.X` (or `import agency_mcp.tools.X as tools_X` style if the original used `import tools.X`); every `from bitwize_music.X` → `from agency_mcp.X` per the analogous spec 004 rule. Use a small sed/Python script and paste the script into Self-Review.
   - Do **not** rewrite stdlib imports (`import os`, `from pathlib import Path`, etc.).
5. **Port `tools/shared/`, `tools/state/`, `tools/cloud/`, `tools/sheet-music/`** with the same protocol. The `sheet-music` → `sheet_music` rename (hyphen → underscore) is the only structural change; document it in `references/sheet-music-rename.md`.
6. **Write the smoke test.** `tests/unit/tools/test_imports_smoke.py` does:
   ```python
   import pkgutil
   import importlib
   import agency_mcp.tools
   def test_every_submodule_imports():
       failed = []
       for _, name, _ in pkgutil.walk_packages(agency_mcp.tools.__path__, prefix='agency_mcp.tools.'):
           try:
               importlib.import_module(name)
           except Exception as e:
               failed.append(f"{name}: {e}")
       assert not failed, f"Failed imports:\n" + "\n".join(failed)
   ```
   Run **RED** before any port (the package doesn't exist), then **GREEN** after porting. Paste both runs in Evidence.
7. **Gate 3 — Evidence.** Paste under `## Evidence`:
   - The bitwize v0.91.0 commit SHA.
   - The full output of `find ~/work/vendor/bitwize-music/tools -name '*.py' | sort | wc -l` and the matching count after porting (`find servers/agency-mcp/src/agency_mcp/tools -name '*.py' ! -name '__init__.py' | wc -l`) — they must match (modulo the sheet-music → sheet_music rename, which is 1:1).
   - The 5 import smoke commands from Done-When listed above, each followed by `echo $?` showing 0.
   - The empty-output proof for the two `rg` checks (Done-When 4, 5).
   - The full `pytest -x tests/unit/tools/test_imports_smoke.py` output.
8. **Gate 4 — Self-Review.** Answer the 3 questions. In #1 (drift), name any submodule from the source inventory that was deliberately NOT ported (and why). In #3 (pattern), name one concrete sed/Python-script convention you'd refine for the next "port a vendor package verbatim" spec.

## Acceptance (Gherkin)

```gherkin
# anchor: 004a.1
Scenario: Every bitwize tools submodule resolves under agency_mcp.tools.*
  Given the bitwize-music v0.91.0 tools/ subtree has been ported per this spec
  And no PYTHONPATH addition includes ~/work/vendor/bitwize-music
  When the operator runs the 5 import commands from Done-When
  Then each exits with status 0

# anchor: 004a.2
Scenario: Internal cross-references use absolute agency_mcp.tools.* paths only
  Given the ported tools/ subtree
  When the operator runs "rg 'from tools\\.|import tools\\.' servers/agency-mcp/src/agency_mcp/tools/"
  Then the output is empty
  And no occurrence of "bitwize_music" remains anywhere under the tools/ tree

# anchor: 004a.3
Scenario: pkgutil walks the entire tools namespace without ImportError
  Given the ported tools/ subtree and the smoke test in place
  When the operator runs "pytest -x tests/unit/tools/test_imports_smoke.py"
  Then the test passes
  And the failed-imports list in the assertion message is empty

# anchor: 004a.4
Scenario: sheet-music → sheet_music rename is documented
  Given Python forbids hyphens in module names
  When a reviewer inspects Plan/004a-music-lib-port/references/sheet-music-rename.md
  Then the doc explains the rename
  And references which dynamic-loader call sites in the handlers will need adjustment (spec 004 redo)
```

## Out of scope

- The handler modules themselves (`servers/agency-mcp/src/agency_mcp/handlers/music/`) — spec 004 redo owns those, dispatched after this merges.
- Wiring the music tools into the FastMCP registry — spec 008 owns Code Mode registration.
- The `lib/audio_processing/` path mentioned in the original spec 004 Approach §3 — that path was misnamed in the source spec; the actual bitwize source uses `tools/mastering/` (the audio-processing pipeline) and `tools/shared/` (helpers). No `lib/` subtree exists in bitwize.
- Rewriting any handler-side imports — the handlers stay where Jules left them (PR #36, still `[BLOCKED]`); they'll be replaced by the fresh spec 004 dispatch.
- Adding any new functionality, refactoring, or improving the bitwize source — VERBATIM port only.

## References

- `Plan/JULES_PROTOCOL.md` (gates 1–4, §4 source-repo rules, anti-pattern §6 on affects: drift)
- `Plan/SOURCES.md` (bitwize-music v0.91.0 clone command)
- Spec dependency: `Plan/003-unified-statecache-port/spec.md` (the agency-side StateCache; note this is NOT the same as the bitwize handler-side `tools.state.indexer` being ported here).
- Forward link: `Plan/004-music-handlers-port/spec.md` (will be redispatched after this merges, against the new `agency_mcp.tools.*` package).
- Background: PR #36 `[BLOCKED: missing-lib-package]` — the original spec 004 attempt that surfaced this gap.
- Vendor source (read-only): `~/work/vendor/bitwize-music/tools/`
