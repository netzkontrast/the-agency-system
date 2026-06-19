# Chapter Zero — Arbiter Synthesis (Round 2)

**Role:** Synthesizer, not judge. Consolidates agreed fixes → Section A; surfaces
every cross-lens conflict without resolving it → Section B.
**Ground truth:** `SOURCE/section-meta.md` → `SOURCE/kapitel-0.md`
(hierarchy per `SOURCE/loop/NAVIGATION.md` §1).
**Inputs:** `DESIGN.md` (v2) + `SOURCE/loop2/fidelity.md` · `feasibility.md` ·
`accessibility.md`.

---

## Section A — Ranked Work-Order for DESIGN v3

*The agreed, non-conflicting fixes. Execute top-to-bottom. Items are de-duplicated
across all three critiques. Every item below either has no lens objection, or the
other lenses are silent on it.*

**Ordering principle:** fidelity-correctness first (source facts), then feasibility
"how" fixes that carry no tradeoff, then accessibility enhancements that are pure
staging wins the other lenses do not contest.

---

### A1 — [FIDELITY] Drop 0.67 from the Track 9 paradox ladder; correct to 0.84 → 0.99
**Sources:** fidelity/NEW-MINOR-1.
**Precise change:** In `DESIGN.md` §2 row 9 (L107), §3 Track 9 (L176), §4 KOH
density ladder (L256), and §0 revision log entry for C1 — remove "zero point six
seven →" from every instance of the paradox-meter sequence so it reads
**"zero point eight four → zero point nine nine"** (not "zero point six seven →
zero point eight four → zero point nine nine"). 0.67 remains Track 8's reading
only (§3 Track 8 L175, §8 L609 spell-out list).
**Why:** 0.67 is kapitel-0.md's *perturbation* log (L195); the two *schrecken*
paradox logs are 0.84 (L217) and 0.99 (L237). Fidelity critic: "same class of
error as the original C1, just smaller."
**Sections touched:** §0, §2, §3, §4.

---

### A2 — [FIDELITY] Restore name-quarantine: return §0/§2/§3/§6 to function-form
**Sources:** fidelity/NEW-MAJOR-1.
**Precise change:** Replace every personal name that leaked out of §7 back to its
function-form equivalent, restoring §7 as the sole names zone:
- **§0 revision log** (L25–37): `lex` → "the logic-voice"; `arg` → "the
  annotating-voice"; `mor` / "Moros" → "the heavy-voice"; "Juna" → "the signal /
  the anomaly"; "Silas" → "the mirror-echo".
- **§2 Source-Fidelity Map** (L98–110): "MOROS-echo" → "the heavy-voice echo";
  "RHYS" → "the warm-voice"; "LIA" → "the reaching-voice"; "KIKO" → "the
  small-voice"; "LEX" → "the logic-voice"; "ARGUS" → "the annotating-voice";
  "NYX" → "the kinetic-voice"; "JUNA" → "the signal/anomaly"; "SILAS" → "the
  mirror-echo"; "AEGIS axiom" → "the first system axiom"; "OBLIVION" → "the
  sweep-voice"; "KAEL" → "the host".
- **§3 voice-key legend** (L160–164): remove "AEGIS-as-system-logic" if it appears
  as a cap-name form; replace with "the protocol / the system / the watch".
- **§6 art direction** (L413): "Silas's gold leaf" → "no Kintsugi gold leaf — the
  mirror-echo's vocabulary is not present here" (or simply "no gold leaf —
  no Kintsugi").
Cross-references from §2/§3 to §7 should use function form only ("see §7 for
source mapping").
**Why:** The §7 firewall exists to prevent a careless copy-paste from leaking a
name into a style box or art prompt. §2/§3 are the tables a lyric-writer or
art-director reads at the handoff. Fidelity critic: "once 'MOROS-echo' or
'Silas's gold leaf' sit in the working brief beside the track they map to, a
name-leak … is one careless copy-paste away."
**Sections touched:** §0, §2, §3, §6.

---

### A3 — [FIDELITY] Add 0.41 to the §8 spell-as-words substitution list
**Sources:** fidelity/NEW-MINOR-2.
**Precise change:** In §8 "Spell every number/decimal as words" list (L606–612),
add: `persistence 0.41` → `"zero point four one"`. The value appears at §3 Track 7
(L174) and must be covered so it isn't stripped by a later editor and so
pronunciation-specialist logs it in Track 7's Pronunciation Notes table.
**Sections touched:** §8.

---

### A4 — [FEASIBILITY] Clarify narrator-intro wording: separate clips, not a bridged tag
**Sources:** feasibility/NEW-1.
**Precise change:** In §8 "Narrator intros" (L577–582), replace the phrase "then
hard-cut to `[Verse 1]`" with a clarification that the intro clip *ends* and the
sung body is a **separate generation whose own lyrics begin at `[Verse 1]` /
`[Intro]`**; the "hard-cut" is a mix/edit butt-join, not a tag bridging clip A
to clip B. One sentence rewrite.
**Sections touched:** §8.

---

### A5 — [FEASIBILITY] Make Suno-box phonetic-only rule explicit re: token-bias guard ordering
**Sources:** feasibility/NEW-2.
**Precise change:** In §8 token-bias section (L613–617), add one sentence making
the ordering explicit: the **Suno box carries only the already-spelled/phonetic
form** (e.g. "K-O-H" not "KOH"), and the `Do not change any words. Sing exactly
as written.` guard then locks that form. The pronunciation-specialist must apply
phonetic substitutions *before* the token-bias guard is set, not after. Prevents
the guard from fighting the deliberate phonetic spellings.
**Sections touched:** §8.

---

### A6 — [FEASIBILITY] Add per-section Persona assignment for T6/T11/T12
**Sources:** feasibility/NEW-4.
**Precise change:** In §8, for each of Track 6, Track 11, and Track 12 (their
per-track NEEDS-CHANGE entries), add a one-line **Persona-assignment-per-section**
note specifying which Persona (host vs. watch/system) drives which section of the
generation. Example form for T6: "host Persona for the proto-host opening sections;
watch Persona for the axiom delivery and the second-movement cold reboot." This
ensures the per-voice-generation discipline is explicit before lyric-writer runs.
**Sections touched:** §8.

---

### A7 — [FEASIBILITY] Flag Track 9 accelerando risk; recommend generation strategy
**Sources:** feasibility/NEW-3.
**Precise change:** In the Track 9 per-track NEEDS-CHANGE entry (§8 L539–540), add
a flag: "Suno honors a single in-track accelerando instruction unreliably across
a 3–4 min generation. Preferred approach: generate Track 9 at a **fixed 116 BPM**
and impose the accel feel via the owned-stem post layer / arrangement. Alternative:
split-generate (pre-cliff vs post-cliff) as per Track 11's open decision (§8
L643–644) — add this as open decision #3."
**Sections touched:** §8.

---

### A8 — [FEASIBILITY, BUILD PREREQUISITE — not a design edit] Create the bucket-level genre README
**Sources:** feasibility/C5 + QW8 (PARTIAL — the only unmet build prerequisite).
**Precise change:** This is a **pre-generation build action**, not a DESIGN.md
edit. Before lyric-writer runs, create
`artists/the-agency-system/albums/dystopian-future-synth/README.md` (or the
genre-bucket equivalent per the bitwize-music plugin's genre-README convention)
with:
- Target word ceilings: 140–220 words (ambient/electroacoustic: T1, 2, 3, 7, 13);
  200–350 words (rock/industrial: T5, 9, 10, 12).
- Per-track Target Duration (required for lyric-reviewer's density gate to fire).
The §8 prerequisite note (L514–518) already documents this; the file simply needs
to be created on disk.
**Sections touched:** none in DESIGN.md — separate file creation.

---

### A9 — [ACCESSIBILITY — pure win, no lens objects] Elevate heavy-voice T1→T10 callback to a deliberate hook strategy
**Sources:** accessibility/§D (area D, ranked item #5).
**No fidelity objection** (the hook already exists: fidelity confirmed M1 closed,
the heavy-voice echo is correctly in T1; feasibility does not object).
**Precise change:** In §3 Track 1 (L168) and §3 Track 10 (L177), add a shared
**callback note**: the heavy-voice's "It is pointless. It was always pointless"
appears as a faint fracture in T1 and returns full-voiced in T10. Treat this
as a *deliberate hook strategy* — make the T1 seeding "just audible enough to
register subliminally" (not buried to inaudibility) so the T10 return pays off as
a recognizable return. A lyric-writer note in §8 should flag this as the album's
strongest existing memorability device.
**Sections touched:** §3, §8.

---

### A10 — [ACCESSIBILITY — pure win, no lens objects] Establish the axiom as a hook, not a spoken aside; T2/T4 one-line anchors
**Sources:** accessibility/§D.
**No lens objection** (fidelity already locked the axiom verbatim at §7 L478–480;
feasibility has no objection to how it is staged).
**Precise change:**
- In §3 Track 6 (L173), add a note that the axiom "It is what prevents it from
  not being" must be staged as a **genuine melodic hook** (repeated, given a
  melodic shape) — not a spoken aside; the lyric-writer should treat this as the
  record's signature line.
- In §3 Track 2 (L169), note that "It is cold. I am small." is the hook candidate
  — **elevate it to a returning refrain**, not a one-time line.
- In §3 Track 4 (L171), identify one repeatable line ("hold can be prepared," or
  "predict the wave") to be explicitly elevated to a **motif** so the track has
  a grip anchor beyond cold-sequencer texture.
**Sections touched:** §3.

---

### A11 — [ACCESSIBILITY — pure win, no lens objects] Staging note for T13: host-Persona-as-knife + placed ending gesture + brevity
**Sources:** accessibility/§E.
**No lens objection** (fidelity already requires sterile/anti-heal; feasibility
confirmed T13 anti-heal plan as GO; no critic objects to staging specifics).
**Precise change:** In §8 Track 13 anti-heal plan (L559–575), add:
1. A note naming the **host Persona's sameness as the primary emotional lever**:
   the listener has heard this timbre as the frightened, feeling proto-host in
   T1/2/3; that same voice now affectless and counting is the payoff — treat this
   as the load-bearing emotional moment, not just a Layer-C bullet.
2. Permission for a **1–2 second ghost of T3's warm melodic fragment** under the
   counting as a *production* memory the host doesn't react to (stays within the
   §8 guardrail: the host names nothing; the production remembers, he doesn't).
3. A **brevity target**: 90–120 seconds preferred; flag that a long sterile track
   tests patience while a short one lands like a slammed door.
4. Clarify that the ending should be a **deliberate, placed final gesture** — the
   arp resolving to the open interval (b6/2nd per the anti-heal plan) and
   *holding* — so the flatness reads as intentionality, not file-cutoff.
**Sections touched:** §8.

---

**Section A total: 11 items.** Top 3 by priority:
1. **A1** — paradox-ladder source error (same class as C1; touches §0/§2/§3/§4).
2. **A2** — name-quarantine restoration (architectural firewall; touches §0/§2/§3/§6).
3. **A3** — add 0.41 spell-out to §8 list (one line; low cost, guards a real number).

Items A4–A7 are feasibility wording tightenings.
Item A8 is a **build prerequisite** (file creation), not a DESIGN.md edit.
Items A9–A11 are accessibility staging enhancements with no lens objections.

---

## Section B — Conflicts & Tensions (DO NOT RESOLVE)

**Two fixed boundaries — not conflicts, just the walls every option must respect:**

1. **Source truth for fidelity facts.** `section-meta.md` wins all KOH/tier/state
   disputes. `kapitel-0.md` wins all verbatim-prose disputes. An option that
   contradicts either is out of bounds regardless of accessibility or feasibility
   benefit.

2. **name_exposure hard rule.** Function/role only in all output fields (lyrics,
   Suno metatags, Style Boxes, promo, art prompts). Personal names (Kael, Nyx,
   Lex, Rhys, Kiko, Lia, Moros, Argus, Silas, Juna, AEGIS, Oblivion) appear
   ONLY in `DESIGN.md §7` and SOURCE files. Any option that moves a name into an
   output field is out of bounds.

---

### B1 — Track 10: simultaneous polyphony vs. sequential round
**[SIGNIFICANT — escalate to user]**

**The decision:** How to render the four-voice cascade of `kaskade` (section-meta
L42: "all echoes roar; KIKO · LIA · MOROS · SILAS max polyphony") in the
generated/comped audio.

**Fidelity's position:** The source language is *simultaneous* — section-meta
annotation (L42) reads "alle Echos auf einmal" (all echoes at once); the design
(§3 Track 10 L108) says "all echoes roar at once … maximum polyphony." The
section-meta L42 explicitly states max polyphony. Rendering it as a sequential
round would soften the simultaneity that is part of the source's meaning: a
*cascade* that hits all at once, not one that politely takes turns. Fidelity is
not a voice in this critique round but its v2 text (preserved in §3 L108) and
section-meta L42 are the ground truth.

**Accessibility's position** (accessibility/§C, ranked item #3): "Don't render
the cascade as a simultaneous four-part chord. Render it as a **round / rapid
hand-off** — each echo surfaces, dominates for 2–4 bars, gets swamped by the
next, the way intrusive memories actually cascade." Accessibility argues this
is *more* faithful to the word "Kaskade" (a cascade is sequential by definition),
AND makes the voices perceptually distinguishable (which the simultaneous stack
will not), AND de-risks the comp (fewer truly-simultaneous stems). Accessibility
explicitly says: "Sequential-with-overlap reads as *one mind being flooded by
distinct ghosts* far better than a simultaneous stack reads as anything."

**Feasibility's position** (feasibility/§2, recipe spot-check): The multi-pass
comp "is the correct platform-true method for >2 simultaneous distinct registers"
and the track is confirmed GO. Feasibility says it can build *either* —
simultaneous (as designed) or sequential — and does not object to either option.
It is neutral on the faithfulness question.

**The genuine conflict:** Fidelity and accessibility disagree about which is
*more faithful*. Fidelity reads "alle Echos auf einmal" as simultaneity;
accessibility reads "Kaskade" as implying sequential. Both cite the source. This
is not a how-to dispute — it is a craft/interpretation dispute about what the
source actually calls for.

**Concrete stake / cost of each option:**
- **Simultaneous (current design):** source annotation "alle Echos auf einmal"
  honoured literally; max-polyphony as stated. Risk: to a cold listener, four
  voices at once is perceptually a wall of sound, not distinct ghosts. The
  *fidelity* point (one consciousness fracturing) may read as "a crowd," which is
  the opposite of the intent. Comp is the album's most labor-intensive track.
- **Sequential round:** "Kaskade" etymology honored; voices are individually
  distinguishable; emotional legibility highest; de-risks comp. Risk: the
  simultaneity of "alle Echos auf einmal" is lost; the crash feels more
  like a procession than an explosion; may understate the source's violence.
- **Hybrid (sequential-with-overlap):** echoes break the surface in rapid
  succession with some overlap — proto-host lead continuous underneath, each echo
  enters before the previous has fully faded. Tries to capture both the
  instantaneous-flood feel and individual legibility. Neither critic explicitly
  endorses or rules out this middle path.

**Realistic choices:** (a) simultaneous stack as written; (b) sequential round
as accessibility proposes; (c) rapid sequential-with-overlap hybrid.

---

### B2 — Track 9: dynamic staging — violent turn-inward vs. tight/airless/mid-volume
**[SIGNIFICANT — escalate to user]**

**The decision:** What is the dynamic and loudness character of Track 9 ("Inward")
as a *listener experience*?

**Fidelity's implicit position (from the current design, §3 T9 L176):** The design
describes T9 as "dark electro rock → industrial; mid-track datamosh, KOH-drone
collapse" — the imagery is violent and industrial. §4 Layer E masters S3 "loudest
/ most compressed." The source (`schrecken` = "algorithmic terror," the system
"turning its weapons inward") reads as a high-intensity event.

**Accessibility's position** (accessibility/§A, ranked item #1): T9 should be
**tight/airless/mid-volume/compressed** — not yet the loudest track. The
argument: with T9, T10, and T11 all maxed-out in a row, the listener experiences
ear-fatigue and plateau. By making T9 "claustrophobic, accelerating dread" at
mid-volume, T10 becomes the explosive *release* of T9's compression (the widest,
loudest peak), and T11 becomes the implosion. Accessibility frames this as a
pure staging move that "keeps all three beats at full source-truth intensity while
giving the ear a *shape* (build, peak, void) instead of a flat loud plateau."

**Feasibility's position** (feasibility/NEW-3): Separately flagged the in-track
accelerando risk — Suno handles it unreliably — and recommends generating at flat
116 BPM with post-accel via owned layer. Feasibility does not weigh in on the
loudness/dynamic character question directly, but its flat-116 recommendation
interacts with the design's "116, accelerating" spec (§3 T9 L176): if the accel
is moved to post, is the in-track energy of T9 further softened, reinforcing
accessibility's "mid-volume" reading? Or can post-accel preserve the violence?

**The genuine conflict:** Whether "turning weapons inward" is faithfully rendered
as immediate max-violence (fidelity instinct in current design), or as a
claustrophobic build toward violence — with T10 as the actual explosion — is a
staging interpretation, not a source-fact dispute. But it is a significant one:
it determines the loudness contour of the entire back half.

**Concrete stake / cost of each option:**
- **T9 as loud/industrial (current design):** faithful to "terror" and to the
  S3/Flame color in §4's state table (though note: section-meta tags T9 as Tier
  2 / ALERT, not Tier 3 / KERNEL PANIC — so using S3 mastering for T9 may itself
  be a fidelity tension). Worst case: T9, T10, T11 form an undifferentiated loud
  plateau; T10's cascade has no dynamic room to be louder than T9; the climax
  becomes wallpaper.
- **T9 as tight/airless/mid-volume (accessibility proposal):** preserves T10 as
  the true loudness peak; gives the back-half a shape (compress → explode →
  implode); differentiates T9 from T10 for the cold listener. Potential concern:
  does "mid-volume terror" understate what `schrecken` says? Source's tone is
  extreme, not restrained.
- **Note on state-palette interaction:** section-meta L41 tags `schrecken` as Tier
  2 / ALERT, while L42 (`kaskade`) is Tier 3 / KERNEL PANIC. The design honors
  this divergence in palette (§2 L142–147). If T9's mastering follows Tier 2
  (S2 = "~1–2 LU louder / lower LRA / faster attack") rather than S3, it is
  *already* supposed to be less compressed than T10/T11 — which would naturally
  support accessibility's shape. This is a fidelity-alignment argument for the
  accessibility position, but it is not unambiguous.

**Realistic choices:** (a) T9 as designed (industrial/loud, S3 mastering);
(b) T9 as tight/airless/mid-volume with S2 mastering to match its Tier 2 tag,
making T10 the loudest point; (c) T9 industrial but explicitly capped at S2
mastering to let T10 peak — treating the two separately (design flavor vs.
loudness tier).

---

### B3 — Track 10 (continued from B1): mirror-echo role — lead texture (T9) vs. comped layer (T10)
**[routine — Design decides]**

**The decision:** In T10, what is the status of the mirror-echo within the
polyphony stack?

**Fidelity / current design:** §3 T10 (L177) lists "mirror-echo" as one of the
four comped voices at max polyphony; §5 (L350) confirms it first appears in T9.

**Accessibility's position** (accessibility/§B, §C): In T9, the mirror-echo
should be the **lead texture** (the self-attacking-its-own-echo device that makes
T9 legible). In T10, however, accessibility flags a specific perceptual risk:
"proto-host lead vs. mirror-echo … In T10 they're both present — the listener
may not perceive two things at all, just a smeared lead." It recommends
**separating them in time or pan**, not running them simultaneously at equal
level.

**Feasibility:** No objection to either approach; both are buildable under the
multi-pass comp plan.

**The conflict:** Accessibility asks for the mirror-echo to be elevated as lead
in T9 *and* to be separated/deprioritized (or offset in time/pan) from the
proto-host in T10 — but the current design treats the mirror-echo as a comped
layer in T10's polyphony stack at equal footing. The resolution in T9 (mirror-echo
as lead) is already an uncontested pure win (see B1 discussion), but how the
mirror-echo functions in T10 is a design question: if it becomes sequential
(B1, option b or c), the T10 collision is resolved automatically. If it stays
simultaneous, the proto-host/mirror-echo blurring in T10 is a real risk.

**Concrete stake:** If the mirror-echo is running simultaneously with the
proto-host timbre in T10 (both mid-baritone, both phase-offset), a cold listener
hears one smeared voice, not two. The "one consciousness fracturing" intent reads
as "a crowd" or a muddied lead. The fix (separate in time or pan) is low-cost
but requires explicit staging in §3/§8.

**Note:** This conflict is structurally downstream of B1. If B1 resolves as
sequential round (option b or c), B3 resolves automatically. If B1 stays
simultaneous, B3 needs its own explicit answer.

---

### B4 — Track 9 dynamic vs. T9 state-tier: is T9's mastering S2 or S3?
**[routine — Design decides]**

**The decision:** Which mastering tier does Track 9 receive under Layer E?

**Current design ambiguity:** §3 T9 (L176) carries the label "S2 · 0.21" (correct
per section-meta L41, Tier 2 / ALERT). §4 Layer E (L232–239) specifies S3 as
"loudest / most compressed." The design's sonic description of T9 ("dark electro
rock → industrial") implies high energy. But the state-palette row for T3
(Collapse-Peak, §6 L422) assigns T9 to T3 visual tier alongside T10/T11/T12,
while §3 correctly labels T9's *state* as S2. These two assignments (visual tier
= T3, state = S2) are the "misaligned coherence" the design explicitly honors —
but the mastering tier assignment is not made explicit for T9.

**Accessibility's position** (B2 above): argues that T9 should be at S2 mastering
(not S3) to create loudness headroom for T10. This is consistent with T9's Tier 2
state label.

**What the design needs:** an explicit decision on whether T9's mastering follows
its *state* (S2 = less compressed) or its *visual/energy character* (S3 = loudest/
most compressed). The §4 Layer E table currently assigns mastering by state-axis,
which would put T9 at S2 — but the design's sonic descriptions and §6 visual
palette both treat T9 as a T3-energy track. This ambiguity needs resolving in
§4 and §8.

**Realistic choices:** (a) T9 masters at S2 per its state label, preserving
dynamic headroom for T10; (b) T9 masters at S3 per its energy character and §6
palette assignment, making the back-half plateau explicit; (c) T9 is
explicitly called out as the "transition track" that uses S2 mastering *despite*
T3 visual palette, with a one-line note explaining the distinction.

---

### B5 — Number recitation across back-half tracks: T9 especially
**[routine — Design decides]**

**The decision:** Should number-recitation (KOH decimals spoken aloud) appear in
Track 9's lyrics?

**Fidelity's position (implicit):** The paradox-meter values (0.84, 0.99) are
logged in `kapitel-0.md` L217, L237 and are source-authentic for T9. Including
them maintains the KOH-as-running-text fidelity.

**Accessibility's position** (accessibility/§F): "Use sparingly — the numbers are
atmospheric texture, not hooks." Explicitly recommends "keep number-recitation to
T8, T11, T13 (where it's iconic); **strip it from T9** (let sound carry that
track)." Accessibility argues that T9 should be legible as self-attack via the
mirror-echo (see B1/B2); adding decimal recitation to an already-dense industrial
track risks "cold/clinical filler" for a cold listener, and the self-attack idea
is already the least legible beat — numbers would further obscure it.

**No lens objects to keeping numbers in T8, T11, T13.** The conflict is
specifically whether paradox-meter values belong in T9's lyrics.

**Concrete stake:**
- Keep in T9: source fidelity to the in-text logs preserved; the "misaligned
  coherence" paradox (0.84 → 0.99 alongside state 0.21) is audible as text.
- Strip from T9: the self-attack is more legible as a sound-driven event; T9
  is differentiated from T8 (which carries its own numbers) and T11 (which
  carries the warning count). Risk: T9 loses the paradox-meter anchor that is
  its fidelity signature.

**Realistic choices:** (a) include the paradox values "zero point eight four" and
"zero point nine nine" in T9 lyrics; (b) strip number-recitation from T9 entirely,
let the mirror-echo sound carry the paradox; (c) include them once, briefly —
one pass of the paradox values in T9 rather than a recitation motif.

---

*End of arbiter.md — Round 2.*

ARBITER-SUMMARY: SECTION-A=11 · SECTION-B-CONFLICTS=5 · SIGNIFICANT=2 (B1, B2) · ROUTINE=3 (B3, B4, B5)
