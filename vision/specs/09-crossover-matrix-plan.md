---
slug: spec-09-crossover-matrix-plan
type: plan
status: draft
owner: claude
created: 2026-05-20
updated: 2026-05-20
summary: Implementation plan for spec 09. Groups the six unbuilt crossover cells into three dependency-ordered waves (Wave A — envelope discipline; Wave B — workflow chaining and watchers; Wave C — schema composition and hygiene). Names exact file paths, schema edits, gate YAMLs, and test files per wave. Wave A is small/medium, Wave B is medium/large, Wave C is small. Does NOT include Python or YAML bodies — that's the next phase.
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

> **STATUS — 2026-05-20**: draft. Sequences the six unbuilt cells of
> spec 09 (§3.1, §3.2, §3.3, §3.5, §3.8, §3.9) and the two fixes to
> the built ones (§3.4 envelope validation, §3.7 PreToolUse veto).
> Cells §3.4 and §3.6 are otherwise no-op for this plan — they ship
> the strengthening assertions only.

## 1. Sequencing

Three waves, ordered by dependency. Each wave's exit criterion is the
corresponding spec-09 §6 acceptance scenario.

### Wave A — envelope discipline (foundation)

Builds the contract that every other cell relies on. Without the
PreToolUse veto and the strengthened bootloader wrapper, none of the
later waves can trust their inputs.

- **Cells built**: §3.1 (agentic->agentic re-entry assertion), §3.3
  (agentic->context routing rule + lint), §3.4 (handler-return
  validation strengthening), §3.7 (PreToolUse veto enforcement).
- **Files touched**:
  - `agentic/_bootloader.py:12-25` (`make_hooked_wrapper`) — wrap
    PreToolUse return in a veto check; catch handler exceptions;
    ensure PostToolUse always fires.
  - `agentic/_harness/cell_loader.py:31` (`call_tool`) — round-trip
    every return through the spec-02 envelope validator from spec
    06 §5.
  - `context/_shared/error_codes.py` — add `ENVELOPE_INVALID`,
    `PRETOOLUSE_VETO`, ensure `HANDLER_BAD_RETURN` is present.
  - `tests/agentic/test_no_direct_store_imports.py` (new) — import-
    graph lint that fails when an `agentic/<row>/**.py` module
    imports from `context._store`, `context._drivers`, or
    `context._hooks` directly.
- **ADRs / lessons honored**: ADR-0003 (single MCP), ADR-0005
  (envelope), lesson 06 (schema over prose — PreToolUse return is now
  load-bearing), lesson 12 (silent-fail recovery — exceptions still
  produce envelopes).
- **Exit criteria** (from spec 09 §6):
  - Scenario "3.7 context->agentic PreToolUse veto blocks the handler".
  - Scenario "3.4 workflow->agentic walker rejects malformed handler
    returns".
  - Scenario "3.3 agentic->context refuses direct Store access from
    agentic modules".
  - Scenario "3.1 agentic->agentic re-entry routes through the hook
    chain".

### Wave B — workflow chaining and watchers

Builds the runtime cross-row dispatch primitives. Depends on Wave A
because every chain leg and watcher emission is itself a hook-wrapped
call.

- **Cells built**: §3.2 (agentic->workflow via `next_workflow`), §3.5
  (workflow->workflow `PRECEDES` traversal + `chain_to`), §3.8
  (context->workflow watcher cells).
- **Files touched**:
  - `agentic/_bootloader.py` — after PostToolUse ingest, inspect
    `envelope.data.next_workflow`; if present, call `mcp__call_tool`
    against `mcp__<row>_start` (NOT a direct `pipeline.start`,
    preserving §3.8's rule).
  - `workflow/_runner/pipeline.py:231` (`start` signature) — add
    `chain: bool = False`; after a `completed` envelope, traverse
    `PRECEDES` and re-enter when `chain` is true.
  - `workflow/_runner/pipeline.py:414` (`_walk_phase` tail) —
    after the `_walk_phase` return, inspect
    `tool_result.data.chain_to`; if present, recurse through
    `pipeline.start` with the chained inputs; propagate the
    resulting envelope.
  - `agentic/_harness/cell_loader.py` — new code path: read
    `[watcher]` sub-table from any column's `manifest.toml`; for each
    enabled watcher register a periodic task that calls
    `mcp__call_tool(emits, payload)`.
  - `context/_shared/schemas/context-cell.schema.json` — add optional
    `[watcher]` sub-table definition (boolean `enabled`, integer
    `poll_seconds`, string `handler`, string `emits`).
  - `context/_shared/schemas/tool_result.schema.json` — add optional
    `data.next_workflow` triple and optional `data.chain_to` triple
    (both with `row` / `phase_id` / `inputs`; `chain_to` adds
    `wait: bool` default true).
  - `context/_shared/schemas/watcher-emission.schema.json` (new) —
    payload for the `WatcherEmission` node used for dedupe (§3.8).
  - `workflow/jules/gates/watcher-dedupe.yaml` (new, jules-row
    reference impl) — gate that the watcher emitter uses to refuse
    duplicate `(row, phase_id, dedupe_key)` triples.
- **ADRs / lessons honored**: ADR-0003 (every chain leg routes
  through the single MCP), ADR-0009 (chained envelopes still obey
  the 4 KB cap; the chain leg's envelope is the one returned, the
  intermediate stays under provenance only), lesson 12 (watcher
  dedupe = independent verification of "terminal state observed
  once"), Plan/137 (CompositeWatcher semantics).
- **Exit criteria**:
  - Scenario "3.2 agentic->workflow next_workflow respects
    lazy-link".
  - Scenario "3.5 workflow->workflow cross-row chain refuses missing
    target".
  - Scenario "3.5 workflow->workflow PRECEDES traversal requires
    chain=True".
  - Scenario "3.8 context->workflow watcher emits via the four-verb
    contract".
  - Scenario "3.8 watcher dedupe rejects double-emit".

### Wave C — schema composition and hygiene

Closes the matrix. Depends on Wave B only for the watcher-emission
schema's `ExternalRef` audit hook; otherwise independent.

- **Cells built**: §3.9 (context->context schema `$ref` rules +
  `DERIVED_FROM` audit), §3.6 (assertion strengthening only — no
  runtime change).
- **Files touched**:
  - `context/_hooks/pre_tool_use.py:14` (`_validate_manifest`) —
    add `$ref` walker that rejects cross-row `$ref` targets
    (paths matching `../<other-row>/schemas/`).
  - `context/_hooks/post_tool_use.py:91` (`_ensure_node`) — add a
    `created_at_epoch` field to placeholder `ExternalRef` nodes so
    the audit gate can age them.
  - `workflow/_runner/gate.py:8` (`evaluate_gate`) — no code change;
    add a test that pins the `{ok, message}` exact-shape contract
    (already enforced; this is regression armour).
  - `workflow/meta/gates/dangling-externalref.yaml` (new) — advisory
    gate that fires the audit query and emits warnings.
  - `context/_shared/schemas/artefact-node.schema.json` — add
    optional `created_at_epoch` to the ExternalRef placeholder shape
    (placeholders share the schema today).
- **ADRs / lessons honored**: ADR-0007 (context defers via manifest
  + anchor triad — cross-row `$ref` would shatter the per-row
  ontology slice), lesson 06 (schema enforcement, not prose), lesson
  14 (advisory audits do not block but always surface).
- **Exit criteria**:
  - Scenario "3.9 context->context $ref to another row's schema is
    rejected".
  - Scenario "3.9 dangling ExternalRef audit surfaces as advisory
    warning".
  - Scenario "3.6 workflow->context evaluator return shape is
    enforced" (regression-pinned only).

## 2. Per-wave deliverables

### Wave A deliverables

**Code (edit):**
- `agentic/_bootloader.py` — `make_hooked_wrapper` rewrite per §3.7.
- `agentic/_harness/cell_loader.py` — envelope-validation wrap on
  `CellRegistry.call_tool`.
- `context/_shared/error_codes.py` — three new codes.

**Schemas:** none new. Spec-02 envelope schema gets ONE optional
field clarification (the `error.code` enum gains
`PRETOOLUSE_VETO`).

**Gate YAMLs:** none.

**Tests (new):**
- `tests/agentic/test_pretooluse_veto.py` — asserts a failing
  `validate_envelope_in` short-circuits the handler.
- `tests/agentic/test_handler_exception_still_logs.py` — asserts
  PostToolUse ingest fires on a handler that raises.
- `tests/agentic/test_call_tool_validates_return.py` — asserts a
  non-envelope return is wrapped to `ENVELOPE_INVALID`.
- `tests/agentic/test_no_direct_store_imports.py` — import-graph
  lint per Wave A §1.
- `tests/agentic/test_agentic_to_agentic_reentry.py` — asserts an
  inner `mcp__call_tool` fires both hooks.

### Wave B deliverables

**Code (edit):**
- `agentic/_bootloader.py` — `next_workflow` interception post-ingest.
- `agentic/_harness/cell_loader.py` — `[watcher]` table reader,
  periodic-task registration.
- `workflow/_runner/pipeline.py` — `chain` parameter on `start`;
  `chain_to` handling in `_walk_phase`; PRECEDES traversal.

**Schemas (edit/new):**
- `context/_shared/schemas/tool_result.schema.json` — add
  `data.next_workflow` and `data.chain_to`.
- `context/_shared/schemas/context-cell.schema.json` — add
  `[watcher]` sub-table.
- `context/_shared/schemas/watcher-emission.schema.json` — new.

**Gate YAMLs (new):**
- `workflow/jules/gates/watcher-dedupe.yaml` — reference impl;
  evaluator `callable` -> `workflow.jules.gates.watcher_dedupe.check`.

**Tests (new):**
- `tests/agentic/test_next_workflow_dispatch.py` — asserts the
  bootloader inspects `next_workflow` and calls `mcp__<row>_start`.
- `tests/agentic/test_next_workflow_lazy_link.py` — asserts a
  missing phase + lazy_link=false produces a failed envelope.
- `tests/workflow/test_chain_to.py` — asserts cross-row chaining
  with `wait=True` returns the chained envelope.
- `tests/workflow/test_chain_to_missing_row.py` — asserts an
  unknown target row fails.
- `tests/workflow/test_precedes_traversal.py` — asserts default
  `chain=False` does NOT traverse PRECEDES; `chain=True` does.
- `tests/agentic/test_watcher_registration.py` — asserts a
  manifest with `[watcher] enabled = true` registers the task.
- `tests/agentic/test_watcher_dedupe.py` — asserts a second
  emission of the same `(row, phase_id, dedupe_key)` is refused.
- `tests/agentic/test_watcher_uses_four_verb.py` — asserts the
  watcher calls `mcp__call_tool`, NOT `pipeline.start` directly
  (introspect via a monkeypatch on `mcp__call_tool`).

### Wave C deliverables

**Code (edit):**
- `context/_hooks/pre_tool_use.py` — cross-row `$ref` reject path
  on schema validation.
- `context/_hooks/post_tool_use.py` — `created_at_epoch` on
  ExternalRef placeholders.

**Schemas (edit):**
- `context/_shared/schemas/artefact-node.schema.json` — optional
  `created_at_epoch` on the placeholder shape.

**Gate YAMLs (new):**
- `workflow/meta/gates/dangling-externalref.yaml` — advisory; queries
  `MATCH (n:ExternalRef) WHERE n.created_at_epoch < $cutoff RETURN n`.

**Tests (new):**
- `tests/context/test_cross_row_ref_rejected.py` — asserts a
  `$ref` to `../<other-row>/schemas/*` returns
  `{"ok": False, "errors": [...]}`.
- `tests/context/test_intra_row_ref_allowed.py` — asserts a `$ref`
  to `../../_shared/schemas/*` resolves cleanly.
- `tests/workflow/test_dangling_externalref_advisory.py` — asserts
  the audit gate emits a warning, NOT a block, on a 7-day-old
  ExternalRef.
- `tests/workflow/test_gate_evaluator_shape_regression.py` —
  re-asserts the `{ok, message}` exact-shape contract.

## 3. Test plan

Minimum three tests per cell. The test files named in §2 cover the
counts below; the assertions per test are listed inline.

| Cell | Test files | Total assertions |
|---|---|---|
| §3.1 | `test_agentic_to_agentic_reentry.py` (3) | 3 |
| §3.2 | `test_next_workflow_dispatch.py` (2), `test_next_workflow_lazy_link.py` (2) | 4 |
| §3.3 | `test_no_direct_store_imports.py` (2), `test_call_tool_validates_return.py` (1) | 3 |
| §3.4 | `test_call_tool_validates_return.py` (2), plus existing `tests/workflow/test_pipeline.py` HANDLER_BAD_RETURN coverage | 3 |
| §3.5 | `test_chain_to.py` (1), `test_chain_to_missing_row.py` (1), `test_precedes_traversal.py` (2) | 4 |
| §3.6 | `test_gate_evaluator_shape_regression.py` (3) | 3 |
| §3.7 | `test_pretooluse_veto.py` (2), `test_handler_exception_still_logs.py` (1) | 3 |
| §3.8 | `test_watcher_registration.py` (1), `test_watcher_dedupe.py` (1), `test_watcher_uses_four_verb.py` (1) | 3 |
| §3.9 | `test_cross_row_ref_rejected.py` (1), `test_intra_row_ref_allowed.py` (1), `test_dangling_externalref_advisory.py` (1) | 3 |

Per-test assertion summary (one line each):

- `test_agentic_to_agentic_reentry::test_inner_call_fires_pretooluse`
- `test_agentic_to_agentic_reentry::test_inner_call_fires_posttooluse`
- `test_agentic_to_agentic_reentry::test_outer_skill_receives_spec02`
- `test_next_workflow_dispatch::test_skill_with_next_workflow_triggers_start`
- `test_next_workflow_dispatch::test_returned_envelope_is_phase_state`
- `test_next_workflow_lazy_link::test_missing_phase_with_lazy_false_fails`
- `test_next_workflow_lazy_link::test_missing_phase_with_lazy_true_creates`
- `test_no_direct_store_imports::test_no_agentic_module_imports_store`
- `test_no_direct_store_imports::test_lint_error_message_names_alternative`
- `test_call_tool_validates_return::test_non_envelope_wraps_to_envelope_invalid`
- `test_call_tool_validates_return::test_handler_bad_return_propagates`
- `test_chain_to::test_chain_to_returns_chained_envelope`
- `test_chain_to_missing_row::test_missing_row_fails_fast`
- `test_precedes_traversal::test_chain_false_does_not_traverse`
- `test_precedes_traversal::test_chain_true_traverses_one_hop`
- `test_gate_evaluator_shape_regression::test_extra_keys_rejected`
- `test_gate_evaluator_shape_regression::test_missing_keys_rejected`
- `test_gate_evaluator_shape_regression::test_correct_shape_accepted`
- `test_pretooluse_veto::test_veto_blocks_handler_invocation`
- `test_pretooluse_veto::test_veto_returns_envelope_invalid_envelope`
- `test_handler_exception_still_logs::test_exception_produces_envelope_and_ingest`
- `test_watcher_registration::test_enabled_watcher_registers`
- `test_watcher_dedupe::test_second_emit_refused`
- `test_watcher_uses_four_verb::test_emit_calls_mcp_call_tool`
- `test_cross_row_ref_rejected::test_other_row_ref_returns_error`
- `test_intra_row_ref_allowed::test_shared_ref_resolves`
- `test_dangling_externalref_advisory::test_old_node_emits_warning`

## 4. Risk register

| # | Risk | Mitigation |
|---|---|---|
| 1 | **Boot ordering** — watchers register before the four-verb tools, calling into a half-built registry. | Wave B watcher registration runs in `boot()` AFTER `register_four_verb_contract(mcp, registry)`; add `tests/agentic/test_watcher_boot_order.py` asserting the order. |
| 2 | **Schema cycle** — `tool_result.schema.json` adds `next_workflow` / `chain_to`; if a chain-leg envelope also carries `chain_to`, validation can loop on `$ref`. | Both fields are typed as flat objects, not as `$ref` back to `tool_result`. Validator depth-limited by JSON Schema's natural non-recursion. |
| 3 | **Watcher runaway** — a watcher whose `poll()` raises every iteration burns API calls / locks the registry. | `cell_loader` wraps each watcher's `poll()` in a try/except with exponential backoff; after 5 consecutive failures the watcher disables itself and logs once. |
| 4 | **PRECEDES cycle** — a misconfigured graph (`A->B->A`) makes `chain=True` infinite-loop. | Spec 09 §3.5 PRECEDES traversal is single-hop only; a separate spec adds multi-hop. Wave B test `test_precedes_traversal::test_chain_true_traverses_one_hop` pins single-hop. |
| 5 | **Provenance log explosion** — every watcher poll + every chain leg writes a `tools_call_log` row; the table grows fast. | Out of scope per spec 08-v1 (no TTL sweeper for `tools_call_log`); document the deferred concern in Wave B's PR description so future operators see it. |

## 5. Estimate

Rough cell-count of work per wave. Cells are "person-day-equivalent
units of focused work", not commits.

| Wave | Cells | Size | Notes |
|---|---|---|---|
| A | §3.1, §3.3, §3.4, §3.7 | **small/medium** (~3-4 cells) | The PreToolUse veto + the bootloader wrapper rewrite is most of the work; the lint and the assertion tests are light. |
| B | §3.2, §3.5, §3.8 | **medium/large** (~6-8 cells) | Three new dispatch primitives, schema additions, watcher infrastructure, dedupe node. Largest wave; ~half the total effort lives here. |
| C | §3.6, §3.9 | **small** (~2 cells) | Cross-row `$ref` reject is one walker addition; the advisory audit is one YAML + one query. §3.6 is regression armour only. |

Total: ~12 cells of work; Wave B is the critical-path long pole.

## Dependencies

- **Spec 09** (the design) — every wave's exit criterion cites a
  §6 scenario from the design.
- **Spec 06** §5 — envelope validation primitive that Wave A wraps.
- **Spec 07-v1** §FR3 — `_walk_phase` is the integration point for
  Wave B's `chain_to`.
- **Spec 08-v1** §FR1, §FR3, §FR4 — Store singleton, REGISTRY, and
  the hook chain that Wave A strengthens and Wave C extends.
- **ADR-0003, ADR-0005, ADR-0007, ADR-0009** — every wave honors
  these; the per-wave ADR list above is the per-wave subset.
