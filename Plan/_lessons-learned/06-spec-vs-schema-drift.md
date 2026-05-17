---
lesson_id: 06
slug: spec-vs-schema-drift
severity: medium
seen_in: [spec-012]
applies_to:
  - spec-template
  - spec-author
captured_at: 2026-05-17
---

# Spec text drifts from upstream schemas

## Pattern

Spec 012 (Dramatica + NCP libs) Gherkin 012.5/012.6 said:

> Then the returned doc has top-level keys "storyform", "players", "scenes", "metadata"

But the actual vendored `ncp-schema.json` (from `agency/skills/ncp-author/upstream/schema/`) requires `schema_version` + `story.narratives` — a completely different top-level shape. The spec text was authored from memory of an older NCP v1.2.x shape; the v1.3.0 schema has moved on.

Jules caught this mid-implementation and asked. The right resolution: **schema wins** (it's the canonical contract); the compiler generates schema-shaped output; the test asserts against the schema, not the spec text. Self-Review #1 documents the divergence.

The same pattern surfaced in spec 010's term-count (spec said 17, agency vendor actually had 23) and spec 004a's subdir count (spec said 5, actual was 10).

## What to change

### Spec template should encode the "schema wins" rule

Add a `## Schema authority` section to specs that reference an upstream schema/data file:

> When this spec's Gherkin or Done-When list conflicts with the upstream schema/data file (`<path>` at SHA `<sha>`), THE SCHEMA WINS. Implement against the schema, test against the schema, and document the divergence in PR Self-Review #1. Do NOT open `[BLOCKED]` for spec-vs-schema mismatches — the orchestrator will patch the spec post-merge.

### Spec author should re-survey upstream data right before authoring

Whenever a spec references vendored data (ontology counts, schema keys, file counts), the spec author MUST run a survey command and paste the actual numbers into the spec at write-time. Don't rely on memory:

```bash
# For schema specs
jq -r 'keys' upstream-schema.json

# For ontology / data-file specs
jq -r '. | length' ontology.json
find vendor/tools -name '*.py' | wc -l
```

The numbers in the spec then carry write-time provenance.

## Concrete deliverable for the meta-spec

Add a `Schema authority` section to the spec template. Add a `pre-author-survey` checklist that I (the orchestrator) work through whenever I draft a vendor-referencing spec. Possibly add a CI check that compares spec-cited counts against actual file counts in the vendor.
