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

## Pipeline (per round `n`)

```
DESIGN (Opus)
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
   │  merges the 3 critiques → one ranked, de-conflicted work-order
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

## Arbiter conflict-resolution precedence

1. **Source truth wins fidelity facts** (`section-meta.md` → `kapitel-0.md`); non-negotiable.
2. **Feasibility is a hard constraint** — a fix that can't be built in Suno is not a fix.
3. **Accessibility may not betray the source or break feasibility.** When a
   listenability ask tensions with fidelity/feasibility, choose the reconciliation
   that keeps the source truth *and* is buildable.
4. **name_exposure hard rule overrides everything** — function/role only in any
   output field; personal names live solely in `DESIGN.md §7` and SOURCE files.

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
