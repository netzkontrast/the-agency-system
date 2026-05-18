# Research 03 — Test-coverage baseline (2026-05-18)

> **Question.** Where are the holes in today's test coverage that L1 + L2 should close, and what stays out of scope?
> **Answer.** Six coverage gaps named below; L1 closes 1-4; L2 closes 5; gap 6 stays Plan/023's job.

This research file captures the test-coverage audit done by the parallel sub-agent on 2026-05-18. Numbers and paths cited here are the source for the design's "Done When" rationale.

## 1. Test surface today

- **63 test files** across `tests/`:
  - `tests/smoke/` — 4 files (`test_boot.py`, `test_dev_install.py`, `test_jules_bulk_cli.py`, `test_manifest.py`)
  - `tests/integration/` — 9 files including `test_context_anchor_triad.py`, `test_context_subscriptions.py`, `test_boot_token_budget.py`, `install/test_dev_mode.py`
  - `tests/unit/` — 50 files (large novel handler coverage)
  - `tests/fixtures/` — 8 fixture trees (not test files)
- **37 tests collected** by pytest with current sandbox deps; **44 collection errors** due to missing `fastmcp`, `tiktoken`, `numpy`, `boto3`, etc. — install via `bin/agency-dev-install` resolves them.
- **No `conftest.py`** in `tests/` root. Each test imports `create_mcp` and FastMCP directly.

## 2. Existing patterns we are NOT replacing

L1 layers on top of the existing patterns; it does not displace them:

| Pattern | Where | Keep / Replace |
|---|---|---|
| Full `create_mcp()` boot + `mcp.call_tool()` | `tests/integration/test_context_anchor_triad.py:7-49` | **Keep.** L1's `harness_mcp()` is the same call, memoised. |
| Handler-isolated `FastMCP("test-<domain>") + register_<domain>_handlers(mcp)` | `tests/unit/jules/test_handlers_smoke.py:7-10`, `tests/unit/music/handlers_smoke.py` | **Keep.** Useful for testing one handler module without booting the rest of the surface. L1 is the full-surface complement. |
| Direct private-helper import (`from agency_mcp.handlers.context.anchors import _context_read`) | `tests/integration/test_context_subscriptions.py:178-183` | **Keep.** Tests internal logic without MCP envelope. Out of L1's contract. |
| Hand-stubbed `uv` and `python` for install-script tests | `tests/integration/install/test_dev_mode.py` | **Keep, but extend.** L2 adds a *real* claude-CLI nested invocation; the install test stays as the fast manifest-only check. |

## 3. The six gaps

### Gap 1 — No unified tool-inventory test

No test asserts `len(create_mcp().tools) >= 113`. Smoke tests are domain-isolated (music smoke asserts ≥60 music tools; jules smoke asserts ≥12 jules tools). The cross-domain total never appears. Spec 131 (`test_boot_budget.py`) will assert *token budget* but not necessarily *tool count*. → **Closed by L1.**

### Gap 2 — No SKILL.md schema / name validator

58 SKILL.md files exist (`skills/music/`×54 + `skills/agentic/`×3 + `skills/jules/`×1). No test enforces:
- YAML frontmatter is parseable.
- `name:` field is present and follows the `<domain>-<slug>` convention (the *correct* convention; the `agency-system:` prefix is auto-added by Claude Code).
- `description:` field is present and non-empty.

→ **Closed by L1's `list_skills` verb** — exposing every skill's frontmatter to per-test assertions; a single skills-validator test in `tests/smoke/test_skill_manifest.py` (future Phase 1 sibling spec) can iterate over `list_skills()` and enforce the schema.

### Gap 3 — No real dev-install end-to-end test

`tests/integration/install/test_dev_mode.py` mocks `uv` and `python` (the test creates fake bin shims at `tmp_path / "bin"`). It verifies the script's flow control but never exercises `uv pip install -e .` against the real `servers/agency-mcp/pyproject.toml`. → **Closed in part by L1** (which assumes the install ran and surfaces a clear error if not), and **completely closed by L2** (which runs the actual `claude --plugin-dir` boot against the installed package).

### Gap 4 — No in-memory tool invocation as a generic helper

`tests/integration/test_context_anchor_triad.py` is the closest, but it's a single integration test specific to the context triad. Phase 1's incoming smoke tests will each need to invoke representative tools (e.g. `health_check`, a music tool, a novel tool). Without a shared helper, each test re-implements the `await mcp.call_tool(...) → result.content[0].text → json.loads` ritual. → **Closed by L1's `call_tool` verb.**

### Gap 5 — No real-boot fidelity for `--plugin-dir`

The pre-PR-115 test attempted this but used the chat-routed `/help` probe and was flaky. PR #115's interim `claude plugin validate` is deterministic but doesn't exercise `--plugin-dir`. → **Closed by L2.**

### Gap 6 — No external-agent reachability test

`agency-mcp` is only reachable to Claude Code (via `--plugin-dir` or installed plugin). Cursor, Codex CLI, Jules sandboxes, bash-only LLM harnesses have no way in. → **NOT closed here.** Plan/023 owns this gap; its daemon + CLI design is the answer. L1 + L2 deliberately don't try to solve it.

## 4. Coverage estimate against the 114-tool surface

Of the ~114 registered tools, current tests **exercise** (call, assert on response) a small fraction:

| Domain | Tools registered (approx) | Exercised by tests today |
|---|---|---|
| music | 82 | 0 directly; 1 smoke test counts them (`tests/unit/music/handlers_smoke.py`) |
| novel | 83 | 0 directly; novel unit tests target internal helpers, not tools |
| jules | 28 | 0 directly; jules-handlers smoke counts them |
| context | 4 | 4 (`test_context_anchor_triad.py` covers `context_search`, `context_describe`, `context_read`, plus `notifications/resources/updated`) |
| shared | 8 | 0 directly |
| **Total** | **~114** | **~4 directly** |

L1's `call_tool` verb does not *test* the 110 untouched tools, but it makes adding such tests cheap. The decision of *which* tools each Phase 1 smoke test should call belongs to those specs (131, 105), not to this design.

## 5. Why a `conftest.py` is the right place

Pytest fixtures defined in `tests/conftest.py` are automatically discovered by every test under `tests/`. No imports needed. This means:

- Spec 131's `tests/smoke/test_boot_budget.py` gets `mcp`, `tool`, `tools`, `skill` for free.
- Spec 105's `tests/smoke/test_toon_gate.py` gets them for free.
- Future per-spec smoke tests inherit the same vocabulary.

The L1 design picks `conftest.py` (not `pytest_plugins`, not a separate package) to maximise this discoverability — fixtures are pytest's primary extension point and the pattern is universally understood.

## 6. Risk register for L1 + L2

| Risk | Likelihood | Mitigation |
|---|---|---|
| ContextWatcher thread leaks across tests | High | `harness_mcp()` is session-scoped + `pytest_sessionfinish` calls `watcher.stop()` |
| Test isolation broken by shared `create_mcp()` (StateCache mutation) | Medium | StateCache is read-mostly during normal tool calls; tests that mutate state document that they do |
| `claude` CLI flaky in CI under load | Medium | L2 is opt-in (`@pytest.mark.smoke_slow`); CI gates use the marker |
| API auth required for L2 in CI | High | L2 skips if `ANTHROPIC_API_KEY`/keyhelper not set, gracefully |
| L1's lru-cache singleton hides handler-init bugs (only first boot exercised) | Low | Spec 131 explicitly tests cold-boot tokens; that test resets the cache once before measurement |

## References

- Parallel sub-agent reports (this branch's `claude/fix-pr-merge-issues-sn1CS` session, 2026-05-18): Dev-Install audit, MCP+codemode-surface, Skill-routing audit, Test-coverage audit
- `tests/integration/test_context_anchor_triad.py` — canonical in-memory call pattern
- `tests/unit/jules/test_handlers_smoke.py` — handler-isolated pattern
- `tests/integration/install/test_dev_mode.py` — mock-bin install test
- Plan/023-harness-in-harness/spec.md — owns Gap 6 (external-agent reachability)
