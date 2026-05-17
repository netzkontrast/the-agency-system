---
spec_id: 121
slug: contextignore-hardblock
status: ready
owner: jules
depends_on: [108, 114]
affects:
  - servers/agency-mcp/src/agency_mcp/lib/codemode/contextignore.py
  - servers/agency-mcp/src/agency_mcp/hooks/contextignore_hook.py
  - hooks/hooks.json
  - .contextignore.example
  - tests/unit/codemode/test_contextignore.py
  - tests/integration/test_contextignore_pretooluse.py
source-repos:
  - token-optimizer @ main
estimated_jules_sessions: 1
domain: cross
wave: B
---

> **Jules: read `Plan/JULES_PROTOCOL.md` before starting.** Run gates 1→4 in order:
> (1) Confidence ≥ 0.90, (2) TDD Red-Green-Refactor, (3) Evidence pasted under `## Evidence`, (4) Self-Review answered.
> Branch: `claude/agency-plugin-refactor-PgMQ4`. Only modify paths under `affects:` below.
> Source repos under `source-repos:` are clone-and-read-only into `~/work/vendor/`; never commit them.
> If anything is ambiguous, open a draft PR labelled `[BLOCKED: clarification]` and stop — do not guess.

# Spec 121 — `.contextignore` Hard Block (gitignore-style file blocklist)

## Why

token-optimizer ships a tiny but high-leverage primitive: **`.contextignore` is a gitignore-syntax file that hard-blocks the `Read` tool from loading the listed paths**. Their canonical example:

```
dist/**
node_modules/**
package-lock.json
*.min.js
```

Today, an `agency-mcp` agent that grep-walks an `audio/` or `documents/` LFS-pinned directory pulls multi-MB binaries straight into context — Spec 114's read-cache then dutifully caches them. `.contextignore` is the user's escape hatch: zero-cost block before any cache or hook fires. Two scopes: project-root `.contextignore` and global `~/.claude/.contextignore` — both apply, project takes precedence on rule conflicts.

This is independently shippable from Spec 114 (read-cache) and Spec 115 (structure-map), and it MUST run **first** in the PreToolUse chain (a blocked file should never reach the cache or the AST walker).

## Done When

- [ ] `agency_mcp.lib.codemode.contextignore.ContextIgnore` exposes `is_blocked(path: str) -> bool` and `matched_rule(path) -> str | None`.
- [ ] Two ignore-file scopes are loaded at hook-cold-start: project `<git_root>/.contextignore` and global `~/.claude/.contextignore`. Both compose; either match → blocked. Rules use **gitignore syntax** via a stdlib-only implementation (fnmatch + `**` glob handling).
- [ ] Patterns supported: literal paths, `*` (single segment), `**` (recursive), `!negation` (re-allow), trailing `/` (directory-only), leading `/` (anchored to ignore-file location).
- [ ] `hooks/contextignore_hook.py` runs on `PreToolUse` for `Read` and `Glob`/`Grep`. On block, emits `{action: "block", message: f"[contextignore] Path {path} blocked by rule '{rule}' — edit .contextignore to allow."}` and exits with non-zero to signal a hard block per the hook contract.
- [ ] The contextignore hook is **first** in the PreToolUse chain: `contextignore_hook` → `structure_map_hook` (Spec 115) → `read_cache_hook` (Spec 114) → context-mode/agency-sync (Spec 108).
- [ ] Block precedence: explicit `!negation` later in the file overrides earlier ignores (matches gitignore semantics).
- [ ] `.contextignore.example` ships at repo root with sensible defaults for our tree (`audio/**`, `documents/**`, `node_modules/**`, `dist/**`, `*.lock`, `.venv/**`, `__pycache__/**`).
- [ ] `pytest -x tests/unit/codemode/test_contextignore.py tests/integration/test_contextignore_pretooluse.py` exits 0.
- [ ] Token-budget regression: integration test attempts `Read("audio/big.wav")` with the example `.contextignore`, asserts block + zero bytes leak into the model context.

## Source clones (run first)

```bash
git clone --depth=1 https://github.com/alexgreensh/token-optimizer.git \
  ~/work/vendor/token-optimizer
```

License: PolyForm Noncommercial 1.0.0. Read-only reference for syntax + dual-scope rule. We re-implement in Python (stdlib `fnmatch` + custom `**` handling).

## Files

- **Create**:
  - `servers/agency-mcp/src/agency_mcp/lib/codemode/contextignore.py` — parser + matcher.
  - `servers/agency-mcp/src/agency_mcp/hooks/contextignore_hook.py` — PreToolUse hook.
  - `.contextignore.example` at repo root with defaults.
  - `tests/unit/codemode/test_contextignore.py`, `tests/integration/test_contextignore_pretooluse.py`.
- **Modify**:
  - `hooks/hooks.json` — insert contextignore_hook as the **first** entry under `PreToolUse`.

## Approach

1. **Gate 1 — Confidence.** Verify Specs 108 + 114 shipped (the PreToolUse chain exists). Read `~/work/vendor/token-optimizer/openclaw/src/` for the `.contextignore` loader — confirm the gitignore-subset syntax (no `[…]` character classes, no `?` single-char wildcard in their published syntax; we ship the same subset). Cite SHA.
2. **Implement the parser.** `parse(lines: list[str]) -> list[Rule]` where `Rule = {pattern: str, negation: bool, dir_only: bool, anchored: bool}`. Strip comments (lines starting with `#`) and blank lines. Parse leading `!` → `negation=True`. Parse trailing `/` → `dir_only=True`. Parse leading `/` → `anchored=True`.
3. **Implement matcher.** `is_blocked(path)`: normalise path to relative-from-ignore-file. Walk rules in order. For each, convert pattern → regex: `*` → `[^/]*`, `**/` → `(.*/)?`, `**` → `.*`, anchor handling per the `anchored` flag. Track current-block-state: last matching non-negation flips to `blocked=True`; last matching negation flips to `blocked=False`. Final state wins (gitignore semantics).
4. **Implement loader.** `ContextIgnore.load(cwd: str)`: read `<git_root>/.contextignore` and `~/.claude/.contextignore` (creating an empty in-memory rule list if either is missing). Project rules append AFTER global rules so project takes precedence on conflicts (the later rule wins per gitignore semantics, and matches token-optimizer's documented behaviour).
5. **Author the hook.** `contextignore_hook.py`: read PreToolUse JSON event from stdin. If `tool_name` not in `{"Read", "Glob", "Grep"}` → exit 0 silently. Else: extract target path(s) from event input. For Read: single path. For Glob/Grep: the search root or a single file argument. If `is_blocked(path)`: emit JSON `{action: "block", reason: f"contextignore: rule={matched_rule(path)}"}` on stdout, exit non-zero. Else exit 0.
6. **Wire hooks.json ordering.** Insert as the FIRST entry under `PreToolUse`. Document the ordering rule in the file's leading comment.
7. **Ship `.contextignore.example`** at repo root with the defaults listed in the §Done When list. Document in a single-line comment at the top: `# Copy to .contextignore; edit per project. Global rules go in ~/.claude/.contextignore.`
8. **TDD — Gate 2.** RED: write `test_contextignore.py` with table-driven cases: `dist/**` blocks `dist/a/b.js`; `node_modules/**` blocks at any depth; `*.min.js` blocks `dist/app.min.js`; `!important.lock` re-allows after `*.lock`; anchored `/dist/**` does NOT block `src/dist/foo.js`. Write `test_contextignore_pretooluse.py` integration with the example file, asserting Read on `audio/big.wav` is blocked, Read on `src/main.py` is not.
9. **GREEN + REFACTOR.** Implement minimally. Refactor: factor `_pattern_to_regex(pat, anchored)` into a pure helper that's directly unit-testable.
10. **Stdlib check.** No `pathspec`, no `wcmatch`, no `gitignore-parser` — pure `re` + `fnmatch`. **Gate 3 — Evidence.** Paste pytest output, the `.contextignore.example` content, and the captured PreToolUse JSON showing the block. **Gate 4 — Self-Review.** Flag the gitignore semantics we deliberately don't ship (e.g. `[a-z]` character classes, `?` wildcard) and confirm token-optimizer also omits them.

## Acceptance (Gherkin)

```gherkin
# anchor: 121.1
Scenario: Project .contextignore blocks the Read tool with a clear message
  Given a project root with .contextignore containing the literal line "audio/**"
  When the agent invokes Read("audio/song.wav")
  Then the contextignore_hook emits action="block"
  And the block message contains the substring "audio/**"
  And the hook exits with a non-zero status

# anchor: 121.2
Scenario: Negation re-allows a path previously blocked
  Given .contextignore contains "*.lock" followed by "!Pipfile.lock"
  When the agent invokes Read("Pipfile.lock")
  Then the hook does NOT block
  When the agent invokes Read("package.lock")
  Then the hook DOES block

# anchor: 121.3
Scenario: Global ~/.claude/.contextignore composes with project rules
  Given ~/.claude/.contextignore contains "*.pem"
  And the project root .contextignore contains "audio/**"
  When the agent invokes Read("secrets/cert.pem")
  Then the hook blocks via the global rule
  When the agent invokes Read("audio/x.wav")
  Then the hook blocks via the project rule

# anchor: 121.4
Scenario: Non-Read tools pass through silently
  Given a project with .contextignore blocking audio/**
  When the agent invokes Bash("ls audio/")
  Then the contextignore_hook exits 0 with no output
  And the Bash call proceeds normally
```

## Out of scope

- `[a-z]` character classes, `?` single-char wildcard — token-optimizer ships the same subset.
- Auto-generation of `.contextignore` based on `.gitignore` — operator runs `cp .gitignore .contextignore` themselves.
- A `.contextignore` editor tool — operators edit the file directly.
- Wildcard support in Bash/Grep target paths — only the explicit target path is checked; complex glob patterns inside Bash invocations are out of scope.
- License flag: token-optimizer is PolyForm Noncommercial 1.0.0. We re-implement the gitignore-subset matcher in Python; no source copied. The `.contextignore.example` content is generic and not derived from token-optimizer.

## References

- token-optimizer README — `.contextignore` syntax + dual-scope (`~/.claude/.contextignore` + project root): https://github.com/alexgreensh/token-optimizer/blob/main/README.md
- Gitignore syntax reference: https://git-scm.com/docs/gitignore
- Python stdlib `fnmatch` (matching primitive): https://docs.python.org/3/library/fnmatch.html
- `Plan/JULES_PROTOCOL.md` — gates 1–4
- Spec dependency: `Plan/108-context-mode-integration/spec.md` (hooks.json conventions)
- Spec dependency: `Plan/114-read-cache-delta-mode/spec.md` (chain order — contextignore must run BEFORE the cache)
- Spec sibling: `Plan/115-structure-map-ast/spec.md` (also in the PreToolUse chain; contextignore runs first)
