---
slug: spec-01-cell-manifest
type: spec
status: ready
owner: claude
created: 2026-05-19
updated: 2026-05-19
summary: Strict `manifest.toml` schema for every cell in the 3xN matrix. Defines required keys per column, the derivation rules that produce skill/tool names from `(row, column)`, and the validation JSON Schemas used by the context column to enforce isomorphism.
affects:
  - vision/specs/01-cell-manifest.md
depends_on:
  - vision/00.1-Overview.md
referenced_by:
  - vision/specs/06-agentic-base.md
  - vision/specs/07-workflow-base.md
  - vision/specs/08-context-base.md
---

# Spec 01 — Cell Manifest

## Purpose

Every cell in the 3×N matrix has exactly one `manifest.toml`. This is the cell's only required boot file. The strict form contains ONLY what cannot be derived from `(row, column)`. The harness derives everything else (skill names, MCP namespaces, tool prefixes) deterministically. Strictness is the token-economy enforcer.

This spec defines:

- The required keys per column type.
- The derivation rules the harness MUST follow.
- The JSON Schemas (`agentic-cell.schema.json`, `workflow-cell.schema.json`, `context-cell.schema.json`) that validate cells.

## Universal preamble

Every manifest, regardless of column, starts with:

```toml
[cell]
row    = "<row-name>"        # e.g. "music", "novel", "jules"
column = "<agentic|workflow|context>"
```

Validation rules:

- `row` is lowercase, kebab-case, matches `^[a-z][a-z0-9-]{0,30}$`.
- `column` is one of the three literals.
- The cell's filesystem path MUST be `<column>/<row>/manifest.toml`. Mismatch is a validation error.

## Column-specific keys

### Agentic cell (`agentic/<row>/manifest.toml`)

```toml
[cell]
row    = "music"
column = "agentic"

[skills]
exports = ["producer", "master"]   # strict — no row prefix

[tools]
exports = ["analysis", "synthesis", "review"]   # strict — no row prefix

[codemode]
prefers = ["analysis"]   # OPTIONAL — list of tool exports that should boot in Code Mode
```

**Required:** `[cell]`, `[skills]`, `[tools]`.
**Optional:** `[codemode]`.

### Workflow cell (`workflow/<row>/manifest.toml`)

```toml
[cell]
row    = "music"
column = "workflow"

[workflow]
entry_verbs = ["scaffold", "start", "resume"]   # subset of the four-verb contract

[[phases]]
id   = "01"
path = "phases/01-research.md"

[[phases]]
id   = "02"
path = "phases/02-draft.md"

[[gates]]
id            = "research-complete"
path          = "gates/research-complete.yaml"
blocks_phase  = "02"     # the phase this gate guards

[artefacts]
produced = ["track.mp3", "stems/*.wav"]   # globs relative to result/<row>/
```

**Required:** `[cell]`, `[workflow]`, at least one `[[phases]]`.
**Optional:** `[[gates]]`, `[artefacts]`.

### Context cell (`context/<row>/manifest.toml`)

```toml
[cell]
row    = "music"
column = "context"

[ontology]
node_types = ["Track", "Album", "LyricSheet"]

[templates]
lyric_sheet = { path = "templates/lyric_sheet.md.jinja" }
track       = { path = "templates/track.md.jinja" }

[schemas]
track_meta = { path = "schemas/track.schema.json" }

[storage]
vault_root = "result/music"   # OPTIONAL — declares external vault path for this row's artifacts
```

**Required:** `[cell]`, `[ontology]`.
**Optional:** `[templates]`, `[schemas]`, `[storage]`.

## Derivation rules (the harness MUST honor)

Given `row = "music"`, `column = "agentic"`, `skills.exports = ["producer"]`, `tools.exports = ["analysis"]`:

| Surface | Derived value | Owner |
|---|---|---|
| Skill (slash command) | `/music-producer` | agentic harness |
| Skill SKILL.md location | `agentic/music/skills/producer/SKILL.md` | agentic harness |
| MCP tool name | `mcp__music_analysis` | agentic harness |
| MCP namespace prefix | `music_` | agentic harness |
| Ontology node id | `music/Track` | context store |
| Schema id | `tag:agency-system.local,2026:schema:music/Track` | context store |

**Forbidden:** the manifest MUST NOT contain `namespace_prefix`, `skill_name`, or any other field that repeats the row. Lint failure.

## JSON Schemas

The context column owns three JSON Schemas in `context/_shared/schemas/`:

- `agentic-cell.schema.json`
- `workflow-cell.schema.json`
- `context-cell.schema.json`

Each schema:

- Uses JSON Schema draft 2020-12.
- Has `$id = "tag:agency-system.local,2026:schema:<column>-cell"`.
- Declares required keys per the sections above.
- Rejects unknown top-level tables (`additionalProperties: false` at root).
- Validates `row` against the kebab-case regex.
- Validates `[skills].exports` and `[tools].exports` as non-empty arrays of kebab-case strings WITHOUT row prefix (regex assertion).

The schemas are referenced by the context base layer's PreToolUse hook on any write to `*/manifest.toml`.

## Worked example — music row, all three columns

`agentic/music/manifest.toml`:

```toml
[cell]
row    = "music"
column = "agentic"

[skills]
exports = ["producer", "master"]

[tools]
exports = ["analysis", "synthesis", "review"]
```

Derived: skills `/music-producer`, `/music-master`. MCP tools `mcp__music_analysis`, `mcp__music_synthesis`, `mcp__music_review`.

`workflow/music/manifest.toml`:

```toml
[cell]
row    = "music"
column = "workflow"

[workflow]
entry_verbs = ["scaffold", "start", "resume"]

[[phases]]
id   = "01"
path = "phases/01-concept.md"

[[phases]]
id   = "02"
path = "phases/02-lyrics.md"

[[gates]]
id           = "lyrics-reviewed"
path         = "gates/lyrics-reviewed.yaml"
blocks_phase = "03"

[artefacts]
produced = ["track.mp3"]
```

`context/music/manifest.toml`:

```toml
[cell]
row    = "music"
column = "context"

[ontology]
node_types = ["Track", "Album", "LyricSheet"]

[templates]
lyric_sheet = { path = "templates/lyric_sheet.md.jinja" }

[schemas]
track_meta = { path = "schemas/track.schema.json" }

[storage]
vault_root = "result/music"
```

## Acceptance criteria (Gherkin)

```gherkin
Scenario: Strict-form manifest validates
  Given a manifest at `agentic/music/manifest.toml` containing only [cell], [skills], [tools]
  When the context PreToolUse hook validates it
  Then the schema accepts the file
  And no row prefix appears in any export string

Scenario: Redundant prefix is rejected
  Given a manifest contains `[skills] exports = ["music-producer"]`
  When the PreToolUse hook validates it
  Then validation fails with error "row prefix in export string"

Scenario: Derived skill name reaches the agentic harness
  Given `agentic/music/manifest.toml` exports skill "producer"
  When the harness boots
  Then `/music-producer` is registered as a slash command
  And the corresponding `SKILL.md` is located at `agentic/music/skills/producer/SKILL.md`

Scenario: Derived MCP tool name is namespaced
  Given `agentic/music/manifest.toml` exports tool "analysis"
  When the harness boots
  Then the tool is registered as `mcp__music_analysis`
  And there is exactly one such tool in the registry

Scenario: Path mismatch is rejected
  Given a file at `agentic/novel/manifest.toml` declaring `row = "music"`
  When the PreToolUse hook validates it
  Then validation fails with error "filesystem path does not match (row, column)"
```

## Dependencies

- `vision/00.1-Overview.md` — establishes the strict form and the derivation rule that "what is not present cannot be queried via the context graph — and need not be".
- `vision/specs/02-tool-result-envelope.md` — tool exports surface returns conform to the envelope.
- `vision/specs/04-phase-state-envelope.md` — workflow's phase yields wrap the envelope.
- `vision/specs/05-gate-yaml.md` — `[[gates]]` `path` resolves to a YAML file matching that schema.
- `vision/specs/08-context-base.md` — owns the JSON Schemas and validation hooks.
