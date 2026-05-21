# Chapter Zero — Design-Loop Protocol

The multi-agent loop that turns the source chapter into a ship-ready album
concept. Three guard lenses, one synthesis, automatic convergence. Every agent
reads `SOURCE/loop/NAVIGATION.md` first.

## Goal (the bar every round is measured against)

A translation of *Kapitel 0 — Kohärenz Protokoll* that is simultaneously:
1. **Faithful** — a 1:1 transfer of the source (fidelity lens),
2. **Feasible** — buildable in Suno via the bitwize chain (feasibility lens),
3. **Listenable** — enriching for a novel reader *and* accessible/enjoyable for a
   music lover who never read it (accessibility lens).

## Two loop modes

The loop runs in one of two modes per round. **Divergent mode** is the richer
front-end used to open up or significantly improve a design; **Default mode** is
the steady-state critique→converge loop. The Opus arbiter at the end of a
divergent round feeds its mediated synthesis into the next default round.

### Divergent mode (3 isolated designs → adversary → tri-review → mediating arbiter)

Use when the design space should be re-opened or sharply improved (e.g. Round 3).

```
PHASE 1 — DESIGN ×3 (Opus, parallel, ISOLATED)
   one agent per goal-concern, each maximizing ITS concern only:
   ├─ Fidelity-Design      → SOURCE/loop<n>/design-fidelity.md
   ├─ Feasibility-Design   → SOURCE/loop<n>/design-feasibility.md
   └─ Accessibility-Design → SOURCE/loop<n>/design-accessibility.md
   ISOLATION RULE: no design agent sees another's brief or output. Each is told
   the other concerns are handled separately and must NOT hedge/balance — push
   its concern to its strongest, most uncompromising form. Divergence is the goal.
        ▼
PHASE 2 — ADVERSARIAL (Opus)
   critical-thinking decomposition of the 3 designs; arranges them into the
   MAXIMALLY clashing conflicts (steel-man each side, expose real
   incompatibilities) → SOURCE/loop<n>/adversarial.md
        ▼  (all FOUR docs — the 3 designs + the adversarial map — feed forward)
PHASE 3 — TRI-REVIEW (Opus, parallel)
   each reads ALL FOUR docs and weighs in from its lens:
   ├─ Review agent (feasibility)   → SOURCE/loop<n>/review.md
   ├─ Listener agent (accessibility) → SOURCE/loop<n>/listener.md
   └─ Spec-Panel agent (fidelity)  → SOURCE/loop<n>/spec-panel.md
        ▼  (all SEVEN docs feed forward)
PHASE 4 — OPUS ARBITER (mediating)
   reads everything; surfaces the conflicts AND mediates — proposes
   reconciliations, flags residual user-decisions — and writes the integration
   directive that informs the next default-mode iteration.
   → SOURCE/loop<n>/arbiter.md
        ▼
PHASE 5 — INTEGRATE → DESIGN.md v(n+1)  → re-enter Default mode for convergence.
```

Data-flow guarantee: every phase reads the full set of files produced by all
prior phases (Phase 3 gets the 4 docs; Phase 4 gets all 7). Agents pass **file
paths**, not pasted bodies, and read `NAVIGATION.md` + `loop<n>/DECISIONS.md`
first so locked user decisions are never re-litigated.

### Default mode (1 design → 3 parallel critics → arbiter → converge)
   │  writes/revises DESIGN.md (+ §0 revision log) · archives → SOURCE/loop<n>/design.md
   ▼
CRITICS (Opus, parallel — one message, three agents)
   ├─ Fidelity      → SOURCE/loop<n>/fidelity.md
   ├─ Feasibility   → SOURCE/loop<n>/feasibility.md
   └─ Accessibility → SOURCE/loop<n>/accessibility.md
   │  each: verify prior-round items (CLOSED/PARTIAL/NOT/REGRESSED) + fresh pass
   │        full critique → file · ≤300-word summary + VERDICT line → orchestrator
   ▼
ARBITER (Sonnet, cheap)
   │  consolidates the agreed, non-conflicting fixes → one ranked work-order, AND
   │  surfaces every cross-lens conflict (does NOT resolve it) → "Conflicts & Tensions"
   │  → SOURCE/loop<n>/arbiter.md
   ▼
CONVERGENCE GATE (orchestrator)
   │  parse the 3 VERDICT lines
   ├─ all pass → CONVERGED: stop, present DESIGN.md as ship-ready concept
   └─ else     → feed arbiter work-order to DESIGN round n+1
                 (re-critique only the flagged scope to save tokens)
```

## Machine-readable verdicts (last line of each critique file)

- fidelity: `VERDICT: <SHIP|REVISE> · CRITICAL=<n> · MAJOR=<n> · MINOR=<n> · ROUND1_CLOSED=<k>/14`
- feasibility: `VERDICT: <GO|NEEDS-CHANGE|WONT-WORK> · BLOCKERS=<n> · NEEDS_CHANGE=<n> · ROUND1_CLOSED=<k>/<total>`
- accessibility: `VERDICT: <STRONG|WORKABLE|WEAK> · BLOCKERS=<n> · LISTENABILITY_RISKS=<n>`

**Convergence = ALL of:** fidelity `SHIP` & CRITICAL=0; feasibility `GO` &
BLOCKERS=0; accessibility `STRONG|WORKABLE` & BLOCKERS=0.

## Arbiter: surface conflicts, do NOT resolve them

The arbiter is a **synthesizer, not a judge.** Its job is to make the next
Design pass *fully informed*, not to make decisions for it. Concretely:

1. **Consolidate the agreed work.** Where the three critics align (or don't
   touch each other), merge their fixes into ONE ranked, de-duplicated work-order
   the Design agent can execute top-to-bottom.
2. **Surface every cross-lens conflict — explain, don't decide.** Wherever two
   lenses pull in different directions (e.g. accessibility wants the Track-10
   cascade thinned for listenability while fidelity requires maximum polyphony),
   write it up in a dedicated **"Conflicts & Tensions"** section: state each
   lens's position *in its own terms*, the concrete stake/cost of each option,
   and the realistic choices — then **hand the decision to the Design agent.**
   Do not pick a winner. Do not bury the tradeoff. The Design needs to know this.
3. **State the two hard constraints as fixed** (these are NOT conflicts to
   debate, just boundaries every option must respect): **source truth** for
   fidelity facts (`section-meta.md` → `kapitel-0.md`) and the **name_exposure**
   hard rule (function/role only in any output field; names live solely in
   `DESIGN.md §7` and SOURCE files). If a critic ask would breach either, the
   arbiter flags it as out-of-bounds — but everything else is a genuine,
   surfaced tradeoff for Design (and the user) to weigh.

**Orchestrator routing:** the Design agent decides routine tensions with the
arbiter's framing in hand; the orchestrator escalates *significant* or
architectural conflicts to the user (via `AskUserQuestion`) before the next
Design pass, rather than letting them be silently chosen.

## Model tiering (cost control)

- **Opus:** DESIGN + the three judgment critics.
- **Sonnet:** ARBITER, compliance/guard scans, extraction/mechanical tasks.

## Token / throughput rules

- Read `NAVIGATION.md`, not whole files; jump to its line anchors.
- Write full output to files; return ≤300-word summaries to the orchestrator
  (protects the costly main context).
- After round 1, critics verify *deltas* (the §0 log) + their own prior items —
  they don't re-derive the whole design.
- Launch independent critics in **one** message (parallel).
- The convergence gate is the stop condition; the orchestrator also surfaces to
  the user at convergence, after round 3 regardless (runaway guard), or earlier
  if any critic returns a fundamental `WONT-WORK`/`WEAK` needing a user decision.

## Optional specialized agents (add when the work calls for them)

- **Compliance/guard (Sonnet):** deterministic pre-filter — name leaks, bracket
  misuse in lyric bodies, unspelled numbers — runs *before* the judgment critics
  so they don't burn tokens on mechanical checks.
- **Lyric prototyper (Opus):** drafts 1–2 representative tracks' English lyrics in
  function-voice idiolect to stress-test singability before the full lyric-writer.
- **Suno-prompt prototyper:** drafts Style Boxes + section metatags for 2 tracks
  and dry-runs them against the suno-engineer rules (plan → demonstrated).
- **Visual-design critic:** ASDLS-law compliance for the §6 art direction.
```
```
