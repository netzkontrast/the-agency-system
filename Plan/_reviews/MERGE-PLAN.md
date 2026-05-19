---
slug: 2026-05-19-three-way-jules-merge-plan
type: merge-plan
status: draft
owner: claude
created: 2026-05-19
updated: 2026-05-19
summary: How to fold Sessions A (critical), B (improvements), C (from-scratch) into one revised design + ADR set after they return.
related:
  - 2026-05-19-agency-base-design
  - Plan/_jules-briefs/dispatch.yaml
---

# 3-way Jules merge plan

Three Jules sessions return three independent artefacts. This plan
describes how Claude folds them back into the design without losing
their independence and without privileging any one of them.

## Inputs (when sessions complete)

| Source | Folder | Headline outputs |
|---|---|---|
| Session A (critical) | `session-A-critical/` | `REVIEW.md`, optional `EVIDENCE.md` |
| Session B (improvements) | `session-B-improvements/` | `IDEAS.md` |
| Session C (from-scratch) | `session-C-from-scratch/` | `CORE.md`, `DOMAIN-EXAMPLES.md`, `GRAPH.md`, `GHERKIN.md`, `DIVERGENCE.md` |

Each session lands as its own PR. The branches are merge-orthogonal
because their `affects:` lists do not overlap.

## Merge algorithm

### Step 1 — Read each artefact in full, in isolation

In separate Explore-subagent calls so the main context doesn't bloat:

- Read A's `REVIEW.md` only. Extract: P0/P1/P2 verdicts, the triad-vs-5+1
  conclusion, the ≤3 hard-reject recommendations.
- Read B's `IDEAS.md` only. Extract: top-5 ideas + their impact/cost, the
  should-kill list, the inspiration-mining stolen items.
- Read C's 5 files only. Extract: triad shape, two domain examples, the
  graph contract, the 12 refined Gherkin scenarios, the divergences vs
  VOCABULARY.md.

Output: three separate summary docs in main context, ≤300 words each.

### Step 2 — Tri-vote the open questions

Treat each session as a vote on the design's open decisions:

| Question | A says | B says | C says | Resolution |
|---|---|---|---|---|
| Triad vs 5+1 domains | (from A's verdict) | (from B's analysis) | (C inherits triad) | Majority + steelman the loser |
| Q1 cold-boot budget (≤6000 / ≤500) | … | … | … | Same |
| Q2 migration order | … | … | … | Same |
| Q3 supersession aggression | … | … | … | Same |
| prefers_codemode placement | … | … | … | Same |
| Code Mode default OFF vs ON | … | … | … | Same |

Where A and B disagree: take the side with the stronger evidence. Where
both agree against C: C loses (PR's-design-defended). Where C agrees
with A or B against the other: triple-source signal, accept.

### Step 3 — Apply A's hard-rejects (if any)

A's ≤3 hard-reject recommendations are the highest-cost feedback —
they're the items A believes must be removed from the design or the
ship fails. For each:

1. Check whether B or C independently arrived at the same conclusion
   (strong corroboration).
2. If yes → supersede the relevant ADR with a new ADR documenting the
   reversal and citing A+B (or A+C) as evidence.
3. If no → respond on the PR with the counter-argument; A's lone
   objection is filed but not actioned without corroboration.

### Step 4 — Apply B's top-5 ideas (filtered through A's review)

For each top-5 idea in B:

1. Cross-check against A's findings — does A's evidence support or
   contradict the idea?
2. Cross-check against C's design — did C arrive at the same idea
   independently?
3. If A confirms + C confirms → adopt immediately, file as ADR
   amendment.
4. If A contradicts → drop the idea (B is overruled by evidence).
5. If A is neutral + C confirms → adopt as ADR amendment.
6. If only B → file as deferred idea in `Plan/_research-briefs/`.

### Step 5 — Decide what to absorb from C's independent design

C was quarantined from the PR, so anything C invented that the PR also
has is a structural convergence — evidence that the shape is forced by
the constraints, not by my preferences. Anything C invented that the PR
*lacks* is a candidate addition:

- **Convergences:** note them in the design as "independently verified
  by Session C". Strengthens the ADR.
- **C-only additions:** evaluate via the same A+B filter as B's ideas.
- **C divergences from VOCABULARY:** read C's `DIVERGENCE.md`; for each
  divergence, decide whether to amend VOCABULARY or reject the
  divergence. Bias toward amending VOCABULARY when C's reasoning is
  strong, because VOCABULARY is supposed to be descriptive of the
  isomorphism we want.

### Step 6 — Triad reframe → spec + ADR rewrites

Assuming the triad wins (the prior is strong):

1. Amend ADR-0003 (`domain-plugin-contract`) to use the triad: `agentic
   / workflows / context`. Supersede the 5+1 framing.
2. Amend the design spec §3 (Pillars) to be 3 pillars + 3 cross-cutting
   concerns instead of 5+1 + meta-loop.
3. Update VOCABULARY.md §4 (the five-children rule) — the triad changes
   the cardinality.
4. File a new ADR-0009 (or whatever's next) for the triad explicitly.

### Step 7 — Refresh the 12 Gherkin scenarios

C delivered refined Gherkin with concrete expected outputs. Promote
C's Gherkin to be the canonical acceptance contract for the design.
Each spec in the 12-spec plan (§13 of the design) gets a "verifies:"
field naming the Gherkin scenarios it implements.

### Step 8 — Commit + amended PR

One commit per amendment (so the audit trail is clean):

1. `spec: amend design for triad (from session A+C convergence)`
2. `adr: amend ADR-0003 — domain count is 3, not 5+1`
3. `adr: ADR-0009 — triad as cross-domain contract`
4. `spec: promote Session-C Gherkin to canonical acceptance contract`
5. `spec: apply Session-B top-N ideas (each cited)`
6. `spec: respond to Session-A hard-rejects (each addressed or filed)`

Push and update PR #133's description with a "Triad amendment" section
linking to the three review PRs.

## Anti-patterns to avoid

- **Cherry-picking only the flattering feedback.** Each session's hard
  critique is the most valuable part. Read A's verdict before B's
  ideas.
- **Treating C as the new design.** C is one vote; the merge product
  is *between* A, B, C, and the original PR — not C's solo conception.
- **Skipping the steelman.** When the triad wins, write down the
  strongest argument FOR 5+1 in the amended ADR so the future reader
  knows what was considered.
- **Folding all three into one giant commit.** Audit trail matters
  more than commit count.

## Self-check (post-merge)

- [ ] Every A finding has a verdict (adopted / rejected with reasoning
      / filed).
- [ ] Every B idea has a status (adopted / rejected / deferred).
- [ ] Every C divergence has a resolution (amend VOCABULARY / reject).
- [ ] The amended design passes all 12 Gherkin scenarios from C.
- [ ] The amended ADR set has no internal contradictions.
- [ ] The triad reframe is reflected in VOCABULARY.md if adopted.
