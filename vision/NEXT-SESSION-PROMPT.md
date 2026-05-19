---
slug: vision-next-session-prompt
type: session-prompt
status: ready
owner: claude
created: 2026-05-19
updated: 2026-05-19
summary: Self-contained ~3500-char prompt for the next Claude Code session. Goal — ship v0.1 of the `agency` MCP plugin via Jules fan-out + in-session integration.
---

# Next-session start prompt

Paste the block below into a fresh Claude Code session on `netzkontrast/the-agency-system` targeting `Master`.

---

```
GOAL — ship v0.1 of the `agency` MCP plugin: a running FastMCP server with
all three columns (agentic / workflow / context) wired, basic ability to
define a skill + a workflow + a context, and `jules` as the first
materialized row. Done = vision/04-nextsteps.md V1–V11 pass.

ALREADY SHIPPED — do NOT redo:
- Architecture canon at vision/03-architecture.md: ONE FastMCP engine walks
  ONE graph (GraphQLite-backed SQLite at context/_store/ontology.db).
  System metadata in graph; artifact bytes outside via pluggable drivers
  (fs only in v1). NO .meta.json sidecar files. Continuation is a graph
  node.
- Base layer at repo root: agentic/, workflow/, context/ (PRs #148–#150).
  GraphQLite binding, artifact-driver protocol + fs driver, Pre/Post hooks
  (NOT yet wired), cell loader, four-verb contract, pipeline runner with
  lazy_link flag, meta-row scaffolder templates.
- Schema drafts under vision/specs/schemas/{agentic,context}/. workflow/
  patch ready — apply via:
    PYTHONPATH=jules-plugin/mcp-server/src python3 \
      tools/jules-patch-extract.py 17230962122169358495

READ vision/04-nextsteps.md (your playbook with concrete diffs) +
vision/{README,03-architecture}.md + vision/specs/0{6,7,8}*.md. Files you
edit: agentic/_bootloader.py, workflow/_runner/pipeline.py,
context/_hooks/.

EXECUTE IN ORDER:

N0 — close gaps W5 + C5 in one in-session PR (~50 lines + 2 tests).
W5: workflow/_runner/pipeline.py::_run_meta_scaffold must emit Cell+Phase+
Row nodes via context.Store().upsert_node() after each mkdir.
C5: agentic/_bootloader.py::boot() must wrap each registered tool so
context._hooks.pre_tool_use.validate_envelope_in fires before the call
and post_tool_use.ingest fires after. Concrete diffs in 04-nextsteps §N0.

N1 — apply workflow-schemas patch (extract command above), push to a new
branch with mcp__github__push_files, PR to Master.

N2 — canonicalize schemas: diff vision/specs/schemas/<col>/ vs
context/_shared/schemas/. Promote vision drafts over v0 stubs. Rename
context/_shared/schemas/sidecar.schema.json → artefact-node.schema.json
and update the reference in context/_hooks/post_tool_use.py.

N3 — write vision/specs/07-workflow-base-v1.md + 08-context-base-v1.md
locking lazy-link manifest field, driver REGISTRY, Artefact node schema,
graph bootstrap, drop raw-SQLite fallback. User signs off before N4.

N4 — JULES FAN-OUT (3 parallel sessions, strict per-column scope).
Per-column deliverables in 04-nextsteps §N4 — three jules-row cells:
agentic/jules/{manifest,skills/research.md,tools/query.py},
workflow/jules/{manifest, phases/0{1,2}-*.md, gates/*.yaml} + generic
graph walker in pipeline.start for non-meta rows,
context/jules/{manifest,schemas/*,templates/*}.

Use jules-bulk pattern from prior session (jules_create via
PYTHONPATH=jules-plugin/mcp-server/src). Auto-approve at
AWAITING_PLAN_APPROVAL. Recover silent-fail per JULES_PROTOCOL §8: probe
via jules_message, else patch-extract + mcp__github__push_files.

N5 — run V1–V11 from 04-nextsteps. If green, merge to Master, write
vision/05-v0-1-retrospective.md.

CONSTRAINTS:
- ONE engine, ONE graph. No second FastMCP boot, no parallel store.
- GraphQLite fixed; drivers pluggable (only fs mandatory).
- No backwards-compat for deprecated sidecar — pattern is DEAD.
- In-session for integration glue; Jules only for parallel per-column
  work >30 lines.
- Default branch is `Master` (capitalised). All PRs target Master.

START with N0. Report after each phase.
```
