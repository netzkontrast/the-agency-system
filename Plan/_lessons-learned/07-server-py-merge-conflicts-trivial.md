---
lesson_id: 07
slug: server-py-merge-conflicts-trivial
severity: low
seen_in: [spec-004, spec-006, spec-009]
applies_to:
  - spec-author
  - dispatch-policy
captured_at: 2026-05-17
---

# server.py merge conflicts are trivial — don't serialize specs over them

## Pattern

I held back specs 006 and 009 for a while because all three (004, 006, 009) modify `servers/agency-mcp/src/agency_mcp/server.py` — each spec adds one `register_<domain>_handlers(mcp)` line inside `register_all(mcp)`. I worried about merge conflicts.

In practice, Git's 3-way merge handles these cleanly because the additions are append-only and on different lines. Even when conflicts occur, the resolution is mechanical (accept both, with stable ordering).

Serializing specs over a `server.py` lock would have cost ~3 Jules sessions of wait time. Better to parallelize and resolve conflicts at merge.

## What to change

### Spec author should annotate "append-only `server.py` edit" specs

Specs that add a register call to `server.py` should declare:

```yaml
server_py_edit: append-only   # parallel-safe with other append-only specs
```

The dispatch orchestrator can then fan out all `append-only` specs concurrently without waiting.

### Alphabetical-by-domain ordering

To reduce conflict frequency, the `register_all(mcp)` body should call domains in alphabetical order: `agentic, jules, music, novel, shared`. Each spec inserts at its alphabetical position. Conflicts shrink because the insertion points are deterministic.

The current dispatch prompt already mentions this — formalise it in the spec template.

## Concrete deliverable for the meta-spec

Add the `server_py_edit: append-only` frontmatter field. Update the spec template's Approach section template to call out the alphabetical-insertion convention. Document the parallelization policy in `Plan/000-overview.md` §3 (rollout waves).
