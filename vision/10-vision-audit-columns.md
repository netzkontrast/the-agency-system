---
slug: vision-audit-columns
type: audit
status: ready
owner: claude
created: 2026-05-20
updated: 2026-05-20
summary: Findings from the post-spec-09-r2 audit of vision/agentic|workflow|context/ — interface mismatches, mechanism contradictions, and stale critiques that block spec 09 from landing across the per-column canon.
audited:
  - vision/agentic/**
  - vision/workflow/**
  - vision/context/**
---

# Vision Audit — Per-Column Canon vs Spec 09 r2

Scope: 36 files (agentic/10 + workflow/13 + context/13). Anchor:
`vision/specs/09-crossover-matrix.md` r2.

## §1 Index of Findings

| # | file:line | severity | lens | one-line |
|---|---|---|---|---|
| F01 | vision/agentic/INTERFACE-TO-WORKFLOW.md:19, :35 | HIGH | L1 | `dispatch_skill(skill_id, args)` (string+dict) contradicts spec 09 §3.1 / workflow side `dispatch_skill(row, skill_slug, context_refs)`. |
| F02 | vision/agentic/INTERFACES.md:21 | HIGH | L1 | Names `dispatch_skill(row, phase, context_refs)` — third distinct signature; mixes "phase" semantics into the agentic dispatch verb. |
| F03 | vision/agentic/INTERFACES.md:48 / vision/workflow/INTERFACE-TO-AGENTIC.md:42 | HIGH | L2 | Both name `execute_pipeline(row, phase, inputs) -> ToolResult` as a workflow-exposed callable; spec 09 §3.2/§9 says it is an *in-process callable behind* `mcp__call_tool("mcp__<row>_start", …)`, not a direct surface. Neither file says so. |
| F04 | vision/agentic/INTERFACE-TO-WORKFLOW.md:14-20 | HIGH | L2 | Four-verb listed as `list_tools / call_tool / list_skills / dispatch_skill` — spec 06 (cited by spec 09) names `mcp__list_tools / mcp__call_tool / mcp__list_skills / mcp__dispatch_skill`. Bare-verb form bypasses the `mcp__` namespacing the matrix is anchored on. |
| F05 | vision/agentic/INTERFACE-TO-WORKFLOW.md:44-47 | MED | L2 | `mcp__workflow_scaffold_row(row_name)` is presented as workflow's *required* contract; spec 09 §3.4/§3.5 routes scaffolding through `mcp__call_tool("mcp__workflow_start", …)`. Bypasses four-verb. |
| F06 | vision/workflow/INTERFACE-TO-AGENTIC.md:43-44 | HIGH | L1, L2 | Requires "Graph edge creation (`write_edge`)" from agentic. Spec 09 §3.7 / TBD-3 puts graph writes in PostToolUse `ingest` — no handler `write_edge`. Direct contradiction. |
| F07 | vision/workflow/INTERFACE-TO-AGENTIC.md:48 | HIGH | L1 | "ToolResult envelope must be cleanly extended to accept the `audit_trail` field." Spec 09 §3 / §4 anchors on spec-02 closed envelope (no audit_trail root). Already negotiated away in `vision/agentic/INTEGRATED-DRAFT.md` §3 (Rejected) but workflow side still asserts it. |
| F08 | vision/workflow/INTERFACES.md:30-33 | HIGH | L1 | Four-verb listed as bare `list_tools, call_tool, list_skills, dispatch_skill`; `dispatch_skill(skill_id, args)`. Same naming + signature drift as F04 + F01. |
| F09 | vision/context/INTERFACE-TO-AGENTIC.md:9 | HIGH | L1, L2 | Surface declared as `query_graph(cypher) -> list[dict]` directly callable by agentic. Spec 09 §3.3 forbids direct surface; must route through `mcp__context_query/_describe/_read`. Plain `query_graph` invites the lint-failure §3.3 names. |
| F10 | vision/context/INTERFACE-TO-AGENTIC.md:15-16 | MED | L2 | `tag:agency-system.local,2026:schema:shared/tool_result` is named, but the spec-02 envelope has *four* required keys (ok, data, warnings, next_suggested_tools). This file silently keeps the older 6-key shape via INTERFACES.md (see F18). |
| F11 | vision/context/INTERFACE-TO-AGENTIC.md:23-26 | HIGH | L2 | "agentic MUST execute `validate_frontmatter(payload, schema_id)` before writing… MUST execute `ingest_node(filepath, frontmatter)`… MUST explicitly call `write_edge(...)`". Spec 09 §3.7 (and TBD-3) makes these PostToolUse/PreToolUse hooks the bootloader wraps around tools, *not* handler responsibilities. Direct contradiction with §3.7 + TBD-3. |
| F12 | vision/context/INTERFACE-TO-WORKFLOW.md:24 | HIGH | L2 | "workflow MUST emit a graph event mapping `Artefact -> SATISFIES_PHASE -> Phase`." Spec 09 §3.6 routes all gate-related context writes through the gate evaluator's `{ok, message}` contract and the spec-08 PostToolUse ingest path — `SATISFIES_PHASE` is not in the spec 09 / spec 08-v1 edge canon (canon uses `PRECEDES`, `DERIVED_FROM`, `DISPATCHED_TO`, `INVOKED_TOOL`). Stale ontology. |
| F13 | vision/workflow/INTERFACE-TO-CONTEXT.md:23-28 | HIGH | L2 | Workflow side names a `audit_trail: {template_used, schema_used, originating_skill}` envelope field as a required handoff. Spec 09 §3 + spec 02 close the envelope at four keys. No `audit_trail` slot. |
| F14 | vision/workflow/INTERFACE-TO-CONTEXT.md:37 | MED | L2 | Required edges named `SUPERSEDES` and `DERIVED_FROM`. Spec 09 §3.9 keeps `DERIVED_FROM`; `SUPERSEDES` is not in the spec 09 / spec 08-v1 edge canon. Drifted. |
| F15 | vision/workflow/INTERFACE-TO-CONTEXT.md:38 | MED | L2 | "`pandoc_render(node_slug)`" listed as a context-required callable. Spec 09 §6 lists Code Mode rendering as out-of-scope; pandoc is not in any spec-09 edge/tool table. Likely deferred / not part of the crossover canon. |
| F16 | vision/context/INTERFACE-TO-WORKFLOW.md:9-18 | MED | L1 | Context-side surface lists `workflow-cell.schema.json`, `tool_result.schema.json`, `get_storage_path(row, vault)`. Workflow side (INTERFACE-TO-CONTEXT.md) calls the same resolver `get_vault_path(...)` (line 41 of agentic side) / unnamed in workflow side. Resolver name drift (`get_vault_path` vs `get_storage_path`). |
| F17 | vision/agentic/INTERFACE-TO-CONTEXT.md:15 | HIGH | L2 | Envelope shape declared as `{ok, data, warnings, artefacts_written, next_suggested_tools, error}` (six keys, with `artefacts_written` and `error` at root). Spec 02 (cited by spec 09) closes at four keys with `data.artefact_ref` for overflow. `artefacts_written` and root `error` are phantom slots. |
| F18 | vision/context/INTERFACES.md:22 | HIGH | L2 | Same six-key envelope (`ok, data, warnings, artefacts_written, next_suggested_tools, error`) reasserted. Spec 02 closed shape contradicts. |
| F19 | vision/agentic/COLUMN.md:76 | MED | L2 | Handler envelope contract names four keys (`ok, data, warnings, next_suggested_tools`) — *correct vs spec 02* — but the same column's INTERFACE-TO-CONTEXT.md (F17) names six. Self-contradiction within column. |
| F20 | vision/workflow/COLUMN.md:91-115 | MED | L2 | `handoffs/envelope.yaml` declares `ok, data, warnings, artefacts_written, next_suggested_tools` (no `error`, no `next_suggested_tools` required) and lists `artefacts_written` as a wire field. Spec 02 closes the wire shape; overflow goes through `data.artefact_ref`. The local envelope is the schema-drift risk that vision/workflow/REVIEW-OF-CONTEXT.md:18 already flagged. |
| F21 | vision/agentic/COLUMN.md:98-101 | HIGH | L1, L2 | "Verb: `dispatch_skill` (or `mcp__workflow_dispatch`)… Envelope MUST specify `{row, phase, context_refs}`." Three problems: (a) `mcp__workflow_dispatch` is not a four-verb tool (spec 06); (b) `phase` not `phase_id` — schema name drift vs spec 09 §4.2; (c) "context_refs" payload contradicts the `workflow-dispatch.schema.json` shape `{row, phase_id, inputs}` in spec 09 §4.2. |
| F22 | vision/agentic/COLUMN.md:100 | MED | L2 | "writes a `DispatchedTo` edge in the graph" — handler-side write. Spec 09 §3.7 makes graph edges PostToolUse `ingest` responsibility. Same as F06. |
| F23 | vision/workflow/COLUMN.md:117-128 | HIGH | L1, L2 | "Dispatch Contract" names verb `start_phase` (or `resume_phase`) with args `{phase_id, envelope}`. Spec 09 §3.4 / §3.5 names the canonical verb `mcp__<row>_start` with args `{row, phase, inputs}` (or `phase_id`). Bare verb naming + arg drift. |
| F24 | vision/context/COLUMN.md:9 | LOW | L2 | "context-cell.schema.json" cited as the layout enforcer; spec 09 §3.8 amends it to add a closed `watcher` block. COLUMN.md does not mention watchers. (Future addition; flag only.) |
| F25 | vision/context/COLUMN.md:80-85 | MED | L2 | Schema `$id` URI scheme `tag:agency-system.local,2026:schema:<row>/<name>` — spec 09 §4.2/§4.4/§4.5 uses `https://agency-system.dev/schemas/<path>`. Two schema-identifier conventions in canon. |
| F26 | vision/workflow/META-WORKFLOW.md:50 | MED | L2 | Scaffold verb shown as `scaffold("podcast")` with no row/phase wire. Spec 09 §3.4 routes through `mcp__call_tool("mcp__workflow_start", …)`. Same shape drift as F05. |
| F27 | vision/workflow/META-WORKFLOW.md:33-39 | LOW | L1 | Template names `agentic-cell.template.md`, `workflow-cell-manifest.template.toml`, etc. Sibling context-side INTERFACE-TO-WORKFLOW.md:13-16 uses `agentic-cell.jinja`, `workflow-cell.jinja`, `context-cell.jinja`. Pure filename drift across siblings. |
| F28 | vision/agentic/REVIEW-OF-WORKFLOW.md:21,25 | HIGH | L3 | Critique "`audit_trail` injection into the core `ToolResult` payload" — spec 09 §3 / §4 closes the envelope at four keys and routes audit data through PostToolUse `ingest`. The critique is now *resolved* by spec 09; the file still presents it as an open conflict. Stale. |
| F29 | vision/agentic/REVIEW-OF-WORKFLOW.md:26 | HIGH | L3 | "`execute_pipeline()`: forces agentic to read and interpret workflow gate state" — spec 09 §3.2/§3.4 makes `execute_pipeline` the in-process callable backing `mcp__call_tool("mcp__<row>_start", …)`. The walker (workflow/_runner) interprets gates, not agentic. Critique now obsolete. |
| F30 | vision/agentic/REVIEW-OF-WORKFLOW.md:27 | MED | L3 | `handoffs/envelope.yaml` duplicates `ToolResult` — spec 09 §3 + spec 02 pin the wire shape. Critique still valid: workflow/COLUMN.md:91 still ships the duplicate (F20). Confirm the fix in COLUMN.md, not the review. |
| F31 | vision/agentic/REVIEW-OF-CONTEXT.md:23 | HIGH | L3 | "ToolResult Envelope Ownership… dual-master syndrome" — spec 09 §3 + spec 02 pin context as schema owner; FastMCP envelope is not redefined here. Critique was the right call at MVP-era but spec 09 resolves the ownership. Stale. |
| F32 | vision/agentic/REVIEW-OF-CONTEXT.md:24 | HIGH | L3 | "Hook Implementation Burden… violates separation of concerns" — spec 09 §3.7 puts hook bodies in context-row code wrapped *by* the agentic bootloader. The critique inverts the actual ownership in spec 09 §3.7 + TBD-3. Stale. |
| F33 | vision/agentic/REVIEW-OF-CONTEXT.md:25 | HIGH | L3 | "Graph Edge Writing: agentic handlers are required to explicitly call `write_edge`. This contradicts the PostToolUse auto-ingest hook paradigm." — Spec 09 §3.7 + TBD-3 confirms PostToolUse is the single write path. Critique still valid against the *current INTERFACE-TO-AGENTIC.md text* (F11), but the resolution is to fix the interface file, not record an unresolved conflict. |
| F34 | vision/workflow/REVIEW-OF-AGENTIC.md:13 | MED | L3 | "Returning a synchronous `ToolResult` for a multi-phase workflow is impossible…" — spec 09 §3.5 explicitly fixes synchronous (`wait=True`) chaining as the v0 contract; `wait=False` is in §6 out-of-scope. Critique still valid as a friction note but spec 09 has *picked* the answer. Re-state as resolved-with-tradeoff, not as open conflict. |
| F35 | vision/workflow/REVIEW-OF-AGENTIC.md:18 | HIGH | L3 | "control-flow cycle: Agentic → Workflow (`execute_pipeline`) → Agentic (`dispatch_skill`)" — spec 09 §3.2 cycle guard (`workflow_dispatch_depth ≤ 3`, error code `WORKFLOW_DISPATCH_CYCLE`) directly answers this. Stale. |
| F36 | vision/workflow/REVIEW-OF-CONTEXT.md:22 | HIGH | L3 | "Graph Edge Emission Ownership: workflow's execution is deferred to agentic handlers" — spec 09 §3.6/§3.7 puts edges in the PostToolUse ingest path that the bootloader wraps around every tool, regardless of column. Stale. |
| F37 | vision/workflow/REVIEW-OF-CONTEXT.md:23 | HIGH | L3 | "Envelope Schema Rigidity… limits workflow's ability to embed opaque continuation state" — spec 04 + spec 09 §3.5 + §4.7 introduce `Continuation` graph nodes + `previous_continuation_id` pointer. Resolved. |
| F38 | vision/context/REVIEW-OF-AGENTIC.md:11 | HIGH | L3 | "Agentic commits to writing explicit edges (`DispatchedTo`, `InvokedTool`, `GeneratedArtefact`)" — characterised as a "huge win for Context". Spec 09 §3.7 / TBD-3 *removes* handler-side edge writes. The agreement praised here is now exactly the contract spec 09 outlaws. Stale. |
| F39 | vision/context/REVIEW-OF-WORKFLOW.md:18 | MED | L3 | "Workflow defines `handoffs/envelope.yaml` locally… Context must assert that the workflow handoff MUST reference the central schema" — still valid; spec 09 §3 closes the envelope and disallows local redefinition. Acknowledge as still-actionable in the review. |
| F40 | vision/agentic/Vision.md:51-53 | LOW | L2 | "Workflow extensions… occur *inside* the arbitrary `data` dict" — directionally correct but says nothing about `data.workflow_dispatch` (spec 09 §3.2/§4.2). Vision is silent on the new shared schema. |
| F41 | vision/workflow/INTEGRATED-DRAFT.md:24-30 | HIGH | L2 | `PhaseStateEnvelope` with `status: Literal["running", "blocked_on_gate", "completed"]`. Spec 04 (cited by spec 09 §3) has `status` enum that includes `failed`, `blocked_on_user`, `completed`, etc. Status enum drift. |
| F42 | vision/workflow/INTEGRATED-DRAFT.md:34 | HIGH | L2 | "Workflow's Gates emit the `SATISFIES_PHASE` edge ONLY when the gate evaluates `ok: true`." Spec 09 §3.6 names the gate's return shape as `{ok, message}` only — no edge emission inside the evaluator. Same drift as F12. |
| F43 | vision/context/INTEGRATED-DRAFT.md:22-24 | MED | L2 | Sidecar Metadata Pattern (`.meta/<file>.meta.json`) — spec 09 §3 routes overflow through `data.artefact_ref` → `Artefact` node, not via filesystem sidecars. Two different overflow models. |
| F44 | vision/agentic/INTEGRATED-DRAFT.md:33 | MED | L2 | "central FastMCP server wrapper… registers middleware hooks provided by `context`. agentic yields standard metadata; the hook maps it to the graph." Closer to spec 09 §3.7 than other files but uses a different hook-registration model (`@mcp.tool(..., context_edges=[...])` decorator at line 33). Spec 09 §3.7 uses `make_hooked_wrapper` at boot — no per-tool decorator. |
| F45 | vision/workflow/INTEGRATED-DRAFT.md:67-68 | LOW | L2 | Open questions "Handoff Interruption", "Graph Transactionality" — spec 09 §3.5 closes the first (Continuation node persistence); spec 09 §7 DSA #4 punts on the second (compensating-transaction rollback deferred). Replace open-question framing with resolved/deferred status. |
| F46 | vision/agentic/COLUMN.md:81-83 | LOW | L2 | Routing skill lives at `agentic/_router/`. Spec 09 §3.3 names anchor triad `mcp__context_query/_describe/_read` for context queries — but does not contradict the router location. Compatible; flag as needing reconciliation in INTERFACE-TO-CONTEXT.md to point `/agency` at the triad rather than `query_graph`. |
| F47 | vision/context/ONTOLOGY.md:39-42 | HIGH | L2 | Edge canon lists `DISPATCHES`, `USES_SCHEMA`, `USES_TEMPLATE`, `SUPERSEDES`, `PRODUCED_LESSON`. Spec 09 §3.7-§3.9 + spec 08-v1 names `PRECEDES`, `DERIVED_FROM`, `DISPATCHED_TO`, `INVOKED_TOOL` (note tense + name). Edge-name drift between context-canon and spec-canon. |
| F48 | vision/context/Vision.md:43-44 | MED | L2 | Edge list `CONTAINS, ADJACENT_TO, PREREQUISITE_OF, USES_TEMPLATE, USES_SCHEMA, SATISFIES_PHASE`. Same drift as F47 + F12. |
| F49 | vision/workflow/GHERKIN-OWNED.md:30-36 | LOW | L2 | Isomorphism gherkin still lists `handoffs/` as a canonical directory; if `handoffs/envelope.yaml` is to be replaced by `_shared/workflow-dispatch.schema.json` (F20 + F30), this gherkin needs alignment. |
| F50 | vision/agentic/GHERKIN-OWNED.md:42 | MED | L1 | "the payload strictly conforms to `{row, phase, context_refs}`" — matches F21 not spec 09 §4.2 (`{row, phase_id, inputs}`). |

50 findings: HIGH 22, MED 21, LOW 7.

## §2 Lens 1 — Cross-Column Interface Mismatches

Sibling `INTERFACE-TO-*` files must agree.

### 2.1 `dispatch_skill` signature triangulation

Three different signatures across siblings:

- `vision/agentic/INTERFACE-TO-WORKFLOW.md:19`  
  `dispatch_skill(skill_id: str, args: dict) -> ToolResult`
- `vision/workflow/INTERFACE-TO-AGENTIC.md:41`  
  `dispatch_skill(skill_id: str, args: dict) -> ToolResult` (consistent with above)
- `vision/agentic/INTERFACES.md:21`  
  `dispatch_skill(row: str, phase: str, context_refs: list[str]) -> ToolResult` (workflow-dispatch payload smuggled into skill verb)
- `vision/agentic/COLUMN.md:98`  
  Verb `dispatch_skill (or mcp__workflow_dispatch)` with payload `{row, phase, context_refs}`

**Spec 09 sides with**: `dispatch_skill(row: str, skill_slug: str, context_refs: list[str])` per §3.1 (the `mcp__dispatch_skill` four-verb form, schema at `vision/specs/schemas/agentic/four-verb/dispatch-skill-request.schema.json`).

Workflow-dispatch payloads (`{row, phase_id, inputs}`) live in `data.workflow_dispatch` per §3.2 + §4.2 — a different mechanism, not a `dispatch_skill` overload.

### 2.2 `execute_pipeline` — surface or behind-the-curtain?

- `vision/agentic/INTERFACE-TO-WORKFLOW.md:33-36` requires it as a workflow-exposed callable.
- `vision/workflow/INTERFACE-TO-AGENTIC.md:42` mirrors that as "uniform entry point".
- Both are silent on the four-verb wrapping.

**Spec 09 sides with**: `execute_pipeline` is the in-process callable behind `mcp__call_tool("mcp__<row>_start", …)` per §9 reconciliation table row 1. Neither sibling says so — both need a one-line clarification.

### 2.3 Four-verb naming

- `vision/agentic/INTERFACE-TO-WORKFLOW.md:14-19` — bare `list_tools, call_tool, list_skills, dispatch_skill`.
- `vision/workflow/INTERFACES.md:30-31` — same bare form.
- `vision/agentic/Vision.md:69` — same bare form.

**Spec 09 sides with**: `mcp__list_tools / mcp__call_tool / mcp__list_skills / mcp__dispatch_skill` per §3.1 anchored to `vision/specs/schemas/agentic/four-verb/*.schema.json`. The namespace prefix is load-bearing because §3.2/§3.5 rely on `mcp__<row>_start` discrimination.

### 2.4 Graph write authority

- `vision/workflow/INTERFACE-TO-AGENTIC.md:43-44` — "agentic must record the `DispatchedTo` edge" (handler-side).
- `vision/context/INTERFACE-TO-AGENTIC.md:26` — "agentic handlers MUST explicitly call `write_edge(...)`".
- `vision/agentic/INTEGRATED-DRAFT.md:32` — "agentic does NOT manually write graph edges in its handlers… `context_edges` decorator".

**Spec 09 sides with**: PostToolUse `ingest` is the single write path (§3.7, TBD-3). `make_hooked_wrapper` at boot — no per-tool decorator, no handler-level `write_edge`. The agentic INTEGRATED-DRAFT is closest to right but uses the wrong wrapper-registration mechanism.

### 2.5 Context query surface

- `vision/context/INTERFACE-TO-AGENTIC.md:9` — `query_graph(cypher) -> list[dict]` as a direct callable.
- `vision/agentic/INTERFACE-TO-CONTEXT.md:50-52` — same shape `query_graph(query) -> list[dict]`.
- `vision/agentic/INTERFACES.md:42` — `write_edge` direct callable.

**Spec 09 sides with**: `mcp__context_query / _describe / _read` four-verb-wrapped anchor triad per §3.3; direct `query_graph` from agentic-row modules is exactly what the §3.3 `test_no_direct_store_imports` lint forbids (acceptance scenario at line 840 of spec 09).

### 2.6 Envelope shape

- `vision/agentic/COLUMN.md:76` — 4 keys (`ok, data, warnings, next_suggested_tools`). Correct.
- `vision/agentic/INTERFACE-TO-CONTEXT.md:15` — 6 keys (adds `artefacts_written`, `error`). Wrong.
- `vision/context/INTERFACES.md:22` — same 6-key shape. Wrong.
- `vision/workflow/COLUMN.md:91-115` — 5 keys including `artefacts_written`. Wrong.

**Spec 09 sides with**: spec 02 closed 4-key shape (`ok, data, warnings, next_suggested_tools`); overflow via `data.artefact_ref` (§3 bullet 3, §4.1, §4.7).

### 2.7 Storage-path resolver name

- `vision/context/INTERFACE-TO-WORKFLOW.md:17` — `get_storage_path(row, vault)`.
- `vision/agentic/INTERFACE-TO-CONTEXT.md:44` — `get_vault_path(row, vault_type)`.

Spec 09 doesn't pin the resolver name (out-of-scope) but the cross-sibling drift will block any wave that wires storage.

## §3 Lens 2 — Per-Column Claims vs Spec 09 r2 (per cell)

For each of the 9 cells, files that name a contradictory mechanism.

### 3.1 agentic → agentic (spec 09 §3.1: four-verb re-entry through `mcp__call_tool` / `mcp__dispatch_skill`)

- `vision/agentic/INTERFACES.md:21` (F02) — wrong `dispatch_skill` signature.
- `vision/agentic/INTERFACE-TO-WORKFLOW.md:14-20` (F04) — bare-verb naming.

### 3.2 agentic → workflow (spec 09 §3.2: `data.workflow_dispatch` triple → harness re-emits via `mcp__call_tool("mcp__<row>_start", …)`)

- `vision/agentic/INTERFACE-TO-WORKFLOW.md:31-36` (F03) — names `execute_pipeline` as surface; silent on wrapping.
- `vision/agentic/COLUMN.md:98-101` (F21) — names verb `dispatch_skill` or `mcp__workflow_dispatch`; payload `{row, phase, context_refs}` — wrong shape vs `_shared/workflow-dispatch.schema.json`.
- `vision/agentic/Vision.md:51-53` (F40) — silent on the new dispatch slot.
- `vision/workflow/INTEGRATED-DRAFT.md:24-30` (F41) — wrong `PhaseStateEnvelope` status enum.

### 3.3 agentic → context (spec 09 §3.3: anchor triad `mcp__context_query/_describe/_read`)

- `vision/context/INTERFACE-TO-AGENTIC.md:9` (F09) — names raw `query_graph(cypher)`.
- `vision/agentic/INTERFACE-TO-CONTEXT.md:50-52` (Lens 1 §2.5) — mirrors the raw form.
- `vision/agentic/INTERFACES.md:42` — direct `write_edge`.

### 3.4 workflow → agentic — BUILT (spec 09 §3.4: `_walk_phase` via `CellRegistry`)

- `vision/workflow/INTERFACE-TO-AGENTIC.md:42` (F03) — names `execute_pipeline` as agentic-required, silent on cell-registry routing.
- `vision/workflow/COLUMN.md:117-128` (F23) — names verb `start_phase`/`resume_phase`, not `mcp__<row>_start`.

### 3.5 workflow → workflow (spec 09 §3.5: `PRECEDES` traversal (chain=True) + `data.workflow_dispatch` for inter-row)

- `vision/workflow/COLUMN.md:117-128` (F23) — names `start_phase`/`resume_phase`; no `chain` parameter, no `PRECEDES`.
- `vision/workflow/META-WORKFLOW.md:50` (F26) — `scaffold("podcast")` direct verb.
- All workflow files are silent on the cycle guard (`workflow_dispatch_depth ≤ 3`) and the `Continuation` node + `previous_continuation_id` composition pattern.

### 3.6 workflow → context — BUILT (spec 09 §3.6: gate evaluator returns `{ok, message}`; Cypher via `Store.query`)

- `vision/workflow/INTEGRATED-DRAFT.md:34` (F42) — claims gate emits `SATISFIES_PHASE` edge (spec 09 says no edge in evaluator).
- `vision/workflow/INTERFACE-TO-CONTEXT.md:24` (F12) — names `Artefact -> SATISFIES_PHASE -> Phase` as required emission; `SATISFIES_PHASE` not in spec-canon edges.
- Stale edge canon: `SUPERSEDES`, `SATISFIES_PHASE` (F47, F48).

### 3.7 context → agentic — BUILT (spec 09 §3.7: hook chain via `make_hooked_wrapper`; PreToolUse may veto, PostToolUse may not)

- `vision/context/INTERFACE-TO-AGENTIC.md:23-26` (F11) — moves `validate_frontmatter` and `ingest_node` execution to agentic. Spec 09 puts the bodies in context-row code, wrapped *around* tools by the bootloader.
- `vision/agentic/INTERFACE-TO-CONTEXT.md:19-22` (F17 adj) — `execute_with_hooks(tool_name, args, pre_hooks, post_hooks)` is a different hook-execution model than `make_hooked_wrapper`.
- `vision/agentic/INTEGRATED-DRAFT.md:33` (F44) — decorator-based hooks; spec 09 uses boot-time wrapping.
- No file names PostToolUse's lack of veto authority (spec 09 §3.7 TBD-5 explicitly).

### 3.8 context → workflow (spec 09 §3.8: `[watcher]` block in `context-cell.schema.json`; emission via `mcp__call_tool("mcp__<row>_start", …)`; `WatcherEmission` + `WatcherHealth` nodes)

- No per-column file mentions watchers at all (spec 09 acknowledges this is forward-looking — closes panel ORR #7).
- `vision/context/COLUMN.md` is silent (F24).
- `vision/context/ONTOLOGY.md` does not list `WatcherEmission` / `WatcherHealth` node types.

### 3.9 context → context (spec 09 §3.9: intra-row `$ref` + `_shared/`; `DERIVED_FROM` edges in PostToolUse; cross-row `$ref` rejected)

- `vision/context/ONTOLOGY.md:39-42` (F47) — edge canon missing `DERIVED_FROM` for `Artefact -> Artefact`; uses `DERIVED_FROM` only for "rendered output Artefact -> Source Artefact".
- No file mentions the cross-row `$ref` rejection (`CROSS_ROW_REF` error code).

## §4 Lens 3 — Stale Critiques in REVIEW-OF-* Files

Critiques spec 09 r2 has answered (now stale):

| Review file:line | Critique | Spec 09 resolution | Verdict |
|---|---|---|---|
| vision/agentic/REVIEW-OF-WORKFLOW.md:21,25 (F28) | `audit_trail` injection into envelope | §3 + §4 close envelope; audit data lives in PostToolUse `ingest` log | STALE — fix or strike |
| vision/agentic/REVIEW-OF-WORKFLOW.md:26 (F29) | `execute_pipeline` forces agentic to interpret gates | §3.2/§3.4 `execute_pipeline` is in-process callable; walker (workflow side) interprets gates | STALE |
| vision/agentic/REVIEW-OF-WORKFLOW.md:27 (F30) | `handoffs/envelope.yaml` duplicates `ToolResult` | Spec 02 closed shape pins it | STILL VALID, but the fix belongs in workflow/COLUMN.md (F20), not in a review |
| vision/agentic/REVIEW-OF-CONTEXT.md:23 (F31) | "ToolResult Envelope Ownership — dual-master syndrome" | §3 + spec 02: context owns envelope, FastMCP doesn't redefine it | STALE |
| vision/agentic/REVIEW-OF-CONTEXT.md:24 (F32) | "Hook Implementation Burden violates separation of concerns" | §3.7 wraps hooks at boot in agentic bootloader around context-supplied logic | STALE |
| vision/agentic/REVIEW-OF-CONTEXT.md:25 (F33) | "Graph Edge Writing contradicts PostToolUse auto-ingest" | §3.7 + TBD-3 — agreed, PostToolUse is the single path | STILL VALID against current INTERFACE-TO-AGENTIC.md text (F11); fix the interface |
| vision/workflow/REVIEW-OF-AGENTIC.md:13 (F34) | Sync `ToolResult` impossible for multi-phase | §3.5 picks synchronous (`wait=True`) v0; `wait=False` deferred §6 | STALE (resolved-with-tradeoff) |
| vision/workflow/REVIEW-OF-AGENTIC.md:18,21-23 (F35) | "control-flow cycle Agentic → Workflow → Agentic" | §3.2 cycle guard `workflow_dispatch_depth ≤ 3` + `WORKFLOW_DISPATCH_CYCLE` | STALE |
| vision/workflow/REVIEW-OF-CONTEXT.md:22 (F36) | "Graph Edge Emission Ownership: workflow vs agentic" | §3.6/§3.7 puts emission in PostToolUse `ingest` for either column | STALE |
| vision/workflow/REVIEW-OF-CONTEXT.md:23 (F37) | "Envelope Schema Rigidity limits opaque continuation state" | §3.5 `Continuation` node + §4.7 `previous_continuation_id` | STALE |
| vision/workflow/REVIEW-OF-CONTEXT.md:24 | "Templates static vs progressive disclosure needed" | Not addressed by spec 09 (orthogonal) | STILL VALID |
| vision/context/REVIEW-OF-AGENTIC.md:11 (F38) | Praises handler-side edge writes as "a huge win" | §3.7 / TBD-3 outlaws them | STALE + INVERTED |
| vision/context/REVIEW-OF-WORKFLOW.md:18 (F39) | Local `handoffs/envelope.yaml` redefinition | §3 closes envelope; still actionable | STILL VALID — push to workflow/COLUMN.md fix |

## §5 Per-File Verdict

| File | Verdict |
|---|---|
| vision/agentic/BRIEF.md | aligned (informational; pre-spec-09 framing OK) |
| vision/agentic/COLUMN.md | needs-touch (3 findings — F19 self-contradiction, F21 dispatch verb, F22 write_edge) |
| vision/agentic/GHERKIN-OWNED.md | needs-touch (2 findings — F50 + cross-row payload shape) |
| vision/agentic/INTEGRATED-DRAFT.md | needs-touch (2 findings — F40, F44; closer to right than peers) |
| vision/agentic/INTERFACE-TO-CONTEXT.md | needs-touch (3 findings — F17 envelope, hook model, query route) |
| vision/agentic/INTERFACE-TO-WORKFLOW.md | needs-touch (4 findings — F01, F03, F04, F05) |
| vision/agentic/INTERFACES.md | needs-touch (3 findings — F02 dispatch sig, F03, four-verb name) |
| vision/agentic/RESEARCH-PATTERNS.md | aligned (research/inventory only; pre-spec content) |
| vision/agentic/REVIEW-OF-CONTEXT.md | superseded (F31, F32 stale; F33 still actionable but in wrong file) |
| vision/agentic/REVIEW-OF-WORKFLOW.md | superseded (F28, F29 stale; F30 still actionable but in wrong file) |
| vision/agentic/ROW-EXAMPLES.md | aligned (concrete row-level examples; no mechanism contradictions surfaced) |
| vision/agentic/Vision.md | needs-touch (1 finding — F40; otherwise close) |
| vision/workflow/BRIEF.md | aligned (pre-spec) |
| vision/workflow/COLUMN.md | needs-touch (3 findings — F20 envelope, F23 verb, F30/F39 confirm) |
| vision/workflow/GHERKIN-OWNED.md | needs-touch (1 finding — F49 isomorphism shape) |
| vision/workflow/INTEGRATED-DRAFT.md | needs-touch (3 findings — F41 status enum, F42 gate edge, F45 open questions) |
| vision/workflow/INTERFACE-TO-AGENTIC.md | inconsistent-self-contradicts + needs-touch (4 findings — F06 write_edge, F07 audit_trail, F08 four-verb, F03) |
| vision/workflow/INTERFACE-TO-CONTEXT.md | needs-touch (3 findings — F13 audit_trail, F14 SUPERSEDES, F15 pandoc) |
| vision/workflow/INTERFACES.md | needs-touch (2 findings — F08, four-verb) |
| vision/workflow/META-WORKFLOW.md | needs-touch (2 findings — F26 scaffold verb, F27 template names) |
| vision/workflow/RESEARCH-PATTERNS.md | aligned (research only) |
| vision/workflow/REVIEW-OF-AGENTIC.md | superseded (F34, F35 stale) |
| vision/workflow/REVIEW-OF-CONTEXT.md | superseded (F36, F37 stale; F39 still valid for COLUMN.md) |
| vision/workflow/ROW-EXAMPLES.md | aligned (examples; verb-drift inherited from COLUMN.md only) |
| vision/workflow/VISION.md | needs-touch (2 findings — F41 carried, status enum + no chain/Continuation mention) |
| vision/context/BRIEF.md | aligned (pre-spec) |
| vision/context/COLUMN.md | needs-touch (2 findings — F24 watchers, F25 $id scheme) |
| vision/context/GHERKIN-OWNED.md | needs-touch (1 finding — six-key envelope at line 14) |
| vision/context/INTEGRATED-DRAFT.md | needs-touch (1 finding — F43 sidecar vs artefact_ref) |
| vision/context/INTERFACE-TO-AGENTIC.md | inconsistent-self-contradicts + needs-touch (3 findings — F09 query_graph, F10 envelope tag, F11 hook authority) |
| vision/context/INTERFACE-TO-WORKFLOW.md | needs-touch (2 findings — F12 SATISFIES_PHASE, F16 resolver name) |
| vision/context/INTERFACES.md | needs-touch (1 finding — F18 envelope shape) |
| vision/context/ONTOLOGY.md | needs-touch (1 finding — F47 edge canon drift) |
| vision/context/RESEARCH-PATTERNS.md | aligned (research only) |
| vision/context/REVIEW-OF-AGENTIC.md | superseded (F38 stale + inverted) |
| vision/context/REVIEW-OF-WORKFLOW.md | aligned-mostly (F39 still valid) |
| vision/context/ROW-EXAMPLES.md | aligned |
| vision/context/Vision.md | needs-touch (1 finding — F48 edge canon) |

Tally: aligned 12, needs-touch 18, superseded 5, inconsistent-self-contradicts 2 (one is also needs-touch), aligned-mostly 1. (Counts row each file once; the two `inconsistent` files are double-tagged with needs-touch.)

## §6 Headline Blockers for Landing Spec 09

Top 5 things in the per-column canon that must be fixed before Wave A.

1. **Envelope shape canon — collapse to spec-02 four keys everywhere.**  
   `vision/agentic/INTERFACE-TO-CONTEXT.md:15`, `vision/context/INTERFACES.md:22`, `vision/workflow/COLUMN.md:91-115` and the workflow review/integrated chain all carry six-key (`+artefacts_written, +error`) or five-key shapes. Spec 09 §3 + §4.1 anchor on the closed 4-key shape with `data.artefact_ref` for overflow. Until these three files match, every cross-column wire description is ambiguous.

2. **`dispatch_skill` signature collision (three forms in three files).**  
   `vision/agentic/INTERFACE-TO-WORKFLOW.md:19` and `vision/workflow/INTERFACE-TO-AGENTIC.md:41` say `(skill_id, args)`. `vision/agentic/INTERFACES.md:21` says `(row, phase, context_refs)`. `vision/agentic/COLUMN.md:98` adds `mcp__workflow_dispatch` and `{row, phase, context_refs}`. Spec 09 §3.1 pins `(row, skill_slug, context_refs)`; workflow-dispatch is a separate `data.workflow_dispatch` triple per §3.2/§4.2. The three files must converge.

3. **Graph-write authority — `write_edge` in agentic handlers is dead per spec 09.**  
   `vision/workflow/INTERFACE-TO-AGENTIC.md:43-44`, `vision/context/INTERFACE-TO-AGENTIC.md:26`, `vision/agentic/COLUMN.md:100`, and (perversely) `vision/context/REVIEW-OF-AGENTIC.md:11` (which praises the deprecated pattern) still require handler-side `write_edge`. Spec 09 §3.7 + TBD-3 puts all graph writes in the PostToolUse `ingest` flow wrapped by `make_hooked_wrapper`. Wave A cannot start while four files still demand the opposite contract.

4. **Edge-canon drift (`SATISFIES_PHASE`, `SUPERSEDES`, `DISPATCHES` vs spec-08-v1 / spec 09).**  
   `vision/context/ONTOLOGY.md:39-42`, `vision/context/Vision.md:43-44`, `vision/context/INTERFACE-TO-WORKFLOW.md:24`, `vision/workflow/INTERFACE-TO-CONTEXT.md:37`, `vision/workflow/INTEGRATED-DRAFT.md:34`. Spec 09 §3.6/§3.7/§3.9 + spec 08-v1 use `PRECEDES`, `DERIVED_FROM`, `DISPATCHED_TO`, `INVOKED_TOOL`. The drift drags `SATISFIES_PHASE`-emission contracts that have no implementation target.

5. **Four-verb naming — bare `call_tool` vs `mcp__call_tool`.**  
   `vision/agentic/INTERFACE-TO-WORKFLOW.md:14-19`, `vision/workflow/INTERFACES.md:30-31`, `vision/agentic/Vision.md:69`, and the agentic INTEGRATED-DRAFT all use the bare form. Spec 09 §3.1/§3.2/§3.4/§3.5 is anchored on `mcp__call_tool("mcp__<row>_start", …)`. The `mcp__` prefix is load-bearing because §3.2/§3.5 dispatch by tool name — fail to fix this and every spec-09 acceptance scenario reads as referring to something that doesn't exist in the per-column canon.
