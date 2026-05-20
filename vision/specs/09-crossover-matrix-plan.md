---
slug: spec-09-crossover-matrix-plan
type: plan
status: draft
owner: claude
created: 2026-05-20
updated: 2026-05-20
summary: Implementation plan for spec 09 (revision 2). Groups the six unbuilt crossover cells into three dependency-ordered waves (Wave A — envelope discipline; Wave B — workflow dispatch / chaining / watchers; Wave C — schema composition and hygiene). Names exact file paths, schema edits, gate YAMLs, and test files per wave. Reflects the r2 design changes — `workflow_dispatch` triple replaces split `next_workflow`/`chain_to`; `previous_continuation_id` replaces inline `original`; `data.artefact_ref` replaces phantom `archived_to`; new schemas under `vision/specs/schemas/_shared/` and `vision/specs/schemas/context/nodes/` are listed.
affects:
  - vision/specs/09-crossover-matrix-plan.md
depends_on:
  - vision/specs/09-crossover-matrix.md
  - vision/specs/06-agentic-base.md
  - vision/specs/07-workflow-base-v1.md
  - vision/specs/08-context-base-v1.md
referenced_by: []
---

# Spec 09 (Plan) — Crossover Matrix Implementation

> **STATUS — 2026-05-20**: draft (revision 2). Sequences the six
> unbuilt cells of spec 09 (§3.1, §3.2, §3.3, §3.5, §3.8, §3.9) and
> the two fixes to the built ones (§3.4 envelope validation, §3.7
> PreToolUse veto). Reconciled with the r2 spec: the
> `workflow_dispatch` triple replaces panel r1's
> `next_workflow`/`chain_to`; the composition-cap rule pulls in a
> `previous_continuation_id` pointer rather than inlining prior
> envelopes; all new schemas are closed with an explicit
> `extensions` slot.

## 1. Sequencing

Three waves, ordered by dependency. Each wave's exit criterion is the
corresponding spec-09 §8 acceptance scenario.

### Wave A — envelope discipline (foundation)

Builds the contract that every other cell relies on. Without the
PreToolUse veto, the strengthened bootloader wrapper, and the
envelope-validation pre-walker step, none of the later waves can
trust their inputs.

- **Cells built**: §3.1 (agentic->agentic re-entry assertion), §3.3
  (agentic->context routing rule + lint), §3.4 (handler-return
  validation strengthening), §3.7 (PreToolUse veto enforcement).
- **Files touched**:
  - `agentic/_bootloader.py` (function `make_hooked_wrapper` — anchor
    by symbol, not line range) — wrap PreToolUse return in a veto
    check; catch handler exceptions and synthesise
    `HANDLER_EXCEPTION`; ensure PostToolUse always fires.
  - `agentic/_harness/cell_loader.py` (function `call_tool`) — round-
    trip every return through the spec-02 envelope validator from
    spec 06 §5.
  - `context/_shared/error_codes.py` — add `ENVELOPE_INVALID`,
    `PRETOOLUSE_VETO`, `HANDLER_EXCEPTION`, `HANDLER_BAD_RETURN`,
    `WORKFLOW_DISPATCH_CYCLE`, `CROSS_ROW_REF`, `PHASE_NOT_IN_GRAPH`.
    Single canonical list; per-cell tests assert membership.
  - `tests/agentic/test_no_direct_store_imports.py` (new) — import-
    graph lint scoped to `agentic/<row>/**.py`; explicitly EXCLUDES
    `agentic/_harness/**` (closes panel TCA #4).
- **Schemas**: none new. The spec-02 envelope schema is unchanged
  (closed-shape root); the `error.code` enum is documented in
  `context/_shared/error_codes.py` (the canonical source — schema
  per-tool data shapes reference this list).
- **vision/canon honored**: vision/03-architecture.md §3 (one
  engine); vision/agentic/INTERFACE-TO-CONTEXT.md §3.1 (PreToolUse
  validation); vision/specs/02 §Encoding rules (4 KB cap);
  vision/specs/06 §5 (envelope validation).
- **Exit criteria** (from spec 09 §8):
  - "3.7 context->agentic PreToolUse veto blocks the handler".
  - "3.7 handler exception synthesises a failed envelope AND fires ingest".
  - "3.4 workflow->agentic walker rejects malformed handler returns".
  - "3.4 workflow->agentic envelope schema validation runs before the walker receives".
  - "3.3 agentic->context refuses direct Store access from agentic row modules".
  - "3.1 agentic->agentic call_tool re-entry routes through the hook chain".
  - "3.1 agentic->agentic dispatch_skill returns a ToolResult OR PhaseStateEnvelope".

### Wave B — workflow dispatch, chaining, and watchers

Builds the runtime cross-row dispatch primitives. Depends on Wave A
because every dispatch leg and watcher emission is itself a hook-
wrapped call.

- **Cells built**: §3.2 (agentic->workflow via `workflow_dispatch`),
  §3.5 (workflow->workflow `PRECEDES` traversal + same triple for
  inter-row), §3.8 (context->workflow watcher cells).
- **Files touched**:
  - `agentic/_bootloader.py` — after PostToolUse ingest, inspect
    `envelope.data.workflow_dispatch`; if present, increment
    `Session.payload.workflow_dispatch_depth`; if depth ≤ 3, emit
    via `CellRegistry.call_tool("mcp__<row>_start", args)`; else
    return `WORKFLOW_DISPATCH_CYCLE`. Routes through the four-verb
    contract; NEVER calls `pipeline.start` directly.
  - `workflow/_runner/pipeline.py` (function `start`) — add
    `chain: bool = False`; after a `completed` envelope, if
    `chain=True`, look up the `PRECEDES` next-hop and emit a
    `workflow_dispatch` triple through the same bootloader
    interception code path (one hop only per call; cycle guard
    shared with §3.2).
  - `workflow/_runner/pipeline.py` (function `_walk_phase`) — after
    the handler return, inspect `tool_result.data.workflow_dispatch`;
    if the row differs from the current row, persist the current
    envelope as a `Continuation` node, then emit via the bootloader
    path (NOT a direct `pipeline.start` recursion — closes panel
    DSA #3). The chained envelope sets
    `tool_result.data.previous_continuation_id` to the persisted
    node id.
  - `agentic/_harness/cell_loader.py` — new code path: read
    `[watcher]` sub-table from `context/<row>/manifest.toml`; for
    each enabled watcher register a periodic task that calls
    `CellRegistry.call_tool(emits, payload)`. Registration runs
    AFTER `register_four_verb_contract(mcp, registry)` AND
    `_wrap_registry_with_hooks(registry)` — pinned by the boot-
    order test below.
  - `context/_shared/schemas/context-cell.schema.json` — add
    optional closed `watcher` block (`additionalProperties: false`,
    required `enabled`, `poll_seconds`, `handler`, `emits`; optional
    `extensions`).
  - `context/_shared/schemas/tool_result.schema.json` — UNCHANGED.
    `data` remains open; per-tool schemas constrain it. The
    `workflow_dispatch` and `previous_continuation_id` slots are
    documented in §4.2 / §4.7 of the spec and validated by per-tool
    `data` schemas on emitting tools.
- **New schemas (vision/specs/schemas/)**:
  - `vision/specs/schemas/_shared/workflow-dispatch.schema.json`
    (NEW) — closed shape `{row, phase_id, inputs, wait?, extensions?}`;
    `wait` enum restricted to `["true"]` for v0.
  - `vision/specs/schemas/context/nodes/watcher-emission.schema.json`
    (NEW) — closed shape; `dedupe_key.minLength: 1`.
  - `vision/specs/schemas/context/nodes/watcher-health.schema.json`
    (NEW) — closed shape; operator queryable.
  - `vision/specs/schemas/context/nodes/session.schema.json` (EDIT) —
    add optional `workflow_dispatch_depth` integer to payload.
- **New gate YAML**:
  - `workflow/jules/gates/watcher-dedupe.yaml` (new, jules-row
    reference impl) — gate the watcher emitter uses to refuse
    duplicate `(row, phase_id, dedupe_key)` triples.
- **vision/canon honored**: vision/agentic/INTERFACE-TO-WORKFLOW.md
  §3.1 (`execute_pipeline` is the in-process callable behind the
  four-verb route); vision/workflow/INTERFACE-TO-AGENTIC.md §3
  (uniform entry); vision/specs/04 STATUS note (Continuation is a
  graph node); vision/specs/07-v1 §FR1 (lazy-link policy).
- **Exit criteria**:
  - "3.2 agentic->workflow workflow_dispatch respects lazy-link".
  - "3.2 agentic->workflow recursion is capped at depth 3".
  - "3.5 workflow->workflow cross-row chain refuses missing target".
  - "3.5 workflow->workflow chained envelope size stays under 4 KB".
  - "3.5 workflow->workflow PRECEDES traversal requires chain=True".
  - "3.5 chained leg PreToolUse veto surfaces to the caller".
  - "3.8 context->workflow watcher emits via the four-verb contract".
  - "3.8 watcher dedupe rejects double-emit and increments WatcherHealth".
  - "3.8 watcher empty dedupe_key is rejected at PreToolUse".
  - "3.8 watcher registration runs after the four-verb contract".
  - "3.8 watcher disables itself after consecutive failures and surfaces in WatcherHealth".

### Wave C — schema composition and hygiene

Closes the matrix. Depends on Wave B only for the watcher-emission
schema's `ExternalRef` audit hook; otherwise independent.

- **Cells built**: §3.9 (context->context schema `$ref` rules +
  `DERIVED_FROM` audit), §3.6 (assertion strengthening — promoted
  from regression armour to real test).
- **Files touched**:
  - `context/_hooks/pre_tool_use.py` (function `_validate_manifest`)
    — add `$ref` walker that rejects cross-row `$ref` targets
    (paths matching `../<other-row>/schemas/`). On failure emit
    `CROSS_ROW_REF` (the new error code).
  - `context/_hooks/post_tool_use.py` (function `_ensure_node`) —
    add a `created_at_epoch` field to placeholder `ExternalRef`
    nodes so the audit gate can age them.
  - `workflow/_runner/gate.py` — NO code change to the evaluator
    shape check (already exact); add a test that pins the contract
    AND covers a new path: "evaluator returns raw query rows ⇒ gate
    fails closed" (closes panel TCA #3 — promote to real test).
  - `workflow/meta/gates/dangling-externalref.yaml` (new) — advisory
    gate that fires the audit query
    `MATCH (n:ExternalRef) WHERE n.created_at_epoch < $cutoff RETURN n LIMIT 50`
    and emits a warning prefixed with "first 50 of N total" when
    truncation occurs (closes panel TBS #4).
  - `context/_shared/schemas/artefact-node.schema.json` — add
    optional `created_at_epoch` integer to the ExternalRef
    placeholder shape (placeholders share the schema today).
- **vision/canon honored**: vision/context/Vision.md (per-row
  ontology slice); vision/specs/schemas/context/edges/derived-from.schema.json
  (closed shape, existing).
- **Exit criteria**:
  - "3.9 context->context $ref to another row's schema is rejected".
  - "3.9 context->context $ref to _shared resolves cleanly" (uses the
    corrected `#/properties/sha256` fragment).
  - "3.9 dangling ExternalRef audit surfaces as advisory warning".
  - "3.6 workflow->context evaluator return shape is enforced (not regression armour)".
  - "3.6 dangling ExternalRef audit respects LIMIT 50".

## 2. Per-wave deliverables

### Wave A deliverables

**Code (edit):**
- `agentic/_bootloader.py` — `make_hooked_wrapper` rewrite per §3.7.
- `agentic/_harness/cell_loader.py` — envelope-validation wrap on
  `CellRegistry.call_tool`.
- `context/_shared/error_codes.py` — six canonical codes (see §1).

**Schemas:** none new. spec-02 envelope schema unchanged.

**Gate YAMLs:** none.

**Tests (new):**
- `tests/agentic/test_pretooluse_veto.py` — veto blocks handler;
  envelope shape; PostToolUse still fires.
- `tests/agentic/test_handler_exception_still_logs.py` — handler
  raises; envelope has `HANDLER_EXCEPTION`; ingest fires.
- `tests/agentic/test_call_tool_validates_return.py` — non-envelope
  return wraps to `ENVELOPE_INVALID`.
- `tests/agentic/test_no_direct_store_imports.py` — import-graph lint
  scoped to `agentic/<row>/**.py`; excludes `agentic/_harness/**`.
- `tests/agentic/test_agentic_to_agentic_reentry.py` — inner
  `mcp__call_tool` fires both hooks AND inner `mcp__dispatch_skill`
  returns the correct envelope variant.

### Wave B deliverables

**Code (edit):**
- `agentic/_bootloader.py` — `workflow_dispatch` interception post-
  ingest; cycle-guard via `Session.payload.workflow_dispatch_depth`.
- `agentic/_harness/cell_loader.py` — `[watcher]` table reader,
  periodic-task registration with boot-order assertion.
- `workflow/_runner/pipeline.py` — `chain` parameter on `start`;
  `workflow_dispatch` handling in `_walk_phase` (persist
  `Continuation` first, then emit via bootloader path); PRECEDES
  traversal one-hop only.

**Schemas (edit/new):**
- `vision/specs/schemas/_shared/workflow-dispatch.schema.json` (NEW).
- `vision/specs/schemas/context/nodes/watcher-emission.schema.json` (NEW).
- `vision/specs/schemas/context/nodes/watcher-health.schema.json` (NEW).
- `vision/specs/schemas/context/nodes/session.schema.json` (EDIT) —
  add `workflow_dispatch_depth`.
- `context/_shared/schemas/context-cell.schema.json` (EDIT) — add
  closed `watcher` block.
- `context/_shared/schemas/tool_result.schema.json` — UNCHANGED
  (closes panel SL #3 by NOT opening the root; per-tool data
  schemas constrain `workflow_dispatch` / `previous_continuation_id`).

**Gate YAMLs (new):**
- `workflow/jules/gates/watcher-dedupe.yaml` — reference impl;
  evaluator callable -> `workflow.jules.gates.watcher_dedupe.check`.

**Tests (new):**
- `tests/agentic/test_workflow_dispatch_dispatch.py` — bootloader
  inspects `workflow_dispatch` and emits via four-verb.
- `tests/agentic/test_workflow_dispatch_lazy_link.py` — missing
  phase + lazy_link=false produces a `PHASE_NOT_IN_GRAPH` envelope.
- `tests/agentic/test_workflow_dispatch_cycle_guard.py` — chain
  A→B→A→B→ refused at depth 4 with `WORKFLOW_DISPATCH_CYCLE`.
- `tests/workflow/test_chain_size_cap.py` — chain of two 3.5 KB
  envelopes returns ≤ 4 KB envelope with
  `previous_continuation_id`.
- `tests/workflow/test_chain_missing_row.py` — unknown target row
  fails fast.
- `tests/workflow/test_chain_veto_propagation.py` — chained leg's
  PreToolUse veto surfaces to caller (closes panel TCA #6).
- `tests/workflow/test_precedes_traversal.py` — `chain=False` does
  not traverse; `chain=True` does one hop.
- `tests/agentic/test_watcher_registration.py` — `[watcher]
  enabled = true` registers the task.
- `tests/agentic/test_watcher_dedupe.py` — second emit refused;
  `WatcherHealth.dedupe_hit_count` increments.
- `tests/agentic/test_watcher_uses_four_verb.py` — watcher calls
  `CellRegistry.call_tool`, NOT `pipeline.start` directly.
- `tests/agentic/test_watcher_boot_order.py` — fault-injection: flip
  the boot order, assert clear failure (closes panel TCA #1).
- `tests/agentic/test_watcher_health_disable.py` — five raises ⇒
  `last_status="disabled"` queryable.
- `tests/agentic/test_watcher_empty_dedupe_key.py` — `dedupe_key=""`
  rejected at PreToolUse via the schema's `minLength: 1`.

### Wave C deliverables

**Code (edit):**
- `context/_hooks/pre_tool_use.py` — cross-row `$ref` reject path
  on schema validation; emit `CROSS_ROW_REF`.
- `context/_hooks/post_tool_use.py` — `created_at_epoch` on
  ExternalRef placeholders.

**Schemas (edit):**
- `context/_shared/schemas/artefact-node.schema.json` — optional
  `created_at_epoch` on the placeholder shape.

**Gate YAMLs (new):**
- `workflow/meta/gates/dangling-externalref.yaml` — advisory; query
  carries `LIMIT 50`; warning prefixed with "first 50 of N total".

**Tests (new):**
- `tests/context/test_cross_row_ref_rejected.py` — `$ref` to
  `../<other-row>/schemas/*` returns
  `{"ok": False, "errors": [...]}` with `CROSS_ROW_REF`.
- `tests/context/test_intra_row_ref_allowed.py` — `$ref` to
  `../../_shared/schemas/artefact-node.schema.json#/properties/sha256`
  resolves cleanly (uses the CORRECTED fragment; closes panel
  BLOCKER 5).
- `tests/workflow/test_dangling_externalref_advisory.py` — audit
  emits warning (not block) on a 7-day-old ExternalRef AND respects
  `LIMIT 50`.
- `tests/workflow/test_gate_evaluator_shape_strict.py` — evaluator
  that returns raw query rows fails the gate closed (promoted from
  regression armour; closes panel TCA #3).

## 3. Test plan

Minimum three tests per cell. The test files named in §2 cover the
counts below.

| Cell | Test files | Total assertions |
|---|---|---|
| §3.1 | `test_agentic_to_agentic_reentry.py` (3) | 3 |
| §3.2 | `test_workflow_dispatch_dispatch.py` (2), `test_workflow_dispatch_lazy_link.py` (2), `test_workflow_dispatch_cycle_guard.py` (1) | 5 |
| §3.3 | `test_no_direct_store_imports.py` (2), `test_call_tool_validates_return.py` (1) | 3 |
| §3.4 | `test_call_tool_validates_return.py` (2), `test_pipeline.py` HANDLER_BAD_RETURN (1) | 3 |
| §3.5 | `test_chain_size_cap.py` (1), `test_chain_missing_row.py` (1), `test_chain_veto_propagation.py` (1), `test_precedes_traversal.py` (2) | 5 |
| §3.6 | `test_gate_evaluator_shape_strict.py` (3) | 3 |
| §3.7 | `test_pretooluse_veto.py` (3), `test_handler_exception_still_logs.py` (1) | 4 |
| §3.8 | `test_watcher_registration.py` (1), `test_watcher_dedupe.py` (2), `test_watcher_uses_four_verb.py` (1), `test_watcher_boot_order.py` (1), `test_watcher_health_disable.py` (1), `test_watcher_empty_dedupe_key.py` (1) | 7 |
| §3.9 | `test_cross_row_ref_rejected.py` (1), `test_intra_row_ref_allowed.py` (1), `test_dangling_externalref_advisory.py` (2) | 4 |

## 4. Risk register

| # | Risk | Mitigation |
|---|---|---|
| 1 | **Boot ordering** — watchers register before the four-verb tools, calling into a half-built registry. | Wave B watcher registration runs in `boot()` AFTER `register_four_verb_contract(mcp, registry)` AND `_wrap_registry_with_hooks(registry)`; `tests/agentic/test_watcher_boot_order.py` does fault-injection to assert clear failure on the wrong order (closes panel TCA #1). |
| 2 | **`workflow_dispatch` recursion (unbounded)** — handler A returns dispatch→B, B returns dispatch→A. | Per-session counter on `Session.payload.workflow_dispatch_depth`; hard cap at 3; over-cap returns `WORKFLOW_DISPATCH_CYCLE` (closes panel BLOCKER 3 / DSA #2). Counter shared with §3.5 PRECEDES chain; spec 09 §3.5 explicitly states one-hop-only per call. |
| 3 | **Watcher runaway** — a watcher whose `poll()` raises every iteration burns API calls. | `cell_loader` wraps each `poll()` in try/except with exponential backoff; after 5 consecutive failures the watcher self-disables AND a `WatcherHealth` node is upserted with `last_status="disabled"` so operators can find it via `mcp__context_query` (closes panel ORR #1 / #6). |
| 4 | **Composition oversizing** — chained PhaseStateEnvelopes inline prior payloads. | §3.5 persists the prior leg as a `Continuation` node; chained envelope carries `previous_continuation_id` only. `test_chain_size_cap.py` asserts the ≤ 4 KB invariant on the wire (closes panel BLOCKER 1 / TBS #1). |
| 5 | **PRECEDES cycle** — `A->B->A` graph with `chain=True`. | `pipeline.start` PRECEDES traversal is single-hop per call AND shares the `workflow_dispatch_depth` cap. `test_precedes_traversal.py` pins single-hop; a misconfigured graph cannot exceed depth 3. |
| 6 | **Provenance log growth** — every watcher emission writes a `tools_call_log` row. | Out of scope per spec 08-v1; the deferral is acknowledged in spec 09 §6 and surfaced in the Wave B PR description so future operators see the budget concern (closes panel TBS #3). |
| 7 | **`wait=False` re-introduced prematurely** — fire-and-forget chaining without an envelope-read surface would re-create the L12 trap. | v0 schema (`workflow-dispatch.schema.json`) restricts `wait` enum to `["true"]`; widening blocked behind landing `mcp__meta_envelope_read` (closes panel BLOCKER 4 / DSA #1). |
| 8 | **`validate_envelope_in` is a near no-op today** — TBD-5 veto applies to a check that always passes. | Wave C ships the cross-row `$ref` reject path, making PreToolUse load-bearing for context-row writes. Wave A's `tests/agentic/test_pretooluse_veto.py` uses a synthetic validator that returns ok=False to exercise the veto contract independent of today's near-no-op behaviour (closes panel ORR #3 / LLA #1). |

## 5. Estimate

Rough cell-count of work per wave. Cells are "person-day-equivalent
units of focused work", not commits.

| Wave | Cells | Size | Notes |
|---|---|---|---|
| A | §3.1, §3.3, §3.4, §3.7 | **small/medium** (~3-4 cells) | PreToolUse veto + bootloader wrapper rewrite is most of the work; lint and assertion tests are light. |
| B | §3.2, §3.5, §3.8 | **medium/large** (~7-9 cells) | Three new dispatch primitives, three new schemas, watcher infrastructure (registration + dedupe + health), cycle-guard counter on Session node. Largest wave; ~half the total effort lives here. The size went up vs r1 because §3.5 now persists Continuation pointers AND the schema set widened to three closed schemas with an `extensions` slot. |
| C | §3.6, §3.9 | **small** (~2-3 cells) | Cross-row `$ref` reject is one walker addition; the advisory audit is one YAML + one query with `LIMIT 50`. §3.6 promotes the regression test to a real strict-evaluator test (slightly more than r1's regression-only). |

Total: ~12-14 cells of work; Wave B is the critical-path long pole.

## Dependencies

- **Spec 09 (revision 2)** — every wave's exit criterion cites a §8
  scenario from the design.
- **Spec 06 §5** — envelope validation primitive that Wave A wraps.
- **Spec 07-v1 §FR1** — `_walk_phase` is the integration point for
  Wave B's `workflow_dispatch` interception.
- **Spec 08-v1 §FR1, §FR3, §FR4** — Store, REGISTRY, and hook chain
  that Wave A strengthens and Wave C extends.
- **vision/specs/schemas/** — new schemas under `_shared/` and
  `context/nodes/` (listed in Wave B); existing schemas referenced
  throughout (Wave A four-verb schemas; Wave C derived-from edge).
- **vision/03-architecture.md §3, §5.1** — one engine, GraphQLite
  substrate; binding for every crossing's mechanism.
- **vision/agentic/INTERFACE-TO-WORKFLOW.md §3.1**;
  **vision/workflow/INTERFACE-TO-AGENTIC.md §3** — `execute_pipeline`
  reconciliation pinned in spec 09 §9.
- **vision/context/INTERFACE-TO-AGENTIC.md §3.1, §3.4** — PreToolUse
  validation contract, `query_graph` signature; Wave A strengthens
  the first, Wave A names the second as the underlying call behind
  `mcp__context_query`.
