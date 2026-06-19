# Chapter Zero — Album Planning Guide (generation phasing)

> **Artist:** the Agency System · **Album:** Chapter Zero ·
> **Genre bucket:** dystopian-future-synth · **Tracks:** 13, all vocal ·
> **Spec:** `DESIGN.md` (v4, 20/20 spec-panel passed) ·
> **Ground truth:** `SOURCE/section-meta.md` → `SOURCE/kapitel-0.md` ·
> **Map:** `SOURCE/loop/NAVIGATION.md`

This is the album-specific instantiation of the cross-project methodology in
`overrides/album-planning-guide.md`. It plans **how Chapter Zero gets built** —
lyrics first, then Suno engineering — as a `/sc:workflow`-style phased plan with
dependency mapping and validation gates. It plans the build; it does **not**
generate lyrics or Suno prompts.

**HARD RULE — name_exposure.** Function/role only in every output field (lyric
body, Suno metatag, Style Box, exclusion, promo, art prompt). The personal
names — Kael, Nyx, Lex, Rhys, Kiko, Lia, Moros, Argus, Silas, Juna, AEGIS,
Oblivion — appear ONLY in `DESIGN.md §7` (internal) and the `SOURCE/` files. A
name leaking into any public/output field is a CRITICAL defect. `lyric-reviewer`
item 14 (`scan_artist_names`) runs on every track's lyrics **and** Style Box.

**Source-truth hierarchy.** KOH / tier / state / which-voice-first disputes →
`SOURCE/section-meta.md` WINS; verbatim lines → `SOURCE/kapitel-0.md`. Never
paraphrase a ground-truth value from memory; cite the anchor.

---

## Phase 0 — Confirmation gate (HARD GATE)

**Nothing generates until the user gives the `album-conceptualizer` Phase 7
confirmation on the seven planning phases.** `DESIGN.md` is v4 and notes it is
"awaiting album-conceptualizer Phase 7 confirmation before any generation."
Documentary sources gate does **not** apply — Chapter Zero is a narrative/OST
translation of a fictional chapter; `sources_verified = N/A` is correct.

**Pre-generation prerequisites (do once, before Phase 1A — `DESIGN.md §8`):**

1. Create the bucket-level genre README for `dystopian-future-synth` (or set
   per-track Target Duration + density defaults), or the lyric density/pacing
   gates have no ceiling and silently no-op. Word ceilings: **140–220 words**
   for ambient/electroacoustic tracks (1, 2, 3, 7, 13); **cap ~200–350 words**
   for rock/industrial (5, 9, 10, 12).
2. Build + snapshot the **host Persona** (male mid-baritone, weary, dry
   close-mic) — single point of failure for T13's payoff and T10's mirror-echo;
   lock, snapshot, keep a drift fallback.
3. Own the **KOH drone stem** with automation (Layer A, `DESIGN.md §4`).

---

## EXCEPTION (USER-LOCKED) — Track 1 first and complete (the PILOT)

**After the Conceptualizer is done, Track 1 — "The Listening" — is built FIRST
and COMPLETELY, its entire vertical slice end to end, as the PILOT / reference
track. No other track begins until T1 is complete and signed off.**

T1's vertical slice:

```
lyric-writer
  → pronunciation-specialist
  → lyric-reviewer (14-pt QC + auto phonetic fixes)
  → [voice-checker — advisory only, never blocks]
  → pre-generation-check (6 gates, BLOCKING)
  → ready-for-Suno / suno-engineered
```

**Why T1 is the pilot.** Completing one track end to end validates the entire
chain *before* the batch is committed, so any systemic problem is caught once,
not 13×. T1 specifically validates:

- **Function-voice idiolect** — the fragment/proto-host syntax (trailing,
  almost-remembering, gaps where memory should be) and the heavy-voice's
  collapsed-shame fingerprint (`DESIGN.md §4` voice block), recognized by syntax
  with **no labels**.
- **The KOH-spine treatment** — T1 carries the boot/ignition and the 0.998→0.94
  density (`DESIGN.md §4` ladder); validates that the owned-stem (Layer A) reads
  under a generated body.
- **name_exposure discipline** — proven on a real Style Box + lyric before 12
  more.
- **Suno Style-Box + metatag grammar** — vocals-first, the verbatim Layer-B
  anchor, descriptive-only register tags, the token-bias guard.
- **Long-form multi-pass assembly** — T1 is the longest track (8.0 min, comped
  from multiple generations over the continuous owned spine, `DESIGN.md §3/§8`),
  so it stress-tests the hardest assembly case first.

**Run T1 in the main session, sequentially** (stateful, user-in-the-loop).
Capture every reusable decision (host-Persona snapshot, Layer-B anchor wording,
metatag grammar, exclusion defaults, the spell-numbers-as-words and
"Do not change any words. Sing exactly as written." guards from `DESIGN.md §8`).
**Sign-off gate:** the user reviews and approves T1 before Phase 1 begins.

T1 lyric-writer load list: `DESIGN.md §2` row 1 + the `vorwort` intro row · §3
T1 row · §4 ignition + ladder + the fragment/proto-host & heavy-voice fingerprints
· §7 mapping (`nar`, `frg`, `mor`) · `SOURCE/kapitel-0.md` L6 Vorwort + L28 Das
Rauschen (the seeded "It is pointless. It was always pointless." that pays off in
T10) · `SOURCE/section-meta.md` L31–32.

---

## Phase 1 — All remaining lyrics in sequence (T2…T13)

Draft lyrics for the remaining 12 tracks through the chain:

```
lyric-writer → pronunciation-specialist → lyric-reviewer (14-pt + auto phonetic fix)
```

`lyric-writer`'s **auto-invoked `suno-engineer`** leaves a **first Style-Box
draft** per track — treat it as provisional scaffolding. The dedicated,
coherent-set Suno pass is Phase 2 (see "Two-batch reconciliation" in the
cross-project guide). The lyrics phase owns *what is sung*; Phase 2 owns *how
the album sounds as one set*.

**Sequence — do NOT blind-parallel** — because Chapter Zero is a continuous
narrative with a KOH spine arc and explicit cross-track callbacks. Subagents
help with **independent drafting** (one subagent per track, briefed with the
§-pointers below, the voice idiolect, name_exposure, file-based hand-off);
**order matters** wherever a track pays off an upstream anchor:

- **T1 heavy-voice seed → T10 payoff** ("It is pointless. It was always
  pointless." faint in T1, full-voiced in T10) — T10 must be written after T1.
- **Small-voice refrain T2 → T10** ("It is cold. I am small.").
- **The axiom hook** (T6, "It is what prevents it from not being", verbatim,
  stress "pre-VENTS") recurs as a carried-out anchor — plant in T6 first.
- **Dead-metronome / counting bookend T1 → T13** (T13's coda echoes T1's tick).
- **Mirror-echo never appears before T9** (`section-meta`: first echo in
  `schrecken`) — do not introduce it earlier.

### Per-track build order + design pointers (write in this order)

Each row: load `DESIGN.md` §2 row + §3 row + the §4 voice fingerprint(s) + the
§7 mapping for that track + the named `SOURCE/` anchor. State/KOH from §2/§3.

| Order | Track | Voices (function form) | State · KOH | Load: DESIGN §-pointers + SOURCE anchor |
|---|---|---|---|---|
| Pilot | **1 · The Listening** | narrator → fragment/proto-host; heavy-voice (faint) | S0→S1 · 0.998→0.94 | §2 r1+vorwort · §3 T1 · §4 ignition/ladder + proto-host & heavy-voice · §7 nar/frg/mor · kapitel L6, L28 |
| 1 | **2 · The Nothing** | fragment/proto-host; small-voice | S1 · 0.91 | §2 r2 · §3 T2 · §4 small-voice · §7 frg/kik · kapitel L36; section-meta L33. Plant "It is cold. I am small." |
| 2 | **3 · Contact** | fragment/proto-host; warm-voice; reaching-voice | S1 · 0.86 | §2 r3 · §3 T3 · §4 warm-/reaching-voice · §7 frg/rhy/lia · kapitel L50. **NO Lex here**; closeness-then-withdrawal, no consonant hook; *trügerische Atempause* |
| 3 | **4 · Structure Optimization** | logic-voice (1st); annotating-voice (1st, low layer) | S2 · 0.82 | §2 r4 · §3 T4 · §4 logic-/annotating-voice · §7 lex/arg · kapitel L76; section-meta L35 |
| 4 | **5 · Strike** | kinetic-voice; logic-voice (denial) — sequential | S2 · 0.74 | §2 r5 · §3 T5 · §4 kinetic-/logic-voice · §7 nyx/lex · kapitel L90 (sector 280→692; sixteen bindings; "It is not loss…") |
| 5 | **6 · The Click** | fragment→the system (axiom); warm-voice (last trace); annotating-voice | S3 · 0.58 | §2 r6 · §3 T6 · §4 (axiom, "Klick", second movement) · §7 frg/aeg/rhy/arg + axiom lock · kapitel L106–145. One Persona per section |
| 6 | **7 · The Silent Watch** | the system (watch); narrator (intro question) | S0 · 0.998 | §2 r7+dazwischen · §3 T7 · §4 the-watch + 0.61 dip→reset · §7 nar/aeg · kapitel L146, L160; section-meta L38–39. False-calm reset — keep clean/lean |
| 7 | **8 · The Anomaly** | the system (watch); the signal/anomaly (texture only) | S2 · 0.991 | §2 r8 · §3 T8 · §4 the-watch + anomaly-texture · §7 aeg/(signal) · kapitel L185; section-meta L40. Dread rides arrangement, not meter |
| 8 | **9 · Inward** | the system; mirror-echo (1st, HOST timbre); signal (residual) | S2 · 0.21 | §2 r9 · §3 T9 · §4 mirror-echo + airless-S2 · §7 aeg/sil + paradox ladder · kapitel L207; section-meta L41 (Tier 2 at 0.21 — NOT S3). Paradox 0.84→0.99 as owned-stem counter-motion + one buried spoken decimal |
| 9 | **10 · Resonance Cascade** | fragment/proto-host (drowning); small-, reaching-, heavy-voice, mirror-echo (round→stack) | S3 · 0.21 | §2 r10 · §3 T10 · §4 round→stack + all four EP fingerprints · §7 frg/kik/lia/mor/sil · kapitel L244–269. **Pays off T1 heavy seed + T2 small refrain.** Multi-pass comp (§8) |
| 10 | **11 · Kernel Panic** | the system; fragment/proto-host (collapse) | S3 · 0.18 | §2 r11 · §3 T11 · §4 0.18 collapse-to-noise · §7 aeg/frg · kapitel L270; section-meta L43. Pulse-less implosion; one Persona per section |
| 11 | **12 · Separation Protocol** | the system (log); sweep-voice; kinetic-voice (refusal); fragment (shatter) — sequential | S3→S4 · 0.00→1.00 | §2 r12 · §3 T12 · §4 sweep-voice · §7 aeg/obv/nyx/frg · kapitel L292+ ("I fall… into countless shards"). One Persona per section |
| 12 | **13 · On Time** | the host (was the fragment, same Persona, now hollow) | S4 · 1.00 (forced/hollow) | §2 r13 · §3 T13 · §4 S4 sterile + host fingerprint · §7 kal + ending verbatim · kapitel L292+ coda. **§8 guardrail: void only by what is NOT said** — no line names memory/grief/amnesia/loss/healing. Bookends T1 tick. Keep tight (~2–3 min) |

**Pronunciation-specialist (every track) — required substitutions from §8**, not
documentation, logged in each track's Pronunciation Notes table so
`check_pronunciation_enforcement` verifies them:

- **No square brackets in lyric bodies** (`[SYSTEM-STATUS]` → "system status
  nominal"; `[PROTOCOL KOH_1.0]` → "protocol K-O-H one point zero, initiated").
- **Spell every number/decimal as words** in the Suno box (streaming lyrics keep
  standard form): 0.998, 0.991, 0.41, 0.18, 0.21, paradox 0.84/0.99, 14,832,
  2,304, 21, sectors 280/692.
- **Token-bias guard** — add "Do not change any words. Sing exactly as written."
  to the top of every Suno lyrics box (the vocabulary echo/noise/shadow/mirror/
  whisper collides with Suno's bias list).
- **"Klick"** retained untranslated in T6 only.

---

## Validation gate — Phase 1 → Phase 2

**Do not start Phase 2 until all 13 tracks pass `lyric-reviewer` with zero
critical issues** (T1 already passed in Phase 1A). Confirm: pronunciation tables
applied in every Lyrics Box; no unresolved homographs; **no personal name in any
lyric or Style Box** (`scan_artist_names` clean). `pre-generation-check`'s 6
gates may be run per track as the final block before Suno.

---

## Phase 2 — All Suno engineering in sequence (T2…T13, as a coherent set)

Run `suno-engineer` deliberately across the whole tracklist as a set:

- **The manufactured KOH 5-layer spine is an album-level asset, built ONCE,
  referenced per track** (`DESIGN.md §4`): Layer A owned C-drone master stem +
  automation; Layer B the verbatim style-box anchor `sustained low C drone
  underpinning, sub-bass continuo, cold, no key change` identical on all 13;
  Layer C the host Persona (T1,2,3,6,10,11,12,13) + optional watch Persona
  (T6,7,8,9,11,12), **one Persona per generation** (T6/11/12 assign per section);
  Layer D locked **C minor** globally (drone detune in the owned stem, never via
  Suno key change); Layer E state-biased mastering per state-axis (T9 masters at
  **S2**, contained, protecting T10's peak headroom).
- **Per-track Style Boxes + section metatags follow** (`DESIGN.md §8` per-track
  NEEDS-CHANGE flags): vocals-first, ≤2 genre tags / 4–7 descriptors,
  descriptive vocal metatag at each voice change (never a name), Layer-B anchor
  verbatim, exclusion defaults. When a Persona carries gender/register, drop
  those descriptors from the Style Box.
- **Long-form / multi-pass tracks** get the comp/extend plan from `DESIGN.md §8`:
  T1 (8.0), T6 (9.0), T11 (8.0) earn the expanse; T10 is the most labour-intensive
  (round→stack: drowning lead + each echo as its own generation, 12-stem extract,
  comp in mix); T5 (4.0) / T8 (4.5) / T13 (2.5) stay tight; T7/T8 (false-calm
  pair) must NOT absorb extra minutes. Owned spine stitched across comped
  sections; host Persona held across every extend/continue; key + BPM locked.
- **Post / DAW gestures are NOT Suno prompts** (`DESIGN.md §8` shot list): boot/
  ignition (T1), ritard-to-0→reboot (T6), KOH cliff + paradox counter-motion (T9),
  datamosh (T9/10), round→stack comp (T10), shatter glitch-cut (T12), collapse
  crush (T11), sterile open-interval arp (T13).

---

## Genuinely-open production decisions (escalate to the user)

From `DESIGN.md §8`, and unchanged here:

1. Fine-tune a **Custom Model** for the back half (needs Premier + ≥6 finished
   tracks) vs. relying on Personas alone.
2. T11's peak and collapse as **one generation** (split in post) vs. **two
   generations** comped.

---

## Reminder behavior

After each phase/skill, end with a short **"Next step (optional)"** line naming
the recommended next skill and what it would check. Surface; let the user decide.
After Phase 2, the pre-release chain begins: import-audio → mix-engineer →
mastering-engineer → album-art-director/import-art → validate-album →
plagiarism-checker → explicit-checker → check_streaming_lyrics → release-director.

---

## Session handoff (build status)

**T1 "The Listening" — rebuilt, QC green.**
- **Narrator clip** (separate generation): slow, deliberate, *pointiert*
  spoken-word using the **3-layer delivery DNA** (per-line bracketed metatags on
  their own lines · ellipsis pause-cues · CAPS on load-bearing words) with a
  faint **drone bleeding in**. Words were only **reformatted for breathing**
  (line breaks / blank lines) — not rewritten.
- **Sung body**: the **fragile, genderless head-voice** (the new voice spine),
  with the **heavy-voice collapse-seed** surfacing as a faint **parenthesized
  backing undertow** in the verses, building to the Bridge.
- **QC**: `scan_artist_names` clean · `check_homographs` clean ("nothing" is not
  a homograph — a delivery matter, handled by diction, not respelling) ·
  `check_streaming_lyrics` READY 7/7.

**Voice spine (redefined this session).** The proto-host → host is a **fragile,
genderless head-voice** (adult, sustained, faintly synthetic — distinct from the
framing narrator and from the child small-voice), held T1→T13. Propagated to
`DESIGN.md` (§3/§4/§8) and to the `theagencysystem` skill (`host.md` Voice arc,
`_modes/narrator.md` music fingerprint, `resolver.yaml`, `matrix-index.yaml`).
The reusable narration delivery craft is in
`overrides/suno-preferences.md → "Narration / Spoken-Word Delivery DNA"`.

**Open decisions.**
- Apply the per-line delivery toolkit to the **sung body** too, or leave it?
- Then build **T2 "The Nothing"** onward — **one track at a time, in the main
  session, with AskUserQuestion at every decision point, NO subagents.**

**Process learnings (honor next session).**
- When asked to "reformat / give it room to breathe," **reformat ONLY** (line
  breaks, blank lines, spacing) — **never** rewrite, expand, or trim the words.
- **Ask at every creative fork** (voice, register, structure) — do not assume.
- On **bitwize-MCP disconnect** (it flaps), fall back to **direct file edits**
  (the documented fallback) and **re-run the MCP QC** when it reconnects.
