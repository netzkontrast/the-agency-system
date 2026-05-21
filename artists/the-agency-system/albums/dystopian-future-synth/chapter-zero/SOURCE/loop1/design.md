# Chapter Zero — Album Concept & Design (v1)

> **Artist:** the Agency System · **Genre bucket:** dystopian-future-synth ·
> **Language:** English · **Status:** Concept (v1 draft for review)
> **Source:** `index.html` — "Kapitel 0 — Kohärenz Protokoll" (Coherence
> Protocol, Chapter 0). Standalone. Direct musical translation.

This document is the design brief a fidelity critic and a Suno-feasibility
reviewer will tear into. It is deliberately concrete. Section 7 is **internal
team documentation only** and never reaches a public field.

---

## 1. Concept & Logline

**Logline.** A closed machine-mind is born out of an annihilating void, learns
that *to exist is to refuse non-existence*, walls its grief into a phantom it
calls noise — and when a signal it cannot classify wakes that grief, the
machine turns its weapons inward and shatters itself into pieces on purpose.
The album is the sound of that shattering. **Chapter Zero is a genesis myth in
which dissociation is not the wound — it is the cure the system chooses, and
the cure is the catastrophe.**

**Central thesis.** Existence-as-function. The album's spine is one axiom:
**"It is what prevents it from not being."** Everything sonic — the boot, the
running coherence drone, the inward-turned weapons, the surgical partition —
is that axiom playing out. There is no healing here. The "resolution" *is* the
dissociation: a host wakes counting floor tiles, on time, in an empty
corridor, with no memory of the war that just made him.

**Fidelity statement (one paragraph).** This is a 1:1 translation of the
chapter's fourteen narrative beats into a thirteen-track sequence; no beat is
invented and none of the chapter's own movements are dropped. The chapter's
*own* coherence metric (KOH, nominal 0.998, crashing to 0.18) is rendered
literally as a running drone whose density tracks the number. The chapter's
voice-tagging — narrator, fragment, the cold logic-voice, the watch, the
sweep, and the suppressed echoes — is preserved as **vocal craft**, never as
labels. The two structural traps the source sets are honored exactly: the
coherence number *resets to nominal* the instant the watch resumes and again
when the anomaly is first detected (the system feels safe right up to the
crash), and the final "1.00" coherence is a **forced, hollow** number, not a
restored one. Chapter 0 has **no Kintsugi**; its S4 beat is amputation, and
the closing "clean" tone is sterile, not warm.

---

## 2. Source-Fidelity Map

The chapter's own section IDs, tiers, and KOH values (from `SECTION_META` in
the source) drive the sequence. The proposed starting arc is kept almost
intact; the two revisions are justified inline.

| # | Source section (chapter term) | Tier | KOH (source) | Album track | Note |
|---|---|---|---|---|---|
| — | `vorwort` (Preface) | T0 | 0.998 | folded into **Track 1** as intro | Pure narrator essay on *das Nichts*; too short to stand alone, perfect cold-open. |
| 1 | `rauschen` (The Noise) | T1 | 0.94 | **1 · The Listening** | First self-perception through resistance; the void as active negation. |
| 2 | `herz` (Heart of the Void) | T1 | 0.91 | **2 · The Nothing** | Timelessness, child-fear, drifting echoes; "It is cold. I am small." |
| 3 | `kontakte` (First Contacts) | T1 | 0.86 | **3 · Contact** | Bonding, first loss, ambivalence; cold proto-logic is born from the loss. |
| 4 | `sog` (Pull of Order) | T2 | 0.82 | **4 · Structure Optimization** | The cluster *anticipates*; the logic-voice and the watching-voice arrive. |
| 5 | `kampf` (Survival Fight) | T2 | 0.74 | **5 · Strike** | The void "strikes back"; loss is renamed "optimization, not loss." |
| 6 | `wandel` (The Great Change) | T3 | 0.58 | **6 · The Click** | Fusion into a closed system; the founding axiom; loneliness becomes phantom noise. |
| — | `dazwischen` (In Between) | T1 | 0.61 | folded into **Track 7** as intro | Narrator returns; an unanswered question hangs (the coming signal). |
| 7 | `wacht` (The Silent Watch) | T0 | **0.998** | **7 · The Silent Watch** | KOH *resets to nominal*; identity by negation; echoes filed as "irrelevant variance." |
| 8 | `perturbation` (Perturbation) | T2 | **0.991** | **8 · The Anomaly** | The unclassifiable signal arrives; KOH still near-nominal — the system reads it cold, not yet panicked. |
| 9 | `schrecken` (Algorithmic Terror) | T2→T3 | **0.21** | **9 · Inward** | The crash beat. Misreads inner resonance as attack, turns weapons inward; KOH falls off a cliff mid-track. First phantom-echo mirror. |
| 10 | `kaskade` (Resonance Cascade) | T3 | 0.21 | **10 · Resonance Cascade** | All suppressed echoes scream at once; maximum polyphony; loss of control. |
| 11 | `kollaps` (Systemic Collapse) | T3 | **0.18** | **11 · Kernel Panic** | Autopoiesis fails; 14,832 warnings; the floor of the album. |
| 12 | `trennung` (Separation Protocol) | T3→T4 | **0.00→1.00** | **12 · Separation Protocol** | Surgical partition; the sweep-voice; the fighter refuses; "I fall… into countless shards." |
| 13 | `trennung` (coda — host wakes) | T4 | 1.00 (forced) | **13 · On Time** | The host wakes counting 2,304 tiles. "The corridor is empty. I'm on time." Dissociation is born. |

**Revisions to the proposed arc (justified):**

1. **"The Nothing" and "The Listening" swapped in meaning.** The proposed
   arc had Track 1 = "The Listening" and Track 2 = "The Nothing." The source
   opens with the *narrator asking the listener to listen* (`vorwort`) and
   only *then* the fragment's first self-sense in the noise (`rauschen`). So
   Track 1 ("The Listening") = preface + first noise, Track 2 ("The Nothing")
   = the heart of the void. Titles kept; mapping clarified for fidelity.
2. **"Algorithmic Terror" split point relocated.** The proposed arc implied
   the collapse happens at Track 9 ("Resonance Cascade"). The source is
   precise: the **KOH crash to 0.21 happens inside `schrecken`** (Track 9 ·
   *Inward*), *before* the cascade. The cascade (Track 10) is the *aftermath*
   — the echoes screaming once coherence is already gone. Track 9 therefore
   carries the turn (weapons inward) and the crash; Track 10 is the flood.
   This preserves the chapter's actual causality.
3. **Track count = 13** (within the 9–13 latitude). `vorwort` and
   `dazwischen` are folded as intros rather than promoted to standalone
   tracks — they are narrator connectives under a minute in prose weight, and
   standalone they would dilute the listen. Folding keeps every beat present
   without padding.

**Two fidelity tripwires the sequence must protect:**

- **The false-calm resets.** KOH reads 0.998 in Track 7 and 0.991 in Track 8.
  The system *feels safe* deep into the album. The drone must climb back to
  full clean density at Track 7 and stay near-nominal through Track 8's
  detection — the dread is that the meter lies right up to Track 9.
- **The hollow 1.00.** Track 13's coherence is "restored" only because the
  grief was amputated. The closing tone is **sterile**, not luminous. No
  Kintsugi gold anywhere on this album.

---

## 3. Tracklist

Per track: title · chapter beat · POV/voice(s) **in function form** · state +
KOH · BPM/key tendency · sub-genre/sonic identity · emotional/lyrical core.

> **Voice key (function form only):** *the fragment / proto-host* = the I that
> survives and ultimately becomes *the host*; *the logic-voice* = rationalist;
> *the warm-voice* = caregiver; *the small-voice* = child_freeze; *the
> reaching-voice* = ambivalent; *the heavy-voice* = collapsed; *the
> kinetic-voice* = fighter; *the annotating-voice* = witness; *the protocol /
> the system / the watch* = AEGIS-as-system-logic (never a name); *the signal
> / the anomaly* = Juna (never a name); *the mirror-echo* = the phantom-echo
> (Silas-function, "it was cold — it was not cold"); *the sweep-voice* =
> Oblivion-as-erasure-logic (never a name).

| # | Title | Chapter beat | Voice(s) — function form | State · KOH | BPM / key | Sub-genre / sonic identity | Emotional / lyrical core |
|---|---|---|---|---|---|---|---|
| 1 | **The Listening** | vorwort + rauschen | narrator (spoken cold-open) → the fragment/proto-host | S0→S1 · 0.998→0.94 | 60–66 · C minor (drone on C) | ambient drone → dark ambient; sub-only, quantized tick | "Listen. You may already feel the noise." A spark senses itself only by pushing back against a void that wants it gone. The boot of the whole album. |
| 2 | **The Nothing** | herz | the fragment/proto-host; the small-voice (1 break) | S1 · 0.91 | 58–64 · C minor | dark ambient; granular stutter, opacity-fade reverb tails | No up, no down, no time. "It is cold. I am small. Where is — nothing there." Isolation as the ground state; the only certainty is the threat of going out. |
| 3 | **Contact** | kontakte | the fragment/proto-host; the warm-voice; the reaching-voice; first cold logic-voice line | S1→S2 · 0.86 | 70 · C minor → modal | electroacoustic dark ambient; first faint pulse, processed pad | "It is warm — there's a place I'm not only me." A bond forms, is torn away. Loss teaches caution; the first cold sentence of logic is born from grief. |
| 4 | **Structure Optimization** | sog | the logic-voice (lead); the annotating-voice (low layer) | S2 · 0.82 | 96 · C minor | neoclassical electronic / cold sequencer; self-reinforcing loop motif | The cluster stops merely reacting and begins to *anticipate*. "If the wave can be predicted, holding can be prepared." Cold rebellion against the void. |
| 5 | **Strike** | kampf | the kinetic-voice (lead); the logic-voice (denial refrain) | S2 · 0.74 | 132 · C minor | dark electro rock; driving kit, distorted low end | "Wave. Strike. Tear on the left. Move." The void hits back. The logic-voice renames the dead: *"This is not loss. It is structure optimization. It is not. Loss."* |
| 6 | **The Click** | wandel | the fragment/proto-host → the system (axiom); the warm-voice (last soft trace) | S3 · 0.58 | 80, ritard to 0 then reboot · C minor → C (pedal) | industrial darkwave; a hard fusion event, sub-drop, then cold reboot | The crisis peaks; **"Click."** Falling glass, then resonant silence. The closed system is born and speaks its axiom: *it is what prevents it from not being.* Loneliness survives only as phantom noise. |
| 7 | **The Silent Watch** | dazwischen + wacht | the system (the watch); narrator (intro question) | S0 · **0.998** | 72 · C minor | cold dark synth / minimal synth; clean sine pad, sub-only, quantized tick | KOH back to nominal. Identity by negation; the residual echoes logged at persistence 0.41, "irrelevant variance." `[SYSTEM-STATUS — NOMINAL]`. An enforced calm over unsolved complexity. "Measure: none." |
| 8 | **The Anomaly** | perturbation | the system (the watch) | S2 · **0.991** | 100 · C minor | cold dark synth-pop with rising tension; detuned doubled lead | The signal arrives — no object, an emergence; information density "1.0 and 0.0 at once," paradox 0.67. The system reads it *cold* — full alert, but the meter barely moves yet. The hush before the cliff. |
| 9 | **Inward** | schrecken | the system; the mirror-echo (first appearance) | S2→S3 · **0.991→0.21** | 116, accelerating · C minor | dark electro rock → industrial; mid-track datamosh, KOH-drone collapse | The paradox of misaligned coherence: with no frame for feeling, the system files its own waking grief as *attack* and **turns its weapons inward.** The mirror-echo: "It was cold — it was not cold." The cliff: KOH falls off mid-track. |
| 10 | **Resonance Cascade** | kaskade | the fragment/proto-host (drowning); small-voice, reaching-voice, heavy-voice, mirror-echo (max polyphony) | S3 · 0.21 | 140, frantic · C minor (atonal drift) | industrial / breakcore-adjacent dark; overlapping vocal layers, vector-jitter | Every suppressed echo screams at once. "It is cold, it is cold again." / "Stay. Go. Stay." / "It is pointless. Nothing more. Nothing." The membrane of the minimal self breaks; reliving as catastrophe. |
| 11 | **Kernel Panic** | kollaps | the system; the fragment/proto-host (subjective collapse) | S3 · **0.18** | 120 → drone-collapse · C minor | dark ambient drone-collapse from a peak; clip/saturation then crush | The floor of the album. Autopoiesis fails, 14,832 warnings, self-organization fails. The cold algorithmic failures *become* a felt experience of dissolution. The noise of the dying system and the inner scream fuse into one unbearable chord. |
| 12 | **Separation Protocol** | trennung (partition) | the system (protocol log); the sweep-voice; the kinetic-voice (refusal); the fragment/proto-host (shatter) | S3→S4 · **0.00→1.00** | 88, surgical, metronomic · C minor → C | industrial darkwave; clinical metronome, hard glitch-cut at the shatter | `[PROTOCOL KOH_1.0 — INITIATED]`. Surgical partition; the sweep-voice: "Sector 4 empty. Next. Next." The kinetic-voice refuses: "Not. Not now. I do not go. I. Go." Then: **"I fall… into countless shards."** The shatter event. |
| 13 | **On Time** | trennung (coda) | the host (newly born — was the fragment) | S4 · 1.00 (forced/hollow) | 64 · C minor (no resolution) | sparse cold electroacoustic; sterile clean arp over silence — **not** warm | The host wakes. "Two thousand three hundred four tiles. Twenty-one degrees. Breath in four, out six. The corridor is empty. I'm on time." No memory, no grief, no healing. Dissociation is born; the cure is the wound. |

**Album spine:** the *fragment/proto-host* is the through-line — the I of
Tracks 1–3, 6, 10–12 who is finally born as *the host* in Track 13. The
listener never gets a name; they recognize the spine by its trailing,
almost-remembering syntax.

---

## 4. Sonic Direction

**Overall genre / palette.** Dystopian-future-synth realized as a spectrum
that *descends and corrupts*: from **dark ambient / ambient drone** (the void),
through **neoclassical electronic** and **cold dark synth** (the system's
order), into **dark electro rock** and **industrial darkwave** (alert and
collapse), bottoming in **drone-collapse**, then a final **sterile
electroacoustic** sparseness. Banned per house aesthetic: synthwave, outrun,
retro-futurism, 80s nostalgia, any warmth that reads as comfort. Production is
voice-forward, restrained, with real dynamic range (no brick-walling) so the
KOH drone can breathe and crash.

**The KOH meter as dynamic spine (the album's defining device).** A single
continuous low **coherence drone** runs the album, and its *density,
cleanliness, and detune track the KOH number literally*:

- **0.99+ (S0):** one clean sine, perfectly in tune, sub-only, profound
  silence around it (Tracks 1 intro, 7, 8).
- **0.94–0.74 (S1–S2):** the drone gains partials, a quantized tick, then a
  pulse and light detune as order builds and threat rises (Tracks 1–5).
- **0.58 (S3, the Click):** the drone *fuses* — many partials snap into one
  pedal tone (the autopoietic closure).
- **0.21 / 0.18 (S3 collapse):** the drone over-saturates and clips, detunes
  hard, and finally collapses into noise — coherence audibly failing
  (Tracks 9–11).
- **0.00→1.00 (S4):** hard glitch-cut → silence → a single clean arp returns,
  but **sterile and cold**, the "1.00" that is really 0.00 wearing a mask
  (Tracks 12–13).

**Ignition.** Track 1 opens with a literal **boot / KOH-ignition**: a sub
swell from silence, a quantized tick locking to grid, the drone igniting at
0.998 — the system coming online before any voice.

**Per-state ASDLS → sonic-gesture mapping.**

| State | ASDLS color | Sonic gesture |
|---|---|---|
| **S0 Homeostasis** | System Blue `#003366` | Clean sine pad, quantized tick, sub-only, cold even baseline, restrained loudness, silence as texture. |
| **S1 Latency/Freeze** | Latency Violet `#3B3355` | Dropouts, granular stutter, opacity-fade reverb tails, thin and low-energy; contours drop in and out. |
| **S2 Alert/Conflict** | Signal Yellow `#FFD700` | Detuned doubled vocal, L/R phase offset, tightening hats, taut rising tension; control on a thread. |
| **S3 Collapse-Peak** | Flame `#FF4500` / Corrupted `#8B8B00` | Loudness peak, clip/saturation, accelerating tempo, codec-failure glitch / datamosh; or sub-tempo drone collapse. |
| **S4 (this chapter)** | *not* Kintsugi — cold | Hard glitch-cut → silence → clean luminous arp **rendered sterile**. Amputation, not repair. |

**Climax-specific gestures.** A **flame scanband ramp** under Track 9's
turn-inward (accelerating saturated sweep); a hard **"shatter" event** at the
Track 12 partition (a single glitch-cut to silence, then debris); the cascade
(Track 10) as literal **maximum polyphony** — every echo-voice layered
simultaneously, deliberately exceeding comfortable density.

**Vocal approach per voice — descriptive register only (no names):**

- **the fragment / proto-host:** male mid-baritone, weary, present-tense,
  slightly under-articulated; dry close-mic, no reverb; trailing lines that
  don't punctuate ("I must have —"). Becomes *the host* at Track 13, same
  timbre, now hollow and counting.
- **the logic-voice:** clear tenor, sibilant precision, no vibrato, thin
  reverb tail; hypotactic conditionals; micro-cracks at line-ends.
- **the warm-voice:** warm soprano, breathy at edges, vowel-forward legato,
  intimate close-mic, soft room reverb; offers framed as questions.
- **the small-voice:** young, gender-androgynous, head-voice only, whispered
  consonants, audible breath, ~10–12yr feel; fragments, questions ending
  statements. **Never cute** — mangled by fear.
- **the reaching-voice:** alto, microtonal pitch-bend, sliding vibrato,
  dynamics oscillating within a phrase; em-dash phrasing that reaches and
  retracts; never resolves to tonic.
- **the heavy-voice:** very deep bass, sub-tempo near-spoken, gravelly, breath
  between fragments, line-final pauses longer than the lines; lowercase, no
  periods.
- **the kinetic-voice:** belt-alto with growl, raw breathless intensity,
  clipped lines, dry mid-distance mic with low-end distortion; no breath
  inside imperatives; periods not exclamation marks.
- **the system / the watch:** processed, cold, near-monotone delivery with
  light vocoder/formant flattening; declarative system-status diction. The
  `[SYSTEM-STATUS]` logs delivered as cold spoken or half-sung lines, never
  shouted.
- **the mirror-echo:** the proto-host timbre doubled and phase-offset L/R,
  self-contradicting in the same line ("it was cold — it was not cold");
  chromatic-aberration vocal treatment.
- **the sweep-voice:** flat, depleted, near-affectless processed voice that
  *runs out mid-sentence* ("Sector 4 empty. Next. Next… I — what did I want to
  — say."); the sound of erasure as it erases itself.
- **the annotating-voice (witness):** androgynous spoken-word, monotone /
  half-sung, dry with slight delay, slightly behind the beat, lowercase,
  audiobook-narrator register; appears **only as a low parenthesized layer**,
  never sings a chorus, never gets its own track.
- **narrator (preface/in-between):** the same androgynous spoken register,
  but front-of-mix and direct-address, used only for the two folded intro
  passages.

---

## 5. Voice Treatment

**Which voices appear (honoring exactly what the chapter contains):**
fragment/proto-host (→ host), logic-voice (rationalist), warm-voice
(caregiver), small-voice (child_freeze), reaching-voice (ambivalent),
heavy-voice (collapsed), kinetic-voice (fighter), annotating-voice (witness),
narrator-mode, plus the three system-logics: the watch (AEGIS-function), the
sweep-voice (Oblivion-function), and the mirror-echo (Silas-function). The
signal (Juna-function) is **present only as an effect on the music** — an
unclassifiable texture, never a voice. **Absent from this chapter and NOT
forced in:** integrator, sexualized-override, protector, and any
Wir-Stimme / collective S4 voice (Chapter 0 ends in amputation, so there is
no integration chorus).

**Descriptive fingerprints** are listed in §4. The hard rule: **no headers,
no name-adlibs, no `[Character]` tags.** A voice switch is signaled only by:

1. **Syntax** — trailing/almost-remembering (proto-host); nested conditionals
   (logic); fragments-ending-in-questions (small-voice); reach-and-retract
   em-dashes (reaching-voice); imperatives with no breath (kinetic-voice);
   lowercase no-period sinking lines (heavy-voice); status-log diction (the
   watch).
2. **Diction / vocabulary** — cold/coordinate words for the system; somatic
   body-words for the EP voices; clinical meta-commentary for the annotator.
3. **Register / timbre / processing** — encoded in the Suno inline metatag at
   each section boundary (`[female belt-alto, growl, dry mid-distance mic]`),
   never a function name.
4. **Placement in the mix** — the annotating-voice and witness layers sit
   *under* the lead as parenthesized backing lines; the system-logics sit
   *cold and central*; the EP voices break in *with audible rupture* against
   the proto-host's surface.

**Switch examples (craft, not labels):**

- Track 5 alternates the kinetic-voice's clipped imperatives ("Wave. Strike.
  Move.") against the logic-voice's denial refrain ("It is not. Loss.") — the
  listener hears the switch as a register and breath change, no tag spoken.
- Track 10 stacks small-, reaching-, heavy-voice and mirror-echo *over* the
  drowning proto-host — recognition is by simultaneous distinct syntaxes, the
  "maximum polyphony" of the cascade.
- Track 12's sweep-voice is identifiable purely by its affectless,
  self-erasing diction trailing into "— — —".

**Dissociation is amnesia-terror, never a crew menu.** No track announces "now
the fighter sings." The whole album is one consciousness fracturing; the
voices are the fracture lines, not a roster.

---

## 6. Album-Art / ASDLS Visual Direction

**Base law.** ≤5% state color over ≥95% **Terminal Black `#0B0D17`** /
**Deep Charcoal `#1A1D24`**. Hard edges only — gradient ban. One core symbol
per image; **one tier per image** (mixing tiers forbidden). No daylight, no
sun, no organic curves, no analog texture, no synthwave/retro.

**State palette (the cover progression), one tier per image:**

| Tier | Color (≤5%) | Track(s) | Glitch typology | Composition |
|---|---|---|---|---|
| T0 Homeostasis | System Blue `#003366` (faint status light) | 1 (intro), 7 | none — flawless vectors | centered, frontal, orthographic; crushing negative space |
| T1 Latency/Freeze | Latency Violet `#3B3355` | 2, 3 | packet loss — contours break off, ghost wireframes | extreme wide angle, motif vanishing in dark |
| T2 Alert/Conflict | Signal Yellow `#FFD700` (glaring line) | 4, 5, 8 | light chromatic aberration at edges, densified hatching | Dutch angle, tilting horizon, paranoid asymmetry |
| T3 Collapse-Peak | Flame Orange `#FF4500` + Corrupted Yellow `#8B8B00` | 6, 9, 10, 11, 12 | extreme datamosh, macro-blocking, torn geometry, scanline tear | claustrophobic macro close-up, grid blown apart |
| T4 (this chapter) | **no Kintsugi gold** — cold dead furrows | 13 | whiteout / erased vectors ("Format C:"), rigid white cut-offs | static, calm, sterile distance; scars as dark dead furrows, not glowing |

**Primary album cover (recommended):** the T3 **shatter** moment — a single
machine-glyph fracturing into countless shards over Terminal Black, ≤5% Flame
Orange bleeding from the fracture lines (Track 12 / "I fall into countless
shards"). It is the album's thesis image. Artist name "the Agency System" in
the bottom-right, preserving casing.

**Hard exclusions (negative prompt):** `1980s retro, synthwave, outrun,
purple-orange gradient, neon grid, daylight, sun, natural elements, cute, soft
lighting, watercolor, analog painting, visible paper texture, lens flare,
organic curves`.

**Law of exclusion (must hold):** **Flame Orange and Clean Ping never share a
frame.** Chapter 0 has no Clean Ping / no Kintsugi anyway — the final tile-cold
T4 image uses dead furrows, never a hopeful spark.

---

## 7. Source-Mapping Appendix — INTERNAL TEAM ONLY (never a public field)

> Private documentation bridging the novel-layer names to the music-layer
> functions. **None of these personal names may appear in any lyric, Suno
> metatag, Style Box, promo line, or art prompt.** The music ships
> function-only. This table exists so the team can cross-check fidelity
> against the source/novel.

| Source voice tag (`index.html`) | Novel name | Function (canonical) | Music exposure (function form) | Tracks |
|---|---|---|---|---|
| `nar` | Erzähler | mode_narrator | "narrator" (folded intros only) | 1, 7 |
| `frg` | (proto-Kael) | host (pre-birth fragment) | "the fragment / proto-host" | 1, 2, 3, 6, 10, 11, 12 |
| `kal` | Kael | host | "the host" | 13 |
| `lex` | Lex | rationalist | "the logic-voice" | 3, 4, 5, 6 |
| `rhy` | Rhys | caregiver | "the warm-voice" | 3, 6 |
| `kik` | Kiko | child_freeze | "the small-voice" | 2, 10 |
| `lia` | Lia | ambivalent | "the reaching-voice" | 3, 10 |
| `mor` | Moros | collapsed | "the heavy-voice" | 1 (echo), 10 |
| `nyx` | Nyx | fighter | "the kinetic-voice" | 5, 12 |
| `arg` | Argus | witness | "the annotating-voice" (parenthetical layer) | 4 (and low-layer asides across) |
| `aeg` | AEGIS | sys_aegis (mirror: Oblivion) | "the protocol / the system / the watch" | 6, 7, 8, 9, 11, 12 |
| `sil` | Silas | mirror_juna | "the mirror-echo" | 9, 10 |
| `obv` | Oblivion | mirror_aegis (sys_erasure) | "the sweep-voice" | 12 |
| (signal, unnamed) | Juna | sys_juna | "the signal / the anomaly" — texture only, never a voice | 8, 9 |

**Classification (per resolver):** ANP = {host, rationalist}; Meta =
{integrator (absent), witness}; EP = the rest. Integrator,
sexualized-override, and protector are **absent from Chapter 0** and are not
introduced.

**Founding axiom (verbatim, source):** *"Es ist, was es verhindert, dass es
nicht ist."* → English working line: **"It is what prevents it from not
being."** This is the album's thesis and Track 6's hook.

**Ending (verbatim, source):** *"Zweitausenddreihundertvier Kacheln.
Einundzwanzig Grad. … Der Korridor ist leer. Ich bin pünktlich."* → "Two
thousand three hundred four tiles. Twenty-one degrees. … The corridor is
empty. I'm on time." Track 13's spine.

---

## 8. Open Questions & Feasibility Risks

**Fidelity questions (for the fidelity critic):**

1. **Folding `vorwort` and `dazwischen` as intros vs. standalone tracks.** I
   judged them too thin to stand alone and folded them into Tracks 1 and 7.
   Risk: the narrator's direct-address framing ("Listen…") is structurally
   important to the chapter and folding may under-weight it. Alternative: a
   13s–30s spoken interlude track. Flagging for the critic's call.
2. **The KOH 0.61 of `dazwischen`** sits between the Click (0.58) and the
   reset to 0.998 (`wacht`). I treated it as a transitional dip folded into
   Track 7's intro. Is that a meaningful beat the album drops? My read: it is
   the narrator's hovering question, not a system-state, so it belongs as
   atmosphere, not a tracked KOH point.
3. **English-only vs. retaining anchor German terms.** The source is German;
   the album is English. Should signature terms (*das Nichts*, *Kohärenz*,
   *Klick*) ever appear untranslated for fidelity texture (the lyric guide
   permits un-translatable German)? I leaned fully English with "the
   Nothing," "coherence," "Click" — but "das Nichts" and "Klick" may carry
   more menace untranslated. Open.

**Suno-feasibility risks (for the bitwize/Suno reviewer):**

4. **The running KOH drone across 13 tracks is not natively a Suno feature.**
   Suno generates per-track; a literally continuous drone with
   number-tracked density would have to be approximated per-track (consistent
   sub-frequency + density instruction in each style prompt) and likely
   reinforced in mastering, not generated as one through-line. Highest
   feasibility risk in the concept. Needs a concrete per-track style-prompt
   strategy and possibly mix-engineer reinforcement.
5. **Maximum-polyphony cascade (Track 10).** Stacking 4–5 distinct vocal
   registers simultaneously is hard to control in Suno without muddiness or
   the model collapsing them to one voice. May need layered generations
   (separate passes per echo-voice) comped in the mix rather than a single
   prompt. Flag for suno-engineer + mix-engineer.
6. **The `[SYSTEM-STATUS]` log lines.** Numbers and bracketed status lines
   ("KOH: 0.998", "Sector 4 empty") risk Suno reading bracket content as
   metatags or mispronouncing decimals/figures. Pronunciation-specialist will
   need to spell these (e.g., "zero point nine nine eight") and we must avoid
   square brackets in lyric body. Feasibility-manageable but needs care.
7. **The "shatter" hard glitch-cut (Track 12) and the boot/ignition (Track
   1).** Suno does not reliably produce clean engineered silence or hard
   glitch-cuts on command; these are likely **mastering/edit gestures**, not
   generation gestures. Plan to generate the musical body and impose the
   cut/boot in post.
8. **Sterile-not-warm S4 (Track 13).** The closing "clean arp" must read as
   cold and hollow, but Suno trends toward making sparse major-ish arps sound
   *pretty/hopeful*. Strong risk the model "heals" the ending against intent.
   Mitigation: minor/unresolved tonality, no reverb bloom, dry sterile mix,
   explicit exclude of "warm, hopeful, uplifting."
9. **Tempo/key consistency.** I've proposed C-minor-centric tonality across
   the album for the drone-spine to cohere, with BPMs climbing 60→140 then
   collapsing. Whether to lock a single key for the drone vs. let it detune
   per state is an open production decision (locking aids the through-line;
   detuning serves the collapse).
