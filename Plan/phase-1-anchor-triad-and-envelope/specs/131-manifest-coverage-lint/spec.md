---
spec_id: 131
slug: manifest-coverage-lint
status: draft
owner: jules
depends_on: [008]
affects:
  - servers/agency-mcp/src/agency_mcp/tools/check_codemode_manifest.py
  - servers/agency-mcp/src/agency_mcp/lib/codemode/registry.py
  - tests/unit/codemode/test_manifest_coverage.py
  - .github/workflows/manifest-coverage.yml
  - Plan/000-overview.md
source-repos: []
estimated_jules_sessions: 1
domain: cross
wave: C
---

> **Jules: read `Plan/JULES_PROTOCOL.md` before starting.** Run gates 1→4 in order:
> (1) Confidence ≥ 0.90, (2) TDD Red-Green-Refactor, (3) Evidence pasted under `## Evidence`, (4) Self-Review answered.
> Branch: `Master` (default base for fresh specs post-Wave-A; see JULES_PROTOCOL.md §3). Only modify paths under `affects:` below.
> Source repos under `source-repos:` are clone-and-read-only into `~/work/vendor/`; never commit them.
> If anything is ambiguous, open a draft PR labelled `[BLOCKED: clarification]` and stop — do not guess.

# Spec 131 — Code Mode Manifest Coverage Lint (drift detector)

## Why

Spec 008's `lib/codemode/registry.py:classify()` raises `ValueError("unclassified tool: <name>")` at boot when a tool is registered without a manifest entry — the loud-fail discipline is correct, but it fires only **after** a developer has shipped the new handler and tried to start the server. For Jules-fanned-out sessions that don't routinely boot the server (most music/novel handler PRs only run `pytest -x tests/unit/<domain>/`), the drift surfaces at integration time on Master, not in the PR's checks. The mirror failure is silent: a deleted handler that still has a stale manifest entry boots fine because `classify()` never gets called for the now-missing tool, but the entry rots indefinitely. Spec 008's manifest (`codemode/manifest.json`) is at 110 entries today; without a coverage lint, every new spec that adds tools (011, 011a, 013, 014, 015, 016, 021) silently drifts further. The fix is a `check_codemode_manifest.py` script that walks every `@mcp.tool` registration site (or, more reliably, boots `create_mcp()` in a subprocess and dumps `mcp._tools.keys()`), diffs against the manifest's `tools` keys, and exits non-zero on either-direction divergence. Wired into a GitHub Actions check, the lint fails the PR before merge — turning the existing `ValueError` from a runtime tripwire into a CI tripwire. Distinct from Spec 008 (which only validates at boot) and Spec 022 (which boots `claude --plugin-dir` once for dev verification, not per-PR).

## Done When

- [ ] `servers/agency-mcp/src/agency_mcp/tools/check_codemode_manifest.py` is an executable Python script that: (a) boots `create_mcp()` in-process, (b) collects `registered = set(mcp._tools.keys())`, (c) loads `codemode/manifest.json` and computes `declared = set(manifest["tools"].keys())`, (d) prints two sorted diffs `MISSING_FROM_MANIFEST = registered - declared` and `STALE_IN_MANIFEST = declared - registered`, (e) exits 0 iff both sets are empty, else exits 1.
- [ ] `agency_mcp.lib.codemode.registry` gains a public `manifest_diff() -> tuple[set[str], set[str]]` helper that returns `(missing_from_manifest, stale_in_manifest)` — the script and the unit test both consume it; the boot-time `classify()` check stays unchanged.
- [ ] `tests/unit/codemode/test_manifest_coverage.py` exercises three scenarios via a temp manifest fixture: clean parity (no diff), missing entry (one registered tool absent from manifest), stale entry (one manifest tool not registered). Each scenario asserts the right `manifest_diff()` output and the right script exit code.
- [ ] `.github/workflows/manifest-coverage.yml` runs the script on every PR that touches `servers/agency-mcp/src/agency_mcp/handlers/**` OR `servers/agency-mcp/src/agency_mcp/codemode/manifest.json`. Workflow uses `uv pip install -e servers/agency-mcp/`, then `python servers/agency-mcp/src/agency_mcp/tools/check_codemode_manifest.py`. Job name: `manifest-coverage`. Required status check (admin opt-in left to repo owner; spec does not toggle branch protection).
- [ ] `Plan/000-overview.md` §2.1 #5 (tool classification) gains a one-line addendum citing this spec and the lint script path, so future spec authors know to run the script locally before opening a PR.
- [ ] `pytest -x tests/unit/codemode/test_manifest_coverage.py` exits 0.
- [ ] The script handles the "Code Mode unavailable" graceful-fallback path (Spec 008's `_CODE_MODE_AVAILABLE = False` branch) — if `CodeMode` failed to import, `mcp._tools` still contains every tool because the manifest hides nothing; the diff logic is unaffected.

## Source clones (run first)

None. Local references:
- `servers/agency-mcp/src/agency_mcp/lib/codemode/registry.py:93-108` — `classify()` raises on missing entries; this spec is its CI-side mirror.
- `servers/agency-mcp/src/agency_mcp/codemode/manifest.json` — the 110-entry manifest this script audits.
- `servers/agency-mcp/src/agency_mcp/tools/validate_help_completeness.py:34-39` — the precedent pattern for plugin-root walking validators; this script follows the same `if __name__ == "__main__"` shape and Colors output convention.

Reference docs (read but do not clone):
- https://docs.github.com/en/actions/using-workflows/triggering-a-workflow#paths-filter — for the `paths:` filter that scopes the workflow to MCP changes only.
- https://gofastmcp.com/servers/server (FastMCP's `mcp._tools` private attribute is the only documented enumeration path; confirm shape in PR Confidence).

## Files

- **Create**:
  - `servers/agency-mcp/src/agency_mcp/tools/check_codemode_manifest.py` — executable script (chmod +x, shebang `#!/usr/bin/env python3`).
  - `tests/unit/codemode/test_manifest_coverage.py` — three-scenario pytest.
  - `.github/workflows/manifest-coverage.yml` — GitHub Actions workflow scoped to MCP paths.
- **Modify**:
  - `servers/agency-mcp/src/agency_mcp/lib/codemode/registry.py` — add `manifest_diff()` helper after the existing `background_companions()` definition. Pure additive — does not alter `classify()` semantics.
  - `Plan/000-overview.md` §2.1 #5 — one-line addendum pointing at this spec.
- **Move / Delete**: none.

## Approach

1. **Gate 1 — Confidence.** Verify Spec 008 has shipped `lib/codemode/registry.py` with `load_manifest()` cached via `lru_cache`. Run `python -c "from agency_mcp.server import create_mcp; m=create_mcp(); print(len(m._tools))"` to confirm the registered count (expected ≥110); run `python -c "import json; print(len(json.load(open('servers/agency-mcp/src/agency_mcp/codemode/manifest.json'))['tools']))"` to confirm manifest entry count. If they already differ, cite the divergence in PR Confidence — that's the bug this spec retro-detects.
2. **Implement `manifest_diff()`.** In `registry.py`, add a public function that returns `(registered - declared, declared - registered)`. Wire it through `create_mcp()` so the test can stub a temporary manifest path via the existing `load_manifest(path=...)` override (which already exists per Spec 008's contract). The function MUST NOT mutate the lru-cache; tests call `_reset_cache()` between scenarios.
3. **Build the script.** `check_codemode_manifest.py` does: import `create_mcp` + `manifest_diff`; boot the server; call the helper; format two sorted bullet lists (or a single "OK" line); exit 0 / 1. Use the existing `agency_mcp.tools.shared.colors.Colors` palette so the output matches `validate_help_completeness.py`. Total ≤80 LOC including shebang + docstring.
4. **Author the GitHub Actions workflow.** `.github/workflows/manifest-coverage.yml` triggers on `pull_request` with `paths: ['servers/agency-mcp/src/agency_mcp/handlers/**', 'servers/agency-mcp/src/agency_mcp/codemode/manifest.json', 'servers/agency-mcp/src/agency_mcp/lib/codemode/**']`. Steps: checkout, `uv pip install -e servers/agency-mcp/`, run the script, on failure print the diff as a GitHub Annotation (`::error::missing from manifest: <name>`). Use `actions/setup-python@v5` pinned to Python 3.11 to match `pyproject.toml`.
5. **TDD — Gate 2.** RED: write `test_manifest_coverage.py` with three pytest cases. Each builds a tiny temp manifest, monkeypatches `load_manifest` (or uses its existing `path=` override), constructs a minimal `FastMCP` with two synthetic tools, and asserts the expected `manifest_diff()` output + script exit code (use `subprocess.run([sys.executable, "-m", "agency_mcp.tools.check_codemode_manifest"])` to test the script end-to-end). Run — must fail (`manifest_diff` doesn't exist).
6. **GREEN.** Implement the helper + script. Re-run; tests pass. Verify the script run against the live tree exits 0 (today's manifest should already be in parity per Spec 008's boot check; if it isn't, file a follow-up Task and pin the spec on `[BLOCKED: pre-existing drift]`).
7. **REFACTOR.** Extract the diff-formatting block into `_format_diff(missing, stale) -> str` so future Plan-side tooling can reuse it.
8. **Wire the workflow.** Verify the YAML syntax via `python -c "import yaml; yaml.safe_load(open('.github/workflows/manifest-coverage.yml'))"`. Do NOT enable branch-protection auto-fail; that's a repo-admin decision out of scope.
9. **Update overview.** Add a one-line addendum to `Plan/000-overview.md` §2.1 #5 after the existing "Tool classification" sentence: `Lint enforced by Spec 131 via servers/agency-mcp/src/agency_mcp/tools/check_codemode_manifest.py.`
10. **Gate 3 — Evidence.** Paste: (a) `pytest -x tests/unit/codemode/test_manifest_coverage.py -v` output. (b) `python servers/agency-mcp/src/agency_mcp/tools/check_codemode_manifest.py` against the live tree (expected exit 0). (c) A mocked-drift output sample showing the two-section diff format. (d) `python -c "import yaml; yaml.safe_load(open('.github/workflows/manifest-coverage.yml'))"` to confirm YAML parses. **Gate 4 — Self-Review.** Confirm the script does not import any private FastMCP internals beyond `mcp._tools` (which Spec 008 already depends on); list any handler whose tool name was historically registered with `.replace("-", "_")` or similar mangling that would defeat the diff (none expected, but call it out if found).

## Acceptance (Gherkin)

```gherkin
# anchor: 131.1
Scenario: manifest_diff returns empty sets when registry and manifest are in parity
  Given a manifest with entries {"a", "b"} and an MCP with registered tools {"a", "b"}
  When the test calls manifest_diff()
  Then the function returns (set(), set())

# anchor: 131.2
Scenario: manifest_diff detects a tool registered without a manifest entry
  Given a manifest with entries {"a"} and an MCP with registered tools {"a", "b"}
  When the test calls manifest_diff()
  Then the missing_from_manifest set equals {"b"}
  And the stale_in_manifest set is empty

# anchor: 131.3
Scenario: manifest_diff detects a stale manifest entry whose tool was removed
  Given a manifest with entries {"a", "b"} and an MCP with registered tools {"a"}
  When the test calls manifest_diff()
  Then the missing_from_manifest set is empty
  And the stale_in_manifest set equals {"b"}

# anchor: 131.4
Scenario: check_codemode_manifest.py exits 0 on parity and 1 on drift
  Given the live manifest and registered tools are in parity
  When the operator runs `python servers/agency-mcp/src/agency_mcp/tools/check_codemode_manifest.py`
  Then the process exits 0
  And the stdout contains "OK"
  Given the manifest has been hand-edited to drop one tool entry
  When the operator runs the script again
  Then the process exits 1
  And the stderr names the dropped tool under "MISSING_FROM_MANIFEST"

# anchor: 131.5
Scenario: GitHub Actions workflow is scoped to MCP-affecting paths only
  Given the workflow file .github/workflows/manifest-coverage.yml exists
  When the test parses the workflow YAML
  Then the `on.pull_request.paths` list contains "servers/agency-mcp/src/agency_mcp/handlers/**"
  And it contains "servers/agency-mcp/src/agency_mcp/codemode/manifest.json"
  And the job named "manifest-coverage" runs python>=3.11
```

## Out of scope

- Auto-fixing the manifest by inserting placeholder entries for missing tools — every new tool MUST have an explicit classification decision (eager / deferred / background); auto-defaulting to `deferred` would mask the human decision and undo the discipline.
- Enforcing the lint as a required status check on branch protection — that is a repo-admin choice, not a spec mandate. The spec ships the check; ownership decides when to require it.
- Validating the `anchor_tools` array or `status_companion` correctness — Spec 008's boot-time validation already covers those; this spec only diffs the keyspace.
- Detecting renames vs delete+add — a `music_get_track` → `music_track_get` rename produces a (missing, stale) pair, which is the correct signal; pretty-printing it as a rename is out of scope.
- Per-PR token-budget regression (e.g. asserting boot tokens stay ≤500) — that's Spec 008's integration test; this spec only enforces keyspace parity.

## References

- `Plan/000-overview.md` §2.1 #1 (snake_case naming), #5 (Tool classification — this spec adds the lint addendum).
- `Plan/JULES_PROTOCOL.md` (gates 1–4).
- Spec dependency: `Plan/008-codemode-registry/spec.md` (`classify()` boot-time tripwire; `load_manifest()` cache; manifest schema).
- Spec sibling: `Plan/022-dev-mode-install/spec.md` (per-PR smoke-test contract this spec extends to a per-PR keyspace lint).
- Spec sibling: `Plan/104-tool-search-anchor-triad/spec.md` (consumers of the manifest's `always_eager` list — coverage lint also protects it from drift).
- Local precedent: `servers/agency-mcp/src/agency_mcp/tools/validate_help_completeness.py` (vendored bitwize validator — same script shape).
- GitHub Actions `paths` filter docs: https://docs.github.com/en/actions/using-workflows/triggering-a-workflow#paths-filter