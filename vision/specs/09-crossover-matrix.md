---
slug: spec-09-crossover-matrix
type: spec
status: draft
owner: claude
created: 2026-05-20
updated: 2026-05-20
summary: Locks the 3x3 column-crossover matrix for `agency-system`. Names a single dispatch mechanism per cell, fixes the envelope that flows, names the verification gate per ADR-0005 and lesson 12, and resolves the five founder TBDs. Three cells are already built (workflow->agentic, workflow->context, context->agentic); the other six get concrete contracts here. All routing remains inside the one MCP server (ADR-0003) and the four-verb contract (spec 06).
affects:
  - vision/specs/09-crossover-matrix.md
depends_on:
  - vision/specs/06-agentic-base.md
  - vision/specs/07-workflow-base-v1.md
  - vision/specs/08-context-base-v1.md
referenced_by: []
---

# Spec 09 — The 3x3 Column-Crossover Matrix

> **STATUS — 2026-05-20**: draft. Locks the dispatch primitive and
> envelope for every (caller, callee) column pair. 3/9 cells are
> already built (workflow->agentic via `pipeline._walk_phase`,
> workflow->context via gate `MATCH` queries, context->agentic via
> the hook-wrapped registry). The remaining 6 cells are new or
> implicit and become contracts here.

## 1. Why

Spec 06 fixed the agentic surface (four verbs, deferred schemas).
Spec 07-v1 fixed the workflow runner (graph walker, gates as nodes).
Spec 08-v1 fixed the context substrate (single Store singleton, driver
REGISTRY, hook chain). Each spec terminates at its own column boundary
and explicitly defers "cross-row / cross-column dispatch" to "planned
spec 09" (`vision/specs/07-workflow-base-v1.md:492-494`,
`vision/specs/06-agentic-base.md:113`).

This spec is that 09. Without it the matrix has nine plausible call
paths between columns and only three with a named mechanism — the rest
are either accidental (skills hand-rolling Cypher), forbidden by ADR
without a stated alternative (manifest-edit watchers), or simply
absent (cross-row phase chaining). Every cell here pins one primitive
so the implementation phase has a single target to build against.

## 2. The matrix

Caller column down the rows; callee column across the top. Each cell
names the single dispatch mechanism this spec sanctions.

| caller \ callee | agentic | workflow | context |
|---|---|---|---|
| **agentic**  | §3.1 `dispatch_skill` re-entry, ToolResult envelope | §3.2 skill returns `tool_result.next_workflow` triple; harness calls `pipeline.start` | §3.3 four-verb `call_tool` on context-row tools (anchor triad: `context_search` / `context_describe` / `context_read`) |
| **workflow** | §3.4 `pipeline._walk_phase` (BUILT) — handler resolution via `cell_loader.discover()` | §3.5 `PRECEDES` edges + `chain_to` field on terminal envelope | §3.6 gate evaluator + `Store.query` Cypher (BUILT) |
| **context**  | §3.7 PostToolUse / PreToolUse hook chain (BUILT) | §3.8 `Watcher` cells emit `mcp__<row>_start` via the four-verb contract | §3.9 schema `$ref` resolution + `DERIVED_FROM` edges in PostToolUse |

Three cells are **built** today; the other six are **new** under this
spec. No cell is "partial" — the new six are not yet wired anywhere
load-bearing.

## 3. Per-cell contracts

Every cell SHALL conform to ADR-0003 (one MCP server), ADR-0005
(`ToolResult` envelope everywhere), and ADR-0009 (per-result <= 4 KB,
overflow archived per spec 117 to `archived_to`). Every cell SHALL
declare a verification gate that distinguishes "the callee replied"
from "the callee did the work" (lesson 12, `state=COMPLETED` is not
done).

### 3.1 agentic -> agentic

- **Caller / callee**: agentic column (skill or tool) -> agentic column.
- **Status**: new.
- **Mechanism**: re-entry through the four-verb contract. A skill that
  needs another row's tool calls `mcp__call_tool(name, args)`; a skill
  that needs another row's skill calls `mcp__dispatch_skill(name, args)`.
  Direct `from agentic.<other_row>.handlers.<x> import handle` is
  **forbidden** — that path bypasses the hook chain wired in
  `agentic/_bootloader.py:60-65`.
- **Envelope**: spec 02 `ToolResult` on the wire. The inner `data` is
  the callee's own per-tool schema; the caller MUST NOT extend the
  envelope beyond the spec-02 shape.
- **Verification gate**: caller asserts `envelope["ok"] is True` AND
  inspects `envelope["data"]` for the callee's contracted success
  marker (e.g. `data.artefact_metadata.sha256` for an artefact
  producer). `ok=True` alone is insufficient.
- **Worked example (jules row)**: `/jules-orchestrate` skill, mid-flow,
  needs to query the cache before dispatching a new session. It
  invokes `mcp__call_tool(name="mcp__jules_query", args={"topic": ...})`
  through the same harness, receives a spec-02 envelope, checks
  `envelope["data"]["hits"]` is a list, then continues. Both calls flow
  through `make_hooked_wrapper` (`agentic/_bootloader.py:12-25`) so
  PreToolUse/PostToolUse fire on both legs.

### 3.2 agentic -> workflow

- **Caller / callee**: agentic skill -> workflow phase.
- **Status**: new.
- **Mechanism**: the skill's handler returns a spec-02 `ToolResult`
  carrying a NEW field `data.next_workflow` of shape
  `{"row": str, "phase_id": str, "inputs": dict}`. The harness inspects
  this field after PostToolUse ingest and calls
  `workflow._runner.pipeline.start(row, phase_id, inputs)`. The
  resulting `PhaseStateEnvelope` is what the caller receives — the
  original `ToolResult` is preserved under `tool_result` on the phase
  envelope per spec 04.
- **Envelope**: outbound is `ToolResult` with `next_workflow`; inbound
  is `PhaseStateEnvelope` (spec 04).
- **Verification gate**: harness rejects `next_workflow` whose `row`
  has no `Phase` node for `phase_id` AND whose
  `[workflow.lazy_link] enabled = false` — exactly the lazy-link
  contract spec 07-v1 §FR3 already enforces. The skill therefore
  cannot launch into a vacuum; failure surfaces as a `failed`
  envelope, not a silent miss.
- **Worked example (jules row)**: `/jules-research` completes its
  retrieval and wants to hand off to the dispatch phase. Its handler
  returns
  `{"ok": True, "data": {"hits": [...], "next_workflow": {"row": "jules", "phase_id": "03", "inputs": {"topic": ...}}}, ...}`.
  The bootloader-wrapped tool sees `next_workflow`, calls
  `pipeline.start("jules", "03", {"topic": ...})`, and the caller
  receives the phase envelope (status `running` or `blocked_on_user`).

### 3.3 agentic -> context

- **Caller / callee**: agentic skill/tool -> context column.
- **Status**: new (the underlying tools exist; the contract that
  skills must route through them does not).
- **Mechanism**: context-row tools (the future
  `context_search` / `context_describe` / `context_read` anchor triad,
  registered as `mcp__context_search` / `_describe` / `_read` per the
  cell loader's `mcp__<row>_<export>` convention,
  `agentic/_harness/name_deriver.py:14-17`) are the **only** sanctioned
  route into the ontology for agentic callers. Direct
  `from context import get_store; store.query(...)` from an `agentic/`
  module is **forbidden** — it skips PreToolUse validation, defeats
  the 4 KB cap (ADR-0009), and bypasses provenance logging.
- **Envelope**: spec 02 `ToolResult`. Bulk results route through
  `archived_to` per ADR-0009 / spec 117.
- **Verification gate**: PreToolUse `validate_envelope_in` runs on
  the inbound args; PostToolUse `ingest` logs the call. The skill
  asserts `envelope["ok"]` AND that the returned ids round-trip
  through a follow-up `context_describe` (the spec 112 anchor-triad
  pattern: search returns ids, describe confirms presence).
- **Worked example (jules row)**: `/jules-recover` needs to find the
  Artefact node for a patch by sha256. It invokes
  `mcp__call_tool(name="mcp__context_search", args={"label": "Artefact", "where": {"sha256": "..."}})`
  rather than reaching into `Store`. The returned ids feed
  `mcp__context_read` to fetch the manifest entry.

### 3.4 workflow -> agentic — BUILT

- **Caller / callee**: workflow phase -> agentic handler.
- **Status**: built (`workflow/_runner/pipeline.py:359-363`
  `_resolve_handler`; `workflow/_runner/pipeline.py:440-447` invocation).
- **Mechanism**: `_walk_phase` resolves
  `mcp__<row>_<entry_verb>` from the cached `CellRegistry` and calls
  it with the phase inputs.
- **Envelope**: handler returns spec 02 `ToolResult`; the walker wraps
  it as a spec 04 `PhaseStateEnvelope`
  (`workflow/_runner/pipeline.py:504-516`).
- **Verification gate**: walker validates `isinstance(tool_result, dict)`
  and an `ok` boolean; non-conforming returns are coerced to
  `HANDLER_BAD_RETURN` failed envelopes
  (`workflow/_runner/pipeline.py:491-498`). Spec 06 §5 envelope
  validation must run on the registry-wrapped tool before the walker
  receives it — this spec strengthens spec 07-v1 §FR3 step 5 to
  REQUIRE that validation, currently elided.
- **Worked example (jules row)**: `pipeline.start("jules", "03", {...})`
  resolves `mcp__jules_dispatch`, invokes the handler, gets back a
  `ToolResult`, wraps as `PhaseStateEnvelope(status="completed")`,
  returns. The jules-row dispatch phase (`workflow/jules/phases/03-dispatch.md`)
  is the production reference.

### 3.5 workflow -> workflow

- **Caller / callee**: workflow phase -> workflow phase (any row).
- **Status**: new.
- **Mechanism**: two complementary primitives:
  1. **Intra-row chaining** uses the existing `PRECEDES` edge in the
     ontology graph. `pipeline.start` MAY traverse
     `(p:Phase {row, phase_id})-[:PRECEDES]->(next:Phase) RETURN next`
     only when the caller passes `chain=True` (new parameter, default
     `False`). The default is opt-out so a single-phase run never
     stampedes.
  2. **Cross-row chaining** uses a new optional field on the inbound
     `PhaseStateEnvelope.tool_result.data.chain_to` of shape
     `{"row": str, "phase_id": str, "inputs": dict, "wait": bool}`.
     The pipeline, after persisting / completing the current phase,
     re-enters `pipeline.start(...)`. With `wait=True` (default) the
     caller blocks on the chained envelope; with `wait=False` the
     chained start is fire-and-forget and the caller's envelope
     returns immediately with `next_dispatch_session_id` recorded.
- **Envelope**: spec 04 `PhaseStateEnvelope` for both legs.
- **Verification gate**: a `chain_to` whose target row has no
  matching `Phase` node fails fast under the same lazy-link policy
  as §3.2. `PRECEDES` traversal requires the next-phase node to
  exist; lazy-create across a `PRECEDES` edge is **never** allowed
  (refuses silently filling in chain links).
- **Worked example (jules row)**: phase 06 (`verify`) finds the
  remote branch missing and chains to phase 07 (`recover`) with
  `chain_to={"row": "jules", "phase_id": "07", "inputs": {"sid": ...}, "wait": True}`.
  The pipeline transitions verify -> recover in one user turn,
  emitting two `PhaseStateEnvelope`s but returning only the
  terminal one to the user.

### 3.6 workflow -> context — BUILT

- **Caller / callee**: gate evaluator -> ontology.
- **Status**: built (`workflow/_runner/gate.py:23-38` invokes a
  caller-supplied `callable` evaluator that issues
  `Store.query(...)` against the singleton). The jules row's
  `workflow/jules/gates/*.py` evaluators are the production
  reference.
- **Mechanism**: gate evaluator imports `context.get_store` and calls
  `store.query(cypher, params)`. The Cypher dialect is whatever
  GraphQLite offers (spec 08-v1 §FR7).
- **Envelope**: evaluator MUST return exactly
  `{"ok": bool, "message": str}` — pinned in
  `workflow/_runner/gate.py:32-35`. The gate runner translates that
  into a blocked / advisory envelope.
- **Verification gate**: the evaluator's return shape is asserted at
  the call site; any other shape fails the gate closed with
  `"evaluator return must be exactly {ok, message}"`. This spec
  promotes that behaviour to a hard requirement on every
  workflow->context query: the result MUST be reduced to a
  pass/fail boolean inside the evaluator, never returned raw to
  the pipeline.
- **Worked example (jules row)**: `session-completed.yaml` gate
  evaluator queries
  `MATCH (s:JulesSession {sid: $sid}) RETURN s.state` and returns
  `{"ok": s.state == "COMPLETED", "message": ...}`. The pipeline
  consumes the boolean; the Store's raw rows never leave the
  evaluator.

### 3.7 context -> agentic — BUILT

- **Caller / callee**: hook chain (PreToolUse / PostToolUse) ->
  agentic tool.
- **Status**: built (`agentic/_bootloader.py:12-25`
  `make_hooked_wrapper` fires PreToolUse before and PostToolUse
  after every registered tool).
- **Mechanism**: the bootloader wraps every registry entry in a
  closure that calls `validate_envelope_in(tool_name, kwargs)` first
  and `ingest(tool_name, envelope)` after. The chain is
  `PreToolUse -> tool -> PostToolUse`.
- **Envelope**: PreToolUse receives `(tool_name, args_dict)` and
  returns `{ok, errors}`; PostToolUse receives
  `(tool_name, envelope_dict)` and returns `None`. Neither shape is
  the spec-02 envelope — they are intentionally minimal.
- **Verification gate**: this spec adds the **right of rejection**
  (TBD-5 below): PreToolUse returning `{ok: False, ...}` SHALL be
  treated by the bootloader as a hard veto — the tool is NOT
  invoked and a failed `ToolResult` carrying the PreToolUse errors
  is returned. The current wrapper at
  `agentic/_bootloader.py:18-21` discards the PreToolUse return,
  which violates lesson 06 ("spec prose over schema") because
  validation runs but has no enforcement. This spec mandates the
  fix.
- **Worked example (jules row)**: when `mcp__jules_dispatch` is
  invoked with a path that ends in `manifest.toml`,
  `validate_envelope_in` runs the manifest-schema check; on
  failure the bootloader wrapper returns the failed envelope and
  never reaches the handler. PostToolUse then ingests the failure
  envelope into `tools_call_log` for provenance.

### 3.8 context -> workflow

- **Caller / callee**: context-column watcher cell -> workflow
  phase.
- **Status**: new.
- **Mechanism**: a context-row cell MAY declare a `[watcher]`
  sub-table in its `manifest.toml`:

  ```toml
  [watcher]
  enabled = true
  poll_seconds = 30
  handler = "watchers.jules_state"   # context.<row>.watchers.jules_state.poll()
  emits = "mcp__jules_start"          # four-verb route, not a direct call
  ```

  At bootloader time the cell loader registers each watcher as an
  async task. The watcher's `poll()` returns either `None` (no
  emission) or a `{"row", "phase_id", "inputs"}` triple, identical to
  the agentic->workflow `next_workflow` field. The bootloader then
  invokes the workflow start through the **four-verb contract**
  (i.e., `mcp__call_tool(name=emits, args=triple)`), NOT a direct
  `pipeline.start`. This preserves the hook chain (PreToolUse,
  PostToolUse) on every watcher-emitted phase start, satisfying
  ADR-0003 and the spec-06 single-routing surface.
- **Envelope**: outbound emission is the same shape as §3.2's
  `next_workflow`; the returned `PhaseStateEnvelope` is logged but
  not surfaced to the user (the user did not invoke the watcher).
- **Verification gate**: each watcher emission MUST be deduplicated
  on `(row, phase_id, dedupe_key)` where `dedupe_key` is a watcher-
  supplied string (e.g. the Jules session id). The dedupe set lives
  as a `WatcherEmission` node in the ontology; double-emits are
  refused with a logged warning. This implements Plan/137
  CompositeWatcher's terminal-state-once semantics inside the
  matrix.
- **Worked example (jules row)**: `context/jules/watchers/state.py`
  polls the GitHub API for branches matching open Jules session
  ids. When a new branch appears for `sid=abc`, `poll()` returns
  `{"row": "jules", "phase_id": "06", "inputs": {"sid": "abc"}, "dedupe_key": "abc"}`.
  The bootloader emits via `mcp__call_tool("mcp__jules_start", {...})`.
  The verify phase runs once and never re-runs for the same `sid`
  even if the branch re-appears.

### 3.9 context -> context

- **Caller / callee**: context column -> context column. Two
  sub-mechanisms; both are intra-column composition, not runtime
  dispatch.
- **Status**: new (formalisation of an existing pattern).
- **Mechanism**:
  1. **Schema `$ref` composition**. A row's
     `context/<row>/schemas/*.schema.json` MAY reference shared
     schemas via JSON Schema `$ref` to
     `context/_shared/schemas/<name>.schema.json`. PreToolUse
     resolution walks `$ref`s in the same process; cross-row
     `$ref`s (`context/<other-row>/schemas/*`) are **forbidden**
     (every row is its own ontology slice; cross-row constraints
     belong in `_shared/`).
  2. **`DERIVED_FROM` edges** between Artefact nodes (already
     emitted by `context/_hooks/post_tool_use.py:60-67`). This is
     the runtime side of context->context: artefacts in one row
     point at artefacts in another via the same `DERIVED_FROM`
     relationship, with `_ensure_node` placeholder targets keeping
     the graph closed even when the source artefact has not been
     ingested yet.
- **Envelope**: no wire envelope — both legs are intra-process.
  Schema composition is a build-time / hook-time operation; edge
  emission is part of the PostToolUse `ingest` flow.
- **Verification gate**:
  - For `$ref`: `jsonschema.RefResolver` failures surface as
    PreToolUse errors and (per §3.7) reject the call.
  - For `DERIVED_FROM`: PostToolUse `_ensure_node`
    (`context/_hooks/post_tool_use.py:91-105`) already guarantees
    edge closure; this spec adds a periodic "dangling
    `ExternalRef` audit" gate (advisory, not blocking) that flags
    `ExternalRef` nodes older than 7 days that were never
    backfilled to their real label.
- **Worked example (jules row)**:
  `context/jules/schemas/session.schema.json` uses
  `"$ref": "../../_shared/schemas/artefact-node.schema.json#/definitions/sha256"`
  for the session-output hash field. At ingest time, a Jules
  session artefact's `derived_from: ["music/Artefact/<sha>"]` emits
  an edge from the jules-row artefact into the music-row artefact;
  the music artefact's placeholder is overwritten in-place when it
  later ingests through its own channel.

## 4. Resolving founder TBDs

### TBD-1: error routing between columns (does an agentic exception block PostToolUse?)

**Decision**: No. PostToolUse SHALL fire on every tool invocation,
including ones whose handler raised. The bootloader wrapper
catches handler exceptions and synthesises a failed envelope
(`workflow/_runner/pipeline.py:483-489` already does this for the
workflow walker; the agentic wrapper at
`agentic/_bootloader.py:17-21` SHALL adopt the same pattern). The
ingest log is the system's provenance record; suppressing it on
exception would violate lesson 12 (silent-fail recovery requires
an audit trail).

**Rationale**: provenance > propagation. The hook chain order
(`PreToolUse -> tool -> PostToolUse`) is invariant per Plan/000
§3.2; an exception is a tool outcome, not a hook-skipping event.

### TBD-2: per-row vs central registry for cross-column dispatch

**Decision**: central. The single `CellRegistry` built by
`agentic/_harness/cell_loader.discover()` is the canonical lookup
for every cell — workflow's `_resolve_handler`
(`workflow/_runner/pipeline.py:359-363`) already uses it, and
watchers (§3.8) MUST use the four-verb contract that reaches it
too. Per-row registries would re-introduce the "many MCP servers"
trap ADR-0003 closed.

**Rationale**: one MCP, one registry. Boot ordering is
deterministic: `agentic._bootloader.boot()` is the only entry
point; `CellRegistry` is built once; watchers and the pipeline
both late-import it.

### TBD-3: who owns `context-mode-sync` (hook vs service vs explicit tool)

**Decision**: hook. The PostToolUse `ingest` flow is the single
point where artefact metadata becomes graph state. Context-mode
manifest sync (the Plan/111 / Plan/112 surface) SHALL be a
PostToolUse extension that runs after artefact ingest and updates
`~/.agency-system/cache/manifest.json` in-place. Making it a
separate service would double-source the truth; making it an
explicit tool would force every producer to remember to call it.

**Rationale**: one write path. Spec 08-v1 §FR4 already establishes
PostToolUse as the artefact landing site; manifest sync is
downstream of that, not parallel.

### TBD-4: whether skills' chained-call results must also wrap in ToolResult

**Decision**: yes, always. Every cross-column boundary in §3
returns spec 02 `ToolResult` or spec 04 `PhaseStateEnvelope` (which
carries `tool_result` internally). Intra-column composition (a
skill's helper calling its own private function) is exempt — but
the moment a result crosses a column line, it wears the envelope.
Lesson 14 (unbounded results across boundaries) is the reason: the
envelope is the only shape with `archived_to` and warning slots.

**Rationale**: the envelope is the contract; without it, nothing
enforces ADR-0009's 4 KB cap.

### TBD-5: whether hooks may reject tool results, not just transform them

**Decision**: yes, on PreToolUse only. PreToolUse returning
`{ok: False, errors: [...]}` SHALL veto the call; the bootloader
wrapper SHALL synthesise a `ENVELOPE_INVALID` (per spec 06 §5)
failed envelope and skip handler invocation. PostToolUse SHALL
NOT have rejection authority — by the time it runs, the side
effect has occurred; rejecting it would force the caller to
implement compensating transactions the system has no primitives
for.

**Rationale**: validation is cheap before the call, expensive
after. The current wrapper's silent discard of PreToolUse return
values (`agentic/_bootloader.py:18`) is a lesson-06 violation
(spec prose over schema enforcement) and is closed here.

## 5. Out of scope

- **L1 / L2 / L3 transport equivalence** — spec 06 territory; this
  spec assumes L1 (in-process FastMCP). L3 daemon dispatch follows
  the same four-verb contract by definition.
- **Code Mode rendering of crossover results** — the
  `prefers_codemode` flag on the spec-02 envelope flows through
  unchanged; this spec does not introduce a Code-Mode-specific
  crossover path.
- **Skill `skill_kind` enforcement at crossover time** — VOCABULARY
  §4.2 catalogues kinds but does not gate which kind may call
  which; this spec stays kind-agnostic.
- **Hot reload of cells, schemas, or watchers** — cold-restart
  only, consistent with spec 06 / 07-v1 / 08-v1.
- **Multi-process or multi-tenant graphs** — spec 08-v1 §Out of
  scope still governs.
- **`Plan/_research` corpus ingestion** as a context->context
  source — separate spec.

## 6. Acceptance criteria

```gherkin
Scenario: 3.1 agentic->agentic re-entry routes through the hook chain
  Given a skill /jules-orchestrate invokes mcp__call_tool("mcp__jules_query", {...})
  When the inner call returns
  Then validate_envelope_in fired on the inner call's args
  And ingest fired on the inner call's envelope
  And the outer skill received a spec-02 ToolResult

Scenario: 3.2 agentic->workflow next_workflow respects lazy-link
  Given a skill returns data.next_workflow = {"row": "jules", "phase_id": "99", ...}
  And no Phase node phase/jules/99 exists
  And workflow/jules/manifest.toml has [workflow.lazy_link] enabled = false
  When the harness inspects next_workflow
  Then pipeline.start returns a failed envelope with "not in graph" in the message
  And the skill's caller observes the failed envelope, not a Python exception

Scenario: 3.3 agentic->context refuses direct Store access from agentic modules
  Given an agentic handler imports from context._store.sqlite at module load
  When the test_no_direct_store_imports lint runs
  Then it fails listing the offending module
  And the fix-hint names mcp__context_search / _describe / _read

Scenario: 3.4 workflow->agentic walker rejects malformed handler returns
  Given mcp__jules_dispatch returns the string "ok"
  When pipeline.start("jules", "03", {}) runs
  Then the envelope.status == "failed"
  And tool_result.data.error.code == "HANDLER_BAD_RETURN"

Scenario: 3.5 workflow->workflow cross-row chain refuses missing target
  Given a handler returns tool_result.data.chain_to = {"row": "ghost", "phase_id": "01", "inputs": {}}
  And no row "ghost" exists
  When the pipeline processes chain_to
  Then the returned envelope.status == "failed"
  And the original phase's envelope is preserved under tool_result.data.original

Scenario: 3.5 workflow->workflow PRECEDES traversal requires chain=True
  Given pipeline.start("jules", "03", {}, chain=False) is invoked
  And phase/jules/03-[:PRECEDES]->phase/jules/04 exists
  When phase 03 completes
  Then phase 04 is NOT invoked
  And the returned envelope.phase_id == "03"

Scenario: 3.6 workflow->context evaluator return shape is enforced
  Given a gate evaluator returns {"ok": True, "message": "x", "extra": "y"}
  When evaluate_gate runs
  Then (ok, message, _) == (False, "evaluator return must be exactly {ok, message}", {})

Scenario: 3.7 context->agentic PreToolUse veto blocks the handler
  Given validate_envelope_in returns {"ok": False, "errors": ["bad arg"]}
  When the bootloader-wrapped tool is invoked
  Then the handler function is NOT called
  And the returned envelope has data.error.code == "ENVELOPE_INVALID"
  And the returned envelope.data.error.message contains "bad arg"
  And PostToolUse ingest fired on the failure envelope

Scenario: 3.8 context->workflow watcher emits via the four-verb contract
  Given context/jules/watchers/state.py.poll() returns {"row": "jules", "phase_id": "06", "inputs": {"sid": "abc"}, "dedupe_key": "abc"}
  When the bootloader handles the emission
  Then it called mcp__call_tool("mcp__jules_start", {"row": "jules", "phase_id": "06", "inputs": {"sid": "abc"}})
  And NOT pipeline.start directly

Scenario: 3.8 watcher dedupe rejects double-emit
  Given a WatcherEmission node exists for ("jules", "06", "abc")
  When the watcher emits the same triple a second time
  Then no phase invocation occurs
  And a log warning records the dedupe hit

Scenario: 3.9 context->context $ref to another row's schema is rejected
  Given context/jules/schemas/foo.schema.json contains "$ref": "../music/schemas/bar.schema.json"
  When PreToolUse resolves the schema chain
  Then it returns {"ok": False, "errors": [...]} naming "cross-row $ref forbidden"

Scenario: 3.9 dangling ExternalRef audit surfaces as advisory warning
  Given an ExternalRef node was created 8 days ago with no backfill
  When the context->context audit gate runs
  Then it emits an advisory warning (not blocking)
  And the warning lists the node id and age
```

## Dependencies

- **Spec 06** — agentic base layer. §3.1 / §3.7 / §3.8 all route
  through the four-verb contract and `make_hooked_wrapper`.
- **Spec 07-v1** — workflow base. §3.4 / §3.5 / §3.6 extend
  `pipeline._walk_phase` and the `Phase`/`PRECEDES` graph model.
- **Spec 08-v1** — context base. §3.6 / §3.7 / §3.9 rely on the
  `Store` singleton, the driver REGISTRY, and the hook chain.
- **ADR-0003** — single MCP server. Every cell routes through the
  same `agency-system` FastMCP instance.
- **ADR-0005** — shared `ToolResult` envelope; binding for every
  cross-column return value (TBD-4).
- **ADR-0009** — token budget invariants; every per-result MUST
  obey the 4 KB cap, overflow via `archived_to`.
- **VOCABULARY §3 (four-verb contract)** — §3.1 / §3.3 / §3.8 are
  defined relative to the canonical verb names.
- **VOCABULARY §6A (frontmatter canon)** — this spec's frontmatter
  conforms.
