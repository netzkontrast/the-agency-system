---
slug: spec-03-sidecar-metadata
type: spec
status: ready
owner: claude
created: 2026-05-19
updated: 2026-05-19
summary: `.meta.json` sidecar schema for binary artifacts in `result/<row>/`. Carries content-type, hash, provenance, and graph-edge metadata. Ingested by context PostToolUse hook to register artifacts in the SQLite graph without parsing the binary.
affects:
  - vision/specs/03-sidecar-metadata.md
depends_on:
  - vision/00.1-Overview.md
  - vision/context/INTEGRATED-DRAFT.md
referenced_by:
  - vision/specs/02-tool-result-envelope.md
  - vision/specs/07-workflow-base.md
  - vision/specs/08-context-base.md
---

# Spec 03 — Sidecar Metadata

> **DEPRECATED — 2026-05-19**: ⚠️ superseded by
> [`vision/specs/08-context-base-v1.md`](08-context-base-v1.md) §FR5
> ("Artefact node schema is canonical"). The fields enumerated here
> (`sha256`, `content_type`, `derived_from`, `satisfies_phase`,
> `produced_by`, `artifact_driver`, `driver_pointer`) remain canonical
> on the `Artefact` graph node; the **file-on-disk format is retired**.
> The schema previously known as `context/_shared/schemas/sidecar.schema.json`
> was renamed to `artefact-node.schema.json` in N2 PR #155 — `sidecar.schema.json`
> no longer exists in the tree. The body of this spec describes the
> historical `.meta.json` pattern and is retained for archeology only;
> do not implement against it.

## Purpose

Binary artifacts (audio, PDF, image) live in the **result registry** at `result/<row>/` — outside the context graph (per `00.1-Overview.md` §2). They cannot carry frontmatter and must not be parsed by the graph layer. Every binary the system produces is paired with a sidecar JSON holding the metadata the graph DOES need: content-type, hash, provenance, derivation edges.

**Tradeoff vs storing artifacts inside the graph:**

- **Rejected (store in graph):** duplicates every MP3 / PDF into SQLite, explodes the working-memory token cost, forces the graph to parse binary formats it has no business understanding.
- **Accepted (sidecar):** the graph holds only a node referencing the artifact's path + hash + edges. The binary is opaque to the matrix. The sidecar is the join key between registry (the product) and graph (the machine's memory of how the product came to be).

The context column's PostToolUse hook is the sole ingestion path: when a sidecar lands on disk, the hook upserts a node into the SQLite store and emits any `SATISFIES_PHASE` edge declared by it. The binary itself is never read.

## Schema

JSON Schema (draft 2020-12), `$id = "tag:agency-system.local,2026:schema:shared/sidecar"`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "tag:agency-system.local,2026:schema:shared/sidecar",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "artefact_path",
    "content_type",
    "sha256",
    "size_bytes",
    "created_at",
    "produced_by",
    "derived_from"
  ],
  "properties": {
    "artefact_path": {
      "type": "string",
      "description": "Path to the artifact, relative to the repository root. Example: `result/music/whispers.mp3`."
    },
    "content_type": {
      "type": "string",
      "description": "MIME type of the artifact. Examples: `audio/mpeg`, `audio/wav`, `application/pdf`, `image/png`.",
      "pattern": "^[a-z]+/[a-z0-9.+-]+$"
    },
    "sha256": {
      "type": "string",
      "description": "Hex digest (lowercase) of the artifact bytes.",
      "pattern": "^[0-9a-f]{64}$"
    },
    "size_bytes": {
      "type": "integer",
      "minimum": 0
    },
    "created_at": {
      "type": "string",
      "format": "date-time",
      "description": "RFC 3339 UTC timestamp when the artifact was written."
    },
    "produced_by": {
      "type": "object",
      "additionalProperties": false,
      "required": ["skill", "phase", "session_id"],
      "properties": {
        "skill":      {"type": "string", "description": "Slash-command form, e.g. `music-producer`."},
        "phase":      {"type": "string", "description": "Workflow phase id, e.g. `04-master`."},
        "session_id": {"type": "string", "description": "Opaque session id from the workflow runner."}
      }
    },
    "derived_from": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Graph node IDs the artifact derives from. Each becomes a DERIVED_FROM edge in the SQLite graph."
    },
    "satisfies_phase": {
      "type": "string",
      "description": "OPTIONAL. Workflow phase id this artifact completes. Emits a SATISFIES_PHASE edge when set."
    }
  }
}
```

## Filesystem layout

Default placement — sidecar mirrors the artifact relative path under a sibling `.meta/` tree:

```
result/<row>/<sub>/<artefact>           # the binary
result/<row>/.meta/<sub>/<artefact>.meta.json   # the sidecar
```

Example:

```
result/music/whispers/master.mp3
result/music/.meta/whispers/master.mp3.meta.json
```

**Fallback — centralized registry.** When the artifact lives in a user-defined external vault (declared via `[storage] vault_root` in `context/<row>/manifest.toml`) and the FastMCP filesystem sandbox refuses writes to a `.meta/` subdir inside that vault (Context Q1), the writer falls back to a centralized path keyed by row + artifact hash:

```
context/_store/sidecars/<row>/<sha256[:2]>/<sha256>.meta.json
```

The fallback path is fully determined by the sidecar's own `sha256` and the row — no separate index file. The PostToolUse hook scans both locations in this order:

1. `result/<row>/.meta/**/*.meta.json`
2. `context/_store/sidecars/<row>/**/*.meta.json`

Duplicate sidecars (same `sha256`) are deduplicated at ingest; first-seen `created_at` wins.

## Worked example

Music track `master.mp3` produced by `music-producer` at workflow phase `04-master`:

Artifact: `result/music/whispers/master.mp3`
Sidecar: `result/music/.meta/whispers/master.mp3.meta.json`

```json
{
  "artefact_path": "result/music/whispers/master.mp3",
  "content_type":  "audio/mpeg",
  "sha256":        "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08",
  "size_bytes":    7340032,
  "created_at":    "2026-05-19T14:22:07Z",
  "produced_by": {
    "skill":      "music-producer",
    "phase":      "04-master",
    "session_id": "wf-2026-05-19-whispers-a1b2"
  },
  "derived_from": [
    "music/LyricSheet/whispers",
    "music/SunoPrompt/whispers-v3"
  ],
  "satisfies_phase": "04-master"
}
```

The resulting `tool_result` envelope (per spec 02) points at this sidecar:

```json
{"ok": true, "data": {"artefact_ref": "result/music/.meta/whispers/master.mp3.meta.json"}, "warnings": [], "next_suggested_tools": ["mcp__music_review"]}
```

## Acceptance criteria (Gherkin)

```gherkin
Scenario: Writing a binary produces a sidecar
  Given a workflow phase emits `result/music/whispers/master.mp3`
  When the producing tool returns its `tool_result` envelope
  Then a sidecar exists at `result/music/.meta/whispers/master.mp3.meta.json`
  And the sidecar validates against `sidecar.schema.json`
  And `data.artefact_ref` in the envelope points at the sidecar path

Scenario: PostToolUse ingests sidecar into the graph
  Given a freshly written sidecar at `result/music/.meta/whispers/master.mp3.meta.json`
  When the context PostToolUse hook fires
  Then node `music/Artefact/<sha256>` is upserted into SQLite
  And one DERIVED_FROM edge is emitted per entry in `derived_from`
  And if `satisfies_phase` is set, a SATISFIES_PHASE edge is emitted
  And the binary itself is never read

Scenario: Missing sidecar warns, does not fail
  Given a binary at `result/music/whispers/master.mp3` with no sibling sidecar
  When the PostToolUse hook scans the directory
  Then a warning is surfaced via `tool_result.warnings` of the next tool call
  And the binary is left in place and the graph is unchanged

Scenario: Sandbox fallback to centralized registry
  Given `context/music/manifest.toml` declares `[storage] vault_root = "albums"`
  And the FastMCP sandbox rejects writes to `albums/.meta/`
  When the producing tool writes a sidecar
  Then it lands at `context/_store/sidecars/music/<sha256[:2]>/<sha256>.meta.json`
  And the PostToolUse hook discovers it via its second scan path
  And ingest proceeds identically to the default placement
```

## Dependencies

- `vision/00.1-Overview.md` §2 — establishes the result registry and the join-key role of the sidecar.
- `vision/context/INTEGRATED-DRAFT.md` (Sidecar Metadata Pattern, Context Q1) — origin of the pattern and the sandbox fallback question.
- `vision/specs/02-tool-result-envelope.md` — `data.artefact_ref` points at sidecars defined by this spec.
- `vision/specs/07-workflow-base.md` — workflow phases that emit artifacts MUST also write sidecars.
- `vision/specs/08-context-base.md` — owns `sidecar.schema.json` in `_shared/schemas/` and the PostToolUse ingest hook.
