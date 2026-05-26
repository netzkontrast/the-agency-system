---
slug: spec-09-crossover-matrix-review
type: review
status: ready
owner: claude
created: 2026-05-20
updated: 2026-05-20
summary: Five-expert panel review of spec 09 + plan. Surfaces 9 BLOCKER, 17 IMPORTANT, 7 NIT defects; recommends revise-first before status:draft leaves.
reviews:
  - vision/specs/09-crossover-matrix.md
  - vision/specs/09-crossover-matrix-plan.md
---

# Spec 09 review — five-expert panel

## Panel

- **§1 — Distributed-Systems Architect (DSA).** Lens: cycles, idempotency,
  retry semantics, re-entrancy, ordering hazards across cells that can fire
  simultaneously (watcher + user, chain + dedupe, exception during chain).
- **§2 — Schema Linguist (SL).** Lens: L06. Envelope shape per cell,
  closed JSON Schemas (`additionalProperties: false`), `$ref` targets,
  field-name consistency with already-shipped schemas.
- **§3 — Token-Budget Skeptic (TBS).** Lens: L14 + ADR-0009. Per-result
  ≤ 4 KB, `tools/list` < 4 KB, boot < 500 tokens. Where can a cross-column
  composition exceed it? Where is the truncation contract?
- **§4 — Test-Coverage Auditor (TCA).** Lens: for each cell, is there a
  falsifiable assertion? Do the proposed tests fail loudly on the
  worst-case (phase never publishes emission, hook vetoes after call,
  watcher emits before its row's manifest is loaded)?
- **§5 — Operational Risk Reviewer (ORR).** Lens: boot ordering, registry
  timing, hot-reload non-policy, observability, recovery. Cold-boot, row
  added mid-session, watcher polling a half-built registry, provenance
  log growth.
- **§6 — Sixth voice: Lessons-Learned Archivist (LLA).** Added because
  the spec cites L05/L06/L12/L14 by number without auditing whether the
  proposed mechanism actually satisfies each lesson. The other voices
  cover technical defects; the LLA confirms the lessons-cited match the
  lessons-applied.

---

## §1 Distributed-Systems Architect

### Findings

1. **BLOCKER — `chain_to` with `wait=False` has no failure path back to
   the original caller.** `09-crossover-matrix.md:188-190` defines
   `wait=False` as "fire-and-forget and the caller's envelope returns
   immediately with `next_dispatch_session_id` recorded." Nothing in §3.5
   or §6 says how a *failed* chained phase surfaces — the caller has
   already returned a `completed` envelope. This is exactly the L12 trap
   (`COMPLETED` ≠ done) reproduced in the chain primitive the spec is
   adding.

2. **BLOCKER — re-entry cycle through `next_workflow` is unbounded.**
   `09-crossover-matrix.md:98-104` lets a skill's handler return
   `data.next_workflow`. The bootloader inspects this **after PostToolUse
   ingest** and re-enters `pipeline.start`. The handler returned by that
   start is itself a `ToolResult`. If *that* handler also returns
   `next_workflow`, the bootloader fires again. No depth limit, no cycle
   detection. A misconfigured skill chain like `A.next_workflow → B,
   B.next_workflow → A` will run until the stack blows. The plan's risk
   register only addresses `PRECEDES` cycles (`09-crossover-matrix-plan.md:306`),
   not the more dangerous `next_workflow → start → handler → next_workflow`
   loop.

3. **IMPORTANT — `chain_to` is processed where, exactly?** Spec
   `09-crossover-matrix.md:182-190` puts `chain_to` inside the inbound
   `PhaseStateEnvelope.tool_result.data.chain_to`, but the plan
   (`09-crossover-matrix-plan.md:84-89`) edits
   `pipeline.py:414` (`_walk_phase` tail) to recurse — i.e., **before**
   the envelope leaves the pipeline. So a handler can chain forever
   without the bootloader-level hook ever firing on the chain leg.
   Compare to §3.8 watchers, which the spec explicitly forces through
   `mcp__call_tool` to preserve the hook chain
   (`09-crossover-matrix.md:286-288`). The chain primitive bypasses
   precisely that contract — internally inconsistent.

4. **IMPORTANT — PreToolUse veto on a chained leg can desynchronise
   provenance.** The bootloader catches an exception (TBD-1) and
   synthesises a failed envelope, but TBD-5 says PreToolUse veto means
   "the tool is NOT invoked." If the *chained* leg vetoes, the original
   phase has already completed and ingested. The graph now has an
   envelope claiming completion for phase A and a `WatcherEmission` for
   phase B that never ran. There is no compensating record.

5. **IMPORTANT — watcher dedupe key is watcher-supplied.**
   `09-crossover-matrix.md:294-298` makes the watcher author responsible
   for the `dedupe_key`. A buggy watcher that returns `dedupe_key=""`
   will collide on every emission, refusing them all silently. The
   "logged warning" surface means a watcher can suppress itself
   indefinitely after a single typo. No floor / validation on the key.

6. **NIT — "single-hop only" claim in risk register is contradicted by
   the spec body.** Risk-register entry 4
   (`09-crossover-matrix-plan.md:306`) asserts "Spec 09 §3.5 PRECEDES
   traversal is single-hop only" — but spec
   `09-crossover-matrix.md:178-183` only says the walker *may* traverse
   `PRECEDES` when `chain=True`. Nothing in the body limits hops. If
   `chain=True` is sticky across the recursion, A→B→C→A is achievable
   in three hops with no cycle guard.

### Hypothetical break

Cell §3.5, `chain_to` with `wait=False`. A skill kicks off
`jules/verify` (phase 06) which fires `chain_to={"row":"jules","phase_id":"07","wait":false}`.
Phase 06 returns `completed` to the caller; phase 07 starts, gates fail,
writes a `failed` PhaseStateEnvelope into provenance, no propagation.
User sees green; recovery never ran. **L12 in the primitive built to
fix L12.**

### Suggested edits

- `09-crossover-matrix.md:188-190` → drop `wait=False` from v0; require
  `wait=True` for v0. State: "Fire-and-forget chaining is post-v0;
  current v0 only supports `wait=True` so the chain leg's failure can
  propagate." If `wait=False` is non-negotiable, name the polling
  primitive callers use to recover the chained session.
- `09-crossover-matrix.md:98-104` → add to §3.2: "A handler that
  returned via `next_workflow` SHALL NOT itself appear in the
  re-entered phase's handler chain. The bootloader maintains a
  per-session `next_workflow_depth` and refuses re-entry when depth > 3
  with `NEXT_WORKFLOW_CYCLE`." (Three is a defensible default; whatever
  the number, name it and code-anchor it.)
- `09-crossover-matrix-plan.md:84-89` → either change the plan to put
  `chain_to` interception at the bootloader (matching §3.8 watcher
  semantics) or amend §3.5 to acknowledge that intra-pipeline chaining
  bypasses Pre/PostToolUse and add a `pipeline-internal` provenance row
  with the same key shape.
- Add a §3.5 acceptance scenario: "chained leg failure surfaces to the
  caller even when `wait=False`" (or remove `wait=False`).

---

## §2 Schema Linguist

### Findings

1. **BLOCKER — `archived_to` is invoked four times but the field does
   not exist in `tool_result.schema.json`.** `09-crossover-matrix.md:63,
   136, 405, 539` all refer to `archived_to` as the ADR-0009 overflow
   slot. The actual schema at
   `context/_shared/schemas/tool_result.schema.json:1-36` has no
   `archived_to` property; spec 02 names the sidecar pointer
   `data.artefact_ref` (`vision/specs/02-tool-result-envelope.md:76`).
   Either spec 09 is referencing an unwritten Plan/117 surface as if it
   were canonical, or it is renaming the field. Either way, every
   acceptance scenario about overflow is unfalsifiable until the slot
   has a name in the schema.

2. **BLOCKER — §3.9 worked example uses a `$ref` path that cannot
   resolve.** `09-crossover-matrix.md:342-345` shows
   `"$ref": "../../_shared/schemas/artefact-node.schema.json#/definitions/sha256"`.
   The actual schema at
   `context/_shared/schemas/artefact-node.schema.json:1-30` has no
   `definitions` block — `sha256` is a top-level property at line 26.
   The correct fragment would be `#/properties/sha256`. As written, the
   example fails at `jsonschema.RefResolver` and any test built on this
   example will fail for the wrong reason.

3. **BLOCKER — `data.next_workflow` / `data.chain_to` cannot be
   enforced by the existing schema.** The plan
   (`09-crossover-matrix-plan.md:96-99`) adds these fields to
   `tool_result.schema.json`, but spec 02's `data` is `{"type":
   "object"}` with no `additionalProperties: false`
   (`context/_shared/schemas/tool_result.schema.json:17-20`). Adding
   *optional* properties under `data` does not constrain the shape —
   any handler can put garbage under those names and validation
   passes. L06 ("schema beats prose") is violated by the very edit the
   plan calls out as the L06 fix.

4. **IMPORTANT — closed-schema requirement absent from new schemas.**
   `09-crossover-matrix-plan.md:101-102` adds
   `watcher-emission.schema.json` without specifying
   `additionalProperties: false`. Same for the proposed `[watcher]`
   sub-table in `context-cell.schema.json` (line 95). Default-open
   schemas were exactly the L06 failure mode.

5. **IMPORTANT — `next_workflow` shape collides with `chain_to`.**
   `09-crossover-matrix.md:99` and `:185` both define
   `{row, phase_id, inputs}` triples — but `chain_to` adds `wait: bool`
   and §3.8 watcher emissions add `dedupe_key`. The plan treats them as
   four schemas (`next_workflow`, `chain_to`, `[watcher]`, watcher
   payload) with no `$ref` shared between them. Schema duplication
   guarantees drift.

6. **IMPORTANT — gate evaluator return shape claim is one character
   wide.** Spec `09-crossover-matrix.md:215-218` says the evaluator
   returns "exactly `{"ok": bool, "message": str}`" — pinned in
   `workflow/_runner/gate.py:32-35`. The actual line is
   `gate.py:32-33`, and the enforcement is `set(result.keys()) != {"ok",
   "message"}` — that does check exact match, but the spec's anchored
   line-range is off by 2-3. Repeated throughout (see §3.4 anchor
   `pipeline.py:359-363` is exact, `:440-447` is exact, but
   `:483-489` (exception path) is actually `:483-489` only for the
   second except clause; `:491-498` (HANDLER_BAD_RETURN) is correct).
   Anchor drift is the L06 hazard the spec promised to avoid.

7. **NIT — `name_deriver.py:14-17` cited as the `mcp__<row>_<export>`
   source.** `09-crossover-matrix.md:130-132` anchors the convention to
   `name_deriver.py:14-17`, but those lines are
   `_assert_no_row_prefix`. The actual derivation lives at
   `mcp_tool_name` lines 24-27. Cite the function, not its helper.

8. **NIT — `pipeline.py:504-516` cited for envelope wrapping.**
   §3.4 anchor; actual range is `:507-516` (the dict literal is at
   507). Off-by-three.

### Hypothetical break

Cell §3.9, schema composition. A jules-row schema adds the
canonical-looking `"$ref":"../../_shared/schemas/artefact-node.schema.json#/definitions/sha256"`
from the spec's worked example. PreToolUse calls `RefResolver`,
resolution fails (path is wrong), `validate_envelope_in` returns
`{"ok": False, ...}`. Under TBD-5, the veto blocks the call. Every
manifest write involving that schema is rejected. The skill author
fixes by removing `$ref` and inlining the constraint — silently
killing the cross-schema invariant the spec was supposed to lock.

### Suggested edits

- `09-crossover-matrix.md:63` → replace "overflow archived per spec 117
  to `archived_to`" with "overflow flagged via `data.artefact_ref`
  (spec 02 §Encoding rules); Plan/117's `archived_to` rename is
  deferred until that plan promotes to a spec." Repeat at :136, :405,
  :539.
- `09-crossover-matrix.md:343` → fix the `$ref` fragment:
  `#/properties/sha256` (NOT `#/definitions/sha256`). Or replace the
  example with a definition that actually exists.
- `09-crossover-matrix-plan.md:96-99` → require the schema edit to
  introduce a shared definition file
  `context/_shared/schemas/workflow-dispatch.schema.json` carrying the
  `{row, phase_id, inputs}` base and `$ref` it from both
  `next_workflow` and `chain_to` so the shape can't drift.
- `09-crossover-matrix-plan.md:101-102` → spell out
  `additionalProperties: false` and the required-keys list on
  `watcher-emission.schema.json` in the plan body, not "TBD in the
  next phase."
- Sweep all `pipeline.py:` and `gate.py:` anchors against the live
  files; bind to function names plus a sentinel comment instead of
  raw line ranges.

---

## §3 Token-Budget Skeptic

### Findings

1. **BLOCKER — chained `PhaseStateEnvelope` carries the original under
   `tool_result.data.original` (acceptance scenario
   `09-crossover-matrix.md:480`) with no size cap.** Two phases each
   producing a 3.5 KB envelope chain into a 7 KB combined return. Per
   ADR-0009 every per-result is ≤ 4 KB — this single primitive blows
   the cap by design. No truncation contract is named. L14 verbatim.

2. **BLOCKER — `next_workflow` re-entry returns the chained
   `PhaseStateEnvelope` as the original skill's reply
   (`09-crossover-matrix.md:101-104`).** Spec 04's envelope already
   contains a `tool_result` (the inner spec-02 envelope) plus session
   metadata. A skill that returns `{"ok": True, "data": {"next_workflow":
   ...}}` of 1 KB then receives a `PhaseStateEnvelope` whose
   `tool_result.data` may itself be 3.9 KB → wrapped phase envelope is
   ~5+ KB before warnings. There is no rule that the *original*
   skill's `data` must be stripped before the swap.

3. **IMPORTANT — watcher payload + dedupe write doubles per-poll
   traffic.** Each watcher emission writes a `WatcherEmission` node AND
   invokes `mcp__call_tool` (`09-crossover-matrix.md:286-288`). Both
   pass through PreToolUse / PostToolUse hooks; PostToolUse `ingest`
   writes a `tools_call_log` row. A 30-second polling watcher with no
   new state still costs no log writes, but a busy polling cycle that
   dedupes on every other poll writes ~120 log rows/hour per watcher.
   Risk-register entry 5 (`09-crossover-matrix-plan.md:307`) names this
   "out of scope" — but ADR-0009 is in scope, and the boot/`tools/list`
   budget is not the only invariant; the per-session conversation
   budget is too.

4. **IMPORTANT — `tools_call_log` size on the wire from a query is
   uncapped.** §3.6 promises evaluators reduce graph results to
   `{ok, message}` (`09-crossover-matrix.md:223-225`) — good for gates.
   But the dangling-ExternalRef audit gate
   (`09-crossover-matrix-plan.md:236-238`) returns a Cypher result
   "MATCH (n:ExternalRef) WHERE ... RETURN n" — with no LIMIT clause.
   A long-running install can accumulate thousands of dangling
   ExternalRefs; the advisory warning's `message` field would balloon
   past 4 KB.

5. **NIT — boot-time `[watcher]` registration is added to
   `cell_loader.discover()` without a budget for boot-payload
   additions.** ADR-0009 caps boot < 500 tokens. Adding N watcher
   registrations doesn't directly land in `tools/list` (the four-verb
   contract is unchanged), but each `[watcher]` description loaded at
   boot is a memory cost not currently bounded. Worth a one-line
   "watcher schema bodies do NOT participate in `tools/list`" note.

### Hypothetical break

Cell §3.5, `wait=True` cross-row chain. Phase A produces a 3.8 KB
envelope (within cap). Phase A chains to phase B, which produces a
3.6 KB envelope. The final return is the chained PhaseStateEnvelope
with phase B's tool_result inline AND phase A's preserved at
`tool_result.data.original` (per acceptance scenario at
`09-crossover-matrix.md:480`). Total wire: ~7.4 KB. Caller's MCP
client receives a payload that exceeds the ADR-0009 cap. No truncation
gate fires.

### Suggested edits

- `09-crossover-matrix.md:480` → replace the `original` preservation
  with `original_session_id` (a 36-byte UUID pointer to the persisted
  envelope) and state that the full prior envelope is recoverable via
  `mcp__call_tool("mcp__meta_envelope_read", {session_id})`.
- `09-crossover-matrix.md` add a new §4.6: "Per-cell size cap": every
  cell's return SHALL fit in 4 KB after composition; the §3.2 / §3.5
  wrappers SHALL drop the original `data` payload and replace with
  `previous_session_id` when their compositional return would exceed
  3 KB."
- `09-crossover-matrix-plan.md:237-238` → add `LIMIT 50` to the
  dangling-ExternalRef query and a "first 50 of N total" prefix on the
  warning message.

---

## §4 Test-Coverage Auditor

### Findings

1. **BLOCKER — §3.8 watcher dedupe has no test for the worst case:
   emission BEFORE the row's manifest is loaded.** The plan tests
   `test_watcher_dedupe::test_second_emit_refused`
   (`09-crossover-matrix-plan.md:293`) but never the boot-race where
   `cell_loader` has registered the watcher (Wave B,
   `09-crossover-matrix-plan.md:90-92`) but the target row's
   `mcp__<row>_start` is not yet in the registry. The watcher will fail
   at `mcp__call_tool("mcp__jules_start", ...)` with "tool not found"
   and there is no falsifiable assertion for that scenario.

2. **BLOCKER — §3.2 acceptance "lazy_link=true creates" test exists
   (`09-crossover-matrix-plan.md:277`) but the spec never authorises
   the bootloader to invoke lazy_link=true from a `next_workflow`
   emission.** Spec §3.2 only says it "rejects" when lazy_link is
   false. So the test name asserts behaviour the spec does not
   define. Either the spec needs to state that `next_workflow` passes
   `lazy_link=manifest_reader.get_lazy_link(row)` to
   `pipeline.start`, or the test is testing fiction.

3. **IMPORTANT — Cell §3.6 "tests" are regression armour only.**
   `09-crossover-matrix-plan.md:155` says §3.6 ships "regression-pinned
   only." `test_gate_evaluator_shape_regression` has three assertions
   already covered by the live gate implementation. There is no test
   for the new claim that "the result MUST be reduced to a pass/fail
   boolean inside the evaluator, never returned raw"
   (`09-crossover-matrix.md:222-225`). That contract is unenforced.

4. **IMPORTANT — `test_no_direct_store_imports` checks `agentic/<row>/**`
   only; the spec's prohibition is broader.** Spec §3.3 forbids "Direct
   `from context import get_store; store.query(...)` from an `agentic/`
   module." The plan's lint scope (`09-crossover-matrix-plan.md:51-53`)
   names `agentic/<row>/**.py` — but the harness itself
   (`agentic/_harness/*.py`) imports from `context` legitimately. The
   test as scoped would either over-match or be defined in a way that
   the lint is trivially bypassed by colocating offending code under
   `agentic/_<something>/`.

5. **IMPORTANT — TBD-1 promised behaviour is not tested.** TBD-1
   (`09-crossover-matrix.md:356-362`) says the agentic wrapper SHALL
   catch handler exceptions and synthesise a failed envelope. Test
   `test_handler_exception_still_logs::test_exception_produces_envelope_and_ingest`
   (`09-crossover-matrix-plan.md:291`) checks that ingest fires — but
   does not assert the envelope shape is the spec-02 ENVELOPE with
   `data.error.code = HANDLER_EXCEPTION` (or whichever new code).
   Halfway falsifiable.

6. **IMPORTANT — `chain_to` test coverage misses the chain-then-veto
   case.** `09-crossover-matrix-plan.md:282-285` covers chain to known
   row, chain to missing row, and PRECEDES traversal. None covers
   "chain target's PreToolUse vetoes the call." Per §3.7 the veto
   produces an ENVELOPE_INVALID — but the caller's original phase has
   already completed; there is no test that the chained-leg veto
   surfaces correctly to the original envelope.

7. **NIT — three-tests-per-cell minimum is partly fictional.**
   §3.4 row in the test plan table
   (`09-crossover-matrix-plan.md:262`) claims "3" assertions but two
   are reused from the §3.3 row and the third is "existing
   tests/workflow/test_pipeline.py coverage." The cell ships zero new
   tests.

### Hypothetical break

Cell §3.8, watcher emits during cold-boot. `cell_loader.discover()`
walks `agentic/`, `workflow/`, `context/` in lexicographic order. The
jules watcher's `manifest.toml` is in `context/jules/manifest.toml`
(C-column), but `mcp__jules_start` is registered from
`workflow/jules/manifest.toml` (W-column). If the watcher's
`poll()` is scheduled before `register_four_verb_contract` returns,
the first emission to `mcp__call_tool("mcp__jules_start", ...)` raises
`ValueError("Tool mcp__jules_start not found.")` from `cell_loader.py:30`.
The plan's
`test_watcher_boot_order` (`09-crossover-matrix-plan.md:303`) asserts
order but not the *failure mode* if order is wrong. Silent in CI.

### Suggested edits

- `09-crossover-matrix-plan.md:303` → expand mitigation: test must
  assert the watcher's first poll() call resolves through the registry
  AFTER `register_four_verb_contract` returns. Add a fault-injection
  test that flips the order and confirms `ValueError` is not raised in
  user-visible logs.
- `09-crossover-matrix.md:222-225` → add an acceptance scenario:
  "Given an evaluator imports `get_store` and returns the raw rows,
  When `evaluate_gate` runs, Then the gate fails closed with `evaluator
  return must be exactly {ok, message}`." Promote §3.6 from regression
  armour to a real test.
- Add to §3.5 acceptance scenarios: "Given chain_to target's
  PreToolUse vetoes; When pipeline processes chain_to; Then the
  returned envelope.status == 'failed' AND the original phase's
  envelope is recoverable by `original_session_id`."

---

## §5 Operational Risk Reviewer

### Findings

1. **BLOCKER — there is no defined behaviour when a watcher manifest
   is added between boot cycles.** Spec 09 §5 declares "cold-restart
   only" (`09-crossover-matrix.md:438-439`). But a watcher registered
   at cold boot is a *running async task*. The plan's risk-register
   entry 3 (`09-crossover-matrix-plan.md:305`) talks about disabling a
   misbehaving watcher after 5 failures, but the disable state is
   in-memory only. After the next cold boot, the same watcher
   re-registers and the same 5-failure dance plays out. No persistent
   "watcher quarantine" state, no operator override.

2. **BLOCKER — watcher emission goes through `mcp__call_tool` (good),
   but the four-verb path implicitly requires a *MCP client* on the
   other end.** The bootloader registers `register_four_verb_contract`
   on a FastMCP server (`agentic/_bootloader.py:55`). Watchers are
   running inside the same process. The spec
   (`09-crossover-matrix.md:286-288`) says "the bootloader emits via
   `mcp__call_tool(...)` " — but the bootloader is the *server*, not a
   client. There is no in-process MCP-client → MCP-server short-circuit
   defined. Either the watcher reaches into `registry.call_tool`
   directly (which the spec forbids "NOT a direct `pipeline.start`"),
   or it needs a stub client this spec hasn't introduced.

3. **IMPORTANT — `validate_envelope_in` today only validates
   manifest-write tools.** `context/_hooks/pre_tool_use.py:68-80`
   passes every non-manifest call through with `{ok: True, errors:
   []}`. TBD-5 promotes PreToolUse to a hard veto. But there are no
   non-trivial PreToolUse checks today — the veto applies to a check
   that almost always returns OK. The result is a *theoretical*
   enforcement: the spec changes the contract surface but ships no new
   enforcement. L06 again ("schema beats prose"): prose says veto,
   schema says permissive.

4. **IMPORTANT — `dispatch_skill` is mentioned in §3.1 but the cell's
   verification gate names only `mcp__call_tool`.**
   `09-crossover-matrix.md:73-77` says skills can call either
   `mcp__call_tool` or `mcp__dispatch_skill`, but the acceptance
   scenario at `:449-453` only tests `mcp__call_tool`. Dispatch_skill
   returns a `ToolResult | PhaseStateEnvelope`
   (`vision/specs/06-agentic-base.md:108`) — the verification-gate
   assertion that "envelope is spec-02 ToolResult" is wrong for that
   path. No coverage for the variant.

5. **IMPORTANT — boot ordering risk extends past watchers to
   `next_workflow` interception.** Plan
   `09-crossover-matrix-plan.md:78-82` says the bootloader, "after
   PostToolUse ingest, inspect `envelope.data.next_workflow`; if
   present, call `mcp__call_tool` against `mcp__<row>_start`." But
   `register_four_verb_contract` is what registers `mcp__call_tool`
   itself. The interception code path must run AFTER that registration
   too — and the plan doesn't anchor it. No test for "next_workflow
   intercept before mcp__call_tool registers."

6. **IMPORTANT — observability surface for watcher emissions is "log
   warning" only (`09-crossover-matrix.md:295-298`).** Dedupe hits go
   to logs. The PostToolUse ingest writes `tools_call_log` rows. There
   is no metric counter, no `WatcherEmission` count in a status query,
   no way for an operator to ask "how many watchers fired in the last
   hour." Operationally invisible.

7. **NIT — §3.8 worked example cites `context/jules/watchers/state.py`
   but no such file exists.** `context/jules/` today has `manifest.toml`,
   `schemas/`, `templates/`. The watcher module is forward-looking.
   That's fine for a draft spec, but the example would be sharper if
   it called out the path is "to be created in Wave B" rather than
   reading as a live reference.

### Hypothetical break

Cell §3.8, mid-session watcher addition. User adds a new row
`youtube` between sessions. Cold boot picks up `context/youtube/manifest.toml`
with `[watcher] enabled = true`. But `workflow/youtube/manifest.toml`
has no `mcp__youtube_start` tool. The watcher's first emission calls
`mcp__call_tool("mcp__youtube_start", ...)` which fails with "tool not
found" from `cell_loader.py:30`. Per spec the watcher's `poll()` is
wrapped in try/except with exponential backoff (risk-register entry
3). After 5 failures the watcher self-disables — silently. There is
no `WatcherDisabled` node, no operator surface, no test asserting the
disabled state is reachable from a status query. The watcher row is
dark and undiagnosable until cold boot.

### Suggested edits

- `09-crossover-matrix.md:438-439` → add a sentence: "Hot-reload of
  cells is out of scope; the runtime SHALL however persist watcher
  health state (disabled, last_error, consecutive_failures) as a
  `WatcherHealth` node so operators can `mcp__context_search` for
  unhealthy watchers without a cold boot."
- `09-crossover-matrix.md:286-288` → name the in-process client surface
  explicitly: "The bootloader resolves `mcp__call_tool` via the
  `CellRegistry.call_tool` callable (i.e., the same dispatch that
  FastMCP's wire path uses), NOT a side-channel into `registry.tools[
  ...]`." Or: "Watchers SHALL invoke `mcp__call_tool` via the FastMCP
  in-process client (`mcp._local_provider`); the same path used by the
  cold-boot payload emitter (`agentic/_bootloader.py:78`)."
- `09-crossover-matrix.md:283-286` → add a precondition to the
  `[watcher]` sub-table: "Watcher registration SHALL be deferred until
  the bootloader has finished `register_four_verb_contract(mcp,
  registry)` AND `_wrap_registry_with_hooks(registry)`. Tests SHALL
  fail loudly when this order is violated."
- §3.1 acceptance — split into `mcp__call_tool` and
  `mcp__dispatch_skill` scenarios.

---

## §6 Lessons-Learned Archivist

### Findings

1. **IMPORTANT — L06 ("schema beats spec prose") is cited but
   inverted in the implementation.** Spec §3.7 / TBD-5
   (`09-crossover-matrix.md:412-424`) promises the PreToolUse veto
   fixes a "lesson-06 violation." But — see SL #3 and ORR #3 — the
   field that would enforce it (`data.next_workflow`,
   `data.chain_to`) is unconstrained by schema, and the validator
   `validate_envelope_in` itself is a near no-op today
   (`context/_hooks/pre_tool_use.py:68-80`). The spec calls L06 but
   does not write the schema teeth that would honor L06.

2. **IMPORTANT — L12 is cited as the reason for the verification
   gate, but the verification gate for §3.2 is the same lazy-link
   policy that already exists.** `09-crossover-matrix.md:107-112` says
   the verification gate is "exactly the lazy-link contract spec 07-v1
   §FR3 already enforces." That's a true statement but it does not
   add any new verification — L12 motivated *additional* verification
   ("verify the branch on remote"), not "reuse the existing graph
   lookup." The cell's L12 invocation is decorative.

3. **IMPORTANT — L14 ("unbounded results across boundaries") is
   contradicted by the chained envelope design (see TBS #1 and #2).**
   The spec cites L14 at TBD-4 (`09-crossover-matrix.md:404-408`)
   while §3.2 and §3.5 explicitly compose envelopes whose combined
   size can blow ADR-0009. The lesson is named; the design walks past
   it.

4. **NIT — L05 ("independent review subagent is load-bearing") is
   honored implicitly by the existence of this review.** No spec-side
   defect; mentioned for completeness.

### Hypothetical break

A future developer reading `09-crossover-matrix.md:404-408` (the L14
citation under TBD-4) takes "the envelope is the only shape with
`archived_to` and warning slots" at face value. They build a new
cross-column path that produces a 6 KB envelope and assume the
envelope will handle overflow. The overflow never lands (no
`archived_to` exists), the wire payload trips the ADR-0009 cap, and
the failure mode is silent truncation on the MCP client.

### Suggested edits

- For every "Lesson NN" citation in spec 09, add a one-line "honored
  by:" pointer to the schema field, test name, or acceptance scenario
  that mechanically enforces the lesson. If no mechanical enforcement
  exists, downgrade the citation to "informative" or add the
  enforcement.

---

## §7 Chair synthesis

### Top 5 blockers

1. **Chain composition exceeds 4 KB by design.** §3.5 acceptance
   scenario preserves the original envelope inline
   (`09-crossover-matrix.md:480`); spec 02's 4 KB cap is broken on
   the first non-trivial chain. (TBS #1, LLA #3)
2. **`archived_to` is a phantom field.** Cited four times in spec 09
   (`:63, :136, :405, :539`); does not exist in
   `tool_result.schema.json`. (SL #1)
3. **`next_workflow` re-entry has no cycle guard.** Handler A returns
   `next_workflow: B`, B returns `next_workflow: A`, unbounded
   recursion. Risk register only covers PRECEDES cycles. (DSA #2)
4. **`chain_to` with `wait=False` silently swallows failures.** §3.5
   defines fire-and-forget chaining with no failure propagation —
   the L12 trap reproduced in the primitive built to address L12.
   (DSA #1)
5. **§3.9 worked example uses a `$ref` that does not resolve.**
   `#/definitions/sha256` (`09-crossover-matrix.md:343`) — the
   artefact schema has no `definitions` block. Any test built on the
   example fails for the wrong reason. (SL #2)

### Top 10 important issues

1. `data.next_workflow` / `data.chain_to` added under `data` which is
   schema-open; L06 promise unkept. (SL #3, LLA #1)
2. `chain_to` is processed inside `_walk_phase` — bypassing
   Pre/PostToolUse — while §3.8 watcher emission is required to go
   through the hook chain. Internal contradiction. (DSA #3)
3. Watcher emission's `mcp__call_tool` round-trip from inside the
   server has no defined in-process client primitive; the spec
   implies one without naming it. (ORR #2)
4. PreToolUse veto enforcement (TBD-5) presumes meaningful PreToolUse
   checks; today the validator is a near no-op. The spec changes the
   contract without shipping the enforcement. (ORR #3, LLA #1)
5. Watcher boot ordering only mitigated by a single ordering test;
   no fault-injection test covers the missing-tool failure mode.
   (TCA #1, ORR #5)
6. Watcher dedupe key is watcher-supplied with no minimum-length /
   non-empty validation. A typoed watcher can suppress itself silently.
   (DSA #5)
7. New schemas (`watcher-emission`, `[watcher]` sub-table) not
   required to be closed (`additionalProperties: false`) — same trap
   the rest of the system avoids. (SL #4)
8. Dangling-ExternalRef audit query is unbounded; large installs
   produce a 4 KB+ warning message. (TBS #4)
9. `dispatch_skill` is named in §3.1 but no acceptance scenario
   covers it — only `mcp__call_tool` is tested. (ORR #4)
10. Multiple line anchors in §3.4 / §3.6 / §3.7 are off by 2-3
    lines against the live files. L06 hazard repeated. (SL #6, SL #7,
    SL #8)

### Consensus disagreements

- **`wait=False` cross-row chaining.** DSA #1 wants it dropped from
  v0 entirely (failure-path hazard). TBS #2 is silent. ORR #6 wants
  it kept but with observable health surface. **Chair recommends:**
  drop from v0. The fire-and-forget primitive is the right idea
  *once* there is a status-query surface; today there is not. Re-add
  alongside `mcp__meta_envelope_read` or a `WatcherHealth`-style
  surface. (Status: contested between DSA and ORR — DSA wins
  on L12-rigor.)
- **`additionalProperties: false` on new schemas.** SL #4 demands
  it; TBS #5 wants flexibility for forward-compat. **Chair
  recommends:** closed schemas with explicit `extensions: dict`
  property when forward-compat is required. The L06 cost of an open
  schema exceeds the migration cost of adding an `extensions` slot
  later.

### Greenlights

- The 3x3 matrix framing itself is sound. Naming the dispatch
  mechanism per cell is the right contract granularity; the three
  BUILT cells anchor the other six.
- TBD-1 (PostToolUse fires on exception) is the right call and
  aligns with the existing walker behaviour
  (`workflow/_runner/pipeline.py:483-498`).
- TBD-2 (central registry, not per-row) is the right call and
  follows from ADR-0003 cleanly.
- TBD-3 (PostToolUse owns context-mode sync) avoids a double-source
  hazard.
- The plan's wave ordering (envelope discipline → chaining/watchers
  → schema hygiene) is dependency-correct. Wave A genuinely is the
  foundation; Wave B is the long pole.
- The §3.6 promotion of `{ok, message}` exact-shape from
  permissive to required is the right tightening; the test-coverage
  side just needs to ship beyond regression armour.
- Spec correctly identifies that §3.8 watcher emissions must route
  through the four-verb contract — the right ADR-0003 alignment.
  (Implementation primitive is missing — ORR #2 — but the *rule* is
  right.)

### Verdict

**Revise-first.** The 9 BLOCKER findings (5 surfaced in the Top-5,
4 more carried in the §-level lists) include three that would land
broken implementations in Wave B (chain composition oversizing,
`next_workflow` recursion, watcher in-process client). The spec is
within reach — fixing the phantom `archived_to`, the `$ref`
fragment, the chain composition rule, the cycle guard, and the open
schemas should take less than one focused day. Recommend staying at
`status: draft` until the BLOCKER findings are resolved and the
Top-10 important issues are at least named in the spec body with a
deferral pointer.
