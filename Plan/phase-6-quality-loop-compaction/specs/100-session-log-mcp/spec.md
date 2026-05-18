---
spec_id: 100
slug: session-log-mcp
status: ready
owner: jules
depends_on: [001]
affects:
  - servers/session-log-mcp/run.py
  - servers/session-log-mcp/pyproject.toml
  - servers/session-log-mcp/src/session_log_mcp/__init__.py
  - servers/session-log-mcp/src/session_log_mcp/server.py
  - servers/session-log-mcp/src/session_log_mcp/tools/__init__.py
  - servers/session-log-mcp/src/session_log_mcp/tools/record.py
  - servers/session-log-mcp/src/session_log_mcp/tools/query.py
  - servers/session-log-mcp/src/session_log_mcp/tools/summary.py
  - servers/session-log-mcp/src/session_log_mcp/tools/export.py
  - servers/session-log-mcp/src/session_log_mcp/tools/tokens.py
  - servers/session-log-mcp/src/session_log_mcp/db/__init__.py
  - servers/session-log-mcp/src/session_log_mcp/db/schema.py
  - .mcp.json
  - tests/unit/session_log/__init__.py
  - tests/unit/session_log/test_record.py
  - tests/unit/session_log/test_query.py
  - tests/unit/session_log/test_summary.py
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

# Spec 100 — Session-Log MCP Server

## Why

Wave A and Wave B taught us (L11, L12, L14) that the orchestrator has no durable, queryable record of *what happened* across Jules sessions. Today, post-mortems require scraping shell history, GitHub PR comments, and `jules_activities` dumps that blow the token budget every time (L14). When a session reports `completed` but no PR was opened (L12), there is no audit trail to diagnose where it diverged. A dedicated, append-only session-log MCP server backed by a single SQLite file under `~/.agency-system/session-log/log.db` solves three problems at once: durable event history, cheap structured queries, and a markdown-export path for human-readable post-mortems. Spec 099 wires the watcher to call `session_log_record`; this spec ships the server itself.

## Done When

- [ ] `python -m session_log_mcp` (or `servers/session-log-mcp/run.py`) starts cleanly and registers exactly five tools: `session_log_record`, `session_log_query`, `session_log_summary`, `session_log_export_md`, `session_log_record_tokens`.
- [ ] On first start the server creates `~/.agency-system/session-log/log.db` with the `events` table and three indexes (`spec_id`, `session_id`, `(kind, ts)`).
- [ ] `pytest -x tests/unit/session_log/` exits 0 with at least 12 tests across `test_record.py`, `test_query.py`, `test_summary.py`.
- [ ] `.mcp.json` declares the `session-log` server entry pointing at `servers/session-log-mcp/run.py`.
- [ ] `session_log_record` is idempotent on `(session_id, ts, kind)` and returns the row id.
- [ ] `session_log_summary(spec_id=...)` returns counts grouped by `kind` plus the most-recent event in ≤200 ms over 10 000 rows (asserted in `test_summary.py` via a seeded fixture).
- [ ] `session_log_export_md(spec_id=...)` returns a markdown document grouped by session, ordered by `ts`.
- [ ] No reference to `the-agency-system` working-tree paths leaks into the SQLite path (always `~/.agency-system/...`).

## Source clones (run first)

None — this spec creates a new server from scratch. `source-repos:` is `[]`. Read `servers/agency-mcp/run.py` and `servers/agency-mcp/src/agency_mcp/server.py` for the FastMCP project shape and copy the conventions (entry-point script, `register_all(mcp)`, `pyproject.toml` deps).

## Files

- **Create**:
  - `servers/session-log-mcp/run.py` — tiny entry-point that imports `session_log_mcp.server.create_mcp` and calls `mcp.run()`.
  - `servers/session-log-mcp/pyproject.toml` — `fastmcp>=3.1.0`, `pydantic>=2`, stdlib `sqlite3` (no extra dep).
  - `servers/session-log-mcp/src/session_log_mcp/__init__.py` — exports `create_mcp`.
  - `servers/session-log-mcp/src/session_log_mcp/server.py` — `create_mcp()` builds the FastMCP, opens the DB via `db.schema.ensure()`, and calls `tools.register_all(mcp)`.
  - `servers/session-log-mcp/src/session_log_mcp/tools/__init__.py` — `register_all(mcp)` calls each module's `register(mcp)`.
  - `servers/session-log-mcp/src/session_log_mcp/tools/record.py` — `session_log_record(kind, payload, spec_id=None, session_id=None, pr_number=None, actor=None, ts=None)`.
  - `servers/session-log-mcp/src/session_log_mcp/tools/query.py` — `session_log_query(spec_id=None, session_id=None, kind=None, since=None, until=None, limit=100)`.
  - `servers/session-log-mcp/src/session_log_mcp/tools/summary.py` — `session_log_summary(spec_id=None, session_id=None)` returns `{counts_by_kind, latest_event, total}`.
  - `servers/session-log-mcp/src/session_log_mcp/tools/export.py` — `session_log_export_md(spec_id=None, session_id=None)` returns markdown text.
  - `servers/session-log-mcp/src/session_log_mcp/tools/tokens.py` — `session_log_record_tokens(session_id, input_tokens, output_tokens, model, ts=None)` thin wrapper around `record.py` with `kind='tokens'`.
  - `servers/session-log-mcp/src/session_log_mcp/db/__init__.py` — exports `get_conn()` and `ensure()`.
  - `servers/session-log-mcp/src/session_log_mcp/db/schema.py` — DDL + index creation + migration check.
  - `tests/unit/session_log/__init__.py`.
  - `tests/unit/session_log/test_record.py` — record idempotency, missing-column defaults, payload round-trip.
  - `tests/unit/session_log/test_query.py` — filter combinations, limit honoured, ordering by `ts DESC`.
  - `tests/unit/session_log/test_summary.py` — counts-by-kind correctness, latest-event semantics, 10 000-row latency budget.
- **Modify**:
  - `.mcp.json` — append a `session-log` entry. No existing entries change.
- **Move / Delete**: none.

## Approach

1. **Gate 1 — Confidence.** Verify `servers/session-log-mcp/` does not exist (`ls servers/ | rg session-log`). Re-read `Plan/_lessons-learned/11-side-quest-session-log-mcp.md` for the schema rationale and L14 for the token-recording shape. Cite both in the PR Confidence table.
2. **Author the schema first.** `db/schema.py` defines a single `events` table: `id INTEGER PRIMARY KEY, ts TEXT NOT NULL, kind TEXT NOT NULL, spec_id TEXT, session_id TEXT, pr_number INTEGER, actor TEXT, payload TEXT NOT NULL`. Create three indexes: `idx_events_spec_id(spec_id)`, `idx_events_session_id(session_id)`, `idx_events_kind_ts(kind, ts)`. `ensure()` is idempotent — `CREATE TABLE IF NOT EXISTS` + `CREATE INDEX IF NOT EXISTS`.
3. **Author the connection helper.** `db/__init__.py` exposes `get_conn(path: Path | None = None)` defaulting to `Path.home() / ".agency-system/session-log/log.db"`, ensuring the parent directory exists, and applying `PRAGMA journal_mode=WAL`. Tests inject a tmp-path override.
4. **Author `record.py`.** `session_log_record` defaults `ts` to `datetime.utcnow().isoformat()`, JSON-serialises `payload` if dict, and uses `INSERT OR IGNORE` on the unique tuple `(session_id, ts, kind)` to make the call idempotent. Return `{id, inserted: bool}`.
5. **Author `query.py` and `summary.py`.** `query.py` builds a parameterised `SELECT` filtering by any combination of `spec_id`, `session_id`, `kind`, `since`, `until`, ordered `ts DESC`, with `LIMIT ?`. `summary.py` runs one `GROUP BY kind` query plus one `ORDER BY ts DESC LIMIT 1`; assert the EXPLAIN QUERY PLAN uses the `(kind, ts)` index.
6. **Author `export.py` and `tokens.py`.** `export.py` calls into `query.py` with no limit, then formats each session as `## session <sid>` heading and each event as a bullet. `tokens.py` is a one-line wrapper: it calls `session_log_record` with `kind='tokens'` and the token counts in `payload`.
7. **Wire `.mcp.json`.** Append the new server entry with `"command": "python"` and `"args": ["servers/session-log-mcp/run.py"]`. Keep the rest of the file byte-identical (preserve key ordering).
8. **TDD — Gate 2.** RED: write `test_record.py` first asserting `INSERT OR IGNORE` semantics on a duplicate `(session_id, ts, kind)` tuple. Then write `test_query.py` filter-matrix tests and `test_summary.py` latency assertion. GREEN: implement the four modules. REFACTOR: pull common `(conn, row_factory)` setup into a `_with_conn` context manager.
9. **Gate 3 — Evidence.** Paste outputs of `pytest -x tests/unit/session_log/ -v`, `python -c "from session_log_mcp.server import create_mcp; m=create_mcp(); print(sorted(m._tools))"`, and `sqlite3 /tmp/test.db '.schema'` after running the test suite once. Capture under a clean install per Gate 3 (L03).
10. **Gate 4 — Self-Review.** Answer the three Self-Review questions. Dispatch the review subagent per spec 099's prompt template.

## Acceptance (Gherkin)

```gherkin
# anchor: 100.1
Scenario: The session-log server exposes exactly five tools
  Given spec 100 has been merged
  When the operator runs "python -c \"from session_log_mcp.server import create_mcp; print(sorted(create_mcp()._tools))\""
  Then stdout lists exactly: session_log_export_md, session_log_query, session_log_record, session_log_record_tokens, session_log_summary

# anchor: 100.2
Scenario: session_log_record is idempotent on (session_id, ts, kind)
  Given a fresh SQLite database created by db.schema.ensure()
  When session_log_record is called twice with the same session_id, ts, and kind
  Then the second call returns inserted=False
  And the events table contains exactly one matching row

# anchor: 100.3
Scenario: session_log_summary completes under 200 ms on 10 000 rows
  Given the events table has been seeded with 10 000 synthetic rows across 5 kinds
  When the operator calls session_log_summary(spec_id="050")
  Then the call returns within 200 ms
  And the returned counts_by_kind dict has exactly 5 entries

# anchor: 100.4
Scenario: session_log_export_md groups by session and orders by ts
  Given two sessions A and B have each recorded three events
  When the operator calls session_log_export_md(spec_id="100")
  Then the returned markdown contains exactly two H2 headings
  And within each section the bullets are sorted ascending by ts
```

## Out of scope

- Wiring `combined-poller` (or any watcher) to call `session_log_record` — spec 099 §watcher integration owns that change.
- Adding a web UI or any HTTP surface (the server is stdio-only FastMCP).
- Cross-machine sync of the SQLite file — `~/.agency-system/` is local-only by design.
- Token-budget alerting / threshold notifications (a future spec may add a `session_log_alert` tool).
- Schema migrations beyond the v1 DDL — when the schema changes, a follow-up spec ships the migration.

## References

- `Plan/JULES_PROTOCOL.md` (gates 1–4)
- `Plan/_lessons-learned/11-side-quest-session-log-mcp.md`
- `Plan/_lessons-learned/12-completed-without-pr-or-state-mismatch.md`
- `Plan/_lessons-learned/14-token-consumption-postmortem.md`
- Spec dependency: `Plan/001-scaffold-plugin-skeleton/spec.md` (FastMCP runtime contract)
- Spec sibling: `Plan/099-jules-orchestration-improvements/spec.md` (watcher integration target)
- Spec downstream: `Plan/101-jules-mcp-tool-additions/spec.md` (`jules_session_summary` keys off the same event stream)
