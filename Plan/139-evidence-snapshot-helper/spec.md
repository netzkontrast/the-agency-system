---
spec_id: 139
slug: evidence-snapshot-helper
status: draft
owner: jules
depends_on: [099]
affects:
  - Plan/JULES_PROTOCOL.md
  - tools/agency-evidence-snapshot.py
  - tests/unit/tools/test_agency_evidence_snapshot.py
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

# Spec 139 — Clean-Install Evidence-Snapshot Helper for Gate 3

## Why

JULES_PROTOCOL Gate 3 requires every `[x]` ticked in a spec's `Done When:` list to be backed by an artefact pasted into the PR body's `## Evidence` block. Today the artefact-capture step is **manual**: Jules runs `pytest`, eyeballs the last twenty lines, and pastes them by hand. Two failure modes have already burned PRs:

1. **Lesson 03 (Evidence with polluted PYTHONPATH).** PR #36 captured a green `pytest` run under `PYTHONPATH=$PWD/src:$HOME/work/vendor/bitwize-music`, masking a missing `tools/` package. The Evidence block looked valid; the production import would have failed on a clean clone. Gate 3 became evidence theatre.
2. **Lesson 14 (Token consumption postmortem).** Re-fetching the same PR body to read the `## Evidence` block costs 3–5 kB per call. The orchestrator does this ≥ 6 times during a wave (#36 / #41 / #42 / #46), which compounds into ~25 kB of duplicated body text. A locally-captured, normalised snapshot would let the orchestrator `grep` the artefact instead of re-fetching the PR body.

Spec 099 hardens the *content* of evidence (clean-install Done-When, review-subagent dispatch). Spec 102 hardens *rebase drift*. Neither ships a tool that **produces** the evidence block deterministically.

This spec ships `tools/agency-evidence-snapshot.py` — a single Python script that runs the canonical Gate-3 commands (pytest, lint, type-check, build, import-smoke) under a clean Python environment (no `PYTHONPATH` additions outside the repo), captures the last-20-lines of each, and emits a Markdown-fenced `## Evidence` block ready to paste into the PR body or commit. The script is the mechanical answer to "how do I know my evidence wasn't captured under a polluted environment?" — by construction, it can't be.

## Done When

- [ ] `tools/agency-evidence-snapshot.py` exists, is executable (`chmod +x`), and runs as `python tools/agency-evidence-snapshot.py` with no required arguments (defaults: detect `pyproject.toml`, run pytest under `-x`, run `ruff check` if `ruff` is on PATH, run `python -c "import <pkg>"` for every top-level package under `servers/*/src/`).
- [ ] The script enforces a clean Python environment: before invoking any captured command it asserts that no `PYTHONPATH` element points outside the repo root (resolves each entry against `git rev-parse --show-toplevel`); on violation it exits 2 with diagnostic `agency-evidence-snapshot::ERROR:E.1:PYTHONPATH element '<path>' points outside repo root '<root>'` and refuses to capture any evidence.
- [ ] The script writes its output to a default path `Plan/_session-state/evidence-snapshot.md` (overwriting any prior snapshot) and ALSO prints the same content to stdout. The default path is configurable via `--out PATH`.
- [ ] The snapshot file contains a single `## Evidence` H2 heading followed by one fenced code block per captured command. Each fenced block carries a sub-heading line of the form `### <slug>` (e.g. `### pytest`, `### ruff`, `### import-smoke:agency_mcp`). The fenced block contains the **last 20 lines** of the command's combined stdout+stderr, plus a final `# exit: <code>` line.
- [ ] The script supports `--include CMD` and `--exclude CMD` flags (repeatable) to add or skip command slugs. Unknown slugs in `--exclude` are silent no-ops; unknown slugs in `--include` cause exit 2 with diagnostic `E.2:unknown-command`.
- [ ] The script supports `--max-bytes N` (default 32 KB) to cap the snapshot file size. On overflow it truncates the last (largest) fenced block and appends a single line `# truncated to fit --max-bytes 32768` inside that block. The hard ceiling is enforced regardless of `--max-bytes` setting at 64 KB to prevent runaway captures.
- [ ] The script exits 0 when every captured command exited 0 AND `PYTHONPATH` validation passed. It exits 1 when any captured command exited non-zero (the snapshot is still written so Jules can paste it into a `[BLOCKED:]` PR). It exits 2 on environment-validation failure with no snapshot written.
- [ ] `pytest -x tests/unit/tools/test_agency_evidence_snapshot.py` exits 0 with at least four cases: (a) all-green capture exits 0 + writes well-formed snapshot, (b) one-red capture exits 1 + writes snapshot, (c) polluted PYTHONPATH exits 2 + writes no snapshot, (d) `--max-bytes` truncation appends the truncation marker.
- [ ] JULES_PROTOCOL.md Gate 3 is patched to name `tools/agency-evidence-snapshot.py` as the **preferred** mechanism for producing the `## Evidence` block, with the manual fenced-blocks approach retained as a fallback when the captured command does not fit the script's model (e.g. `curl -i` for an HTTP endpoint).

## Source clones (run first)

None — this spec is meta-work. `source-repos:` is `[]`. The behavioural model draws on `~/agency/tools/check-governance.sh` (the unified pre-commit suite that captures many command outputs) as a **read-only reference**; we deliberately ship a much smaller, snapshot-only tool rather than porting the full check-governance pipeline (out of scope below).

## Files

- **Create**:
  - `tools/agency-evidence-snapshot.py` — single-file Python 3.11 script, stdlib-only (`subprocess`, `argparse`, `pathlib`, `os`, `sys`). No external deps.
  - `tests/unit/tools/test_agency_evidence_snapshot.py` — pytest cases per Done When.
- **Modify**:
  - `Plan/JULES_PROTOCOL.md` — Gate 3 table (add the script as the preferred capture mechanism) and §5 anti-pattern wording (cross-reference `PYTHONPATH` violation).
- **Move / Delete**: none.

## Approach

1. **Gate 1 — Confidence.** Confirm `tools/` exists at repo root (`ls tools/` returns the existing `cleanup-merged-branches.sh`, `jules-patch-extract.py`). Confirm `pytest`, `ruff` are available via `pyproject.toml`'s `[tool]` sections. Read Lesson 03 and Lesson 14 end-to-end. Read `~/agency/tools/check-governance.sh` lines 1–150 as a **reference shape**; do not copy. Cite all checks in the Confidence table.
2. **Design the command registry.** Hard-code a small registry at the top of the script:
   ```python
   COMMANDS = {
     "pytest":         ["python", "-m", "pytest", "-x", "--tb=short"],
     "ruff":           ["ruff", "check", "."],
     "mypy":           ["mypy", "."],
     "build":          ["python", "-m", "build"],
     "import-smoke":   None,  # generated dynamically: one entry per servers/*/src/<pkg>/
   }
   ```
   Each entry has an `enabled_if` predicate: pytest enabled iff `pyproject.toml` exists, ruff iff `ruff` on PATH, mypy iff `mypy` on PATH, build iff `pyproject.toml` declares a `[build-system]` table, import-smoke iff at least one `servers/*/src/*/` package exists.
3. **Implement `PYTHONPATH` validation.** Top of `main()`: resolve repo root via `git rev-parse --show-toplevel`. Walk `os.environ.get("PYTHONPATH", "").split(os.pathsep)`. For each non-empty entry, resolve to absolute path and check `Path(entry).resolve().is_relative_to(repo_root)`. On any violation, emit `E.1` diagnostic + exit 2.
4. **Implement command capture.** `subprocess.run(cmd, capture_output=True, text=True, cwd=repo_root, timeout=600)`. Collect `stdout + "\n" + stderr`, split lines, keep the last 20. Format as fenced `text` block with `### <slug>` sub-heading and trailing `# exit: <code>` line.
5. **Implement size-cap logic.** Sum total bytes of all fenced blocks. If over `--max-bytes`, sort blocks by size descending and truncate the largest until under the cap. Append `# truncated to fit --max-bytes <N>` inside the truncated block. Hard ceiling 64 KB applied unconditionally.
6. **Implement the import-smoke generator.** For each `servers/*/src/*/__init__.py` found by glob, emit a synthetic command `["python", "-c", f"import {pkg_name}"]`. The slug is `import-smoke:<pkg_name>`. **The smoke runs from `cwd=/tmp` (not the repo root)** so an editable install — not a `sys.path` happy accident — is what answers the import. This is the direct mitigation for Lesson 03.
7. **TDD — Gate 2.** RED: write `tests/unit/tools/test_agency_evidence_snapshot.py` with four cases. Each case `monkeypatch`es `subprocess.run` to return canned `CompletedProcess` instances, sets `PYTHONPATH` via `monkeypatch.setenv`, runs the script via `subprocess.run([sys.executable, "tools/agency-evidence-snapshot.py", "--out", tmp_path / "snap.md"])`, and asserts exit code + file contents. GREEN: implement steps 2–6. REFACTOR: extract `_capture_one(cmd, slug)` and `_format_block(slug, lines, exit_code)` as pure helpers.
8. **Patch JULES_PROTOCOL.md Gate 3.** Append a row to the artefact table:
   > | All Gate-3 commands at once | `python tools/agency-evidence-snapshot.py --out -` then paste stdout into the PR `## Evidence` block. |
   Add a sentence: "When the script exits 2 with an `E.1:PYTHONPATH` diagnostic, the evidence is by definition theatre (Lesson 03); the PR MUST NOT be flipped to ready until the environment is cleaned." Cross-reference §5 anti-pattern #3.
9. **Gate 3 — Evidence.** Paste `python tools/agency-evidence-snapshot.py --out -` output against the live tree (this spec's own snapshot becomes its own evidence — self-test), the pytest output for the new test file, and `rg -n 'agency-evidence-snapshot' Plan/JULES_PROTOCOL.md` to prove the protocol patch landed.
10. **Gate 4 — Self-Review.** Answer the three questions. Dispatch the Spec 099 review subagent. Cite the smoke-test fact that this PR's `## Evidence` block was produced by the very script under review.

## Acceptance (Gherkin)

```gherkin
# anchor: 139.1
Scenario: All-green capture writes a well-formed Evidence block
  Given a working tree where pytest, ruff, and import-smoke all exit 0
  And PYTHONPATH is empty or contains only paths inside the repo root
  When the operator runs "python tools/agency-evidence-snapshot.py --out evidence.md"
  Then the process exits with status 0
  And the file "evidence.md" begins with the line "## Evidence"
  And the file contains exactly one fenced code block per enabled command
  And each fenced block carries a "### <slug>" sub-heading and a trailing "# exit: 0" line

# anchor: 139.2
Scenario: Polluted PYTHONPATH refuses to capture evidence
  Given PYTHONPATH contains the path "/home/user/work/vendor/bitwize-music"
  And that path resolves outside the repo root
  When the operator runs "python tools/agency-evidence-snapshot.py"
  Then the process exits with status 2
  And stderr contains the substring "E.1:PYTHONPATH element"
  And no evidence file is written

# anchor: 139.3
Scenario: A red command still writes the snapshot but exits 1
  Given a working tree where pytest exits 1 (one failing test)
  When the operator runs "python tools/agency-evidence-snapshot.py --out evidence.md"
  Then the process exits with status 1
  And the file "evidence.md" exists
  And the fenced block for "### pytest" ends with the line "# exit: 1"

# anchor: 139.4
Scenario: Output is capped under the --max-bytes ceiling
  Given a working tree where pytest emits 100 KB of output
  When the operator runs "python tools/agency-evidence-snapshot.py --max-bytes 8192 --out evidence.md"
  Then the file "evidence.md" is no larger than 8192 bytes
  And the pytest fenced block contains the line "# truncated to fit --max-bytes 8192"

# anchor: 139.5
Scenario: Import-smoke runs from /tmp to defeat sys.path happy accidents
  Given the working tree has a package "agency_mcp" under servers/agency-mcp/src/
  When the operator runs "python tools/agency-evidence-snapshot.py" with PYTHONPATH unset
  Then the import-smoke for agency_mcp runs with cwd="/tmp"
  And the fenced block "### import-smoke:agency_mcp" reflects that invocation
```

## Out of scope

- Porting Agency's full `tools/check-governance.sh` pipeline (~26 step suite). The 099 lint-script wave already provides `Plan/_lint/`; this spec ships an orthogonal capture tool, not a governance gate.
- A pre-commit hook that auto-invokes the script. `the-agency-system` has not yet adopted a pre-commit framework; introducing one is a separate concern (a future spec might wrap this script under `.githooks/pre-commit` once the framework lands).
- HTTP-endpoint evidence (`curl -i`). The script targets repeatable in-process commands; ad-hoc network calls remain a manual fenced-block in the PR body.
- Persistent evidence history (every snapshot overwrites `Plan/_session-state/evidence-snapshot.md`). A history-aware variant could ship later as a Spec 100 (session-log MCP) consumer, but per-snapshot persistence is not in scope here.
- The `## Frustration Log` section (owned by Spec 138). The snapshot script captures evidence; FL declaration is a sibling discipline emitted by the agent, not the tool.

## References

- `Plan/JULES_PROTOCOL.md` Gate 3 (artefact table being extended) and §5 (anti-pattern #3 cross-reference)
- `Plan/_lessons-learned/03-evidence-with-polluted-pythonpath.md` — the load-bearing motivation for E.1 PYTHONPATH validation and the import-smoke `cwd=/tmp` rule
- `Plan/_lessons-learned/14-token-consumption-postmortem.md` — the load-bearing motivation for the size cap and the "local snapshot beats refetching PR body" workflow
- External reference (read-only): `~/agency/tools/check-governance.sh` — entry-point shape for unified-suite scripts (Agency's version runs a full governance suite; we ship the capture-only subset)
- External reference (read-only): `~/agency/PRE_COMMIT.md` §4 "Testing & Verification" — discipline rationale
- Spec dependency: `Plan/099-jules-orchestration-improvements/spec.md` (lint-script entry-point conventions, dispatch-prompt hardening that names the script's invocation)
- Spec sibling: `Plan/138-frustration-log-protocol/spec.md` — orthogonal Gate 4 mechanisation (per-PR FL declaration)
- Spec downstream: `Plan/100-session-log-mcp/spec.md` — may later ingest snapshot files as structured events
