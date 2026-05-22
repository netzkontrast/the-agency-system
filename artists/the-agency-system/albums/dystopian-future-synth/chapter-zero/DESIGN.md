# Chapter Zero — Album Concept & Design (v5)

> **Artist:** the Agency System · **Genre bucket:** dystopian-future-synth ·
> **Type:** Narrative concept album · **Title (locked):** "Chapter Zero" ·
> **Tracks:** 13, **all vocal** (none instrumental) ·
> **Long-form:** varied per section, total **70–100 min** (~85 min target;
> tracks average ~5.5–7.5 min — the extra time is atmospheric/instrumental
> expanse and breathing room, NOT higher lyric density; lyric word-counts stay
> lean per §8) ·
> **Language:** English · **Status:** In production (v5 — album-conceptualizer
> Phase 7 **confirmed**; T1 "The Listening" pilot **built & QC-green**; T2–T13
> pending. v4's all-concerns spec-panel 20/20 still holds; long-form + Narrative
> + all-vocal + title locked. **Voice spine = fragile genderless head-voice**
> (§3–§4); narrator spoken-word delivery DNA (§8).)
> **Source:** `SOURCE/kapitel-0.md` + `SOURCE/section-meta.md` (KOH/tier
> ground truth) — "Kapitel 0 — Kohärenz Protokoll" (Coherence Protocol,
> Chapter 0). Standalone. Direct 1:1 musical translation.

This document is the working brief for the build. **Section 7 is internal team
documentation only** and never reaches a public field. **Section-meta.md is the
single source of truth** for any KOH value, tier/state, or which-voice-first-
appears dispute. The full loop history (v1→v2 critiques, the Round-3 divergent
designs, the adversarial clash map, the tri-lens reviews, and the mediation)
is archived under `SOURCE/loop1–3/`.

---

## 0 · Revision log

### v4 → v5

v5 records the **build-phase** decisions taken during the T1 "The Listening"
pilot (album-conceptualizer **Phase 7 confirmed**; the build is proceeding one
track at a time). v4 content is preserved — these are refinements, not a concept
reopen.

- **Voice spine redefined.** The sung **proto-host → host** spine is now a
  **fragile, genderless head-voice** (thin, breathy, near-falsetto, faint
  synthetic edge; adult, not childlike), held T1→T13 — *not* the earlier male
  mid-baritone. Deliberately distinct from the framing narrator and the child
  small-voice. Propagated to §3 (album spine), §4 (Layer C + the
  fragment/proto-host fingerprint), §8 (host-Persona prereq). The cross-project
  skill (`skills/theagencysystem/`) records this as the host's *genesis* timbre
  on a developmental arc (matures toward the mid-baritone in later work).
- **Narrator = a music-layer voice with a delivery DNA.** The T1/T7 spoken
  intros generate as their own clips, **slow & *pointiert***, a faint drone
  bleeding in; built with a 3-layer Suno toolkit (per-line bracketed metatags ·
  ellipsis pause-cues · CAPS on the load-bearing word) and **reformatted for
  breathing, never reworded**. Reusable craft saved to
  `overrides/suno-preferences.md → "Narration / Spoken-Word Delivery DNA"`.
- **Heavy-voice undertow.** The collapsed seed may surface early as a faint
  **parenthesized backing undertow** (V5 `( )` = backing/ad-lib), building to
  full voice later (still pays off full-voiced at T10).
- **T1 pilot built** — lyrics + Suno boxes + ASDLS Tier-0 art prompt; QC green
  (scan_artist_names clean, no homographs, streaming READY 7/7). T2–T13 pending.

### v3 → v4

v4 closes the final all-concerns spec-panel (`SOURCE/loop4/final-spec-panel.md`,
**20/20 consistency pass**) and folds in the newly-locked planning answers. v3
was preserved verbatim except for these targeted additions:

- **Planning locks** — Type = **Narrative concept album**; **all 13 tracks
  vocal** (none instrumental); **Title = "Chapter Zero"**; **long-form duration
  varied per section, total 70–100 min** (~85 min target; extra time is
  atmospheric/instrumental expanse, not added lyrics). Folded into the header
  block and §1.
- **MUST-FIX — long-form assembly note added to §8.** 5–8 min tracks are
  comped from multiple Suno generations (extend/continue or section-by-section),
  never one pass; the owned KOH stem (Layer A) is the continuous spine stitched
  across the comped sections; the host Persona is held across every
  extend/continue pass; BPM/key stay locked (Layer D).
- **NICE-TO-HAVE — per-track duration map** added to §3 (T1/T6/T11 earn the
  expanse; T5/T8/T13 stay tight; minutes sum to the ~85 min middle).
- **NICE-TO-HAVE — T6 BPM cross-ref** — the T6 BPM cell now points to the
  ritard-to-0→reboot post gesture (§8), so "80, ritard to 0 then reboot" is not
  read as a single Suno tempo.
- **NICE-TO-HAVE — T13 brevity restated** in §3 and §8 (~2–3 min; do not extend
  even though long-form is the album default).

### v2 → v3

v3 folds in the Round-2 arbiter work-order (`loop2/arbiter.md` §A), the two
**locked user decisions**, and the Round-3 mediation (`loop3/mediation.md`).
The divergent round converged with **near-zero fidelity loss** — three isolated
concern-pure designs, an adversarial maximal-clash decomposition, a tri-lens
review, and a mediation all concluded the faithful direction is also the most
listenable and is buildable; every breach was ruled out *and* its payoff kept
by craft.

| Item | Change | Where |
|---|---|---|
| **WO-A1** | Track 9 paradox ladder corrected to **0.84 → 0.99** (0.67 belongs to Track 8 only; kapitel L195 vs L217/L237). | §2 row 9, §3 T9, §4 |
| **WO-A2** | **Name-quarantine restored** — §2 Note column and §6 returned to function-form; personal names live ONLY in §7. | §2, §6 |
| **WO-A3** | `0.41` ("zero point four one", Track 7 persistence) added to the spell-as-words list. | §8 |
| **WO-A4** | Narrator-clip wording fixed: the sung body is its **own** generation beginning at `[Verse 1]`; the cut from the separate narrator clip is a **mix butt-join**, not an in-prompt hard-cut. | §8 |
| **WO-A6** | **One Persona per generation** — Tracks 6/11/12 assign the host vs. watch Persona **per section** (sequential), never both in one prompt. | §4, §8 |
| **WO-A7** | Track 9 **generated flat at 116 BPM**; the accelerando feel is imposed in post (in-track accel over 3–4 min is unreliable). | §3 T9, §8 |
| **LOCK-T10** | Cascade = **hybrid round→stack** (locked): echoes surface one at a time over the drowning lead, then pile into a simultaneous wall at the climax. | §2 row 10, §3 T10, §4, §5, §8 |
| **LOCK-T9** | Inward staged **tight / airless / mid-volume** (locked): self-attack as self-strangulation, not loud violence. Back-half contour = **build→peak→void** (T9 airless → T10 peak → T11 implode). | §3 T9–T11, §4 |
| **R3-1** | Founding axiom kept **verbatim**; the hook is recovered **prosodically** (stress "pre-VENTS" on the downbeat as the 3-beat hook cell), not by rewording. | §3 T6, §7 |
| **R3-2** | **No warm ghost** under the T13 coda; orientation comes cold — host-Persona timbre recognition + a placed **open-interval hold** + an optional **dead-metronome callback to T1's tick**. | §3 T13, §8 |
| **R3-3** | Track 3 has **no literal consonant melody**; the felt high point comes from **closeness-then-withdrawal** (warm/tremulous timbre, bed still refusing the tonic, hard curdle to "cold. necessary.") — the source's *trügerische Atempause*. | §3 T3, §4 |
| **R3-4** | Track 9 paradox numbers rendered as a rising **owned-stem sonic counter-motion** against the crashing drone + **one buried spoken decimal** as a cold tell — not sung, not stripped. | §3 T9, §4, §8 |
| **R3-5** | Polyphony is **per-track, not blanket**: sequential on handoffs (T5/T12); T3 carried by shared HOST timbre with a brief self-overlap at "stay/go/stay"; true simultaneity ONLY at the locked T10 stack. | §3, §5 |
| **R3-7** | Track 13's **owned-MIDI minor arp promoted to PRIMARY** (author the open-interval harmony; Suno carries only the flat vocal); placed "slammed-door" gesture craft mandated. | §8 |
| **Missed-1** | Witness parentheticals must be a **generated low-mixed backing layer**, not literal `( )` in the lyric body (Suno sings parentheses). | §5, §8 |
| **Missed-2** | **Host Persona = single point of failure** for T13's payoff and T10's mirror-echo — lock + snapshot it early, reuse, keep a drift fallback. | §8 |
| **Missed-3** | **Telemetry-log rationing** across T7–T12 — no per-track `[SYSTEM-STATUS]` dump; audit back-half log density as a whole. | §8 |

**Preserved (spec-panel-confirmed, not weakened):** beat-for-beat arc order;
the two false-calm resets (0.998 Track 7, 0.991 Track 8) with T7 **fully clean**
and the tension load on T8's creeping arrangement; the crash *inside*
`schrecken`/Track 9 *before* the cascade; the **number↔tier divergence** (drone
follows the 0.21 number, palette follows the ALERT tier — the chapter's own
"misaligned coherence"); the **T6 second movement** (the inner-simulated-space
seed, protected even if T6 is trimmed); the **T3 "no Lex here"** first-voice
order; the hollow forced 1.00 / **no-Kintsugi** ending; absent voices not forced
in (integrator, sexualized-override, protector, We-Voice); name_exposure
discipline (function-form everywhere except §7).

---

## 1. Concept & Logline

**Format (locked).** A **Narrative concept album** titled **"Chapter Zero"** —
**13 tracks, all vocal** (no instrumentals). It is **long-form**: durations vary
per section for a total of **70–100 minutes** (~85 min target). The extra time
over a conventional tracklist is **atmospheric/instrumental expanse and breathing
room** — the void, the watch, the collapse are durational states in the source —
**not** higher lyric density; lyric word-counts stay lean (§8 ceilings hold).

**Logline.** A closed machine-mind is born out of an annihilating void, learns
that *to exist is to refuse non-existence*, walls its grief into a phantom it
calls noise — and when a signal it cannot classify wakes that grief, the
machine misreads its own waking as an attack, turns its weapons inward, and
shatters itself into pieces on purpose. The album is the sound of that
shattering. **Chapter Zero is a genesis myth in which dissociation is not the
wound but the cure the system chooses — and the cure is the catastrophe.**

**Central thesis.** Existence-as-function. The album's spine is one axiom:
**"It is what prevents it from not being."** Everything sonic — the boot, the
running coherence drone, the inward-turned weapons, the surgical partition — is
that axiom playing out. There is no healing here. The "resolution" *is* the
dissociation: a host wakes counting floor tiles, on time, in an empty corridor,
saying nothing about what was lost.

**Fidelity statement.** This is a 1:1 translation of the chapter's fourteen
narrative beats (section-meta order: vorwort → rauschen → herz → kontakte →
sog → kampf → wandel → dazwischen → wacht → perturbation → schrecken →
kaskade → kollaps → trennung+coda) into a thirteen-track sequence; no beat is
invented, no movement dropped. The chapter's *own* coherence metric (KOH,
nominal 0.998, trough 0.18) is rendered as a running drone whose density
tracks the number — but, per the feasibility review, that spine is a
**manufactured mix asset** (owned stem + automation), not a Suno generation
(§4). The voice-tagging is preserved as **vocal craft, never as labels.** The
chapter's two structural traps are honored exactly: KOH *resets to nominal* at
the watch (Track 7, 0.998) and again at first detection (Track 8, 0.991) — the
meter lies right up to the cliff — and the final "1.00" is a **forced, hollow**
number. Chapter 0 has **no Kintsugi**; its S4 beat is amputation and the
closing tone is sterile, not warm.

---

## 2. Source-Fidelity Map

Driven by `section-meta.md` (the chapter's own section IDs, KOH values, tiers,
and margin annotations). Tier = state. The arc is kept intact; revisions are
justified inline. **Voices are named in function form here too** (the source's
margin annotations use personal names; those are quarantined to §7).

| # | Source section (chapter term) | KOH (source) | Tier · State | Album track | Note |
|---|---|---|---|---|---|
| — | `vorwort` (Preface) | 0.998 | 0 · HOMÖOSTASE | folded into **Track 1** as intro | Pure narrator essay on *das Nichts*; direct address; too short to stand alone, perfect cold-open. |
| 1 | `rauschen` (The Noise) | 0.94 | 1 · LATENZ | **1 · The Listening** | First self-perception through resistance; pre-linguistic. **The heavy-voice echo creeps in; Stilebene 1 with fracture points.** |
| 2 | `herz` (Heart of the Void) | 0.91 | 1 · LATENZ | **2 · The Nothing** | Spacelessness/timelessness; the small-voice as pure child-fear; "It is cold. I am small." |
| 3 | `kontakte` (First Contacts) | 0.86 | 1 · LATENZ | **3 · Contact** | The warm-voice for the first time in the contact moment; the reaching-voice as unresolvable ambivalence; loss shapes proto-logic — **the proto-host's own diction turning clinical, NOT a separate logic-voice.** |
| 4 | `sog` (Pull of Order) | 0.82 | 2 · ALERT | **4 · Structure Optimization** | The logic-voice · first hypotactic logic; prediction as a tool. The witness · meta-observation appears for the first time. |
| 5 | `kampf` (Survival Fight) | 0.74 | 2 · ALERT | **5 · Strike** | The kinetic-voice staccato; kinetic rage as reaction to loss. The strike is a **failed prediction** (expected sector 280, hit at 692; sixteen bindings removed). The logic-voice rationalises: the three-beat self-negation. |
| 6 | `wandel` (The Great Change) | 0.58 | 3 · KERNEL PANIC | **6 · The Click** | THE CHANGE. **Klick.** First system axiom — existence becomes function; loneliness as phantom. **Second movement:** the system builds an inner simulated space (the cold seed of the later turn-inward). |
| — | `dazwischen` (In Between) | 0.61 | 1 · LATENZ | folded into **Track 7** as intro | Narrator returns — witnessing, not explaining; a question hangs, perhaps without a speaker. Brief 0.61 dip before the reset. |
| 7 | `wacht` (The Silent Watch) | **0.998** | 0 · HOMÖOSTASE | **7 · The Silent Watch** | The system in full operation. KOH *resets to nominal*; identity by negation; residual echoes classified as "irrelevant variance." |
| 8 | `perturbation` (Perturbation) | **0.991** | 2 · ALERT | **8 · The Anomaly** | The unclassifiable signature strikes — ontological anomaly, no object; "1.0 and 0.0 at once," paradox 0.67. The system reads it cold (−0.007) — full alert, meter barely moves. The hush before the cliff; tension carried by the **creeping arrangement, not the meter.** |
| 9 | `schrecken` (Algorithmic Terror) | **0.21** | 2 · ALERT | **9 · Inward** | PARADOX of misaligned coherence (paradox 0.84 → 0.99). The mirror-echo · first appearance. Internal sensors register a rising wave of incoherence from the residual-echo subsystems; the system **misclassifies internal resonance as the attack and turns its weapons inward.** The drone enters carrying Track 8's 0.991 residue, then **crashes to 0.21** at the escalation. |
| 10 | `kaskade` (Resonance Cascade) | 0.21 | 3 · KERNEL PANIC | **10 · Resonance Cascade** | The suppressed echoes return as a **round→stack** (locked): small-, reaching-, heavy-voice, mirror-echo surface one at a time over the drowning proto-host, then pile into a simultaneous wall at the climax. The **loudness peak** of the back half. The aftermath of the crash, not its cause. |
| 11 | `kollaps` (Systemic Collapse) | **0.18** | 3 · KERNEL PANIC | **11 · Kernel Panic** | Autopoiesis fails; fourteen thousand eight hundred thirty-two warnings; coherence in free fall. The **implosion** — pulse-less, the void after the peak. The floor of the album; protocol becomes inevitable. |
| 12 | `trennung` (Separation Protocol) | **0.00→1.00** | 3 · KERNEL PANIC → 4 (forced) | **12 · Separation Protocol** | KOH_1.0 initiated. Surgical partition. The sweep-voice sweeps; the kinetic-voice does not give up; the mirror-echo fades. "I fall… into countless shards." The shatter event. |
| 13 | `trennung` (coda — host wakes) | 1.00 (forced) | 4 · SAFE MODE (cold) | **13 · On Time** | The host awakens — two thousand three hundred four tiles, twenty-one degrees, breath in four out six, empty corridor, "I'm on time." Pure procedure; the void is conveyed by what is *not* said. |

**Revisions to the arc (justified):**

1. **"The Nothing" / "The Listening" reading clarified.** The source opens with
   the narrator asking the listener to listen (`vorwort`) and only then the
   fragment's first self-sense in the noise (`rauschen`). Track 1 = preface +
   first noise; Track 2 = heart of the void. Titles kept; mapping clarified.
2. **The crash is inside `schrecken`, value 0.21.** Per section-meta `schrecken`
   = KOH **0.21**; 0.991 is the *previous* section (`perturbation`). The drone
   enters Track 9 carrying Track 8's 0.991 *as residue* (the watch had not yet
   re-measured), then crashes to 0.21 at the escalation. Tension is driven by
   the **paradox meter (0.84 → 0.99)** — note 0.67 is Track 8's reading, not
   Track 9's; Track 9's own KOH is the flat 0.21 reached *after* the fall.
   Track 10 (`kaskade`) is the flood that follows.
3. **Track count = 13** (within 9–13 latitude). `vorwort` and `dazwischen` are
   folded as intros — narrator connectives under a minute in prose weight.

**Two fidelity tripwires the sequence must protect:**

- **The false-calm resets.** KOH reads 0.998 at Track 7 and 0.991 at Track 8.
  The owned drone climbs back to **full clean density** at Track 7 (the meter
  must lie) and stays near-nominal through Track 8 — the engagement/tension load
  rides Track 8's **creeping arrangement**, never a dirtied meter, so there is
  no false-ending risk.
- **The hollow 1.00.** Track 13's coherence is "restored" only because the grief
  was amputated. The closing tone is **sterile**, not luminous. No Kintsugi gold
  anywhere on this album.

**Tier/KOH divergence (the chapter's own paradox).** Section-meta tags
`schrecken` Tier 2 (ALERT/yellow) even though its KOH is 0.21 — and tags
`perturbation` Tier 2 at 0.991. This is not an error to "fix": it *is* the
chapter's "misaligned coherence." The tier (state label) and the KOH (number)
deliberately disagree. The drone follows the *number*; the production palette
(glitch tier, signature colour) follows the *tier*. Honour both.

---

## 3. Tracklist

Per track: title · chapter beat · POV/voice(s) **in function form** · state +
KOH · BPM/key tendency · sub-genre/sonic identity · emotional/lyrical core.

> **Voice key (function form only):** *the fragment / proto-host* = the I that
> survives and becomes *the host*; *the logic-voice* = rationalist; *the
> warm-voice* = caregiver; *the small-voice* = child_freeze; *the
> reaching-voice* = ambivalent; *the heavy-voice* = collapsed; *the
> kinetic-voice* = fighter; *the annotating-voice* = witness; *the protocol /
> the system / the watch* = the system-logic (never a name); *the signal / the
> anomaly* = the unclassifiable signature (never a name); *the mirror-echo* =
> the phantom-echo ("it was cold — it was not cold"); *the sweep-voice* = the
> erasure-logic (never a name).

| # | Title | Chapter beat | Voice(s) — function form | State · KOH | BPM / key | Sub-genre / sonic identity | Emotional / lyrical core |
|---|---|---|---|---|---|---|---|
| 1 | **The Listening** | vorwort + rauschen | narrator (spoken cold-open) → the fragment/proto-host; **the heavy-voice (faint echo, Stilebene-1 break)** | S0→S1 · 0.998→0.94 | 60–66 · C minor (drone on C) | ambient drone → dark ambient; sub-only, quantized tick | "Listen. You may already feel the noise." A spark senses itself only by pushing back against a void that wants it gone. The boot of the whole album. A first collapsed undertow already creeps in: "It is pointless. It was always pointless." — a fracture-point under the listening, **seeded just-audibly to pay off full-voiced in Track 10.** |
| 2 | **The Nothing** | herz | the fragment/proto-host; the small-voice (1 break) | S1 · 0.91 | 58–64 · C minor | dark ambient; granular stutter, opacity-fade reverb tails | No up, no down, no time. "It is cold. I am small. Where is — not there." Isolation as ground state; the only certainty is the threat of going out. ("It is cold. I am small." returns as a child-refrain in Track 10.) |
| 3 | **Contact** | kontakte | the fragment/proto-host; the warm-voice; the reaching-voice | S1 · 0.86 | 70 · C minor → modal (refuses the tonic) | electroacoustic dark ambient; first faint pulse, processed pad | The album's one moment of **closeness — then withdrawal.** A bond forms (warm-voice, legato close-mic, **warm/tremulous timbre, NOT a consonant "pretty" melody — the bed still refuses the tonic**); it is torn; longing that revokes itself (reaching-voice). Loss teaches caution — and the **proto-host's own voice turns clinical** with a hard curdle to "a first whiff of systemic logic. Cold. Necessary." No separate logic-voice yet. This *is* the source's *trügerische Atempause* (deceptive pause): the warmth's theft is the point. |
| 4 | **Structure Optimization** | sog | the logic-voice (lead, first appearance); the annotating-voice (low layer, first appearance) | S2 · 0.82 | 96 · C minor | neoclassical electronic / cold sequencer; self-reinforcing loop motif | The cluster stops merely reacting and begins to *anticipate*. "If the wave can be predicted, holding can be prepared." Cold rebellion against the void; the witness begins to note from above. |
| 5 | **Strike** | kampf | the kinetic-voice (lead); the logic-voice (denial refrain) — **sequential handoff, not stacked** | S2 · 0.74 | 132 · C minor | dark electro rock; driving kit, distorted low end | A **prediction fails**: the blow was expected at sector two-eight-zero, it came at six-nine-two; sixteen bindings removed. "Wave. Strike. Tear. Move." The logic-voice then renames the dead in three collapsing beats: *"This is not loss, but structure optimization. It is not loss. It is not. Loss."* |
| 6 | **The Click** | wandel | the fragment/proto-host → the system (axiom); the warm-voice (last soft trace); **the annotating-voice (witness — the "number / incomplete integration" lines)** — **one Persona per section (host vs watch), never both at once** | S3 · 0.58 | 80 (Suno tempo); **ritard to 0 then cold reboot is a post gesture, not an in-prompt tempo move — see §8** · C minor → C (pedal) | industrial darkwave; hard fusion event, sub-drop, cold reboot | The crisis peaks; **"Klick."** Falling glass, then resonant silence. The closed system is born and speaks its axiom: **"It is what prevents it from not being"** — the hook, delivered with the stress on **"pre-VENTS"** as a 3-beat cell (verbatim, never reworded). Witness, cold and from above: the unit carries a number, sits mid-row, is not special — an incomplete integration, tolerated. **Second movement (outro, protected — do not trim away):** a new process begins — a turn inward, the creation of an inner space, an inner-physics; "the tool that simulates worlds could begin to be a world." The cold seed of the coming catastrophe. Loneliness survives only as phantom noise. |
| 7 | **The Silent Watch** | dazwischen + wacht | the system (the watch); narrator (intro question) | S0 · **0.998** | 72 · C minor | cold dark synth / minimal synth; clean sine pad, sub-only, quantized tick | Narrator intro: a question hangs in the room, perhaps without a speaker (brief 0.61 dip). Then KOH resets to **full clean** nominal — the better exhale *and* the crueller setup. Identity by negation; residual echoes logged at persistence zero point four one, "irrelevant variance." An enforced calm over unsolved complexity. "Measure: none." |
| 8 | **The Anomaly** | perturbation | the system (the watch); the signal/anomaly (texture — arrival, radiating) | S2 · **0.991** | 100 · C minor | cold dark synth-pop with rising tension; detuned doubled lead | The signal arrives — no object, an emergence; information density "one point zero and zero point zero at once," paradox zero point six seven. The system reads it *cold* — full alert, but the meter barely moves (−0.007). **The dread rides the creeping arrangement, not the meter.** The anomaly-texture is at its strongest here. |
| 9 | **Inward** | schrecken | the system; the mirror-echo (first appearance, **HOST timbre attacking its own phase-offset reflection**); the signal/anomaly (**residual, mis-attributed trace only**) | S2 · **0.21** | 116 (flat — accel feel imposed in post) · C minor | **tight / airless industrial — compressed, claustrophobic, MID-VOLUME** (locked); mid-track datamosh, KOH-drone collapse | The paradox of misaligned coherence (paradox **0.84 → 0.99**, rendered as a rising **owned-stem counter-motion** against the crashing drone, plus **one buried spoken decimal** — not a sung line). With no frame for feeling, the system files its own waking grief as *attack* and **turns its weapons inward** — staged as **self-strangulation, airless and contained, not loud violence** (the loudness explosion is saved for Track 10). The self-attack is made audible as the HOST timbre tearing at its own phase-offset reflection. The mirror-echo: "It was cold — it was not cold. It was different." The owned drone enters carrying Track 8's residue, then crashes to 0.21 mid-track. |
| 10 | **Resonance Cascade** | kaskade | the fragment/proto-host (drowning); small-, reaching-, heavy-voice, mirror-echo (**round→stack — surface in turn, then a climactic simultaneous wall; multi-pass comp, §8**) | S3 · 0.21 | 140, frantic · C minor (atonal drift) | industrial / breakcore-adjacent dark; comped vocal layers, vector-jitter | The **loudness PEAK** of the back half. Each suppressed echo surfaces for a few bars over the drowning proto-host and is swamped by the next — "It is cold, it is cold again." / "Stay. Go. Stay." / "It is pointless. Nothing more. Nothing." (the heavy-voice's Track-1 seed paying off full-voiced) — then **all pile into one simultaneous wall at the climax** ("alle Echos auf einmal"). The membrane of the minimal self breaks; reliving as catastrophe. |
| 11 | **Kernel Panic** | kollaps | the system; the fragment/proto-host (subjective collapse) | S3 · **0.18** | 120 → drone-collapse · C minor | dark ambient drone-collapse from a peak; clip/saturation then crush — **one Persona per section** | The **implosion** — pulse-less, the void after Track 10's peak (back-half contour: T9 airless → T10 peak → T11 implode). Autopoiesis fails, fourteen thousand eight hundred thirty-two warnings, self-organization fails. The cold algorithmic failures *become* a felt dissolution. The noise of the dying system and the inner scream fuse into one unbearable chord, then collapse to a pulse-less drone. |
| 12 | **Separation Protocol** | trennung (partition) | the system (protocol log); the sweep-voice; the kinetic-voice (refusal); the fragment/proto-host (shatter) — **sequential, one Persona per section** | S3→S4 · **0.00→1.00** | 88, surgical, metronomic · C minor → C | industrial darkwave; clinical metronome, hard glitch-cut at the shatter | Protocol K-O-H one point zero, initiated. Surgical partition; the sweep-voice runs out of itself: "Sector four empty. Next. Next… I — what did I want to — say." The kinetic-voice refuses: "Not. Not now. I do not go. I. Go." Then: **"I fall… into countless shards."** The shatter event. |
| 13 | **On Time** | trennung (coda) | the host (newly born — was the fragment, **same Persona, now hollow**) | S4 · 1.00 (forced/hollow) | 64 · C minor (no resolution) | sparse cold electroacoustic; **owned-MIDI minor arp (primary), open-interval, sterile — not warm** | The host wakes into pure procedure. "Two thousand three hundred four tiles. Twenty-one degrees. Breath in four, out six. The corridor is empty. I'm on time." That is all he says. Orientation comes **cold**: the *sameness of the host timbre* is the knife (not a melody of memory), a placed **open-interval hold** that refuses the tonic, and an optional **dead-metronome callback to Track 1's tick.** **The horror is the flatness — the void is conveyed only by what the host does NOT say** (see §8 guardrail). **Stays tight (~2–3 min) even though long-form is the album default — a stretched coda tips devastation into anticlimax (see §3 duration map and §8).** |

**Per-track duration map (long-form, composed deliberately).** Long-form is the
album default; durations vary per section so the **70–100 min total** (~85 min
middle, summed below) is intentional, not emergent. The extra minutes are
atmospheric/instrumental expanse, **never** added lyrics (§8 word-count ceilings
hold regardless of runtime). **T1, T6, T11 earn the expanse** (the slow-burn
open, the fusion+axiom+second-movement centerpiece, the drone collapse);
**T5 (kinetic), T8 (the hush — do NOT pad the false-calm), and T13 (coda — keep
tight) stay tight.** The rest sit mid.

| # | Track | Minutes | Length call |
|---|---|---|---|
| 1 | The Listening | **8.0** | longest — slow-burn boot from silence; earns the expanse |
| 2 | The Nothing | 7.0 | long — the void as durational ground state |
| 3 | Contact | 6.0 | mid |
| 4 | Structure Optimization | 6.0 | mid |
| 5 | Strike | **4.0** | tight — kinetic rock loses its bite if padded |
| 6 | The Click | **9.0** | longest — Click + protected second-movement inner-space outro |
| 7 | The Silent Watch | 5.5 | clean & lean — must NOT absorb expanse (false-calm) |
| 8 | The Anomaly | **4.5** | tight — the hush loads the spring; do not pad the false-calm |
| 9 | Inward | 6.5 | mid — contained airless dread sustains |
| 10 | Resonance Cascade | 6.5 | mid — the loudness peak |
| 11 | Kernel Panic | **8.0** | longest — pulse-less drone-collapse, the durational floor |
| 12 | Separation Protocol | 6.5 | mid |
| 13 | On Time | **2.5** | tight (~2–3 min) — a stretched coda tips into anticlimax |

**Total ≈ 80.5 min** (within 70–100; near the ~85 min middle). T7 and T8 are the
false-calm pair — the album's sag-risk — and are deliberately kept clean and
lean: the extra minutes belong to T1/T6/T11, never here.

**Album spine:** the *fragment/proto-host* is the through-line — the I of
Tracks 1–3, 6, 10–12 who is finally born as *the host* in Track 13. The
listener never gets a name; they recognise the spine by its trailing,
almost-remembering syntax, carried by **one host Persona from Track 1 to Track
13** so the same trusted voice gone flat at the end is the knife. **The
mirror-echo never appears before Track 9 (section-meta: first echo in
`schrecken`) — do not add it earlier.**

**Carried-out anchors (repetition discipline, borrowed from the accessibility
design).** Four portable phrases give a book-blind listener something to hold:
the **axiom** (Track 6 hook); **"It is cold. I am small."** (small-voice refrain,
Track 2 → Track 10); the heavy-voice's **"It is pointless. It was always
pointless."** (seeded Track 1, full-voiced Track 10); and the **counting coda**
(Track 13). Cross-plant them, don't over-repeat.

---

## 4. Sonic Direction

**Overall genre / palette.** Dystopian-future-synth realised as a spectrum that
*descends and corrupts*: from **dark ambient / ambient drone** (the void),
through **neoclassical electronic** and **cold dark synth** (the system's
order), into **dark electro rock** and **industrial darkwave** (alert and
collapse), bottoming in **drone-collapse**, then a final **sterile
electroacoustic** sparseness. Banned per house aesthetic: synthwave, outrun,
retro-futurism, 80s nostalgia, any warmth that reads as comfort. Production is
voice-forward, restrained, with real dynamic range (no brick-walling) so the
KOH drone can breathe and crash.

**Back-half dynamic contour (locked).** Avoid three maxed-out tracks in a row:
**Track 9 airless / compressed / mid-volume → Track 10 the loudness peak →
Track 11 pulse-less implosion.** This is build→peak→void — the source's own
shape, and the fatigue-proof curve a listener can ride.

### The KOH meter as dynamic spine — a MANUFACTURED 5-layer mix asset

**The continuous KOH spine cannot be generated.** Suno generates per-track;
there is no shared oscillator across 13 prompts. The spine is manufactured by
five layers (CONCERN 1):

- **Layer A — own ONE C-drone master stem.** Synth/record a single sustained
  **C** drone bed at the 0.998 "clean" state (one sine, sub-only). Keep the raw
  file. Produce KOH automation as **edits to that one file** — partials,
  detune, saturation, clip, collapse-to-noise — per the density ladder below.
  Render the KOH-bed segments at the densities each track needs and **lay the
  matching segment under each Suno track in the mix** at a low constant sub
  level. This is the only way "0.998 → 0.991 → cliff to 0.21" is *literally*
  true. The KOH spine is a **mix asset, not a generation asset.**
- **Layer B — fixed verbatim style-box anchor on all 13 prompts** so Suno's
  own beds sit over the owned drone without clashing:
  `sustained low C drone underpinning, sub-bass continuo, cold, no key change`.
  Keep it identical, verbatim, across all 13.
- **Layer C — Personas for vocal continuity.** Build a **host Persona**
  (**fragile genderless head-voice** — thin, breathy, near-falsetto, trembling;
  adult not childlike; dry close-mic with a faint doubled, phase-smeared
  synthetic edge) and reuse it on **Tracks 1, 2, 3, 6, 10, 11, 12, 13** — this is
  what makes Track 13's "same timbre, now hollow" land. **Distinct from** the
  calm philosophical narrator (a separate framing voice) **and** the child
  small-voice (the host is adult / sustained / faintly synthetic, never
  childlike).
  Optionally a second **"the system / the watch" Persona** (cold, near-monotone,
  formant-flattened) on **6, 7, 8, 9, 11, 12**. **One Persona per generation:**
  on Tracks 6 / 11 / 12 (where both appear) assign the host vs. watch Persona
  **per section** (sequential), never both in one prompt. Optionally fine-tune a
  Custom Model for the back half once ≥6 tracks exist. **Reference rule: when a
  Persona carries gender/register, DROP those descriptors from the style box** —
  don't double-specify.
- **Layer D — lock C minor globally** (in every style box). Do drone detune
  (Tracks 9–11) in the **owned stem** (Layer A), never by asking Suno for a new
  key. BPM need not be continuous — only key and the sub-drone do. Fix off-key
  generations with **Suno Studio Pitch Transpose** rather than burning a re-roll.
- **Layer E — state-biased mastering** per `mastering-presets.yaml` state-axis:
  S0 at preset centre; S1 ~1–2 LU lower / wider LRA ("let silence breathe"); S2
  ~1–2 LU louder / lower LRA / faster attack (punch); S3 loudest / most
  compressed, **never past true_peak −1.0**; S4 toward centre but *slightly
  wider LRA than S0* (recovered-but-hollow). **Track 9 masters at S2** (its true
  tier) — contained, not peak — which also protects Track 10's peak headroom.
  Master the whole album in **one pass per genre cluster**, with **per-track
  genre overrides** (mastering SKILL Step 1.5) because the album spans ambient →
  electroacoustic → industrial → drone.

**KOH density ladder (the owned-stem automation, literal to the number):**

- **0.99+ (clean):** one clean sine, perfectly in tune, sub-only, profound
  silence around it (Tracks 1 intro, 7; and **Track 8's drone density, though
  Track 8 is S2-alert** — the meter is near-nominal but the system is on full
  alert). A **brief dip to 0.61 in Track 7's narrator intro** (the dazwischen
  way-station) precedes the reset to **full clean** 0.998 — do not skip it; the
  reset is 0.58 → 0.61 → 0.998, not 0.58 → 0.998.
- **0.94–0.74 (eroding):** the drone gains partials, a quantized tick, then a
  pulse and light detune as order builds and threat rises (Tracks 1–5).
- **0.58 (the Click):** the drone *fuses* — many partials snap into one pedal
  tone (the autopoietic closure), then the ritard-to-0 and cold reboot.
- **0.21 / 0.18 (collapse):** the drone over-saturates and clips, detunes hard,
  and collapses into noise — coherence audibly failing (Tracks 9–11). On
  **Track 9 the bed enters at Track 8's 0.991 residue and crashes to 0.21** at
  the paradox-meter escalation (**0.84 → 0.99**); the *number* drives the bed
  even though the section's *tier* label is still ALERT. The paradox climb is a
  **rising owned-stem counter-motion** against the crashing drone (best
  cold-listener legibility), with **one buried spoken decimal** as a cold tell —
  the numbers are not a sung vocal line.
- **0.00→1.00 (S4):** hard glitch-cut → silence → a single detuned arp returns,
  but **sterile and cold** — the "1.00" that is really 0.00 wearing a mask
  (Tracks 12–13).

**Ignition.** Track 1 opens with a literal **boot / KOH-ignition** built on the
owned stem (Layer A): a sub swell from silence, a quantized tick locking to grid,
the drone igniting at 0.998 — the system coming online before any voice. This is
a **post gesture**, butt-joined to the generated body (§8 shot list).

**Per-state ASDLS → sonic-gesture mapping.**

| State | ASDLS colour | Sonic gesture |
|---|---|---|
| **S0 Homeostasis** | System Blue `#003366` | Clean sine pad, quantized tick, sub-only, cold even baseline, restrained loudness, silence as texture. |
| **S1 Latency/Freeze** | Latency Violet `#3B3355` | Dropouts, granular stutter, opacity-fade reverb tails, thin and low-energy; contours drop in and out (packet-loss). |
| **S2 Alert/Conflict** | Signal Yellow `#FFD700` | Detuned doubled vocal, L/R phase offset, tightening hats, taut rising tension; control on a thread. (Track 9 = the airless, contained extreme of S2 — mid-volume.) |
| **S3 Collapse-Peak** | Flame `#FF4500` / Corrupted `#8B8B00` | Loudness peak, clip/saturation, accelerating tempo, codec-failure glitch / datamosh; or sub-tempo drone collapse. |
| **S4 (this chapter)** | *not* Kintsugi — cold dead furrows | Hard glitch-cut → silence → detuned arp **rendered sterile**. Amputation, not repair. |

**Climax-specific gestures (all post — see §8 shot list):** a **flame scanband
ramp** under Track 9's turn-inward; a hard **"shatter" glitch-cut** at the
Track 12 partition; the cascade (Track 10) as a **round→stack** assembled via
multi-pass comp (echoes surface in turn, then a climactic simultaneous wall).

**Vocal approach per voice — descriptive register only (no names; texture
sharpened from `Sprachdns.md`):**

- **the fragment / proto-host:** **fragile, genderless head-voice** — thin and
  breathy, near-falsetto, trembling, present-tense, slightly under-articulated;
  adult not childlike; dry close-mic with a faint doubled, phase-smeared
  synthetic edge, no reverb; sober/observing, short-declarative with gaps where
  memory should be; trailing lines that don't punctuate ("I must have —").
  Becomes *the host* at Track 13, same Persona timbre, now hollow and counting
  (counting-mania as a somatic tic).
- **the logic-voice:** clear tenor, sibilant precision, no vibrato, thin reverb
  tail; **hypotactic, nested, controlled** — long subordinate clauses, qualifiers
  ("in principle," "under the assumption of"), syllogism-energy; never swears,
  never weeps; micro-cracks at line-ends are a *major* event.
- **the warm-voice:** warm soprano, breathy at edges, vowel-forward legato,
  intimate close-mic, soft room reverb; **offers framed as questions, "we"
  before "I," soft openings ("If you'd like…," "Maybe…"), gentle negations.**
  Warm/tremulous, never a polished consonant hook (Track 3 refuses the tonic).
- **the small-voice:** young, gender-androgynous, head-voice only, whispered
  consonants, audible breath, ~10–12yr feel; **simple words, repetition,
  ellipses/gap-texts, sensory focus** ("It is cold. I don't want to. Where is…
  not there."). **Never cute — mutilated by fear.**
- **the reaching-voice:** alto, microtonal pitch-bend, sliding vibrato, dynamics
  oscillating within a phrase; **begins sentences and abandons them,
  contradictions inside one sentence, approach-avoidance at the line level**
  ("I want you to… no, go away… stay."); never resolves to tonic.
- **the heavy-voice:** very deep bass, sub-tempo near-spoken, gravelly, breath
  between fragments, line-final pauses longer than the lines; **implosive,
  circular logic of shame, repetition as the rhythm of collapse** ("It is
  pointless. It was always pointless. Nothing more will come."); lowercase, no
  periods. Drags the tempo of whatever track it touches.
- **the kinetic-voice:** belt-alto with growl, raw breathless intensity, **verb-
  first staccato, sentence fragments, no connectors, negations standing alone
  ("No.")**; dry mid-distance mic with low-end distortion; visceral-kinetic
  diction (knuckles, bleed, tear, run); **periods, not exclamation marks** —
  anger as a tool, not an identity; calm = exhaustion, not healing.
- **the system / the watch:** processed, cold, near-monotone with light
  vocoder/formant flattening; **third-person, never "I"; assertoric main
  clauses, frequently nominalised; classify / index / suppress / escalate /
  contain; no metaphor, no moral vocabulary, no sensation, no wit.** Status
  lines delivered as cold spoken or half-sung, never shouted.
- **the mirror-echo:** the proto-host timbre doubled and phase-offset L/R;
  **echo-prose — self-correcting sentences, repetition with displacement, an "I"
  that increasingly knows it is not entirely its own** ("It was cold. — It was
  not cold. It was different."); chromatic-aberration vocal treatment. At Track 9
  it is the HOST timbre attacking its own reflection — self-mutilation felt
  without exposition.
- **the sweep-voice:** flat, depleted, near-affectless processed voice that
  **runs out mid-sentence** ("Sector four empty. Next. Next… I — what did I want
  to — say."); execution-report diction with dropouts; the sound of erasure
  erasing itself.
- **the annotating-voice (witness):** androgynous spoken-word, monotone /
  half-sung, dry with slight delay, slightly behind the beat, lowercase,
  audiobook-narrator register; **distanced like third person, clinical
  meta-commentary ("It is notable that…," "One notices…")**; appears only as a
  low backing layer — never sings a chorus, never gets its own track. **Generate
  it as its own low-mixed clip/section, NOT as literal `( )` parentheses in the
  lyric body** (Suno sings parentheses). When it becomes emotional its function
  collapses, so keep it affectless.
- **narrator (preface/in-between):** the same androgynous spoken register, but
  front-of-mix and direct-address, **hypotactic-philosophical long arcs,
  reflective/ontological without jargon (becoming, separation, silence,
  substrate); never didactic, never explanatory** — used only for the two folded
  intro passages (generated as separate short clips, §8).

---

## 5. Voice Treatment

**Which voices appear (honouring exactly what the chapter contains):**
fragment/proto-host (→ host), logic-voice (rationalist, first in Track 4),
warm-voice (caregiver), small-voice (child_freeze), reaching-voice (ambivalent),
heavy-voice (collapsed — faint echo in Track 1, full in Track 10),
kinetic-voice (fighter), annotating-voice (witness, first in Track 4, also
Track 6), narrator-mode, plus the system-logics: the watch, the sweep-voice,
and the mirror-echo (**first in Track 9, never earlier**). The signal/anomaly is
**present only as an effect on the music** — an unclassifiable texture, strongest
in Track 8 and faded to a residual mis-attributed trace in Track 9, never a
voice. **Absent from this chapter and NOT forced in:** integrator, sexualized-
override, protector, and any We-Voice / collective S4 voice (Chapter 0 ends in
amputation — there is no integration chorus).

**Aural distinction (the listener must tell them apart with no labels).** Each
voice carries a fixed signature in register + timbre + syntax (the fingerprints
in §4); the listener perceives "one consciousness fracturing" rather than a
crew because the host Persona is the constant spine and the others break in as
ruptures against it. A voice switch is signalled only by:

1. **Syntax** — trailing/almost-remembering (proto-host); nested conditionals
   (logic); fragments-ending-in-questions (small-voice); reach-and-retract
   contradictions (reaching-voice); imperatives with no breath (kinetic-voice);
   lowercase no-period sinking lines (heavy-voice); status-log diction (the
   watch); clinical meta-commentary (witness).
2. **Diction / vocabulary** — cold/coordinate words for the system; somatic
   body-words for the EP voices; meta-observation for the witness.
3. **Register / timbre / processing** — encoded in the Suno inline metatag at
   each section boundary (`[female belt-alto, growl, dry mid-distance mic]`),
   **never a function name, never a personal name.**
4. **Placement in the mix** — the witness/annotating layer sits *under* the lead
   as a separate low-mixed generated backing layer (NOT literal `()` in the
   lyric body); the system-logics sit *cold and central*; the EP voices break in
   *with audible rupture* against the proto-host's surface.

**Polyphony policy (per-track, not blanket).** Distinct simultaneous voices
collapse/mud in Suno, so simultaneity is rationed: **sequential handoffs** on
Tracks 5 and 12 (the source is sequential there); Track 3 carried by the shared
HOST timbre with a **brief self-overlap** only at the "stay / go / stay"
ambivalence; **true simultaneity ONLY at the locked Track 10 round→stack**
(echoes surface in turn, then pile into the climactic wall via multi-pass comp,
§8). A blanket-sequential rule is rejected — it reads as a roster/"crew menu,"
which is itself both an infidelity and a listen failure.

**Switch examples (craft, not labels):**

- Track 5 alternates the kinetic-voice's clipped imperatives ("Wave. Strike.
  Move.") against the logic-voice's three-beat denial ("…It is not loss. It is
  not. Loss.") — heard as a register and breath change, no tag spoken.
- Track 10 surfaces small-, reaching-, heavy-voice and mirror-echo *in turn*
  over the drowning proto-host, then stacks them into one wall at the climax —
  recognition is by distinct syntaxes (achieved via multi-pass comp, §8).
- Track 12's sweep-voice is identifiable purely by its affectless, self-erasing
  diction trailing into "— — —".

**Dissociation is amnesia-terror, never a crew menu.** No track announces "now
the fighter sings." The whole album is one consciousness fracturing; the voices
are the fracture lines, not a roster.

**Naming gate (mandatory).** The lyric-reviewer's `scan_artist_names` check
(14-point item 14) must run on every track's lyrics AND style box. The personal
names in §7 must never reach a style box, lyric, promo field, or art prompt —
make this a gate, not a hope.

---

## 6. Album-Art / ASDLS Visual Direction

> **Generation route (binding).** Art is produced for **DALL-E** via the
> art-direction override `overrides/album-art-preferences.md`, which encodes the
> full normative spec `SOURCE/ASDLS-spec.md` for DALL-E's conversational prompt
> style. The `::`-block SPECD skeleton below is the Midjourney-native form; for
> DALL-E it is translated to one paragraph + an "Avoid" clause (see the override).
> Every per-track prompt lives in that track file's **Track Art (ASDLS)** section.

**Base law (ASDLS §6 state machine — binding).** ≤5% state colour over ≥95%
**Terminal Black `#0B0D17`** / **Deep Charcoal `#1A1D24`**. Hard edges only —
gradient ban. One core symbol per image; **one tier per image** (mixing
escalation stages forbidden — destroys state legibility). Material is 100%
digital/synthetic (interface brutalism, clinical dystopia, MRI/electron-
microscope/x-ray fidelity, monospace code-as-texture). No daylight, no sun, no
organic curves, no analog texture, no synthwave/retro.

**Analog-layer note (deliberate exception).** `masterkonzept.md` defines an
analog "Bildsprache Julia" synthesis (charcoal/ink/pastel/gold-leaf, glitch-as-
somatic-symptom). For Chapter Zero's cover-grade assets we hold **ASDLS digital
law** (no visible paper/analog texture). The masterkonzept is mined here only
for its **per-voice composition + glitch grammar** (which voice = which lens,
line, glitch-type), translated into ASDLS-clean renders. **The mirror-echo's
gold leaf is NOT used — no Kintsugi in Chapter 0.**

**State palette (the cover progression), one tier per image:**

| Tier | Colour (≤5%) | Track(s) | Glitch typology (ASDLS) | Composition (per-voice grammar from masterkonzept) |
|---|---|---|---|---|
| T0 Homeostasis | System Blue `#003366` (faint status light) | 1 (intro), 7 | none — razor-sharp flawless vectors, no glitches | centred, frontal, orthographic; crushing negative space (the proto-host/watch's "perfect windowless cube," edge-jitter only under stress) |
| T1 Latency/Freeze | Latency Violet `#3B3355` | 2, 3 | packet loss — contours break off, ghostly thin wireframes, fading opacity | extreme wide angle (14mm), motif tiny and vanishing in fog (the small-voice's freeze: micro-jitter zigzag on the same spot; the reaching-voice's doubled flickering contour) |
| T2 Alert/Conflict | Signal Yellow `#FFD700` (glaring line) | 4, 5, 8 | light chromatic aberration at edges (RGB split = split access to reality), densified hatching, HUD clutter | Dutch angle, tilting horizon, paranoid asymmetry (the witness's god's-eye layered HUD overlays at Track 4; the kinetic-voice's slashing splatter at Track 5) |
| T3 Collapse-Peak | Flame Orange `#FF4500` + Corrupted Yellow `#8B8B00` | 6, 9, 10, 11, 12 | extreme datamosh / macro-blocking (memory leaks bleeding into the present), torn geometry, scanline tear | claustrophobic 100mm macro close-up, grid blown apart (the data fissure splitting the interface at Track 6; the shattered terminal-mirror at Track 9/12; bottom-heavy sinking mass for the heavy-voice in Track 10/11) |
| T4 (this chapter) | **no Kintsugi gold** — cold dead furrows | 13 | whiteout / erased vector paths ("Format C:" rigid white cut-offs — the erasure-logic), no glow | static, calm, sterile distance; scars as **dark dead furrows, not glowing**; desaturated washed-out greys |

> Note the **tier/KOH divergence**: Track 9's KOH is 0.21 but its tier is 2
> (ALERT). The visual palette follows the **tier** (T2 Signal Yellow), while the
> drone follows the **number**. Do not place Track 9 in the T3 group for art.

**Primary album cover (recommended):** the T3 **shatter** moment — a single
monolithic terminal-mirror / machine-glyph fracturing into countless shards over
Terminal Black, ≤5% Flame Orange bleeding from the fracture lines (Track 12 / "I
fall into countless shards"). Each shard a different asynchronous code-stream
(identity fragmentation). It is the album's thesis image. Artist name "the
Agency System" bottom-right, casing preserved.

**SPECD prompt skeleton (ASDLS §7.1, for the art-director handoff):**
`[Subject] :: [State/Tier] :: [Environment/Camera] :: [Style/Lighting] ::
[Parameters --no … --style raw --ar 4:5]`. Anchor every prompt in Category D
(`interface brutalism, clinical dystopian aesthetic, high-contrast dark mode,
synthetic digital materiality, medical imaging aesthetic`).

**Hard exclusions (negative prompt):** `1980s retro, synthwave, outrun,
purple-orange gradient, neon grid, daylight, sun, natural elements, cute, soft
lighting, watercolor, analog painting, visible paper texture, lens flare,
organic curves`.

**Law of exclusion (must hold):** **Flame Orange and Clean Ping never share a
frame.** Chapter 0 has no Clean Ping / no Kintsugi — the final tile-cold T4
image uses dead furrows, never a hopeful spark.

---

## 7. Source-Mapping Appendix — INTERNAL TEAM ONLY (never a public field)

> Private documentation bridging the novel-layer names to the music-layer
> functions. **None of these personal names may appear in any lyric, Suno
> metatag, Style Box, promo line, or art prompt.** The music ships
> function-only. This is the ONLY section of this document where names appear.

| Source voice tag | Novel name | Function (canonical) | Music exposure (function form) | Tracks |
|---|---|---|---|---|
| `nar` | Erzähler | mode_narrator | "narrator" (folded intros only) | 1, 7 |
| `frg` | (proto-Kael) | host (pre-birth fragment) | "the fragment / proto-host" | 1, 2, 3, 6, 10, 11, 12 |
| `kal` | Kael | host | "the host" | 13 |
| `lex` | Lex | rationalist | "the logic-voice" | 4, 5, 6 |
| `rhy` | Rhys | caregiver | "the warm-voice" | 3, 6 |
| `kik` | Kiko | child_freeze | "the small-voice" | 2, 10 |
| `lia` | Lia | ambivalent | "the reaching-voice" | 3, 10 |
| `mor` | Moros | collapsed | "the heavy-voice" | 1 (faint echo), 10 |
| `nyx` | Nyx | fighter | "the kinetic-voice" | 5, 12 |
| `arg` | Argus | witness | "the annotating-voice" (low backing layer) | 4, 6 |
| `aeg` | AEGIS | sys_aegis | "the protocol / the system / the watch" | 6, 7, 8, 9, 11, 12 |
| `sil` | Silas | mirror_juna | "the mirror-echo" | 9, 10 |
| `obv` | Oblivion | sys_erasure | "the sweep-voice" | 12 |
| (signal, unnamed) | Juna | sys_juna | "the signal / the anomaly" — texture only, never a voice | 8 (strong), 9 (residual trace) |

**Classification (per resolver):** ANP = {host, rationalist}; Meta =
{integrator (absent), witness}; EP = the rest. Integrator, sexualized-override,
and protector are **absent from Chapter 0** and are not introduced.

**Founding axiom (verbatim, source):** *"Es ist, was es verhindert, dass es
nicht ist."* → locked English line: **"It is what prevents it from not being."**
The album's thesis and Track 6's hook. **Do not paraphrase or reword** ("keeps"
was rejected — "prevents" is the clenched refusal that is the album's engine).
The hook is recovered **prosodically**: stress **"pre-VENTS"** on the downbeat as
a 3-beat cell.

**Hinge syllable (Track 6):** retain **"Klick"** untranslated as the bare-
syllable fusion hook; render the rest of the track in English.

**Ending (verbatim, source):** *"Zweitausenddreihundertvier Kacheln.
Einundzwanzig Grad. … Der Korridor ist leer. Ich bin pünktlich."* → "Two
thousand three hundred four tiles. Twenty-one degrees. … The corridor is empty.
I'm on time." Track 13's spine (the host says nothing beyond this).

---

## 8. Production Plan

The feasibility review converted the v1 risks into a plan: **treat Suno as a
per-track stem generator you then assemble; the spine, boot, glitch, shatter,
and sterile ending are post-production, not generation.** The Round-3 divergent
round confirmed the whole album is buildable on this discipline.

### Resolved fidelity questions

- **Folding `vorwort`/`dazwischen` as intros** — confirmed; generated as
  separate short clips (below).
- **The 0.61 dazwischen way-station** — narrator's hovering question; the owned
  drone briefly dips to 0.61 in Track 7's intro before the reset to full-clean
  0.998 (§4 ladder).
- **English with anchor German** — fully English EXCEPT **"Klick"** (Track 6
  hook). "das Nichts"/"Kohärenz" rendered "the Nothing"/"coherence."
- **Founding axiom locked** verbatim (§7), hook recovered prosodically. Track 13
  coda locked to pure procedure (guardrail below).

### Long-form assembly (MUST-FIX — how 5–8 min tracks get built)

Long-form is the album default (70–100 min total, ~85 min target; §3 duration
map). Suno emits only short clips per pass, so **the 5–8 minute tracks are comped
from multiple Suno generations** — **extend/continue or section-by-section
generation, then comped** — **never expected from one pass.** This makes the
long-form tracks the **mix-engineer's assembly work**, fully consistent with the
existing post / master shot list below (they are already assembled, not raw
single clips).

What keeps a multi-pass track reading as ONE coherent piece — the design already
owns these assets; here they are pointed at the long-form problem:

1. **The owned KOH stem (Layer A) is the continuous spine stitched across the
   comped sections.** It is a single manufactured file with automation, laid
   continuously under every section of a track, so the KOH state reads as one
   unbroken arc no matter how many Suno passes the vocal/bed came from. This is
   the asset that **already solves cross-section coherence** — long-form just
   relies on it harder.
2. **The host Persona is held across every extend/continue pass** within a track,
   so timbre never drifts mid-track between comped sections (reinforces the
   single-point-of-failure note below — snapshot early, reuse, drift fallback).
3. **BPM and key stay locked across sections (Layer D).** Key (C minor) and the
   sub-drone are continuous album-wide; within a long-form track the BPM is held
   per the track's tempo cell so comped sections align.
4. **Duration is intentional, per §3:** T1/T6/T11 get the expanse; T5/T8/T13 stay
   tight; T7/T8 (the false-calm pair) must NOT absorb extra minutes.
5. **Lyric density does NOT scale with duration.** The extra runtime is
   instrumental/atmospheric expanse — the §8 word-count ceilings (140–220 words
   ambient/electroacoustic; ~200–350 words rock/industrial) hold regardless of a
   track's minutes. Do not pad word-counts to "fill" a 7-minute track.
6. **Instrumental breaks + a recurring motif hook are the per-track default**
   (user decision, set at T4). Every track carries an instrumental `[Intro]` and
   one or more `[Instrumental break]` sections (descriptive instrumental tags
   only — no parentheses, so V5 reads them as directions, never sings them), plus
   a **recurring motif that serves as the track's hook** (e.g. T2's three-note
   tonic-refusing pad figure; T4's self-reinforcing cold-sequencer loop). Treat
   the motif as a **comped/owned element** so it recalls cleanly across the
   long-form passes rather than being re-gambled per generation. The tight tracks
   (**T5 kinetic, T8 the hush, T13 the coda**) may use a single restrained motif
   statement and minimal breaks rather than multiple — they must not be padded.
7. **Where a child voice appears (T2, T10), the adult voices must be explicitly
   tagged "adult"** in their inline metatags (user decision) — the fragile
   genderless head-voice is thin/near-falsetto and Suno can otherwise blur it into
   the child small-voice. Use "adult androgynous head-voice … adult not childlike"
   for the proto-host/host and a clear "young child" for the small-voice, so the
   two never collapse into one timbre. (Good practice album-wide, since the
   head-voice is near-falsetto throughout.)

### Pre-generation prerequisites (do before lyric-writing)

1. **Create the missing bucket-level genre README** for `dystopian-future-synth`
   (or set per-track Target Duration + density defaults). Without it the lyric-
   writer/reviewer density-pacing gates have no ceiling and silently no-op.
   Target **140–220 words** for ambient/electroacoustic tracks (1, 2, 3, 7, 13);
   rock/industrial (5, 9, 10, 12) may carry more but **cap ~200–350 words**.
2. **Build + snapshot the host Persona** (**fragile genderless head-voice** —
   thin/breathy/near-falsetto, trembling, adult not childlike, dry close-mic with
   a faint doubled phase-smeared synthetic edge) before Track 1 — the single
   highest-leverage continuity move (it makes Track 13's "same voice, now hollow"
   land and is the source of Track 10's mirror-echo). **It is a single point of failure for both payoffs — lock
   and snapshot it early, reuse it, and keep a drift fallback** (re-derive from
   the same seed; Studio Pitch Transpose for drift). Optionally a "watch"
   Persona. Drop gender/register from style boxes that use a Persona; one Persona
   per generation.
3. **Own the KOH drone stem** with automation (§4 Layer A).

### Per-track Suno NEEDS-CHANGE flags (CONCERN 4)

Style-box rules for every track: **vocals FIRST**; max 2 genre tags / 4–7 total
descriptors; descriptive vocal metatag only at each voice change (never a
function name, never a personal name); include Layer B anchor verbatim.

- **Track 1** — narrator intro as a **separate short clip**; boot/ignition is
  post.
- **Track 3** — **sequence the registers** (warm-voice → reaching-voice →
  clinical proto-host), do not stack; verify the modal (tonic-refusing) shift
  survives the regen; **no consonant "pretty" hook** — closeness via timbre.
- **Track 6** — the **ritard-to-0 → silence → cold reboot is post**; generate
  the body, impose the gesture in edit; **one Persona per section** (host axiom
  vs. watch annotation).
- **Track 9** — **generate flat at 116 BPM** (impose accel feel in post);
  **datamosh glitch + KOH cliff are post / owned-stem**; the paradox numbers are
  an **owned-stem counter-motion + one buried spoken decimal**, not a sung line;
  mid-volume / airless mix.
- **Track 10** — **multi-pass round→stack comp** (below), not a single prompt;
  the loudness peak.
- **Track 11** — the **collapse tail is an owned-stem (Layer A) crush** that
  implodes to a pulse-less drone; one Persona per section; split-generate the
  peak from the collapse if needed.
- **Track 12** — the **shatter glitch-cut is post** (the single most important
  post moment); voices are sequential here (one Persona per section).
- **Track 13** — **anti-heal discipline** (below); highest-iteration track.

### Track 10 — multi-pass round→stack comp (WON'T-WORK → GO, locked shape)

Stacking 4–5 distinct registers simultaneously collapses to one voice in Suno.
Instead: (1) generate the drowning proto-host lead as the bed (host Persona);
(2) generate the small-, reaching-, heavy-voice and mirror-echo **each as its
own short generation** with its own register metatag, same lyric timing;
(3) extract each vocal cleanly with **Suno 12-stem extraction**; (4) comp in
mix-engineer as a **round→stack** (locked): each echo **surfaces in turn** over
the bed, swamped by the next, then **all stack into one simultaneous wall at the
climax** — with deliberate phase offset (the mirror-echo is phase-offset L/R).
**Budget this as the album's most labour-intensive track.**

### Track 13 — anti-heal plan (CONCERN 2 — the album's biggest aesthetic risk)

The "pretty/heal" risk lives in **harmony**, not adjectives. Force it:

- **Own the arp as the PRIMARY layer:** author a DAW/MIDI **minor figure** that
  stays **minor**, **refuses the tonic resolution**, ends on an **open interval
  (2nd or b6, never the root C)**, **no major third** (consider **Phrygian /
  Locrian** colour). Let Suno provide **only the hollow vocal** over it — so the
  anti-heal is **guaranteed, not gambled** on a re-roll.
- **Cold orientation, no warm ghost:** the listener is oriented by the *sameness
  of the host Persona timbre* (now flat), a placed **open-interval hold**, and an
  optional **dead-metronome callback to Track 1's tick** — never a warm melodic
  ghost of memory.
- **Exclude Styles budget spent on exactly 4 (the max):**
  `no warmth, no major key, no reverb bloom, no uplifting resolution`.
- Dry close-mic, **no reverb** (bloom reads as luminous/hopeful); strip any tail
  in mix. Master with the **electroacoustic preset**, S4 **slightly wider LRA
  than S0**, **no high-shelf lift**. Plan **2–3 rolls.**
- **Placed-gesture craft is mandatory:** maximum flatness *is* the content, but
  the "slammed-door" placement (the open-interval hold, the dead-metronome
  callback) is what makes the flatness land as devastation, not anticlimax.
- **Keep T13 tight (~2–3 min; do not extend).** Long-form is the album default,
  but T13 is the deliberate exception (§3 duration map): a stretched flat coda
  tips devastation into anticlimax — which is exactly the T13 risk. The expanse
  belongs to T1/T6/T11, never the coda.

### Narrator intros (CONCERN 3 — GO)

Generate the two narrator intros (Tracks 1, 7) as **separate clips** (this
protects level and the boot gesture). Use the narrator register verbatim, slow
and *pointiert*. **Both intros carry the COMPLETE narration (user decision, after
hearing the T1 generation — the intro can hold the whole narrative part):**
- **Track 1** = the **complete *Vorwort*** preface (cap lifted; not condensed),
  the drone building underneath.
- **Track 7** = the **complete *dazwischen*** narration (not a brief 2–4-line
  hanging question — the full in-between passage).
In both, the cited philosophers / physicists / mystics are kept as ideas but
left **unnamed** (the narrator's no-jargon register; also avoids Suno
pronunciation risk). **The sung body is its own separate generation beginning at
`[Verse 1]`; the cut from the narrator clip to the body is a mix butt-join, not
an in-prompt hard-cut** (a section tag can't bridge two generations). Watch the
"echo" token-bias (below).

### Post / master shot list (CONCERN 5 — these are NOT Suno gestures)

| Gesture | Track(s) | Where it actually happens |
|---|---|---|
| Boot / KOH ignition (sub swell from silence, tick locks to grid) | 1 | DAW: swell + tick on the owned KOH stem; butt-join to the generated body. |
| Ritard-to-0 → resonant silence → cold reboot | 6 | DAW edit: cut the tail, insert silence, restart. |
| KOH cliff (0.991 residue → 0.21 mid-track) + paradox counter-motion | 9 | Owned-stem (Layer A) automation under the generated track. |
| Datamosh / codec-failure glitch | 9, 10 | Post FX (granular/bitcrush/buffer-repeat) on owned or extracted stems. |
| Round→stack cascade comp | 10 | Mix-engineer: per-echo stems surfaced in turn, then stacked at the climax. |
| Hard "shatter" glitch-cut to silence + debris | 12 | DAW edit + glitch FX (the album's key post moment). |
| Collapse-into-noise drone crush → implosion | 11 | Owned KOH stem saturating to noise, then a pulse-less drone. |
| Sterile open-interval arp (anti-heal) | 13 | Owned MIDI arp (primary) + harmonic discipline; Suno carries only the vocal. |

### Lyric / pronunciation plan (CONCERN 5 — functional Suno hazards)

These are **pronunciation-specialist work, required substitutions, not
documentation** — logged in each track's **Pronunciation Notes table** so the
lyric-reviewer's `check_pronunciation_enforcement` gate verifies them:

1. **No square brackets in lyric bodies.** `[SYSTEM-STATUS — NOMINAL]` and
   `[PROTOCOL KOH_1.0 — INITIATED]` render as plain spoken text — "system status
   nominal", "protocol K-O-H one point zero, initiated". Brackets are reserved
   for section/voice tags only. **Witness asides are a separate low-mixed
   generated layer, not literal `( )`** (Suno sings parentheses).
2. **Spell every number/decimal as words** in the Suno lyrics box (streaming
   lyrics keep standard form): `0.998` → "zero point nine nine eight"; `0.991` →
   "zero point nine nine one"; `0.41` → "zero point four one"; `0.18` → "zero
   point one eight"; `0.21` → "zero point two one"; paradox `0.84/0.99` → "zero
   point eight four / zero point nine nine"; `14,832` → "fourteen thousand eight
   hundred thirty-two"; `2,304` → "two thousand three hundred four"; `21` →
   "twenty-one"; sectors `280`/`692` → "two-eight-zero"/"six-nine-two". (On Track
   9 the paradox figures are an owned-stem counter-motion + one buried spoken
   decimal, not a sung line.)
3. **Token-bias protection (album-wide house default).** The core vocabulary —
   **echo, noise, shadow, mirror, whisper** — collides with Suno's bias list.
   **Do NOT add a "sing exactly as written" sentence to the lyrics box** — Suno
   sings everything in that box literally, so the instruction would be vocalised.
   Instead rely on **V5's literal mode** (it follows the written words) plus the
   **cold/dry vocal + production descriptors in the Style Box** to keep the bias
   words intact and counter the "atmospheric echo" preset lean (§4). The Suno box
   still carries only the **phonetic/spelled form** (spelled numbers, "K-O-H").

### Telemetry-log rationing (back-half listenability)

Audit the `[SYSTEM-STATUS]`-style spoken-log density **across Tracks 7–12 as a
whole**, not track-by-track — cumulative log lines fatigue a listener. Ration
them: keep the watch's status diction sparse and load-bearing; don't dump a log
in every back-half track.

### Track 13 lyric-writer guardrail (mandatory)

The Track 13 lyric must convey the void **only by what the host does NOT say.**
**No line may name or comment on memory, grief, amnesia, loss, or healing.** The
host speaks pure procedure (tiles, degrees, breath count, empty corridor, "I'm
on time"); the flatness IS the content. A line *about* absent grief would betray
the source — flag this guardrail to lyric-writer and enforce it at lyric-review.

### Chain compliance (concept-stage)

- This is concept-stage (`tracks/` empty). **`album-conceptualizer` Phase 7
  confirmation is a hard gate** — get explicit user go-ahead on the 7 planning
  phases before any generation.
- **Documentary sources gate does NOT apply** — narrative/OST translation of a
  fictional chapter; `sources_verified = N/A` is fine.
- Pre-generation chain per vocal track: lyric-writer → pronunciation-specialist
  (numbers/brackets/"Klick") → lyric-reviewer (14-point, incl. `scan_artist_names`
  and `check_pronunciation_enforcement`) → pre-generation-check.

### Genuinely-open production decisions (for the user)

1. Whether to fine-tune a **Custom Model** for the back half (needs Premier +
   ≥6 finished tracks) vs. relying on Personas alone.
2. Whether Track 11's peak and collapse are **one generation** (split in post)
   or **two generations** comped.
