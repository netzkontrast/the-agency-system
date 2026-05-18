---
spec_id: 118
slug: quality-score-telemetry
status: ready
owner: jules
depends_on: [100, 108]
affects:
  - servers/agency-mcp/src/agency_mcp/lib/quality/__init__.py
  - servers/agency-mcp/src/agency_mcp/lib/quality/score.py
  - servers/agency-mcp/src/agency_mcp/lib/quality/signals.py
  - servers/agency-mcp/src/agency_mcp/handlers/shared/quality.py
  - servers/agency-mcp/src/agency_mcp/hooks/quality_score_hook.py
  - hooks/hooks.json
  - tests/unit/quality/test_score.py
  - tests/unit/quality/test_signals.py
  - tests/integration/test_quality_userprompt.py
source-repos:
  - token-optimizer @ main
estimated_jules_sessions: 2
domain: cross
wave: C
---

> **Jules: read `Plan/JULES_PROTOCOL.md` before starting.** Run gates 1→4 in order:
> (1) Confidence ≥ 0.90, (2) TDD Red-Green-Refactor, (3) Evidence pasted under `## Evidence`, (4) Self-Review answered.
> Branch: `Master` (default base for fresh specs post-Wave-A; see JULES_PROTOCOL.md §3). Only modify paths under `affects:` below.
> Source repos under `source-repos:` are clone-and-read-only into `~/work/vendor/`; never commit them.
> If anything is ambiguous, open a draft PR labelled `[BLOCKED: clarification]` and stop — do not guess.

# Spec 118 — Quality Score Telemetry (7-signal weighted + nudges + session-log integration)

## Why

token-optimizer's most measurable lever for human-loop steering: a **seven-signal weighted quality score** (0-100, letter grade S-F) computed every `UserPromptSubmit` from cheap session telemetry. When the score drops 15+ points OR below 60, an inline `[Quality dropped to 58. Consider /compact to protect context.]` note is injected into the conversation — the model sees its own context degrading and self-corrects. None of our existing specs measure or surface quality. The signals + weights (verbatim from the README):

| Signal | Weight | Meaning |
|---|---|---|
| Context fill | 20% | distance from MRCR cliff |
| Stale reads | 20% | cached file mtime diverged |
| Bloated results | 20% | tool outputs never referenced again |
| Compaction depth | 15% | each compaction loses 60-70% |
| Duplicates | 10% | same system reminders reinjected |
| Decision density | 8% | ratio of decisions to overhead |
| Agent efficiency | 7% | subagent cost-to-value |

We already have Spec 100 (session-log-mcp) capturing the underlying events. This spec layers quality scoring on top, exposes a `shared_quality_status()` tool for the dashboard, and wires the nudge mechanism. Expected impact: NOT a direct token saving but a **20-30% reduction in zombie sessions** (token-optimizer reports loop sessions waste 47K tokens on average; real-time nudges prevent that).

## Done When

- [ ] `agency_mcp.lib.quality.signals` exposes one pure function per signal, each `(session_id: str, log: SessionLogClient) -> float` in [0.0, 1.0] where 1.0 is "perfect" and 0.0 is "worst".
- [ ] `agency_mcp.lib.quality.score.compute(session_id, log) -> QualityScore` returns `{score: int (0-100), grade: str ("S","A","B","C","D","F"), signals: {name: value}, computed_at: datetime}` using the weights in the table above.
- [ ] Grade boundaries match token-optimizer: S=90-100, A=80-89, B=70-79, C=60-69, D=50-59, F=0-49.
- [ ] `shared_quality_status(session_id: str | None = None) -> QualityScore` is an always-eager MCP tool (`tags={"domain:shared"}`, snake_case, ≤120-char docstring; declared in `manifest.json:always_eager`).
- [ ] `hooks/quality_score_hook.py` runs on `UserPromptSubmit`, calls `score.compute(...)`, and if (a) score dropped ≥ 15 points since last check OR (b) crosses below 60 for the first time in this session: emits an `additionalContext` JSON with kind="quality_nudge" and a one-line message matching the token-optimizer format: `[Token Optimizer] Quality dropped to {score}. Consider /compact to protect context.` (we replace "Token Optimizer" with "Agency").
- [ ] Nudge cooldown: ≥ 5 minutes since the last nudge in this session AND ≤ 3 nudges per session. Suppressed on the first check after a `PreCompact` event.
- [ ] Quality snapshots persist to a new `session_log_record(kind="quality_snapshot", payload={score, grade, signals})` per turn — Spec 100 owns the schema; this spec just calls the existing API.
- [ ] `pytest -x tests/unit/quality/test_score.py tests/unit/quality/test_signals.py tests/integration/test_quality_userprompt.py` exits 0.
- [ ] Determinism regression: with a fixed fixture session log, `compute(...)` returns the same `QualityScore` byte-for-byte across runs.

## Source clones (run first)

```bash
git clone --depth=1 https://github.com/alexgreensh/token-optimizer.git \
  ~/work/vendor/token-optimizer
```

License: PolyForm Noncommercial 1.0.0. Read-only reference for the weights, thresholds, and nudge cooldown rules. We re-implement in Python (stdlib + the existing `session-log-mcp` client) — no source copied.

## Files

- **Create**:
  - `servers/agency-mcp/src/agency_mcp/lib/quality/__init__.py` — package exports.
  - `servers/agency-mcp/src/agency_mcp/lib/quality/signals.py` — 7 pure signal functions.
  - `servers/agency-mcp/src/agency_mcp/lib/quality/score.py` — `compute()` + `QualityScore` + grade boundaries.
  - `servers/agency-mcp/src/agency_mcp/handlers/shared/quality.py` — `shared_quality_status` MCP tool.
  - `servers/agency-mcp/src/agency_mcp/hooks/quality_score_hook.py` — UserPromptSubmit hook.
  - `tests/unit/quality/test_score.py`, `tests/unit/quality/test_signals.py`, `tests/integration/test_quality_userprompt.py`.
- **Modify**:
  - `hooks/hooks.json` — register the new `UserPromptSubmit` hook entry.

## Approach

1. **Gate 1 — Confidence.** Verify Spec 100 (`session-log-mcp`) ships `session_log_query(filters, limit)` and supports `kind="quality_snapshot"` or a generic kind. Read `~/work/vendor/token-optimizer/openclaw/src/quality.ts` and the Python equivalent in `measure.py` for the per-signal formulas and grade boundaries. Cite SHA.
2. **Implement the 7 signals (`signals.py`).** Each is a small pure function reading from `SessionLogClient`:
   - `context_fill(...)` — `1.0 - min(1.0, current_context_tokens / model_context_window)`. Uses the most recent `kind="turn_metadata"` event for token counts.
   - `stale_reads(...)` — ratio of cached file reads whose mtime has changed without being re-read; reads from Spec 114's read-cache stats (export a `stats()` API on `ReadCache`).
   - `bloated_results(...)` — fraction of archived results (Spec 117) that were never `expand`ed within the next 20 turns.
   - `compaction_depth(...)` — number of `kind="compaction"` events in the session; signal = `max(0.0, 1.0 - 0.3 * compactions)` (matches the "each compaction loses 60-70%" formulation).
   - `duplicates(...)` — number of identical system reminders fired more than once.
   - `decision_density(...)` — count of `kind="decision_extracted"` events (Spec 120 — Smart Compaction defines this kind) divided by total turn count, clamped to 1.0.
   - `agent_efficiency(...)` — subagent cost-to-value: fraction of `kind="subagent_dispatch"` events whose follow-up `kind="subagent_result"` was referenced by the main session within the next 5 turns.
3. **Implement `score.compute(...)` (`score.py`).** Call all 7 signals, weight per the table above, multiply by 100, round to int. Map to grade via boundaries. Build a `QualityScore` dataclass with `score`, `grade`, `signals: dict[str, float]`, `computed_at: datetime`. Determinism: do not call `time.time()` outside the `computed_at` field.
4. **Implement `shared_quality_status`.** Snake_case MCP tool. If `session_id is None`, derive from the current session context (Spec 100 helper). Returns `QualityScore` serialised. Add to `manifest.json:always_eager` so it's visible without `agency_tool_search` (Spec 104).
5. **Implement nudge hook (`quality_score_hook.py`).** On UserPromptSubmit: compute score, compare to the previous score stored at `~/.cache/agency-system/quality/<session_id>.json`. If drop ≥ 15 or new score < 60 (and previous ≥ 60), check cooldown via the same file's `last_nudge_at`. If cooldown clears AND `nudge_count_this_session < 3`, emit `additionalContext` and update the file. Also call `session_log_record(kind="quality_snapshot", payload={score, grade, signals})` regardless of whether a nudge fired. **Always** suppress the nudge on the first check after a `PreCompact` event (read the most recent compaction timestamp from the session log).
6. **Wire hooks.json.** Add the new entry under `UserPromptSubmit` after any context-mode handlers (Spec 108 owns ordering of context-mode events). The hook is non-blocking; on internal error, exit 0 silently — quality scoring MUST NEVER break the user's prompt.
7. **TDD — Gate 2.** RED: write three test files. Unit tests for each signal use fixture session-log payloads. Score test asserts grade boundaries at the exact 50/60/70/80/90 cusps. Integration test pipes synthetic UserPromptSubmit JSON through the hook and asserts the cooldown, the 3-nudge cap, and the post-compact suppression.
8. **GREEN.** Implement minimally.
9. **REFACTOR.** Lift `_load_state(session_id) / _save_state(session_id, state)` into a shared helper. Confirm signal functions remain pure (no I/O outside `SessionLogClient`).
10. **Gate 3 — Evidence.** Paste pytest output, a sample `QualityScore` dump on a synthetic 100-turn fixture, and the deterministic-replay byte-for-byte assertion. **Gate 4 — Self-Review.** Flag the signal whose formula deviated from token-optimizer's exact implementation (if any) and the rationale (e.g. "stale_reads inverted from their definition because we measure 1.0=perfect not 0.0=perfect").

## Acceptance (Gherkin)

```gherkin
# anchor: 118.1
Scenario: Quality score weights sum to 1.0
  Given the score.compute weights table
  When the test sums the seven weights
  Then the sum equals 1.0 within floating-point tolerance (±1e-9)

# anchor: 118.2
Scenario: Grade boundaries match token-optimizer
  Given QualityScore.grade is computed from QualityScore.score
  When score=89 grade="A", score=90 grade="S", score=49 grade="F", score=50 grade="D"
  Then each assertion holds

# anchor: 118.3
Scenario: Nudge fires once per drop, respects cooldown, capped at 3 per session
  Given a fixture session with quality dropping from 85 → 67 → 55 → 42 → 38 across 4 UserPromptSubmit events
  And no compaction has occurred
  When the quality_score_hook processes each event
  Then exactly 3 nudges are emitted via additionalContext (drops at 67, 55, and the first <60 cross is satisfied by the same chain)
  And the 4th UserPromptSubmit (score=38) does NOT emit a nudge

# anchor: 118.4
Scenario: Nudge suppressed for one turn after PreCompact
  Given the previous turn fired a PreCompact event
  And the current quality score is 45 (a drop of 30 from before the compact)
  When the quality_score_hook processes UserPromptSubmit
  Then no nudge is emitted
  But session_log_record(kind="quality_snapshot", payload={score:45,...}) IS recorded
```

## Out of scope

- Live status-line / terminal UI (token-optimizer's `setup-quality-bar` feature). We expose `shared_quality_status` only; UI is a separate spec.
- A standalone SQLite "trends.db" — we re-use Spec 100's session-log as the canonical store (one event canon, per Spec 108's design).
- Per-signal tuning UI / dashboard — Wave C.
- Auto-actions on low quality (auto-compact, auto-clear) — strictly advisory; the model decides what to do.
- License flag: token-optimizer is PolyForm Noncommercial 1.0.0. We re-implement signals in Python; the seven-signal table and grade boundaries are factual claims, not copyrightable expression. No source copied.

## References

- token-optimizer README — 7-signal table with weights, S-F grade boundaries, nudge cooldown rules: https://github.com/alexgreensh/token-optimizer/blob/main/README.md
- token-optimizer `quality.ts`: `~/work/vendor/token-optimizer/openclaw/src/quality.ts`
- token-optimizer measure.py quality module: `~/work/vendor/token-optimizer/skills/token-optimizer/scripts/measure.py`
- MRCR benchmark (basis for context-fill weight): https://github.com/openai/mrcr
- `Plan/JULES_PROTOCOL.md` — gates 1–4
- Spec dependency: `Plan/100-session-log-mcp/spec.md` (event canon)
- Spec dependency: `Plan/108-context-mode-integration/spec.md` (hooks.json wiring conventions)
- Spec sibling: `Plan/119-loop-detection/spec.md` (complementary real-time degradation signal)
- Spec sibling: `Plan/120-smart-compaction-checkpoints/spec.md` (consumes compaction events this spec scores against)
