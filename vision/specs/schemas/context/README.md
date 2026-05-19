# Context Column Schemas

This directory contains Draft 2020-12 JSON Schema files defining the CONTEXT column's ontology and its interfaces with the `agentic` and `workflow` columns.

All schemas strictly enforce the `https://agency-system.dev/schemas/context/...` namespace.

## 1. Node Schemas (`nodes/`)
Graph nodes representing the system's structural types. The `Artefact` node incorporates the fields from the deprecated sidecar metadata schema.
- `skill.schema.json`
- `tool.schema.json`
- `phase.schema.json`
- `gate.schema.json`
- `artefact.schema.json`
- `row.schema.json`
- `cell.schema.json`
- `session.schema.json`
- `continuation.schema.json`
- `template.schema.json`
- `schema.schema.json`

## 2. Edge Schemas (`edges/`)
Graph edges representing relationships between nodes.
- `precedes.schema.json`
- `blocks.schema.json`
- `blocked-on.schema.json`
- `produces.schema.json`
- `consumes.schema.json`
- `derived-from.schema.json`
- `satisfies-phase.schema.json`
- `dispatched-to.schema.json`
- `invoked-tool.schema.json`

## 3. Artifact Driver Schemas (`artifact-driver/`)
Contracts for pluggable user-facing artifact storage (e.g., fs, repo, s3).
- `driver-manifest.schema.json`
- `get-bytes-request.schema.json`
- `get-bytes-response.schema.json`
- `put-bytes-request.schema.json`
- `put-bytes-response.schema.json`

## 4. Hook Payload Schemas (`hooks/`)
Validation payloads used by the PreToolUse and PostToolUse decorators.
- `pretooluse.schema.json`
- `posttooluse.schema.json`
- `session-start.schema.json`

## 5. Interface Schemas
How the context column views inputs and outputs from peer columns.
- `interface-to-agentic.schema.json`
- `interface-to-workflow.schema.json`
