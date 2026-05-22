---
lesson_id: 11
slug: side-quest-session-log-mcp
severity: medium
seen_in: [meta]
applies_to:
  - new-mcp-server
captured_at: 2026-05-17
---

# Side-quest — session-log MCP for post-mortem analysis

## Why this is worth building

Throughout this wave I've been hand-grepping Jules activity streams to answer questions like:

- "Which PR had the most blockers?" → manual scroll through 5 PR comments.
- "How long did spec 004a's first attempt run before failing?" → manual timestamp math.
- "Which Jules sessions had AWAITING_USER_FEEDBACK gates?" → paginated `jules_activities` calls per session.

The data exists (in Jules' activity stream + GitHub PR comments + the watcher's JSONL output) but it's scattered. A session-log MCP that **captures the data as it flows** and **lets me query it later** would:

1. Save context-token spend (no need to re-fetch full activity streams during post-mortems).
2. Enable cross-session pattern detection ("scratch-file anti-pattern happened in 3 specs — which ones, what did they have in common?").
3. Provide an audit trail without polluting `~/.bitwize-music/` or any other state dir.

## Sketch (this is just notes — real spec to follow)

### MCP server: `session-log-mcp`

Location: `tools/session-log/` or a new `servers/session-log-mcp/`. Pinned to FastMCP. Backing store: SQLite at `~/.agency-system/session-log/log.db` (atomic, fast, easy to query).

### Tools

| Tool | Returns | Use case |
|---|---|---|
| `session_log_record(kind, payload)` | `{ok, row_id}` | Append-only event capture — orchestrator calls after every Jules state change, PR comment, review verdict |
| `session_log_query(filters, limit)` | `[{event, ts, ...}]` | Filter by spec_id, session_id, kind, time-range |
| `session_log_summary(group_by, since)` | Aggregated counts + averages | "How many blockers per spec; avg time-to-merge per wave" |
| `session_log_export_md(spec_id)` | Markdown report | Generate a per-spec retro doc |

### Schema (rough)

```sql
CREATE TABLE events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts TEXT NOT NULL,  -- ISO 8601 UTC
  kind TEXT NOT NULL,  -- jules_state_change | pr_comment | review_verdict | spec_dispatch | spec_merge
  spec_id TEXT,      -- '004', '004a', '012', etc.
  session_id TEXT,   -- Jules session ID if applicable
  pr_number INTEGER,
  actor TEXT,        -- 'jules' | 'orchestrator' | 'human' | 'subagent'
  payload TEXT NOT NULL  -- JSON blob with the event details
);
CREATE INDEX events_spec ON events(spec_id);
CREATE INDEX events_session ON events(session_id);
CREATE INDEX events_kind_ts ON events(kind, ts);
```

### Token efficiency

- Storage is JSONL/SQLite — disk, not context.
- Query tools return summaries by default, full payloads only via `ref_id` lookup.
- A `session_log_summary` of an entire wave (~50 events) fits in ~500 tokens; reading 5 PR comment threads would be ~15k.

### Integration with the watcher

The combined-poller watcher already produces JSONL events. Sink them into `session_log_record` instead of (or in addition to) printing to stdout. Zero extra orchestrator code.

## Concrete deliverable for the meta-spec

A standalone spec — likely **Plan/100-session-log-mcp/spec.md** — authored after the wave finishes. Probably 1 Jules session to implement (server + 4 tools + schema + smoke test). The reason it's a side-quest: the value compounds across waves, not within the one that builds it.
