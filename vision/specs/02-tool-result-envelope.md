---
slug: spec-02-tool-result-envelope
type: spec
status: ready
owner: claude
created: 2026-05-19
updated: 2026-05-19
summary: Canonical `tool_result.schema.json`. Pure FastMCP envelope `{ok, data, warnings, next_suggested_tools}`. Column-specific extensions (audit_trail, provenance, etc.) go INSIDE `data`. The root envelope never grows.
affects:
  - vision/specs/02-tool-result-envelope.md
depends_on:
  - vision/00.1-Overview.md
  - vision/agentic/INTEGRATED-DRAFT.md
referenced_by:
  - vision/specs/04-phase-state-envelope.md
  - vision/specs/06-agentic-base.md
  - vision/specs/08-context-base.md
---

# Spec 02 — Tool Result Envelope

## Purpose

Every MCP tool in the matrix returns the same envelope. The envelope shape is **pure FastMCP** and frozen. Column-specific extensions (workflow's `audit_trail`, context's validation provenance, agentic's `dispatch_skill` payload) live ONLY inside `data`. This is the resolution to the Phase 3 envelope-ownership tension: agentic refuses envelope mutation, workflow needs audit info, context demands schema validation — all three are satisfied by treating the root as frozen and the `data` payload as schema-validated-per-tool.

## Schema

JSON Schema (draft 2020-12), `$id = "tag:agency-system.local,2026:schema:shared/tool_result"`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "tag:agency-system.local,2026:schema:shared/tool_result",
  "type": "object",
  "additionalProperties": false,
  "required": ["ok", "data", "warnings", "next_suggested_tools"],
  "properties": {
    "ok": {
      "type": "boolean",
      "description": "True iff the tool completed without error. False indicates a recoverable failure surfaced in `data.error`."
    },
    "data": {
      "type": "object",
      "description": "Tool-specific payload. Column extensions (audit_trail, provenance, gate_state) live as keys inside this object. Per-tool JSON Schemas MAY further constrain this via $ref."
    },
    "warnings": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Human-readable warnings that did NOT block the operation. Used by context hooks to surface non-fatal issues."
    },
    "next_suggested_tools": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Tool names (MCP form: `mcp__<row>_<verb>`) the caller might invoke next. Used by the routing skill for what-next queries."
    }
  }
}
```

## Encoding rules

- The envelope is JSON. UTF-8.
- `data` is ALWAYS an object, never a primitive or array — even when there is no payload (`data: {}` is valid).
- `warnings` and `next_suggested_tools` are ALWAYS arrays, possibly empty.
- Total wire size of the envelope SHOULD stay under 4 KB. Tools producing larger payloads emit a sidecar (see spec 03) and reference the sidecar via `data.artefact_ref`.

## Column extension idioms (informative)

Each column extends the envelope by stuffing fields into `data`:

| Column | Extension key in `data` | Spec |
|---|---|---|
| workflow | `data.audit_trail` | spec 04 (PhaseStateEnvelope wraps tool_result) |
| workflow | `data.gate_state` | spec 05 |
| context | `data.provenance` | spec 08 |
| context | `data.artefact_ref` | spec 03 (sidecar pointer) |
| agentic | `data.dispatch_target` | spec 06 (cross-row dispatch) |

Per-tool JSON Schemas in `context/_shared/schemas/tools/<row>_<verb>.schema.json` MAY constrain the shape of `data` for a specific tool. They are validated by the agentic harness on tool return.

## Worked example — success

```json
{
  "ok": true,
  "data": {
    "track_id": "music/2026/05/whispers",
    "artefact_ref": "result/music/whispers.mp3.meta.json",
    "audit_trail": {
      "skill": "music-producer",
      "phase": "04-master"
    }
  },
  "warnings": [],
  "next_suggested_tools": ["mcp__music_review"]
}
```

## Worked example — recoverable failure

```json
{
  "ok": false,
  "data": {
    "error": {
      "code": "VALIDATION_FAILED",
      "message": "Lyrics contain explicit content but [explicit] flag is unset.",
      "fix_hint": "Run `/bitwize-music:explicit-checker` and accept the flag."
    }
  },
  "warnings": ["streaming lyrics drift detected"],
  "next_suggested_tools": ["mcp__music_explicit_check"]
}
```

## Acceptance criteria (Gherkin)

```gherkin
Scenario: Tool returns canonical envelope
  Given any MCP tool in the matrix completes execution
  When the wire payload is captured
  Then it validates against `tool_result.schema.json`
  And the four root keys are exactly `ok`, `data`, `warnings`, `next_suggested_tools`

Scenario: Root envelope rejects extensions
  Given a tool tries to return `{ok, data, warnings, next_suggested_tools, audit_trail}`
  When the envelope validator runs
  Then validation fails with error "unknown property: audit_trail at root; move under data"

Scenario: Oversized payload triggers sidecar pattern
  Given a tool's `data` would exceed 4 KB serialized
  When the agentic harness intercepts the return
  Then the harness writes a sidecar JSON file in `result/<row>/.meta/`
  And replaces the heavy payload with `data.artefact_ref` pointing at the sidecar
  And the resulting envelope is under 4 KB

Scenario: Per-tool data schema validates
  Given `mcp__music_analysis` declares a per-tool data schema
  When the tool returns
  Then `data` is validated against that schema in addition to the root envelope schema
  And a failure surfaces as `ok=false` with `data.error.code = "DATA_SCHEMA_FAILED"`
```

## Dependencies

- `vision/00.1-Overview.md` (§4 Code Mode) — confirms data-only extension pattern.
- `vision/agentic/INTEGRATED-DRAFT.md` (sections 1-2) — resolves envelope-ownership tension by moving extensions inside `data`.
- `vision/specs/03-sidecar-metadata.md` — defines the sidecar referenced by `data.artefact_ref`.
- `vision/specs/04-phase-state-envelope.md` — wraps `tool_result` in `PhaseStateEnvelope` for workflow yields.
- `vision/specs/08-context-base.md` — owns the schema file in `_shared/schemas/`.
