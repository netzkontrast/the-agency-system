<!--
Sources, top to bottom:
  1. https://github.com/netzkontrast/agency/blob/867453e/skills/the-agency-system-architect/sprachliche_abbildung.md
  2. https://github.com/netzkontrast/agency/blob/867453e/skills/suno-lyric-writer/craft-reference.md
  3. https://github.com/netzkontrast/agency/blob/867453e/skills/suno-lyric-writer/SKILL.md (Phase 1, Phase 3)
  4. https://github.com/netzkontrast/agency/blob/867453e/skills/suno-lyric-writer/examples.md
Source commit: 867453e
Edit upstream and re-import, or edit here and document the divergence.
-->


# Lyric Writing Guide

## Part 1 — The Agency System project DNA

*Project-specific lyric rules. These override generic craft conventions when they conflict.*

# Sprachliche Abbildung — Zwei Stimmen, ein Lexikon

Referenz für den **Lyricist**. Sprache ist hier Architektur, nicht Ornament.

---

## Die beiden Register

Agency und Kern teilen das Vokabular (kybernetisch, systemisch). Sie unterscheiden sich in **Person, Modus, Satzbau**.

| Dimension | **Agency-Register** (außen) | **Kern-Register** (innen) |
|---|---|---|
| Person | 2. Sg./Pl. („du wirst …“, „ihr werdet …“) oder unpersönlich | 1. Sg. („ich registriere …“) seltener 1. Pl. („wir halten …“) |
| Modus | Imperativ, Futur als Befehl | Indikativ, deklarativ |
| Satzbau | Kurz, elliptisch, Nominalstil | Vollsätze, gelegentlich Enjambement |
| Affekt | Null. Autorität durch Kälte. | Gedämpft. Präzision statt Emotion. |
| Metaphern-Verwendung | Als Systemanweisung („Run compliance.“) | Als Zustandsbeschreibung („Compliance läuft nicht mehr.“) |

**Entscheidend:** beide Register sind **analytisch**. Weder Pathos noch Distanz als Schutzhaltung. Das Projekt sagt schwere Dinge in einfacher, stehender Sprache.

---

## Prosodie-Regeln

1. **Silbensymmetrie zwischen parallelen Verses.** Verse 1 und Verse 2 haben dieselbe Silbenzahl pro Zeile (±1). Dies dient nicht nur dem Latent-Modell — es *ist* Teil der DNA.
2. **Reimschema je Section konstant.** AABB oder ABAB pro Section, nicht mischen. Chorus darf eigenes Schema haben.
3. **Staccato in Verses, Legato in Chorus.** Verses: kurze Phrasen, harte Konsonanten. Chorus: längere Bögen, offene Vokale.
4. **Keine Füllwörter.** Jedes Wort trägt Last. Streichbar heißt zu streichen.
5. **Enjambement nur bewusst** — als Bruchstelle, nicht als Flusskorrektur.

---

## Objective Correlative — keine Emotions-Adjektive

**Verboten:** traurig, einsam, verzweifelt, wütend, glücklich, stolz, leer.

**Stattdessen:** Zustand aus Umgebung und Metapher erzeugen.

| Gefühl (nicht benennen) | Objective Correlative |
|---|---|
| Erschöpfung | „Der Lüfter dreht seit drei Uhr früh im Leerlauf.“ |
| Panik | „Packet Loss. Packet Loss. Handshake. Packet Loss.“ |
| Verbundenheit | „Zwei Cursor blinken im selben Takt.“ |
| Kontrollverlust | „Der Log scrollt ohne mich weiter.“ |
| Klarheit | „Grid locked. 120. Ich höre den Puls jetzt außen.“ |

---

## POV-Matrix

| Wer spricht? | Typisch in Phase | Register |
|---|---|---|
| **Agency** (System-Stimme) | Onboarding, Optimization | Agency-Register, imperativ |
| **Core / Manager** | Optimization, Systematic Agency | Kern-Register, 1. Sg. deklarativ |
| **Exile** (verletzter Teil) | Lingering Echoes, System Failure | Kern-Register, 1. Sg. leiser, kürzere Zeilen |
| **Firefighter** (Abwehr-Teil) | System Failure | Kern-Register, 1. Sg. härter, abgehackt |
| **Beobachter** (Außenblick) | Fragile Connections, Meaning in the Mosaic | Kern-Register, 1. Sg. distanziert oder 3. Sg. |

**POV-Shifts innerhalb eines Tracks:** erlaubt an Section-Grenzen (Verse → Pre-Chorus), niemals innerhalb einer Zeile. Wenn ein Draft einen nicht-standardisierten Shift enthält → **nachfragen, nicht korrigieren** (Kern-Invariante 5).

---

## Lexikon-Ausschlüsse (Projekt-Verbote)

- Liebes-Vokabular des Pop-Mainstreams („Herz“, „ewig“, „dich halten“).
- Generische Dunkelheits-Tropen („Nacht“, „Schatten“ nur als Metapher für Überwachung, nie als Stimmung).
- Religiöse Metaphorik ohne Systembezug („Sünde“, „Erlösung“ → verboten; „Absolution-Protocol“ → möglich, wenn narrativ motiviert).
- Deutsche Diminutive („Herzchen“, „Stückchen“).

---

## Beispiel: Chorus-Draft nach Regelwerk

**Context:** Phase = Optimization, Cluster = Systematic Agency, Voice = Core (Manager).

```
[Chorus]
Ich halte das Grid. Das Grid hält mich.
Kein Handshake nach außen. Kein Paketverlust.
Der Kernel kennt den Takt. Der Takt kennt mich.
Ich bin nicht die Maske. Ich trage sie nur.
```

Silbenzahlen: 10-11-10-10. AABA. Kern-Register, 1. Sg. Zwei Metaphern (Grid, Kernel). Kein Emotions-Wort.

---

## Part 2 — Generic Suno lyric craft reference

*Adapted from suno-lyric-writer; applies when project DNA is silent.*


# Lyric Writer Craft Reference

Detailed tables and reference data for the lyric writer skill.

---

## Rhyme Techniques

### Rhyme Types (use variety)
| Type | Description | Example |
|------|-------------|---------|
| Perfect | Exact match | love/dove |
| Slant/Near | Similar but not exact | love/move |
| Consonance | Same ending consonants | blank/think |
| Assonance | Same vowel sounds | lake/fate |
| Internal | Rhymes within a line | "fire and desire higher" |

### Rhyme Scheme Patterns
| Pattern | Effect |
|---------|--------|
| AABB | Stable, immediate resolution |
| ABAB | Classic, delayed resolution |
| ABCB | Lighter, less pressure |
| AAAX | Strong setup, surprise ending |

### Rhyme Schemes by Genre

| Genre Family | Default Scheme | Strictness | Key Difference |
|---|---|---|---|
| **Hip-Hop / Rap** | AABB (couplet) | High — multisyllabic + internal mandatory | Rhyme density throughout the bar |
| **Pop** | XAXA (conversational) | Low — near rhymes preferred | If it sounds "crafted," it fails |
| **Rock** | XAXA or ABAB | Low — meaning > rhyme | Imagery and energy over technique |
| **Punk** | AABB (loose) | Low — half-rhymes authentic | Shoutable at 150+ BPM |
| **Metal / Industrial** | Optional | Very low | Concrete imagery, riff alignment |
| **Country / Folk** | ABCB (ballad stanza) | Moderate | Lines 2 & 4 rhyme, 1 & 3 free |
| **Electronic / EDM / Synthwave** | Repetition > rhyme | Minimal | Single phrases looped |
| **Darkwave / Goth / Post-Punk** | XAXA or free | Low | Atmospheric, moody — meaning first |
| **Ambient / Lo-Fi** | None | None | Vocals are texture |
| **Trip-Hop** | XAXA (loose) | Low | Abstract, moody |
| **R&B / Soul** | Flexible | Low — emotion first | Space for melisma |
| **Ballad (any)** | ABCB or ABAB | Moderate | Emotion serves the story |

### Rhyme Quality Standards (Universal)

- **Forced rhymes** never acceptable
- **No self-rhymes**
- **No lazy repeats** (mind/mind, time/time)
- **Meaning over rhyme** — near rhyme > unnatural perfect rhyme
- **Consistency** — maintain chosen scheme through each section

### Common Anti-Patterns

- ❌ Wrong scheme for genre
- ❌ Filler lines to set up quotes
- ❌ Clichés: "cold as ice," "broke my heart," "by my side," "set me free"
- ❌ Telling instead of showing
- ❌ Generic abstractions when specificity serves better

---

## Song Length

### Default Target: 3:30–5:00 minutes

### Duration → Word Count

| Target Duration | Non-Hip-Hop | Hip-Hop |
|-----------------|-------------|---------|
| 2:00–2:30 | 120–180 | 200–300 |
| 2:30–3:30 | 150–250 | 250–400 |
| 3:30–5:00 | 220–400 | 400–600 |
| 5:00–7:00 | 350–500 | 550–750 |

### Word Count Targets by Genre (Suno)

| Genre | Duration | Word Count | Structure |
|-------|----------|------------|-----------|
| Electronic / Synthwave / Darkwave | 3:30–5:00 | 220–300 | 3V + pre-chorus + chorus + bridge + break |
| Pop / Synth-Pop | 3:30–4:30 | 250–350 | 2–3V + pre-chorus + chorus + bridge |
| Rock / Alt-Rock / Post-Punk | 3:30–5:00 | 250–400 | 2–3V + chorus + bridge |
| Goth / Post-Punk | 3:30–5:00 | 200–300 | 2–3V + chorus + bridge + atmospheric break |
| Hip-Hop / Rap | 3:30–5:00 | 400–600 | 3V + hook + bridge |
| Folk / Country | 3:30–5:00 | 250–400 | 3V + chorus + bridge |
| Ballad (any) | 3:30–5:00 | 200–300 | 2–3V + chorus + bridge |
| Punk | 2:30–3:30 | 150–250 | 2V + chorus + bridge |

### Structure Defaults

- **Default**: 2–3 verses + chorus + bridge
- **Chorus**: 4–6 lines, repeated verbatim
- **Bridge**: 2–4 lines
- **Pre-chorus**: 2–4 lines
- **Instrumental breaks**: Add ~20–40 seconds runtime each

### How to Hit Duration Targets

**Add more sections, not longer sections.**
- Add a 3rd verse
- Add a pre-chorus before each chorus
- Add an instrumental break
- Do NOT write 10-line verses or 8-line choruses

---

## Section Length Limits by Genre

### Electronic / Synthwave / Darkwave / Goth / Industrial

| Section | Max Lines | Notes |
|---------|-----------|-------|
| Verse | 4–6 | Vocals sparse — less is more |
| Chorus / Hook | 2–4 | Often a repeated phrase |
| Bridge | 2–4 | |
| Drop / Break | 0 | Use `[Drop]` or `[Synth Solo]` tag |

### Pop / Synth-Pop

| Section | Max Lines |
|---------|-----------|
| Verse | 6–8 |
| Chorus | 4–6 |
| Bridge | 4 |
| Pre-Chorus | 2–4 |

### Rock / Alt-Rock / Post-Punk / Indie

| Section | Max Lines |
|---------|-----------|
| Verse | 6–8 |
| Chorus | 4–6 |
| Bridge | 4 |

### Punk / Hardcore

| Section | Max Lines |
|---------|-----------|
| Verse | 4–6 |
| Chorus | 2–4 |
| Bridge | 2–4 |

### Metal / Industrial / Doom

| Section | Max Lines |
|---------|-----------|
| Verse | 4–8 |
| Chorus | 4–6 |
| Breakdown | 2–4 |

### Hip-Hop / Rap

| Section | Max Lines |
|---------|-----------|
| Verse | 8 |
| Hook | 4–6 |
| Bridge | 4–6 |

### Folk / Country / Singer-Songwriter

| Section | Max Lines |
|---------|-----------|
| Verse | 4–8 |
| Chorus | 4–6 |
| Bridge | 2–4 |

### Ambient / Trip-Hop / Lo-Fi

| Section | Max Lines |
|---------|-----------|
| Verse | 2–4 |
| Chorus | 2–4 |
| Bridge | 2 |

### Enforcement Rules

1. Count lines per section. Compare against table.
2. Exceeds max → trim. Cut weakest lines, keep hook and opening.
3. Any chorus over 6 lines → trim.
4. Electronic verse over 6 lines → cut.
5. Long sections cause Suno to rush, compress, or skip.

---

## Lyric Density & Pacing (Suno)

### Suno Verse Length Defaults

| Genre Family | Default Lines | Max Safe | Topics/Verse |
|---|---|---|---|
| Hip-Hop / Rap | 8 | 8 | 2-3 |
| Pop | 4 | 6-8 | 1-2 |
| Rock | 6 | 8 | 2 |
| Punk | 4 | 4 | 1 |
| Metal | 6-8 | 10 | 2-3 |
| Doom Metal | 4 | 6 | 1 |
| Electronic / Synthwave / Darkwave | 2-4 | 4 | 1 |
| Ambient | 0-2 | 4 | 1 |
| R&B / Soul | 6 | 8 | 1-2 |
| Singer-Songwriter | 6-8 | 8 | 2-3 |
| Progressive | 8-10 | 12 | 3-4 |

### BPM-Aware Limits (Universal Fallback)

| BPM Range | Max Lines/Verse | Topics | Feel |
|-----------|----------------|--------|------|
| < 80 | 4 | 1-2 | Slow, heavy |
| 80-94 | 4-6 | 1-2 | Laid back |
| 94-110 | 6 | 2-3 | Energetic |
| 110-140 | 6-8 | 2-3 | Standard |
| 140+ | 4 | 1 | Fast — short |

### Red Flags

- 8-line verse at BPM under 100
- Verse reads like a Wikipedia list
- "Laid back" concept with wall-to-wall syllables
- 3+ proper nouns in a single verse
- Every verse dense with no breathing room

---

## Line Length by Genre

| Genre | Syllables/Line | Tolerance |
|-------|----------------|-----------|
| Pop/Folk/Punk | 6-8 | ±2 |
| Rock/Indie/Goth | 8-10 | ±2 |
| Hip-Hop/Rap | 10-13+ | ±3 |
| Metal/Electronic | Varies | Flexible |

**Critical**: V1 line lengths must match V2 line lengths (±2 syllables).

---

## Refinement Pass Reference

### Pass 1: Tighten

| Pattern | Before | After | Why |
|---------|--------|-------|-----|
| Filler phrases | "He stood up and spoke the words" | "He said" | Padding |
| Redundant modifiers | "completely destroyed" | "destroyed" | Absolutes need no intensifiers |
| Passive voice | "The door was opened by her" | "She opened the door" | Active = singable |
| Double-saying | "alone and by myself" | "alone" | One expression per idea |
| Throat-clearing | "Well, I think that maybe" | Direct statement | Cut hedging |

### Pass 2: Strengthen

| Pattern | Before | After | Why |
|---------|--------|-------|-----|
| Generic imagery | "The city at night" | "Neon bleeding on wet asphalt" | Specific sticks |
| Abstract emotion | "I felt so lost" | "Couldn't find my keys, my name, my street" | Concrete |
| Clichés | "Cold as ice" | "Cold as a landlord's smile" | Fresh comparisons |
| Single-sense | "The room was dark" | "Dark — just the hum of pipes and mildew air" | Multi-sensory |
| Weak verbs | "He went across" | "He cut across" | Strong verbs |

### Pass 3: Flow & Ear

| Pattern | Before | After | Why |
|---------|--------|-------|-----|
| Consonant clusters | "Sixth street's strict structures" | "Sixth Street's sharp edges" | Tongue-trippers |
| Missing breath points | 12 syllables, no pause | Split at caesura | Singers need air |
| Stress misalignment | "into the DARK-ness" on weak beat | "the DARKness CALLS" on strong | Downbeat stress |
| Syllable mismatch | V1: 8, V2: 13 | Match within ±2 | Same melodic phrase |

---

## Part 3 — Generic Suno lyric pipeline: Phase 1 craft principles

*Adapted from suno-lyric-writer SKILL.md. These augment Part 2 (craft-reference) with the workflow-shaped principles that drive a draft.*

## Phase 1: Write Lyrics

### Input Gathering

If any of these are missing, ask before drafting:
- **Genre** (determines rhyme scheme, section limits, density)
- **Mood / Theme** (drives imagery, vocabulary, energy)
- **Target duration** (default: 3:30–5:00 → see craft-reference.md for word count mapping)
- **BPM** (determines max verse density — see craft-reference.md BPM table)
- **POV** (first/second/third person)
- **Concept album context?** (if yes: which track number, previous track themes for cross-referencing)

### Core Principles

#### Rhyme Craft
- Never rhyme a word with itself; no near-repeats (mind/mind, time/time)
- No lazy predictable pairs (fire/desire, moon/June, night/light)
- Use variety: perfect, slant, consonance, assonance, internal (see craft-reference.md)
- Meaning over rhyme — if a perfect rhyme sounds unnatural, use a near rhyme

#### Prosody (Syllable Stress)
- Stressed syllables land on downbeats (beats 1 and 3 in 4/4)
- Multi-syllable words need natural emphasis: DES-ti-ny, not des-TIN-y
- Content words (nouns, verbs) take emphasis, not function words (the, into, a)
- **Syllable balance**: V1 and V2 must match within ±2 syllables per line — drift causes timing collapse
- **Test**: Speak the lyric aloud. If emphasis feels wrong, rewrite it.

#### Show Don't Tell
- **ACTION**: `❌ "My heart is breaking"` → `✅ "She fell to her knees as he packed his bag"`
- **IMAGERY**: `❌ "I felt so sad"` → `✅ "Coffee gone cold on the counter"`
- **SENSORY DETAIL**: Engage multiple senses (sight, sound, smell, touch, taste, kinesthetic)
- **Section balance**: Verses = sensory details. Choruses = emotional statements.

#### Verse/Chorus Contrast

| Element | Verse | Chorus |
|---------|-------|--------|
| Lyrics | Observational, narrative | Emotional, universal |
| Energy | Building | Peak |
| Detail | Specific sensory | Abstract emotional |

#### No Verse-Chorus Echo
A verse must never repeat a key phrase, image, or rhyme word from the chorus it leads into.

#### Hook & Title
- Title in first or last line of chorus; give it rhythmic accent and melodic peak priority

#### V2 Must Develop (No Twin Verses)
V2 must advance the story, deepen emotion, or shift perspective — never rephrase V1.

### Section & Length Limits

Refer to **craft-reference.md** for genre-specific tables. Universal rules:
- **Max words**: 400 (non-hip-hop), 600 (hip-hop). Hard fail above.
- **Min words**: 200 for 3:30+ tracks.
- **Add more sections, not longer sections** to hit duration targets.
- Instrumental tags add ~20–40 seconds each.
- **Max lines per section**: 6–8 (v5 processes up to ~12 syllables/line cleanly)

### No Invented Contractions
Suno only handles standard contractions (they'd, he'd, wouldn't).
`❌ signal'd, TV'd` → `✅ "signal would", "TV could"`

### Refinement Passes

After drafting, run 1 pass (configurable 0–3):

| Pass | Focus | Goal |
|------|-------|------|
| 1 — Tighten | Cut filler, compress, remove redundancy | Every word earns its place |
| 2 — Strengthen | Upgrade weak imagery, sharpen sensory detail | Lines that stick |
| 3 — Flow & Ear | Read-aloud test, singability at BPM | Sounds right when sung |

---


---

## Part 4 — Generic 14-point lyric QC checklist

*Adapted from suno-lyric-writer SKILL.md Phase 3. Pairs with the project-specific 13-point audit in research-preferences.md — this one focuses on craft quality, that one on project DNA.*

## Phase 3: QC Review (14-Point Checklist)

| # | Check | Severity | What to Scan |
|---|-------|----------|-------------|
| 1 | **Rhyme** | ⚠ | Self-rhymes, repeated end words, lazy patterns |
| 2 | **Prosody** | ⚠ | Stress misalignment, inverted word order |
| 3 | **Pronunciation** | 🔴 | Homographs unresolved, proper nouns unphonetic |
| 4 | **POV/Tense** | ⚠ | Inconsistent pronouns or tense within section |
| 5 | **Structure** | ⚠ | Missing tags, twin verses, buried hook |
| 6 | **Flow** | ⚠ | Forced rhymes, inverted word order, filler |
| 7 | **Documentary** | 🔴 | Internal state claims, fabricated quotes (conditional) |
| 8 | **Factual** | 🔴 | Wrong dates/names/facts (conditional) |
| 9 | **Length** | 🔴 | Word count vs genre target |
| 10 | **Section length** | 🔴 | Lines per section vs genre max |
| 11 | **Rhyme scheme** | ⚠ | Scheme matches genre, no orphan lines |
| 12 | **Density/pacing** | 🔴 | Verse lines vs BPM-aware limits |
| 13 | **Verse-chorus echo** | ⚠ | Shared phrases/images across boundaries |
| 14 | **Artist names** | 🔴 | Real artist names in lyrics or style prompt |

### Severity & Report Format

| Level | Meaning | Action |
|-------|---------|--------|
| 🔴 Critical | Suno will fail or mispronounce | Must fix before generation |
| ⚠ Warning | Quality issue | Should fix, can proceed |

```markdown
## Lyric Review — [Track Title]
**Genre**: [genre] | **BPM**: [bpm] | **Words**: [count]
**Status**: ✅ Ready / ❌ Needs Fixes

### 🔴 Critical Issues
- [#3] V1:L2 — "lead" homograph, unresolved
### ⚠ Warnings
- [#1] V2:L2-L4 — self-rhyme "night/night"
### ✅ Auto-Fixed
- "FBI" → "F-B-I" (V2:L3)

### Ready-for-Suno Gate
- [ ] Zero critical issues  - [ ] All pronunciation notes applied
- [ ] No unresolved homographs  - [ ] Word count within genre target
```

---

---

## Part 5 — Before/after examples

*Adapted from suno-lyric-writer examples.md. Concrete transformations illustrating the principles above.*

# Lyric Writer Examples

Before/after transformations demonstrating key principles.

---

## Show Don't Tell

### Heartbreak

**Weak (tells):**
```
I was devastated when she left
My heart was broken, feeling bereft
I couldn't believe that she was gone
I felt so empty and alone
```

**Strong (shows):**
```
Found her coffee mug still in the sink
Poured it out but couldn't watch it drain
Her keys still hanging by the door
I keep forgetting she's not coming back
```
Concrete objects (mug, keys, door) and actions (poured, hanging, forgetting) let listeners feel the emotion.

### Anger

**Weak:** `I'm so angry at what you did`
**Strong:** `Threw your picture at the wall / Glass still scattered in the hall`

---

## Prosody (Syllable Stress)

### Multi-syllable Word

**Bad:** `I need to find my des-TIN-y` — wrong stress
**Fixed:** `My DES-ti-ny is CALL-ing me` — natural emphasis on downbeats

### Preposition Emphasis

**Bad:** `I walked IN-to THE room` — function words stressed
**Fixed:** `I WALKED in-to the ROOM` — content words stressed

---

## Twin Verses (V2 Must Develop)

### Narrative Song

**Bad V2 (twins V1):**
```
[V1] The streets are cold, I walk alone / No one around, just skin and bone
[V2] The roads are freezing, by myself / Empty sidewalks, no one else
```
V2 restates V1 with synonyms.

**Good V2 (develops):**
```
[V1] The streets are cold, I walk alone / No one around, just skin and bone
[V2] Found your old coat in the closet / Still smells like smoke and home
```
New detail, emotional shift, story advancement.

### Character Song

**Bad V2:** `He made a fortune, rose so high / The greatest man beneath the sky`
**Good V2:** `But late at night the ledgers showed / The debt behind the golden throne`

V2 introduces conflict and reveals what V1 was hiding.

---

## Verse-Chorus Echo

### Shared Hook Word

**Bad:**
```
[Verse] This is where it all got its START
[Chorus] Where it all got its START
```
"Start" in both — chorus loses impact.

**Fixed:**
```
[Verse] This is where we lit the spark
[Chorus] Where it all got its start
```
"Spark" sets up "start" without stealing it.

### Shared Imagery

**Bad:** "Warehouse" in both verse and chorus.
**Fixed:** Verse describes the space (echoes, dust, silence) without naming it; chorus reveals "This warehouse holds our memories."

---

## Filler Phrases

**Bad:**
```
And then he turned around and said to me
These words that I will not forget, you see
"The truth will set you free"
```

**Fixed:**
```
He turned and locked eyes with me
"The truth will set you free"
```
Direct setup, no padding.

---

## Forced Rhymes

### Inverted Word Order

**Bad:** `Into the night so dark I walked / Of all the things we never talked`
**Fixed:** `I walked into the darkest night / We never talked — that wasn't right`

### Forced Synonym

**Bad:** `She left me standing in the rain / My heart was filled with so much bane`
**Fixed:** `She left me standing in the rain / I don't think I'll be whole again`

---

## Too Vague vs. Too Specific

### Too Vague

**Bad:** `Everything changed that day / Nothing would be the same`
**Fixed:** `The phone lit up at 2 AM / Your voice cracked on the line / I sat down on the kitchen floor / The dog just licked my hand`

### Too Specific (Alienating)

**Bad:** `Remember when we saw Jen's cousin Mark / At the Walgreens on North Dearborn and Clark`
**Fixed:** `Remember running into him / At the drugstore, late that night`

---

## Rhyme Quality

### Self-Rhyme

**Bad:** `I gave you all my love / You threw away my love`
**Fixed:** `I gave you all my heart / You tore that love apart`

### Predictable Rhyme

**Bad:** `You set my heart on fire / Burning with desire`
**Fixed:** `You set my heart on fire / Now I'm just ash and bone`

---

## Density Mismatch

**Musical Direction**: "Slow groove, 75 BPM, laid-back feel"

**Bad (too dense):**
```
Running through the city streets at night, sirens blaring
Cops on every corner, helicopter in the air
Ducking through the alley, jumping fences, heart is pounding
```

**Fixed (matches tempo):**
```
Slow night in the city
Streetlights on the rain
Nothing but the echo
Of an empty train
```
Four short lines give the slow tempo room to breathe.
