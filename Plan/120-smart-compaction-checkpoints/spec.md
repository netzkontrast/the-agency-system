---
spec_id: 120
slug: smart-compaction-checkpoints
status: ready
owner: jules
depends_on: [100, 108, 117, 118]
affects:
  - servers/agency-mcp/src/agency_mcp/lib/compaction/__init__.py
  - servers/agency-mcp/src/agency_mcp/lib/compaction/checkpoint.py
  - servers/agency-mcp/src/agency_mcp/lib/compaction/restore.py
  - servers/agency-mcp/src/agency_mcp/lib/compaction/decisions.py
  - servers/agency-mcp/src/agency_mcp/handlers/shared/checkpoint.py
  - servers/agency-mcp/src/agency_mcp/hooks/precompact_hook.py
  - servers/agency-mcp/src/agency_mcp/hooks/compaction_end_hook.py
  - hooks/hooks.json
  - tests/unit/compaction/test_checkpoint.py
  - tests/unit/compaction/test_restore.py
  - tests/unit/compaction/test_decisions.py
  - tests/integration/test_compaction_lifecycle.py
source-repos:
  - token-optimizer @ main
estimated_jules_sessions: 2
domain: cross
wave: C
---

> **Jules: read `Plan/JULES_PROTOCOL.md` before starting.** Run gates 1→4 in order:
> (1) Confidence ≥ 0.90, (2) TDD Red-Green-Refactor, (3) Evidence pasted under `## Evidence`, (4) Self-Review answered.
> Branch: `claude/agency-plugin-refactor-PgMQ4`. Only modify paths under `affects:` below.
> Source repos under `source-repos:` are clone-and-read-only into `~/work/vendor/`; never commit them.
> If anything is ambiguous, open a draft PR labelled `[BLOCKED: clarification]` and stop — do not guess.

# Spec 120 — Smart Compaction Checkpoints (PreCompact snapshots + decision digest restore)

## Why

token-optimizer reports: **"When auto-compact fires, 60-70% of your conversation vanishes. Decisions, error-fix sequences, agent state — all gone."** Their fix: at each of 5 fill thresholds (20%, 35%, 50%, 65%, 80%) **plus** quality-drop triggers (below 80/70/50/40), capture a checkpoint of `{user_messages, decisions, tool_invocations, agent_state}`. On `CompactionEnd`, **restore the richest eligible checkpoint** (not just the most recent) and inject a decision digest so the model knows the gist of what got summarized away.

Real-world reported numbers: "708 messages, 2 compactions, 88% of original context gone" without checkpoints. With them, decision continuity is preserved across compactions — the model still knows the user's intent.

This complements:
- Spec 100 (session-log-mcp) — already captures the raw events; this spec builds checkpoints from them.
- Spec 117 (tool-result-archive) — archived results survive compaction; checkpoint restores the archive ids so the model can re-`expand` them.
- Spec 118 (quality-score) — the compaction-depth signal consumes events this spec emits.

## Done When

- [ ] `agency_mcp.lib.compaction.checkpoint.Checkpoint` dataclass holds `{id, session_id, created_at, fill_pct, quality_score, trigger: Literal["fill_20","fill_35","fill_50","fill_65","fill_80","quality_80","quality_70","quality_50","quality_40","agent_fanout","large_edit_batch"], summary, decisions, tool_invocations, archive_ids, message_count}`.
- [ ] `agency_mcp.lib.compaction.checkpoint.snapshot(session_id, trigger) -> Checkpoint` builds a checkpoint by querying Spec 100's session log for the session's events, producing a compact JSON ≤ 8 KB per checkpoint.
- [ ] `agency_mcp.lib.compaction.checkpoint.persist(cp: Checkpoint) -> str` writes to `~/.cache/agency-system/checkpoints/<session_id>/<id>.json`; returns id.
- [ ] `agency_mcp.lib.compaction.restore.pick_richest(session_id) -> Checkpoint | None` returns the checkpoint with the **highest** `richness` score, computed as `0.5 * fill_pct + 0.3 * len(decisions) + 0.2 * len(tool_invocations)` — NOT the most recent (matches token-optimizer's documented choice).
- [ ] `agency_mcp.lib.compaction.decisions.extract(events: list[SessionLogEvent]) -> list[Decision]` scans for decision statements via the published regex set: `r"(?im)^\s*(decision|chose|going with|let'?s use|we'?ll use|we should|i'?ll go with)\s+[:\-]?\s*(.+)"`. Cap at 10 decisions per session. Only fires on events whose payload length > 500 chars (token-optimizer's threshold).
- [ ] `hooks/precompact_hook.py` runs on `PreCompact`, calls `snapshot(...)` + `persist(...)`, records a session-log event `kind="checkpoint_taken"`.
- [ ] `hooks/compaction_end_hook.py` runs on `CompactionEnd`, calls `pick_richest(...)`, injects a decision digest via `additionalContext` of kind=`compaction_restore` with the format token-optimizer ships: `[Restored from checkpoint {id}: {N} decisions, {M} tool invocations, {K} archived results recoverable via shared_archive_expand]`. Followed by the decision text.
- [ ] `shared_checkpoint_list(session_id)`, `shared_checkpoint_get(checkpoint_id)`, `shared_checkpoint_restore(checkpoint_id)` MCP tools expose the surface. The first two are always-eager; `restore` returns the checkpoint payload so the model can self-rehydrate.
- [ ] `pytest -x tests/unit/compaction/ tests/integration/test_compaction_lifecycle.py` exits 0.
- [ ] Continuity regression: integration test asserts that a checkpointed decision survives a synthetic CompactionEnd event and appears verbatim in the restored digest.

## Source clones (run first)

```bash
git clone --depth=1 https://github.com/alexgreensh/token-optimizer.git \
  ~/work/vendor/token-optimizer
```

License: PolyForm Noncommercial 1.0.0. Read-only reference for thresholds + richness formula. We re-implement in Python (stdlib only).

## Files

- **Create**:
  - `servers/agency-mcp/src/agency_mcp/lib/compaction/__init__.py` — package exports.
  - `servers/agency-mcp/src/agency_mcp/lib/compaction/checkpoint.py` — `Checkpoint`, `snapshot`, `persist`.
  - `servers/agency-mcp/src/agency_mcp/lib/compaction/restore.py` — `pick_richest`, `compose_digest`.
  - `servers/agency-mcp/src/agency_mcp/lib/compaction/decisions.py` — `extract` + regex set.
  - `servers/agency-mcp/src/agency_mcp/handlers/shared/checkpoint.py` — three MCP tools.
  - `servers/agency-mcp/src/agency_mcp/hooks/precompact_hook.py`, `servers/agency-mcp/src/agency_mcp/hooks/compaction_end_hook.py`.
  - `tests/unit/compaction/test_checkpoint.py`, `test_restore.py`, `test_decisions.py`, `tests/integration/test_compaction_lifecycle.py`.
- **Modify**:
  - `hooks/hooks.json` — register `PreCompact` and `CompactionEnd` entries.

## Approach

1. **Gate 1 — Confidence.** Verify Specs 100 + 108 + 117 + 118 shipped. Read `~/work/vendor/token-optimizer/openclaw/src/smart-compact.ts` and `checkpoint-policy.ts` for the trigger list (5 fill thresholds + 4 quality thresholds + 2 event triggers), the richness formula (compose from documented impact), and the decision-extraction regex. Cite SHA.
2. **Implement `decisions.py`.** The regex above runs per session-log event whose `payload` length > 500 chars. Cap output at 10 decisions per session, deduplicated by case-folded text. Each `Decision` carries `{text, source_event_id, captured_at}`.
3. **Implement `checkpoint.snapshot(...)`.** Query the session log for the session's events. Build `Checkpoint` from: most recent user messages (last 8), all `Decision`s from `decisions.extract`, last 20 `tool_invocation` events (compressed to `{tool_name, ts, archive_id}` if Spec 117 archived them), last `quality_snapshot` from Spec 118, fill_pct from session-log metadata. Cap total serialised size at 8 KB — if over, drop oldest tool_invocations first.
4. **Implement `restore.pick_richest`.** Walk every persisted checkpoint for the session. Compute `richness = 0.5 * (fill_pct / 100) + 0.3 * (min(len(decisions), 10) / 10) + 0.2 * (min(len(tool_invocations), 20) / 20)`. Return the max. Tiebreak by most recent.
5. **Implement `compose_digest(cp)`.** Returns the additionalContext payload string. Format: `[Restored from checkpoint {cp.id}: {len(cp.decisions)} decisions, {len(cp.tool_invocations)} tool invocations, {len(cp.archive_ids)} archived results recoverable via shared_archive_expand]\n\nDecisions:\n` followed by `- {decision.text}` per line. Cap total digest at 1,200 tokens.
6. **Author both hooks.** `precompact_hook.py`: read JSON event, derive trigger from event metadata (the model layer publishes which threshold fired), call `snapshot` + `persist`, write `session_log_record(kind="checkpoint_taken", payload={id, trigger, fill_pct, quality_score})`. `compaction_end_hook.py`: call `pick_richest`, on success emit `additionalContext` of kind=`compaction_restore` with `compose_digest(cp)`, log `session_log_record(kind="checkpoint_restored", payload={id})`.
7. **Wire hooks.json.** Add `PreCompact` and `CompactionEnd` entries. Order doesn't matter relative to other plugins; coexists with Spec 108's context-mode handlers.
8. **Implement the three MCP tools.** All snake_case, ≤120-char docstrings, `tags={"domain:shared"}`. `shared_checkpoint_list` paginates per overview §2.1 #6 (cap 20 + cursor). `shared_checkpoint_restore` returns the restored payload; it does NOT actually mutate session state — only the hook on CompactionEnd injects context. The tool exists so the model can self-rehydrate on demand (e.g. after `/clear`).
9. **TDD — Gate 2.** RED: write four test files. Unit tests: decision regex matches the published set; richness formula picks the right checkpoint; snapshot stays under 8 KB. Integration test: build a synthetic session log with 5 decisions and 30 tool invocations, fire `PreCompact`, fire `CompactionEnd`, assert the additionalContext contains all 5 decisions verbatim.
10. **GREEN + REFACTOR.** Implement minimally. Refactor: factor checkpoint-directory helpers into a shared `_paths.py`. **Gate 3 — Evidence.** Paste pytest output, a sample digest dump, and the byte-size of a worst-case checkpoint (8 KB cap respected). **Gate 4 — Self-Review.** Flag the trigger we couldn't reliably detect from hook events (likely `agent_fanout` and `large_edit_batch`) and the fallback (fill thresholds always fire; the event-based triggers are best-effort).

## Acceptance (Gherkin)

```gherkin
# anchor: 120.1
Scenario: PreCompact captures a checkpoint under 8 KB
  Given a session log with 50 events including 3 decisions and 12 tool invocations
  When the precompact_hook processes a PreCompact event with fill_pct=65
  Then checkpoint.snapshot(...) returns a Checkpoint whose serialised JSON is ≤ 8192 bytes
  And the Checkpoint contains all 3 decisions verbatim
  And persist(...) writes the checkpoint to ~/.cache/agency-system/checkpoints/<session_id>/

# anchor: 120.2
Scenario: Richest-checkpoint selection beats most-recent
  Given two checkpoints for a session: A at fill_pct=80 with 1 decision, B at fill_pct=50 with 9 decisions
  When restore.pick_richest(session_id) is called
  Then it returns checkpoint B (richer despite earlier fill)
  And not checkpoint A

# anchor: 120.3
Scenario: CompactionEnd injects decision digest with archive recovery hint
  Given a checkpoint at id="cp_abc123" with 5 decisions and 4 archive_ids
  When the compaction_end_hook processes a CompactionEnd event
  Then additionalContext of kind="compaction_restore" is emitted
  And the message contains exactly the substring "Restored from checkpoint cp_abc123: 5 decisions"
  And the message contains "4 archived results recoverable via shared_archive_expand"
  And every decision.text appears verbatim in the digest body

# anchor: 120.4
Scenario: Decision extraction caps at 10 per session and dedupes
  Given a session with 15 messages each containing the same "let's use FastMCP" phrase
  When decisions.extract(events) is called
  Then the result contains exactly 1 Decision (deduplicated by case-folded text)
  When 12 distinct decision statements exist across separate events
  Then the result contains exactly 10 Decisions (cap honoured)
```

## Out of scope

- Replacing Claude Code's native compaction algorithm — we only wrap it with checkpoint/restore around its events.
- Cross-session checkpoint sharing — each session owns its own checkpoint directory.
- Per-user checkpoint dashboards — Wave C+; this spec ships data, not UI.
- LLM-based decision summarisation — regex extraction stays cheap and deterministic; LLM summarisation would burn tokens during compaction (defeats the purpose).
- License flag: token-optimizer is PolyForm Noncommercial 1.0.0. We re-implement the checkpoint/restore algorithm in Python; no source copied.

## References

- token-optimizer README — checkpoint thresholds + richest-eligible restore + decision injection: https://github.com/alexgreensh/token-optimizer/blob/main/README.md
- token-optimizer smart-compact source: `~/work/vendor/token-optimizer/openclaw/src/smart-compact.ts`
- token-optimizer checkpoint-policy source: `~/work/vendor/token-optimizer/openclaw/src/checkpoint-policy.ts`
- `Plan/JULES_PROTOCOL.md` — gates 1–4
- Spec dependency: `Plan/100-session-log-mcp/spec.md` (event source)
- Spec dependency: `Plan/108-context-mode-integration/spec.md` (hooks.json wiring + PreCompact event flow)
- Spec dependency: `Plan/117-tool-result-archive/spec.md` (archive_ids preserved across compaction)
- Spec dependency: `Plan/118-quality-score-telemetry/spec.md` (quality_snapshot consumed for triggers)
- Spec sibling: `Plan/119-loop-detection/spec.md` (sibling fast-twitch quality signal)
