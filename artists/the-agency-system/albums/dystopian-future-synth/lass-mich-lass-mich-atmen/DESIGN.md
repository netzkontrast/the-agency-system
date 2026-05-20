---
title: "Lass mich, lass mich atmen — Album Design Spec"
date: 2026-05-20
status: v3.1 — panel review applied, pending final user sign-off
revision_history:
  - v3.0 (2026-05-20): initial draft from brainstorming
  - v3.1 (2026-05-20): 5-panel review applied (Lyric Craft / Sonic-Suno / Discography / Trauma-Authenticity / Polyphonic Coherence); user-locked 6 spec-architecture decisions (A–F)
artist: the-agency-system
release_type: full-length album, 13 tracks, polyphonic suite
working_slug: lass-mich-lass-mich-atmen
working_branch: claude/trauma-flashback-song-2BU7j
discography_position: Album 4 in the artist's arc; release-order position TBD — see §0
existing_v2_branch: claude/song-idea-breathing-an1Wr (different shape, kept as reference)
content_warning: Album re-confronts childhood sexual abuse at album length. Track 07 sustains a simultaneous Fighter-belt + Child-Freeze-scream peak; Tracks 03/05/09 give an introjected perpetrator-voice (carried by Sexualized-Override) verbatim quotation rights. CW must appear in album README front-matter before scaffolding.
---

# Lass mich, lass mich atmen — Album Design Spec

## 0. Position in the discography

The Agency System has built a deliberate three-album arc. This album is its fourth movement *in arc-order* — but **not chronologically a later event**. It is the **form that "Kern der Wahrheit" takes when expanded** into thirteen polyphonic movements; it is the *artistic-architectural shape* that the same truth-confrontation moment takes when held open across an album, rather than the artist's biography taking a new step.

In catalogue-release terms it may sit beside or after *Systematic Agency*; in narrative-arc terms it is the **sustained holding of the position** that *Kern der Wahrheit* named and *Autoren-Feder* gave permission to author. The album does not move the artist's biography forward from *Autoren-Feder*. It demonstrates what authoring the held truth can sound like at album length — that is the move.

| # | Album | Function in the arc | DNA-Songs cited in this spec |
|---|---|---|---|
| 1 | Together We Confide (Apr 2024) | **Witness** — surrender, the "perfect world" facade, the yellow void perceived as loss | "All Is Lost", "Perfect World" |
| 2 | Moment der Klarheit | **Descent & Confrontation** — bunker, finding the child, naming the abuse | "Vor der Konfrontation", "Kern der Wahrheit" |
| 3 | Systematic Agency | **Authorship** — taking the pen, narrative agency, the writer's hand still shaking | "Autoren-Feder" |
| 4 | **Lass mich, lass mich atmen** *(THIS)* | **Sustained Polyphonic Authorship — as form, not as new event** | The form that *Kern der Wahrheit* takes when expanded; the act of authorship that *Autoren-Feder* gave permission to. Same truth, thirteen polyphonic angles, the position held instead of resolved |

**Relationship to "What Lies Ahead":** That in-progress album (13 tracks, electroacoustic, deploys all eleven canonical alters of `the-eleven.md` as polyphonic worldview) is the artist's *parallel* polyphonic work. The distinction: WLA's track 12 ("all eleven at once") is a *worldview-frame* — alters speaking ABOUT the system. This album's polyphony is *intra-event* — alters speaking INSIDE a single sustained confrontation moment. WLA is mosaic; this album is fugue.

The album does not begin in the dark — it begins in the position that "Autoren-Feder" earned: **with the pen in hand, with the truth named, with the child still holding on**. From that position it walks through the yellow room thirteen times.

## 1. Album identity

| Attribute | Value |
|---|---|
| Artist | the-agency-system |
| Type | Full-length album, 13 tracks, **polyphonic suite** (cross-track motif inventory + heartbeat bookend connect the tracks; "one piece in 13 movements" was demoted to "suite" per Panel-5 honesty check — the album does not commit to attacca transitions, tonal centre, or recurring-fragment as structural devices) |
| Working title | "Lass mich, lass mich atmen" |
| Working slug | `lass-mich-lass-mich-atmen` |
| Genre folder | `dystopian-future-synth` |
| Genre tags | dystopian-future-synth (core), industrial-metal-elements, darkwave-pads, post-punk-elements, dark-ambient-closer |
| Frame | Fictional / artistic composite — `sources_verified: N/A` for all tracks (no documentary source gate). DNA from the artist's own released material is acknowledged in the spec but not "verified material" in the bitwize-music sense |
| Language | Deutsch primary; English at three precise moments where dissociation/foreign-voice/repertoire-direct-quotation demands it |
| Explicit | provisional `false` — abuse is named (per "Kern der Wahrheit" precedent: "Es war der Missbrauch"), but symbolic, not graphic. Re-check per track in pre-generation |
| Number of tracks | 13 |
| Repository layout decision | **Pending user sign-off**: replace existing v2 on `claude/song-idea-breathing-an1Wr` (same slug, old version archived in branch), or land parallel (e.g., suffix `-konfrontation` or different genre folder) |
| Distribution-tagging note | Surface streaming tags should use journalism-recognized labels (`darksynth`, `darkwave`, `post-punk`, `industrial`, `EBM`) per `overrides/genre-dystopian-future-synth.md` §1. The internal genre folder `dystopian-future-synth` is the artist-coined umbrella; do not surface that tag to listeners |
| Content warning | Childhood sexual abuse named at album length. Track 07 sustains simultaneous belt + scream peak. Tracks 03/05/09 give an introjected perpetrator-voice (Sexualized-Override carrying the Albtraum) verbatim quotation rights. CW required in README front-matter |

## 2. DNA sources (artist's own catalogue)

Four songs from the artist's released and in-progress material are treated as **canonical source layer**. The new album answers, echoes, and extends them.

### 2.1 "All Is Lost" — Together We Confide (Apr 2024)
**Function as DNA:** the surrender-position, the yellow void perceived as empty, the silent scream, the pillow on the face. The voice that says *"I surrender to the void, and let it set me free."*

**Key extracted phrases for cross-reference:**
- "Lost in a void where yellow particles dance around"
- "Each breath a struggle, like a pillow on my face"
- "world of flatness, where echoes have no sound"
- "Lost in the echo of my own silent scream"
- "All is lost, in this endless yellow void"
- "I surrender to the void, and let it set me free"

**Role in the new album:** the **Albtraum's seductive language**. The Albtraum quotes this song to lure. The new album's Collapsed One echoes it. Track 09 ("Don't Let It Stop") is the direct answer-track.

### 2.2 "Perfect World" — Together We Confide (Apr 2024)
**Function as DNA:** the family facade, the yellowed childhood pillow as sanctuary AND torture, the child's distant gaze, the "behind closed doors" abuse architecture, the longing-into-darkness.

**Key extracted phrases:**
- "Yellowed threads, a pillow worn thin" (twice)
- "a pillow's embrace"
- "My sanctuary, where the journey begins"
- "A child's gaze distant, lost in the haze"
- "Behind closed doors, love in masquerade"
- "a moment of fracture's strain / Where innocence shatters, a silent pain"
- "In the darkness, I long to stray"

**Role in the new album:** the **yellow is now historicized** — yellowed by years, by stains, by use; not abstract color. The pillow is a specific childhood object with double function. The Albtraum echoes "behind closed doors" to assert his historical claim on the silence.

### 2.3 "Vor der Konfrontation" — Moment der Klarheit
**Function as DNA:** the descent into the bunker of memory, finding the child, escorting her to the threshold of the yellow room. Ends at "Angekommen."

**Key extracted phrases:**
- "Tiefer im Bunker nun, durch Gänge kalt und grau"
- "Die Schuld sitzt tief im Nacken"
- "Vorbei an leeren Räumen, wo Schutz einst Trost versprach"
- "Ein Wimmern führt mich weiter, ganz leise, zart und schwach"
- "Da lebt der Tod! Er wartet! Voll gelbem Lärm und Schein!"
- "Ich nehm' dich an die Hand, komm mit in diese Welt"
- "Ein Funken Licht in mir gibt Kraft"
- "dein Griff hält mich ganz fest"
- "Der Eingang! Flackernd! Gelb! Ein schriller Alarm! Hellwach!"
- "Angekommen."

**Role in the new album:** the **pre-history**. Track 01 of the new album begins *immediately after* "Angekommen." The somatic state at the chorus of "Vor der Konfrontation" (Schläfen-Druck, Kehle zu, Herz an Rippen, Knie weich) is the inherited body state of Track 01. The Caregiver-Protector hybrid voice from this song becomes the "Ich" of the new album. Child-Freeze holds the hand throughout.

### 2.4 "Kern der Wahrheit" — Moment der Klarheit, follows "Vor der Konfrontation"
**Function as DNA: spine of the new album.** This song is the *seed* the album expands. Every truth named here is a truth the album sustains across 13 voices.

**Key extracted phrases:**
- "Hier drin! Der Lärm! Das Licht! Gelb! Grell! Zerreißt die Sicht!"
- "Dacht' an die Schuld, den Kampf in mir... / Doch das hier... anders... / Nicht meine Fehler... fremde Gewalt?"
- "Der Druck! Das Kissen! Auf dem Mund!"
- "Das Gelb! Die Leere! War NIE leer!"
- "Die alte Leere war NIE stumm!"
- "Es war der Missbrauch! WARUM?!"
- "Keine Erinnerung! Nichts gewusst!"
- "Doch bin selbst Eis! Steh auf der Stell'!"
- "Wir müssen hier... gemeinsam... raus? / Nein... durch! Fühlen! Auch wenn's brennt!"
- "Die Wahrheit... anerkannt... getrennt... / Von mir so lang... jetzt ist sie hier!"
- Outro: "Wahr... heit... ... Das war"

**Role in the new album:** every track is a polyphonic re-enactment of one beat from this song. The album is a 13-fold expansion of the realization-confrontation-truth-naming-not-out-but-through sequence.

### 2.5 "Autoren-Feder" — Systematic Agency (Album 3)
**Function as DNA:** the author-position. The artist takes the pen even when the hand still shakes. The trilogy's meta-statement: **the survivor authors the narrative now, not the trauma**.

**Key extracted phrases:**
- "Der Bunker kalt und modrig, der stumme Schrei des Endes" (returns to bunker imagery)
- "Du glaubst du schreibst die Story, Du bist doch nur die Schrift"
- "Nein! Dieses alte Skript sein Ende ist erreicht"
- "Ich nehm die Autoren-Feder selbst wenn die Hand noch bebt"
- "Kein Opfer mehr der Umstände kein Blatt im kalten Wind"
- "Ich schreibe meine Richtung bestimme neu mein Kind"
- "Weil Weglaufen nur stirbt weil nur die Wahrheit heilen kann"
- "Wir gehen mit dir zusammen... Du bist nicht mehr allein"
- "Narrative Agency die Kraft das Skript zu drehen"
- "Aus Ohnmacht wird Gestaltung aus Lähmung wird die Tat"
- "Die Tinte ist noch feucht / Der erste Satz gemacht / Der Weg beginnt / Jetzt"

**Role in the new album:** the **meta-position** of the artist. The new album is itself an act of authorship. It demonstrates that the truth-confrontation can be **held open for 13 movements** as a written, polyphonic work. The album's existence is the proof of "Aus Ohnmacht wird Gestaltung." The closing word of "Autoren-Feder" ("Jetzt") is the *opening permission* of this album.

## 3. Album thesis

**Sustained authorship as proof of "Aus Ohnmacht wird Gestaltung."** The album exists because the artist took the pen (in *Autoren-Feder*) and now writes the post-confrontation truth at album length. Its existence is the demonstration that authorship can hold the polyphonic truth without collapsing into one position — without surrender, without escape, without heroic resolution.

It is **not a new event in the artist's biography** — it is the *artistic-architectural form* that the realization "Es war der Missbrauch — durch! fühlen! — anerkannt, getrennt" takes when held open across 13 voices simultaneously, in suite-form, with all alters in dialogue with each other and with the introjected perpetrator-voice (the Albtraum) carried by Sexualized-Override.

The album refuses three escapes:

1. **It refuses surrender** ("All Is Lost"'s outro). When Collapsed One sings the surrender voice (Tracks 08, 09), the other voices stay.
2. **It refuses escape** ("Vor der Konfrontation"'s "raus?"). When the instinct to flee surfaces (Track 10), it is met with "Nein — durch."
3. **It refuses heroic resolution** (any "I won, the trauma is over" narrative). The closer ("Ich bin hier. Das war.") is not triumph; it is *staying*.

What the album does instead: it **stays inside the yellow room with all its voices present**, until the body, the child, the rage, the collapse, the witness, and the author each can speak the same truth in their own register, without erasing each other. This is the polyphonic position. This is what "Together We Confide" couldn't yet do (one voice surrendered), what "Kern der Wahrheit" started doing (multi-voice within one song), and what "Autoren-Feder" gave permission to do (taking the pen). The new album is the form that authorship takes when it sustains.

## 4. Voice architecture (album-wide)

**Eight canonical alters from `what-lies-ahead/the-eleven.md` carry the album**, plus the Albtraum entity (carried *by* Sexualized-Override — see below). Ur-Getier was deprecated per Panel-3 recommendation (non-canonical voice while subsetting The Eleven weakened continuity); Sexualized-Override was activated per user-decision D as the carrier of the Albtraum's voice — the DID-honest reading of "fremde Gewalt" / "behind closed doors" DNA.

| Voice | Canonical source | Album role | Fingerprint axes (syntax / punctuation / register cue) | Parenthesis discipline |
|---|---|---|---|---|
| **Ich** (Caregiver-Protector hybrid) | Composite — Caregiver warmth + Protector strategic vigilance, lineage from "Vor der Konfrontation" | Lead voice on most tracks; carries the album's authorial perspective | Hypotactic clauses with em-dash branching, declarative full-stops at line-end, "Ich + verb + concrete object", baritone Sprechgesang register | Never in parens |
| **Child-Freeze** | #7 in The Eleven — ~10–12, whispered head-voice, breath-audible | Hand-held companion to Ich on most tracks (held by hand from "Vor der Konfrontation" forward); **released to her own agency in Track 06** (sleeps in pillow); screams aloud in Track 07; finally speaks present-tense in Track 13 outro | Short paratactic fragments, ellipses + line-final breath, "ich..." with mid-line abandonment, never compound sentences | In parens when secondary; lead in Track 07 |
| **Fighter** | #6 in The Eleven — belt-alto + growl, kinetic rage holder | Hot rage; Track 07 co-lead with Child-Freeze; **parenthetical residue in Tracks 06, 08, 09** (no longer one-track cameo); fragmentary returns in Track 10 | Imperative single-clause sentences, exclamation point + caesura, monosyllabic verbs ("Schlag", "Reiß", "Tritt"), belt-alto register cue | Out of parens in Track 07; in parens otherwise |
| **Collapsed One** | #10 in The Eleven — deepest bass, sparse, near-spoken; carries the "All Is Lost" surrender voice | Lead in Tracks 08 and 09; **parenthetical residue in Tracks 03, 05, 11** to honor the "anti-arc voice always present, sometimes loud" reading; never granted final word | Long line-final pauses ("...lass...los..."), three-dot trailing, fewer than 5 syllables per spoken unit, sub-bass-near-spoken register cue | Same gender as Ich → in parens whenever not lead. **Track 08 blur mitigation:** Ich = dry close-mic baritone (no reverb tail), Collapsed = subkick-close-gravelly with 60 ms slap-back, register gap of perfect fifth+ enforced; line-final pause-length differs by 1.5× minimum |
| **Ambivalent** | #8 in The Eleven — microtonal alto, oscillating, approach/withdraw | Lead in Track 06 (now **the pillow-as-sanctuary track** in which Child-Freeze sleeps in the pillow); **parenthetical residue in Tracks 03, 10** before lead-track to seed her presence | Self-correcting clauses ("komm her — geh weg — komm her"), microtonal slide between sustained pitches, "vielleicht" / "oder" hedges, alto register cue | In parens when not lead |
| **Integrator** | #5 in The Eleven — mezzo-alto, ageless, spacious, the inner light from "Vor der Konfrontation"'s "Funken Licht in mir" | Lead in Track 11 (polyphonic peak); **parenthetical residue in Tracks 03, 08, 12** before/after lead-track; holds all voices simultaneously in T11 | Long sustained sung lines (no stops), commas instead of periods, "wir" instead of "ich", mezzo-alto ageless register cue | In parens when not lead |
| **Witness-of-Witnesses** | #11 in The Eleven — spoken-word, monotone, annotative | **Lead only in Track 12** (per user-decision F — cross-album annotation role dropped; one alter, one function). Spoken-word delivery throughout T12 | Nominal-style ("Sie atmet. Sie hat gekämpft. Das war Missbrauch."), no first-person, full-stop-per-line, androgynous spoken-word register cue | Outside the polyphonic field — no parens needed; appears only in T12 |
| **Sexualized-Override** (carries Albtraum) | #9 in The Eleven — adult ~30s low contralto, controlled/performative; the canonical perpetrator-introject alter | **IS the Albtraum's voice.** Speaks in Tracks 03, 05, 09; quotes "All Is Lost" verbatim in EN as luring language. Per user-decision D + Panel-4: explicit inclusion is the DID-honest reading of the Missbrauch material; honors the perpetrator-introject without flinch | Verbatim citation of "All Is Lost" lines ("yellow particles dance around" / "set me free" / "behind closed doors, love in masquerade"), low contralto register with alien-EQ processing, foreign-sounding reverb tail, controlled-performative cadence (no Sprechgesang) | Always in parens in DE-language tracks; outside parens only when delivering EN verbatim quotations in T05 lead-section |

**Not in this album** (deliberate exclusions, with named reasons):
- **Container** — the daytime mask is implied as *prior state*; the album begins after the mask was removed. Including him would re-enact rather than honor the descent
- **Rationalist** — reality-check during the polyphonic stay would interrupt the held position. The album refuses the "this is just a memory, it's 2026" rescue line
- **Caregiver-solo** — folded into the Ich-composite; her warmth is constitutive of Ich, not a separate speaker here
- **Ur-Getier** — non-canonical voice. Dropped per Panel-3: subsetting The Eleven while adding a non-canonical layer weakened the cast-logic. The somatic-trauma-presence is rendered through breath-markers and sub-bass drone instead of via a new alter

**Same-gender parenthesis rule applied throughout:** when two same-gender voices co-occur, one carries the line, the other parenthesizes. Cross-gender pairings (e.g. Ich-baritone + Child-Freeze-head-voice or Ich + Fighter-belt-alto) can use parens for craft (echo, doubling) but not for distinguishability — gender does that work.

**Through-line residue rule (Panel-5 implementation):** every alter that is a lead-voice on any track must have parenthetical residue on at least 2 adjacent tracks (one before, one after). This makes the polyphonic claim *real* rather than aspirational. Voice presence over the album is not casting-by-need.

## 5. Yellow protocol (album-wide)

The yellow is not abstract color. It is **the historical yellowing of an old object, weighted with stain, light, and noise**. Per the DNA:

- "Yellowed threads, a pillow worn thin" (Perfect World) → yellow as time-staining
- "Yellow particles dance around" (All Is Lost) → yellow as suspended dust, not surface
- "Voll gelbem Lärm und Schein" (Vor der Konfrontation) → yellow has sound (noise) and shine (light)
- "Das Gelb! Die Leere! War NIE leer!" (Kern der Wahrheit) → yellow is filled with abuser-presence, not empty

**Each track carries one yellow image:**

| # | Yellow image (per-track) |
|---|---|
| 01 | das gelbe Flackern am Eingang, schriller Alarm |
| 02 | gelbe Partikel zwischen Lippen und Kissen |
| 03 | das gelbe Pulver an der Wand, vergilbt |
| 04 | die alte Leere ist gelb, sie war nie leer |
| 05 | gelber Lärm, gelber Schein, der fremde Atem ist gelb |
| 06 | yellowed threads of the pillow — both embrace and mouth-gag |
| 07 | das Gelb zerreißt im Schrei |
| 08 | gelbes Pulver setzt sich auf die Augenlider |
| 09 | yellow particles dance around (Collapsed One quotes "All Is Lost") |
| 10 | gelber Sog zieht abwärts (raus-impuls / fluchtgelb) |
| 11 | gelb wird durchsichtig — alle Stimmen halten es gemeinsam |
| 12 | gelb in den Augen, aber draußen — anerkannt, getrennt |
| 13 | gelb wird gold — Morgen, Sonnenstaub |

## 6. Sonic core

### 6.1 Album-wide DNA layers (every track)
- **Yellow noise / HF-glitch** (from "gelbem Lärm" in Vor der Konfrontation) — a flickering high-frequency synth-noise layer present across all tracks, increases in density at confrontation moments
- **Heartbeat motif** (from Autoren-Feder's intro and outro) — appears at the album's opening, before silence, and in the closer; the album's pulse
- **[breath]-markers** (from existing v2-branch's voice-craft + Kern der Wahrheit's "Keine Luft! Ich kann nicht mehr!") — audible breath as percussive/structural element
- **Dystopian-future-synth pads** — the core sonic umbrella, dark synth-pad architecture (chorus-rich, reverb-soaked) connecting all tracks
- **Sub-bass drone** — continuous low-end presence, mehr gefühlt als gehört

### 6.1.1 DNA-layer density grid (per Panel-2 recommendation)

Density grid for each cross-track DNA layer per track. `lo` = barely audible / textural; `mid` = clearly present but not foregrounded; `hi` = foregrounded. Used by suno-engineer as a parameter rather than a vibe.

| # | Track | Yellow-noise | Heartbeat | [breath]-marker | DFS pads | Sub-bass drone |
|---|---|---|---|---|---|---|
| 01 | Eingetreten | lo→mid | **hi** (intro pulse) | mid | mid | mid |
| 02 | Lass mich, lass mich atmen | **hi** | lo | mid | **hi** | **hi** |
| 03 | Es war nie leer | mid | lo | mid | **hi** | mid |
| 04 | Nicht meine Fehler | mid | lo | lo | mid | mid |
| 05 | Fremde Gewalt | **hi** | lo | **hi** | **hi** | mid |
| 06 | Das Kissen auf dem Mund | lo | lo | mid | **hi** | **hi** |
| 07 | WARUM | **hi** | mid | mid | mid | **hi** |
| 08 | Auch ich bin Eis | mid | lo | mid | mid | **hi** |
| 09 | Don't Let It Stop | mid | lo | mid | mid | **hi** |
| 10 | Raus? | mid | lo | mid | mid | mid |
| 11 | Durch. Fühlen. | mid | lo | mid | **hi** | mid |
| 12 | Anerkannt, getrennt | lo | mid | mid | mid | **hi** |
| 13 | Ich bin hier / Das war | lo | **hi** (outro fade) | **hi** | **hi** | mid |

This grid is the unifying spine of the polyphonic-suite claim; if it isn't followed track-by-track, the suite reads as 13 unrelated tracks.

### 6.2 Per-track sonic palette (industrial-metal element distribution)

| # | Track | BPM | Industrial-Metal % | Other elements |
|---|---|---|---|---|
| 01 | Eingetreten | 60→90 ramp | low | heartbeat from Autoren-Feder, schriller Alarm, machine pulse build |
| 02 | Lass mich, lass mich atmen | 105 | **full** | downtuned distorted bass, concrete room drums, detuned guitar feedback stabs, metal clang hits, pulverizing repetition |
| 03 | Es war nie leer | 85 | low | synth-goth atmospheric, sleepwalking pulse, breath-led |
| 04 | Nicht meine Fehler | 95 | mid | post-punk bass line, cold synth lead, declamatory |
| 05 | Fremde Gewalt | 80 | low | foreign-sounding synth, alien EQ on Albtraum vocal, no drum kit |
| 06 | Das Kissen auf dem Mund | 70 | low | witch-house × darkwave, slow pulse, oscillating microtonal pad |
| 07 | WARUM | 115 | **full** | belt + scream, military-style drums, distortion-heavy synths, peak track |
| 08 | Auch ich bin Eis | 75 | mid | cooling industrial, bass drainage, glacial drift |
| 09 | Don't Let It Stop | 70 | mid | doom-leaning, sub-bass dominant, dark techno underpulse |
| 10 | Raus? | 90 | mid | post-punk × darkwave, propulsive but ambivalent, no resolution |
| 11 | Durch. Fühlen. | 100 | low | dense polyphonic synth layers, chorus-rich, all voices simultaneous, orchestral string layers (echo of Autoren-Feder bridge) |
| 12 | Anerkannt, getrennt | 65 | very low | dark-ambient × darkwave, sub-bass drone prominent, spoken-word delivery |
| 13 | Ich bin hier / Das war | 60 | none | ambient-drone × dream-pop, lush widescreen pads, breath-led, heartbeat fade |

**Production continuity** (carried forward from the existing v2-branch's design where it serves the new direction):
- Cyberpunk-synth pads as album leitmotif — prominent in 01/02/07, dense in bridge sections
- Darkwave-pads as cross-genre connective tissue
- No metal/industrial elements in Track 13 (closer) — earned silence

### 6.3 Vocal architecture
- **Ich** (Sprechgesang-Baritone): dry close-mic, throat-audible. Lineage from Autoren-Feder's "male vocal: Sprechgesang technique, slight throat distortion." Lead on Tracks 01, 02, 03, 04, 08, 10, 12, 13.
- **Child-Freeze** (whispered head-voice): ~10–12, breath-audible, fragile. Parenthetical echo on most tracks; lead in Track 07.
- **Fighter** (belt-alto + growl): Track 07 lead with Child-Freeze. Cracked tenor belt on the WARUM-scream.
- **Collapsed One** (deepest bass, near-spoken): Tracks 08, 09 lead. Echoes "All Is Lost" surrender language.
- **Ambivalent** (microtonal alto, oscillating): Track 06 lead. Holds approach/withdraw simultaneously.
- **Integrator** (ageless mezzo-alto): Track 11 lead. The voice that can hold all other voices in one room.
- **Witness-of-Witnesses** (spoken-word, androgynous, monotone): Track 12 lead. Annotative spoken-word delivery, no singing.
- **Albtraum / Tod** (carried by **Sexualized-Override**): low contralto with alien-EQ processing, foreign-sounding reverb, controlled-performative cadence. Speaks in Tracks 03, 05, 09 quoting "All Is Lost" verbatim in EN. Sonically separated from Ich (different gender register + alien processing); the perpetrator-introject's voice is structurally distinct from the survivor's voice
- ~~Ur-Getier~~ *(dropped per Panel-3; somatic-trauma-presence carried by breath-markers + sub-bass drone instead)*

## 7. Therapeutic position (album-wide)

The album holds the position named in "Kern der Wahrheit":

| Refused | Embraced |
|---|---|
| raus (escape) | durch (through) |
| surrender to the void | stay in the yellow |
| fight alone | feel with the others |
| triumph / cure | anerkannt + getrennt (acknowledged AND separated) |
| amnesia ("nichts gewusst") | sustained witnessing |
| forced integration | polyphony — voices distinct but together |

The closer "Ich bin hier. Das war." holds **present-tense self** + **past-tense truth** in the same breath. Not "I am healed" — *I am here. That happened.*

## 8. Tracklist (13 movements)

Each track is a polyphonic angle on the same sustained truth-confrontation moment. They are not sequential events in time but **vertical re-statements** in different registers.

### Track 01 — "Eingetreten"
- **Language**: DE
- **Lead**: Ich (Sprechgesang-Baritone)
- **Polyphony**: (Child-Freeze parenthetical, hand-held), heartbeat from Autoren-Feder, schriller Alarm from Vor-der-Konfrontation outro
- **Yellow**: das gelbe Flackern am Eingang, schriller Alarm
- **Sonic**: 60→90 BPM ramp, heartbeat + machine pulse build, dystopian-future-synth pads, low industrial; ends in the somatic peak inherited from "Vor der Konfrontation" chorus
- **Function**: continuity bridge from prior album. The door has been crossed. The body is in maximum activation. The album begins inside.

### Track 02 — "Lass mich, lass mich atmen"
- **Language**: DE
- **Lead**: Ich + (Child-Freeze parenthetical doubled refrain)
- **Polyphony**: (Albtraum/Sexualized-Override as ambient presence only — no verbatim quotation here; that arrives in T03)
- **Yellow**: gelbe Partikel zwischen Lippen und Kissen
- **Sonic**: 105 BPM, **full industrial-metal stack** — the album's loudest track. Title-track-anchor. Three simultaneous planes only (Ich main + Child paren + Albtraum ambient) per Panel-2 — Ur-Getier dropped to keep mix legible
- **Function**: the demand. Pillow on the mouth, in the dream. The doubled "Lass mich" — first the frozen Damals-utterance (Child-Freeze paren), second the angry Heute-utterance (Ich main).

### Track 03 — "Es war nie leer"
- **Language**: DE
- **Lead**: Ich
- **Polyphony**: **(Albtraum)** first speaks here — quoting "All Is Lost" in English parenthetically: "(through a veil I can't unsheathe)"
- **Yellow**: das gelbe Pulver an der Wand, vergilbt
- **Sonic**: 85 BPM, synth-goth atmospheric, sleepwalking pulse, breath-led, no drum kit
- **Function**: realization 1 — the void was filled. The Albtraum answers from inside the yellow.

### Track 04 — "Nicht meine Fehler"
- **Language**: DE
- **Lead**: Ich
- **Polyphony**: (Schuld-Stimme — a **temporary introject**, not a canonical alter; fingerprint: hypotactic clinical-clause syntax with em-dash self-correction, mid-line abandonment to render "abblätternd". Loses authority across the track until silent by the outro)
- **Yellow**: die alte Leere ist gelb, sie war nie leer
- **Sonic**: 95 BPM, post-punk bass line, cold synth lead, declamatory
- **Function**: realization 2 — the guilt the artist carried ("Schuld sitzt tief im Nacken" from Vor der Konfrontation) belongs to the abuser. Re-attribution. The Schuld-Stimme is structurally an introject that this track *processes out*; Ich's voice gains authority as Schuld loses it.

### Track 05 — "Fremde Gewalt"
- **Language**: DE primary, **EN Albtraum-lines parenthetical** quoting "All Is Lost"
- **Lead**: Ich
- **Polyphony**: **(Albtraum)** quotes "All Is Lost" verbatim — "(yellow particles dance around)" / "(let it set me free)" / "(behind closed doors, love in masquerade)"
- **Yellow**: gelber Lärm, gelber Schein, der fremde Atem ist gelb
- **Sonic**: 80 BPM, alien synth, foreign EQ, no drum kit, breath-noise prominent
- **Function**: realization 3 — naming the perpetrator-presence. The Albtraum's voice is the artist's own old surrender voice from 2024 — internalized perpetrator-mask. The track exposes the impersonation.

### Track 06 — "Das Kissen (sie schläft)" *(retitled per user-decision C — Child-Freeze agency-track)*
- **Language**: DE
- **Lead**: **Ambivalent** (microtonal alto, oscillating)
- **Polyphony**: **Child-Freeze sleeps in the pillow — she is NOT hand-held here. This is her only track without the adult-Ich's grip. She is fully absent as parenthetical companion; her presence is rendered only as a breath-marker layer (Panel-4 implementation of child-agency).** (Fighter paren residue establishing presence for T07 lead-track)
- **Yellow**: yellowed threads of the pillow — both embrace and not-mouth-gag (she is in the sanctuary-mode of the doubled object, not the weapon-mode). The Perfect World direct citation: "Yellowed threads, a pillow worn thin / My sanctuary, where the journey begins"
- **Sonic**: 70 BPM, witch-house × darkwave, slow pulse, oscillating microtonal pad, sub-bass-drone hi (cradle-like sub-bass), [breath]-marker as the child's audible sleep-breath
- **Function**: the **sanctuary-mode** of the pillow. The album's structural release-valve for Child-Freeze. Ambivalent holds the truth of the doubled object — *this same object was both her refuge and her weapon* — without resolving it. The child is allowed to sleep in the sanctuary-mode for one track; the weapon-mode is reserved for T07 (WARUM) where Fighter speaks her rage on her behalf. **This track refuses to re-stage the abuse from inside the child's perspective — she is allowed her sleep here.**

### Track 07 — "WARUM"
- **Language**: DE
- **Lead**: **Fighter** (belt-alto + growl) AND **Child-Freeze** (scream) — simultaneous peak per user-decision A
- **Polyphony**: (Ich grounding line, paren) acts as anchor; Fighter and Child-Freeze peak together at the chorus
- **Yellow**: das Gelb zerreißt im Schrei
- **Sonic**: 115 BPM, **full industrial-metal**, military drums, distortion-heavy. The album's emotional peak by intensity. **Mix-required track** per Panel-2 — primary Suno generation lead + 2 paren voices; child-scream layered as stem in mix-engineer if Suno can't render the simultaneity cleanly
- **Function**: the WARUM cry from "Kern der Wahrheit" sustained. Belt + child-scream simultaneous. No answer. The polyphonic peak by sound-pressure.
- **⚠ CONTENT WARNING (per Panel-4 + user-decision A)**: this track sustains a simultaneous adult-belt + child-scream peak; potentially re-traumatizing for both artist (during generation/listening) and listener (especially survivor-listeners). The album README must mark this track explicitly. Recommend a "skip" version in promo material that fades scream at peak rather than holding it

### Track 08 — "Auch ich bin Eis"
- **Language**: DE
- **Lead**: Ich + **Collapsed One** in dialogue (Ich without parens, Collapsed in parens)
- **Polyphony**: (Child-Freeze paren), Collapsed One paren echoing "All Is Lost"
- **Yellow**: gelbes Pulver setzt sich auf die Augenlider
- **Sonic**: 75 BPM, cooling industrial, bass drainage, glacial drift
- **Function**: the Heute-Ich also freezes, per "Kern der Wahrheit" Verse 2 ("Doch bin selbst Eis"). Collapsed One whispers surrender; Ich holds even while frozen.

### Track 09 — "Don't Let It Stop"
- **Language**: EN
- **Lead**: **Collapsed One** (deepest bass, near-spoken)
- **Polyphony**: (Ich refuses, paren in EN: "stay" / "not yet")
- **Yellow**: yellow particles dance around (Collapsed One quotes "All Is Lost" outro: "I surrender to the void, and let it set me free")
- **Sonic**: 70 BPM, doom-leaning, sub-bass dominant, dark techno underpulse
- **Function**: the **direct answer-track to "All Is Lost"**. The 2024 surrender voice gets the mic; the 2026 Ich refuses to let it close. The "set me free" line is uttered and *not answered with surrender* but with "stay."

### Track 10 — "Raus?"
- **Language**: DE
- **Lead**: **Fighter** (raus-impuls is her rage-energy) — no parens
- **Polyphony**: (Child-Freeze paren echoing the original "raus?" question from "Kern der Wahrheit"), Ich **withholds** (no paren echo, no line) — Ich's silence is the structural answer-to-come in Track 11
- **Yellow**: gelber Sog zieht abwärts (raus-impuls / fluchtgelb)
- **Sonic**: 90 BPM, post-punk × darkwave, propulsive but ambivalent, no chorus-resolution
- **Function**: the escape-instinct from "Kern der Wahrheit" bridge ("Wir müssen hier... gemeinsam... raus?"). The album holds the question without yet answering. Ich's silence here makes T11's "durch" land — Ich answers in the next track, not this one.

### Track 11 — "Durch. Fühlen."
- **Language**: DE
- **Lead**: **Integrator** (mezzo-alto, ageless)
- **Polyphony — engineered, not asserted (Panel-2/Panel-5 implementation):**
  - **Primary Suno generation:** Integrator lead + 2 paren voices only (Ich paren + Child-Freeze paren) — Suno can render this cleanly
  - **Mix-engineer stem layer:** Fighter, Collapsed One, Ambivalent added as separate stems via mix-engineer, mixed under Integrator's harmonic line
  - **Entry mechanics:** Integrator enters bar 1 alone; Ich joins bar 4 in paren; Child-Freeze joins bar 8 in paren; Fighter stem layered bar 12; Collapsed One stem layered bar 16; Ambivalent stem layered bar 20; all voices held through bar 28; voices exit in reverse-order over bars 28-32 leaving Integrator alone
  - **Harmonic distribution:** Integrator carries the melodic line; Ich + Child harmonize at fifth + octave above; Fighter holds the dissonant counter-line a tritone below; Collapsed One holds the sub-bass pedal; Ambivalent oscillates microtonally between Integrator and Fighter pitches
- **Yellow**: gelb wird durchsichtig — alle Stimmen halten es gemeinsam
- **Sonic**: 100 BPM, dense polyphonic synth layers, chorus-rich, orchestral string crescendo (echoing Autoren-Feder bridge architecture: "orchestral strings enter in layers / gradual crescendo over 16 bars")
- **Function**: **album center.** The polyphonic peak by complexity. The position from "Kern der Wahrheit" — "Nein... durch! Fühlen! Auch wenn's brennt!" — is held by all voices simultaneously. No voice dominates. This is what authorship-of-polyphony sounds like.
- **Mix-required track marker**: this track is the album's most production-intensive. Suno generates the primary polyphony; mix-engineer adds the additional stems. Document this in track scaffolding.

### Track 12 — "Anerkannt, getrennt"
- **Language**: DE
- **Lead**: **Witness-of-Witnesses** (spoken-word, monotone, annotative)
- **Polyphony**: (Ich confirms each line in paren)
- **Yellow**: gelb in den Augen, aber draußen — anerkannt, getrennt
- **Sonic**: 65 BPM, dark-ambient × darkwave, sub-bass drone prominent, near-silent percussion, spoken-word delivery
- **Function**: the separation. Witness annotates: "Sie atmet. Sie hat gekämpft. Das war Missbrauch. Es geschah. Es ist vorbei. Sie ist hier." Each line a fact. Each fact separates the past from the present. This is the line from "Kern der Wahrheit": "Die Wahrheit... anerkannt... getrennt... / Von mir so lang... jetzt ist sie hier!" — slowed to a spoken liturgy.

### Track 13 — "Ich bin hier / Das war"
- **Language**: DE
- **Lead**: Ich, with a heartbeat-paced approach (per Panel-1/3/5 expansion) before the final couplet; Child-Freeze speaks aloud in present-tense for the first time in the album near the end
- **Polyphony**: minimal — Child-Freeze speaks present-tense once near the close (her arc-completion: the silent-held child now speaks). All other voices have dispersed
- **Yellow**: gelb wird gold — Morgen, Sonnenstaub
- **Sonic**: 60 BPM, ambient-drone × dream-pop, lush widescreen pads, breath-led, heartbeat from Autoren-Feder fades over final 8 seconds (callback to Track 01 intro)
- **Lyric architecture (per Panel-1 expansion from 2-line under-build to heartbeat-paced approach):**
  - **Approach section** (~4-6 lines, slow heartbeat-paced):
    > Der Raum ist leer.
    > Das Kissen ist Stoff.
    > Mein Atem geht.
    > Mein Atem geht weiter.
    > *(Child-Freeze speaks aloud, present-tense, for the first time)*
    > (ich... ich bin... auch hier.)
  - **Final couplet:**
    > Ich bin hier.
    > Das war.
- **Function**: closer. Present-tense self + past-tense truth. Not triumph. Not closure. *Staying*. The heartbeat is the same heartbeat from Track 01's opening — the album loops in body-time but lands in language at the end. Child-Freeze's first present-tense utterance is her arc-completion: silently held throughout, she speaks at the end on her own (the agency-release seeded in T06's sleep returns here as voice). Final word: "Das war." — past-tense as the album's last word, refusing both *Together We Confide*'s "set me free" surrender-outro and *Perfect World*'s "illusion of the perfect world" outro.

## 9. Cross-track motif inventory

| Motif | First appearance | Recurs in | Function |
|---|---|---|---|
| Heartbeat (60 BPM) | Track 01 intro | Track 13 outro | bookends the album in body-time; callback to Autoren-Feder intro/outro |
| Yellow noise / HF-glitch | Track 01 | every track at varying density (see §6.1.1 grid) | the sonic body of the yellow |
| [breath]-marker | Track 01 | every track | the disputed resource |
| Pillow-thread imagery | Track 02 | Tracks 06, 09 | the central object |
| Doubled "Lass mich" | Track 02 refrain | Track 13 outro silence (refused repetition) | the demand and its eventual unnecessariness |
| schriller Alarm | Track 01 intro | Track 07 chorus | the threshold-marker |

**Intertextual citations (NOT internal motif inventory):** "All Is Lost"-verbatim phrases — particularly "set me free", "yellow particles dance around", "behind closed doors love in masquerade" — appear in Tracks 03, 05, 09 as **the Albtraum's quotations from a prior album the artist released**. These are *intertextual* (a citation device pointing to *Together We Confide*), not *motif* (a within-this-album recurring element). Distinction matters: the new album's motif spine is heartbeat/breath/yellow-noise/pillow-thread/schriller-Alarm; the quoted phrases are foreign material the Albtraum carries.

**Witness spoken-word delivery** appears only in Track 12 per user-decision F. The earlier "annotations across the album" plan was dropped — Witness has one function, one track. The album's recording-angel function lives in T12 alone.

## 10. Workflow chain (post-spec)

1. **User reviews this spec (v3.1)** — final sign-off required before scaffolding
2. **Decide repo layout** (replace v2 / parallel slug)
3. `/bitwize-music:new-album` — scaffold album directory (run requires `rebuild_state` first per MCP state)
4. `/bitwize-music:album-conceptualizer` — 7-phase deep-dive (Phase 7 is hard gate before lyric-writing)
5. Per-track loop:
   - `/bitwize-music:lyric-writer` (auto-invokes suno-engineer)
   - `/bitwize-music:pronunciation-specialist` (close-mic German, cracked tenor — homograph risk high)
   - `/bitwize-music:lyric-reviewer` (14-point QC)
   - `/bitwize-music:voice-checker` (advisory)
   - `/bitwize-music:pre-generation-check` (6 hard gates if invoked)
6. Suno generation, mix-engineer (per-stem polish — Tracks 07 and 11 marked as mix-required), mastering-engineer, release-director
7. Album-art-director — visual concept must hold yellow + threshold + polyphony

### 10.1 Mastering plan (per Panel-2)

Per-track LUFS targets (target spread caps at 8 LU due to ambient closer vs. industrial peak; unified album-mode mastering recommended):

| # | Track | Per-track LUFS | Mastering preset (from `overrides/mastering-presets.yaml`) |
|---|---|---|---|
| 01 | Eingetreten | -14 LUFS | dark-electro |
| 02 | Lass mich, lass mich atmen | -10 LUFS | industrial-darkwave |
| 03 | Es war nie leer | -14 LUFS | darkwave |
| 04 | Nicht meine Fehler | -13 LUFS | post-punk |
| 05 | Fremde Gewalt | -14 LUFS | dark-ambient leaning |
| 06 | Das Kissen (sie schläft) | -16 LUFS | witch-house |
| 07 | WARUM | -10 LUFS | industrial-darkwave |
| 08 | Auch ich bin Eis | -14 LUFS | dark-electro |
| 09 | Don't Let It Stop | -13 LUFS | doom-leaning darkwave |
| 10 | Raus? | -13 LUFS | post-punk |
| 11 | Durch. Fühlen. | -12 LUFS | darkwave (orchestral) |
| 12 | Anerkannt, getrennt | -17 LUFS | dark-ambient |
| 13 | Ich bin hier / Das war | -18 LUFS | ambient |

**Album-mode unified pass:** after per-track masters, apply a unified -13 LUFS album-mode pass to enforce shuffle-playlist coherence. Without this the 8 LU spread (Track 13's -18 vs. Tracks 02/07's -10) will alienate listeners who shuffle.

**Master-bus character:** tape and console saturation for glue rather than brick-wall limiting (per the territory's documented practice — see `overrides/genre-dystopian-future-synth.md` §7). True Peak ceiling -1 dBTP for sub--14 LUFS tracks, -2 dBTP for above--14 LUFS tracks (codec headroom).

## 11. Decisions locked (v3.1) + remaining open questions

### Decisions locked by user-sign-off (panel-question round, 2026-05-20)

| Q | Decision | Source |
|---|---|---|
| A — Track 07 sound-pressure | Keep simultaneous Fighter-belt + Child-Freeze-scream peak; add Content Warning in README front-matter | user-decision A |
| B — Albtraum verbatim quotation | Albtraum quotes "All Is Lost" verbatim in **all three** tracks (T03, T05, T09) — overrides Panel-1's "one-track-only" recommendation; user takes the intertextual-density risk consciously | user-decision B |
| C — Child-Freeze agency-track | Track 06 becomes Child's sleep moment — she sleeps in the pillow (sanctuary-mode) without hand-holding | user-decision C |
| D — Sexualized-Override | Activated: she IS the Albtraum's voice in T03/T05/T09; DID-honest reading of the perpetrator-introject material; CW required | user-decision D |
| E — Polyphony claim | Demoted "polyphonic single-piece" to "polyphonic suite" throughout — does not commit to attacca/tonal-centre/recurring-fragment structural devices | user-decision E |
| F — Witness-of-Witnesses role | Only Track 12 lead; cross-album annotation dropped — one alter, one function | user-decision F |
| Cast subset | 8 canonical alters + Albtraum (carried by Sexualized-Override). Ur-Getier dropped. Container, Rationalist, Caregiver-solo excluded with named reasons | spec §4 |

### Remaining open questions (require user input before scaffolding)

1. **Repo layout decision** (still open): replace existing v2-branch's `lass-mich-lass-mich-atmen` slug (same path, old version archived in branch — recoverable), or land parallel (e.g., suffix or alt genre folder)?
2. **Album title final**: "Lass mich, lass mich atmen" — keep (spec assumes keep), or shift to *"Durch"* / *"Das war"* / *"Anerkannt, getrennt"*?
3. **Release-order placement** (also still open): release this as Album 4 (after *Systematic Agency*), or as parallel side-album, or as expanded re-statement of *Moment der Klarheit*? Affects how the album is marketed and how the discography reads on streaming.

## 12. Files to create (informational — implementation plan will specify)

- `IDEAS.md` update — move "Lass mich, lass mich atmen" entry to In Progress with link to this spec
- `artists/the-agency-system/albums/dystopian-future-synth/lass-mich-lass-mich-atmen/README.md`
- `artists/the-agency-system/albums/dystopian-future-synth/lass-mich-lass-mich-atmen/RESEARCH.md` *(optional — DNA-song extracts could live here)*
- `artists/the-agency-system/albums/dystopian-future-synth/lass-mich-lass-mich-atmen/tracks/01-eingetreten.md` through `13-ich-bin-hier-das-war.md`
- `artists/the-agency-system/albums/dystopian-future-synth/lass-mich-lass-mich-atmen/the-cast.md` — voice-DNA documentation for the 7+ alters in this album

## 13. Status

**v3.1 — panel review applied; user-decisions A–F locked in §11; ready for user sign-off and album scaffolding.**

Three remaining open questions (§11): repo layout, album title final, release-order placement. These do not block scaffolding (the working slug + working title are sufficient); they will be re-confirmed at album-conceptualizer Phase 6.

Panel review (5 reviewers) ran 2026-05-20. Verdicts:
- Lyric Craft & Voice-DNA: needs revision → applied
- Sonic Architecture & Suno Producibility: needs sonic refinement → applied (DNA-layer density grid §6.1.1, mastering plan §10.1, Track 02 load reduced, Track 11 polyphony engineered)
- Discography Continuity: lands with reframing → applied (§0 reframed as form-of-Kern-der-Wahrheit, §3 thesis opens with sustained-authorship-as-proof, WLA-overlap distinguished in §0)
- Trauma-Authenticity: holds with risk → CW added in frontmatter and Track 07; Child-Freeze agency-track added (T06); Sexualized-Override exclusion replaced with named inclusion per user-decision D
- Polyphonic Coherence: polyphony partially delivered → through-line residue rule added §4; Track 11 entry/exit/yield engineered; Witness role simplified; Ich/Collapsed blur mitigation explicit in §4

Final sign-off requested.
