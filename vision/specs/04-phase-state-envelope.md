---
slug: spec-04-phase-state-envelope
type: spec
status: ready
owner: claude
created: 2026-05-19
updated: 2026-05-19
summary: `PhaseStateEnvelope` — workflow's async yield envelope. Wraps a tool_result with phase metadata so multi-phase pipelines can suspend on a gate or user-input and resume across turns. Serialized as JSON to `workflow/_state/<session_id>/<phase_id>.json`.
affects:
  - vision/specs/04-phase-state-envelope.md
depends_on:
  - vision/specs/02-tool-result-envelope.md
  - vision/workflow/INTEGRATED-DRAFT.md
referenced_by:
  - vision/specs/06-agentic-base.md
  - vision/specs/07-workflow-base.md
---

# Spec 04 — Phase State Envelope

> **STATUS — 2026-05-19**: 🟡 **Partial-deprecation.** Per `vision/03-architecture.md` §4 & §9, the TypedDict wire format defined below remains canonical for tool returns. The **file-on-disk serialization** (`workflow/_state/<session_id>/<phase_id>.json`) is SUPERSEDED — `Continuation` is now a graph node in `context/_store/ontology.db`, upserted via `context.upsert_node(Continuation{...})`. The shipped implementation (PR #150) already follows the new model: `workflow/_runner/envelope.py::persist` writes to the graph, and the `workflow/_state/` directory is GONE. Sections of this spec describing file paths, atomic-write rename, and the TTL sweep against on-disk JSON are obsolete; sweep semantics will move to the graph-side `Continuation` node.

## Purpose

A workflow pipeline is multi-phase, gated, and frequently blocked on a human reply. The MCP wire is request/response — there is no streaming "yield" primitive. The `PhaseStateEnvelope` is the **async-yield envelope** the workflow runner returns whenever a phase suspends. It wraps a canonical `tool_result` (spec 02) with phase metadata so the agentic runner can recognise the pipeline is paused, surface the block reason, persist the runner's internal state, and resume cleanly on the next turn.

This spec freezes the envelope shape, its serialization format, the on-disk layout, and the legal status transitions. Runner internals land in spec 07.

## Schema

### Python TypedDict (source of truth for the in-process shape)

```python
from typing import TypedDict, Literal, Any

class PhaseStateEnvelope(TypedDict):
    status: Literal["running", "blocked_on_gate", "blocked_on_user", "completed", "failed"]
    phase_id: str                # e.g. "02"
    row: str                     # the row this envelope belongs to (kebab-case, matches spec 01)
    session_id: str              # opaque session UUID for resume keying
    opaque_state: dict[str, Any] # workflow's internal state — agentic MUST NOT mutate
    tool_result: dict            # validates against tool_result.schema.json (spec 02)
    blocked_reason: str | None   # human-readable; required when status is "blocked_*"
    resume_token: str | None     # required when status is "blocked_*"; agentic passes this back on resume
```

### JSON Schema (serialized form, `$id = "tag:agency-system.local,2026:schema:workflow/phase_state"`)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "tag:agency-system.local,2026:schema:workflow/phase_state",
  "type": "object",
  "additionalProperties": false,
  "required": ["status", "phase_id", "row", "session_id", "opaque_state", "tool_result", "blocked_reason", "resume_token"],
  "properties": {
    "status":         {"enum": ["running", "blocked_on_gate", "blocked_on_user", "completed", "failed"]},
    "phase_id":       {"type": "string", "pattern": "^[0-9]{2}(-[a-z0-9-]+)?$"},
    "row":            {"type": "string", "pattern": "^[a-z][a-z0-9-]{0,30}$"},
    "session_id":     {"type": "string", "format": "uuid"},
    "opaque_state":   {"type": "object"},
    "tool_result":    {"$ref": "tag:agency-system.local,2026:schema:shared/tool_result"},
    "blocked_reason": {"type": ["string", "null"]},
    "resume_token":   {"type": ["string", "null"]}
  }
}
```

`opaque_state` is intentionally schema-less. It is the workflow runner's private box. The agentic harness is permitted to **read** the envelope and **persist** it untouched, but **MUST NOT** introspect or mutate `opaque_state` — doing so is a hard contract violation enforced by spec 06.

## Serialization rules

- **Location:** `workflow/_state/<session_id>/<phase_id>.json` (relative to repo root).
- **Encoding:** UTF-8 JSON, two-space indent, trailing newline.
- **Atomic write:** the runner writes to `<phase_id>.json.tmp` in the same directory, then calls `os.replace()` to swap. No partial files are ever observable.
- **One file per (session_id, phase_id):** a subsequent yield of the same phase overwrites; resume reads the freshest file.
- **Directory creation:** `workflow/_state/<session_id>/` is created with `mkdir(parents=True, exist_ok=True)` on first write.
- **TTL:** 30 days from file mtime. On every workflow runner boot, scan `workflow/_state/*/` and delete any envelope whose mtime is older than the TTL. Empty `<session_id>/` directories are pruned in the same pass.
- **Resume API:** `workflow.resume(session_id, phase_id, user_response)` reads the envelope, validates against the JSON Schema, restores `opaque_state` into the runner, and continues the phase. If the file is missing or expired, the API returns a `failed` envelope with `data.error.code = "RESUME_EXPIRED"`.

## Status state machine

```
                 ┌──────────────────────────────────────────────┐
                 │                                              │
   [start]       v                                              │
      │     +---------+      ok+input pending      +---------+  │
      ├────>│ running │────────────────────────────│ blocked │  │ resume(token, response)
      │     +---------+                            │_on_user │──┘
      │          │                                 +---------+
      │          │ gate eval: ok=false             ^
      │          v                                 │
      │     +---------+    user/system unblocks    │
      ├────>│ blocked │────────────────────────────┘
      │     │_on_gate │
      │     +---------+
      │          │ phase work completes successfully
      │          v
      │     +-----------+
      ├────>│ completed │   (terminal)
      │     +-----------+
      │
      │     +--------+
      └────>│ failed │     (terminal — unrecoverable)
            +--------+
```

Legal transitions:

| From              | To                                  | Trigger                                  |
|-------------------|-------------------------------------|------------------------------------------|
| (start)           | `running`                           | runner accepts phase invocation          |
| `running`         | `blocked_on_gate`                   | gate evaluator returns `ok: false`       |
| `running`         | `blocked_on_user`                   | phase calls `AskUserQuestion` or equiv.  |
| `running`         | `completed`                         | phase work finishes; `tool_result.ok=true` |
| `running`         | `failed`                            | unrecoverable error in phase             |
| `blocked_on_gate` | `running`                           | `resume()` with satisfying input         |
| `blocked_on_user` | `running`                           | `resume()` with user response            |
| `completed`       | —                                   | terminal                                 |
| `failed`          | —                                   | terminal                                 |

`completed` and `failed` are terminal: the serialized file is retained for audit until TTL eviction, but cannot be resumed. Any `resume()` against a terminal envelope returns `RESUME_TERMINAL`.

## Worked example

A 3-phase music pipeline (`research → draft → master`) on row `music`, session `8f2a1c4e-...`:

**Phase 01 (research) completes normally.** Runner returns:

```json
{
  "status": "completed",
  "phase_id": "01",
  "row": "music",
  "session_id": "8f2a1c4e-3b9d-4f12-9c0a-d1e2f3a4b5c6",
  "opaque_state": {"sources": ["sec-filing-2023"], "verified_at": "2026-05-19T10:00:00Z"},
  "tool_result": {"ok": true, "data": {"phase": "01-research", "artefacts": ["RESEARCH.md"]}, "warnings": [], "next_suggested_tools": ["mcp__music_start"]},
  "blocked_reason": null,
  "resume_token": null
}
```

**Phase 02 (draft) blocks at gate `lyrics-reviewed`.** Runner writes to `workflow/_state/8f2a1c4e-.../02.json`:

```json
{
  "status": "blocked_on_gate",
  "phase_id": "02",
  "row": "music",
  "session_id": "8f2a1c4e-3b9d-4f12-9c0a-d1e2f3a4b5c6",
  "opaque_state": {"draft_path": "drafts/track-02.md", "gate_attempts": 1},
  "tool_result": {"ok": false, "data": {"gate_state": {"id": "lyrics-reviewed", "failed_at": "2026-05-19T10:42:00Z"}, "error": {"code": "GATE_FAILED", "message": "lyric-reviewer has not run on track-02"}}, "warnings": [], "next_suggested_tools": ["mcp__music_review"]},
  "blocked_reason": "gate lyrics-reviewed: lyric-reviewer has not run on track-02",
  "resume_token": "rt_8f2a1c4e_02_a91b"
}
```

The agentic harness surfaces `blocked_reason` to the user. User runs `/music-review`, then issues `workflow.resume(session_id, "02", {"reviewed": true})`. Runner reads `02.json`, restores state, re-evaluates the gate, transitions back to `running`, and on success transitions to `completed`. Phase 03 (master) then proceeds.

## Acceptance criteria (Gherkin)

```gherkin
Scenario: Blocked envelope serializes atomically
  Given a phase yields with status "blocked_on_gate"
  When the workflow runner writes the envelope
  Then a file appears at `workflow/_state/<session_id>/<phase_id>.json`
  And no `.tmp` file remains in the directory
  And the file validates against the phase_state JSON Schema

Scenario: Resume reads and continues
  Given a valid serialized envelope at `workflow/_state/<sid>/02.json` with status "blocked_on_user"
  When `workflow.resume(sid, "02", {"reply": "yes"})` is invoked
  Then the runner reads the file
  And restores `opaque_state` into the in-process runner
  And the next yield has status "running" or a terminal status

Scenario: Expired envelope auto-deletes
  Given an envelope file with mtime older than 30 days
  When the workflow runner boots
  Then the file is deleted as part of TTL sweep
  And the parent `<session_id>/` directory is pruned if empty
  And a subsequent `resume()` against that session returns `data.error.code = "RESUME_EXPIRED"`

Scenario: Agentic refuses to mutate opaque_state
  Given the agentic harness receives a `PhaseStateEnvelope` with `opaque_state = {"k": "v"}`
  When the agentic side handles the yield (e.g., persists, surfaces blocked_reason)
  Then the bytes of `opaque_state` are byte-equal on the way back to `workflow.resume()`
  And any attempted mutation is rejected at the harness boundary with `OPAQUE_STATE_MUTATED`

Scenario: Root extension rejected — extensions go in opaque_state or tool_result.data
  Given a runner produces an envelope with an extra root key `audit_trail`
  When the envelope validator runs
  Then validation fails with "additionalProperties: audit_trail at root not permitted"
  And the fix-hint instructs moving the field into `tool_result.data` (per spec 02) or `opaque_state`
```

## Dependencies

- `vision/specs/01-cell-manifest.md` — `row` shape and the kebab-case regex used here.
- `vision/specs/02-tool-result-envelope.md` — the `tool_result` field validates against that schema; column extensions inside `data` flow through unchanged.
- `vision/specs/05-gate-yaml.md` — `blocked_on_gate` is produced when a gate from that spec evaluates `ok: false`.
- `vision/specs/07-workflow-base.md` — owns the runner, the TTL sweeper, and the `resume()` API surface described above.
