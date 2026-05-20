---
slug: vision-alignment-workflow
type: workflow
status: ready
owner: claude
created: 2026-05-20
updated: 2026-05-20
summary: A wave-by-wave roadmap to (a) align vision/ with spec 09 r2, (b) promote the Harness-in-Harness draft from Plan/ into vision/ canon, and (c) achieve the user-stated goal — an isomorphic, token-efficient design that implements Harness-in-Harness end to end.
depends_on:
  - vision/specs/09-crossover-matrix.md
  - vision/specs/09-crossover-matrix-plan.md
  - vision/10-vision-audit-specs.md
  - vision/10-vision-audit-columns.md
  - vision/10-vision-audit-foundational.md
  - Plan/023-harness-in-harness/spec.md
  - Plan/harness/design.md
  - Plan/harness/VOCABULARY.md
  - Plan/harness/restructure/spec.md
referenced_by: []
---

# Vision Alignment Workflow — promote Harness-in-Harness, land spec 09 r2

## §1 The goal restated

An **isomorphic, token-efficient design** where the **four-verb contract** (`mcp__list_tools` / `mcp__call_tool` / `mcp__list_skills` / `mcp__dispatch_skill`) is **identical across the three transport layers** — L1 (pytest in-memory FastMCP), L2 (subprocess probe via `claude --bare --plugin-dir`), L3 (sidecar daemon + `bin/agency` CLI over Streamable HTTP) — and where the **3x3 crossover matrix** in spec 09 r2 routes every cross-column call through that single surface. The token budget is non-negotiable: **boot context < 500 tokens, `tools/list` < 4 KB, per-tool result ≤ 4 KB** (`Plan/harness/VOCABULARY.md:42-46`; spec 02 §Encoding rules; spec 09 §3 bullet 3 at lines 132-138). Harness-in-Harness is not a deferred future feature; it is the **design center** — one MCP server, one envelope, one cell registry, no domain backdoors. Layer-fidelity isomorphism + matrix-cell isomorphism are the same invariant viewed from two axes.

## §2 Hierarchy of canon (post-alignment)

The post-alignment authority order. When two artefacts disagree, the higher row wins.

1. **`vision/specs/schemas/`** — wire-level ground truth. Schema wins (L06 in `vision/10-vision-audit-specs.md:29`).
2. **`vision/specs/0X-*.md`** — typed spec text (01-cell-manifest, 02-tool-result-envelope, 04-phase-state-envelope, 05-gate-yaml, 06-agentic-base, 07-workflow-base-v1, 08-context-base-v1, 09-crossover-matrix, and the two harness specs landed in Wave 0).
3. **`vision/{agentic,workflow,context}/INTERFACE-TO-*.md` + `GHERKIN-OWNED.md`** — per-column behavioral contracts.
4. **`vision/03-architecture.md` + `vision/00-charter.md`** — founding intent. Architecture survives spec 09 r2; charter is superseded by `vision/00.1-Overview.md` per `vision/00-charter.md:12`.
5. **`vision/{agentic,workflow,context}/{COLUMN,BRIEF,Vision}.md`** — narrative context.
6. **`Plan/_research/`, `Plan/_lessons-learned/`, `Plan/decisions/`** — historical record only. **NOT canon.** Spec 09 §1 line 93-97 already names `Plan/decisions/0003/5/7/9` as "archeology"; this workflow extends that demotion to all of `Plan/`. The user has been explicit (CLAUDE.md and this workflow's spec): **Plan/ is draft, vision/ is canon.**

## §3 Waves

The waves run in order. Each wave's exit criteria must be green before the next begins. Wave 6 is the only wave that touches implementation code; everything before is documentation/schema reconciliation.

### Wave 0 — Promotion (Harness-in-Harness draft → vision canon)

The user's clarification is binding: `Plan/harness/` and `Plan/023-harness-in-harness/` are DRAFTS awaiting promotion. Wave 0 moves them into `vision/` as first-class canon, then re-points spec 09 r2 and the per-column files at the new locations.

**Files touched (move, restate, or delete):**
- `Plan/harness/design.md` (1011 lines) → split across two new vision specs:
  - **NEW** `vision/specs/10-harness-ladder.md` — three-layer L1/L2/L3 ladder, §2 north star table, §3 L1 module, §4 L2 probe, §5 L3 daemon + CLI, §6 out-of-scope, §7 Done-When, §8 Gherkin (anchors `harness.L1.*`, `harness.L2.*`, `harness.L3.*`), §9 evidence, §11 path-A levers (L-α/β/γ).
  - **NEW** `vision/specs/11-four-verb-canon.md` — the four-verb contract itself extracted as a top-level spec (currently scattered across `Plan/harness/VOCABULARY.md` §3, `Plan/harness/design.md` §2/§3.2/§5.3, and spec 06 §FR2). Names the verbs, fixes the namespacing (`mcp__<verb>`, never bare `<verb>` — closes column-audit F04/F08 and §6 headline 5), references `vision/specs/schemas/agentic/four-verb/` as the wire-level source, and pins the L1↔L2↔L3 equivalence invariant.
- `Plan/harness/VOCABULARY.md` (353 lines) → restated as **NEW** `vision/specs/12-vocabulary.md`. Cross-cutting canon (three layers, four-verb contract, five handler-bearing domains + agentic, frontmatter conventions, repair-authority tiers, content tiers, Path-A/B disambiguation). This is the single lexicon other vision/ specs cite.
- `Plan/harness/restructure/spec.md` (341 lines) → **NEW** `vision/specs/13-domain-isomorphism.md` with `status: vision`. The Path-B endgame stays a vision artefact (not active implementation) but lives where reviewers will find it. Path-A levers (already documented in 10-harness-ladder) remain the active path.
- `Plan/023-harness-in-harness/spec.md` (198 lines) → its MVP scope (items 2-3-5-6-7-8) is already absorbed by `Plan/harness/design.md` §5 (now 10-harness-ladder.md L3); its deferred items 1+4 become **NEW** `vision/specs/14-progressive-disclosure-roadmap.md` with `status: roadmap`. Plan/023 itself stays in Plan/ as historical record with a `superseded_by:` pointer to 10-harness-ladder.

**Deferred levers — explicit disposition:**

| Lever | Origin | Disposition in vision/ |
|---|---|---|
| **L-α** unified `register(mcp)` | design.md §11.5 | Active — folded into 10-harness-ladder §11. |
| **L-β** `@domain_tool` decorator | design.md §11.5 | Active — folded into 10-harness-ladder §11. |
| **L-γ** manifest auto-sync at boot | design.md §11.5 | Active — folded into 10-harness-ladder §11. |
| **L-δ** SKILL.md required-base schema | design.md §11.5 | Roadmap — 14-progressive-disclosure-roadmap §2. |
| **L-ε** stateful tools (`requires_state`) | design.md §11.5 | Roadmap — 14-progressive-disclosure-roadmap §3. |
| **L-ζ** binary envelope standardisation | design.md §11.5 | Roadmap — 14-progressive-disclosure-roadmap §4. Note: distinct from spec 02 `data.artefact_ref` overflow (which IS canon per Wave 1). |
| **L-η** tool-only domains formal flag | design.md §11.5 | Roadmap — 14-progressive-disclosure-roadmap §5. |
| **L-progressive-disclosure** 4-tier ladder | Plan/023 item 4 | Roadmap — 14-progressive-disclosure-roadmap §6. The 2-tier baseline (`list` + `describe`) stays in 10-harness-ladder §5.6 as active. |

**Spec 09 r2 ↔ Harness-in-Harness reconciliation:**
- Spec 09 §3 bullet 1 ("one MCP server") = harness ladder's "one `create_mcp()` factory across all three layers" (design.md §5.2, VOCABULARY §1, §2). **They are the same invariant.** Wave 0 makes that explicit by cross-citing.
- Spec 09 §3 bullet 4 ("4 KB per-result invariant") = VOCABULARY §1 "per-tool result max in context ≤ 4 KB → archived". **Same invariant; same source.**
- Spec 09's four-verb references throughout §3.1/3.2/3.3 = the harness four-verb contract. **Wave 0 collapses the duplication** by having spec 09 cite 11-four-verb-canon for the verb signatures.
- Spec 09 does NOT supersede any harness/ section. The harness ladder does NOT supersede spec 09. They are **orthogonal axes** (layer-fidelity vs. matrix-cell) of the same isomorphism. The promotion makes both visible side-by-side in `vision/specs/`.

**Findings closed by Wave 0:** none directly (Wave 0 is structural; it stages the substrate Waves 1-3 fix). Downstream effect: closes column-audit §6 headline 5 (bare `call_tool` → `mcp__call_tool`) and foundational-audit F2/F11/F14/F16 (the phantom `specs/09-cross-row-dispatch.md` framing is replaced by the new harness specs naming the 3x3 matrix as their callee).

**New artefacts:**
- `vision/specs/10-harness-ladder.md`
- `vision/specs/11-four-verb-canon.md`
- `vision/specs/12-vocabulary.md`
- `vision/specs/13-domain-isomorphism.md` (status: vision)
- `vision/specs/14-progressive-disclosure-roadmap.md` (status: roadmap)

**Files LEFT in Plan/ (history only):**
- `Plan/harness/_research/01..06-*.md` — research record; not promoted. Cite from new vision specs by Plan-path only.
- `Plan/harness/design.md` — keep with frontmatter `status: superseded`, `superseded_by: [vision/specs/10-harness-ladder.md, vision/specs/11-four-verb-canon.md]`.
- `Plan/harness/VOCABULARY.md` — keep with frontmatter `status: superseded`, `superseded_by: [vision/specs/12-vocabulary.md]`.
- `Plan/harness/restructure/spec.md` — keep with `status: superseded`, `superseded_by: [vision/specs/13-domain-isomorphism.md]`.
- `Plan/023-harness-in-harness/spec.md` — keep with `status: superseded`, `superseded_by: [vision/specs/10-harness-ladder.md §5, vision/specs/14-progressive-disclosure-roadmap.md]`.
- `Plan/decisions/` — left untouched; spec 09 §1 line 93-97 already marks them as MVP-era archeology.

**Exit criteria:**
- All five new specs exist with frontmatter (`status: ready` for 10/11/12; `status: vision` for 13; `status: roadmap` for 14).
- Every superseded Plan/ file carries a reciprocal `superseded_by:` pointer (reciprocity rule, VOCABULARY §6B).
- Spec 09 r2 line-by-line scan finds zero references to `Plan/harness/` / `Plan/023/` that have not been redirected to the new vision/specs/ slots (one exception: `Plan/_research/` historical citations are allowed).
- `vision/specs/10-harness-ladder.md` §8 contains the `harness.L1.4` Gherkin (PR #115 smoke-test resolution; design.md:589-594) AND a new `harness.matrix.iso` scenario asserting that an L1 `call_tool` against `mcp__<row>_start` returns the same body as the L3 daemon's `agency tool execute mcp__<row>_start` (the layer-fidelity invariant the L1↔L3 equivalence test pins).

**Size:** large. ~5 new spec files totalling ~1800-2200 lines, mostly restated from existing Plan/ material with re-anchored references and 4-verb naming canonicalisation. No new research required; all substrate already exists in Plan/. Estimated 3-4 Jules sessions or 1-2 days of focused authoring.

**Dependencies:** none upstream — Wave 0 is the foundation for all subsequent waves. Wave 1 cannot start until 11-four-verb-canon and 12-vocabulary exist (they are cited as the schema-and-naming source of truth in Wave 1 edits).

### Wave 1 — Schema reconciliation (the 16 BLOCKERs)

**Files touched:**
- `vision/specs/schemas/agentic/four-verb/call-tool-response.schema.json`, `dispatch-skill-response.schema.json` — fix broken `$ref` (F27/F28).
- `vision/specs/schemas/agentic/four-verb/list-tools-request.schema.json` (CREATE), `list-skills-request.schema.json` (CREATE) — fill missing request schemas (F31).
- `vision/specs/schemas/agentic/four-verb/dispatch-skill-request.schema.json` — confirm `{row, skill_slug, context_refs}` (F02 review).
- `vision/specs/schemas/agentic/interface-to-context.schema.json` — widen `action` enum to include `describe`, `read`; remove or carve out `upsert_node`/`upsert_edge` (F04/F05); fix `node` shape (F33).
- `vision/specs/schemas/agentic/interface-to-workflow.schema.json` — rename `phase` → `phase_id` (F32/F44).
- `vision/specs/schemas/agentic/harness-bootstrap.schema.json` — default `agency-system`, not `agency-mcp` (F19).
- `vision/specs/schemas/agentic/skill-frontmatter.schema.json` + `vision/specs/schemas/context/nodes/skill.schema.json` — align status enums (F36).
- `vision/specs/schemas/agentic/tool-manifest.schema.json` — fix name pattern `mcp__<row>_<export>` (F18).
- `vision/specs/schemas/context/nodes/artefact.schema.json` — full Artefact rewrite (F14/F15/F16/F17): `produced_by` as object `{skill, phase, session_id}`; make `artifact_driver`/`driver_pointer` optional; add required `size_bytes`/`created_at`/`derived_from`; add optional `row`. This is Wave 1's largest single edit (audit headline B1).
- `vision/specs/schemas/context/nodes/continuation.schema.json` — add `envelope`, `created_at_epoch`, `previous_continuation_id` to payload (F07/F08/F47/F50).
- `vision/specs/schemas/context/nodes/phase.schema.json` — replace `{name, status, blocked_on_gate}` with `{body_ref, lazy_created}` (or unify); align with 07-v1 FR2 (F09).
- `vision/specs/schemas/context/nodes/session.schema.json` — add optional `workflow_dispatch_depth` (F06; spec 09 §4.3; foundation for the cycle guard).
- `vision/specs/schemas/context/nodes/gate.schema.json` — extend payload with policy fields or rule that policy lives in YAML and the node is a runtime stub (F37).
- `vision/specs/schemas/context/edges/blocks.schema.json` + `blocked-on.schema.json` — decide direction (F34/F35); audit headline B2 says **pick one and delete the other**, or document the two-edge graph explicitly.
- `vision/specs/schemas/context/edges/satisfies-phase.schema.json` — pin direction (F48). Note: column-audit F12/F47 says `SATISFIES_PHASE` is not in spec-09/08-v1 edge canon. **Recommended resolution:** delete the edge entirely; gate satisfaction lives in PostToolUse ingest emitting `DERIVED_FROM` from artefact to source per spec 09 §3.6/§3.9.
- `vision/specs/schemas/context/hooks/posttooluse.schema.json` — close envelope to spec 02's 4 keys; move `artefacts_written` / `error` to `data` slots (F20/F21; audit headline B4).
- `vision/specs/schemas/context/hooks/pretooluse.schema.json` — widen `args` to accept the agentic→context query shape; add companion response schema declaring `{ok, errors}` for veto (F39; spec 09 G8).
- `vision/specs/schemas/_shared/workflow-dispatch.schema.json` (CREATE; F26/F49) — spec 09 §4.2 names this schema. Wave 1 creates `_shared/` dir + the schema.
- `vision/specs/schemas/context/nodes/watcher-emission.schema.json` (CREATE; F24; spec 09 §4.4).
- `vision/specs/schemas/context/nodes/watcher-health.schema.json` (CREATE; F25; spec 09 §4.5).
- `vision/specs/schemas/README.md`, `vision/specs/schemas/agentic/README.md`, `vision/specs/schemas/context/README.md` — catalog updates for the three new schemas + the corrected four-verb count (F31).
- `vision/specs/06-agentic-base.md` — fix `dispatch_skill(name, args)` → `dispatch_skill(row, skill_slug, context_refs)` per schema (F01/F43; audit headline B3). Fix STATUS line 32 to reflect C5 hook-wiring landed (F60). Fix server name (F19 spec-side).
- `vision/specs/07-workflow-base-v1.md` — align Continuation/Phase payload language with the fixed schemas (F08/F09 spec-side).
- `vision/specs/08-context-base-v1.md` — align Artefact FR5 with the fixed Artefact schema (F15/F16/F17); align SATISFIES_PHASE direction with Wave 1's decision (F48 spec-side); document `data.workflow_dispatch` extension and `workflow_dispatch_depth` on Session (G3/G8 from audit-specs §4).
- `vision/specs/02-tool-result-envelope.md` — extension table picks up `data.workflow_dispatch`, `data.previous_continuation_id`; promote `data.artefact_ref` from "context column extension" to universal slot (F40/F41/F42/F46; G1/G2/G6/G10).

**Cross-tree `$ref` resolution (the key isomorphism call):**

The vision schemas at `vision/specs/schemas/agentic/four-verb/` `$ref` into `context/_shared/schemas/` (the runtime tree). This is the F27/F28 hazard — the vision tree is NOT self-contained.

**Decision (made here, locked for Wave 1):** vision-side schemas reference each other only **within `vision/specs/schemas/`**. The runtime tree at `context/_shared/schemas/` becomes a generated mirror (or — if generation is too heavy — a hand-mirrored copy with a CI lint asserting equality). Justification by isomorphism: **the same envelope schema must be the source of truth at L1 (pytest), L2 (subprocess), and L3 (sidecar daemon)**. If runtime imports from `context/_shared/schemas/` while spec citations point at `vision/specs/schemas/`, the two layers can drift unobserved. The vision tree IS the source; the runtime tree mirrors it. CI lint added in Wave 5.

**Findings closed:** F01, F02 (review), F04, F05, F06, F07, F08, F09, F10, F14, F15, F16, F17, F18, F19, F20, F21, F22, F23 (file-existence side), F24, F25, F26, F27, F28, F31, F32, F33, F34, F35, F36, F37, F39, F43, F44, F47, F48, F49, F50, F60. All 16 BLOCKERs from `vision/10-vision-audit-specs.md`, plus the IMPORTANT findings that ride along.

**New artefacts:** 5 new schema files (2 four-verb request, 1 workflow-dispatch, 2 watcher), 1 new schemas subdirectory (`_shared/`), 1 PreToolUse response schema (G8).

**Exit criteria:**
- Zero cross-tree `$ref` from `vision/specs/schemas/` to anywhere outside that tree (CI-checkable; lint added Wave 5).
- All schemas resolve cleanly against Draft 2020-12 (a JSON-Schema validator run against each file passes).
- Artefact-node schema audit (F14-F17) closes — `vision/specs/08-context-base-v1.md` FR5 and `vision/specs/schemas/context/nodes/artefact.schema.json` agree field-by-field.
- Spec 09 r2's three "BLOCKER 3" findings on missing schemas (F24/F25/F26) close — files exist, README catalogs list them.
- `vision/specs/06-agentic-base.md` §FR2 `dispatch_skill` signature matches `dispatch-skill-request.schema.json` exactly.

**Size:** large. ~25 schema edits, ~5 schema creations, ~6 spec-text edits. Estimated 2-3 Jules sessions in parallel (the schemas split cleanly: one session for agentic/, one for context/nodes+edges, one for hooks+_shared+spec-text). Critical path.

**Dependencies:** Wave 0 must land first — Wave 1 cites 11-four-verb-canon for the verb signatures it locks into the schemas, and 12-vocabulary for the naming conventions.

### Wave 2 — Column canon reconciliation (the 22 column HIGHs)

**Files touched (per column):**

*agentic/* (10 files audited; 7 need touch):
- `vision/agentic/INTERFACE-TO-WORKFLOW.md` — fix dispatch_skill signature (F01), four-verb naming (F04), `execute_pipeline` as in-process callable (F03), drop `mcp__workflow_scaffold_row` (F05).
- `vision/agentic/INTERFACE-TO-CONTEXT.md` — envelope to 4 keys (F17); replace `query_graph` with anchor triad routing; switch hook model to `make_hooked_wrapper` (column-audit §2.5/§2.6).
- `vision/agentic/INTERFACES.md` — fix dispatch_skill signature (F02); rename four-verb to `mcp__` form (F08 sibling); drop direct `write_edge` (column-audit §2.4).
- `vision/agentic/COLUMN.md` — collapse `dispatch_skill (or mcp__workflow_dispatch)` confusion (F21); drop handler-side `write_edge` (F22); confirm 4-key envelope (F19 self-contradiction resolves once F17 fixed).
- `vision/agentic/Vision.md` — name `data.workflow_dispatch` slot per spec 09 §3.2 (F40).
- `vision/agentic/INTEGRATED-DRAFT.md` — replace decorator-based hook model with `make_hooked_wrapper` boot-time wrapping (F44).
- `vision/agentic/GHERKIN-OWNED.md` — fix `{row, phase, context_refs}` → `{row, phase_id, inputs}` for workflow_dispatch payload (F50). Note: dispatch_skill keeps `{row, skill_slug, context_refs}` per Wave 1.

*workflow/* (13 files audited; 7 need touch):
- `vision/workflow/INTERFACE-TO-AGENTIC.md` — drop `write_edge` requirement (F06); drop `audit_trail` envelope extension (F07); fix four-verb naming (F08); `execute_pipeline` as behind-the-curtain (F03).
- `vision/workflow/INTERFACE-TO-CONTEXT.md` — drop `audit_trail` (F13); drop `SUPERSEDES` (F14); defer `pandoc_render` (F15) — note as out of scope for the matrix.
- `vision/workflow/INTERFACES.md` — fix four-verb naming (F08).
- `vision/workflow/COLUMN.md` — collapse `handoffs/envelope.yaml` to spec 02 (F20); switch dispatch verb from `start_phase`/`resume_phase` to `mcp__<row>_start` (F23).
- `vision/workflow/INTEGRATED-DRAFT.md` — align PhaseStateEnvelope status enum to spec 04 (F41); drop SATISFIES_PHASE emission from evaluator (F42); flip open questions to resolved/deferred per spec 09 §3.5/§7 (F45).
- `vision/workflow/META-WORKFLOW.md` — route scaffold via `mcp__call_tool("mcp__workflow_start", …)` (F26); fix template filename drift (F27).
- `vision/workflow/GHERKIN-OWNED.md` — drop `handoffs/` if envelope.yaml deleted (F49).
- `vision/workflow/VISION.md` — pick up status enum + chain/Continuation (F41 carried).

*context/* (13 files audited; 5 need touch):
- `vision/context/INTERFACE-TO-AGENTIC.md` — replace `query_graph(cypher)` with `mcp__context_query/_describe/_read` (F09); align envelope tag (F10); pull handler authority for `validate_frontmatter`/`ingest_node`/`write_edge` (F11); these are PostToolUse-wrapped, not handler-side.
- `vision/context/INTERFACE-TO-WORKFLOW.md` — drop `SATISFIES_PHASE` emission requirement (F12); resolve resolver name `get_storage_path` vs `get_vault_path` (F16; column-audit §2.7).
- `vision/context/INTERFACES.md` — envelope to 4 keys (F18).
- `vision/context/COLUMN.md` — add watcher block awareness (F24); align `$id` URI scheme to `https://agency-system.dev/schemas/…` (F25; matches spec 09 §4.4/§4.5).
- `vision/context/ONTOLOGY.md` — edge canon: keep `PRECEDES`, `DERIVED_FROM`, `DISPATCHED_TO`, `INVOKED_TOOL`; drop `DISPATCHES`, `USES_SCHEMA`, `USES_TEMPLATE`, `SUPERSEDES`, `PRODUCED_LESSON`, `SATISFIES_PHASE` (F47/F12/F48).
- `vision/context/Vision.md` — edge canon update (F48 carried).
- `vision/context/INTEGRATED-DRAFT.md` — drop sidecar pattern, route overflow via `data.artefact_ref` (F43).
- `vision/context/GHERKIN-OWNED.md` — 6-key envelope at line 14 → 4-key.

**REVIEW-OF-* files (10 files; 5 superseded):**
- `vision/agentic/REVIEW-OF-WORKFLOW.md` — mark F28/F29 STALE; F30 redirected to `vision/workflow/COLUMN.md` Wave 2 edit.
- `vision/agentic/REVIEW-OF-CONTEXT.md` — mark F31/F32 STALE; F33 redirected to `vision/context/INTERFACE-TO-AGENTIC.md` Wave 2 edit.
- `vision/workflow/REVIEW-OF-AGENTIC.md` — mark F34/F35 STALE (resolved by spec 09 §3.2 cycle guard + §3.5 wait=True).
- `vision/workflow/REVIEW-OF-CONTEXT.md` — mark F36/F37 STALE; F39 redirected to `vision/workflow/COLUMN.md`.
- `vision/context/REVIEW-OF-AGENTIC.md` — mark F38 STALE + INVERTED (the praised handler-side edge writes are now outlawed by spec 09 §3.7).

**Findings closed:** F01-F50 in `vision/10-vision-audit-columns.md` (22 HIGH, 21 MED, 7 LOW; some HIGH overlap with audit-specs and close in Wave 1's spec-text edits).

**New artefacts:** none. All column-canon edits.

**Exit criteria:**
- `grep -rn "write_edge" vision/{agentic,workflow,context}/` returns zero hits in active text (allowed only in reviews marked STALE).
- `grep -rn "audit_trail" vision/{agentic,workflow,context}/` returns zero hits.
- `grep -rn "SATISFIES_PHASE\|SUPERSEDES\|DISPATCHES" vision/{agentic,workflow,context}/` returns zero hits in edge canon (allowed only in historical REVIEW-OF-* marked STALE).
- Every cross-column verb invocation reads `mcp__<verb>`, not bare `<verb>`. Spot-check the four headline files: `vision/agentic/INTERFACE-TO-WORKFLOW.md`, `vision/workflow/INTERFACES.md`, `vision/agentic/Vision.md`, `vision/agentic/INTEGRATED-DRAFT.md`.
- All three `INTERFACES.md` and the six `INTERFACE-TO-*.md` agree on a single `dispatch_skill(row, skill_slug, context_refs)` signature (column-audit headline 2 closes).
- All three `INTERFACES.md` and the six `INTERFACE-TO-*.md` agree on a single 4-key envelope (column-audit headline 1 closes).

**Size:** medium-to-large. ~25-30 file edits across the three columns; most are surgical (a paragraph or signature change). Estimated 2 Jules sessions in parallel (one per column, with the agentic edits split off because they cite spec 09 more heavily).

**Dependencies:** Wave 1 must land first — every column edit cites a Wave-1 schema or spec-text. Cannot start Wave 2 in parallel because the per-column files reference shapes (e.g. `workflow-dispatch.schema.json`, the fixed Artefact node, the fixed Continuation) that Wave 1 creates.

### Wave 3 — Foundational reconciliation (the 9 foundational HIGHs)

**Files touched:**
- `vision/README.md` — Canon §6 update to v1 specs (07-v1, 08-v1) and add specs 09, 10, 11, 12 (F1). Drop phantom `specs/09-cross-row-dispatch.md` + `specs/10-bootloader.md` from Out-of-Scope (F2 — D1/D2). Refresh Status snapshot to post-v0.1 + v0.3 (F3/F4). Add Canon entry pointing readers at spec 09 r2 (F5). Add link to `vision/05-v0-1-retrospective.md` (A11). Add the 3x3 matrix framing line at the top so the foundational story names what spec 09 delivers (closes foundational-audit §6 headline 1 and §4 drift).
- `vision/00-charter.md` — frontmatter `superseded_by: vision/00.1-Overview.md` (S4/F28). Inline note that scenario 10's R1-agentic→R2-workflow framing is one of nine crossings (F6).
- `vision/00.1-Overview.md` — §2 "Result Registry" body rewritten: the `result/<row>/` directory is RETIRED; overflow routes through `data.artefact_ref` → `Artefact` graph node per spec 02 §Encoding rules + spec 09 §3 bullet 3 + spec 03-architecture §8. §3 "Resolving Edge Cases" sidecar prescription `track.meta.json` is RETIRED; field-set moves to `Artefact.payload` per 08-context-base-v1 §FR5 (F8/F9 — foundational-audit headline 2). Optional: slice the retired prose into a "historical annex" rather than delete, to preserve traceability.
- `vision/02-plan.md` — frontmatter `status: superseded` with `superseded_by: [vision/04-nextsteps.md, vision/05-v0-1-retrospective.md]` (S7/F10). Drop phantom `specs/09-cross-row-dispatch.md` + `specs/10-bootloader.md` (F11 — D3/D4).
- `vision/03-architecture.md` — `referenced_by:` update to v1 specs (F12). §8 "Consequences for the spec set" rewritten in past tense — both v1 specs have shipped (F13). §10 phantom names fixed (F14 — D5/D6).
- `vision/04-nextsteps.md` — frontmatter `status: superseded` with `superseded_by: vision/05-v0-1-retrospective.md` (S5/F15). §"Cross-row dispatch (planned `specs/09`)" — change inline language: 09 r2 is on disk as the 3x3 crossover matrix (F16 — D7).
- `vision/05-v0-1-retrospective.md` — v0.3 jules-orchestration creep made visible in README (F17). `referenced_by` becomes reciprocal once README adds the link (F18).
- `vision/NEXT-SESSION-PROMPT.md` — replace with a fresh prompt that drops into Wave 1 of this workflow, OR delete (S6/F19).
- `vision/specs/07-workflow-base.md` — frontmatter `superseded_by: vision/specs/07-workflow-base-v1.md` (S1/F20).
- `vision/specs/08-context-base.md` — frontmatter `superseded_by: vision/specs/08-context-base-v1.md` (S2/F21).
- `vision/specs/03-sidecar-metadata.md` — frontmatter `superseded_by: vision/specs/08-context-base-v1.md` (S3/F22).

**Findings closed:** F1-F19, F28, S1-S7 in `vision/10-vision-audit-foundational.md`. All 9 foundational HIGHs, plus the asymmetric supersede chains.

**The 3x3 framing hoist (foundational-audit §4 + headline 1):** A short paragraph (~3-5 sentences) lands in `vision/00.1-Overview.md` §2 (or §1, as appropriate) and is mirrored in `vision/03-architecture.md` §1 — naming the 3x3 caller-column × callee-column matrix as the canonical framing, replacing the older "agentic-owns-cross-row-dispatch" framing of `vision/00-charter.md:78-85`. The reader following the canonical read-order now arrives at spec 09 r2 with the right mental model.

**New artefacts:** none.

**Exit criteria:**
- `grep -rn "09-cross-row-dispatch" vision/` returns zero hits (the phantom name is exterminated).
- `grep -rn "result/<row>/\|track.meta.json" vision/00.1-Overview.md` returns zero hits in prescriptive prose (allowed only in marked-historical sections).
- Every superseded foundation file has reciprocal frontmatter pointing at its successor.
- `vision/README.md` Canon section lists 07-v1, 08-v1, AND the new specs 09-14 in read-order.
- The 3x3 framing paragraph exists in `vision/00.1-Overview.md` (or `vision/03-architecture.md`); cross-referenced from spec 09 §1.

**Size:** medium. ~10 file edits, mostly small-to-medium per file. Estimated 1 Jules session or one focused authoring pass.

**Dependencies:** Wave 0 must land first (the new specs 10-14 are listed in README's updated Canon §6). Wave 3 can run **in parallel with Wave 2** — the foundational and per-column files have no shared edits.

### Wave 4 — Cross-ref hygiene (10 dead links, 12 asymmetric refs, 7 stale supersedes)

**Files touched:** all files in the foundational audit's §3 tables (D1-D10, A1-A12, S1-S7). Most of S1-S7 closes in Wave 3; Wave 4 closes the residual A1-A12 reciprocity.

**Specific edits:**
- `vision/specs/02-tool-result-envelope.md:14` — add `referenced_by: [..., vision/specs/09-crossover-matrix.md]` (A1).
- `vision/specs/04-phase-state-envelope.md:14` — add `referenced_by: [..., 09]` (A2).
- `vision/specs/06-agentic-base.md:16` — add `referenced_by: [09]` (A3).
- `vision/specs/07-workflow-base-v1.md:22` — add `referenced_by: [09]` (A4).
- `vision/specs/08-context-base-v1.md:22` — add `referenced_by: [..., 09]` (A5).
- `vision/00-charter.md`, `vision/00.1-Overview.md`, `vision/03-architecture.md` — add `referenced_by:` frontmatter fields (A6/A7/A8).
- The six per-column `INTERFACE-TO-*.md` files referenced by spec 09 — add `referenced_by: [vision/specs/09-crossover-matrix.md]` (A9).
- `vision/specs/09-crossover-matrix.md:46` — add `[vision/specs/09-crossover-matrix-plan.md, vision/specs/09-crossover-matrix-review.md]` to `referenced_by:` (A10).
- `vision/05-v0-1-retrospective.md` ↔ `vision/README.md` reciprocity (A11) — closes in Wave 3 already.
- `vision/02-plan.md:10-18` — add `referenced_by:` field (A12).

**Findings closed:** D1-D10, A1-A12 (residual after Wave 3), S1-S7 (residual after Wave 3).

**New artefacts:** none.

**Exit criteria:**
- Reciprocity rule (VOCABULARY §6B) holds across all of `vision/`: for every `depends_on:` or `supersedes:` declaration in frontmatter, the target file carries the inverse pointer.
- Zero dead `[..](path)` markdown links pointing at non-existent files. A CI script (added in Wave 5) `grep`s every link and verifies.

**Size:** small. ~15 frontmatter edits; mostly mechanical. Estimated <1 Jules session or 1-2 hours of authoring.

**Dependencies:** Wave 1 (the new schemas need their catalog updated), Wave 2 (per-column files have their INTERFACE-TO-*.md cite spec 09), Wave 3 (the foundational supersede chains close first).

### Wave 5 — Re-review

**The panel runs again** against the aligned vision/. Until this wave returns zero BLOCKERs, **spec 09 r2 stays `status: draft`**. The user's constraint is binding: do NOT iterate spec 09 again as part of this workflow; the panel re-review IS the next iteration trigger.

**Activities:**
- Re-dispatch the same panel pass that produced the three audits (spec-corpus, per-column, foundational). Expectation: zero BLOCKERs, zero HIGH-severity findings outside ARK (already-deferred deferrals).
- Add CI lint scripts to mechanically enforce the Wave 1-4 invariants:
  1. **`bin/lint-vision-schemas`** — for every schema in `vision/specs/schemas/`, validate against Draft 2020-12 AND assert no `$ref` escapes the `vision/specs/schemas/` subtree.
  2. **`bin/lint-vision-runtime-mirror`** — assert that for every file in `vision/specs/schemas/`, a byte-equal (or semantically-equal) sibling exists in `context/_shared/schemas/`. (This locks the isomorphism between the canonical tree and the runtime tree; closes the F27/F28 hazard permanently.)
  3. **`bin/lint-vision-reciprocity`** — walk every frontmatter `depends_on:` / `supersedes:` and verify the reciprocal pointer exists.
  4. **`bin/lint-no-bare-verbs`** — grep `vision/` for bare `call_tool\|dispatch_skill\|list_tools\|list_skills` and fail if any occurrence is NOT prefixed with `mcp__` outside historical REVIEW-OF-* or audit files.

**Findings closed:** acceptance is "zero new BLOCKER findings from the re-run".

**Exit criteria:**
- Panel re-review returns: BLOCKER 0, HIGH ≤ N (where N = the count of pre-existing deferrals tagged in spec 09 §7 DSAs).
- All four lint scripts green.
- Spec 09 r2 frontmatter status flips from `draft` to `ready`.

**Size:** medium. ~4 lint scripts (small Python utilities), 1 panel re-review pass (1 Jules session). Estimated 1-2 days elapsed.

**Dependencies:** Waves 1-4 must all be green. Wave 5 is the gate.

### Wave 6 — Implementation gate (spec 09 Wave A/B/C, harness L1/L2/L3 land)

**Spec 09 r2's `vision/specs/09-crossover-matrix-plan.md` Wave A/B/C only enters here.** The harness ladder's L1/L2/L3 implementation (much of which is already shipped per VOCABULARY §2 — L1 + L2 in PR #127) lands and is tagged. The Path-A levers (L-α, L-β, L-γ) merge alongside.

This workflow does not author Wave 6's content — it is a separate dispatch arc. The contract Wave 6 inherits from Waves 0-5 is:
- A self-consistent vision/ corpus with spec 09 r2 at `status: ready`.
- A canonical Harness-in-Harness specification at `vision/specs/10-harness-ladder.md` + `vision/specs/11-four-verb-canon.md`.
- Four CI lints enforcing the isomorphism invariants.
- Frontmatter reciprocity across all of vision/.

**Findings closed:** none in this workflow's scope.

**New artefacts:** code implementations, not specs. Out of scope here.

**Exit criteria:** spec 09 r2 acceptance scenarios + harness ladder Gherkin all pass against the running plugin. Defined in `vision/specs/09-crossover-matrix-plan.md` Wave C, not here.

**Size:** XL (weeks of Jules sessions). Out of scope.

**Dependencies:** Wave 5 green.

## §4 Promotion plan for Harness-in-Harness (Wave 0 detail)

**Concrete moves:**

| Plan/ source | New vision/ location | Status | What's preserved | What's restated |
|---|---|---|---|---|
| `Plan/harness/design.md` §1-§10 | `vision/specs/10-harness-ladder.md` | ready | L1/L2/L3 ladder, four-verb contract, Gherkin acceptance anchors, evidence citations | Re-anchored "depends_on" to vision/ paths, not Plan/ paths; cross-refs to 11-four-verb-canon and 12-vocabulary |
| `Plan/harness/design.md` §11 (Paths A/B/C) | `vision/specs/10-harness-ladder.md` §11 (Path A only) + `vision/specs/13-domain-isomorphism.md` (Path B) | ready (10), vision (13) | Decision rationale, the 7 levers table, migration sketches | Path A is the live tag; Path B stays a vision artefact |
| `Plan/harness/VOCABULARY.md` | `vision/specs/12-vocabulary.md` | ready | The three-layer ladder canon, four-verb table, five-domains-plus-agentic, naming conventions, frontmatter rules, repair-authority tiers, content tiers, Path A/B disambiguation | Token budget invariants moved into spec 02 / spec 09 (already there); skill_kind enum stays |
| `Plan/harness/restructure/spec.md` | `vision/specs/13-domain-isomorphism.md` | vision | Target tree, Domain base class, migration strategy, risk register | No content changes — straight restatement |
| `Plan/023-harness-in-harness/spec.md` items 2-3-5-6-7-8 | (already absorbed in 10-harness-ladder §5) | ready | L3 daemon + CLI + bootstrap | Plan/023 marked superseded |
| `Plan/023-harness-in-harness/spec.md` items 1+4 | `vision/specs/14-progressive-disclosure-roadmap.md` §1, §6 | roadmap | Research-epic for prior-art survey + 4-tier ladder design | Re-titled; spec body restated |

**Files LEFT in Plan/ (history-only):**
- All of `Plan/harness/_research/` — research outputs from the harness work; cited by vision/specs/10-harness-ladder.md §9 but not promoted.
- `Plan/decisions/0001-0009/*` — MVP-era ADRs already named "archeology" by spec 09 §1 line 93-97. Stay where they are.
- `Plan/_lessons-learned/` — historical lessons. Stay.
- `Plan/JULES_PROTOCOL.md`, `Plan/JULES-REVIEW-LOOP.md` — operational protocols, not vision canon. Stay.

**Deferred lever disposition (recap):**
- **L-α / L-β / L-γ** become explicit roadmap items in `vision/specs/10-harness-ladder.md` §11 with `status: active` — they ship alongside the implementation tag.
- **L-δ / L-ε / L-ζ / L-η + progressive disclosure** become sections of `vision/specs/14-progressive-disclosure-roadmap.md` with `status: roadmap` — sequenced, dependency-aware, not yet scheduled.

**Spec 09 r2 reconciliation with the promoted Harness-in-Harness — stated plainly:**

Spec 09 and the promoted Harness ladder describe **the same isomorphism viewed from two different axes**.
- Spec 09 r2's axis: **caller-column × callee-column**, 9 cells, one MCP server, one envelope, four verbs at every cell boundary.
- Harness ladder's axis: **transport fidelity**, 3 layers, one MCP server, one envelope, four verbs at every layer boundary.

The single-MCP-server / single-envelope / single-four-verb invariants are **literally the same statements**. Neither supersedes the other. Wave 0's promotion makes the cross-axis citation explicit: spec 09 §3 bullets 1-2 cite `vision/specs/10-harness-ladder.md` §2 for the layer-fidelity axis, and 10-harness-ladder §2 cites `vision/specs/09-crossover-matrix.md` §2 for the matrix-cell axis.

## §5 Isomorphism + token-efficiency proof obligations

The FINAL aligned vision/ corpus must satisfy these four assertions, with anchors. Each is a one-liner the panel re-review (Wave 5) verifies.

1. **Isomorphism — at every layer L, a call to verb V with envelope E produces tool_result T(V, E) independent of L.**
   - Anchor: `vision/specs/11-four-verb-canon.md` §"L1↔L2↔L3 equivalence invariant" (new, authored in Wave 0).
   - Substrate: `Plan/harness/VOCABULARY.md:62-67` ("Cross-layer invariant: every layer exposes the same four verbs. A test that passes on L1 must pass on L2 must pass on L3").
   - Test: `tests/integration/test_devmode_server.py` (named in `Plan/harness/design.md:33` and `Plan/harness/VOCABULARY.md:66`).

2. **Token caps — CI test asserts boot context < 500 tokens, tools/list < 4 KB, per-tool result ≤ 4 KB.**
   - Anchor: `vision/specs/12-vocabulary.md` §1 (the invariant table, restated from `Plan/harness/VOCABULARY.md:42-46`).
   - Spec citation: `vision/specs/02-tool-result-envelope.md:65` (4 KB SHOULD; promoted to MUST for composition in `vision/specs/09-crossover-matrix.md:132-138`).
   - Test plan: `tests/smoke/test_boot_budget.py` (Spec 131; referenced from `Plan/harness/VOCABULARY.md:311`).

3. **Single registry — one CellRegistry, registered once at boot, accessed by all transports.**
   - Anchor: `vision/specs/10-harness-ladder.md` §5.2 (the `bin/agency` + `lib/devmode/` paragraph that fixes "same `create_mcp()` factory L1 imports — no fork").
   - Substrate: `Plan/harness/design.md:393` ("preserves the single-source-of-truth invariant: one `create_mcp()` factory, three transports on top of it").
   - Spec 09 anchor: `vision/specs/09-crossover-matrix.md:125-127` ("One MCP server. Every crossing routes through the same FastMCP instance").

4. **No domain backdoors — cross-column calls cannot bypass the four verbs.**
   - Anchor: `vision/specs/09-crossover-matrix.md:151-156` (the §3.1 paragraph forbidding `from agentic.<other_row>.handlers.<x> import handle` and naming `tests/agentic/test_pretooluse_veto.py` as the lint test).
   - Substrate: `vision/specs/11-four-verb-canon.md` §"No backdoors" (authored in Wave 0; restates the §3.1/§3.3 prohibitions for the lint surface).

These are not new constraints. They restate what Plan/harness/ canon and spec 09 r2 already say. The promotion in Wave 0 produces vision/ lines that match these obligations; Wave 5's lint scripts (`bin/lint-vision-schemas`, `bin/lint-no-bare-verbs`, etc.) operationalise them.

## §6 Risk register

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R1 | **Schema-tree split breaks runtime imports.** `context/_shared/schemas/` is imported by the running plugin; if Wave 1 moves canon to `vision/specs/schemas/` without a mirror, boot fails. | High | High | Wave 5 lint `bin/lint-vision-runtime-mirror` enforces equality. Wave 1's last edit is a one-shot copy from vision→runtime; subsequent edits land via a mirror script. Alternatively (escape hatch): treat `vision/specs/schemas/` as the source and generate `context/_shared/schemas/` at build time. Decide in Wave 1. |
| R2 | **Cross-row dispatch cycle goes undetected.** Spec 09 §3.2 cycle guard depends on `workflow_dispatch_depth` on the Session node; if the schema (F06) and the runtime check land out of sync, runaway recursion is possible. | Medium | High | Wave 1's `session.schema.json` edit + the body-text edit in `vision/specs/08-context-base-v1.md` land in a single PR. Spec 09 §4.6 error code `WORKFLOW_DISPATCH_CYCLE` is the failure signal; add a test case to the Wave 6 implementation. |
| R3 | **Promotion misses a Plan/harness/ lever that should be roadmap-canonical.** L-η or the progressive-disclosure 4-tier ladder is forgotten in Wave 0; the 5-deferred-levers count drifts. | Low | Medium | §4 promotion table above enumerates all 7 levers explicitly; Wave 0 acceptance includes a checklist that every Plan/harness/design.md §11.5 row maps to a vision/ landing site (10-harness-ladder §11 OR 14-progressive-disclosure-roadmap). |
| R4 | **Edge-canon delete on `SATISFIES_PHASE` breaks gate evaluation.** F12/F48/F47 recommend removing the edge entirely (Wave 1+2); but the workflow runner may depend on it for gate-satisfaction queries. | Medium | High | Wave 1's `vision/specs/schemas/context/edges/satisfies-phase.schema.json` edit is "pin direction" first, "delete" only after Wave 6 confirms no runtime caller. Conservative path: Wave 1 pins direction; Wave 6 (implementation) removes the edge if it proves unused. The two-stage approach defers the destructive change until runtime evidence is in. |
| R5 | **Wave 2's column-canon edits conflict with concurrent vision/-touching PRs.** If anyone is editing `vision/agentic/COLUMN.md` or `vision/workflow/COLUMN.md` while Wave 2 runs, merge conflicts wipe one or the other. | Medium | Medium | Sequence: pause vision/-touching PRs for the duration of Waves 1-4 (estimated 4-6 days elapsed). The CI lints from Wave 5 then act as a safety net for any subsequent edit. |

## §7 Estimate

**Critical path:** Wave 0 → Wave 1 → (Wave 2 + Wave 3 in parallel) → Wave 4 → Wave 5 → Wave 6.

**New files (Wave 0 + Wave 1):**
- 5 new vision/specs/0X.md files (10, 11, 12, 13, 14).
- 5 new schema files (`_shared/workflow-dispatch`, two watcher nodes, two four-verb request schemas).
- 1 new schema dir (`vision/specs/schemas/_shared/`).
- 4 new CI lint scripts (Wave 5).
- **Total: ~15 new artefacts.**

**Edits (Waves 1-4):**
- ~25 schema files touched in Wave 1.
- ~6 spec-text files touched in Wave 1.
- ~25-30 column-canon files touched in Wave 2.
- ~10 foundational files touched in Wave 3.
- ~15 frontmatter reciprocity edits in Wave 4.
- **Total: ~80-90 file edits.**

**Token cost estimate (Waves 0-5, documentation only):**
- Wave 0 (promotion): ~80-100 KB output across the 5 new specs.
- Wave 1 (schemas + spec text): ~40-50 KB of edits.
- Wave 2 (column reconciliation): ~30-40 KB of edits.
- Wave 3 (foundational): ~15-20 KB of edits.
- Wave 4 (cross-ref hygiene): ~5 KB.
- Wave 5 (lints + re-review): ~10-15 KB (lint scripts) + 1 panel pass (~50 KB output).
- **Total documentation token cost: ~250-300 KB output.** Roughly 3-5 Jules sessions for Waves 0-5, sequenced per the critical path.

**Wave 6 (implementation):** out of scope of this estimate; spec 09 plan + harness L3 work is weeks of effort.

**Critical-path waves (block downstream):** Wave 0 (substrate), Wave 1 (schema reconciliation), Wave 5 (re-review gate). Wave 2 and Wave 3 can run in parallel; Wave 4 is mostly mechanical.
