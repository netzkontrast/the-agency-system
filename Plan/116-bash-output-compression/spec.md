---
spec_id: 116
slug: bash-output-compression
status: ready
owner: jules
depends_on: [008, 108]
affects:
  - servers/agency-mcp/src/agency_mcp/lib/codemode/bash_compress/__init__.py
  - servers/agency-mcp/src/agency_mcp/lib/codemode/bash_compress/git.py
  - servers/agency-mcp/src/agency_mcp/lib/codemode/bash_compress/pytest.py
  - servers/agency-mcp/src/agency_mcp/lib/codemode/bash_compress/lint.py
  - servers/agency-mcp/src/agency_mcp/lib/codemode/bash_compress/ls.py
  - servers/agency-mcp/src/agency_mcp/lib/codemode/bash_compress/docker.py
  - servers/agency-mcp/src/agency_mcp/lib/codemode/bash_compress/logs.py
  - servers/agency-mcp/src/agency_mcp/lib/codemode/bash_compress/dispatch.py
  - servers/agency-mcp/src/agency_mcp/hooks/bash_compress_hook.py
  - hooks/hooks.json
  - tests/unit/codemode/bash_compress/test_dispatch.py
  - tests/unit/codemode/bash_compress/test_git.py
  - tests/unit/codemode/bash_compress/test_pytest.py
  - tests/unit/codemode/bash_compress/test_lint.py
  - tests/unit/codemode/bash_compress/test_ls.py
  - tests/integration/test_bash_compress_pretooluse.py
source-repos:
  - token-optimizer @ main
estimated_jules_sessions: 2
domain: cross
wave: B
---

> **Jules: read `Plan/JULES_PROTOCOL.md` before starting.** Run gates 1→4 in order:
> (1) Confidence ≥ 0.90, (2) TDD Red-Green-Refactor, (3) Evidence pasted under `## Evidence`, (4) Self-Review answered.
> Branch: `claude/agency-plugin-refactor-PgMQ4`. Only modify paths under `affects:` below.
> Source repos under `source-repos:` are clone-and-read-only into `~/work/vendor/`; never commit them.
> If anything is ambiguous, open a draft PR labelled `[BLOCKED: clarification]` and stop — do not guess.

# Spec 116 — Bash Output Compression (PostToolUse rewrite)

## Why

token-optimizer ships **sixteen CLI handlers** that intercept Bash invocations at the PreToolUse layer and rewrite the **output** before the model sees it: a 60-file `ls -la` truncates to 50, a 564-token pytest summary becomes 115 tokens, full git logs collapse to the diff-only view, lint runs trim to error lines. Their measured impact: **~10% of total session input tokens**. Specs 103 (view-projection) and 108-110 (context-mode) handle MCP tool outputs, but the built-in `Bash` tool — heavily used by our music + jules workflows for git/pytest/rg/ls — is uncompressed today. This spec ports the algorithm: a `PostToolUse` hook for `Bash` runs the raw output through a command-aware compressor (dispatched by `shlex.split(input.command)[0]`), preserving credentials verbatim and never running with `shell=True`.

## Done When

- [ ] `agency_mcp.lib.codemode.bash_compress.dispatch.compress(command: str, stdout: str, stderr: str) -> Compressed` returns `{stdout: str, stderr: str, summary: str | None, original_bytes: int, compressed_bytes: int, fired: str | None}` where `fired` is the handler name (e.g. `"git"`, `"pytest"`) or `None` if no handler matched.
- [ ] At minimum **six handlers** are ported: `git`, `pytest`, `lint` (ruff/eslint/flake8/mypy), `ls`, `docker`, `logs` (journalctl / tail / less-style). Each handler is a pure function `(stdout, stderr) -> (stdout', stderr', summary)`.
- [ ] Dispatch uses `shlex.split(command)` (stdlib) to extract argv[0]; binary-name aliases (`pytest`, `python -m pytest`, `python3 -m pytest`) route to the same handler. The dispatch table is data-driven and lives in `bash_compress/dispatch.py`.
- [ ] **Credential preservation**: any token matching `(?i)(api[_-]?key|token|secret|password|bearer|aws_[a-z_]+|gh[pousr]_[a-z0-9]+)` is preserved verbatim in the compressed output. The corresponding regex test fixture exists.
- [ ] **Exclusion rules** (mirror token-optimizer): output >2,000 lines → bypass compression and let the model see the full stream (compressor adds a `[truncated by line cap]` marker for visibility); generated/minified content (lines >500 chars on average) → bypass.
- [ ] `hooks/bash_compress_hook.py` runs on `PostToolUse` for `Bash`, reads the tool's `stdout`/`stderr` from the event payload, calls `dispatch.compress(...)`, and writes the rewritten output back via the PostToolUse `updatedOutput` mechanism (per token-optimizer's documented hook contract).
- [ ] `pytest -x tests/unit/codemode/bash_compress/ tests/integration/test_bash_compress_pretooluse.py` exits 0.
- [ ] Token-budget regression: pytest handler reduces a fixture pytest output of ≥ 564 chars to ≤ 200 chars while preserving every `FAILED` / `ERROR` line verbatim.

## Source clones (run first)

```bash
git clone --depth=1 https://github.com/alexgreensh/token-optimizer.git \
  ~/work/vendor/token-optimizer
```

License: PolyForm Noncommercial 1.0.0. We re-implement each handler idiomatically in Python (stdlib only). Read `~/work/vendor/token-optimizer/skills/token-optimizer/scripts/measure.py` and `~/work/vendor/token-optimizer/openclaw/src/` for handler patterns. Cite each handler's reference SHA.

## Files

- **Create**:
  - `servers/agency-mcp/src/agency_mcp/lib/codemode/bash_compress/__init__.py` — package + public exports.
  - `servers/agency-mcp/src/agency_mcp/lib/codemode/bash_compress/dispatch.py` — `compress(...)`, dispatch table, credential-preservation regex.
  - Six handler modules: `git.py`, `pytest.py`, `lint.py`, `ls.py`, `docker.py`, `logs.py`.
  - `servers/agency-mcp/src/agency_mcp/hooks/bash_compress_hook.py` — PostToolUse hook.
  - `tests/unit/codemode/bash_compress/test_*.py` (one per handler + dispatch) and `tests/integration/test_bash_compress_pretooluse.py`.
- **Modify**:
  - `hooks/hooks.json` — register the hook on `PostToolUse` for `Bash`. Order is independent of Spec 111/112's PreToolUse hooks.
- **Move / Delete**: none.

## Approach

1. **Gate 1 — Confidence.** Verify Spec 108's `hooks.json` is in place. Read token-optimizer's `measure.py` for the dispatch table — note the binary-name aliases and the credential-preservation regex. Confirm no handler relies on a non-stdlib import (token-optimizer's Python plugin is stdlib-only); cite SHA.
2. **Author `dispatch.py`.** Define `Compressed` dataclass and the `HANDLERS: dict[str, Callable]` table with these keys: `git`, `pytest`, `python -m pytest`, `python3 -m pytest`, `ruff`, `eslint`, `flake8`, `mypy`, `ls`, `docker`, `journalctl`, `tail`. The single `compress(...)` function `shlex.split`s the command, maps argv[0] (and `argv[0] argv[1]` for `python -m pytest`) to a handler, and returns the handler's output framed in the `Compressed` dataclass.
3. **Implement `git.py`.** Detect `git log`, `git diff`, `git status`, `git show`. For `log`: keep first 20 commits, summary `... (N more commits)`. For `diff`: drop all hunks not containing a `+` or `-` line on the immediate edges, then cap at 200 lines. For `status`: pass through (already short).
4. **Implement `pytest.py`.** Strip the dot-progress lines (`.....F....`), strip pyc cache messages and warnings unless `-W error`, keep every line matching `^(FAILED|ERROR|PASSED|SKIPPED)\s`, keep the `=== short test summary ===` block, keep the trailing `=== N passed, M failed in T s ===`. Drop verbose tracebacks above the first `E ` line per failure.
5. **Implement `lint.py`.** Recognise ruff/eslint/flake8/mypy formats. Keep one line per error; drop secondary context lines (the `^^^^` underline rows ruff emits) unless the caller passed `--show-source` (heuristic: presence of `^^^^` lines in the raw output → keep them). Always preserve file:line:col prefix.
6. **Implement `ls.py`.** If output has ≥ 60 entries, keep first 50 + append `... (N more entries, M directories)`. Group `-la` style entries.
7. **Implement `docker.py`** (`docker ps`, `docker images`, `docker logs`). Tabular output: keep header + first 20 data rows + count footer. `docker logs`: keep last 50 lines unless `--tail` flag is present.
8. **Implement `logs.py`** (`journalctl`, `tail`, default fallback for unrecognised streams of plain text). Keep last 50 lines; preserve credential tokens via the dispatch-level regex.
9. **Credential preservation pass.** Before returning, `dispatch.compress` re-scans the final compressed stdout/stderr; if any token from the original output matching `CREDENTIAL_REGEX` is missing from the compressed output, re-inject it on its own line prefixed with `[preserved credential]`. Unit test asserts this round-trip on a synthetic fixture.
10. **Author `bash_compress_hook.py` + wire hooks.json.** Read PostToolUse JSON event from stdin. Verify `tool_name == "Bash"`. Compute compression; if `compressed_bytes < original_bytes - 200` (i.e. saved ≥ 200 bytes), emit `updatedOutput` JSON on stdout. Otherwise exit 0 silently. **TDD — Gate 2.** RED on every handler's table-driven test (six handlers + dispatch + credential preservation = ~30 tests). GREEN. REFACTOR: pull line-cap helpers into `_truncate(lines, cap)` shared utility. **Gate 3 — Evidence.** Paste pytest output, the byte-count delta on the published 564-token pytest fixture, and a sample compressed-vs-original diff. **Gate 4 — Self-Review.** Flag any handler we deliberately deferred (e.g. `kubectl`, `helm`) and the reasoning.

## Acceptance (Gherkin)

```gherkin
# anchor: 113.1
Scenario: pytest output compresses below 200 bytes while preserving failures
  Given a captured pytest stdout fixture of 564+ bytes with 1 PASSED, 1 FAILED, 1 ERROR line
  When bash_compress.dispatch.compress("pytest", stdout, stderr="") is called
  Then result.compressed_bytes ≤ 200
  And every original line matching ^(FAILED|ERROR)\s appears verbatim in result.stdout
  And result.fired == "pytest"

# anchor: 113.2
Scenario: Credentials are preserved verbatim through compression
  Given a Bash output containing the literal "gh_pat_AbCdEf1234567890..." in a curl trace
  When the output passes through bash_compress.dispatch.compress(...)
  Then the original credential token appears verbatim in result.stdout (possibly on a "[preserved credential]" line)

# anchor: 113.3
Scenario: Unrecognised command bypasses compression
  Given a Bash command "esoteric_tool --do --stuff" with 100 lines of output
  When bash_compress.dispatch.compress(...) is called
  Then result.fired is None
  And result.stdout equals the input stdout byte-for-byte

# anchor: 113.4
Scenario: Output above 2,000-line cap bypasses compression with marker
  Given a Bash command "rg pattern src/" returning 2,500 lines of output
  When bash_compress.dispatch.compress(...) is called
  Then result.fired is None
  And result.stdout begins with "[bash-compress: bypassed — output >2000 lines]"
```

## Out of scope

- Live streaming compression (per-chunk) — we compress only after the full output is captured (token-optimizer ships the same constraint).
- Editing the `Bash` command itself (rewriting `git log` → `git log -20 --oneline`) — that is too invasive; we only rewrite output.
- Replacing the credential-preservation regex with a full-fledged secret scanner (gitleaks-style) — out of scope for Wave B.
- Handler coverage beyond the six listed — additional binaries (`make`, `npm`, `cargo`) ship in follow-up specs.
- License flag: token-optimizer is PolyForm Noncommercial 1.0.0. We re-implement each handler in Python; no source copied. If we ever vendor any handler verbatim, revisit.

## References

- token-optimizer README — "564-token pytest output → 115 tokens" and 16-handler claim: https://github.com/alexgreensh/token-optimizer/blob/main/README.md
- Handler source patterns (read-only): `~/work/vendor/token-optimizer/openclaw/src/` and `~/work/vendor/token-optimizer/skills/token-optimizer/scripts/measure.py`
- Python `shlex` (stdlib, safe tokenisation, never `shell=True`): https://docs.python.org/3/library/shlex.html
- `Plan/JULES_PROTOCOL.md` — gates 1–4
- Spec dependency: `Plan/008-codemode-registry/spec.md`
- Spec dependency: `Plan/108-context-mode-integration/spec.md` (hooks.json wiring conventions)
- Spec sibling: `Plan/117-tool-result-archive/spec.md` (archive >4KB outputs end-to-end)
