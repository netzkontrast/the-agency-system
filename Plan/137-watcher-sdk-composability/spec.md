---
spec_id: 137
slug: watcher-sdk-composability
status: draft
owner: jules
depends_on: [007, 100]
affects:
  - jules-plugin/lib/watchers/__init__.py
  - jules-plugin/lib/watchers/base.py
  - jules-plugin/lib/watchers/jules_source.py
  - jules-plugin/lib/watchers/github_pr_source.py
  - jules-plugin/lib/watchers/composite.py
  - jules-plugin/lib/watchers/state.py
  - jules-plugin/skills/jules/references/combined_watcher.py
  - servers/agency-mcp/src/agency_mcp/handlers/agentic/watcher.py
  - servers/agency-mcp/src/agency_mcp/handlers/agentic/__init__.py
  - tests/unit/watchers/test_base.py
  - tests/unit/watchers/test_jules_source.py
  - tests/unit/watchers/test_github_pr_source.py
  - tests/unit/watchers/test_composite.py
  - tests/unit/watchers/fixtures/jules_state_fixture.json
  - tests/unit/watchers/fixtures/github_pr_fixture.json
  - docs/architecture/watcher-sdk.md
source-repos: []
estimated_jules_sessions: 2
domain: agentic
wave: C
---

> **Jules: read `Plan/JULES_PROTOCOL.md` before starting.** Run gates 1→4 in order:
> (1) Confidence ≥ 0.90, (2) TDD Red-Green-Refactor, (3) Evidence pasted under `## Evidence`, (4) Self-Review answered.
> Branch: `Master` (default base for fresh specs post-Wave-A; see JULES_PROTOCOL.md §3). Only modify paths under `affects:` below.
> Source repos under `source-repos:` are clone-and-read-only into `~/work/vendor/`; never commit them.
> If anything is ambiguous, open a draft PR labelled `[BLOCKED: clarification]` and stop — do not guess.

# Spec 137 — Watcher SDK + Composable Polling

## Why

`jules-plugin/skills/jules/references/combined_watcher.py` is the orchestrator's most-reused snippet (Lesson 09: "the combined-poller watcher pattern works") — it polls Jules sessions + GitHub PR comments in one ~100-line file, persists state across restarts to `/tmp/jules_combined_watcher_state.json`, and exits the moment a wake-event fires. But it is **monolithic**: the polling loop, the Jules-API call, the GitHub-REST call, the state-persistence, and the wake-event predicate are all hand-coded inline. Every new event source the orchestrator wants to wait on (Codex bot review status, GitHub Actions check runs, Vercel deploy status, a Spec-100 session-log query, a Spec-099 `affects:` lint result, a Spec-102 PR-rebase staleness check) requires either forking the script or pasting more polling code into the main thread — a P0 token-discipline anti-pattern per L14.

Spec 099 anti-patterns prohibit "watcher heartbeat experiments" (L15b) but the legitimate watcher idiom remains essential. The fix is to extract a small **Watcher SDK** — a `WatcherSource` protocol + a `CompositeWatcher` driver + two concrete sources (Jules + GitHub-PR) — so any future event source ships as a ~30-line `WatcherSource` subclass and the composite driver handles polling, state-persistence, wake-event multiplexing, and structured-event emission. The existing `combined_watcher.py` then becomes a 5-line shim that imports the SDK and wires the two existing sources.

This is the "harness composability" gap Spec 023 does not address: 023 builds a CLI for external agents to *consume* the daemon; this spec builds a library for the orchestrator to *compose its own supervisory polling*. The two are dual.

## Done When

- [ ] `jules-plugin/lib/watchers/base.py` defines an abstract `WatcherSource` class with three methods: `key(self) -> str` (stable identifier for state-persistence; e.g. `"jules:17491..."` or `"github-pr:netzkontrast/repo#33"`), `poll(self, prev_state: dict | None) -> tuple[dict, list[Event]]` (returns `(new_state, new_events_since_prev)`), `is_wake_event(self, event: Event) -> bool` (per-source wake predicate).
- [ ] `Event` is a frozen dataclass with `source_key: str`, `kind: str` (e.g. `"session_state_change"`, `"pr_new_comment"`), `payload: dict`, `timestamp_iso: str`. JSON-serialisable.
- [ ] `jules-plugin/lib/watchers/jules_source.py` implements `JulesSessionSource(WatcherSource)` — wraps the existing `jules_get` call; `is_wake_event` returns True when `kind == "session_state_change"` AND the new state is in `WAKE_STATES = {"AWAITING_PLAN_APPROVAL", "AWAITING_USER_FEEDBACK", "COMPLETED", "FAILED", "CANCELLED"}` (verbatim from current monolith, minus `PAUSED` per L09).
- [ ] `jules-plugin/lib/watchers/github_pr_source.py` implements `GithubPRSource(WatcherSource)` — wraps the existing GitHub-REST comment fetch; `is_wake_event` returns True for any new comment.
- [ ] `jules-plugin/lib/watchers/state.py` provides `StateStore` — a thin wrapper over the existing `/tmp/jules_combined_watcher_state.json` schema, with `get(key) -> dict | None`, `set(key, value)`, `flush()`. The schema is backwards-compatible: `{"sessions": {...}, "prs": {...}}` becomes `{"by_key": {...}}` with an in-place migrator that reads the old shape on first load and writes the new shape on next flush.
- [ ] `jules-plugin/lib/watchers/composite.py` provides `CompositeWatcher` with constructor `(sources: list[WatcherSource], poll_interval_s: int = 60, deadline_hours: int = 6, state_store: StateStore | None = None, sink: Callable[[Event], None] | None = None)`. The `run()` method loops: poll each source, persist state, emit each event via `sink` (default: `print(json.dumps(...))`), exit-zero on the first wake event.
- [ ] `jules-plugin/skills/jules/references/combined_watcher.py` is rewritten as a ≤30-line shim that constructs a `CompositeWatcher([JulesSessionSource(sid) for sid in sids] + [GithubPRSource(**pr) for pr in prs])` and calls `.run()`. Behaviour for the existing CLI invocation `python combined_watcher.py sessions.json prs.json` is unchanged — every emitted JSON line shape is byte-identical to the current output (verified by a snapshot test).
- [ ] `servers/agency-mcp/src/agency_mcp/handlers/agentic/watcher.py` adds one MCP tool `watcher_run_until(sources: list[dict], wake_kinds: list[str], timeout_s: int = 21600)` — runs a `CompositeWatcher` and returns the first wake event as a dict. Each `sources[i]` is `{type: "jules" | "github-pr" | "session-log", ...source-specific-args}`. This is the L09 "Option A" baked-in form.
- [ ] `pytest -x tests/unit/watchers/` exits 0. Covers: (a) `JulesSessionSource.poll` against a recorded fixture returns the expected `Event` list, (b) `GithubPRSource.poll` against a recorded fixture returns the expected `Event` list, (c) `CompositeWatcher` with two sources exits at the first wake event from either source, (d) `StateStore` migrates the legacy schema in place on first load (legacy fixture → run → assert new shape on disk), (e) the rewritten `combined_watcher.py` shim emits byte-identical JSONL to the legacy reference output (snapshot test).
- [ ] `python jules-plugin/skills/jules/references/combined_watcher.py tests/unit/watchers/fixtures/sids.json tests/unit/watchers/fixtures/prs.json` runs end-to-end against a `MockSink` and exits 0.
- [ ] `docs/architecture/watcher-sdk.md` (≤200 lines) describes the `WatcherSource` protocol, the three reference implementations (`Jules`, `GithubPR`, `SessionLog`), the wake-event multiplexing rule, the state-persistence migration path, and one worked example of adding a new source (e.g. a hypothetical `VercelDeploySource`).

## Source clones (run first)

None — this spec refactors existing internal code. `source-repos:` is `[]`. Read the current monolith verbatim: `jules-plugin/skills/jules/references/combined_watcher.py` (107 lines) and confirm its three responsibilities (poll, state, wake-predicate) before splitting.

## Files

- **Create**:
  - `jules-plugin/lib/watchers/__init__.py` — re-exports `WatcherSource`, `CompositeWatcher`, `Event`, `StateStore`.
  - `jules-plugin/lib/watchers/base.py` — `WatcherSource` abstract class + `Event` dataclass.
  - `jules-plugin/lib/watchers/jules_source.py` — `JulesSessionSource`.
  - `jules-plugin/lib/watchers/github_pr_source.py` — `GithubPRSource`.
  - `jules-plugin/lib/watchers/composite.py` — `CompositeWatcher` driver.
  - `jules-plugin/lib/watchers/state.py` — `StateStore` with legacy-schema migration.
  - `servers/agency-mcp/src/agency_mcp/handlers/agentic/watcher.py` — `watcher_run_until` MCP tool.
  - `tests/unit/watchers/test_base.py`, `test_jules_source.py`, `test_github_pr_source.py`, `test_composite.py`.
  - `tests/unit/watchers/fixtures/jules_state_fixture.json`, `github_pr_fixture.json`.
  - `docs/architecture/watcher-sdk.md`.
- **Modify**:
  - `jules-plugin/skills/jules/references/combined_watcher.py` — rewrite as a ≤30-line shim. JSON-line output is byte-identical.
  - `servers/agency-mcp/src/agency_mcp/handlers/agentic/__init__.py` — append one registration line for `watcher_run_until` at end of file (`server_py_edit: append-only` per Spec 099).
- **Move / Delete**: none.

## Approach

1. **Gate 1 — Confidence.** Confirm `jules-plugin/lib/watchers/` does not exist. Re-read `jules-plugin/skills/jules/references/combined_watcher.py` end-to-end and identify the three orthogonal concerns (poll-source, state-persistence, wake-predicate). Verify Spec 007 (Jules skills + commands port) is merged. Cite Lesson 09's "Option B (script in jules-plugin/bin/)" and explain why this spec goes further (library, not just script). Score ≥0.90.
2. **Author `base.py` first (TDD red).** Define `Event` dataclass + `WatcherSource` abstract class. Write `test_base.py::test_watcher_source_is_abstract` that asserts `WatcherSource()` raises `TypeError`. RED → GREEN by adding `abc.ABC` inheritance and `@abstractmethod` decorators.
3. **Author `state.py`.** `StateStore` reads `/tmp/jules_combined_watcher_state.json` if present. Detect legacy schema (`"sessions"` or `"prs"` top-level key) and migrate to `{"by_key": {"jules:<sid>": <state>, "github-pr:<key>": <state>}}`. RED test: write a legacy-shape JSON fixture, instantiate `StateStore`, assert `.get("jules:1234")` returns the migrated value. GREEN: implement the migration in `__init__`.
4. **Author `jules_source.py`.** `JulesSessionSource(sid: str)` — `key()` returns `f"jules:{sid}"`. `poll(prev_state)` calls `jules_get(sid, fields="id,state,title")`, diffs against `prev_state.get("state")`, emits one `Event(kind="session_state_change", ...)` if changed. `is_wake_event(event)` returns True iff `event.payload["new_state"]` is in `WAKE_STATES`. RED-GREEN with a recorded `jules_state_fixture.json`.
5. **Author `github_pr_source.py`.** `GithubPRSource(owner, repo, number)` — `key()` returns `f"github-pr:{owner}/{repo}#{number}"`. `poll(prev_state)` fetches comments via the existing `gh_get` helper (lifted verbatim from the monolith), diffs against `prev_state.get("comment_ids", [])`, emits one `Event(kind="pr_new_comment", ...)` per new comment. `is_wake_event` returns True for any `pr_new_comment`. RED-GREEN with `github_pr_fixture.json`.
6. **Author `composite.py`.** `CompositeWatcher.run()` — loops every `poll_interval_s` until `deadline_hours` or first wake event. For each source: `prev = state_store.get(src.key())`, `new_state, events = src.poll(prev)`, persist new_state, emit each event via `sink`, set `woke = True` if `src.is_wake_event(event)`. Tests: (a) two sources, one fires wake event on iteration 2 → composite exits at iteration 2, (b) no source fires by deadline → composite exits with a `timeout` event.
7. **Rewrite `combined_watcher.py` as a shim.** ≤30 lines. Read sids.json + prs.json (legacy CLI arguments), construct sources, run `CompositeWatcher`. Snapshot test: run the shim against fixtures + capture stdout; assert byte-identical to a known-good golden JSONL file extracted from the current monolith's output (capture once before refactor — Spec 099's evidence discipline).
8. **Add MCP `watcher_run_until`.** Tool body parses `sources[i]["type"]` and constructs the right `WatcherSource`. Returns the first wake event as a JSON-serialisable dict. Tag `domain:agentic`. Docstring ≤120 chars.
9. **Append to `agentic/__init__.py`.** ONE registration line at end of file. Do not refactor existing imports.
10. **Author the docs page.** `docs/architecture/watcher-sdk.md` — ≤200 lines, one sequence diagram of CompositeWatcher → Source → StateStore, one worked example showing how to add a new source class in ~30 lines.
11. **Gate 2 — TDD.** Each source has its own RED-GREEN cycle. The composite test is the integration check. The snapshot test on the rewritten shim is the regression guard.
12. **Gate 3 — Evidence.** Paste `pytest -x tests/unit/watchers/` output, the snapshot diff (must be empty), `python jules-plugin/skills/jules/references/combined_watcher.py` smoke output (≤20 lines), and `python -c "from agency_mcp.server import create_mcp; m=create_mcp(); print('watcher_run_until' in m._tools)"` (must print `True`).
13. **Gate 4 — Self-Review + reviewer dispatch.** Answer the three Self-Review questions; dispatch the Gate-4 reviewer using `Plan/_templates/review-subagent-prompt.md`.

## Acceptance (Gherkin)

```gherkin
# anchor: 137.1
Scenario: WatcherSource is an enforceable contract
  Given a Python module imports WatcherSource from jules-plugin.lib.watchers
  When the module tries to instantiate WatcherSource() directly
  Then a TypeError is raised
  And the error message names "abstract method poll" (or any of the three abstract methods)

# anchor: 137.2
Scenario: CompositeWatcher exits at the first wake event from any source
  Given a CompositeWatcher constructed with [SourceA, SourceB] and poll_interval_s=0
  And SourceA's poll() returns one non-wake event on iteration 1
  And SourceB's poll() returns one wake event on iteration 2
  When the operator calls composite.run()
  Then the method exits with status 0
  And the returned event has source_key matching SourceB's key()
  And no further polls occur on either source

# anchor: 137.3
Scenario: Legacy state schema is migrated transparently on first load
  Given /tmp/jules_combined_watcher_state.json contains the legacy shape {"sessions": {"123": "QUEUED"}, "prs": {}}
  When StateStore() is instantiated
  Then StateStore.get("jules:123") returns "QUEUED"
  And after the first flush, the file content matches {"by_key": {"jules:123": "QUEUED"}}
  And the migration is logged once at INFO level

# anchor: 137.4
Scenario: Rewritten combined_watcher.py shim emits byte-identical JSONL
  Given a recorded golden JSONL file from the legacy combined_watcher.py against known fixtures
  When the operator runs the rewritten shim against the same fixtures
  Then stdout is byte-identical to the golden file
  And the shim is ≤ 30 source lines (verified by wc -l)

# anchor: 137.5
Scenario: watcher_run_until MCP tool composes Jules + PR sources via the SDK
  Given the daemon is running and watcher_run_until is registered
  When the orchestrator calls watcher_run_until(sources=[{type:"jules", sid:"1234"}, {type:"github-pr", owner:"x", repo:"y", number:33}], wake_kinds=["session_state_change","pr_new_comment"])
  And the Jules session 1234 transitions to COMPLETED
  Then the tool returns a dict with kind="session_state_change", source_key="jules:1234", payload.new_state="COMPLETED"
  And the tool's response is ≤ 1000 tokens (measured by tiktoken)
```

## Out of scope

- **Spec 100's session-log MCP source.** A `SessionLogSource(WatcherSource)` is the obvious third reference implementation but its `poll()` semantics depend on Spec 100's query API, which has not landed yet. Document the extension point in the SDK docs and defer the source to a follow-up after Spec 100 merges.
- **Watcher daemonisation / systemd integration.** The current monolith runs as a foreground script invoked by the orchestrator on demand. Daemonisation (PID file, log rotation, restart-on-crash) is Spec 023's territory; the SDK stays in-process.
- **Cross-process state synchronisation.** `StateStore` writes to `/tmp/jules_combined_watcher_state.json` with no file locking — single-watcher-at-a-time is the implicit contract. Multi-watcher concurrency is a future spec.
- **Generic event-bus pattern (pub/sub, listeners).** The SDK ships one-shot wake-event semantics: composite.run() exits on the first wake. Long-running watchers with multiple subscribers are a different shape; not this spec.
- **`PAUSED` as a wake state.** Per L09, `PAUSED` is intentionally excluded from `WAKE_STATES` because it is a transient state during `jules_message` processing, not a human-required pause. Re-adding it requires its own ADR.
- **The L15b "watcher heartbeat experiment" anti-pattern.** Spec 099 forbids per-tool heartbeats; this SDK ships the legitimate composite-watcher idiom only, and the docs explicitly cite Spec 099 §5 to disambiguate.

## References

- `jules-plugin/skills/jules/references/combined_watcher.py` — the monolith being decomposed (107 lines, verbatim verified 2026-05-18)
- `jules-plugin/skills/jules/references/combined_watcher.md` — the prose explainer of the current pattern
- `jules-plugin/skills/jules/references/parallel-orchestration.md` — fan-out checklist that names the watcher as a hard reliability gate ("verify the watcher daemon is alive")
- `Plan/_lessons-learned/09-watcher-pattern-idiom.md` — explicit Option B/C choice now realised as Option A+B (library + MCP tool)
- `Plan/_lessons-learned/14-token-consumption-postmortem.md` — token-discipline motivation for *not* inlining poll loops into the main thread
- `Plan/099-jules-orchestration-improvements/spec.md` §5 — anti-patterns this spec respects (no heartbeats, no agentMessaged loops); also provides `Plan/_templates/review-subagent-prompt.md`
- `Plan/100-session-log-mcp/spec.md` — the future `SessionLogSource` consumer (extension point in this SDK's docs)
- `Plan/023-harness-in-harness/spec.md` — the dual surface: this spec covers in-process composability, 023 covers external-client surface
- `Plan/101-jules-mcp-tool-additions/spec.md` — neighbouring `domain:agentic` handler conventions
- [PEP 544 — Protocols (structural subtyping)](https://peps.python.org/pep-0544/) — the abstract-method approach used in `base.py`
