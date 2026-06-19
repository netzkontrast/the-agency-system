# Chapter Zero — Suno-Feasibility Critique

**Reviewer role:** bitwize-music + Suno V5/V5.5 feasibility.
**Under review:** `artists/the-agency-system/albums/dystopian-future-synth/chapter-zero/DESIGN.md`
**Verdict scale:** GO / NEEDS-CHANGE / WON'T-WORK
**Grounding:** suno-engineer SKILL, lyric-writer/reviewer SKILLs, mastering-engineer SKILL + `mastering-presets.yaml`, `suno-preferences.md`, `reference/suno/v5-best-practices.md`.

> Bottom line up front: the concept is **largely feasible, but only if you stop
> treating Suno as the through-line engine and treat it as a per-track stem
> generator that you then assemble.** The KOH drone, the boot, the shatter, and
> the sterile ending are **post-production gestures**, not generation gestures.
> The author already half-knows this (Section 8 risks 4–9 are accurate). My job
> is to convert "open risk" into "concrete plan." Two items are genuinely at the
> edge of the platform (Track 10 max-polyphony, the literal continuous drone);
> everything else is GO with a defined recipe.

---

## CONCERN 1 — The continuous KOH drone through-line (13 separate generations)

**Verdict: NEEDS-CHANGE (feasible as an *illusion*, never as a literal single drone).**

Suno generates per-track. There is no project-level continuous-bus, no shared
oscillator, no automation that survives across 13 prompts. A "number-tracked
dynamic spine" cannot be *generated*. It must be **manufactured** by three
independent layers working together. The design already gestures at this
(risk 4) but doesn't commit to a recipe. Here is the recipe.

### Layer A — a real, separate drone stem you own (not Suno-generated per track)

Do **not** rely on Suno re-rolling a "consistent sub-frequency" 13 times — it
won't be the same pitch, the same partial structure, or the same level. Instead:

1. Generate (or synth in a DAW) **one** sustained C drone bed at 0.998 "clean"
   state — a single sine on **C** (the design's chosen tonal center), sub-only.
   This is your *master KOH oscillator*. Keep the raw file.
2. Produce the KOH automation as **edits to that one file**: add partials /
   detune / saturation / clip / collapse to noise per the design's own density
   ladder (§4). That ladder is good and literal — keep it. Render 13 KOH-bed
   segments (or fewer, reused) at the densities each track needs.
3. In the mix-engineer stage, **lay the matching KOH segment under each Suno
   track** at a low, constant sub level. This is the only way "0.998 in Track 7,
   0.991 in Track 8, cliff to 0.21 mid-Track 9" is *literally* true rather than
   a vibe. Suno cannot track a decimal; your DAW automation lane can.

This makes the KOH spine a **mix asset**, not a generation asset. It is the
single most important architectural correction in this review.

### Layer B — style-box consistency anchors so Suno's *own* beds don't fight the spine

Every track's Style Box must carry the **same 2–3 anchor descriptors** so the
Suno-generated material sits over the owned drone without clashing. Per
`suno-preferences.md` "Always include: voice forward, restrained, dark
production, contemporary, dynamic range" and **max 2 genre tags**. Add a fixed
Chapter-Zero spine anchor to every prompt:

```
... sustained low C drone underpinning, sub-bass continuo, cold, no key change ...
```

Keep it identical, verbatim, across all 13 so the model's harmonic floor lands
near C every time. Combined with Layer A, drift becomes inaudible.

### Layer C — vocal/character continuity = Personas or a Custom Model (the real fix)

The v5-best-practices reference is explicit: **Personas are "the most reliable
way to maintain vocal consistency across an album,"** and **Custom Models are
"best for series/album consistency."** For a 13-track single-consciousness
album this is not optional polish — it is the mechanism:

- **Build a Persona for the fragment/proto-host voice** (male mid-baritone,
  weary, dry close-mic — matches `suno-preferences.md` default baritone). Reuse
  it on Tracks 1, 2, 3, 6, 10, 11, 12, and 13 (where it "becomes the host, same
  timbre, now hollow"). This is exactly what makes Track 13's "same timbre, now
  hollow" land — a Persona *is* the same singer.
- Optionally build a second Persona for **the system / the watch** (cold,
  near-monotone, vocoder/formant-flattened) reused on 6/7/8/9/11/12.
- If you have Premier and ≥6 finished tracks, **fine-tune a Custom Model** on
  them for the back half — it locks harmonic + production aesthetic across the
  remaining generations and lets you shorten every style box.

> Note the reference rule: when using a **Persona/Voice, drop the gender/register
> descriptors from the style box** — the Persona carries them. Don't double-specify.

### Layer D — key/tempo continuity

- **Lock C minor as the global key** (design already proposes this — keep it).
  Put `C minor` in every style box. For the few tracks where the drone should
  *detune* (9–11), do the detune in **Layer A's owned stem**, not by asking Suno
  for a different key — that protects the spine while still serving the collapse.
- BPM climb 60→140→collapse is fine per-track; Suno honors BPM well for
  electronic material. Tempo does **not** need to be continuous — only key and
  the sub-drone do. The accelerando *within* Track 9 ("116, accelerating") is a
  single-track instruction Suno handles acceptably; verify on regen.
- If a generation lands in the wrong key, use **Suno Studio Pitch Transpose
  (±12 semitones, Premier)** to correct without burning a re-roll — cheaper than
  regenerating and preserves phrasing.

### Layer E — mastering ties it together (this is where the spine becomes "one album")

The `mastering-presets.yaml` already encodes a **state-axis → loudness/LRA
bias** that maps perfectly onto KOH. Use it as designed:

- S0 (0.99+, Tracks 1-intro/7/8): sit at preset center, balanced LRA.
- S1 (Track 2): bias `target_lufs` ~1–2 LU lower, LRA higher — "let the silence
  breathe."
- S2 (4/5/8/9): ~1–2 LU louder, LRA lower, faster attack — punch.
- S3 (6/9/10/11): loudest band, most compressed, **never past true_peak −1.0**.
- S4 (12/13): return toward center but *slightly wider LRA than S0* to mark the
  hollow-resolved feeling.

Master the **whole album in one `master_album` pass per genre cluster** so the
KOH bed's level reads consistently track-to-track. Because the album spans
ambient → electroacoustic → industrial → drone, you cannot use one genre
preset; plan **per-track genre overrides** (mastering SKILL Step 1.5 explicitly
supports this — master the main batch, then re-master outliers).

**Mitigation summary:** the spine is real and achievable, but it is **owned-stem
+ fixed style anchor + Persona/Custom-Model + locked C-minor + state-biased
mastering**, assembled in mix. Generated continuity alone = WON'T-WORK. The
assembled illusion = GO. Add this 5-layer recipe to §4 of the design.

---

## CONCERN 2 — The sterile, un-healed ending (Track 13)

**Verdict: NEEDS-CHANGE (achievable but fragile — Suno's strongest "auto-heal" failure mode).**

The author's risk 8 is correct and is the single biggest *aesthetic* threat:
Suno trends toward making sparse arps sound pretty/hopeful, and `suno-preferences.md`
already bans "happy/uplifting/warm-as-comfort." Reliability here is **medium**,
not high — plan to over-roll Track 13 and to fix it in post. Concrete forcing
moves:

### Style-box wording (sterile, hollow, NON-resolving)

Per the V5-literal principle and the `suno-preferences.md` register table
("control/deliberate: low contralto … restrained vibrato held as a weapon" is
the wrong one here — use the host baritone gone hollow):

```
male mid-baritone, flat affect, hollow, depleted, no warmth, counting cadence.
Sparse cold electroacoustic, single detuned arpeggio in C minor, unresolved,
no reverb bloom, dry sterile mix, clinical, dynamic range, sub-only drone under.
```

Keep it ≤7 descriptors (reference: prompt fatigue past 7). "Flat affect,"
"hollow," "depleted," "no warmth," "clinical," "sterile" are the load-bearing
words. Pair with the V5.5 note that *subtle emotion descriptors land more
reliably now* — "resigned/hollow" tracks closer to intent on 5.5 than it did
on 5.

### Tonality control (the real lever)

The "pretty" risk lives in **harmony**, not adjectives. Force it harmonically:

- **Stay minor and refuse the tonic resolution.** Tell Suno `unresolved`,
  `no resolution`, `ends on an open interval, not the tonic` — and write the
  arp so it never lands on C. The design's "C minor (no resolution)" header is
  right; make the *lyric/melodic* line stop on the 2nd or b6, not the root.
- **No major-third lift.** A single major third is what makes Suno "heal" an
  arp. Specify minor; consider `Phrygian` or `Locrian` color in the style box
  for inherent unease (these read as "cold/wrong" to listeners and to the model).

### Exclude Styles (use the budget here — this is a justified exclusion track)

`suno-preferences.md` caps Exclude Styles at 2–4 items. Spend them:

```
no warmth, no major key, no reverb bloom, no uplifting resolution
```

(That's 4 — the max. Don't add more or you dilute it, per the SKILL.)

### Production / post

- **Dry, no reverb tail.** Reverb bloom is what reads as "luminous/hopeful."
  Specify `dry close-mic, no reverb`. If Suno adds a tail anyway, the
  mix-engineer strips it.
- **Mastering:** master Track 13 with the **electroacoustic preset**
  (`target_lufs −16`, `cut_highs 0`, light comp) but per the state-axis note
  give S4 *slightly wider LRA than S0* — the recovered-but-hollow feel. Do NOT
  brighten. No high-shelf lift.
- **The arp itself can be an owned stem.** If Suno keeps "healing," generate the
  arp in a DAW (or Suno Studio MIDI export → transpose to a fixed minor figure),
  and let Suno provide only the hollow vocal over it. This is the
  belt-and-suspenders fallback and I recommend planning for it.

**Mitigation summary:** reliably-achievable is too strong; **achievable with
2–3 rolls + harmonic discipline + the 4-item exclude + a post fallback.** Flag
Track 13 as the album's highest-iteration track. GO once the harmonic refusal
(no major third, no tonic landing) is written into the lyric/melody, not just
the prompt.

---

## CONCERN 3 — Narrator / spoken-word framing

**Verdict: GO (well within Suno's strengths — but keep it sparse and tagged).**

Spoken-word is feasible and good in Suno V5/V5.5. The platform handles
`[Spoken]` inline tags (per `suno-preferences.md` Section-Tag Conventions:
`[Whispered]`, `[Spoken]` are sanctioned) and the V5.5 vocal engine renders
half-sung/monotone delivery convincingly. The design's narrator is **only two
folded intro passages** (Tracks 1 and 7) — that restraint is exactly right.

What works:
- The `suno-preferences.md` register "Spoken-word/narrator (witness):
  androgynous spoken-word, monotone or half-sung, dry, layered with slight
  delay/echo, lowercase delivery, audiobook-narrator register" is a ready-made
  vocal descriptor. Use it verbatim as the section metatag.
- Direct-address ("Listen. You may already feel the noise.") is fine as the
  cold-open of Track 1.
- The annotating/witness layer as **parenthesized backing lines** is correct and
  Suno-native: the reference and `suno-preferences.md` both confirm
  parenthesized lyric lines render as backing/ad-lib layers in V5. Good call.

Where it fights the platform (minor):
- **Don't let the spoken intro eat the song.** Suno sometimes over-weights a
  long spoken opener and under-delivers the sung body, or rushes the rest.
  Keep the spoken passage to ~2–4 lines, then hard-cut to the first sung
  section with a clear `[Verse 1]` tag.
- **Spoken + sung in one generation can drift in level.** The spoken part often
  comes out quieter. Either accept it (audiobook-quiet suits the aesthetic) or
  generate the spoken intro as its **own short clip** and butt-join it to the
  sung body in the mix. For Tracks 1 and 7 specifically, I'd generate the intro
  separately — it also protects the boot/ignition gesture (see Concern 5).
- **"echo" is a Suno token-bias word** (reference Token Biases: Neon, Echo,
  Ghost, Silver, Shadow, Whisper, Crystal, Velvet). The narrator register's
  "slight delay/echo" is fine as a *production* instruction, but watch that the
  model doesn't start inserting the word "echo" into lyrics. Add
  `Do not change any words. Sing exactly as written.` to the top of any track
  whose lyrics mention echoes/noise/shadow conceptually — and this album's
  vocabulary (echo, noise, the mirror-echo) collides with that bias list hard.
  This is a real, recurring risk across the whole tracklist, not just here.

**Mitigation summary:** GO. Generate the two narrator intros as separate short
clips, use the witness/narrator register verbatim, keep direct-address to a few
lines, and add the "sing exactly as written" guard everywhere the lyrics use
bias words (echo/noise/shadow/whisper).

---

## CONCERN 4 — Per-track style boxes, genres, BPMs, registers (track-by-track)

**Overall verdict: GO with per-track NEEDS-CHANGE flags. One track (10) is at the platform edge.**

The genre choices map cleanly onto `suno-preferences.md` genre mappings and
`mastering-presets.yaml` presets — that's a strong sign the album was designed
inside the house vocabulary. The function-only / no-names rule is **correctly
honored throughout** §3–§5 and §7 is explicitly internal-only. Good.

General rules the per-track boxes must follow (from the SKILLs/refs):
- **Vocals FIRST** in every style box (suno-engineer core principle).
- **Max 2 genre tags** (`suno-preferences.md`) / 4–7 total descriptors
  (reference "prompt fatigue").
- **Descriptive vocal metatag only** at each voice-change section —
  `[female belt-alto, growl, dry mid-distance mic]` — **never** `[the fighter]`,
  never a personal name (`suno-preferences.md` + voice-craft). The design states
  this rule correctly; the lyric-writer/reviewer must enforce it per track.

| # | Track | Genre/BPM/register check | Verdict |
|---|---|---|---|
| 1 | The Listening | ambient drone → dark ambient, 60–66, C min, narrator+baritone. Two-genre descent in one track is fine if you tag the shift; boot/ignition is post (see C5). | GO (intro as separate clip) |
| 2 | The Nothing | dark ambient, 58–64, granular stutter, baritone + 1 small-voice break. Very low BPM + sparse = Suno may struggle to hold structure for full length; lean on `[Instrumental]`/section tags and a short word count. | GO |
| 3 | Contact | electroacoustic dark ambient, 70, modal shift, **four voices** (proto-host, warm, reaching, first logic line). Four registers in one track is the second-densest vocal ask after Track 10 — but they're *sequential*, not stacked, so it's manageable with clean section metatags. | NEEDS-CHANGE (sequence the voices, don't stack; verify modal shift survives) |
| 4 | Structure Optimization | neoclassical electronic / cold sequencer, 96, logic-voice lead + witness low layer. Maps to `orchestral electronic` / `neoclassical` presets. Witness as parenthetical layer = native. | GO |
| 5 | Strike | dark electro rock, 132, kinetic belt-alto + logic denial refrain. Maps to `dark-electro-rock` preset. Two voices trading = use voice-switch metatags per `suno-preferences.md` inline pattern. | GO |
| 6 | The Click | industrial darkwave, 80 → ritard to 0 → reboot, C pedal. **The "ritard to 0 then reboot" is a post gesture** (Suno won't stop-and-restart on command). Generate the body; impose the silence/reboot in edit (see C5). | NEEDS-CHANGE (ritard/reboot in post) |
| 7 | The Silent Watch | cold dark synth / minimal synth, 72, the watch + narrator intro. Maps to `dark synth-pop`/`minimal synth`. KOH-reset to 0.998 is a **mix/master move** (re-clean the owned drone), not a generation move. | GO (drone reset via Layer A + mastering) |
| 8 | The Anomaly | cold dark synth-pop, 100, detuned doubled lead. Detuned-double is achievable via `detuned doubled vocal` descriptor (matches §4 S2 gesture). | GO |
| 9 | Inward | dark electro rock → industrial, 116 accelerating, mid-track datamosh + KOH cliff. Accelerando within a track: acceptable but verify. **Datamosh/glitch + the KOH cliff are post + owned-stem moves**, not Suno. | NEEDS-CHANGE (glitch + cliff in post/Layer A) |
| 10 | Resonance Cascade | industrial / breakcore-adjacent, 140 frantic, **5 stacked vocal registers simultaneously** (proto-host drowning + small + reaching + heavy + mirror-echo). | **WON'T-WORK as a single prompt** — see below |
| 11 | Kernel Panic | dark ambient drone-collapse from a peak, 120 → drone-collapse, clip/saturation then crush. The "from a peak into collapse" arc within one track is ambitious; split-generate or accept that the collapse tail is a Layer-A owned-stem crush. | NEEDS-CHANGE (collapse tail = owned stem) |
| 12 | Separation Protocol | industrial darkwave, 88 metronomic, system + sweep + kinetic refusal + proto-host shatter, hard glitch-cut at shatter. Clinical metronome is fine. **Shatter glitch-cut = post** (C5). Multiple voices are sequential here, manageable. | NEEDS-CHANGE (shatter in post) |
| 13 | On Time | sparse cold electroacoustic, 64, host hollow. See Concern 2 — highest-iteration track. | NEEDS-CHANGE (anti-heal discipline) |

### Track 10 — the only genuine WON'T-WORK (as designed)

Stacking 4–5 *distinct* vocal registers **simultaneously** in one Suno prompt
does not work: V5 collapses simultaneous distinct voices toward one voice, or
muds them. The author flagged this (risk 5) and the flag is correct.

**Mitigation (this turns WON'T-WORK → GO):** generate the cascade as **separate
passes per echo-voice**, then comp in the mix —
1. Generate the drowning proto-host lead as the bed (use the host Persona).
2. Generate the small-voice, reaching-voice, heavy-voice, and mirror-echo each
   as **its own short generation** with its own register metatag, same lyrics
   timing.
3. Layer/comp them in mix-engineer with deliberate phase offset (the mirror-echo
   is "doubled and phase-offset L/R" anyway — design §4). Use **Suno 12-stem
   extraction** to isolate each vocal cleanly before comping.
4. The "maximum polyphony exceeding comfortable density" is then a **mix
   decision** you control, not a dice-roll. This is the only way to get five
   recognizably-distinct syntaxes at once.

This is more labor than any other track. Budget for it explicitly.

### One naming-rule watch item

§3's "Voice key" and §7 are correctly internal. But the design must ensure the
**lyric-reviewer's `scan_artist_names` check** (14-point checklist item 14) runs
on every track's lyrics AND style prompt. "AEGIS," "Oblivion," "Argus," "Nyx,"
"Juna," "Kael" etc. must never reach a style box or lyric — they're novel-layer
only. Low risk given the design's discipline, but make it a gate, not a hope.

---

## CONCERN 5 — Everything else that won't render natively (boot, shatter, silence, glitch, KOH numbers)

**Verdict: NEEDS-CHANGE — all of these are POST/MASTER gestures, not generation gestures. Plan them out of Suno.**

The design's risk 7 is exactly right and should be promoted from "open question"
to "production plan." Suno does **not** reliably produce: engineered silence,
hard glitch-cuts, clean stop-and-restart, datamosh/codec-failure artifacts, or a
controlled boot ignition. These are mix/master/edit moves:

| Gesture | Track(s) | Where it actually happens |
|---|---|---|
| Boot / KOH ignition (sub swell from silence, tick locks to grid) | 1 | DAW: build the swell + tick on the owned KOH stem; butt-join to the generated body. |
| Ritard-to-0 → resonant silence → cold reboot | 6 | DAW edit: cut the generated tail, insert silence, restart. Suno won't do this on command. |
| KOH cliff (0.991 → 0.21 mid-track) | 9 | Owned KOH stem automation (Layer A), dropped under the generated track. |
| Datamosh / codec-failure glitch | 9, 10 | Post FX (granular/bitcrush/buffer-repeat) on the owned stems or stems extracted from Suno. |
| Hard "shatter" glitch-cut to silence + debris | 12 | DAW edit + glitch FX. The single most important post moment of the album. |
| Collapse-into-noise drone crush | 11 | Owned KOH stem (Layer A) saturating to noise. |
| Sterile clean arp (anti-heal) | 13 | Generation + harmonic discipline + possible owned MIDI arp (Concern 2). |

### KOH numbers and `[SYSTEM-STATUS]` log lines (risk 6 — real and fixable)

This is a genuine Suno hazard and the author flagged it correctly:

1. **Square brackets in the lyrics box are read as section/metatags or
   misrendered.** `[SYSTEM-STATUS — NOMINAL]`, `[PROTOCOL KOH_1.0 — INITIATED]`
   **must not appear bracketed in the lyrics body.** Either (a) render the line
   as plain spoken lyric text with no brackets, or (b) make it a *titlecard /
   spoken* line and write it out: `system status nominal`. Brackets are reserved
   for section/voice tags only.
2. **Decimals and large numbers get mispronounced.** Suno will not reliably say
   "0.998" or "14,832" or "2,304." Per lyric-writer pronunciation rules, spell
   them phonetically in the **Suno lyrics box only** (streaming lyrics keep
   standard form):
   - `0.998` → `zero point nine nine eight`
   - `0.18` → `zero point one eight`
   - `14,832` → `fourteen thousand eight hundred thirty-two`
   - `2,304 tiles` → `two thousand three hundred four tiles` (the design's §7
     already writes the ending out in words — good; do the same everywhere).
   - `21 degrees` → `twenty-one degrees`
3. Record every one of these in each track's **Pronunciation Notes table** so
   the lyric-reviewer's `check_pronunciation_enforcement` gate verifies they were
   applied (lyric-reviewer checklist item 3). Numbers-as-words is a *required
   substitution*, not documentation.

### Token-bias collision (album-wide, under-flagged in the design)

The album's core vocabulary — **echo, noise, shadow, mirror, whisper** — sits
squarely on Suno's token-bias list (reference: Echo, Ghost, Silver, Shadow,
Whisper, Crystal, Velvet). Two consequences:
- Suno may **insert** these words where you didn't write them, or **substitute**
  them for your chosen words. Add `Do not change any words. Sing exactly as
  written.` to the top of every lyrics box on this album. This is cheap
  insurance and should be a house default for Chapter Zero.
- It may also lean the *production* toward generic "atmospheric echo" presets.
  Counter with the specific cold/dry descriptors already in the design.

### Word-count / density discipline (lyric-writer/reviewer gate)

There is **no genre README at the `dystopian-future-synth` bucket level** (only
per-album READMEs exist), so the lyric-writer's density/pacing check (item 11)
and the lyric-reviewer's check (item 12) have **no `Density/pacing (Suno)`
default to read**. Two consequences to fix before writing:
- **Create a bucket-level genre README** (or set per-track Target Duration +
  density defaults) so the density/pacing hard-fail gate has a ceiling to check
  against. Without it, those gates silently no-op.
- The `lyric-writing-guide.md` intimate-work target (140–220 words at 3:30–4:30)
  is the right ceiling for the ambient/electroacoustic tracks (1, 2, 3, 7, 13);
  the rock/industrial tracks (5, 9, 10, 12) can carry more but Suno's own
  reference caps usable lyric density at ~200–350 words regardless. Keep all
  tracks lean — sparse fits both the platform and the aesthetic.

---

## Cross-cutting workflow note (chain compliance)

Per the project workflow chains, this is concept-stage only (`tracks/` is empty).
Before any generation:
- `album-conceptualizer` Phase 7 confirmation is a **hard gate** — get explicit
  user go-ahead on the 7 planning phases first.
- Documentary-style sources gate does **not** apply (this is narrative/OST
  translation of a fictional chapter, `sources_verified = N/A` is fine).
- Pre-generation chain per vocal track: lyric-writer → pronunciation-specialist
  (numbers/brackets/German terms) → lyric-reviewer (14-point) → pre-generation-check.
  The number-spelling and bracket-stripping above are **pronunciation-specialist
  work** and must be done, not skipped, because they're functional Suno hazards.

---

## Quick wins to make it more Suno-robust (do these first)

1. **Build the host Persona before writing track 1.** It's the single highest-
   leverage continuity move and makes Track 13's "same voice, now hollow" real.
2. **Own the KOH drone as a separate stem with automation.** Stop trying to make
   Suno track a decimal. This converts risk 4 from open to solved.
3. **Generate the two narrator intros (1, 7) as separate short clips.** Protects
   level, protects the boot gesture, and lets you place them precisely.
4. **Add `Do not change any words. Sing exactly as written.`** to every lyrics
   box (token-bias defense for echo/noise/shadow/mirror/whisper).
5. **Spell every number and strip every bracket** from lyrics bodies; log in
   Pronunciation Notes so the reviewer gate enforces it.
6. **Plan Track 10 as a multi-pass comp**, not a single prompt. Budget the labor.
7. **Reserve Track 13's exclude-styles budget** for `no warmth, no major key,
   no reverb bloom, no uplifting resolution` and write the melody to refuse the
   tonic. Expect 2–3 rolls.
8. **Create the missing bucket-level genre README** so density/pacing gates have
   a ceiling to check.
9. **Plan per-track genre mastering overrides** (ambient/electroacoustic/
   industrial/drone span one preset can't cover) and run the state-axis LUFS/LRA
   bias from `mastering-presets.yaml`.
10. **Treat boot, ritard-reboot, glitch, shatter, and KOH-cliff as a post shot
    list** (the table in Concern 5), handed to mix-engineer, not to suno-engineer.
