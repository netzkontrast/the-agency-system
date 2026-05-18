---
spec_id: 115
slug: structure-map-ast
status: ready
owner: jules
depends_on: [008, 114]
affects:
  - servers/agency-mcp/src/agency_mcp/lib/codemode/structure_map.py
  - servers/agency-mcp/src/agency_mcp/lib/codemode/structure_map_python.py
  - servers/agency-mcp/src/agency_mcp/lib/codemode/structure_map_jsts.py
  - servers/agency-mcp/src/agency_mcp/hooks/structure_map_hook.py
  - hooks/hooks.json
  - tests/unit/codemode/test_structure_map_python.py
  - tests/unit/codemode/test_structure_map_jsts.py
  - tests/integration/test_structure_map_hook.py
source-repos:
  - token-optimizer @ main
estimated_jules_sessions: 2
domain: cross
wave: B
---

> **Jules: read `Plan/JULES_PROTOCOL.md` before starting.** Run gates 1→4 in order:
> (1) Confidence ≥ 0.90, (2) TDD Red-Green-Refactor, (3) Evidence pasted under `## Evidence`, (4) Self-Review answered.
> Branch: `Master` (default base for fresh specs post-Wave-A; see JULES_PROTOCOL.md §3). Only modify paths under `affects:` below.
> Source repos under `source-repos:` are clone-and-read-only into `~/work/vendor/`; never commit them.
> If anything is ambiguous, open a draft PR labelled `[BLOCKED: clarification]` and stop — do not guess.

# Spec 115 — Structure Map (AST skeleton for large code files)

## Why

token-optimizer reports the most extreme single-file compression in their stack: **a 2,000-line / 180,000-token Python file collapses to a 250-token skeleton — a 99% reduction**. The technique: when the agent re-reads a large code file, instead of returning the body (or even a unified diff per Spec 114), the PreToolUse hook returns an AST-derived **structure map**: top-level class names, method signatures, top-level function signatures, module-level docstring — nothing else. The model still navigates the file structurally; the body only loads when the caller asks for a specific symbol. Spec 114's delta mode tops out around 50KB/file; Structure Map takes over above that. Combined coverage: small files get diffs, big files get skeletons, everything else gets `view=summary`.

## Done When

- [ ] `agency_mcp.lib.codemode.structure_map_python.extract(path: str) -> StructureMap` parses Python with `ast.parse(...)` (stdlib) and returns `{module_docstring, classes: [{name, lineno, methods: [{name, signature, lineno}]}], functions: [{name, signature, lineno}], imports_count, total_lines}`.
- [ ] `agency_mcp.lib.codemode.structure_map_jsts.extract(path: str) -> StructureMap` parses TypeScript/JavaScript with **regex-only** (mirror token-optimizer's openclaw approach for JS/TS — no tree-sitter). Recognises `class X`, `function fn`, `const fn = (...) =>`, `export default class`, method shorthand inside class bodies.
- [ ] `structure_map.render(sm: StructureMap, fmt: str = "compact") -> str` produces a deterministic string ≤ 500 tokens for a typical 2,000-line file (`compact` format: class lines indented two spaces, methods four).
- [ ] Size-gating rules: Python files engage Structure Map at **>800 KB OR >20,000 lines**; JS/TS at **>400 KB OR >5,000 lines** (mirror token-optimizer's published file-size limits — see References).
- [ ] Below those thresholds OR on AST parse failure, fall back to Spec 114's delta mode; no error surfaces to the model.
- [ ] `hooks/structure_map_hook.py` runs on `PreToolUse` for `Read`, intercepts large code files BEFORE the read-cache delta hook (it sits "outside" Spec 114's hook in the chain), and emits `additionalContext` of kind="structure_map".
- [ ] `pytest -x tests/unit/codemode/test_structure_map_python.py tests/unit/codemode/test_structure_map_jsts.py tests/integration/test_structure_map_hook.py` exits 0.
- [ ] Token-budget regression: integration test asserts a 20,000-line Python fixture renders to a structure map under 600 tokens (~6× safety vs the claimed 250-token result).

## Source clones (run first)

```bash
git clone --depth=1 https://github.com/alexgreensh/token-optimizer.git \
  ~/work/vendor/token-optimizer
```

License: PolyForm Noncommercial 1.0.0. Read-only reference. We re-implement with Python `ast` (stdlib) + regex (stdlib) — no source copied.

## Files

- **Create**:
  - `servers/agency-mcp/src/agency_mcp/lib/codemode/structure_map.py` — public API, dispatch by extension, `render(...)`.
  - `servers/agency-mcp/src/agency_mcp/lib/codemode/structure_map_python.py` — `ast.parse` walker.
  - `servers/agency-mcp/src/agency_mcp/lib/codemode/structure_map_jsts.py` — regex walker.
  - `servers/agency-mcp/src/agency_mcp/hooks/structure_map_hook.py` — PreToolUse hook script.
  - `tests/unit/codemode/test_structure_map_python.py`, `tests/unit/codemode/test_structure_map_jsts.py`, `tests/integration/test_structure_map_hook.py`.
- **Modify**:
  - `hooks/hooks.json` — register the structure-map hook on `PreToolUse` for `Read`. Order: structure-map hook → read-cache delta hook (Spec 114) → context-mode/agency hooks (Spec 108).
- **Move / Delete**: none.

## Approach

1. **Gate 1 — Confidence.** Verify Spec 114's `read_cache_hook.py` is wired in `hooks.json`. Read `~/work/vendor/token-optimizer/openclaw/src/structure-map.ts` and the Python equivalent in `~/work/vendor/token-optimizer/skills/token-optimizer/scripts/measure.py` to extract size thresholds (800 KB / 20K lines for Python; 400 KB / 5K lines for JS/TS) and rendering conventions. Cite SHA.
2. **Implement Python walker.** `structure_map_python.extract` uses `ast.parse(source)`. Walk top-level body collecting `ClassDef` (with nested `FunctionDef` / `AsyncFunctionDef` methods), `FunctionDef` / `AsyncFunctionDef`, capture argument signatures via `ast.unparse(node.args)` (Py 3.9+). On `SyntaxError`, return `None` → caller falls back.
3. **Implement JS/TS walker.** Regex-only (stdlib `re`). Patterns: `^\s*(export\s+)?(default\s+)?(async\s+)?(function|class)\s+(\w+)`, `^\s*(export\s+)?(const|let)\s+(\w+)\s*=\s*(async\s+)?\(`, class-body method shorthand `^\s+(\w+)\s*\(.*\)\s*\{`. Comment-strip via a small state machine (track `//`, `/* */`, template-literal `\``). On any regex/state-machine failure, return `None`.
4. **Implement `render`.** `compact` format: first line `# Structure map of {path} ({total_lines} lines)`; module docstring (≤120 chars); then each top-level class on its own line `class {name}:  (L{lineno})`; methods indented two spaces; top-level functions after classes. Cap at 200 entries — overflow as `... (N more)`.
5. **Author `structure_map_hook.py`.** Reads PreToolUse JSON from stdin. If tool is not `Read`, exit 0. Stat the target path; if size+line-count exceeds the language-specific threshold, call `extract(...)` + `render(...)`, then emit stdout JSON `{action: "additionalContext", additionalContext: {kind: "structure_map", path, rendered, total_lines, format: "compact"}}` and exit 0. Otherwise exit 0 silently — Spec 114's hook downstream will handle.
6. **Wire hooks.json ordering.** The chain on PreToolUse for `Read` becomes: `structure_map_hook.py` → `read_cache_hook.py` (Spec 114) → context-mode + agency sync (Spec 108). All hooks are non-blocking; each may emit `additionalContext` independently.
7. **TDD — Gate 2.** RED: write the three test files. Python tests: a fixture file with 3 classes + 5 functions + 2 nested functions; assert exact `StructureMap` shape. JS/TS tests: fixture with `export class`, arrow functions, method shorthand; assert names and signatures. Integration test: pipe synthetic PreToolUse event for a 21,000-line generated Python file (no real LLM dependency); assert structure_map emission. Run — must fail.
8. **GREEN + REFACTOR.** Implement minimally. Refactor: factor the signature-extraction helper to share between the Python walker's class methods and top-level functions.
9. **Stdlib-only invariant check.** `rg 'import\s+(tree_sitter|esprima|jedi|libcst)' servers/agency-mcp/src/agency_mcp/lib/codemode/structure_map*` returns empty. The whole subsystem MUST work with `ast`, `re`, and stdlib only — same constraint token-optimizer accepts.
10. **Gate 3 — Evidence.** Paste pytest output, the rendered structure map for the 20K-line fixture, and the byte-count delta versus the raw fixture. **Gate 4 — Self-Review.** Flag languages we deliberately don't cover (Go, Rust, etc.) and the fallback path the user experiences for them (Spec 114 takes over).

## Acceptance (Gherkin)

```gherkin
# anchor: 115.1
Scenario: Large Python file produces a compact structure map
  Given a Python file at /tmp/big.py with 25,000 lines, 40 classes, 200 methods, and a 100-char module docstring
  When the agent invokes Read on /tmp/big.py
  Then the structure_map_hook emits additionalContext of kind="structure_map"
  And rendered text begins with "# Structure map of /tmp/big.py (25000 lines)"
  And rendered text is ≤ 600 tokens (length / 4)

# anchor: 115.2
Scenario: Mid-size file falls through to delta mode
  Given a Python file at /tmp/small.py with 1,200 lines (below 20K threshold)
  When the agent invokes Read on /tmp/small.py
  Then the structure_map_hook exits 0 with no stdout
  And the downstream read_cache_hook handles the call

# anchor: 115.3
Scenario: AST parse failure falls back silently
  Given a malformed Python file at /tmp/broken.py with 25,000 lines and a syntax error
  When the agent invokes Read on /tmp/broken.py
  Then structure_map_hook.extract returns None
  And the hook exits 0 with no stdout (no error surfaced to the model)

# anchor: 115.4
Scenario: TypeScript regex walker captures classes, functions, arrow functions
  Given a TypeScript file with 8,000 lines containing 10 classes and 30 arrow-function exports
  When structure_map_jsts.extract is invoked
  Then the returned StructureMap.classes has length 10
  And StructureMap.functions has length ≥ 30
  And every entry has lineno > 0
```

## Out of scope

- Tree-sitter integration (heavier, would break the stdlib-only invariant).
- Per-symbol body retrieval (`expand` semantics) — Spec 117 covers the archive-and-retrieve pattern.
- Languages other than Python and JS/TS — token-optimizer ships exactly these two. Adding Go/Rust/etc. is a follow-up spec.
- Caching of structure maps (Spec 113 covers context-cache semantics for content axis).
- License flag: token-optimizer is PolyForm Noncommercial 1.0.0. We re-implement with `ast` + `re`; no source copied. If we ever vendor `structure-map.ts` verbatim, revisit.

## References

- token-optimizer README — "180,000-token Python file → 250-token skeleton (95-99% compression)": https://github.com/alexgreensh/token-optimizer/blob/main/README.md
- token-optimizer file-size limits (Python 800 KB / 20K lines; JS/TS 400 KB / 5K lines): `~/work/vendor/token-optimizer/openclaw/src/structure-map.ts`
- Python stdlib `ast`: https://docs.python.org/3/library/ast.html
- `Plan/JULES_PROTOCOL.md` — gates 1–4
- Spec dependency: `Plan/008-codemode-registry/spec.md`
- Spec dependency: `Plan/114-read-cache-delta-mode/spec.md` — fall-through target below thresholds (this spec runs ahead of it in the PreToolUse chain)
- Spec sibling: `Plan/117-tool-result-archive/spec.md` — archive-and-retrieve pattern for body recovery
