# Dramatica Decidability Matrix (embedded brief)

> **Source**: research agent `a78bd055cd15ef572` ("Dramatica Decidability Matrix for Novel-Writing MCP"). This file embeds the **matrix + recommendations**; the full plan-dump is not reproduced. Cite this file from Spec 013's Approach and from `lib/dramatica/navigator.py` docstrings.

## Context (one paragraph)

The novel-writing MCP sits on four assets that already encode Dramatica as data: per-term YAML frontmatter in `dramatica-vocabulary/references/*.md` (each anchor carries `id`, `kind`, `dynamic_pair_id`, `quad_id`, `ktad_position`, `class_id/type_id/variation_id`); the canonical `ontology.json` (304 entries across 11 kinds — 4 classes, 16 types, 62 variations, 63 elements, 8 archetypes, 4 character-dynamics, 4 plot-dynamics, 4 throughlines, 65 dynamic-pairs, 35 quads, 38 concepts); `scenarios.json` (12 indexed scenarios); and NCP v1.3.0 schema (463 appreciation enums + 144 narrative_function enums). Because every structural relationship a storyform asserts is already a typed edge in that graph, a large share of Dramatica coherence is **purely decidable** — graph lookups, set-membership tests, permutation checks. Judgement calls collapse to a narrow band (which slot a piece of prose *encodes*, whether a scene *feels like* its declared throughline).

## Decidability matrix (15 rows: 11 decidable + 2 hybrid + 2 judgement)

| # | Check | Decidable / Judgement | Tool / Skill | State touched |
|---|---|---|---|---|
| 1 | Dynamic-pair reciprocity (A.dynamic=X ⇒ partner.dynamic=anti-X) | **Decidable** | `coherence.check_dynamic_pair_reciprocity` | NCP + ontology.json (`dynamic_pair_id`) |
| 2 | KTAD coherence (every Quad's 4 elements cover K, T, A, D exactly once) | **Decidable** | `coherence.check_ktad_coverage` | ontology.json (`ktad_position` + `quad_id`) |
| 3 | Element-Quad integrity (Quad has exactly 4 elements; all 4 present if any is) | **Decidable** | `coherence.check_quad_completeness` | ontology.json (`quad_id` reverse-index) |
| 4 | Class/Type/Variation slot-fill completeness (4 throughlines × 4 slots = 16 mandatory) | **Decidable** | `storyform.check_slot_fill` | NCP + ontology.json |
| 5 | Throughline partition (4 throughlines exhaust {OS, MC, IC, RS}; no Class duplicated) | **Decidable** | `storyform.check_throughline_partition` | NCP only |
| 6 | Crucial Element placement (declared Crucial Element lives in MC throughline's Class) | **Decidable** | `storyform.check_crucial_element_placement` | NCP + ontology.json |
| 7 | MC Resolve ↔ Outcome ↔ Judgment consistency (enum-pair lookup; 8 legal triples) | **Decidable (table-lookup)** | `storyform.check_resolve_outcome_judgment` | ontology.json (`plot-dynamic` kind) |
| 8 | Approach (Be-er/Do-er) ↔ MC Concern coherence (Be-er↔Mind/Psychology; Do-er↔Universe/Physics) | **Mostly decidable** | `storyform.check_approach_concern` (emits WARN not FAIL) | ontology.json |
| 9 | Mental Sex (Linear/Holistic) ↔ MC Problem-Solving Style | **Decidable** | `storyform.check_mental_sex_problem_solving` | NCP only |
| 10 | Signpost ordering (4 signposts per throughline follow Type-permutation rule per `{Class, Driver, Limit}`) | **Decidable** | `storyform.check_signpost_permutation` | ontology.json (`type` kind, precompiled permutation table) |
| 11 | Storybeat → moment refs (NCP `storybeats[]` ↔ `moments[]` foreign-key + cardinality) | **Decidable (referential)** | `coherence.check_storybeat_moment_refs` | NCP only |
| 12 | Appreciation enum validation (one of 463) | **Decidable** | `ncp_author.validate_appreciations` (passthrough) | NCP schema |
| 13 | Narrative-function enum validation (one of 144) | **Decidable** | same | NCP schema |
| 14 | Scene-Level Bridge Q1–Q5 (dominant throughline, signpost timing, conflict flavor, arc, thematic beat) | **Judgement** | Skill `novel-architect-scene` (Wave A agency) | NCP + scene prose |
| 15 | Encoding suggestions ("how do I make this Element visible?") | **Judgement** | Skills `dramatica-vocabulary` + `chapter-writer` | ontology.json |

**The 11 decidable checks are the work-list for `novel_coherence_check` in Spec 013.**

## Recommendations (verbatim from the brief)

**One unified entry point.** Build `novel_coherence_check(work_id) -> CoherenceReport` as the parallel to bitwize's `album_coherence_check`. It calls every decidable check in the matrix, accumulates violations, returns a single typed report. Decidable checks are cheap (graph lookups against a 304-entry ontology) and independent — straightforward fan-out + merge. Co-locate them in `agency_mcp.handlers.novel.coherence` (referential/structural integrity) and `agency_mcp.handlers.novel.structure` (storyform-internal consistency). Mirror bitwize's `album_coherence_correct` with `novel_coherence_correct(work_id, autofix={"pair_reciprocity", "slot_typing"})` for mechanical fixes (flip declared partner to its `dynamic_pair_id` target).

**Lowest-token-cost output shape.** Optimise the report (it is what the LLM reads back):

```json
{"status":"FAIL","violations":3,"checks":{
  "pair_reciprocity":{"status":"FAIL","items":[{"a":"el.morality","expected":"el.self-interest","got":"el.attitude"}]},
  "ktad_coverage":{"status":"PASS"},
  "throughline_partition":{"status":"FAIL","items":[{"duplicate_class":"class.universe","throughlines":["OS","IC"]}]},
  "signpost_permutation":{"status":"FAIL","items":[{"throughline":"OS","got":["t.past","t.future","t.present","t.progress"],"hint":"see allowed_permutations[class.universe]"}]}
}}
```

Drop PASS-check `items` arrays (only emit on FAIL). Use ontology ids, not labels — the LLM resolves labels from the ontology when prose is needed. Cap each violation at ~120 chars. A 3-violation report fits in ~400 tokens; a clean PASS in ~40.

**Judgement-required checks are skills, not tools.** Q1–Q5 Scene-Level Bridge, encoding suggestions, and "does this draft *feel* like a Change-MC story" all require craft reasoning across prose + structure. Tools *surface inputs* to those skills (e.g. `storyform.get_quad_menu(element_id)` returns the 3 sibling Elements + their dynamic pairs as encoding options) but never adjudicate. **Contract: tools assert structure, skills assert meaning.**

**Spec feed-forward.** Spec 012 (`dramatica-and-ncp-libs`) freezes the NCP-side ids the coherence checks consume (`crucial_element.id`, `mc_throughline.class_id`, `storybeats[].id`, `moments[].storybeat_ref`) and ships the read-only ontology accessors (`get_quad`, `get_dynamic_pair`, `get_allowed_signpost_permutations`, `resolve_term`). Spec 013 (this one) owns the 11 decidable handlers + the unified report. Keep `ontology.json` as the single source of truth; never duplicate its tables into handler code — load once, cache, reference by id.

## Files referenced (from the agency vendor repo, read-only)

- `maintenance/schemas/narrative-ontology/ontology.json` — 304 indexed entries, 11 kinds
- `maintenance/schemas/narrative-ontology/ontology.schema.json` — entry contract
- `maintenance/schemas/narrative-ontology/term-frontmatter.schema.json` — per-term YAML contract (includes the `allOf` clause that already enforces `dynamic-pair` symmetry)
- `maintenance/schemas/narrative-ontology/scenarios.json` — 12 scenario keys (6 novel, 6 lyric)
- `skills/dramatica-vocabulary/references/dynamic-pairs-index.md` — 75 reciprocal pairs (machine-extractable)
- `skills/dramatica-vocabulary/references/element-quads.md` — KTAD pattern + 16 Variation Quads
- `skills/dramatica-vocabulary/references/encoding-patterns.md` — encoding pedagogy (judgement-anchor for skills)
- `tools/dramatica-nav/` — `nav.py`, `extract.py`, `validate.py`, `ontology-build.py` (validator that already enforces frontmatter↔ontology agreement; reuse, don't reimplement)
- `skills/ncp-author/` — owns NCP schema validation (call into it from `novel_coherence_check` for appreciation/narrative_function enum checks; don't duplicate)
