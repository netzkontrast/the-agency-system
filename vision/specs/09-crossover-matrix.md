---
slug: spec-09-crossover-matrix
type: spec
status: draft
owner: claude
created: 2026-05-20
updated: 2026-05-20
summary: Locks the 3x3 column-crossover matrix for `agency-system`. Names a single dispatch mechanism per cell, fixes the envelope that flows (anchored to schemas under `vision/specs/schemas/`), names the verification gate per spec 06 §5 + lesson 12, and resolves the five founder TBDs. Three cells are already built (workflow->agentic, workflow->context, context->agentic); the other six get concrete contracts here. All routing remains inside the one MCP server (`vision/03-architecture.md` §3) and the four-verb contract (spec 06 / `vision/specs/schemas/agentic/four-verb/`).
affects:
  - vision/specs/09-crossover-matrix.md
depends_on:
  - vision/00-charter.md
  - vision/00.1-Overview.md
  - vision/03-architecture.md
  - vision/agentic/INTERFACES.md
  - vision/agentic/INTERFACE-TO-WORKFLOW.md
  - vision/agentic/INTERFACE-TO-CONTEXT.md
  - vision/workflow/INTERFACES.md
  - vision/workflow/INTERFACE-TO-AGENTIC.md
  - vision/workflow/INTERFACE-TO-CONTEXT.md
  - vision/context/INTERFACES.md
  - vision/context/INTERFACE-TO-AGENTIC.md
  - vision/context/INTERFACE-TO-WORKFLOW.md
  - vision/specs/02-tool-result-envelope.md
  - vision/specs/04-phase-state-envelope.md
  - vision/specs/06-agentic-base.md
  - vision/specs/07-workflow-base-v1.md
  - vision/specs/08-context-base-v1.md
  - vision/specs/schemas/agentic/four-verb/call-tool-request.schema.json
  - vision/specs/schemas/agentic/four-verb/call-tool-response.schema.json
  - vision/specs/schemas/agentic/four-verb/dispatch-skill-request.schema.json
  - vision/specs/schemas/agentic/four-verb/dispatch-skill-response.schema.json
  - vision/specs/schemas/agentic/interface-to-workflow.schema.json
  - vision/specs/schemas/agentic/interface-to-context.schema.json
  - vision/specs/schemas/context/interface-to-agentic.schema.json
  - vision/specs/schemas/context/interface-to-workflow.schema.json
  - vision/specs/schemas/context/nodes/phase.schema.json
  - vision/specs/schemas/context/nodes/continuation.schema.json
  - vision/specs/schemas/context/nodes/artefact.schema.json
  - vision/specs/schemas/context/edges/precedes.schema.json
  - vision/specs/schemas/context/edges/derived-from.schema.json
  - vision/specs/schemas/context/edges/dispatched-to.schema.json
  - vision/specs/schemas/context/edges/invoked-tool.schema.json
  - vision/specs/schemas/context/hooks/pretooluse.schema.json
  - vision/specs/schemas/context/hooks/posttooluse.schema.json
referenced_by: []
---

# Spec 09 — The 3x3 Column-Crossover Matrix

> **STATUS — 2026-05-20**: draft (revision 2). Locks the dispatch
> primitive and envelope for every (caller, callee) column pair. 3/9
> cells are already built (workflow->agentic via `pipeline._walk_phase`,
> workflow->context via gate `MATCH` queries, context->agentic via
> the hook-wrapped registry). The remaining 6 cells are new or
> implicit and become contracts here.
>
> **Revision 2 changes vs r1**: re-anchored binding constraints from
> the MVP-era ADRs to the `vision/` canon (charter, per-column
> `INTERFACE-TO-*.md`, schemas under `vision/specs/schemas/`). Every
> envelope now cites a real schema file or names a new closed schema
> the spec proposes. The five panel BLOCKERs are fixed (chain
> composition size, phantom `archived_to`, `next_workflow` cycle
> guard, `wait=False` failure path, broken `$ref` fragment). Each of
> the 17 IMPORTANT findings is either fixed or carries an inline
> "deferred — see <pointer>" note.

## 1. Why

`vision/00-charter.md` defines a 3xN matrix governed by three rules
(column isomorphism, row isomorphism, name-driven discovery).
`vision/03-architecture.md` resolves that matrix into ONE engine
(FastMCP) walking ONE substrate (GraphQLite). Spec 06 fixed the
agentic surface (four verbs, deferred schemas). Spec 07-v1 fixed the
workflow runner (graph walker, gates as nodes, Continuation as graph
node). Spec 08-v1 fixed the context substrate (GraphQLite-only, driver
REGISTRY, hook chain).

Per-column `INTERFACE-TO-*.md` files declare what each column EXPOSES
and what it REQUIRES across each boundary. Each interface is a
contract; the wire shape is defined in
`vision/specs/schemas/<col>/interface-to-<other>.schema.json` and the
four-verb envelope schemas in
`vision/specs/schemas/agentic/four-verb/`.

What is missing across the canon: a **single dispatch mechanism per
(caller, callee) column pair**, with a verification gate per crossing
that distinguishes "the callee replied" from "the callee did the work"
(lesson 12 — `state=COMPLETED` is not done). Spec 09 fills exactly
that gap. It does NOT re-derive the column interfaces; it composes
them.

> Background, informational only: `Plan/decisions/0003`, `0005`,
> `0007`, `0009` (the MVP-era ADRs). They predate the `vision/`
> reframing in `vision/03-architecture.md` and should be read as
> archeology. Where a constraint matters, this spec cites the
> `vision/` source — not the ADR.

## 2. The matrix

Caller column down the rows; callee column across the top. Each cell
names the single dispatch mechanism this spec sanctions.

| caller \ callee | agentic | workflow | context |
|---|---|---|---|
| **agentic**  | §3.1 `mcp__call_tool` / `mcp__dispatch_skill` re-entry through the four-verb contract | §3.2 skill envelope carries `data.workflow_dispatch`; harness inspects post-ingest and emits via `mcp__call_tool` against `mcp__<row>_start` | §3.3 four-verb `call_tool` on the context-row anchor triad (`mcp__context_query` / `_describe` / `_read`); direct `context.Store` imports forbidden |
| **workflow** | §3.4 `pipeline._walk_phase` (BUILT) — handler resolution via `cell_loader.discover()` registry | §3.5 `PRECEDES` traversal (opt-in `chain=True`) intra-row; `data.workflow_dispatch` re-entry through the four-verb contract for inter-row | §3.6 gate evaluator + `Store.query` Cypher (BUILT) |
| **context**  | §3.7 PostToolUse / PreToolUse hook chain (BUILT) | §3.8 `Watcher` cells; the bootloader invokes `mcp__call_tool(mcp__<row>_start, …)` on emission via the registry's in-process callable | §3.9 schema `$ref` resolution (intra-row + `_shared/` only) + `DERIVED_FROM` edges in PostToolUse |

Three cells are **built** today; the other six are **new** under this
spec. No cell is "partial".

A new shared concept binds §3.2 and §3.5: the **workflow_dispatch
triple**. It is the single shape used to ask the harness to start a
workflow phase from inside an envelope. Schema:
`vision/specs/schemas/_shared/workflow-dispatch.schema.json` (NEW;
shape sketch in §4.2). `next_workflow` (panel r1) and `chain_to` (panel
r1) are the same shape with one optional slot, so this revision
collapses them.

## 3. Per-cell contracts

Every cell SHALL conform to:

- **One MCP server** (`vision/03-architecture.md` §3, "FastMCP IS the
  runtime"). Every crossing routes through the same FastMCP instance.
- **One envelope** at the wire boundary: spec 02 `ToolResult`
  (`tag:agency-system.local,2026:schema:shared/tool_result`,
  closed, four required keys: `ok`, `data`, `warnings`,
  `next_suggested_tools`). Workflow yields wrap that envelope inside
  the spec 04 `PhaseStateEnvelope` as `tool_result`.
- **The 4 KB per-result invariant** (spec 02 §Encoding rules,
  "Total wire size of the envelope SHOULD stay under 4 KB").
  Overflow is signalled by `data.artefact_ref` pointing at an
  `Artefact` node in the graph — the same slot spec 02 names. There
  is NO root-level `archived_to` field; the panel r1 BLOCKER on a
  phantom `archived_to` is closed by deleting every such reference
  and routing overflow through `data.artefact_ref`.
- **A verification gate per crossing** that distinguishes reply from
  work-done (lesson 12). Each cell below names its gate explicitly
  and pins the schema field the assertion checks.

### 3.1 agentic -> agentic

- **Caller / callee**: agentic column (skill or tool) -> agentic column.
- **Status**: new.
- **Mechanism**: re-entry through the four-verb contract. A skill that
  needs another row's tool calls `mcp__call_tool(name, arguments)`; a
  skill that needs another row's skill calls
  `mcp__dispatch_skill(row, skill_slug, context_refs)`. Direct
  `from agentic.<other_row>.handlers.<x> import handle` is **forbidden**
  — that path bypasses the hook chain wired in
  `agentic/_bootloader.py::boot()` (anchor: the
  `make_hooked_wrapper` symbol; the test in
  `tests/agentic/test_pretooluse_veto.py` pins the contract instead of
  raw line ranges, per panel SL #6/#7/#8).
- **Envelope (request)**:
  - `mcp__call_tool` — `vision/specs/schemas/agentic/four-verb/call-tool-request.schema.json`
    (`{name, arguments}`, `additionalProperties: false`).
  - `mcp__dispatch_skill` — `vision/specs/schemas/agentic/four-verb/dispatch-skill-request.schema.json`
    (`{row, skill_slug, context_refs}`, `additionalProperties: false`).
- **Envelope (response)**: spec 02 `ToolResult` per
  `call-tool-response.schema.json` / `dispatch-skill-response.schema.json`.
  `dispatch_skill` MAY additionally return a `PhaseStateEnvelope`
  (spec 04) when the dispatched skill triggers a workflow yield —
  see spec 06 §2 (`dispatch_skill` signature).
- **Verification gate**: caller asserts `envelope["ok"] is True` AND
  inspects `envelope["data"]` for the callee's contracted success
  marker (e.g. `data.artefact_metadata.sha256` for an artefact
  producer, validated against
  `vision/specs/schemas/context/nodes/artefact.schema.json`).
  `ok=True` alone is insufficient — that is the lesson-12 trap.
- **Worked example (jules row — the only fully wired row today)**:
  `/jules-orchestrate` skill, mid-flow, needs to query the jules
  cache before dispatching a new session. It invokes
  `mcp__call_tool(name="mcp__jules_query", arguments={"topic": ...})`
  through the harness, receives a spec-02 envelope, checks
  `envelope["data"]["hits"]` is a list, then continues. Both legs flow
  through the hook-wrapping closure registered at boot, so PreToolUse
  and PostToolUse fire on both.
- **`dispatch_skill` variant** (closes panel ORR #4): the same
  worked example with a skill target — `mcp__dispatch_skill(row="jules",
  skill_slug="research", context_refs=["jules:session:abc"])` — returns
  either a `ToolResult` OR a `PhaseStateEnvelope` per spec 06 §2.
  Both response shapes are covered in §6.

### 3.2 agentic -> workflow

- **Caller / callee**: agentic skill -> workflow phase.
- **Status**: new.
- **Mechanism**: the skill's handler returns a spec-02 `ToolResult`
  carrying a NEW field `data.workflow_dispatch` whose value matches
  `vision/specs/schemas/_shared/workflow-dispatch.schema.json` (NEW;
  shape in §4.2). The harness's post-ingest interception code
  (introduced by this spec) reads that field and emits the workflow
  start through the **four-verb contract** — i.e., it calls
  `mcp__call_tool(name="mcp__<row>_start", arguments={row, phase, inputs})`
  through the same in-process registry path that any other caller
  uses. The interception does NOT call `pipeline.start` directly;
  routing through the four-verb contract preserves the hook chain
  per `vision/agentic/INTERFACE-TO-WORKFLOW.md` §3.1
  (`execute_pipeline`) and `vision/workflow/INTERFACE-TO-AGENTIC.md`
  §3 (uniform entry).
- **Envelope (outbound)**: spec 02 `ToolResult` with
  `data.workflow_dispatch` matching the workflow-dispatch schema.
- **Envelope (inbound)**: spec 02 `ToolResult` (the `mcp__call_tool`
  response). If the workflow phase yields, that response IS a
  `PhaseStateEnvelope` per spec 04 — but the harness wraps it as a
  spec 02 envelope at the four-verb boundary (the `data` of the
  outer envelope is the inner `PhaseStateEnvelope`).
- **Verification gate**: the harness rejects a `workflow_dispatch`
  whose `row` has no `Phase` node for `phase_id` AND whose
  `[workflow.lazy_link] enabled = false` — exactly the lazy-link
  contract spec 07-v1 §FR1 already enforces (anchor:
  `workflow/<row>/manifest.toml` `[workflow.lazy_link]` boolean).
  Lesson 12 honoured by: the lazy-link check is a graph lookup
  (`MATCH (p:Phase {row, phase_id}) RETURN p`) — the verification is
  the existence of the node, not a reply from the callee.
- **Cycle guard (closes panel DSA #2 / BLOCKER 3)**: the harness
  maintains a per-session `workflow_dispatch_depth` counter on the
  `Session` node payload (schema:
  `vision/specs/schemas/context/nodes/session.schema.json`; this
  spec introduces a new closed `workflow_dispatch_depth: integer`
  field on its `payload` — see §4.3). Each emission increments;
  values `> 3` are rejected with `WORKFLOW_DISPATCH_CYCLE` (a new
  enum value on the spec 02 `data.error.code` slot — see §4.6).
  Three is a defensible default for v0; the exact limit lives in
  `context/_shared/error_codes.py` so it's auditable. The counter
  is reset when the session ends.
- **Worked example (jules row)**: `/jules-research` completes
  retrieval and wants to hand off to the dispatch phase. Its handler
  returns `{"ok": True, "data": {"hits": [...],
  "workflow_dispatch": {"row": "jules", "phase_id": "03",
  "inputs": {"topic": "..."}}}, "warnings": [], "next_suggested_tools": []}`.
  The interception emits
  `mcp__call_tool("mcp__jules_start", {"row": "jules", "phase_id": "03", "inputs": {"topic": "..."}})`;
  the caller receives the wrapped envelope (status `running` or
  `blocked_on_user`).

### 3.3 agentic -> context

- **Caller / callee**: agentic skill/tool -> context column.
- **Status**: new (the underlying tools exist; the routing contract
  is new).
- **Mechanism**: context-row tools (the future
  `context_query` / `context_describe` / `context_read` anchor triad,
  registered as `mcp__context_query` / `_describe` / `_read` per the
  spec 06 §4 `mcp_tool_name(row, export)` derivation) are the **only**
  sanctioned route into the ontology graph for agentic callers.
  Direct `from context import get_store; store.query(...)` from an
  `agentic/` module is **forbidden** — it skips PreToolUse validation
  (`vision/context/INTERFACE-TO-AGENTIC.md` §3), defeats the 4 KB
  cap (spec 02 §Encoding rules), and bypasses provenance logging.
  The triad-name choice is consistent with the canonical
  `query_graph(cypher) -> list[dict]` signature in
  `vision/context/INTERFACE-TO-AGENTIC.md` §2.
- **Envelope (request)**:
  `vision/specs/schemas/agentic/interface-to-context.schema.json`
  (`{action, query_string | node | edge}`, `additionalProperties: false`).
- **Envelope (response)**: spec 02 `ToolResult`. Bulk results that
  exceed 4 KB MUST be replaced with `data.artefact_ref` pointing at
  an `Artefact` node — same overflow path spec 02 §Encoding rules
  defines. There is NO `archived_to` slot (panel SL #1 closed).
- **Verification gate**: PreToolUse `validate_envelope_in` runs on
  the inbound args (the validator declared in
  `vision/specs/schemas/context/hooks/pretooluse.schema.json`);
  PostToolUse `ingest` logs the call. The skill asserts
  `envelope["ok"]` AND that the returned node IDs round-trip through
  a follow-up `mcp__context_describe` — the lesson-12-honouring
  check is "describe confirms the IDs exist", not just "search
  replied". (Panel LLA #2 closed: the verification is graph-side,
  not a reuse of the request-side validator.)
- **Worked example (jules row)**: `/jules-recover` needs to find the
  `Artefact` node for a patch by sha256. It invokes
  `mcp__call_tool(name="mcp__context_query",
  arguments={"action": "query", "query_string": "MATCH (a:Artefact {sha256: $h}) RETURN a.id"})`
  rather than reaching into `Store` directly. The returned IDs feed
  `mcp__context_read` to fetch the node payload.

### 3.4 workflow -> agentic — BUILT

- **Caller / callee**: workflow phase -> agentic handler.
- **Status**: built (`workflow/_runner/pipeline.py`, function
  `_resolve_handler` / `_walk_phase` — anchor by function name, not
  line range, per panel SL).
- **Mechanism**: `_walk_phase` resolves
  `mcp__<row>_<entry_verb>` from the cached `CellRegistry` and calls
  it with the phase inputs.
- **Envelope (request)**: phase inputs match
  `vision/specs/schemas/agentic/interface-to-workflow.schema.json`
  (`{action, row, phase, inputs}`, `additionalProperties: false`).
- **Envelope (response)**: handler returns spec 02 `ToolResult`; the
  walker wraps it as spec 04 `PhaseStateEnvelope`.
- **Verification gate**: walker validates `isinstance(tool_result,
  dict)` and an `ok` boolean; non-conforming returns are coerced to
  `HANDLER_BAD_RETURN` failed envelopes. **This spec strengthens spec
  07-v1's verification step**: spec 06 §5 envelope validation MUST
  run on the registry-wrapped tool before the walker receives it
  (closes the gap panel SL #6 cited as elided).
- **Worked example (jules row)**: `mcp__call_tool("mcp__jules_start",
  {"row": "jules", "phase": "03", "inputs": {...}})` resolves
  `mcp__jules_dispatch` (the phase-03 handler), invokes it, gets back
  a `ToolResult`, wraps as `PhaseStateEnvelope(status="completed")`,
  returns. The jules-row phase-03 handler is the production
  reference.

### 3.5 workflow -> workflow

- **Caller / callee**: workflow phase -> workflow phase.
- **Status**: new.
- **Mechanism**: ONE primitive serves both intra-row and inter-row
  chaining — the `workflow_dispatch` triple (same shape as §3.2,
  same schema). Two distinct dispatch modes share that shape:
  1. **Intra-row chaining via `PRECEDES`**: when a phase completes
     and the caller passes `chain=True` on `pipeline.start(...)`
     (new parameter, default `False`), the walker emits a
     `workflow_dispatch` triple targeting the next-hop `Phase`
     node found by
     `MATCH (p:Phase {row, phase_id})-[:PRECEDES]->(next:Phase) RETURN next`
     (one hop only; panel DSA #6 closed by the depth cap below).
  2. **Inter-row chaining**: a phase handler returns a `ToolResult`
     whose `data.workflow_dispatch.row` differs from the current
     row. The pipeline emits via `mcp__call_tool("mcp__<row>_start",
     …)` — the SAME path §3.2 uses (closes panel DSA #3:
     `chain_to` no longer bypasses the hook chain; the four-verb
     emission is the only path).
- **Envelope**: spec 04 `PhaseStateEnvelope` for both legs. Inside,
  the carried `tool_result` matches spec 02.
- **No `wait=False` in v0** (closes panel BLOCKER 4 / DSA #1).
  Fire-and-forget chaining requires a status-query surface that
  does not exist in v0 (no `mcp__meta_envelope_read` yet, no
  `WatcherHealth` observable surface). Until then, chain legs run
  synchronously (`wait=True` implicit) so the chained leg's
  failure propagates back to the original caller's envelope. The
  `wait` slot in the workflow-dispatch schema is enum-restricted to
  `["true"]` for v0 — when `mcp__meta_envelope_read` lands, the
  enum is widened.
- **Composition size cap (closes panel BLOCKER 1 / TBS #1)**: the
  chained `PhaseStateEnvelope` SHALL NOT carry the prior leg's full
  payload inline. Instead, the prior envelope is persisted as a
  `Continuation` node in the graph (schema:
  `vision/specs/schemas/context/nodes/continuation.schema.json`,
  already canonical per spec 04 STATUS note: Continuation is now a
  graph node, not a file) and the chained envelope carries
  `tool_result.data.previous_continuation_id: <string>` (the
  Continuation node id) — a fixed-size pointer. The composed wire
  payload is therefore O(1) in chain depth.
- **Cycle guard**: a `chain_depth` counter on the active `Session`
  node payload (same field added in §3.2 as
  `workflow_dispatch_depth`; the two counters share one slot since
  every chain leg is a workflow-dispatch emission). The cap is 3 by
  default; over-cap returns a failed envelope with
  `data.error.code = "WORKFLOW_DISPATCH_CYCLE"`.
- **Verification gate**: a `workflow_dispatch` whose target row has
  no matching `Phase` node fails fast under the lazy-link policy
  from §3.2. `PRECEDES` traversal requires the next-phase node to
  exist; lazy-create across a `PRECEDES` edge is **never** allowed
  (refuses silently filling in chain links).
- **Worked example (jules row)**: phase 06 (`verify`) finds the
  remote branch missing and chains to phase 07 (`recover`). Phase
  06's handler returns
  `{"ok": True, "data": {"workflow_dispatch": {"row": "jules", "phase_id": "07", "inputs": {"sid": "abc"}}}, ...}`.
  The pipeline persists phase 06's envelope as a `Continuation`
  node, emits via `mcp__call_tool("mcp__jules_start", {...})`, and
  returns the phase-07 envelope with
  `tool_result.data.previous_continuation_id` set. Two envelopes
  exist on the wire over the course of the chain, but only one is
  in flight at a time; total wire ≤ 4 KB.

### 3.6 workflow -> context — BUILT

- **Caller / callee**: gate evaluator -> ontology.
- **Status**: built (`workflow/_runner/gate.py`, function
  `evaluate_gate`).
- **Mechanism**: gate evaluator imports `context.get_store` and calls
  `store.query(cypher, params)`. The Cypher dialect is whatever
  GraphQLite offers (`vision/03-architecture.md` §5.1).
- **Envelope**: evaluator MUST return exactly `{"ok": bool,
  "message": str}` — pinned in `evaluate_gate`'s shape check
  (anchor: the `set(result.keys()) != {"ok", "message"}` guard, not
  a line range; this closes panel SL #6's anchor-drift concern).
- **Verification gate**: the evaluator's return shape is asserted at
  the call site; any other shape fails the gate closed with
  `"evaluator return must be exactly {ok, message}"`. This spec
  **promotes that behaviour from regression armour to a real
  contract** (closes panel TCA #3): a new acceptance scenario in §6
  asserts that an evaluator that imports `get_store` and returns the
  raw rows triggers the gate-closed path. The result MUST be reduced
  to a pass/fail boolean inside the evaluator, never returned raw
  to the pipeline. The dangling-`ExternalRef` audit query MUST carry
  `LIMIT 50` (closes panel TBS #4); the warning message includes
  `"first 50 of N total"` when truncation occurs.
- **Worked example (jules row)**: the
  `workflow/jules/gates/session-completed.yaml` evaluator queries
  `MATCH (s:JulesSession {sid: $sid}) RETURN s.state` and returns
  `{"ok": s.state == "COMPLETED", "message": ...}`. The pipeline
  consumes the boolean; the Store's raw rows never leave the
  evaluator.

### 3.7 context -> agentic — BUILT

- **Caller / callee**: hook chain (PreToolUse / PostToolUse) ->
  agentic tool.
- **Status**: built (the `boot()` entrypoint registers
  `make_hooked_wrapper` around every tool — anchor by symbol, not
  line range).
- **Mechanism**: the bootloader wraps every registry entry in a
  closure that calls `validate_envelope_in(tool_name, args)` first
  and `ingest(tool_name, envelope)` after. The chain is
  `PreToolUse -> tool -> PostToolUse`. Hook payloads match
  `vision/specs/schemas/context/hooks/pretooluse.schema.json` and
  `…/posttooluse.schema.json`.
- **Verification gate**: this spec adds the **right of rejection**
  (TBD-5 below): PreToolUse returning `{ok: False, errors: [...]}`
  SHALL be treated by the bootloader as a hard veto — the tool is
  NOT invoked and a failed `ToolResult` carrying the PreToolUse
  errors is returned (with `data.error.code = "PRETOOLUSE_VETO"`).
  The current wrapper discards the PreToolUse return; this spec
  closes that gap. The veto is meaningful even on a near no-op
  validator today because subsequent waves (especially §3.9
  cross-row `$ref` rejection) make `validate_envelope_in`
  load-bearing — closes panel ORR #3 / LLA #1 by naming the future
  enforcement explicitly rather than relying on TODAY's behaviour.
- **Worked example (jules row)**: when `mcp__jules_dispatch` is
  invoked with a malformed args dict, `validate_envelope_in` returns
  `{"ok": False, "errors": ["..."]}`; the wrapper synthesises a
  failed envelope and never reaches the handler. PostToolUse then
  ingests the failure envelope into the `tools_call_log` for
  provenance.

### 3.8 context -> workflow

- **Caller / callee**: context-column watcher cell -> workflow phase.
- **Status**: new.
- **Mechanism**: a context-row cell MAY declare a `[watcher]`
  sub-table in its `manifest.toml`. Schema:
  `context/_shared/schemas/context-cell.schema.json` gains an
  optional closed `watcher` block — `additionalProperties: false`,
  required keys `enabled` (bool), `poll_seconds` (int ≥ 1),
  `handler` (string, dotted module path), `emits` (string, MCP tool
  name), and OPTIONAL `extensions` (object) for future
  forward-compat (closes panel SL #4 / chair recommendation: closed
  schemas with explicit extension slot).
- **In-process emission path (closes panel ORR #2 / BLOCKER)**: the
  bootloader emits via the registered `mcp__call_tool` callable
  exposed by `CellRegistry.call_tool(name, args)` — the same Python
  callable that FastMCP's wire path invokes for an external client.
  There is no second client surface; the bootloader is BOTH the MCP
  server and the in-process consumer of its own `mcp__call_tool`.
  This is the canonical interpretation of "every crossing routes
  through the four-verb contract" — the contract is a Python
  callable; the wire framing is incidental.
- **Watcher boot-ordering invariant (closes panel TCA #1 / ORR
  #5)**: watcher registration SHALL happen **after**
  `register_four_verb_contract(mcp, registry)` returns AND after
  `_wrap_registry_with_hooks(registry)` returns. The fault-injection
  test enumerated in the plan asserts that flipping the order is a
  test failure, not a silent runtime error.
- **Watcher-emitted payload**: the watcher's `poll()` returns
  either `None` (no emission) or a dict matching the
  `workflow_dispatch` triple plus a non-empty `dedupe_key` string
  (min length 1 — closes panel DSA #5 / SL #4). The bootloader
  emits via the four-verb contract; the emission is logged as a
  `WatcherEmission` node (schema:
  `vision/specs/schemas/context/nodes/watcher-emission.schema.json`,
  NEW; shape in §4.4).
- **Envelope**: outbound emission matches the workflow-dispatch
  schema + dedupe_key; the returned spec 02 envelope is logged but
  not surfaced to the user (the user did not invoke the watcher).
- **Verification gate**: each watcher emission MUST be deduplicated
  on `(row, phase_id, dedupe_key)` via a graph existence check on
  the `WatcherEmission` node. Double-emits are refused with a
  logged warning AND a metric increment on the `WatcherHealth` node
  (schema: `vision/specs/schemas/context/nodes/watcher-health.schema.json`,
  NEW; shape in §4.5 — closes panel ORR #6 by giving operators a
  graph-queryable health surface). This implements terminal-state-
  once semantics inside the matrix.
- **Worked example (jules row, forward-looking — closes panel ORR #7
  by acknowledging this path does not yet exist on disk)**: a
  to-be-created `context/jules/watchers/state.py` polls the GitHub
  API for branches matching open Jules session ids. When a new
  branch appears for `sid=abc`, `poll()` returns `{"row": "jules",
  "phase_id": "06", "inputs": {"sid": "abc"}, "dedupe_key": "abc"}`.
  The bootloader emits via
  `mcp__call_tool("mcp__jules_start", {"row": "jules", "phase_id": "06", "inputs": {"sid": "abc"}})`.
  The verify phase runs once and never re-runs for the same `sid`.

### 3.9 context -> context

- **Caller / callee**: context column -> context column.
- **Status**: new (formalisation of an existing pattern).
- **Mechanism**: two sub-mechanisms, both intra-column composition.
  1. **Schema `$ref` composition**. A row's
     `context/<row>/schemas/*.schema.json` MAY reference shared
     schemas via JSON Schema `$ref` to
     `context/_shared/schemas/<name>.schema.json`. PreToolUse
     resolution walks `$ref`s in the same process; cross-row `$ref`s
     (`context/<other-row>/schemas/*`) are **forbidden** — every row
     is its own ontology slice; cross-row constraints belong in
     `_shared/`.
  2. **`DERIVED_FROM` edges** between `Artefact` nodes (schema:
     `vision/specs/schemas/context/edges/derived-from.schema.json`).
     Already emitted by the PostToolUse `ingest` flow. Artefacts in
     one row point at artefacts in another via this relationship;
     placeholder targets keep the graph closed even when the source
     artefact has not been ingested yet.
- **Envelope**: no wire envelope — both legs are intra-process.
  Schema composition is a PreToolUse-time operation; edge emission
  is part of PostToolUse `ingest`.
- **Verification gate**:
  - For `$ref`: `jsonschema.RefResolver` failures surface as
    PreToolUse errors and (per §3.7) reject the call.
  - For `DERIVED_FROM`: PostToolUse `_ensure_node` already
    guarantees edge closure; this spec adds a periodic
    "dangling `ExternalRef` audit" gate (advisory, not blocking)
    that flags `ExternalRef` placeholder nodes older than 7 days
    that were never backfilled. Audit query `LIMIT 50` (closes
    panel TBS #4).
- **Worked example (jules row, `$ref` form corrected — closes panel
  BLOCKER 5 / SL #2)**: `context/jules/schemas/session.schema.json`
  uses `"$ref": "../../_shared/schemas/artefact-node.schema.json#/properties/sha256"`
  for the session-output hash field. The artefact-node schema has
  `sha256` as a top-level property (line 26 of the live file), not
  under a non-existent `definitions` block — `#/properties/sha256`
  is the correct fragment. At ingest time, a Jules session
  artefact's `derived_from: ["music/Artefact/<sha>"]` emits an edge
  from the jules-row artefact into the music-row artefact; the
  music artefact's placeholder is overwritten in-place when it
  later ingests through its own channel.

## 4. New schemas this spec introduces

All new schemas are closed (`additionalProperties: false`) with an
explicit `extensions: object` slot only where forward-compat is
required (panel SL #4 / chair recommendation).

### 4.1 Composition cap policy (informational)

Per-cell return SHALL fit in 4 KB AFTER composition. The §3.2 and
§3.5 wrappers MUST drop the prior `data` payload and replace it with
a fixed-size pointer (see §4.7 below) when their compositional
return would exceed 3 KB inline. Overflow into an `Artefact` node
uses `data.artefact_ref` (the spec 02 §Encoding rules slot — already
canonical).

### 4.2 `workflow-dispatch.schema.json` (NEW)

Proposed path: `vision/specs/schemas/_shared/workflow-dispatch.schema.json`.

```jsonc
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://agency-system.dev/schemas/_shared/workflow-dispatch.schema.json",
  "title": "Workflow Dispatch Triple",
  "description": "Carried inside data.workflow_dispatch on a spec-02 ToolResult to request the harness emit mcp__call_tool('mcp__<row>_start', …). Single shape used by §3.2 (agentic→workflow) and §3.5 (workflow→workflow).",
  "type": "object",
  "additionalProperties": false,
  "required": ["row", "phase_id", "inputs"],
  "properties": {
    "row":      {"type": "string", "pattern": "^[a-z][a-z0-9-]{0,30}$"},
    "phase_id": {"type": "string", "pattern": "^[0-9]{2}(-[a-z0-9-]+)?$"},
    "inputs":   {"type": "object"},
    "wait":     {"enum": ["true"], "description": "v0 supports synchronous chaining only. Widened to ['true','false'] when mcp__meta_envelope_read lands."},
    "extensions": {"type": "object", "description": "Reserved for forward-compat fields."}
  }
}
```

This collapses panel r1's `next_workflow` and `chain_to` into one
shape — closing panel SL #5's drift risk.

### 4.3 `Session` node payload — depth counter addition

The existing `vision/specs/schemas/context/nodes/session.schema.json`
gains one OPTIONAL closed property on its `payload`:

```jsonc
"workflow_dispatch_depth": {
  "type": "integer",
  "minimum": 0,
  "maximum": 16,
  "description": "Per-session counter used by §3.2 / §3.5 to cap recursive workflow dispatches. Reset at session end."
}
```

This is the canonical place for that counter — Continuation is a
state-bearing graph node already (spec 04 STATUS note), so adding a
depth field to the parent Session node fits the graph model. The
hard-cap value (3) lives in `context/_shared/error_codes.py`, not the
schema.

### 4.4 `watcher-emission.schema.json` (NEW)

Proposed path:
`vision/specs/schemas/context/nodes/watcher-emission.schema.json`.

```jsonc
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://agency-system.dev/schemas/context/nodes/watcher-emission.schema.json",
  "title": "WatcherEmission Node",
  "type": "object",
  "additionalProperties": false,
  "required": ["id", "label", "payload"],
  "properties": {
    "id":    {"type": "string"},
    "label": {"const": "WatcherEmission"},
    "payload": {
      "type": "object",
      "additionalProperties": false,
      "required": ["row", "phase_id", "dedupe_key", "emitted_at"],
      "properties": {
        "row":         {"type": "string"},
        "phase_id":    {"type": "string"},
        "dedupe_key":  {"type": "string", "minLength": 1},
        "emitted_at":  {"type": "string", "format": "date-time"},
        "extensions":  {"type": "object"}
      }
    }
  }
}
```

`dedupe_key.minLength: 1` is the schema-side enforcement of the panel
DSA #5 finding (a watcher returning `""` no longer self-silences;
PreToolUse rejects the emission).

### 4.5 `watcher-health.schema.json` (NEW)

Proposed path:
`vision/specs/schemas/context/nodes/watcher-health.schema.json`.

```jsonc
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://agency-system.dev/schemas/context/nodes/watcher-health.schema.json",
  "title": "WatcherHealth Node",
  "type": "object",
  "additionalProperties": false,
  "required": ["id", "label", "payload"],
  "properties": {
    "id":    {"type": "string"},
    "label": {"const": "WatcherHealth"},
    "payload": {
      "type": "object",
      "additionalProperties": false,
      "required": ["handler", "consecutive_failures", "last_status"],
      "properties": {
        "handler":             {"type": "string"},
        "consecutive_failures":{"type": "integer", "minimum": 0},
        "last_status":         {"enum": ["healthy", "warning", "disabled"]},
        "last_error":          {"type": "string"},
        "last_emission_at":    {"type": "string", "format": "date-time"},
        "dedupe_hit_count":    {"type": "integer", "minimum": 0},
        "extensions":          {"type": "object"}
      }
    }
  }
}
```

Operators query `MATCH (h:WatcherHealth {last_status: "disabled"})
RETURN h` to find dark watchers — closing panel ORR #1 / #6 by
giving the disable state a graph-queryable home.

### 4.6 spec 02 `error.code` enum additions

Extends the (informally documented) `data.error.code` slot of the
spec 02 envelope. Per-tool data schemas already validate `data`;
this spec adds the following codes to
`context/_shared/error_codes.py` as the canonical list:

- `ENVELOPE_INVALID` (already used; spec 06 §5)
- `HANDLER_BAD_RETURN` (already used; workflow walker)
- `PRETOOLUSE_VETO` (NEW; §3.7)
- `WORKFLOW_DISPATCH_CYCLE` (NEW; §3.2 / §3.5)
- `HANDLER_EXCEPTION` (NEW; TBD-1 below)
- `CROSS_ROW_REF` (NEW; §3.9 cross-row `$ref` reject)

### 4.7 `previous_continuation_id` slot

A new OPTIONAL property on `tool_result.data`:
`previous_continuation_id: <string>` — the `Continuation` node id of
the chain leg's prior envelope. Used by §3.5 to keep composed chains
under the 4 KB cap. The slot is NOT carried as a schema property on
`tool_result.schema.json` itself (spec 02's `data` is intentionally
open), but per-tool schemas for chain emitters SHALL declare it.
This honours panel SL #3 (closed-shape-by-per-tool-schema is the
canonical L06 path; opening the root would defeat spec 02).

## 5. Resolving founder TBDs

### TBD-1: error routing between columns (does an agentic exception block PostToolUse?)

**Decision**: No. PostToolUse SHALL fire on every tool invocation,
including ones whose handler raised. The bootloader wrapper catches
handler exceptions and synthesises a failed envelope with
`data.error.code = "HANDLER_EXCEPTION"` (closes panel TCA #5: the
test asserts the envelope shape AND the code, not just that ingest
fired).

**Rationale**: provenance > propagation. Suppressing the ingest on
exception would violate lesson 12 (silent-fail recovery requires an
audit trail).

### TBD-2: per-row vs central registry for cross-column dispatch

**Decision**: central. The single `CellRegistry` built by
`cell_loader.discover()` is the canonical lookup for every cell.
Workflow's `_resolve_handler` already uses it; watchers (§3.8) MUST
use the four-verb contract that reaches it too. Per-row registries
would re-introduce the "many MCP servers" trap
`vision/03-architecture.md` §3 explicitly closes.

### TBD-3: who owns context-mode-sync (hook vs service vs explicit tool)

**Decision**: hook. The PostToolUse `ingest` flow is the single
point where artefact metadata becomes graph state.

**Rationale**: one write path. Spec 08-v1's PostToolUse ingest is
already the artefact landing site; manifest sync is downstream of
that, not parallel.

### TBD-4: whether skills' chained-call results must also wrap in ToolResult

**Decision**: yes, always. Every cross-column boundary in §3 returns
spec 02 `ToolResult` or spec 04 `PhaseStateEnvelope`. Intra-column
composition (a skill's helper calling its own private function) is
exempt. The envelope is the contract; without it, nothing enforces
spec 02's 4 KB cap.

### TBD-5: whether hooks may reject tool results, not just transform them

**Decision**: yes, on PreToolUse only. PreToolUse returning
`{ok: False, errors: [...]}` SHALL veto the call; the bootloader
synthesises a `PRETOOLUSE_VETO` failed envelope and skips handler
invocation. PostToolUse SHALL NOT have rejection authority — by the
time it runs, the side effect has occurred.

## 6. Out of scope

- **Code Mode rendering of crossover results** — the
  `prefers_codemode` flag flows through unchanged; this spec does not
  introduce a Code-Mode-specific crossover path.
- **Skill `skill_kind` enforcement at crossover time** — kind catalog
  exists in VOCABULARY; this spec stays kind-agnostic.
- **Hot reload of cells / schemas / watchers** — cold-restart only.
  However, the runtime SHALL persist watcher health state
  (`WatcherHealth` nodes, §4.5) so operators can `mcp__context_query`
  for unhealthy watchers without a cold boot — closes panel ORR #1.
- **Multi-process or multi-tenant graphs** — spec 08-v1 §Out of scope
  still governs.
- **`Plan/_research` corpus ingestion** as a context->context source —
  separate spec.
- **`workflow_dispatch.wait = false`** (fire-and-forget chaining) —
  deferred until `mcp__meta_envelope_read` (or an equivalent envelope-
  read surface) ships. Re-enabled by widening the `wait` enum in
  §4.2.
- **`tools_call_log` growth bound / TTL sweeper** — deferred per
  spec 08-v1 §Out of scope. Acknowledged here so panel TBS #3 is
  not silently dropped.

## 7. Deferrals from the panel review (IMPORTANT-class findings)

Each entry below corresponds to a panel-review IMPORTANT finding
that this revision does NOT fully close. Listed inline so a reader
sees the punted work without grepping the review.

- **DSA #4 (PreToolUse veto on chained leg desynchronises
  provenance)** — partially closed: the §3.5 single-leg-in-flight
  rule means the prior leg is already persisted as a `Continuation`
  before the chained leg's PreToolUse runs. Compensating-transaction
  rollback of the prior `Continuation` on chained-leg veto is
  **deferred — see follow-up spec on compensating transactions**;
  v0 records the veto as a `WatcherHealth.last_error` and surfaces
  it in the returned envelope.
- **TBS #3 (provenance log explosion from watchers)** — deferred to
  spec 08-v1 §Out of scope (no `tools_call_log` TTL in v0). Listed
  in §6 above so the deferral is visible.
- **TBS #5 (boot payload accounting for watcher schemas)** —
  closed by §3.8's note that watcher schema bodies do NOT
  participate in `tools/list`. A one-line CI assertion is
  **deferred — see plan §3 Wave B test plan**.
- **TCA #4 (`test_no_direct_store_imports` scope)** — closed: the
  plan now scopes the lint to `agentic/<row>/**.py` only, and
  explicitly excludes `agentic/_harness/**` (which is the harness;
  legitimate Store consumers).
- **TCA #6 (chain-then-veto test)** — closed: §6 adds an acceptance
  scenario for this case.
- **TCA #7 (three-tests-per-cell fictional in §3.4)** — closed: §6
  acceptance scenarios re-enumerate the §3.4 coverage as three
  distinct assertions (handler bad return, handler exception,
  envelope-shape validation pre-walker).
- **ORR #6 (watcher observability)** — closed by §4.5
  `WatcherHealth` node.
- **LLA #1 (L06 cited but inverted)** — partially closed: §4.2 /
  §4.4 / §4.5 are all closed schemas with explicit `extensions`
  slots. The remaining concern (validate_envelope_in is a near no-op
  today) is addressed by §3.7 making cross-row `$ref` rejection a
  PreToolUse check — full schema teeth land in Wave A + Wave C.
- **LLA #2 (L12 cited but no new verification)** — closed: §3.2 / §3.3
  now name graph-side verification beyond the lazy-link lookup
  (existence check on the `Phase` node for §3.2; round-trip
  `describe` for §3.3).
- **LLA #3 (L14 contradicted by chain composition)** — closed: §4.1
  + §4.7 cap composed envelopes at 4 KB by using fixed-size
  `previous_continuation_id` pointers.

## 8. Acceptance criteria

```gherkin
Scenario: 3.1 agentic->agentic call_tool re-entry routes through the hook chain
  Given a skill /jules-orchestrate invokes mcp__call_tool("mcp__jules_query", {"topic": "x"})
  When the inner call returns
  Then validate_envelope_in fired on the inner call's args
  And ingest fired on the inner call's envelope
  And the outer skill received a spec-02 ToolResult

Scenario: 3.1 agentic->agentic dispatch_skill returns a ToolResult OR PhaseStateEnvelope
  Given a skill invokes mcp__dispatch_skill(row="jules", skill_slug="research", context_refs=[])
  When the called skill completes synchronously
  Then the response validates against tool_result.schema.json
  And when the called skill triggers a workflow yield, the response validates against the phase_state schema

Scenario: 3.2 agentic->workflow workflow_dispatch respects lazy-link
  Given a skill returns data.workflow_dispatch = {"row": "jules", "phase_id": "99", "inputs": {}}
  And no Phase node phase/jules/99 exists
  And workflow/jules/manifest.toml has [workflow.lazy_link] enabled = false
  When the harness inspects workflow_dispatch
  Then the emission returns a failed envelope with data.error.code = "PHASE_NOT_IN_GRAPH"
  And the skill's caller observes the failed envelope, not a Python exception

Scenario: 3.2 agentic->workflow recursion is capped at depth 3
  Given a chain A -> B -> A -> B where each leg returns data.workflow_dispatch
  When the bootloader processes the fourth emission
  Then the envelope.status == "failed"
  And data.error.code == "WORKFLOW_DISPATCH_CYCLE"
  And Session.payload.workflow_dispatch_depth == 4 at the point of refusal

Scenario: 3.3 agentic->context refuses direct Store access from agentic row modules
  Given an agentic/<row> module imports from context._store or context._drivers at module load
  When test_no_direct_store_imports runs
  Then it fails listing the offending module
  And the lint scope excludes agentic/_harness/** (legitimate)
  And the fix-hint names mcp__context_query / _describe / _read

Scenario: 3.4 workflow->agentic walker rejects malformed handler returns
  Given mcp__jules_dispatch returns the string "ok"
  When pipeline.start("jules", "03", {}) runs
  Then the envelope.status == "failed"
  And tool_result.data.error.code == "HANDLER_BAD_RETURN"

Scenario: 3.4 workflow->agentic envelope schema validation runs before the walker receives
  Given mcp__jules_dispatch returns a dict with extra root key "audit_trail"
  When the bootloader-wrapped tool returns
  Then spec-06 §5 envelope validation produces ENVELOPE_INVALID
  And the walker never sees the original malformed dict

Scenario: 3.5 workflow->workflow cross-row chain refuses missing target
  Given a handler returns tool_result.data.workflow_dispatch = {"row": "ghost", "phase_id": "01", "inputs": {}}
  And no row "ghost" exists
  When the pipeline processes the dispatch
  Then the returned envelope.status == "failed"
  And the prior phase's envelope is recoverable by tool_result.data.previous_continuation_id

Scenario: 3.5 workflow->workflow chained envelope size stays under 4 KB
  Given phase A produces a 3.5 KB envelope
  And phase B (chained from A) produces a 3.5 KB envelope
  When the chain completes
  Then the wire payload of the returned envelope is ≤ 4 KB
  And the prior leg is referenced by previous_continuation_id, not inlined

Scenario: 3.5 workflow->workflow PRECEDES traversal requires chain=True
  Given pipeline.start("jules", "03", {}, chain=False) is invoked
  And phase/jules/03-[:PRECEDES]->phase/jules/04 exists
  When phase 03 completes
  Then phase 04 is NOT invoked
  And the returned envelope.phase_id == "03"

Scenario: 3.5 chained leg PreToolUse veto surfaces to the caller
  Given a chain A -> B where B's PreToolUse returns {"ok": False, "errors": ["bad arg"]}
  When the pipeline processes the chain
  Then the returned envelope.status == "failed"
  And data.error.code == "PRETOOLUSE_VETO"
  And tool_result.data.previous_continuation_id points to A's persisted envelope

Scenario: 3.6 workflow->context evaluator return shape is enforced (not regression armour)
  Given a gate evaluator imports get_store and returns the raw query rows
  When evaluate_gate runs
  Then the gate fails closed with message containing "evaluator return must be exactly {ok, message}"

Scenario: 3.6 dangling ExternalRef audit respects LIMIT 50
  Given 200 dangling ExternalRef nodes exist
  When the audit gate runs
  Then the warning message contains at most 50 node ids
  And the message includes "first 50 of 200 total"

Scenario: 3.7 context->agentic PreToolUse veto blocks the handler
  Given validate_envelope_in returns {"ok": False, "errors": ["bad arg"]}
  When the bootloader-wrapped tool is invoked
  Then the handler function is NOT called
  And the returned envelope has data.error.code == "PRETOOLUSE_VETO"
  And the returned envelope.data.error.message contains "bad arg"
  And PostToolUse ingest fired on the failure envelope

Scenario: 3.7 handler exception synthesises a failed envelope AND fires ingest
  Given mcp__jules_dispatch raises RuntimeError("boom")
  When the bootloader-wrapped tool returns
  Then the envelope.status == "failed"
  And data.error.code == "HANDLER_EXCEPTION"
  And data.error.message contains "boom"
  And PostToolUse ingest fired on the failure envelope

Scenario: 3.8 context->workflow watcher emits via the four-verb contract
  Given context/jules/watchers/state.py.poll() returns {"row": "jules", "phase_id": "06", "inputs": {"sid": "abc"}, "dedupe_key": "abc"}
  When the bootloader handles the emission
  Then it called the registered mcp__call_tool callable with name="mcp__jules_start" and args matching the workflow_dispatch schema
  And NOT pipeline.start directly

Scenario: 3.8 watcher dedupe rejects double-emit and increments WatcherHealth
  Given a WatcherEmission node exists for ("jules", "06", "abc")
  When the watcher emits the same triple a second time
  Then no phase invocation occurs
  And the WatcherHealth node for the handler has dedupe_hit_count incremented by 1

Scenario: 3.8 watcher empty dedupe_key is rejected at PreToolUse
  Given a watcher's poll() returns {"row": "jules", "phase_id": "06", "inputs": {}, "dedupe_key": ""}
  When the bootloader attempts to emit
  Then PreToolUse rejects the emission with reason "dedupe_key.minLength"

Scenario: 3.8 watcher registration runs after the four-verb contract
  Given a test that flips the boot order so watchers register before register_four_verb_contract
  When the watcher's first poll fires
  Then the test fails with a clear "boot order violated" assertion
  And no silent ValueError surfaces in user logs

Scenario: 3.8 watcher disables itself after consecutive failures and surfaces in WatcherHealth
  Given a watcher's poll() raises on five consecutive invocations
  When the sixth poll cycle would run
  Then no poll occurs
  And the WatcherHealth node for the handler has last_status="disabled"
  And mcp__context_query for last_status="disabled" returns the node

Scenario: 3.9 context->context $ref to another row's schema is rejected
  Given context/jules/schemas/foo.schema.json contains "$ref": "../music/schemas/bar.schema.json"
  When PreToolUse resolves the schema chain
  Then it returns {"ok": False, "errors": [...]} naming "cross-row $ref forbidden"
  And data.error.code == "CROSS_ROW_REF"

Scenario: 3.9 context->context $ref to _shared resolves cleanly
  Given context/jules/schemas/session.schema.json contains "$ref": "../../_shared/schemas/artefact-node.schema.json#/properties/sha256"
  When PreToolUse resolves the schema chain
  Then resolution succeeds
  And the resolved type is "string" with pattern "^[0-9a-f]{64}$"

Scenario: 3.9 dangling ExternalRef audit surfaces as advisory warning
  Given an ExternalRef placeholder node was created 8 days ago with no backfill
  When the context->context audit gate runs
  Then it emits an advisory warning (not blocking)
  And the warning lists the node id and age
```

## 9. Reconciliation table — vision/ canon vs §3 mechanism names

Where panel reviewers feared `INTERFACE-TO-*.md` already named a
different mechanism than spec 09's previous draft, this table pins
the alignment. Names match the source files.

| Crossing | vision/ name | Spec 09 mechanism | Reconciled? |
|---|---|---|---|
| agentic→workflow | `execute_pipeline(row, phase, inputs) -> ToolResult` (vision/agentic/INTERFACE-TO-WORKFLOW.md §3.1) | `data.workflow_dispatch` triggers `mcp__call_tool("mcp__<row>_start", …)`; harness is the implementation of `execute_pipeline` | Yes — `execute_pipeline` IS the in-process callable behind the four-verb route |
| agentic→context | `query_graph(cypher) -> list[dict]` (vision/context/INTERFACE-TO-AGENTIC.md §2) | Routed via `mcp__context_query` (the four-verb-wrapped form); direct `query_graph` from agentic forbidden | Yes — `query_graph` is the underlying graph API; agentic reaches it ONLY through the wrapped MCP tool |
| context→agentic | `validate_frontmatter` + `ingest_node` (vision/context/INTERFACE-TO-AGENTIC.md §3) | `make_hooked_wrapper` runs PreToolUse `validate_envelope_in` and PostToolUse `ingest` | Yes — same hook chain, spec 09 strengthens it with veto rights |
| workflow→agentic | `dispatch_skill(row, skill_slug, context_refs)` (vision/workflow/INTERFACE-TO-AGENTIC.md §3) | `pipeline._walk_phase` → `CellRegistry.call_tool` → handler | Yes — `dispatch_skill` is the agentic-side four-verb form; the walker reaches handlers through the registry |
| context→workflow | `Watcher` cells in `context/<row>` (this spec, §3.8) | `[watcher]` sub-table; emission via four-verb `mcp__call_tool` | New (no prior interface named this) |
| workflow→context | `Cypher MATCH/RETURN` via `Store.query` (vision/03-architecture.md §5.1) | Gate evaluator (built); evaluator return reduced to `{ok, message}` | Yes — already canonical |
| workflow→workflow | (none — vision treats workflows as paths, not as callees) | `PRECEDES` traversal (intra-row, opt-in) OR `data.workflow_dispatch` (inter-row) | New — formalises a primitive vision/03-architecture.md §4 leaves implicit |
| agentic→agentic | `mcp__call_tool` / `mcp__dispatch_skill` (vision/specs/schemas/agentic/four-verb/*) | Same; re-entry through the four-verb contract | Yes — schema-anchored |
| context→context | `$ref` composition + `DERIVED_FROM` edges (vision/specs/schemas/context/edges/derived-from.schema.json) | Same; cross-row `$ref` forbidden, intra-row + `_shared/` allowed | Yes — schema-anchored |

## Dependencies

- **vision/00-charter.md** — matrix law and three rules.
- **vision/00.1-Overview.md** — column ownership; "agentic owns
  execution rules, workflow owns process rules, context owns memory".
- **vision/03-architecture.md** — one engine (FastMCP), one substrate
  (GraphQLite); the §1 "one engine" tenet is the floor for every
  crossing in this spec.
- **Per-column INTERFACE-TO-*.md files** — the §9 reconciliation
  table pins spec 09's mechanism names against these.
- **Spec 02** — `ToolResult` envelope; the wire boundary for every
  crossing. `data.artefact_ref` is the canonical overflow slot.
- **Spec 04** — `PhaseStateEnvelope`; the workflow yield form.
  `Continuation` is now a graph node (per spec 04 STATUS note),
  enabling §3.5's composition-cap design.
- **Spec 06** — agentic base. §3.1 / §3.7 / §3.8 route through the
  four-verb contract and `make_hooked_wrapper`.
- **Spec 07-v1** — workflow base. §3.4 / §3.5 / §3.6 extend
  `_walk_phase` and the `Phase` / `PRECEDES` graph model.
- **Spec 08-v1** — context base. §3.6 / §3.7 / §3.9 rely on the
  GraphQLite Store, the driver REGISTRY, and the hook chain.
- **`vision/specs/schemas/`** — every envelope in §3 cites a schema
  file under this tree. New schemas this spec proposes are listed
  in §4 with shape sketches.
