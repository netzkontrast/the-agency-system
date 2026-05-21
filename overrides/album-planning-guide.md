# Album Planning Guide

Cross-project generation-workflow methodology for the-agency-system. This file
holds the **reusable phasing** for turning a confirmed album concept into
generated tracks — the step the `album-conceptualizer` hands off to. It is
deliberately **album-agnostic**: no track titles, no character names, no
project-specific KOH/state values live here. Album-specific instantiation
(per-track build order, design-section pointers, the pilot-track choice) lives
in each album's own `ALBUM-PLANNING-GUIDE.md`, never in this file.

Structured per the `/sc:workflow` methodology: derive a phased implementation
plan from the spec — phases, per-step dependencies, what parallelizes, and a
validation gate between phases. This is a **plan**, not an execution: it stops
at the plan and never generates lyrics or Suno prompts itself.

For the no-labels / function-only rule that governs every output field, see
`voice-craft-principles.md`. For the chain order this guide sequences, see the
"Pre-generation chain" section of the repo `CLAUDE.md`.

---

## Core principle: vertical-slice the pilot before you batch

**Build the first track completely — end to end through the whole chain —
before generating any other track.** The first complete track is the **pilot**:
it validates the entire generation chain (voice idiolect, the album's spine
treatment, name_exposure discipline, the Suno Style-Box + metatag grammar, and
long-form multi-pass assembly) on one track. A systemic flaw is then caught
**once** instead of N times across the tracklist. Only after the pilot is
complete and reviewed do the batch phases run.

This is the single highest-leverage move in album generation. Treat it as
non-negotiable unless the user explicitly waives it.

---

## Two-batch strategy: all lyrics first, then all Suno engineering

After the pilot, the remaining tracks move through **two distinct batch
phases**, in order:

1. **Lyrics batch** — every remaining track gets its lyrics drafted, its
   pronunciation resolved, and its 14-point review, in narrative sequence.
2. **Suno-engineering batch** — every track's Style Box and section metatags
   are engineered and finalized as a **coherent set**, after all lyrics exist.

### Reconciling the auto-suno hand-off with the two-batch intent

`lyric-writer` **auto-invokes `suno-engineer` at the end of its own workflow**
(it is the last step of the lyric-writer skill). This appears to collide with a
"lyrics first, Suno later" plan. It does not — keep the two phases distinct by
role, not by suppressing the hand-off:

- In the **lyrics batch**, let the auto hand-off run. It produces a **first
  Style-Box draft** per track as a by-product of finalizing lyrics. Treat that
  draft as provisional scaffolding, not the final prompt.
- In the **Suno-engineering batch**, `suno-engineer` runs deliberately across
  **all** tracks at once, finalizing every Style Box and every section metatag
  **as a set** — so cross-track consistency (shared anchors, register grammar,
  album-level sonic assets, exclusion defaults) is engineered coherently rather
  than per-track in isolation.

The lyrics batch owns *what is sung*; the Suno batch owns *how the whole album
sounds as one body of work*. The auto-draft is the bridge, not a violation.

---

## The phases

### Phase 0 — Confirmation gate (hard gate)

**Nothing generates until the `album-conceptualizer` Phase 7 confirmation is
explicitly given by the user.** This is the binding entry gate. Concept-stage
albums (empty `tracks/`) do not enter Phase 1 on Claude's initiative — the user
must confirm the planning phases first. If the album is documentary, the
sources gate also applies (every track at `Verified` before lyric-writer).

### Phase 1A — Pilot track (vertical slice, complete before any batch)

Build track 1 (or the designated reference track) **completely**, end to end:

```
lyric-writer
  → pronunciation-specialist
  → lyric-reviewer (14-pt QC + auto phonetic fixes)
  → [voice-checker — advisory only, never blocks]
  → pre-generation-check (6 gates, BLOCKING when invoked)
  → ready-for-Suno / suno-engineered
```

Run this in the **main session, sequentially** — it is stateful and the user is
in the loop. Capture every reusable decision the pilot surfaces (any
album-level sonic asset, the host-Persona snapshot, the metatag grammar, the
exclusion defaults). **Sign-off gate:** the pilot is reviewed and approved by
the user before Phase 1B begins. If the pilot reveals a systemic problem, fix
the plan first, then re-run — do not start the batch on a broken chain.

### Phase 1B — Lyrics batch (remaining tracks, in sequence)

Draft lyrics for all remaining tracks through the chain:

```
lyric-writer → pronunciation-specialist → lyric-reviewer
   (lyric-writer's auto-invoked suno-engineer leaves a first Style-Box draft)
```

**Sequence, do not blind-parallel, when the album has a continuous narrative or
a cross-track motif/spine arc** — later tracks reference earlier ones (callbacks,
seeded phrases that pay off later, bookends). Order matters wherever a track's
lyrics depend on a phrase planted upstream.

**Where subagents help:** the *drafting* of tracks whose content is mutually
independent can be delegated, one subagent per track, briefed with the exact
design-section pointers for that track and capped in length. **Where order
matters:** any track that calls back to or pays off another must be written
after its upstream anchor exists. Brief each subagent like a colleague — goal,
the design sections to load, the voice idiolect, the name_exposure rule, and a
file-based hand-off (the subagent edits the track file; the main session checks
the diff).

### Validation gate — Phase 1 → Phase 2

**Do not start Phase 2 until every Phase-1 track has passed `lyric-reviewer`
with zero critical issues.** Suno engineering against unreviewed lyrics wastes
the coherent-set pass. Confirm: pronunciation tables applied in every Lyrics
Box, no unresolved homographs, no artist/character names in any field.

### Phase 2 — Suno-engineering batch (all tracks, in sequence, as a set)

Run `suno-engineer` deliberately across the whole tracklist:

- **Build album-level sonic assets ONCE, reference per track.** Any continuous
  asset that cannot be generated per-clip (a manufactured spine/stem, a locked
  key, state-biased mastering bias, reusable Personas) is authored once as an
  album asset and referenced in each track's prompt — Suno generates per track,
  there is no shared oscillator across prompts.
- **Per-track Style Boxes + section metatags follow**, finalized coherently:
  vocals-first, ≤2 genre tags, 4–7 total descriptors, descriptive vocal metatag
  only at each voice change (never a name), shared verbatim anchors held
  identical across tracks, exclusion defaults applied.
- **Long-form / multi-pass tracks** get their comp/extend plan from the design's
  production section — the 5–8-minute tracks are comped from multiple Suno
  generations (extend/continue or section-by-section), never one pass; the
  continuous album spine is the asset stitched across comped sections; the host
  Persona is held across every extend/continue pass; key and BPM stay locked.

---

## Cross-cutting rules (restate in every album's instantiation)

- **name_exposure (hard rule).** Function/role only in every output field —
  lyric body, Suno metatag, Style Box, exclusion, promo, art prompt. A personal
  name leaking into any public/output field is a CRITICAL defect. Names live
  only in the album's internal source-mapping appendix. `lyric-reviewer` item 14
  (`scan_artist_names`) must run on every track's lyrics **and** Style Box.
- **Source-truth hierarchy.** When a fact disputes, the album's ground-truth map
  decides — the structural/state ground truth wins over decoded prose, which
  wins over design law. Cite the exact source, never paraphrase a ground-truth
  value from memory.
- **Model tiering / subagent orchestration.** One subagent per independently
  draftable track; brief each with the precise design-section pointers, voice
  idiolect, and the name_exposure rule; hand off via the track file (subagent
  edits, main session verifies the diff). Reserve sequential main-session work
  for stateful, user-in-the-loop, or cross-track-dependent steps.
- **Validation gates between phases.** Pilot signed off before the lyrics batch;
  all lyrics pass `lyric-reviewer` before the Suno batch. Gates are checkpoints,
  not paperwork — a failed gate stops the next phase.
- **Tools and skills win.** Status/field changes via `update_track_field`;
  track creation via `create_track`; a stale cache fixed with `rebuild_state`
  before retry — never hand-edit what a tool owns. Prefer the
  `/bitwize-music:<skill>` slash command over the underlying MCP tool.
- **voice-checker is advisory.** Surface its Warning/Info flags; never gate on
  it, never auto-rewrite from it.
- **pre-generation-check is a hard gate when invoked.** Its 6 gates block;
  choosing not to invoke it is the user's call, bypassing its results is not.

---

## Reminder behavior at hand-offs

After each phase or skill completes, end with a short **"Next step (optional)"**
line naming the recommended next skill and what it would check. Surface the
recommended step; let the user decide whether to run it or skip it. Never
auto-invoke an optional chain step unasked.

---

## How this works

1. Confirm the Phase 0 gate (album-conceptualizer Phase 7) is passed.
2. Build the pilot track completely; capture reusable assets; get sign-off.
3. Batch all remaining lyrics in sequence; pass the Phase-1→2 validation gate.
4. Batch all Suno engineering as a coherent set; build album assets once.
5. Hand off to the pre-release chain (import-audio → mix → master → … → release).
