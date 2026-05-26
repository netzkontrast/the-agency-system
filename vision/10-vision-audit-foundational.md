---
slug: vision-audit-foundational
type: audit
status: ready
owner: claude
created: 2026-05-20
updated: 2026-05-20
summary: Findings from the post-spec-09-r2 audit of the foundational vision/ layer + the cross-reference hygiene of the entire vision/ tree.
audited:
  - vision/README.md
  - vision/00-charter.md
  - vision/00.1-Overview.md
  - vision/02-plan.md
  - vision/03-architecture.md
  - vision/04-nextsteps.md
  - vision/05-v0-1-retrospective.md
  - vision/NEXT-SESSION-PROMPT.md
  - vision/specs/01-cell-manifest.md
  - vision/specs/02-tool-result-envelope.md
  - vision/specs/03-sidecar-metadata.md
  - vision/specs/04-phase-state-envelope.md
  - vision/specs/05-gate-yaml.md
  - vision/specs/06-agentic-base.md
  - vision/specs/07-workflow-base.md
  - vision/specs/07-workflow-base-v1.md
  - vision/specs/08-context-base.md
  - vision/specs/08-context-base-v1.md
  - vision/specs/09-crossover-matrix.md
  - vision/specs/09-crossover-matrix-plan.md
---

# Vision audit — foundational layer + cross-ref hygiene (post spec-09 r2)

## §1 Index of findings

| # | file:line | severity | lens | one-line |
|---|---|---|---|---|
| F1 | vision/README.md:51-52 | HIGH | L2 stale supersede | README still links the **superseded** `specs/07-workflow-base.md` / `specs/08-context-base.md` in the canonical reading order; v1 successors exist but are absent from Canon §6. |
| F2 | vision/README.md:82-83 | HIGH | L2 phantom forward-ref | README "Out of scope" cites `specs/09-cross-row-dispatch.md`; the actual spec on disk is `specs/09-crossover-matrix.md`. Dead path + wrong concept. |
| F3 | vision/README.md:25 | MEDIUM | L1 stale status | README claims `vision/specs/schemas/workflow/` "patch ready; apply via tools/jules-patch-extract.py …" — but `vision/05-v0-1-retrospective.md:32` reports N1 merged in PR #157. Two-day-stale. |
| F4 | vision/README.md:17-29 | MEDIUM | L1 stale status | "Status snapshot" still shows the system pre-v0.1 (W5/C5 open). Retrospective says V2–V11 green and W5/C5 closed before merge. |
| F5 | vision/README.md (whole) | MEDIUM | L1 silent on 09 | README's Canon §5–§7 ends at `specs/06–08`; spec 09 r2 (the anchor of this audit) is not referenced from the foundational map at all. |
| F6 | vision/00-charter.md:178-182 | LOW | L3 founding-intent | Charter scenario 10 frames cross-row dispatch as agentic→workflow only ("R1 agentic dispatches into R2 workflow"). Spec 09 r2 generalises to a 3×3 caller-column × callee-column matrix — legitimate drift, but neither charter nor 00.1 acknowledges the broadening. |
| F7 | vision/00-charter.md:88-110 | LOW | L1 stale repo refs | "Quarantined material" lists `claude/agency-system-refactor-wSuD3` PR #133; that PR is long-closed history. Read-order block (Plan/JULES_PROTOCOL.md, Plan/harness/VOCABULARY.md) is still authoritative — keep. |
| F8 | vision/00.1-Overview.md:34-37 | HIGH | L1 architecture conflict | Q1 resolution declares "per-row **artifact registry** (`result/<row>/`)". `vision/03-architecture.md:124-134` and `vision/04-nextsteps.md:166` explicitly retire `result/<row>/` in favour of artifact drivers. The 00.1 STATUS preamble (line 16) hedges but the §2 body still reads as the architectural answer. |
| F9 | vision/00.1-Overview.md:47-49 | HIGH | L1 architecture conflict | §3 "Resolving Edge Cases" prescribes a `track.meta.json` sidecar — the exact pattern `vision/03-architecture.md` §5.2/§8 declares dead and `vision/specs/08-context-base-v1.md` retires. |
| F10 | vision/02-plan.md:23 + (whole) | HIGH | L1 stale | 02-plan calls itself "complete"; its `affects:` and read-order still point at the non-v1 specs (06/07/08) without acknowledging the v1 rewrites or spec 09. Reads as authoritative for the pre-v0.1 wave only. |
| F11 | vision/02-plan.md:163-164 | HIGH | L2 phantom forward-ref | Same `specs/09-cross-row-dispatch.md` + `specs/10-bootloader.md` planned-files claim; both are still absent (`10-bootloader.md` legitimately deferred, `09-cross-row-dispatch.md` was renamed to `09-crossover-matrix.md`). |
| F12 | vision/03-architecture.md:16-17 | HIGH | L2 stale supersede | `referenced_by:` lists `vision/specs/07-workflow-base.md` + `vision/specs/08-context-base.md`. Per `vision/specs/07-workflow-base-v1.md:23` and `08-context-base-v1.md:24` those files are superseded; the v1 successors are not in the `referenced_by` set. |
| F13 | vision/03-architecture.md:182-200 | MEDIUM | L1 stale prescriptive language | §8 still says specs 07/08 "need a v1 rewrite" in future tense; both v1 specs landed. The future-tense list should be in past tense or removed. |
| F14 | vision/03-architecture.md:223-224 | HIGH | L2 phantom forward-ref | §10 names `specs/09-cross-row-dispatch.md` + `specs/10-bootloader.md` as "out of scope for this document". 09 is on disk under a different slug; 10 still missing. |
| F15 | vision/04-nextsteps.md (whole) | HIGH | L1 stale | "Next-step" plan, but the retrospective says all of N0–N5 shipped. The file is now history, not a plan. Frontmatter `status: ready` should be `superseded` or `archived`. |
| F16 | vision/04-nextsteps.md:162-163 | HIGH | L2 phantom forward-ref | "Cross-row dispatch (planned `specs/09`)" still calls 09 a future cross-row-dispatch spec; it is now spec 09 r2 crossover matrix, on disk. |
| F17 | vision/05-v0-1-retrospective.md:178-211 | MEDIUM | L1 scope creep | The retrospective silently absorbs a "v0.3 jules-orchestration" milestone that no foundational doc planned for. README §Status snapshot does not mention v0.3 at all. |
| F18 | vision/05-v0-1-retrospective.md (whole) | MEDIUM | L2 asymmetric ref | Retrospective `referenced_by: [vision/README.md]`, but `vision/README.md` does not link to `05-v0-1-retrospective.md` anywhere; only the v0.3 narrative cites it indirectly. |
| F19 | vision/NEXT-SESSION-PROMPT.md (whole) | HIGH | L1 fully stale | The prompt drops a fresh session into N0 of `04-nextsteps.md`. N0–N5 are done. If pasted, it would re-execute completed work. Either delete, archive, or replace with a "next milestone" prompt. |
| F20 | vision/specs/07-workflow-base.md (frontmatter) | MEDIUM | L2 asymmetric supersede | The superseded file does not carry `superseded_by:` frontmatter; only the v1 successor declares `supersedes:`. Half the chain. |
| F21 | vision/specs/08-context-base.md (frontmatter) | MEDIUM | L2 asymmetric supersede | Same — no `superseded_by:`, despite 08-v1 declaring `supersedes:`. |
| F22 | vision/specs/03-sidecar-metadata.md (frontmatter) | MEDIUM | L2 asymmetric supersede | `08-context-base-v1.md:24` declares `supersedes: vision/specs/03-sidecar-metadata.md`, but 03's own frontmatter does not carry `superseded_by:`. Inline §STATUS at 03:21-23 hints at it but the structural pointer is missing. |
| F23 | vision/specs/02-tool-result-envelope.md:14 | MEDIUM | L2 asymmetric ref | 02 declares `referenced_by: [04, 06, 08]` — does NOT list `09-crossover-matrix.md`, which depends on 02 explicitly (09:24). Spec 09 r2 was added without updating its dependencies' `referenced_by:` sets. Same pattern applies to specs 04, 06, 07-v1, 08-v1 — all listed in 09's `depends_on:` (09:24-28) but none updated their `referenced_by:`. |
| F24 | vision/specs/09-crossover-matrix.md:46 | LOW | L2 self-aware | 09 sets `referenced_by: []`. Truthful for now (only `09-crossover-matrix-plan.md` and `09-crossover-matrix-review.md` reference 09, both inside the spec set) — but the cross-doc reciprocity in F23 is the bigger issue. |
| F25 | vision/specs/09-crossover-matrix.md:116, 521, 951 | LOW | L2 forward-pointing | 09 r2 references `vision/specs/schemas/_shared/workflow-dispatch.schema.json` and proposes new schemas under `vision/specs/schemas/context/nodes/` (watcher-emission, watcher-health). None exist on disk yet — but they are explicitly proposed-in-spec, not phantom refs. The reader needs to read 09 §4 before chasing the path. Flag as expected-pre-impl. |
| F26 | vision/specs/04-phase-state-envelope.md:21 (STATUS) | LOW | L1 still helpful | Spec 04 carries an accurate "partial-deprecation" STATUS pointing readers at 03-architecture §4 / §9. Good model for what 03 / 07 / 08 should do. |
| F27 | vision/00.1-Overview.md:9-12 | LOW | L2 self-ref | `affects:` lists `vision/00-charter.md` even though 00.1 only **succeeds** the charter; this is more "supersedes" than "affects". Cosmetic. |
| F28 | vision/00-charter.md (frontmatter) | MEDIUM | L2 asymmetric supersede | Charter line 12 says "Successor: see 00.1"; frontmatter does not encode `superseded_by:`. Parallel to F20/F21/F22. |

Severity totals: 9 HIGH, 11 MEDIUM, 8 LOW. Counts: ~6 dead/wrong inline links, ~9 asymmetric refs (frontmatter or implicit), ~5 stale supersede chains (07→07-v1, 08→08-v1, 03→08-v1, 00→00.1, the "specs/09-cross-row-dispatch" phantom across 4 files).

## §2 Lens 1 — Foundational doc currency

The foundational layer (`README`, `00-charter`, `00.1-Overview`, `02-plan`, `03-architecture`, `04-nextsteps`) was written in the 2026-05-19 wave that landed the base layer; the v0.1 retrospective + spec 09 r2 (2026-05-20) made most of it stale within 24h.

### `vision/README.md`

Reads as a snapshot of "two integration gaps remain". The retrospective contradicts almost every line of the Status snapshot:

- 51-52: Canon §6 still names the non-v1 specs as authoritative. 07-v1 and 08-v1 are not in Canon at all. (F1)
- 82-83: Out-of-scope block invents `specs/09-cross-row-dispatch.md` and `specs/10-bootloader.md`. Spec 09 r2 is on disk as `09-crossover-matrix.md` and is the anchor of this audit. (F2)
- 25: Workflow schemas claim "patch ready; apply via tools/jules-patch-extract.py 17230962122169358495" — `05-v0-1-retrospective.md:32` says N1 already merged in PR #157. (F3)
- 17-29: W5 / C5 listed as open follow-ups; `05-v0-1-retrospective.md:31` reports both closed in N0 (`979eb73`). (F4)
- No mention of spec 09, no mention of the v0.3 jules-orchestration milestone. (F5, F17)

### `vision/00-charter.md`

Cleanly marks itself "Superseded" at line 12. Quarantined-material section (88-110) is dated but harmless. Scenario 10 (178-182) names the harness-in-harness pattern as **agentic→workflow** — spec 09 r2 generalises to a 3×3 matrix; this is the legitimate drift documented in §4 below. (F6, F7, F28)

### `vision/00.1-Overview.md`

§2 Result Registry (32-37) reads "per-row artifact registry (`result/<row>/`)". `03-architecture.md:124-134` and `04-nextsteps.md:166` retire that directory in favour of pluggable artifact drivers. The STATUS preamble (16) hedges with "the *concept* is preserved … the *mechanism* has been refined" — but the §2 body still presents the registry as the authoritative answer. §3 (47-49) prescribes a `track.meta.json` sidecar — explicitly retired by 03-architecture §8 and 08-context-base-v1.md §FR5. (F8, F9, F27)

### `vision/02-plan.md`

Status line (23) declares "Plan complete". The body still reads as a forward plan for the base layer wave: read-order at 56-57 still names `07-workflow-base.md` and `08-context-base.md`; "what happens after" at 161-164 still calls 09 the "cross-row-dispatch" spec. The frontmatter `affects:` (10-18) only contains the pre-v1 spec list; spec 09 r2 and the v1 successors are absent. (F10, F11)

### `vision/03-architecture.md`

Architecturally still the most useful doc. Two staleness symptoms:

- 16-17 (`referenced_by:`) still lists non-v1 specs. (F12)
- 182-200 (§8 "Consequences for the spec set") is written in future tense ("need a v1 rewrite"). Both v1 specs have shipped. (F13)
- 223-224 (§10) repeats the phantom spec-09 name. (F14)

Otherwise: the doc's runtime model survives spec 09 r2 cleanly. Spec 09 builds **on** 03's "one engine, one graph, drivers" framing rather than fighting it.

### `vision/04-nextsteps.md`

Entirely retrospective work — all phases shipped. The frontmatter still says `status: ready`. It should be `superseded` (by `05-v0-1-retrospective.md`) or `archived`. (F15, F16)

### `vision/05-v0-1-retrospective.md`

Honestly written but quietly extends scope to "v0.3 jules-orchestration" (178-211) — a milestone that no upstream foundational doc planned. The state machine, the new ontology nodes, the new gates: all real and shipped, but invisible from `vision/README.md`. (F17, F18)

### `vision/NEXT-SESSION-PROMPT.md`

The prompt instructs a fresh session to execute N0–N5 of `04-nextsteps.md`. All of those phases shipped. A fresh session pasting this would either re-do completed work or get confused by the discrepancy. (F19)

## §3 Lens 2 — Cross-reference hygiene

### §3.1 Dead links / phantom forward-refs

| # | file:line | broken-ref | reality |
|---|---|---|---|
| D1 | vision/README.md:82 | `specs/09-cross-row-dispatch.md` | File is `vision/specs/09-crossover-matrix.md`; concept also broadened (3×3, not just cross-row). |
| D2 | vision/README.md:83 | `specs/10-bootloader.md` | Does not exist; legitimately deferred. |
| D3 | vision/02-plan.md:163 | `specs/09-cross-row-dispatch.md` | Same as D1. |
| D4 | vision/02-plan.md:164 | `specs/10-bootloader.md` | Same as D2. |
| D5 | vision/03-architecture.md:223 | `specs/09-cross-row-dispatch.md` | Same as D1. |
| D6 | vision/03-architecture.md:224 | `specs/10-bootloader.md` | Same as D2. |
| D7 | vision/04-nextsteps.md:162 | `specs/09` "cross-row dispatch" | Same as D1 — the inline language still calls it cross-row-dispatch. |
| D8 | vision/04-nextsteps.md:163 | `specs/10` | Same as D2. |
| D9 | vision/README.md:25 | "Apply in next session via tools/jules-patch-extract.py 17230962122169358495" | Per retrospective :32 this landed in PR #157 already. |
| D10 | vision/specs/09-crossover-matrix.md:116, :521, :951 | `vision/specs/schemas/_shared/workflow-dispatch.schema.json` and proposed `watcher-emission.schema.json` / `watcher-health.schema.json` | Not on disk yet; explicitly named "(NEW)" in 09 §4 — expected-pre-impl. (Listed for completeness; not strictly a hygiene defect, but a reader chasing the path before reading §4 will hit 404.) |

### §3.2 Asymmetric refs (frontmatter)

| # | file | declares | the other side does not |
|---|---|---|---|
| A1 | vision/specs/09-crossover-matrix.md:24 | `depends_on: vision/specs/02-tool-result-envelope.md` | 02-tool-result-envelope.md:14 `referenced_by:` does not list 09. |
| A2 | vision/specs/09-crossover-matrix.md:25 | `depends_on: vision/specs/04-phase-state-envelope.md` | 04:14 `referenced_by:` does not list 09. |
| A3 | vision/specs/09-crossover-matrix.md:26 | `depends_on: vision/specs/06-agentic-base.md` | 06:16 `referenced_by: []`. |
| A4 | vision/specs/09-crossover-matrix.md:27 | `depends_on: vision/specs/07-workflow-base-v1.md` | 07-v1:22 `referenced_by: []`. |
| A5 | vision/specs/09-crossover-matrix.md:28 | `depends_on: vision/specs/08-context-base-v1.md` | 08-v1:22 `referenced_by:` only lists 07-v1, not 09. |
| A6 | vision/specs/09-crossover-matrix.md:12 | `depends_on: vision/00-charter.md` | Charter has no frontmatter `referenced_by:` field at all. |
| A7 | vision/specs/09-crossover-matrix.md:13 | `depends_on: vision/00.1-Overview.md` | 00.1 has no `referenced_by:` field. |
| A8 | vision/specs/09-crossover-matrix.md:14 | `depends_on: vision/03-architecture.md` | 03:14 `referenced_by:` does not list 09. |
| A9 | vision/specs/09-crossover-matrix.md:15-23 | `depends_on:` lists 6 per-column INTERFACE-TO-*.md files | None of them carry `referenced_by:` frontmatter (sibling-tree audit's scope; flagged because it's the same asymmetry pattern). |
| A10 | vision/specs/09-crossover-matrix-plan.md:12 | `depends_on: vision/specs/09-crossover-matrix.md` | 09:46 `referenced_by: []` does not list the plan or the review. |
| A11 | vision/specs/05-v0-1-retrospective.md:15 | `referenced_by: vision/README.md` | README contains no link to 05-v0-1-retrospective.md (greppable verification — 0 hits). |
| A12 | vision/specs/03-architecture.md:11-17 | `depends_on: 00.1, 02-plan; referenced_by: README, 07-workflow-base, 08-context-base` | 02-plan:10-18 has no `referenced_by:` at all; the non-v1 successors listed in `referenced_by:` are themselves stale (F12). |

### §3.3 Stale supersede chains

| # | superseded file | supersedes-by exists? | superseded_by frontmatter on the old file? |
|---|---|---|---|
| S1 | vision/specs/07-workflow-base.md | Yes — 07-workflow-base-v1.md:23 declares `supersedes: [07-workflow-base.md]` | NO — 07-workflow-base.md frontmatter does not carry `superseded_by:`. Inline STATUS at body line 45 hints; frontmatter is silent. (F20) |
| S2 | vision/specs/08-context-base.md | Yes — 08-context-base-v1.md:24 declares `supersedes: [08-context-base.md]` | NO — same pattern. (F21) |
| S3 | vision/specs/03-sidecar-metadata.md | Yes — 08-context-base-v1.md:24-26 declares `supersedes: [..., 03-sidecar-metadata.md]` | NO — 03's frontmatter does not carry `superseded_by:`. Inline §STATUS preamble at 03:21-23 says so; the frontmatter pointer is missing. (F22) |
| S4 | vision/00-charter.md | Yes — 00.1-Overview.md:11-12 `affects: [vision/00.1, vision/00-charter]` and inline at 00.1:18 "supersedes 00-charter" | NO — 00-charter has no frontmatter `superseded_by:`. Inline line 12 "Successor: see 00.1" is the only signal. (F28) |
| S5 | (logical) vision/04-nextsteps.md | Effectively superseded by 05-v0-1-retrospective.md (all phases shipped) | NOT declared anywhere. 04 still reads as a forward plan; 05's `depends_on:` cites 04 but does not declare itself as a successor. (F15) |
| S6 | (logical) vision/NEXT-SESSION-PROMPT.md | Effectively superseded (the milestone it spawns is shipped) | NOT declared anywhere. (F19) |
| S7 | (logical) vision/02-plan.md | Effectively superseded — the base layer it plans is shipped + v1 specs landed | Inline line 23 "Plan complete"; no successor in frontmatter. (F10) |

### §3.4 Downstream awareness gap

Every doc that referenced 07/08 pre-supersede should now know about 07-v1/08-v1. Reality:

- `vision/README.md` Canon §6 (51-52): NO update to v1.
- `vision/02-plan.md` :56-57: NO update.
- `vision/03-architecture.md` :16-17 (frontmatter `referenced_by:`): NO update.
- `vision/04-nextsteps.md` :101-102: Knows about v1 (only inline-doc that does).
- `vision/05-v0-1-retrospective.md` :12-13: Knows about v1.
- `vision/NEXT-SESSION-PROMPT.md` :60: Knows about v1 inline.

The v1 awareness gap is concentrated in `README` / `02-plan` / `03-architecture` — the canonical entry points.

## §4 Lens 3 — Founding intent vs spec 09 r2

### Charter language (foundation)

`vision/00-charter.md:78-85`:

> Jules WAS a top-level domain. Under the matrix, Jules is **a row, not a column** — `agentic/jules`, `workflow/jules`, `context/jules`. The "harness-in-harness" recursion (one agent orchestrating others) is a **property of the agentic column**, not its own domain: any row's agentic cell may dispatch into other rows' cells, and that cross-row dispatch is recorded as a graph edge.

`vision/00-charter.md:178-182` (scenario 10):

> Scenario: Harness-in-harness (cross-row dispatch)
>   Given an agentic cell from row R1 dispatches into a workflow cell from row R2
>   When the dispatch occurs
>   Then the dispatching handler uses the SAME four-verb contract as a leaf cell
>   And the graph records the cross-row dispatch edge with both row identities

`vision/00.1-Overview.md:28`:

> **`agentic` column**: The WHO and HOW. Owns intent-to-action routing (skills), tool definitions (MCP handlers), and cross-row dispatch (harness-in-harness). Does *not* own pipelines or state.

### Spec 09 r2 framing

`vision/specs/09-crossover-matrix.md:49-66`:

> # Spec 09 — The 3x3 Column-Crossover Matrix
> Locks the dispatch primitive and envelope for every (caller, callee) column pair. 3/9 cells are already built …

09 r2 §2 (matrix table at 104-108) introduces a **caller-column × callee-column** matrix — agentic↔agentic, workflow↔workflow, context↔context, plus the 6 mixed pairs. Each of the 9 cells gets a "single dispatch mechanism".

### Is this drift?

YES — legitimate but unacknowledged.

**Charter and 00.1 frame "cross-row dispatch" exclusively as a property of the agentic column** (00-charter:80-82; 00.1:28). The founding-intent unit was **rows crossing rows through agentic**. Cross-row was the axis of variation; columns were assumed homogeneous-per-cell.

**Spec 09 r2 re-axes the problem around columns.** "Cross-row" disappears from the cell names; "caller column × callee column" replaces it. workflow→workflow chaining (09 §3.5) — an entirely new primitive that the charter did not anticipate — gets first-class treatment. context→workflow watcher cells (09 §3.8) — another new primitive — likewise.

This is a real conceptual broadening from "cross-row dispatch lives in agentic" to "every column-to-column crossing has a contract". Three observations:

1. The broadening is **architecturally legitimate**: `vision/03-architecture.md` §4 already says "workflows are paths through the graph" — once that's true, a workflow phase calling another workflow phase is a graph traversal step, not a category error. Spec 09 r2 just names what 03-architecture left implicit.
2. The broadening is **silent in the foundational layer**: neither the charter nor 00.1-Overview nor 03-architecture acknowledges that the "harness-in-harness" framing has been replaced. Spec 09's reconciliation table at 969-979 lists prior names from per-column INTERFACE-TO-*.md files; it does NOT reconcile against the charter's single-column framing.
3. The charter's scenario 10 is now too narrow: "R1 agentic dispatches into R2 workflow" is one of 9 cells in 09 r2, not the only kind of crossing.

**Recommendation flag (not a rewrite)**: foundational docs need to acknowledge that the "harness-in-harness" model is one of nine crossings, not the only crossing. The 3×3 framing should be hoisted from spec 09 into 00.1-Overview or 03-architecture so the foundational reading order tells the new story.

### Other intent checks

- **Charter rule "name-driven discovery" (00-charter:55-57)**: respected by 09 r2 — every dispatch routes through `mcp__<row>_<verb>` (09 §3.2, §3.5), which the deriver produces from `(row, column)`. No substring-search regressions.
- **Charter rule "column isomorphism" (00-charter:45-49)**: respected — 09 r2 contracts apply uniformly per cell type, not per row.
- **Charter rule "row isomorphism" (00-charter:51-54)**: respected — the worked example pattern in 09 is single-row (jules); inter-row chaining (09 §3.5) goes through `mcp__call_tool` symmetrically.
- **00.1 result-registry conclusion (00.1:32-37)**: ignored by 09 r2, but that's fine — 09 routes overflow through `data.artefact_ref` and `Artefact` graph nodes per 03-architecture. The drift here is in 00.1 (F8/F9), not 09.
- **Cold-boot < 500 tokens (00-charter:185-188)**: spec 09 r2 §6 deferral on watcher schemas (`spec TBS #5 ... boot payload accounting for watcher schemas`) protects this. Honoured.

## §5 Per-file verdict

| file | verdict |
|---|---|
| vision/README.md | **needs-touch (5 findings)** — Canon §6 v1 update, drop phantom 09/10 names, refresh Status snapshot for post-v0.1, surface 05-retrospective + spec 09. |
| vision/00-charter.md | **needs-touch (2 findings, both LOW)** — add frontmatter `superseded_by: vision/00.1-Overview.md`; consider an inline note that scenario 10's framing is one of nine crossings per spec 09. Doc itself reads as "kept for traceability" and that intent survives. |
| vision/00.1-Overview.md | **needs-touch (2 findings, both HIGH)** — §2 / §3 still describe the dead `result/<row>/` registry + `track.meta.json` sidecar. STATUS preamble hedges but the body needs the contradiction removed. |
| vision/02-plan.md | **superseded (3 findings)** — frontmatter says `status: complete`; doc reads as a pre-shipped forward plan. Mark archived; redirect readers to 04-nextsteps + 05-retrospective. |
| vision/03-architecture.md | **needs-touch (3 findings)** — `referenced_by:` update to v1 specs; §8 should move from future-tense plan to past-tense status; phantom spec-09/10 refs in §10. Otherwise architecturally sound and unaffected by spec 09 r2. |
| vision/04-nextsteps.md | **superseded (2 findings)** — all phases shipped per `05-v0-1-retrospective.md`. Reframe as archived plan. |
| vision/05-v0-1-retrospective.md | **needs-touch (2 findings)** — v0.3 jules-orchestration creep is real shipped work; add it to README's status snapshot. Asymmetric `referenced_by` since README does not link back. |
| vision/NEXT-SESSION-PROMPT.md | **superseded (1 finding)** — prompt drops into completed work. Either delete or rewrite for the next milestone (which would be Wave A of `09-crossover-matrix-plan.md`). |

## §6 Headline blockers

Three items in the foundational layer must be resolved before spec 09 r2 can leave `draft`:

1. **Foundational forward-refs to spec 09 are wrong by name and by concept.** `vision/README.md:82`, `vision/02-plan.md:163`, `vision/03-architecture.md:223`, `vision/04-nextsteps.md:162` all call spec 09 "cross-row dispatch" — a 1×1 framing within agentic. Spec 09 r2 is a 3×3 crossover matrix. A reader following the foundational read-order arrives expecting one thing and finds another. Fix the names AND surface the broadened scope in 00.1-Overview or 03-architecture so the foundational layer narrates what 09 r2 actually delivers (F2/F11/F14/F16, and §4 drift).

2. **The 00.1-Overview "Result Registry" + sidecar prescriptions still read as the architectural answer.** `vision/00.1-Overview.md:34-37` and `:47-49` prescribe `result/<row>/` + `track.meta.json` — both retired by `03-architecture.md` and `08-context-base-v1.md`. 09 r2's `data.artefact_ref` overflow path (09 §3 third bullet; 09 §4.1) depends on the artefact-driver model; if the foundational doc still reads as endorsing the registry+sidecar pattern, downstream readers will keep wiring to the dead model. The STATUS preamble at 00.1:16 is not enough — the §2/§3 body needs to either be rewritten or sliced into a "historical" annex. (F8/F9)

3. **The post-v0.1 reading order is broken.** `vision/README.md` Canon §6 still lists the **superseded** 07/08 specs; v1 successors do not appear; 05-v0-1-retrospective is referenced-by-README per its frontmatter but README contains no link; v0.3 jules-orchestration is invisible from the foundational map. Spec 09 r2 builds on 06 + 07-v1 + 08-v1 (09:26-28) — a reader who follows README will not discover the v1 specs, let alone spec 09. Fix Canon §6 to point at the v1 specs, add a Canon entry for spec 09 r2, and link 05-retrospective from the Status snapshot. (F1/F4/F5/F11/F18)

These three blockers are about navigation and prescription, not about spec 09's contracts. Spec 09 r2 itself is internally consistent; the foundational layer beneath it is not.
