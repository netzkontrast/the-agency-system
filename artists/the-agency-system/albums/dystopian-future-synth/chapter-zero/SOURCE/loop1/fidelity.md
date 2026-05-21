# FIDELITY CRITIQUE — Chapter Zero (Kohärenz Protokoll → album)

**Reviewer:** spec-panel fidelity critic
**Source of truth:** `SOURCE/kapitel-0.md` (decoded prose) + `SECTION_META`
(`/tmp/kp0_sectionmeta.txt`) + `resolver.yaml`.
**Standard enforced:** the album must be a 1:1 transfer of Kapitel 0 into
music. Faithfulness first. Every deviation below cites the source.

The design is, on the whole, unusually disciplined — the arc order is
correct, the false-calm resets are preserved, the hollow 1.00 is honored,
and the no-Kintsugi rule is held. But it makes **factual KOH errors**,
**fabricates a voice presence the chapter does not contain**, and **softens
or mis-locates several beats**. These are not stylistic quibbles. They are
betrayals of the source data, and they must be fixed before this ships.

---

## CRITICAL — fix before the design advances

### C1. Track 9 KOH path is FABRICATED: source has no "0.991→0.21" inside `schrecken`.
- **Where:** §2 row 9 (`State · KOH = 0.991`? no — row says **0.21**, but the
  Note column says "KOH falls off a cliff mid-track"); §3 Track 9 row
  (`State · KOH = S2→S3 · **0.991→0.21**`, BPM "116, accelerating");
  §3 revision note 2; §4 KOH-meter bullet.
- **Source evidence:** `SECTION_META['schrecken'] = { koh: '0.21' }`. The only
  numeric coherence readings inside `#schrecken` are the in-text logs:
  `PARADOX: 0.84` (mid-section, internal-resonance log) and then the
  escalation log `PARADOX: 0.99 / KOHÄRENZ: 0.21`. **There is no 0.991 reading
  anywhere in `schrecken`.** 0.991 is the value of the *previous* section,
  `#perturbation` (`KOHÄRENZ: 0.991 [-0.007]`).
- **Why it's a betrayal:** the design invents an intra-track glide
  "0.991 → 0.21" that the chapter never states. The chapter's section value
  for `schrecken` is a flat **0.21** — the crash has *already happened* by the
  time the section's headline number is taken. The internal staging the source
  actually gives is `0.84 paradox` (resonance rising) → `0.99 paradox / 0.21
  koh` (escalation to existential). The drama is a **paradox climb**, not a
  coherence glide from near-nominal.
- **Required fix:** Set Track 9 section KOH to **0.21** (matching
  SECTION_META). Render the *mid-track cliff* as the source stages it: the
  drone enters Track 9 still carrying Track 8's near-nominal 0.991 *as residue
  from the previous track* (legitimate, because perturbation's reading was
  0.991 and the watch had not yet re-measured), then **crashes to 0.21 at the
  internal-resonance escalation** — but label the track's own KOH as 0.21, and
  drive the tension off the **paradox meter (0.67 → 0.84 → 0.99)**, which the
  design currently never mentions for this track. Do **not** write
  "0.991→0.21" as if 0.991 were a `schrecken` reading; it is not.

### C2. The logic-voice (Lex / rationalist) is forced into Track 3 (`kontakte`), where the source does not place it.
- **Where:** §3 Track 3 voice column ("first cold logic-voice line"); §7
  mapping table row `lex … Tracks 3, 4, 5, 6`; §2 row 3 Note ("cold proto-logic
  is born from the loss").
- **Source evidence:** `SECTION_META['kontakte']` annotation lists only
  **RHYS** and **LIA** ("RHYS-Stimme erstmals … LIA als unlösbare
  Ambivalenz"). The prose of `#kontakte` contains the Rhys voice-blocks and the
  Lia voice-block, and ends with narrator prose: *"Etwas in mir beginnt,
  Verbindungen nicht mehr nur zu spüren, sondern zu prüfen. Ein erster Hauch
  systemischer Logik. Kalt. Notwendig."* — that is the **proto-host narrator
  noticing a cold tendency**, NOT a separate logic-voice (Lex) speaking. LEX's
  first hypotactic logic is explicitly placed by SECTION_META in **`sog`**
  ("LEX · erste hypotaktische Logik") — i.e. Track 4, not Track 3.
- **Why it's a betrayal:** the design promotes a *narrator-described tendency*
  ("a first whiff of systemic logic") into an actual sung **logic-voice line**
  one section too early, and the §7 table doubles down by tagging Lex onto
  Track 3. This invents a voice presence and pre-dates the rationalist's birth.
- **Required fix:** Remove the logic-voice from Track 3's voice list. The cold
  proto-logic at the end of `kontakte` belongs to **the fragment/proto-host**
  (narrator-internal), rendered as the proto-host's diction turning clinical —
  not as a distinct logic-voice. Change §7 row to `lex … Tracks 4, 5, 6`.
  Lex's first true line is Track 4 (`sog`).

### C3. Track 8 state label contradicts the source and the design's own thesis.
- **Where:** §3 Track 8 row `State · KOH = S2 · 0.991`; §2 row 8 Tier `T2`.
- **Source evidence:** `SECTION_META['perturbation'] = { tier: 2, koh: '0.991'
  }`. Tier 2 ✓. **But** the in-text log reads `KOHÄRENZ: 0.991 [-0.007]` and
  the prose: *"Die kalte, berechnende Stabilität wich einer systemweiten
  Alarmbereitschaft."* The number barely moves (−0.007) — the system is at
  **full alert** while the meter is still near-nominal. The design's §2/§3 text
  captures this correctly in prose ("reads it cold, not yet panicked"), so the
  **S2** label is defensible. This one is borderline — flagging as CRITICAL
  only because of the interaction with C1: the design simultaneously labels
  Track 8 "S2 · 0.991" and Track 9 "S2→S3 · 0.991→0.21," which **double-uses
  0.991** and makes it ambiguous whether 0.991 is Track 8's or Track 9's
  reading. Resolve C1 and this disambiguates.
- **Required fix:** After fixing C1, ensure 0.991 appears as a KOH value
  **exactly once** in the sequence table — at Track 8 — and Track 9 reads 0.21.

### C4. The witness/annotating-voice (Argus) is under-mapped vs. the source.
- **Where:** §7 row `arg … Tracks 4 (and low-layer asides across)`.
- **Source evidence:** `SECTION_META['sog']` annotation: *"ARGUS ·
  Meta-Beobachtung tritt erstmals auf."* — Argus *first* appears in `sog`
  (Track 4). The design's §3 Track 4 voice column correctly lists
  "the annotating-voice (low layer)." Good. But `wandel` (Track 6) is dense
  with exactly the kind of clinical meta-commentary the witness owns
  (*"Die Funktionseinheit trägt eine Nummer … sie liegt in der Mitte einer
  langen Reihe und ist nicht besonders"*; *"Eine unvollständige Integration.
  Toleriert…"*). The design's Track 6 voice list omits the annotating-voice
  entirely.
- **Why it matters:** the source's Track-6 register IS the witness register
  (cold meta-observation of the unit's number and incomplete integration). The
  design hands all of Track 6 to "fragment/proto-host → the system + warm-voice"
  and silently drops the annotator.
- **Required fix:** Add the annotating-voice (witness, parenthetical low layer)
  to Track 6's voice list — it carries the "trägt eine Nummer / unvollständige
  Integration" lines. This is not optional flavor; it is whose voice the source
  prose is in.

---

## MAJOR — material distortions, fix this pass

### M1. Track 1 drops the Moros echo that SECTION_META explicitly plants in `rauschen`.
- **Where:** §3 Track 1 voice column ("narrator (spoken cold-open) → the
  fragment/proto-host"). §7 row `mor … Tracks 1 (echo), 10` — so the design's
  *own appendix* says the heavy-voice echo is in Track 1, but the §3 tracklist
  voice column omits it.
- **Source evidence:** `SECTION_META['rauschen']`: *"MOROS-Echo schleicht ein.
  Stilebene 1 mit Bruchstellen."* The prose confirms it: the `rauschen`
  paragraph *"Es ist sinnlos. Es war immer schon sinnlos. Es wird nichts mehr
  kommen…"* is verbatim the collapsed-voice (Moros) register that returns in
  full in `kaskade` (*"Es ist sinnlos. Es war immer sinnlos. Es wird nichts
  mehr kommen. Nichts."*).
- **Required fix:** Add "the heavy-voice (faint Moros echo, Stilebene-1
  break)" to Track 1's voice column so §3 matches §7 and the source. The
  "Bruchstellen" (break-points) instruction should be reflected in Track 1's
  sonic note.

### M2. Track 13 imports "no memory, no grief, no healing" — but the source's coda is colder and stranger than "amnesia."
- **Where:** §3 Track 13 emotional core: "No memory, no grief, no healing.
  Dissociation is born; the cure is the wound."
- **Source evidence:** the coda is *only*: *"Zweitausenddreihundertvier
  Kacheln. Einundzwanzig Grad. Der Atem geht in vier Sekunden hinein, in sechs
  hinaus. Der Korridor ist leer. Ich bin pünktlich."* There is **no narration of
  loss, no "no memory," no statement about grief** — the horror is precisely
  that the text says **nothing** about what was lost. The flatness IS the
  content. The design's gloss "No memory, no grief, no healing" is editorializing
  what the source pointedly refuses to say.
- **Why it matters:** the fidelity risk is that a lyricist reads "no grief" and
  writes a *line about absent grief* — which would betray the source by naming
  the void the chapter leaves unnamed. The chapter achieves dread by pure
  banality (tile-counting, breath-counting, "I'm on time"). Any lyric that
  *comments* on the amnesia breaks the effect.
- **Required fix:** Reword the Track 13 core to: the host wakes into pure
  procedure — counts 2,304 tiles, 21 degrees, breath in four out six, empty
  corridor, "I'm on time." **The lyric must NOT name memory, grief, or
  healing**; the absence is conveyed only by what the host does not say. Add
  this as an explicit lyric-writer guardrail.

### M3. Track 6 fuses the axiom and the inward-turn into one beat, blurring the source's two distinct movements.
- **Where:** §2 row 6 Note; §3 Track 6 core (ends at "Loneliness survives only
  as phantom noise"); §3 maps `wandel` → only Track 6.
- **Source evidence:** `#wandel` is a long section that contains TWO discrete
  movements: (a) the Click / founding axiom / phantom-in-the-machine (¶ up to
  *"Ein Phantomgefühl im Herzen der Maschine"*), and (b) a *forward-looking*
  movement — *"Ein neuer Prozess beginnt. Eine logische Eskalation des Prinzips:
  eine Wendung nach innen … die Erschaffung eines inneren Raumes … Eine
  Binnen-Physik … Vielleicht gibt es einen Punkt, an dem das Werkzeug, das
  Welten simuliert, beginnen könnte, eine Welt zu sein."* This **"Wendung nach
  innen" / inner-laboratory** material is the *seed* of the later turn-inward,
  and it is structurally part of `wandel`, not `schrecken`.
- **Why it matters:** the design's Track 6 stops at "phantom noise" and never
  accounts for the second half of `wandel` (the simulated inner world / "the
  tool that simulates worlds could become a world"). That is a dropped beat —
  and it is the source's own foreshadow of the inward catastrophe.
- **Required fix:** Extend Track 6's core to include the **second movement of
  `wandel`**: after the axiom and the phantom, the system builds an *inner
  simulated space* ("a laboratory turned inward," "an inner-physics that
  serves") — the cold seed of the later turn-inward. Either fold it into Track 6
  explicitly or note it as Track 6's outro. Do not let `wandel`'s back half
  vanish.

### M4. "Strike" (Track 5) mis-assigns the prediction-failure beat and risks losing the source's exact denial line.
- **Where:** §3 Track 5; §2 row 5.
- **Source evidence:** `#kampf` contains the precise mechanics: the prediction
  *failed* — *"sie hat den Schlag bei Sektor zwei-acht-null erwartet, er kam bei
  sechs-neun-zwei"* (expected at 280, came at 692); "sixteen bindings removed";
  and the denial is verbatim: *"Dies ist nicht Verlust, sondern
  Strukturoptimierung. Es ist nicht Verlust. Es ist nicht. Verlust."* The design
  paraphrases this as *"This is not loss. It is structure optimization. It is
  not. Loss."* — close, but it **silently drops the middle sentence** ("Es ist
  nicht Verlust" / "It is not loss") and the **prediction-failure** (280 vs 692)
  which is the *cause* of the strike beat.
- **Required fix:** (a) Preserve the full three-step denial structure: "This is
  not loss, but structure optimization. **It is not loss.** It is not. Loss."
  (three beats of negation collapsing, mirroring the German). (b) Note the
  prediction-failure (predicted sector 280, hit at 692) as the lyrical trigger —
  it's why the watch/logic-voice has to rationalize the dead. Currently the
  design's "Strike" reads as the void attacking out of nowhere; the source makes
  it a *failed prediction* the system then denies.

### M5. The signal/anomaly (Juna) is correctly kept as texture — but the design lists it on Track 9, where the source's anomaly has already receded into internal resonance.
- **Where:** §7 row `(signal, unnamed) … Tracks 8, 9`; §3 Track 9 ("the system;
  the mirror-echo").
- **Source evidence:** In `#schrecken` the external signature is explicitly
  *no longer the active threat*: *"Gleichzeitig registrierten interne Sensoren
  eine massive, ansteigende Welle der Inkohärenz, ausgehend von den
  Subsystemen, die mit den Residual-Echos assoziiert waren"* and the system
  **misclassifies the internal resonance as the attack**. The anomaly's role in
  `schrecken` is as *misattributed cause*, present only as the system's false
  belief — it is no longer radiating. Listing Juna-texture across Track 9 as if
  it's still an active external presence risks the mix foregrounding the
  anomaly when the source's whole point is the system turning **inward**.
- **Required fix:** Keep Juna-texture strong in Track 8 (perturbation, where it
  arrives and radiates ontological pressure) and **fade it to a residual / mis-
  attributed trace in Track 9** — the signal should be barely present, because
  the catastrophe in `schrecken` is internal. The mirror-echo (Silas) and the
  internal-resonance bands are what dominate Track 9, not Juna.

---

## MINOR — tighten for accuracy

### m1. KOH meter bullet (§4) lists Track-7/8 as "0.99+ (S0)" — but Track 8 is S2/T2.
- §4 "0.99+ (S0): … (Tracks 1 intro, 7, 8)" groups Track 8 under **S0**. Track 8
  (`perturbation`) is **tier 2 / S2** per SECTION_META, even though its KOH
  reads 0.991. The drone *density* can stay near-nominal, but do not label Track
  8 as S0. Fix: "(Tracks 1 intro, 7; and Track 8's drone density, though Track 8
  is S2-alert)."

### m2. §2 row 9 "First phantom-echo mirror" vs §3 "the mirror-echo (first appearance)" — consistent, but verify Silas is absent before Track 9.
- SECTION_META confirms `schrecken` = "SILAS · erstes Echo" and `kaskade` has
  Silas. The design correctly maps sil → 9, 10 and never earlier. ✓ No change;
  noted for the record so a later editor doesn't "helpfully" add Silas earlier.

### m3. The `dazwischen` 0.61 handling (§8 Q2) is sound — but state it in the table.
- The design folds `dazwischen` (KOH 0.61, tier 1) into Track 7's intro and
  argues in §8 it's the narrator's hovering question, not a system-state. That
  read is defensible and faithful (the prose is pure narrator: *"Hören Sie hin.
  Eine Frage steht im Raum. Vielleicht hat sie keinen Sprecher mehr."*). But the
  §2 table shows `dazwischen` KOH 0.61 with no indication the drone briefly dips
  to 0.61 before resetting to 0.998. Minor: add a half-line in §4's KOH bullet
  noting the brief 0.61 dip in Track 7's narrator intro **before** the reset to
  0.998 — otherwise the reset reads as 0.58 (Click) → 0.998 directly, skipping
  the source's 0.61 way-station.

### m4. "Click" English rendering (§8 Q3) — recommend retaining "Klick" untranslated.
- The source's hinge word is *"Und dann — Klick."* — a single bare syllable
  that IS the fusion event. The design renders it "Click." English "Click" is
  fine semantically, but the source's menace is in the abruptness. Recommend
  keeping the bare-syllable delivery and considering "Klick" untranslated per
  the lyric guide's un-translatable-German allowance (the critic's call from
  §8 Q3: **retain "Klick"** for the hook; render the rest in English). This is a
  recommendation, not a defect.

### m5. Founding axiom translation is faithful — lock it.
- *"Es ist, was es verhindert, dass es nicht ist."* → "It is what prevents it
  from not being." ✓ Accurate. No change. Ensure this exact English line is the
  Track 6 hook and is not paraphrased downstream.

---

## What the design got RIGHT (so it is not weakened in revision)

- **Arc order** follows the chapter beat-for-beat: vorwort → rauschen → herz →
  kontakte → sog → kampf → wandel → (dazwischen) → wacht → perturbation →
  schrecken → kaskade → kollaps → trennung → coda. No beat reordered. ✓
- **False-calm resets preserved exactly:** KOH 0.998 at Track 7, 0.991 at Track
  8 — the meter lies until the cliff. This is the single most important
  structural trap and the design honors it. ✓
- **The crash is located correctly** as happening *inside* the inward-turn
  (`schrecken`/Track 9), *before* the cascade (Track 10). Revision note 2 fixes
  exactly the error a careless reader would make. ✓ (The only error is the
  fabricated 0.991 *value* — see C1 — not the location.)
- **The hollow 1.00 / no-Kintsugi rule is held everywhere:** §1 fidelity
  statement, §2 tripwire, §4 S4 row ("rendered sterile"), §5 ("no integration
  chorus"), §6 ("dead furrows, never a glowing"). The ending does not heal. ✓
- **Voices honored to the chapter, absent voices NOT forced in:** integrator,
  sexualized-override, protector, Wir-Stimme correctly excluded (§5). ✓
- **name_exposure hard rule held:** all music-facing voice references are
  function-form; personal names quarantined to the §7 INTERNAL-ONLY appendix. ✓

---

## RANKED REQUIRED-FIX SUMMARY

1. **C1 (Critical):** Track 9 KOH is **0.21**, not "0.991→0.21." 0.991 is
   `perturbation`'s value, not `schrecken`'s. Drive Track 9 off the paradox
   meter (0.84→0.99). Fix §2 row 9, §3 Track 9, §3 revision note 2, §4 bullet.
2. **C2 (Critical):** Remove the logic-voice (Lex) from Track 3. Per
   SECTION_META, Lex's first logic is in `sog` (Track 4). The cold tendency in
   `kontakte` is the proto-host's, not a separate voice. Fix §3 Track 3 + §7
   `lex` row → Tracks 4,5,6.
3. **C4 (Critical):** Add the annotating-voice (witness/Argus) to Track 6 — the
   source's "trägt eine Nummer / unvollständige Integration" lines are the
   witness register and are currently unassigned.
4. **M2/M3/M4 (Major):** (M2) Track 13 must NOT name memory/grief/healing — the
   source's coda is pure procedure; the absence is the content. (M3) Track 6
   must include `wandel`'s second movement (the inner simulated world / "the
   tool could become a world"); currently dropped. (M4) Track 5 must preserve
   the full three-beat denial ("It is not loss. It is not. Loss.") and the
   prediction-failure (sector 280 vs 692) as the trigger.
5. **M1/M5 (Major):** (M1) Add the faint Moros heavy-voice echo to Track 1's
   voice column to match §7 and SECTION_META's "MOROS-Echo schleicht ein." (M5)
   Fade Juna-texture in Track 9 to a residual mis-attributed trace; in
   `schrecken` the threat is internal, the anomaly has receded.
