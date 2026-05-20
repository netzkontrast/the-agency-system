---
slug: vision-v0-1-retrospective
type: retrospective
status: ready
owner: claude
created: 2026-05-20
updated: 2026-05-20
summary: v0.1 milestone retrospective. What shipped from N0–N5 of vision/04-nextsteps.md, the design decisions that paid off, the bugs that surfaced during verification, and the explicit follow-up list for v0.2.
depends_on:
  - vision/04-nextsteps.md
  - vision/specs/06-agentic-base.md
  - vision/specs/07-workflow-base-v1.md
  - vision/specs/08-context-base-v1.md
referenced_by:
  - vision/README.md
---

# 05-v0-1-retrospective — v0.1 shipped

**Milestone**: a running `agency` MCP plugin with three columns wired,
basic skill/workflow/context definitions, and `jules` as the first
materialized row. **Status**: V2–V11 of the verification checklist green
on the merge candidate (`claude/agency-mcp-v0.1-IyExm`). V1 (`claude plugin
install agency`) is a user-action item and tracked as a smoke test for the
next session.

## What landed

| Phase | Commits | Headline |
|---|---|---|
| N0 | `979eb73` | Closed C5 (hooks not wired) + W5 (meta scaffold blind to graph) |
| N1 | #157 (separate Jules PR) | Workflow-column JSON Schemas (Draft 2020-12) for Phase, Gate, Continuation, Phase-State envelope, Pipeline-Run, Meta-Row, and the two cross-column interfaces |
| N2 | `5510d47` | Canonicalised runtime schemas; `sidecar.schema.json` → `artefact-node.schema.json` with the `artifact_driver` + `driver_pointer` fields |
| N3 | `0fd4baf`, `7821074` | Two v1 specs: `07-workflow-base-v1.md` (FR1–FR7) + `08-context-base-v1.md` (driver REGISTRY, `get_store()` singleton, fallback removal) |
| N4 | `1a507d2`, `d26dc32`, `a7ee639`, `1e1403a`, `5f0fad1` | Three-column row cells for `jules` + generic graph walker + `context.get_store()` singleton + `_MockContext` removal |
| N5 | `e0ecac8` | Bootloader switched to four-verb dispatch; aligned jules paths to the canonical deriver conventions |

Total: roughly two weeks of plan time compressed into two in-session days.
Five Jules sessions fanned out for N4 were ultimately replaced by
in-session subagent work after a duplicate-dispatch incident; the
`superpowers:subagent-driven-development` skill (implementer + spec
reviewer + code-quality reviewer per task, then a final integration
reviewer) is what landed the actual code.

## Verification checklist — actual results

| # | Result | Notes |
|---|---|---|
| V1 | Pending | `claude plugin install agency` — user-driven |
| V2 | ✓ | Four verbs: `mcp__list_tools`, `mcp__call_tool`, `mcp__list_skills`, `mcp__dispatch_skill` — verified after fixing the bootloader's broken `add_tool` loop |
| V3 | ✓ | `test_cold_boot_under_500_tokens` green (was green before the bootloader fix because the test fixture mocked the broken path) |
| V4 | ✓ | `discover()` finds `mcp__jules_query` + `/jules-research` |
| V5 | ✓ | Artefact node lands in `ontology.db` from PostToolUse |
| V6 | ✓ | Meta scaffold emits 3 Cell + 1 Row + 1 Phase per new row |
| V7 | ✓ | `pipeline.start(row="jules", phase_id="01", ...)` reaches `_walk_phase`, invokes `mcp__jules_query`, returns `status="completed"` |
| V8 | ✓ | `/jules-research` skill dispatches |
| V9 | ✓ | ResearchTopic + Finding queryable from ontology.db |
| V10 | ✓ | No `*.meta.json` sidecars under any jules cell directory |
| V11 | ✓ | Continuation persisted as a graph node; `workflow/_state/` does not exist |

## What worked

1. **`superpowers:subagent-driven-development` per-task.** Three implementer
   subagents + spec reviewer + code reviewer per task caught real issues
   (dead branch in `resume()`, unused `g` parameter in
   `_collect_blocking_gates`) before they reached final integration.
   Iteration time was tight — fix-and-re-review loop completed in
   minutes, not the typical multi-day PR cycle.
2. **Spec-panel-driven contract sharpening.** The C1–C5 + M1–M6 panel run
   in N3 produced the v1 specs that the N4 implementers then read as
   their source of truth. The `affects:` allow-list per spec gave each
   subagent a precise file scope, which kept three parallel contributors
   from stepping on each other.
3. **`get_store()` singleton.** Removing `_MockContext` and standardising
   on the singleton accessor (spec 08-v1 §FR1) eliminated three classes
   of test setup bugs and made the resume re-walk implementation
   straightforward.
4. **Disk-scan gate collection as v0.1 simplification.** Spec 07-v1 §FR3
   describes graph-edge gate discovery via `BLOCKS`, but no edge seeder
   exists yet. The implementer's call to fall back to a disk scan of
   `workflow/<row>/gates/*.yaml` (filtered by `blocks_phase`) kept the
   walker functional without forcing the gate-evaluator rewrite into
   this milestone.

## What surprised us

1. **Jules silent-fail recovery is essential.** The N4 fan-out hit a
   duplicate-dispatch on the very first launch — the second dispatch
   inherited the first's incomplete state and produced two parallel
   session sets. JULES_PROTOCOL §8's "verify branch on remote before
   trusting COMPLETED" caught it; the recovery flow (probe via
   `jules_message`, then HALT the duplicates) worked exactly as
   documented. Lesson: any future fan-out should treat the dispatch
   itself as a critical section, not idempotent.
2. **Naming-deriver convention drift.** The N4 task brief I wrote
   instructed implementers to use `agentic/jules/tools/query.py` and
   `agentic/jules/skills/research.md`, but the deriver expects
   `handlers/<export>.py` and `skills/<export>/SKILL.md` respectively.
   The implementers obeyed my brief; the V7 verification caught the
   mismatch. Lesson: when delegating to a subagent, cross-check the
   deriver's canonical paths against the brief, not the other way round.
3. **`FastMCP.add_tool` semantics changed.** The N0 bootloader called
   `mcp.add_tool(wrapped, name=t_name, defer_schema=True)`, which a prior
   FastMCP version accepted. FastMCP 2.x's `add_tool(tool: Tool | Callable)`
   no longer takes a `name` kwarg, and `Tool.from_function` rejects
   `**kwargs` wrappers. Caught only at V2 because the only `boot()`
   test (`test_cold_boot_under_budget`) ran with an empty cwd, so the
   broken code path never executed.

## Open follow-ups (v0.2 backlog)

These are concrete items each known to have at least one downstream
consequence on the current code. Track as issues; not blockers for
shipping v0.1.

1. ~~**Bootstrap path for hand-rolled rows.**~~ **Closed before merge** —
   `pipeline.boot()` now walks `workflow/<row>/phases/*.md` for non-meta
   rows and upserts the corresponding `Phase` nodes (commit `f8bf5dd`).
   V7 reaches `status="completed"` on a fresh ontology with no manual
   seeding.

2. **`research_complete` gate is a placeholder.** Returns `ok=True`
   unconditionally. Real check depends on the spec 08-v1 driver
   REGISTRY plus spec 09 cross-row dispatch. Until then, the phase-02
   prose in `workflow/jules/phases/02-synthesize.md` overstates current
   behavior.

3. ~~**Centralise the error-code catalogue.**~~ **Closed before merge**
   (commit `b676f48`) — eleven codes live in
   `context/_shared/error_codes.py`. All producer call sites
   (`agentic/_harness/{cell_loader,fastmcp_boot}.py`,
   `workflow/_runner/pipeline.py`) import from there. A regression test
   (`tests/context/test_error_codes.py`) rejects any future inline
   `"code": "<UPPER_SNAKE>"` literal.

4. **Raw-SQLite payload tolerance is technical debt.** `_phase_node`
   and `hydrate` in `workflow/_runner/pipeline.py` accept both
   GraphQLite's `{"properties": …}` and the raw-SQLite fallback's
   `{"payload": …}` shape. Spec 08-v1 deletes the fallback; that work
   will also let us drop the two pre-existing `tests/context/test_hooks.py`
   failures.

5. ~~**`context._STORE` singleton is not thread-safe.**~~ **Closed before
   merge** (commit `b676f48`) — `get_store()` docstring now names the
   upgrade path (`threading.Lock` around the lazy init if worker threads
   ever wrap tools).

6. ~~**`_walk_phase` body-before-handler ordering.**~~ **Not a follow-up
   after all** — the implementation already carries an inline comment
   ("Body presence determines the entry_verb (frontmatter override) so
   we read it before resolving the handler") explaining the deliberate
   spec deviation. Documented in place; no further action needed.

7. ~~**Bulk-CLI's `jules_create` lookup is broken.**~~ **Closed before
   merge** — `jules_mcp.server` re-exports `jules_create`,
   `jules_status_all`, `jules_approve_awaiting`, `jules_quota`, and the
   other lifecycle helpers, so the CLI's `from jules_mcp import server
   as mod; mod.jules_*(...)` pattern works without touching the four
   heredocs. Verified by `fanout`, `dashboard`, `approve-awaiting`, and
   `quota` smoke runs.

## What v0.1 means for downstream work

With V2–V11 green:

- **Spec 09 (cross-row dispatch)** is now unblocked. Phases can pull in
  other rows' tools via `mcp__call_tool`; the four-verb contract is
  the integration seam.
- **Spec 08-v1 driver REGISTRY** can land any time — the
  `artefact-node.schema.json` already declares the `artifact_driver` +
  `driver_pointer` slots; current behaviour is fs-by-default.
- **The jules row itself** is intentionally minimal (one tool + one
  skill + two phases + one placeholder gate). It exists primarily as
  a vehicle to prove the three columns interconnect; expanding it to
  a real autonomous coding agent is a separate milestone (v0.3?).

## Numbers

- 7 commits ahead of `Master` at merge time
- ~2200 lines net additions across 35 files
- 52 passing tests, 2 known-failing pre-existing context-hook tests
- ~340 lines `pipeline.py` (target: split `_run_meta_scaffold` into its
  own module before adding row-type-specific logic)
- Cold-boot payload: well under 500 tokens (test threshold)
