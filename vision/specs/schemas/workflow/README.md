# Workflow Column Schemas

This directory contains the JSON Schema (Draft 2020-12) definitions for the workflow column. The workflow column owns process state, step-ordering (phases), handoffs, and policy (gates).

## Domain Schemas (Workflow Owns)

- [`phase-node.schema.json`](phase-node.schema.json) — Phase graph node
- [`gate-node.schema.json`](gate-node.schema.json) — Gate graph node
- [`continuation-node.schema.json`](continuation-node.schema.json) — Continuation graph node holding blocked-phase state
- [`phase-state-envelope.schema.json`](phase-state-envelope.schema.json) — Wire format workflow returns from MCP tools
- [`pipeline-run.schema.json`](pipeline-run.schema.json) — Audit record of a workflow execution path
- [`gate-yaml.schema.json`](gate-yaml.schema.json) — Schema for the YAML gate-config files
- [`meta-row.schema.json`](meta-row.schema.json) — Config for the meta-row scaffolder

## Interface Schemas (Workflow's POV)

- [`interface-to-agentic.schema.json`](interface-to-agentic.schema.json) — Next-step instruction shape workflow returns to agentic
- [`interface-to-context.schema.json`](interface-to-context.schema.json) — Graph operations workflow sends to context
