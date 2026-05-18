---
spec_id: 101
slug: jules-mcp-tool-additions
status: done
owner: jules
depends_on: [006, 100]
affects:
  - servers/agency-mcp/src/agency_mcp/handlers/jules/lifecycle.py
  - servers/agency-mcp/src/agency_mcp/handlers/jules/aliases.py
  - tests/unit/jules/test_session_summary.py
  - tests/unit/jules/test_pr_url.py
source-repos: []
estimated_jules_sessions: 1
domain: jules
wave: C
---

> **Jules: read `Plan/JULES_PROTOCOL.md` before starting.** Run gates 1→4 in order:
> (1) Confidence ≥ 0.90, (2) TDD Red-Green-Refactor, (3) Evidence pasted under `## Evidence`, (4) Self-Review answered.
> Branch: `Master` (default base for fresh specs post-Wave-A; see JULES_PROTOCOL.md §3). Only modify paths under `affects:` below.
> Source repos under `source-repos:` are clone-and-read-only into `~/work/vendor/`; never commit them.
> If anything is ambiguous, open a draft PR labelled `[BLOCKED: clarification]` and stop — do not guess.

# Spec 101 — Jules MCP Tool Additions

## Why

L14's token postmortem proved that the orchestrator's most expensive primitive is `jules_activities` — every call returns the full activity stream and the loop pastes it back into context. The actual signal the orchestrator needs at every poll is a five-line summary: state, title, last five activities, PR URL, patch size. Today that requires four MCP calls plus client-side glue. L10 also documented that `jules_message`'s docstring suggests it is a control-plane mechanism (it is not — sending a message to a paused session does not always resume it). This spec ships three new wrapper tools (`jules_session_summary`, `jules_pr_url`, a re-exported `jules_quota`) backed by the existing handler primitives, flips `jules_activities` to `summary_only=True` by default, and fixes the misleading `jules_message` docstring. The net effect is a >70% drop in tokens-per-poll for the supervisory loop.

## Done When

- [ ] `mcp__jules__jules_session_summary(sid="...")` returns a dict with exactly the keys `state`, `title`, `last_5_activities`, `pr_url`, `patch_size_lines`.
- [ ] `mcp__jules__jules_pr_url(sid="...")` returns the PR URL string (or `None` when no PR exists).
- [ ] `mcp__jules__jules_quota()` is registered as a top-level alias (it currently only lives behind `jules_status`).
- [ ] `jules_activities(sid)` defaults to `summary_only=True`; passing `summary_only=False` is the explicit opt-out for full dumps (L14).
- [ ] `jules_message` docstring contains the literal string "input only, not a control plane" (L10).
- [ ] `pytest -x tests/unit/jules/test_session_summary.py tests/unit/jules/test_pr_url.py` exits 0.
- [ ] The three new tools carry `tags={"domain:jules"}` and follow the `jules_<verb>_<object>` naming convention.
- [ ] `python -c "from agency_mcp.server import create_mcp; m=create_mcp(); print('jules_session_summary' in m._tools)"` prints `True`.

## Source clones (run first)

None — this spec extends an existing handler module. `source-repos:` is `[]`. Read the current shape: `servers/agency-mcp/src/agency_mcp/handlers/jules/lifecycle.py` (which already owns `jules_status`, `jules_activities`, etc.) and `aliases.py` (top-level alias re-exports).

## Files

- **Create**:
  - `tests/unit/jules/test_session_summary.py` — fixtures mocking `lifecycle.get_session()` and `lifecycle.list_activities()`; asserts the exact 5-key shape and the `last_5_activities` slicing.
  - `tests/unit/jules/test_pr_url.py` — asserts `None` is returned when the session has no PR, and the URL string is returned when one exists.
- **Modify**:
  - `servers/agency-mcp/src/agency_mcp/handlers/jules/lifecycle.py` — add `jules_session_summary(sid)`, `jules_pr_url(sid)`, flip `jules_activities` default to `summary_only=True`, fix the `jules_message` docstring.
  - `servers/agency-mcp/src/agency_mcp/handlers/jules/aliases.py` — re-export `jules_quota` at the top level (it currently only resolves via `jules_status`).
- **Move / Delete**: none.

## Approach

1. **Gate 1 — Confidence.** Verify `lifecycle.py` exposes `get_session(sid)`, `list_activities(sid, limit=...)`, and a `pull_request_url` field on the session object. Verify `aliases.py` is the canonical top-level re-export module. Cite both reads in the PR Confidence table. If `pull_request_url` does not exist on the session model, open a draft PR with `[BLOCKED: clarification]` and stop.
2. **Author the test files first (RED).** `test_session_summary.py` mocks the underlying lifecycle primitives, calls `jules_session_summary("sid-abc")`, and asserts the result dict has exactly the five keys listed in Done When. `test_pr_url.py` mocks two cases: session with `pull_request_url=None` returns `None`, session with a URL returns the URL string.
3. **Implement `jules_session_summary`.** Inside `lifecycle.py`, the new function calls `get_session(sid)` once, `list_activities(sid, limit=5)` once, computes `patch_size_lines` from the session's patch field (or 0 when absent), and returns the dict. Decorate with `@mcp.tool(tags={"domain:jules"})`. Keep the docstring ≤120 chars.
4. **Implement `jules_pr_url`.** Thin wrapper: `return get_session(sid).pull_request_url`. Decorate with `@mcp.tool(tags={"domain:jules"})`.
5. **Flip `jules_activities` default.** Change the signature from `summary_only: bool = False` to `summary_only: bool = True`. Update the docstring to note the orchestrator default and the explicit opt-out for post-mortems (L14).
6. **Fix `jules_message` docstring.** Replace any wording that implies control-plane semantics with the verbatim sentence: "Send free-form text to a paused or in-progress session. Input only, not a control plane — does not guarantee resumption." (L10)
7. **Re-export `jules_quota` in `aliases.py`.** Add the top-level alias re-export so `mcp__jules__jules_quota()` resolves without going through `jules_status`. Smoke-check no existing alias collides.
8. **TDD — Gate 2.** Run the two new test files. RED must fail before step 3 lands. GREEN passes once steps 3–4 are in. REFACTOR: extract the activity-slicing helper if both summary and the existing activities path share logic.
9. **Gate 3 — Evidence.** Paste `pytest -x tests/unit/jules/test_session_summary.py tests/unit/jules/test_pr_url.py -v`, `rg -n 'summary_only' servers/agency-mcp/src/agency_mcp/handlers/jules/lifecycle.py`, and `python -c "from agency_mcp.server import create_mcp; m=create_mcp(); print(sorted(t for t in m._tools if t.startswith('jules_')))"` under a clean install (L03).
10. **Gate 4 — Self-Review.** Answer the three Self-Review questions. Dispatch the review subagent per `Plan/_templates/review-subagent-prompt.md` (spec 099).

## Acceptance (Gherkin)

```gherkin
# anchor: 101.1
Scenario: jules_session_summary returns the canonical five-key dict
  Given a Jules session with sid "sid-abc" and three recorded activities
  When the operator calls jules_session_summary(sid="sid-abc")
  Then the result is a dict
  And its keys are exactly: state, title, last_5_activities, pr_url, patch_size_lines
  And last_5_activities has length min(5, total_activities)

# anchor: 101.2
Scenario: jules_pr_url returns None for sessions with no PR
  Given a Jules session whose pull_request_url is None
  When the operator calls jules_pr_url(sid="sid-no-pr")
  Then the return value is None

# anchor: 101.3
Scenario: jules_activities defaults to summary_only=True
  Given the patched lifecycle module
  When the operator runs "rg -n 'summary_only' servers/agency-mcp/src/agency_mcp/handlers/jules/lifecycle.py"
  Then a match shows the default literal value True
  And the docstring explains the explicit opt-out for post-mortems

# anchor: 101.4
Scenario: jules_message docstring no longer implies control-plane semantics
  Given the patched lifecycle module
  When the operator runs "rg -n 'not a control plane' servers/agency-mcp/src/agency_mcp/handlers/jules/lifecycle.py"
  Then at least one match is returned
  And the match sits inside the jules_message docstring
```

## Out of scope

- Implementing the session-log MCP itself — spec 100 ships the underlying event store.
- Wiring `jules_session_summary` to read from the session-log instead of live `jules_activities` — a future spec may add that optimisation.
- Removing the deprecated `summary_only=False` path on `jules_activities` — kept for post-mortem use.
- Any change to the watcher / poller loop that consumes these tools — the orchestrator-discipline skill (spec 099) documents the new contract.
- Adding new Jules lifecycle primitives (start/stop/resume) — the gap tracked in L08 is documented in spec 099 §Appendix, not fixed here.

## References

- `Plan/JULES_PROTOCOL.md` (gates 1–4, §8 token-discipline cross-reference)
- `Plan/_lessons-learned/08-jules-mcp-tool-gaps.md`
- `Plan/_lessons-learned/10-jules-message-can-revive-but-unreliable.md`
- `Plan/_lessons-learned/14-token-consumption-postmortem.md`
- Spec dependency: `Plan/006-jules-handlers-port/spec.md` (`lifecycle.py`, `aliases.py` source of truth)
- Spec dependency: `Plan/100-session-log-mcp/spec.md` (event-store contract for future summary backing)
- Spec sibling: `Plan/099-jules-orchestration-improvements/spec.md` (orchestrator-discipline skill consumes these tools)
