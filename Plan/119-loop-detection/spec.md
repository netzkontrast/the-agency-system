---
spec_id: 119
slug: loop-detection
status: ready
owner: jules
depends_on: [100, 108]
affects:
  - servers/agency-mcp/src/agency_mcp/lib/quality/loop_detect.py
  - servers/agency-mcp/src/agency_mcp/hooks/loop_detect_hook.py
  - hooks/hooks.json
  - tests/unit/quality/test_loop_detect.py
  - tests/integration/test_loop_detect_userprompt.py
source-repos:
  - token-optimizer @ main
estimated_jules_sessions: 1
domain: cross
wave: C
---

> **Jules: read `Plan/JULES_PROTOCOL.md` before starting.** Run gates 1→4 in order:
> (1) Confidence ≥ 0.90, (2) TDD Red-Green-Refactor, (3) Evidence pasted under `## Evidence`, (4) Self-Review answered.
> Branch: `Master` (default base for fresh specs post-Wave-A; see JULES_PROTOCOL.md §3). Only modify paths under `affects:` below.
> Source repos under `source-repos:` are clone-and-read-only into `~/work/vendor/`; never commit them.
> If anything is ambiguous, open a draft PR labelled `[BLOCKED: clarification]` and stop — do not guess.

# Spec 119 — Loop Detection (similarity scoring on last 4 user msgs + last 5 tool results)

## Why

token-optimizer reports **loop sessions waste 47K tokens on average** — the model repeats the same diagnostic move (re-read same file, retry same command, ask the same clarifying question) until the user manually intervenes. Their fix: a UserPromptSubmit hook computes Jaccard similarity over the **last 4 user messages and last 5 tool results**; when similarity ≥ 0.7, a single inline note lands in the context: `[Token Optimizer] Loop detected (confidence 0.82). Same tool result returned 4 times. Try a different approach.` The model sees its own pattern and breaks. Session cap: 2 notes per session — we don't want to spam.

This complements Spec 118 (quality score) — that's a slow-moving aggregate; loop detection is a fast-twitch signal that fires at the exact turn the loop manifests.

## Done When

- [ ] `agency_mcp.lib.quality.loop_detect.detect(messages: list[str], tool_results: list[str]) -> LoopDetection` returns `{detected: bool, confidence: float, evidence: str | None}` using the algorithm: take last 4 messages + last 5 tool results, compute pairwise Jaccard similarity on token sets (3-char shingles), take max across pairs. `detected = max_sim >= 0.7`.
- [ ] Confidence is the max pairwise similarity; `evidence` cites the two indices that drove the match (e.g. `"tool_result[-1] ≈ tool_result[-3] (jaccard=0.84)"`).
- [ ] `hooks/loop_detect_hook.py` runs on `UserPromptSubmit`, pulls the last 4 user messages + 5 tool results from the session log (Spec 100's `session_log_query`), invokes `detect(...)`, and on positive detection emits `additionalContext` of kind=`loop_warning`.
- [ ] Per-session cap: **maximum 2 loop notes per session**. State persists at `~/.cache/agency-system/loop-detect/<session_id>.json` with `{count, last_fired_at}`.
- [ ] Cooldown: ≥ 3 turns since the last loop note (mirror token-optimizer's per-session 2-note cap without overlapping nudges).
- [ ] `pytest -x tests/unit/quality/test_loop_detect.py tests/integration/test_loop_detect_userprompt.py` exits 0.
- [ ] Token-budget regression: integration test on a 10-turn synthetic loop (same tool result returned 4 times) asserts exactly 1 note fired AND the note's confidence ≥ 0.7.

## Source clones (run first)

```bash
git clone --depth=1 https://github.com/alexgreensh/token-optimizer.git \
  ~/work/vendor/token-optimizer
```

License: PolyForm Noncommercial 1.0.0. Read-only reference for the algorithm + thresholds. We re-implement in Python (stdlib only).

## Files

- **Create**:
  - `servers/agency-mcp/src/agency_mcp/lib/quality/loop_detect.py` — `detect(...)` + `LoopDetection` dataclass.
  - `servers/agency-mcp/src/agency_mcp/hooks/loop_detect_hook.py` — UserPromptSubmit hook.
  - `tests/unit/quality/test_loop_detect.py`, `tests/integration/test_loop_detect_userprompt.py`.
- **Modify**:
  - `hooks/hooks.json` — register hook entry under `UserPromptSubmit` after the quality-score hook (Spec 118).

## Approach

1. **Gate 1 — Confidence.** Verify Spec 100 (`session_log_query`) and Spec 118's hooks.json wiring are in place. Read `~/work/vendor/token-optimizer/openclaw/src/quality.ts` for the loop-detection section: 4 user msgs + 5 tool results window, Jaccard on shingles, 0.7 threshold, 2-note cap. Cite SHA.
2. **Implement `detect(...)`.** Build shingles: `shingles(s: str) -> set[str]` returns `{s[i:i+3] for i in range(len(s) - 2)}` after lowercasing and whitespace-normalising. Jaccard: `|A ∩ B| / |A ∪ B|`. Compute pairwise sim for every (i, j) pair in `messages ∪ tool_results` (≤ 9² = 81 pairs, fast). Take max. Return `LoopDetection`. Edge cases: empty inputs → `detected=False, confidence=0.0`.
3. **Author `loop_detect_hook.py`.** Read UserPromptSubmit JSON event from stdin. Query session log for last 4 events of `kind="user_message"` and last 5 events of `kind="tool_invocation"` (using their `payload.result` field). Call `detect(...)`. If `detected and confidence >= 0.7`: load state file, check `count < 2` and `(current_turn - last_fired_turn) >= 3`, emit `additionalContext` of kind=`loop_warning` with message `[Agency] Loop detected (confidence {confidence:.2f}). {evidence}. Consider a different approach.`, update state file.
4. **Wire hooks.json.** Add a `UserPromptSubmit` entry. Order doesn't matter relative to Spec 118's quality-score hook — both are independent sinks.
5. **Resilience.** Hook MUST exit 0 silently on any internal failure (missing session log, parse error). Loop detection MUST NEVER break the user's prompt.
6. **Telemetry.** On positive detection, also call `session_log_record(kind="loop_detected", payload={confidence, evidence})`. This lets Spec 118's quality score derive a "loop frequency" feature from history if needed in a future spec.
7. **TDD — Gate 2.** RED: write `test_loop_detect.py` with fixture pairs (identical strings → confidence=1.0, semi-overlapping → ~0.5, disjoint → ~0.0). Integration test: build a 10-turn synthetic fixture where the same tool result returned at turns 4, 6, 8, pipe a UserPromptSubmit JSON through the hook at turn 9, assert exactly one warning fires; pipe another at turn 10, assert NO second warning (cooldown).
8. **GREEN + REFACTOR.** Implement minimally. Refactor: extract `_pairwise_max(strs)` helper for testability.
9. **Stdlib-only check.** No `numpy`, no `scikit-learn`, no `rapidfuzz` — pure Python sets + comprehensions.
10. **Gate 3 — Evidence.** Paste pytest output and the captured `additionalContext` JSON from the integration test. **Gate 4 — Self-Review.** Flag any false-positive risk (e.g. legitimate iteration on the same file by design) and the user-side knob (env var `AGENCY_LOOP_DETECTION=0` to disable).

## Acceptance (Gherkin)

```gherkin
# anchor: 119.1
Scenario: Identical repeated tool result triggers loop detection at confidence 1.0
  Given a window of 5 tool results where indices 0, 2, and 4 are byte-identical
  When loop_detect.detect(messages=[], tool_results=window) is called
  Then result.detected is True
  And result.confidence == 1.0
  And result.evidence references two of the duplicate indices

# anchor: 119.2
Scenario: Disjoint inputs do not trigger detection
  Given 4 user messages and 5 tool results, all lexically disjoint (shared shingles < 5%)
  When loop_detect.detect(...) is called
  Then result.detected is False
  And result.confidence < 0.3

# anchor: 119.3
Scenario: Per-session cap of 2 notes is honoured
  Given a synthetic session where loops are detected on turns 5, 8, 12, and 15
  When the loop_detect_hook processes each UserPromptSubmit
  Then exactly 2 additionalContext emissions occur (turns 5 and 8)
  And turns 12 and 15 are silent

# anchor: 119.4
Scenario: Cooldown of 3 turns between notes
  Given a loop note fired at turn 5
  And the cooldown is 3 turns
  When a second loop is detected at turn 6
  Then NO additionalContext is emitted
  When a third loop is detected at turn 8
  Then a second additionalContext IS emitted (8 - 5 ≥ 3)
```

## Out of scope

- Auto-action on loop detection (auto-clear, auto-compact, auto-rollback) — strictly advisory.
- Tuning the 0.7 threshold per tool — global constant for Wave C.
- Replacing Jaccard with embedding similarity — embeddings cost tokens; shingles cost zero.
- Per-tool loop pattern detection (e.g. "you ran `git status` 4 times") — token-optimizer doesn't ship this either; future spec.
- License flag: token-optimizer is PolyForm Noncommercial 1.0.0. We re-implement the algorithm in Python; no source copied.

## References

- token-optimizer README — "loop sessions average 47K wasted tokens" and "similarity scoring on last 4 user messages + last 5 tool results, confidence ≥0.7, session cap 2": https://github.com/alexgreensh/token-optimizer/blob/main/README.md
- token-optimizer `quality.ts` loop section: `~/work/vendor/token-optimizer/openclaw/src/quality.ts`
- Jaccard background (stdlib `set`): https://en.wikipedia.org/wiki/Jaccard_index
- `Plan/JULES_PROTOCOL.md` — gates 1–4
- Spec dependency: `Plan/100-session-log-mcp/spec.md`
- Spec dependency: `Plan/108-context-mode-integration/spec.md` (hooks.json wiring)
- Spec sibling: `Plan/118-quality-score-telemetry/spec.md` (aggregate quality score; this spec is the fast-twitch signal)
