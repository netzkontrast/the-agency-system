---
slug: vision-audit-specs
type: audit
status: ready
owner: claude
created: 2026-05-20
updated: 2026-05-20
summary: Findings from the post-spec-09-r2 audit of vision/specs/ — contradictions, schema drift, and composition gaps that block spec 09 from landing cleanly across the existing corpus.
audited:
  - vision/specs/01-cell-manifest.md
  - vision/specs/02-tool-result-envelope.md
  - vision/specs/03-sidecar-metadata.md
  - vision/specs/04-phase-state-envelope.md
  - vision/specs/05-gate-yaml.md
  - vision/specs/06-agentic-base.md
  - vision/specs/07-workflow-base-v1.md
  - vision/specs/07-workflow-base.md
  - vision/specs/08-context-base-v1.md
  - vision/specs/08-context-base.md
  - vision/specs/schemas/**
---

# Vision Spec Corpus — Post-Spec-09-r2 Audit

Anchor for this audit: `vision/specs/09-crossover-matrix.md` (r2). The
audit asks one question of every other file: **can spec 09 land here
without breaking, contradicting, or silently colliding with what is
written?** Three lenses applied sequentially: (1) spec-to-spec
contradiction, (2) spec-to-schema drift (schema wins, L06), (3) spec-09
composition gaps (which existing files must be touched to acknowledge
r2's new fields, nodes, mechanisms).

Spec 09 itself was not audited as a target — only flagged where r2
contradicts itself.

## §1. Index of findings

| # | file:line | severity | lens | one-line |
|---|---|---|---|---|
| F01 | `09-crossover-matrix.md:106` vs `06-agentic-base.md:108` | BLOCKER | 1 | spec 09 calls `mcp__dispatch_skill(row, skill_slug, context_refs)`; spec 06 declares `dispatch_skill(name, args)` |
| F02 | `09-crossover-matrix.md:182` vs `schemas/agentic/four-verb/dispatch-skill-request.schema.json:7-22` | IMPORTANT | 2 | spec 09 example aligns with schema, but `additionalProperties: false` forbids `context_refs=[]` extensions implicit in r2 worked examples (passes today, future-fragile) |
| F03 | `09-crossover-matrix.md:204-210` vs `02-tool-result-envelope.md:36` | BLOCKER | 1 | spec 09 says outer envelope's `data` IS an inner `PhaseStateEnvelope`; spec 02 mandates `data: {type: object}` (open object), but spec 02 schema is closed at root only — the wrapping semantics work but the spec needs to acknowledge that `PhaseStateEnvelope` becomes a `data` payload, not a wire-level alternative |
| F04 | `09-crossover-matrix.md:108` vs `schemas/agentic/interface-to-context.schema.json:9-11` | BLOCKER | 2 | spec 09 names anchor triad `mcp__context_query` / `_describe` / `_read`; agentic→context interface schema's `action` enum is `[query, upsert_node, upsert_edge]` — neither `describe` nor `read` exists |
| F05 | `09-crossover-matrix.md:108` vs `schemas/agentic/interface-to-context.schema.json:9-11` | BLOCKER | 3 | spec 09 forbids direct `upsert_node` / `upsert_edge` from agentic skills (graph writes are PostToolUse-only), but interface-to-context.schema.json still enumerates them as actions |
| F06 | `09-crossover-matrix.md:222-229` vs `schemas/context/nodes/session.schema.json:10-17` | BLOCKER | 3 | spec 09 §4.3 adds `workflow_dispatch_depth` to Session.payload; the schema has neither `additionalProperties:false` nor this property declared — adoption requires editing the file |
| F07 | `09-crossover-matrix.md:345-347` vs `schemas/context/nodes/continuation.schema.json:11-18` | BLOCKER | 3 | spec 09 §3.5 uses `previous_continuation_id` and assumes Continuation carries the full envelope; current Continuation payload has only `{session_id, phase_id, opaque_state}` — no `envelope` slot, no `created_at_epoch` |
| F08 | `07-workflow-base-v1.md:262-275` vs `schemas/context/nodes/continuation.schema.json:11-18` | BLOCKER | 2 | spec 07-v1 FR4 writes `envelope`, `created_at_epoch` into Continuation payload; the schema does not declare either field. Spec-side and schema disagree on what a Continuation actually carries |
| F09 | `07-workflow-base-v1.md:135-141` vs `schemas/context/nodes/phase.schema.json:11-20` | BLOCKER | 2 | spec 07-v1 FR2 declares Phase payload `{row, phase_id, body_ref, lazy_created}`; the schema declares `{row, phase_id, name, status, blocked_on_gate}` and requires `status` — no overlap on `body_ref`/`lazy_created`, schema demands `status` the v1 spec never sets |
| F10 | `04-phase-state-envelope.md:55-65` vs `02-tool-result-envelope.md:36` | BLOCKER | 1 | spec 04 JSON Schema requires `blocked_reason` and `resume_token` as required keys (allowing `null`); spec 09 §3.5 acceptance scenarios produce `completed`/`failed` envelopes without these being set per branch — non-null requirement is mismatched with §3.5's "completed" path |
| F11 | `04-phase-state-envelope.md:21` vs `07-workflow-base-v1.md:60-61` | IMPORTANT | 1 | spec 04 STATUS says "file-on-disk format SUPERSEDED" but spec 04 §Serialization rules (lines 71-79) still document file paths, atomic rename, TTL sweep against files — the body of the spec contradicts its STATUS banner |
| F12 | `04-phase-state-envelope.md:163-183` vs `07-workflow-base-v1.md:347-372` | IMPORTANT | 1 | spec 04 acceptance criteria assert file-based serialization (`workflow/_state/...json`, `.tmp` artifacts), spec 07-v1 TTL sweep operates on graph nodes; the acceptance criteria still anchor on the dead path |
| F13 | `03-sidecar-metadata.md:22-32` (DEPRECATED banner) vs `03-sidecar-metadata.md:36-209` | IMPORTANT | 1 | spec 03 declares "DEPRECATED — file-on-disk format is retired"; the body keeps describing the file pattern + filesystem layout + acceptance scenarios as if live. The DEPRECATED warning is the only signal. Acceptable as archeology but inconsistent self-state. |
| F14 | `03-sidecar-metadata.md:88-97` vs `schemas/context/nodes/artefact.schema.json:11-25` | BLOCKER | 2 | spec 03 declares `produced_by` as object `{skill, phase, session_id}`; artefact schema declares `produced_by: {type: string}` — incompatible types |
| F15 | `08-context-base-v1.md:346-353` vs `schemas/context/nodes/artefact.schema.json:11-25` | BLOCKER | 2 | spec 08-v1 FR5 says `artifact_driver` and `driver_pointer` are OPTIONAL; artefact schema lists them in `required` — direct contradiction |
| F16 | `08-context-base-v1.md:345-348` vs `schemas/context/nodes/artefact.schema.json:11-25` | BLOCKER | 2 | spec 08-v1 FR5 requires `content_type, sha256, size_bytes, created_at, produced_by, derived_from`; artefact schema requires only `sha256, content_type, artifact_driver, driver_pointer` — `size_bytes`, `created_at`, `produced_by`, `derived_from` missing from schema's required list |
| F17 | `08-context-base-v1.md:328-336` vs `schemas/context/nodes/artefact.schema.json:11-25` | BLOCKER | 2 | spec 08-v1 FR4 introduces optional `row` field on Artefact metadata; artefact schema does not declare `row` at all |
| F18 | `01-cell-manifest.md:127` vs `schemas/agentic/tool-manifest.schema.json:8-11` | IMPORTANT | 2 | spec 01 mandates MCP tool naming `mcp__<row>_<export>` (single segment); tool-manifest schema describes `mcp__<row>_<group>_<action>` (two segments). Drift in derivation rule |
| F19 | `06-agentic-base.md:84` vs `schemas/agentic/harness-bootstrap.schema.json:12` | IMPORTANT | 2 | spec 06 FR1 fixes server name "agency-system"; harness-bootstrap schema default is "agency-mcp" |
| F20 | `02-tool-result-envelope.md:36` vs `schemas/context/hooks/posttooluse.schema.json:14-22` | BLOCKER | 2 | PostToolUse hook schema's `envelope` declares root keys including `artefacts_written` and `error` — spec 02 root is closed to exactly `{ok, data, warnings, next_suggested_tools}`; the hook schema would accept envelopes spec 02 rejects |
| F21 | `02-tool-result-envelope.md:36` vs `schemas/context/hooks/posttooluse.schema.json:20` | IMPORTANT | 2 | hook schema declares `error` at envelope root; spec 02 puts error under `data.error` |
| F22 | `09-crossover-matrix.md:325-328` vs `04-phase-state-envelope.md:36-45` | BLOCKER | 3 | spec 09 §3.5 says inter-row chain "wraps as spec-02 envelope at the four-verb boundary (the `data` of the outer envelope is the inner `PhaseStateEnvelope`)" — but spec 04 PhaseStateEnvelope already has `tool_result` (spec-02) inside it; double-wrapping vs flat-wrapping is undefined |
| F23 | `09-crossover-matrix.md:436-444` vs `schemas/context/nodes/cell.schema.json` (no watcher schema) | BLOCKER | 3 | spec 09 §3.8 names `context/_shared/schemas/context-cell.schema.json` as gaining an optional `watcher` block; this file lives in the runtime tree, not under `vision/specs/schemas/` — no vision-side schema needs editing, but the cross-tree split is not acknowledged here |
| F24 | `09-crossover-matrix.md:463-466` (WatcherEmission node) | BLOCKER | 3 | spec 09 §4.4 introduces `watcher-emission.schema.json` under `vision/specs/schemas/context/nodes/`; the file does NOT exist; `schemas/context/README.md:7-19` lists 11 node schemas, not 12+ |
| F25 | `09-crossover-matrix.md:631-660` (WatcherHealth node) | BLOCKER | 3 | spec 09 §4.5 introduces `watcher-health.schema.json` under `vision/specs/schemas/context/nodes/`; the file does NOT exist; not in README catalog |
| F26 | `09-crossover-matrix.md:548-566` (`_shared/workflow-dispatch.schema.json`) | BLOCKER | 3 | spec 09 §4.2 introduces a new shared schema at `vision/specs/schemas/_shared/workflow-dispatch.schema.json`; the `_shared/` directory does NOT exist under `vision/specs/schemas/` — neither schemas/README.md catalog nor the directory tree acknowledges it |
| F27 | `schemas/agentic/four-verb/call-tool-response.schema.json:6` | BLOCKER | 2 | `$ref` points at `../../context/_shared/schemas/tool_result.schema.json` — that path resolves outside `vision/specs/schemas/` into the runtime tree; spec 09 §3.1 cites the four-verb schemas as authoritative, but the `$ref` will not resolve from the vision-side schemas folder |
| F28 | `schemas/agentic/four-verb/dispatch-skill-response.schema.json:6` | BLOCKER | 2 | same as F27 — `$ref` jumps out of `vision/specs/schemas/` into `context/_shared/schemas/`; cross-tree `$ref` violates spec 09 §3.9 ("cross-row `$ref` forbidden"); even though this is cross-tree not cross-row, it breaks resolver portability |
| F29 | `09-crossover-matrix.md:496-500` vs `schemas/context/edges/derived-from.schema.json` | IMPORTANT | 3 | spec 09 §3.9 forbids cross-row `$ref`; derived-from schema is silent on the constraint and not referenced from a row-scoped subdir, so the rule has no anchor in the schema layer yet |
| F30 | `09-crossover-matrix.md:519-529` (corrected `$ref` example) | IMPORTANT | 3 | spec 09's worked example cites `artefact-node.schema.json#/properties/sha256` — but the vision-side `schemas/context/nodes/artefact.schema.json` is the file present here (different filename); the runtime canonical is `context/_shared/schemas/artefact-node.schema.json`. r2 conflates the two trees |
| F31 | `schemas/agentic/four-verb/` (6 files) vs `schemas/README.md:29` | IMPORTANT | 2 | schemas/README catalog lists `four-verb/{list-tools,call-tool,list-skills,dispatch-skill}-{request,response}` (8 files); the directory has 6 — no `list-tools-request` / `list-skills-request`. Spec 06 FR2 has `list_tools(row=None)` / `list_skills(row=None)` taking optional args, so the missing request schemas are real gaps |
| F32 | `schemas/agentic/interface-to-workflow.schema.json:18` vs `09-crossover-matrix.md:561` | BLOCKER | 2 | interface-to-workflow schema uses field name `phase`; spec 09 workflow-dispatch schema (§4.2) uses `phase_id`. Field name drift between the existing interface envelope and the new dispatch triple |
| F33 | `schemas/agentic/interface-to-context.schema.json:17-22` vs `schemas/context/interface-to-agentic.schema.json:13-21` | BLOCKER | 1 | upsert-node payload differs across the two sides: agentic→context uses `node: {id, type, properties}`; context→agentic uses `{id, label, payload}`. Inconsistent boundary contract |
| F34 | `schemas/context/edges/blocks.schema.json` vs `schemas/context/edges/blocked-on.schema.json` | IMPORTANT | 1 | BLOCKS (Gate→Phase) and BLOCKED_ON (Phase→Gate) describe inverse forms of the same fact. Spec 07-v1 FR3 uses `(p:Phase)-[:BLOCKS]->(g:Gate)` direction — contradicts the BLOCKS edge schema description ("a Gate blocking a Phase"). Two edges, same semantic, opposite directions |
| F35 | `07-workflow-base-v1.md:205` vs `schemas/context/edges/blocks.schema.json:5` | BLOCKER | 2 | spec 07-v1 says Phase→Gate via BLOCKS; schema declares BLOCKS as Gate→Phase. Edge direction contradicts |
| F36 | `schemas/context/nodes/skill.schema.json:22` vs `schemas/agentic/skill-frontmatter.schema.json:19` | IMPORTANT | 2 | Skill node status enum: `[proposed, ready, deprecated]`; skill-frontmatter status enum: `[draft, ready, deprecated, proposed]` — frontmatter allows `draft`, the node does not |
| F37 | `schemas/context/nodes/gate.schema.json:11-17` vs `05-gate-yaml.md:42-92` | BLOCKER | 2 | Gate-as-graph-node payload: `{name, row, satisfied}`. Gate-YAML defines: `{id, type, description, blocks_phase, evaluator, on_success, on_failure}`. Two completely different shapes of the same conceptual entity — graph carries almost no policy data |
| F38 | `09-crossover-matrix.md:296-298` vs `06-agentic-base.md:160-178` | IMPORTANT | 1 | spec 09 §3.4 says envelope-shape validation must run BEFORE the walker receives the handler return; spec 06 §FR5 says the harness validates on tool return, which is the right time-of-day, but the relationship to the workflow walker's downstream `isinstance` check is not pinned anywhere in spec 06 |
| F39 | `09-crossover-matrix.md:265-272` vs `schemas/context/hooks/pretooluse.schema.json` | IMPORTANT | 2 | spec 09 §3.3 says "PreToolUse `validate_envelope_in` runs on the inbound args" referencing pretooluse hook schema; the schema's `args` carries only `{path, content}` — does not accommodate the action/query_string/node/edge shape the agentic→context interface uses |
| F40 | `09-crossover-matrix.md:296-298` vs `02-tool-result-envelope.md:115-141` | IMPORTANT | 1 | spec 02 acceptance scenarios use `data.error.code = "DATA_SCHEMA_FAILED"` for schema-validation failures; spec 09 §4.6 enumerates ENVELOPE_INVALID, HANDLER_BAD_RETURN, PRETOOLUSE_VETO, WORKFLOW_DISPATCH_CYCLE, HANDLER_EXCEPTION, CROSS_ROW_REF — `DATA_SCHEMA_FAILED` is not in the canonical list spec 09 declares |
| F41 | `02-tool-result-envelope.md:65` vs `09-crossover-matrix.md:133-138` | IMPORTANT | 1 | spec 02 says payload SHOULD stay under 4 KB; spec 09 makes this MUST for `data.artefact_ref` overflow. Spec 02 is the source of truth and uses SHOULD — spec 09 escalates language unilaterally |
| F42 | `02-tool-result-envelope.md:65` vs `09-crossover-matrix.md:540-544` | IMPORTANT | 1 | spec 02 puts overflow under `data.artefact_ref`; spec 09 §4.1 declares 4 KB cap "AFTER composition", inventing a new policy (composition-aware envelope sizing) not present in spec 02 |
| F43 | `06-agentic-base.md:107-110` vs `schemas/agentic/four-verb/dispatch-skill-request.schema.json:7-22` | BLOCKER | 2 | spec 06 declares `dispatch_skill(name, args) -> ToolResult | PhaseStateEnvelope`; schema requires `{row, skill_slug, context_refs}` not `{name, args}`. Spec 06 source code signature contradicts its own schema |
| F44 | `09-crossover-matrix.md:286-291` vs `schemas/agentic/interface-to-workflow.schema.json:7-32` | IMPORTANT | 2 | spec 09 §3.4 cites interface-to-workflow.schema.json fields `{action, row, phase, inputs}`; the schema requires `phase` (not `phase_id`) only when action=start. Acceptance scenarios in §3.4 use `phase_id` and `phase` interchangeably |
| F45 | `04-phase-state-envelope.md:39` vs `09-crossover-matrix.md:222-229` | IMPORTANT | 1 | spec 04 says `session_id: format=uuid`; spec 09 worked examples use `"abc"` — short strings — not UUIDs. Tests against the schema would reject the spec 09 example |
| F46 | `09-crossover-matrix.md:262-264` vs `02-tool-result-envelope.md:75-80` | IMPORTANT | 1 | spec 09 §3.3 closes panel SL #1 by routing overflow to `data.artefact_ref`; spec 02 already names `data.artefact_ref` — but spec 02's table (line 75-80) shows `data.artefact_ref` as a context column extension, not a universal envelope contract. Status of artefact_ref slot needs lifting |
| F47 | `schemas/context/nodes/continuation.schema.json:14` vs `04-phase-state-envelope.md:36-45` | IMPORTANT | 2 | Continuation.payload includes `opaque_state` but no `tool_result`, `status`, `blocked_reason`, `resume_token` — spec 04 envelope fields are not represented in the node payload schema, yet spec 07-v1 §FR4 writes the full envelope into a payload field |
| F48 | `08-context-base-v1.md:300` (`SATISFIES_PHASE` edge from artefact to phase) vs `schemas/context/edges/satisfies-phase.schema.json` | IMPORTANT | 2 | spec 08-v1 emits `SATISFIES_PHASE` from artefact-node to `phase:{row}/{satisfies}`; satisfies-phase schema is silent on direction. Underspecified at schema layer |
| F49 | `09-crossover-matrix.md:115-119` vs schemas | BLOCKER | 3 | spec 09 names `vision/specs/schemas/_shared/workflow-dispatch.schema.json` as the source schema; the entire `_shared/` directory does not exist in the audited tree, so the dispatch-triple's "canonical schema" is a non-existent file path |
| F50 | `09-crossover-matrix.md:36-44` (depends_on list) vs `schemas/context/nodes/continuation.schema.json` | IMPORTANT | 3 | spec 09 depends_on cites `continuation.schema.json` as anchoring the `previous_continuation_id` pointer; that schema does not declare an `envelope`, `created_at_epoch`, or `previous_continuation_id` field — spec 09 depends on a shape that doesn't exist yet |
| F51 | `07-workflow-base.md:128` (legacy) vs `07-workflow-base-v1.md` | NIT | 1 | legacy spec 07 documents `workflow/_state/<sid>/<pid>.json` file format; superseded but body still describes live behaviour. Tagged DEPRECATED at the top but content reads as current to a fresh reader |
| F52 | `08-context-base.md:51` (legacy) vs `08-context-base-v1.md` | NIT | 1 | legacy spec 08 documents raw-SQLite fallback as live; superseded but body reads as live behaviour |
| F53 | `01-cell-manifest.md:13-16` (referenced_by) vs `07-workflow-base-v1.md` / `08-context-base-v1.md` | NIT | 1 | spec 01 referenced_by lists `07-workflow-base.md` and `08-context-base.md` — the legacy specs. The v1 successors are not back-linked |
| F54 | `09-crossover-matrix.md:563` (`wait` enum `["true"]`) | IMPORTANT | 3 | spec 09 §4.2 uses string `"true"`; JSON-Schema-idiomatic boolean true would be more typical. As enum-of-string, it requires a string sentinel; this seems intentional but is forward-compat brittle |
| F55 | `09-crossover-matrix.md:580-589` vs `schemas/context/nodes/session.schema.json` | IMPORTANT | 2 | spec 09 §4.3 lists `workflow_dispatch_depth` as maximum 16, but body text caps at 3 — internal spec-09 inconsistency between schema max and prose cap |
| F56 | `08-context-base-v1.md:67` vs `schemas/context/interface-to-agentic.schema.json:14` | NIT | 2 | spec 08-v1 uses `Store.upsert_node(node_id, payload, *, label)`; interface-to-agentic uses `{id, label, payload}` — different argument ordering but conceptually aligned. Not contradictory but inconsistent in naming convention |
| F57 | `09-crossover-matrix.md:251-256` vs `schemas/context/interface-to-agentic.schema.json` | IMPORTANT | 3 | spec 09 §3.3 mentions `mcp__context_query` / `_describe` / `_read` but `interface-to-agentic.schema.json` declares only `query_response`, `upsert_node_request`, `upsert_edge_request` — no `describe`/`read` payload shape declared from either side |
| F58 | `05-gate-yaml.md:49` vs `schemas/context/nodes/gate.schema.json` | IMPORTANT | 2 | gate YAML id pattern: `^[a-z][a-z0-9-]{0,60}$`; Gate node schema declares `name: string` (no pattern). Pattern lost at the graph layer |
| F59 | `04-phase-state-envelope.md:57` vs `01-cell-manifest.md:43` | IMPORTANT | 1 | spec 04 `row` pattern matches spec 01 pattern; consistent. However spec 09 §4.2 declares row pattern in workflow-dispatch.schema.json — three places redefine the same pattern. DRY issue, not blocking |
| F60 | `06-agentic-base.md:32` (STATUS: Open follow-up C5) vs `09-crossover-matrix.md:402-413` | IMPORTANT | 1 | spec 06 STATUS notes hooks "need to be wired into agentic/_bootloader.py::boot() so they fire on every tool call"; spec 09 §3.7 STATUS says this is BUILT. Spec 06 needs status update |

---

## §2. Lens 1 — Spec-to-spec contradictions

### F01 — `dispatch_skill` signature mismatch

**Spec 06 line 108:**
```python
def dispatch_skill(name: str, args: dict) -> ToolResult | PhaseStateEnvelope:
```

**Spec 09 line 106:**
> `mcp__dispatch_skill(row, skill_slug, context_refs)`

The two cannot both be true. Spec 09's three-arg form matches the
schema (see F43); spec 06 §FR2 line 107-110 is wrong.

### F03 — envelope-double-wrapping at workflow boundary

**Spec 09 lines 204-210:**
> Envelope (inbound): spec 02 ToolResult (the mcp__call_tool response).
> If the workflow phase yields, that response IS a PhaseStateEnvelope
> per spec 04 — but the harness wraps it as a spec 02 envelope at the
> four-verb boundary (the data of the outer envelope is the inner
> PhaseStateEnvelope).

**Spec 04 lines 36-45 (TypedDict):**
PhaseStateEnvelope already carries `tool_result: dict` (a spec 02
envelope) as one of its fields.

Result: a workflow-yield round-trip is now `ToolResult.data ⊃
PhaseStateEnvelope.tool_result ⊃ ToolResult.data ⊃ …` — recursive
wrapping. The spec needs either:
- (a) a flat-wrapping rule (return the PhaseStateEnvelope as the
  outer wire form, sidestepping the four-verb response schema), or
- (b) explicit documentation that the inner `tool_result` is the
  authoritative payload and the outer ToolResult is mechanical
  framing only.

Neither alternative is stated.

### F10 — phase state required-keys collision with completed-path

**Spec 04 lines 55-65:** required keys include `blocked_reason` and
`resume_token` (allowed null).

**Spec 09 acceptance scenarios (lines 880-884, 906-911):**
emit `status="failed"` envelopes without setting `blocked_reason` /
`resume_token`. JSON Schema `required` does not forbid null, so this
passes — but the semantic intent of "required" is muddied when half
the states never populate the fields.

### F11/F12 — spec 04 body vs STATUS banner divergence

Spec 04 STATUS (line 21) declares file-on-disk SUPERSEDED. Body lines
71-79 still describe file paths, atomic rename, TTL sweep against
files. Acceptance scenario lines 163-183 still assert
`workflow/_state/<sid>/<pid>.json`. A reader who skips the STATUS
banner gets a fully-misleading spec.

### F13 — spec 03 DEPRECATED banner vs body

Same shape as F11. Body still teaches the file pattern; the only
signal it's dead is the banner. Archeology is allowed, but the
body should be flagged inline ("THIS SECTION IS HISTORICAL").

### F22 — chain leg wrapping semantics

Spec 09 §3.5 line 325-328 says "spec 04 PhaseStateEnvelope for both
legs. Inside, the carried tool_result matches spec 02." Spec 04 says
the same. But §3.2 line 209-210 says outer ToolResult.data IS the
inner PhaseStateEnvelope. The two sub-cells use opposite framing
conventions for the same workflow-dispatch primitive. Spec 09's
"single shape" claim (§2 line 113-119) doesn't hold across cells.

### F33 — upsert_node payload shape disagrees across boundary

**`schemas/agentic/interface-to-context.schema.json:17-22`:**
```json
"node": {
  "properties": {
    "id": {"type": "string"},
    "type": {"type": "string"},
    "properties": {"type": "object"}
  }
}
```

**`schemas/context/interface-to-agentic.schema.json:13-21`:**
```json
"upsert_node_request": {
  "properties": {
    "id": {"type": "string"},
    "label": {"type": "string"},
    "payload": {"type": "object"}
  }
}
```

Same operation, two different shapes (`type/properties` vs
`label/payload`). One column writes; the other reads. Without
reconciliation, the call cannot validate at both ends.

### F34/F35 — BLOCKS vs BLOCKED_ON direction conflict

**`schemas/context/edges/blocks.schema.json:5`:**
> Indicates a Gate blocking a Phase.

Direction implied: Gate → Phase.

**Spec 07-v1 FR3 step 3 (line 205):**
> `(p:Phase)-[:BLOCKS]->(g:Gate)`

Direction asserted: Phase → Gate.

BLOCKED_ON exists as a separate edge (Phase → Gate). The graph
contract is incoherent — runtime gate evaluation may match neither
or both.

### F40 — error code catalog drift

Spec 02 acceptance scenario uses `DATA_SCHEMA_FAILED`. Spec 09 §4.6
enumerates the "canonical list" but omits this code. The two specs
disagree on the universe of error codes.

### F41/F42 — overflow / composition-cap escalation

Spec 02 line 65: "Total wire size … SHOULD stay under 4 KB". Spec 09
§3 line 134: "The 4 KB per-result invariant". §4.1 line 538-544 adds
"composition cap". Spec 09 unilaterally escalates SHOULD → MUST and
adds a composition policy spec 02 does not contemplate.

### F46 — `data.artefact_ref` status uplift

Spec 02 line 75-80 lists `data.artefact_ref` in the **context column
extension** table, not as a universal contract. Spec 09 §3.3 and §3
treat it as the universal overflow slot. The promotion needs an
explicit edit to spec 02's extension table (or a new "universal
slots" subsection).

### F60 — spec 06 STATUS outdated by spec 09

Spec 06 STATUS line 32 lists C5 hook-wiring as an open follow-up.
Spec 09 §3.7 declares this BUILT. Spec 06 needs the STATUS line
updated to reflect the wiring landing.

---

## §3. Lens 2 — Spec-to-schema drift (schema wins, L06)

### F02/F43 — `dispatch_skill` schema vs spec 06

Schema file: `schemas/agentic/four-verb/dispatch-skill-request.schema.json` lines 7-22.

Schema requires `{row, skill_slug, context_refs}` with
`additionalProperties: false`. Spec 06 (line 108) says `(name, args)`.
The schema is the wire-level truth; spec 06's signature is
unimplementable as written.

### F08/F47 — Continuation payload drift

Schema file: `schemas/context/nodes/continuation.schema.json` lines 11-18.

Schema declares payload properties: `{session_id, phase_id,
opaque_state}` with required `{session_id, phase_id}`. Spec 07-v1
§FR4 line 262-275 writes payload including `envelope` and
`created_at_epoch`. Spec 09 §3.5 needs the same `envelope` field
plus a `previous_continuation_id` chain pointer. None of these is
declared in the schema. Adoption requires editing the schema.

### F09 — Phase payload drift

Schema file: `schemas/context/nodes/phase.schema.json` lines 11-20.

Schema lists `{row, phase_id, name, status, blocked_on_gate}`,
required `{row, phase_id, status}`. Spec 07-v1 §FR2 line 135-141
writes `{row, phase_id, body_ref, lazy_created}`. Three of the five
schema fields are unused; two of the four runtime fields are
undeclared. The schema both over- and under-constrains.

### F14/F15/F16/F17 — Artefact payload drift

Schema file: `schemas/context/nodes/artefact.schema.json` lines 11-25.

| Field | Spec 08-v1 says | Schema says |
|---|---|---|
| `produced_by` | object `{skill, phase, session_id}` | string |
| `artifact_driver` | optional | required |
| `driver_pointer` | optional | required |
| `size_bytes` | required | missing |
| `created_at` | required | missing |
| `derived_from` | required | optional |
| `row` | optional | absent |

The schema and the spec are in near-total disagreement on the
Artefact payload. This is the single largest drift in the corpus.

### F20/F21 — posttooluse hook envelope drift

Schema file: `schemas/context/hooks/posttooluse.schema.json` lines 14-22.

The schema declares envelope properties:
```
ok, data, warnings, artefacts_written, next_suggested_tools, error
```

Spec 02 closes the envelope at `{ok, data, warnings,
next_suggested_tools}` only. `artefacts_written` and `error` are
fictional at the envelope-root level. The hook schema also lacks
`additionalProperties: false`, so it would accept envelopes that
spec 02's `tool_result.schema.json` rejects — the two validators
disagree on what passes.

### F27/F28 — broken / cross-tree `$ref`

Schemas `call-tool-response.schema.json` and
`dispatch-skill-response.schema.json` both `$ref`:
```
../../context/_shared/schemas/tool_result.schema.json
```

That path resolves outside `vision/specs/schemas/` into the runtime
tree. The vision-side schemas are NOT self-contained. A consumer
loading only the vision tree gets unresolvable refs.

### F32 — `phase` vs `phase_id`

`schemas/agentic/interface-to-workflow.schema.json` line 18 uses
field name `phase`. Spec 09 workflow-dispatch §4.2 line 561 uses
`phase_id`. Same concept, two field names across two schemas.

### F37 — Gate-as-node vs Gate-as-YAML

Schema file: `schemas/context/nodes/gate.schema.json` lines 11-17.

Node payload: `{name, row, satisfied}`. Spec 05 YAML gate carries
`{id, type, description, blocks_phase, evaluator, on_success,
on_failure}`. The graph carries almost no policy data — `satisfied`
is a runtime flag, but the policy (evaluator, on-success edge) is
lost. The graph node is a stub; the YAML is the policy. Spec 09
§3.6 reads from the graph for gate evaluation — but the graph node
schema doesn't carry what evaluation needs.

### F36 — Skill status enum mismatch

`schemas/context/nodes/skill.schema.json:22`: `[proposed, ready,
deprecated]`. `schemas/agentic/skill-frontmatter.schema.json:19`:
`[draft, ready, deprecated, proposed]`. Skills in `draft` status
will fail to ingest as nodes.

### F18 — tool name pattern drift

Spec 01 line 127: `mcp__<row>_<export>`. Tool manifest schema line
10: `mcp__<row>_<group>_<action>`. Schema documents a structure spec
01 explicitly forbids (extra segment = re-encoding row info).

### F19 — server name drift

Spec 06 FR1 line 84: server name "agency-system". Harness-bootstrap
schema default: "agency-mcp". A boot using schema defaults would
register under the wrong name.

### F23/F24/F25/F26 — schemas spec 09 promises but doesn't exist

Spec 09 names 4 new schemas:
1. `_shared/workflow-dispatch.schema.json` — `_shared/` dir absent
2. `context/nodes/watcher-emission.schema.json` — file absent
3. `context/nodes/watcher-health.schema.json` — file absent
4. `context-cell.schema.json` watcher block — needs runtime-tree edit
   (this file is in `context/_shared/schemas/`, not under `vision/`)

The vision schemas README (`schemas/README.md`) does NOT list any of
these. Adoption requires file creation + catalog update.

### F31 — four-verb request schemas missing

The four-verb folder has 6 files (request+response for `call-tool`,
`dispatch-skill`; response only for `list-tools`, `list-skills`).
The schemas README line 29 lists 8 (request+response for all four).
`list-tools-request.schema.json` and `list-skills-request.schema.json`
are missing. Spec 06 declares both take an optional `row` parameter
— that contract has no schema.

### F39 — pretooluse args narrow

PreToolUse hook schema's `args` block carries `{path, content}` only
— matching the file-write tool use case. Spec 09 §3.3 routes the
agentic→context query (with `query_string` / `node` / `edge`)
through this hook; the args won't validate. The hook schema needs
extending or the validation needs to be tool-specific (which the
schema does NOT yet model).

---

## §4. Lens 3 — Spec-09 composition gaps

For every new field/node/mechanism spec 09 r2 introduces, the
existing files that must be edited to acknowledge it:

### G1 — `data.workflow_dispatch` triple (§3.2 / §3.5)

Existing files needing edits:
- `vision/specs/02-tool-result-envelope.md` — extension table (line
  75-80) does not list `data.workflow_dispatch` as a known slot;
  needs adding alongside `data.artefact_ref`.
- `vision/specs/06-agentic-base.md` — §FR5 (tool return validation)
  needs to acknowledge that the harness inspects `data.workflow_dispatch`
  post-validation and emits a downstream four-verb call.
- `vision/specs/07-workflow-base-v1.md` — Out-of-scope list (line 491)
  explicitly excludes "cross-row dispatch (planned spec 09)"; spec 09
  having landed means this exclusion needs an in-scope clause and a
  reference to the workflow_dispatch path.
- New schema file `vision/specs/schemas/_shared/workflow-dispatch.schema.json`
  must be created; `_shared/` directory must be created;
  `schemas/README.md` catalog must list it.

### G2 — `previous_continuation_id` pointer (§3.5)

Existing files needing edits:
- `schemas/context/nodes/continuation.schema.json` — needs `envelope`,
  `created_at_epoch`, and `previous_continuation_id` (or whichever
  slot holds the chain pointer) added to payload. Currently the
  schema declares only `{session_id, phase_id, opaque_state}`.
- `vision/specs/02-tool-result-envelope.md` — extension table needs
  `data.previous_continuation_id` listed as a known slot (or spec 09
  §4.7's "open data" justification needs lifting up).
- `vision/specs/04-phase-state-envelope.md` — TypedDict (line 36) and
  JSON Schema (line 55) need acknowledging that the wrapped
  `tool_result.data` may carry `previous_continuation_id`.

### G3 — `workflow_dispatch_depth` on Session (cycle guard, §3.2 / §3.5)

Existing files needing edits:
- `schemas/context/nodes/session.schema.json` — add the field to
  payload. Currently absent.
- `vision/specs/08-context-base-v1.md` — Session node payload is not
  enumerated in the spec; the addition needs documentation here too.

### G4 — `WatcherEmission` node (§4.4)

Files needing creation:
- `vision/specs/schemas/context/nodes/watcher-emission.schema.json`
  (NEW — spec 09 names the path)
- `schemas/context/README.md` (line 7-19) catalog must list it.

### G5 — `WatcherHealth` node (§4.5)

Files needing creation:
- `vision/specs/schemas/context/nodes/watcher-health.schema.json`
  (NEW)
- `schemas/context/README.md` catalog update.

### G6 — `data.artefact_ref` route for overflow (§3 line 134-138)

Existing files needing edits:
- `vision/specs/02-tool-result-envelope.md` — extension table line
  75-80 lists `data.artefact_ref` as **context column extension**.
  Spec 09 treats it as the universal overflow slot. Promotion to
  universal needs explicit wording.

### G7 — `mcp__call_tool` / `mcp__dispatch_skill` cross-row mechanism (§3.1)

Existing files needing edits:
- `vision/specs/06-agentic-base.md` — §FR2 dispatch_skill signature
  needs alignment with the schema (F01/F43 fix).

### G8 — PreToolUse veto right (§3.7)

Existing files needing edits:
- `vision/specs/06-agentic-base.md` — §FR2 `make_hooked_wrapper`
  semantics need acknowledging PreToolUse's right of rejection;
  currently the spec only describes wrapping, not veto.
- `vision/specs/08-context-base-v1.md` — §FR6 `validate_envelope_in`
  return shape must document `{ok: bool, errors: list[str]}` so the
  bootloader can detect a veto.
- `schemas/context/hooks/pretooluse.schema.json` — currently models
  the input payload only; needs a sibling response schema describing
  `{ok, errors}` shape.

### G9 — `mcp__context_query` / `_describe` / `_read` anchor triad (§3.3)

Existing files needing edits:
- `schemas/agentic/interface-to-context.schema.json` — `action` enum
  needs widening to include `describe`, `read`; the existing
  `upsert_node` / `upsert_edge` actions need either removal (graph
  writes are PostToolUse-only per §3.3) or explicit out-of-scope
  flagging.
- `schemas/context/interface-to-agentic.schema.json` — needs
  describe/read response shapes.

### G10 — `WORKFLOW_DISPATCH_CYCLE`, `PRETOOLUSE_VETO`, `HANDLER_EXCEPTION`, `CROSS_ROW_REF` error codes (§4.6)

Existing files needing edits:
- `vision/specs/02-tool-result-envelope.md` — should enumerate the
  canonical error-code list (currently only shows two examples
  inline); spec 09 §4.6 declares the canonical list lives in
  `context/_shared/error_codes.py` — referenced but not yet a file
  spec 02 acknowledges.

### G11 — Boot-ordering invariant for watchers (§3.8)

Existing files needing edits:
- `vision/specs/06-agentic-base.md` — boot() flow needs to
  acknowledge watcher registration as a post-four-verb-registration
  step.

### G12 — cross-row `$ref` ban + CROSS_ROW_REF error (§3.9)

Existing files needing edits:
- `schemas/context/README.md` — needs a section on the cross-row
  `$ref` ban.
- Per-row schema directories (which spec 09 anticipates: `context/<row>/schemas/`)
  are conventional but not yet structurally present in the vision
  schemas tree.

---

## §5. Per-file verdict

| File | Verdict |
|---|---|
| `01-cell-manifest.md` | needs-touch (3 findings: F18, F19 schema-side; F53 referenced_by) |
| `02-tool-result-envelope.md` | needs-touch (8 findings: F03, F20, F21, F40, F41, F42, F46; plus G1/G2/G6/G10 composition gaps) |
| `03-sidecar-metadata.md` | superseded (DEPRECATED, but F13/F14 inconsistency; body still reads as live) |
| `04-phase-state-envelope.md` | inconsistent-self-contradicts (F10, F11, F12 — STATUS banner vs body; F45 UUID/short-string mismatch with spec 09 examples) |
| `05-gate-yaml.md` | needs-touch (2 findings: F37 Gate-as-node drift; F58 id pattern) |
| `06-agentic-base.md` | inconsistent-self-contradicts (F01, F43, F19, F38, F60 — dispatch_skill signature contradicts own schema, STATUS out of date, harness-bootstrap default mismatch) |
| `07-workflow-base-v1.md` | needs-touch (4 findings: F08, F09, F35, plus G1 cross-row scope inclusion) |
| `07-workflow-base.md` | superseded (F51 — DEPRECATED but body still describes live behaviour) |
| `08-context-base-v1.md` | needs-touch (4 findings: F15, F16, F17, F48 — artefact schema disagrees with FR5; SATISFIES_PHASE direction underspecified; plus G3/G8 composition gaps) |
| `08-context-base.md` | superseded (F52 — DEPRECATED but body still describes live behaviour) |
| `schemas/README.md` | needs-touch (F31 four-verb count; F23-F26 missing-schema catalog updates; G4/G5/G12 catalog adds) |
| `schemas/agentic/README.md` | aligned (descriptive, no contracts) |
| `schemas/agentic/four-verb/*` | needs-touch (F27, F28 broken `$ref`; F31 missing request schemas; F02 minor) |
| `schemas/agentic/interface-to-workflow.schema.json` | needs-touch (F32, F44 — `phase` vs `phase_id` drift) |
| `schemas/agentic/interface-to-context.schema.json` | needs-touch (F04, F05, F33 — action enum doesn't include describe/read; node shape disagrees with context-side; describe/read missing) |
| `schemas/agentic/harness-bootstrap.schema.json` | needs-touch (F19 — default name) |
| `schemas/agentic/skill-frontmatter.schema.json` | needs-touch (F36 — status enum drift) |
| `schemas/agentic/tool-manifest.schema.json` | needs-touch (F18 — tool name pattern) |
| `schemas/context/README.md` | needs-touch (G4/G5/G12 catalog adds) |
| `schemas/context/nodes/artefact.schema.json` | inconsistent-self-contradicts (F14-F17 — disagrees with both spec 03 and spec 08-v1 on required fields, types, and field shapes) |
| `schemas/context/nodes/continuation.schema.json` | needs-touch (F07, F08, F47, F50 — payload missing envelope, created_at_epoch, previous_continuation_id) |
| `schemas/context/nodes/phase.schema.json` | needs-touch (F09 — body_ref/lazy_created missing; required `status` not used by v1) |
| `schemas/context/nodes/session.schema.json` | needs-touch (F06 — workflow_dispatch_depth absent; no closed shape) |
| `schemas/context/nodes/gate.schema.json` | needs-touch (F37 — Gate-as-node carries no policy fields) |
| `schemas/context/nodes/skill.schema.json` | needs-touch (F36 — status enum drift) |
| `schemas/context/nodes/cell.schema.json` | aligned |
| `schemas/context/nodes/row.schema.json` | aligned |
| `schemas/context/nodes/tool.schema.json` | aligned |
| `schemas/context/nodes/template.schema.json` | aligned |
| `schemas/context/nodes/schema.schema.json` | aligned |
| `schemas/context/edges/blocks.schema.json` + `blocked-on.schema.json` | inconsistent-self-contradicts (F34, F35 — two edges with inverse direction for same fact) |
| `schemas/context/edges/dispatched-to.schema.json` | aligned (informational for spec 09 cross-row dispatch) |
| `schemas/context/edges/precedes.schema.json` | aligned |
| `schemas/context/edges/derived-from.schema.json` | aligned (F29 — cross-row ban applies but not at schema level) |
| `schemas/context/edges/satisfies-phase.schema.json` | needs-touch (F48 — direction underspecified) |
| `schemas/context/edges/produces.schema.json` | aligned |
| `schemas/context/edges/consumes.schema.json` | aligned |
| `schemas/context/edges/invoked-tool.schema.json` | aligned |
| `schemas/context/hooks/pretooluse.schema.json` | needs-touch (F39 — args too narrow; G8 needs companion response schema) |
| `schemas/context/hooks/posttooluse.schema.json` | inconsistent-self-contradicts (F20, F21 — envelope shape with `artefacts_written` and `error` at root contradicts spec 02) |
| `schemas/context/hooks/session-start.schema.json` | aligned |
| `schemas/context/interface-to-agentic.schema.json` | needs-touch (F33, F57 — upsert_node shape mismatch; no describe/read response) |
| `schemas/context/interface-to-workflow.schema.json` | aligned |
| `schemas/context/artifact-driver/*` | aligned |

**Summary:** 8 aligned · 27 needs-touch · 4 superseded · 5
inconsistent-self-contradicts. 60 findings total
(16 BLOCKER · 33 IMPORTANT · 4 NIT, plus 7 multi-finding clusters).

---

## §6. Headline blockers for landing spec 09

These 5 fixes must happen in **vision/specs/** (not in spec 09) before
Wave A implementation can start. Plan and execute in order — each
later fix depends on the prior fix's schema or spec being stable.

### B1. Fix Artefact-node schema (F14, F15, F16, F17, F48)

`schemas/context/nodes/artefact.schema.json` must be reconciled with
spec 08-v1 §FR5. Required: align required/optional sets, change
`produced_by` from string to object `{skill, phase, session_id}`,
add `size_bytes`, `created_at`, `derived_from` (required), `row`
(optional). Without this, every PostToolUse ingest in the matrix
runs on a contradictory contract — spec 09 §3.7 cannot specify a
deterministic verification gate when the upstream schema is wrong.

### B2. Fix Continuation + Phase payload schemas (F07, F08, F09, F35)

`schemas/context/nodes/continuation.schema.json` must add `envelope`,
`created_at_epoch`, and a slot for the chain pointer; spec 09 §3.5's
`previous_continuation_id` mechanism is unimplementable until the
schema admits the field. `schemas/context/nodes/phase.schema.json`
must replace `{name, status, blocked_on_gate}` with `{body_ref,
lazy_created}` (or unify both) per spec 07-v1 §FR2. BLOCKS edge
direction (F34/F35) must be resolved one way — pick a single
direction and delete the other edge, OR document the two-edge
graph with intent.

### B3. Reconcile `dispatch_skill` signature and four-verb schemas (F01, F27, F28, F31, F43)

`vision/specs/06-agentic-base.md` §FR2 line 107-110 declares
`dispatch_skill(name, args)` — schema requires `(row, skill_slug,
context_refs)`. Pick one. The schema is the source of truth (L06).
Fix spec 06. Also: create the two missing four-verb request
schemas (`list-tools-request`, `list-skills-request`); fix the
broken cross-tree `$ref` in `call-tool-response` and
`dispatch-skill-response`.

### B4. Fix posttooluse hook schema (F20, F21)

`schemas/context/hooks/posttooluse.schema.json` declares envelope
root keys `{ok, data, warnings, artefacts_written,
next_suggested_tools, error}` — adding `artefacts_written` and
`error` that spec 02 explicitly forbids at root. Without
`additionalProperties: false`, the hook schema would accept
envelopes spec 02 rejects. Spec 09 §3.7's PostToolUse contract is
indeterminate while this disagreement stands.

### B5. Create the 3 new schemas spec 09 names (G1, G4, G5) + catalog updates

Three new files must exist before Wave A:
- `vision/specs/schemas/_shared/workflow-dispatch.schema.json` (and
  the `_shared/` directory)
- `vision/specs/schemas/context/nodes/watcher-emission.schema.json`
- `vision/specs/schemas/context/nodes/watcher-health.schema.json`

`schemas/README.md`, `schemas/context/README.md` catalogs must
list the new nodes/schemas. Spec 09 cites all three by path; until
they exist, every depends_on link in spec 09 §0 frontmatter
points at vapor.

---

## End of audit
