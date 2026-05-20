# Canonical Shape: The Workflow Cell

This document defines the canonical cell-shape for `workflow/<row>`. Every row in the matrix strictly adheres to this structure.

## Cell Layout

Every workflow cell MUST expose the following file tree:

```text
workflow/<row>/
├── manifest.toml         # The structural map of the workflow
├── README.md             # Human-readable overview and context
├── phases/               # The ordered steps of the pipeline
│   ├── 01-first.md       # A single phase definition
│   └── 02-second.md      # Sequential numbering for ordering
├── gates/                # Quality/policy checks between phases
│   └── review-gate.md    # Gate definition
└── handoffs/             # Schemas for envelopes passing between phases
    └── envelope.yaml     # Handoff shape
```

## Manifest Schema

The `manifest.toml` file is the entry point for the workflow cell, loaded during cold-boot. It must conform to this shape:

```toml
[workflow]
row = "<row_name>"
entry_verbs = ["scaffold", "start", "resume"]

[ontology]
artefacts_produced = ["<domain>:<type>"]

[[phases]]
id = "phase-01"
path = "phases/01-first.md"

[[gates]]
id = "gate-01"
path = "gates/review-gate.md"
blocks = "phase-02"
```

## Phase Shape

Each phase is defined in a Markdown file under `phases/`. It relies on YAML frontmatter to declare its constraints.

```markdown
---
id: phase-01
name: First Phase
description: The initial step of the pipeline.
driven_by_skill: agentic/<row>/skills/<skill-name>.md
inputs:
  - context/templates/base-template.md
outputs:
  - workflow/<row>/handoffs/envelope.yaml
---

# Phase Details

Prose describing what this phase represents conceptually and any rules the driving skill must respect.
```

## Gate Shape

Gates enforce policy and quality. They define conditions, failure modes, and recovery paths.

```markdown
---
id: review-gate
type: hard-blocking   # or advisory
blocks_phase: phase-02
---

# Review Gate

## Conditions
1. Confidence score must be >= 0.90.
2. Artefact must pass schema validation.

## Failure Mode
If the gate fails, the handoff envelope is flagged with `ok: false` and the workflow halts.

## Recovery Path
The workflow emits a notification to the user asking for manual correction or override, and transitions to a waiting state.
```

## Handoff Envelope

The `handoffs/envelope.yaml` defines the typed payload passed between phases. To maintain isomorphism with the central MCP architecture, the handoff envelope mirrors the FastMCP `ToolResult` shape:

```yaml
type: object
properties:
  ok:
    type: boolean
    description: Indicates if the upstream phase completed successfully.
  data:
    type: object
    description: The actual artefact or payload produced by the phase.
  warnings:
    type: array
    items: { type: string }
    description: Non-blocking issues encountered during the phase.
  artefacts_written:
    type: array
    items: { type: string }
    description: Paths to artefacts persisted to disk/graph.
  next_suggested_tools:
    type: array
    items: { type: string }
    description: Hints for the agentic column on what skill/tool to invoke next.
required: [ok, data]
```

## Dispatch Contract

The agentic column invokes a phase using a standard four-verb dispatch interface. When a skill drives a phase, it relies on `dispatch_skill`.

**Invocation:**
- **Verb:** `start_phase` (or `resume_phase`)
- **Arguments:**
  - `phase_id` (string): The ID from the manifest.
  - `envelope` (object): The handoff envelope from the previous phase (empty if initial phase).

**Return Shape:**
A completed phase always returns a serialized Handoff Envelope matching the ToolResult schema, determining whether the workflow proceeds to the next gate or phase.
