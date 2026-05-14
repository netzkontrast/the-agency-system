<!--
Sources, top to bottom:
  1. https://github.com/netzkontrast/agency/blob/867453e/skills/the-agency-system-architect/sonic_branding.md
  2. https://github.com/netzkontrast/agency/blob/867453e/skills/the-agency-system-architect/suno_prompt_engineering.md
  3. https://github.com/netzkontrast/agency/blob/867453e/skills/suno-lyric-writer/genre-practices.md
Source commit: 867453e
Edit upstream and re-import, or edit here and document the divergence.
-->

# Suno Preferences

## Part 1 — The Agency System sonic DNA

*Sonic identity, vocal personas, and rhythm grid for the trilogy. These override generic Suno practices when they conflict.*

# Sonic Branding — The Agency System

Referenz für den **Sound Engineer**. Akustisches Gegenstück zur sprachlichen DNA.

---

## Genre-Fusion (Kern)

Primär: **Industrial-Darkwave**. Drumherum drei Texturen, nie mehr als eine pro Track dominant:

| Textur | Funktion | Beispiel-Cluster |
|---|---|---|
| **Minimal Techno** | Grid-Konsolidierung, Sisyphos-Puls | Optimization |
| **Dark Ambient / Dark Synth** | Skalen-Eindruck, Ehrfurcht vor der Agency | Onboarding, Meaning in the Mosaic |
| **Glitch-Hop / IDM** | System-Failure-Markierung | System Failure |
| **Post-Rock-Builds** | Katharsis ohne Auflösung | Systematic Agency (Chorus) |
| **Gothic Rock / EBM** | Verletzlichkeit mit Körper | Fragile Connections |

**Control by Reduction:** Ein Primärgenre + eine Supporting-Texture + ein Signature-Element. Alles darüber hinaus vermatscht das Latent-Modell.

---

## Timbrale Spannung

Jeder Track braucht das Paar:

- **Kalt / digital** (repräsentiert die Agency/das System): FM-Synthese, metallische Transients, quantisierte Hi-Hats, bit-crushed Texturen.
- **Warm / analog** (repräsentiert das Menschliche/den Exile): Moog-ähnliche Oszillatoren, driftende Pads, verarbeitete Field Recordings, unquantisierte Atmungen.

Die beiden dürfen nie verschmelzen. Sie **koexistieren geschichtet**.

---

## Rhythmus-Grid

- **Basis-Tempo:** 120 BPM. Dies ist Identität, keine Empfehlung.
- **Abweichung nach oben** (124-132): nur für System-Failure-Tracks mit Glitch-Dominanz.
- **Abweichung nach unten** (96-110): nur für reine Onboarding-Ambient-Tracks oder Fragile-Connections-Balladen.
- **Polyrhythmik:** IDM-Overlays auf dem 4/4-Grid, nicht gegen es. Die Rigidität des Grids ist der Gegenpol, den das Chaos braucht.

---

## Vokal-Persona

| Persona | Akustisches Merkmal | Zuordnung |
|---|---|---|
| **Agency-Voice** | Kalt, distanziert, oft verarbeitet (Vocoder leicht, Doubling tief + hoch) | Agency-Register |
| **Core / Manager** | Klar, analytisch, trockener Mix, männlicher Bariton | Kern-Register, Systematic Agency |
| **Exile** | Leiser, gewispert oder gesprochen, nach hinten gemischt | Lingering Echoes, System Failure |
| **Firefighter** | Härter, verzerrt, gedoppelt, vorn im Mix | System Failure |
| **Beobachter** | Gebrochen-klar, leichter Chorus, schwebend | Fragile Connections, Meaning in the Mosaic |

Pro Track: **maximal zwei Vokal-Personas**. Mehr zerfasert.

---

## GMIV-Template (Genre · Mood · Instruments · Vocals)

Der Engineer erzeugt einen **Style Prompt ≤ 110 Zeichen**. Bausteine:

### Genre-Slots (einer als Primary)
`industrial darkwave` · `minimal techno` · `glitch-hop idm` · `dark synth-pop` · `post-rock` · `gothic ebm` · `dark ambient`

### Mood-Slots (als Trajektorie formulieren)
- „clinical detachment → euphoric resolve“
- „somatic unease → grounded clarity“
- „compliance drill → glitch breach“
- „isolated longing → guarded warmth“
- „systemic drone → quiet integration“

### Instruments-Slots (3-5 konkret, keine Prosa)
`analog sub-bass` · `FM arpeggios` · `hydraulic percussion` · `typewriter hats` · `server-room drones` · `granular pads` · `bit-crushed leads` · `distant choir` · `industrial snare` · `modular bleeps`

### Vocals-Slots
`clear male baritone, dry mix` · `whispered male, reverb-heavy` · `doubled harsh male, distorted` · `cold processed female, FM-shaded` · `spoken word male, dry`

### Muster-Beispiele

**Optimization × Systematic Agency:**
`industrial darkwave, clinical→resolved, sub-bass, FM arps, typewriter hats, clear male baritone dry`

**System Failure × Polyphony of Self:**
`glitch-hop idm + dark synth, drill→breach, hydraulic perc, bit-crushed leads, doubled harsh male`

**Onboarding × Lingering Echoes:**
`dark ambient, detached unease, sub-drone, granular pads, distant choir, whispered male reverb`

---

## Sound-Design-Signaturen (wiederkehrend über das Album)

Drei „Office-als-Instrument“-Samples, die die Trilogie markieren:

1. **Typewriter-Cluster** — quantisierte Tastatur-Anschläge als Hi-Hat-Ersatz.
2. **Server-Drone** — tiefes Summen eines Rack-Kühlsystems als Sub-Layer.
3. **Handshake-Bell** — kurzes synthetisches Glöckchen bei Section-Übergängen (entspricht der „Signal Acquired“-Metapher).

Pro Album soll mindestens **eines** dieser Signatures in mindestens der Hälfte der Tracks vorkommen.

---

## Dynamik-Architektur

- **Verse:** klinisch, enge Transients, minimaler Reverb-Decay.
- **Pre-Chorus:** erste Störung (Tempo-Drag, Phasing, Filter-Sweep).
- **Chorus:** maximale Kompression ODER maximaler Raum — nie Mitte.
- **Bridge:** Glitch-Zone, Bruch des Grids.
- **Outro:** abrupter Stem-Cut + lingering Delay, oder Rückkehr zu Ambient.

Der Chorus ist **niemals** der laute Pop-Moment im Standard-Sinn. Er ist entweder Anthemic-Industrial-Saturation oder weite Leere.

---

## Part 2 — Agency-specific Suno prompt engineering

*Project-specific Suno tags, the 120-BPM declaration, and reduction rules. Read this before reaching for generic Suno syntax in Part 3.*

# Suno Prompt Engineering — Agency-spezifisch

Referenz für den **Sound Engineer**. Ergänzt `suno-lyric-writer` — dupliziert nicht.

**Grenze:** Was Suno-Syntax allgemein angeht (Section-Tags, Persona, Creative Sliders, Extend/Cover/Remaster), besitzt `suno-lyric-writer` die Autorität. Dieses Dokument liefert nur das, was für The Agency System **projekt-spezifisch** zusätzlich gilt.

---

## Control by Reduction (Agency-Anwendung)

Das allgemeine Prinzip kennt `suno-lyric-writer`. Agency-spezifische Regel:

**Ein Primärgenre + eine Supporting-Texture + ein Signature-Element. Nichts weiter im Style-Prompt.**

Falsch: `industrial darkwave, minimal techno, dark ambient, gothic rock, ebm, glitch-hop, cinematic synthwave`

Richtig: `industrial darkwave, sub-drone layer, typewriter percussion`

---

## 120-BPM-Deklaration

Das Grid wird **früh** deklariert — idealerweise direkt nach dem Genre im Style-Prompt **oder** als Tag im `[Intro]`:

```
[Intro — 120 bpm, industrial darkwave, typewriter percussion fade-in]
```

Bei Abweichung vom 120-Grid (siehe `sonic_branding.md`): Tempo explizit nennen, sonst drifft Suno nach 115.

---

## Agency-spezifische Compound-Tags

Tags, die im Projekt-Kontext semantisch belegt sind. Frei kombinierbar mit Standard-Suno-Syntax.

| Tag | Effekt im Projekt | Wann einsetzen |
|---|---|---|
| `[Agency Voice — cold processed, doubled octave]` | Agency-Register stimmlich trennen | Verses/Pre-Chorus im Agency-POV |
| `[Core Voice — clear male baritone, dry]` | Kern-Register markieren | Kern-Register-Verses und Chorus |
| `[Exile Voice — whispered, low mix]` | Exile-Teil einführen | Bridges in Lingering-Echoes-Tracks |
| `[Glitch Breach — bit-crush, polyrhythm, tempo instability]` | System-Failure-Markierung | Bridge in System-Failure-Tracks |
| `[Grid Lock — 120 bpm, 4/4, tight quantize]` | Systematic-Agency-Chorus setzen | Chorus in SA-Tracks |
| `[Handshake — synth bell, gate close]` | Section-Marker (Signatur) | Übergang Pre-Chorus→Chorus |
| `[Re-Init — stem cut, delay tail]` | Re-Initialization-Phase | Outro in Re-Init-Tracks |
| `[Server Drone — sub-hum enters]` | Ambient-Signatur | Intros in Onboarding-Tracks |

**Regel:** Pro Track maximal **drei** dieser projekt-spezifischen Tags. Kombination mit Standard-Suno-Tags unbegrenzt.

---

## Percussive Focus (Agency-Anwendung)

Der allgemeine Mechanismus kennt `suno-lyric-writer`. Agency-Spezifika:

- Percussive Focus wird **in Optimization-Phase-Tracks automatisch** gesetzt — die Drums tragen dort die Ideologie.
- In Lingering-Echoes-Tracks **niemals** Percussive Focus: die Stimme muss über der Unruhe liegen, nicht drin.
- In System-Failure-Bridges: Percussive Focus + Groove-Modifier für Polyrhythmik.

---

## Struktur-Skelett (Standard-Agency-Track)

```
[Intro — 120 bpm, <primary genre>, <signature element>]
(0:00 – 0:20)

[Verse 1 — <Voice Tag>, <Instrumentation>]
<4-8 Zeilen, Silbensymmetrie mit Verse 2>

[Pre-Chorus — <tension mechanism>]
<2-4 Zeilen, Metrik-Bruch erlaubt>

[Chorus — <Grid Lock ODER anthemic space>]
<4 Zeilen, eigenes Reimschema>

[Verse 2 — <Voice Tag>, <Instrumentation>]
<symmetrisch zu Verse 1>

[Bridge — <Breach oder Pause-Marker>]
<2-6 Zeilen, POV-Shift erlaubt>

[Chorus]
<Wiederholung, ggf. erweitert>

[Outro — <Re-Init oder ambient fade>]
<0-2 Zeilen>
```

Pro Album **mindestens ein Track** bricht dieses Skelett bewusst. Welcher, wird im Architect-Blueprint benannt.

---

## Was der Engineer **nicht** tut

- Keine Lyrics ändern. Falls Tags einen Text-Eingriff erfordern → REJECT zum Lyricist.
- Keine Persona-IDs setzen (das macht `suno-lyric-writer` in seiner Persona-Phase).
- Keine Creative Slider wählen (ebenfalls `suno-lyric-writer`).
- Keine Cover- oder Extend-Prompts formulieren. Dieser Skill arbeitet nur mit Custom-Mode-Basisprompts.

---

## Ausgabeformat

Exakt zwei Blöcke:

```
## Style Prompt
<genau eine Zeile, ≤ 110 Zeichen>

## Tagged Lyrics
<vollständige Lyrics mit allen Tags inline>
```

Kein Kommentar davor, dazwischen, danach.

---

## Part 3 — Generic Suno genre practices

*Adapted from suno-lyric-writer. Use for genres or workflows the Agency-specific layer is silent on.*


# Genre-Specific Suno Prompt Practices

Detailed prompting strategies for each major genre family.

---

## Darkwave / Synth Goth / Post-Punk

**Vocals**: Haunting, atmospheric, emotional — breathy or commanding
**Synths**: Analog warmth, dark pads, arpeggiators, bass-heavy
**Rhythm**: Drum machine, driving bass, 4-on-the-floor or post-punk grooves
**Production**: Dark, spacious reverb, 80s-influenced, atmospheric layers

**Example prompt:**
```
Female alto, haunting breathy vocals, emotional delivery. Darkwave, synth goth,
cold analog synths, driving bass, drum machine. Dark atmospheric production,
spacious reverb, 80s-influenced.
```

**Key instruments:**
- Analog synths (pads, arpeggios, leads), drum machine
- Deep bass (synth or post-punk bass guitar), reverb-drenched guitar
- Atmospheric layers, effects

---

## Electronic / Synthwave / EDM

**Vocals**: Often processed (reverb, delay, vocoder)
**Synths**: Describe texture (warm analog, cold digital, pad, lead)
**Rhythm**: Programmed drums, quantized or swing
**Production**: Layered, atmospheric, effects

**Example prompt:**
```
Female alto, ethereal, breathy vocals. Downtempo electronic,
warm analog synths, sub-bass, crisp programmed drums.
Atmospheric production, spacious reverb.
```

**Key instruments:**
- Synths (analog, digital, pads, leads)
- Programmed drums, sub-bass
- Layers, textures, effects

---

## Industrial / EBM

**Vocals**: Aggressive, distorted, spoken word, or cold/clinical
**Synths**: Harsh, grinding, metallic
**Rhythm**: Heavy mechanical percussion, sequenced
**Production**: Abrasive, compressed, raw

**Example prompt:**
```
Male baritone, aggressive distorted vocals. Industrial, EBM,
grinding synths, heavy mechanical drums, metallic textures.
Abrasive production, compressed.
```

---

## Hip-Hop

**Vocals**: Clear enunciation, rhythmic delivery, confident
**Beat**: Specific drum sounds (808 kick, crisp snare)
**Tempo**: 70–100 BPM laid-back, 100–140 energetic
**Production**: Vocal upfront, beat as foundation

**Example prompt:**
```
Male rapper, clear delivery, storytelling flow. Boom-bap hip-hop,
808 kick, vinyl crackle, dusty samples. Lo-fi production.
```

---

## Alternative Rock / Indie

**Vocals**: Passionate, dynamic (quiet verse / loud chorus)
**Guitars**: Specify clean vs distorted
**Energy**: Build from verse to chorus
**Production**: Live feel, room ambience

**Example prompt:**
```
Male baritone, emotional delivery, dynamic range. Alternative rock,
clean guitar in verses, distorted chorus, driving bass, tight drums.
Modern production with live energy.
```

---

## Folk / Indie Folk

**Vocals**: Conversational, intimate, natural
**Instruments**: Acoustic, organic
**Production**: Minimal, natural ambience

**Example prompt:**
```
Male tenor, intimate storytelling, conversational. Indie folk,
fingerpicked acoustic guitar, subtle upright bass, light brushed drums.
Natural room sound, minimal production.
```

---

## Trip-Hop

**Vocals**: Smoky, mysterious, processed
**Beat**: Sparse, downtempo, breakbeat-influenced
**Production**: Cinematic, dark, sample-heavy

**Example prompt:**
```
Female alto, smoky mysterious vocals. Trip-hop, sparse breakbeats,
deep sub-bass, vinyl crackle, cinematic strings. Dark atmospheric,
downtempo, 80-90 BPM.
```

---

## Ambient / Shoegaze

**Vocals**: Texture, not content — buried, ethereal, or absent
**Instruments**: Layers of reverb, delay, drones
**Production**: Washed-out, immersive

**Example prompt:**
```
Ethereal distant vocals, buried in reverb. Shoegaze, cascading guitars,
dense reverb, shimmering delay, dreamy atmosphere. Washed-out production.
```

---

## Production Direction Reference

### Mix Style

| Term | Effect |
|------|--------|
| Clean production | Polished, professional, clear separation |
| Lo-fi | Vintage, tape hiss, warm distortion |
| Raw | Unpolished, garage, live feel |
| Atmospheric | Spacious, reverb, ambient |
| Dark production | Moody, low-end heavy, shadows |

### Era/Vintage

| Descriptor | Effect |
|------------|--------|
| "80s production" | Gated reverb, synths, big drums |
| "90s grunge" | Raw, mid-heavy, distorted |
| "Modern pop" | Compressed, bright, wide stereo |
| "Vintage analog" | Warm, tape saturation |
| "Cold wave" | Minimal, icy synths, machine-like |

### Dynamic Range

| Descriptor | Effect |
|------------|--------|
| "Dynamic range" | Loud/soft variation (ballads, emotional arcs) |
| "Compressed" | Consistent volume (pop, radio) |
| "Punchy" | Impactful transients (rock, hip-hop) |
| "Cavernous" | Deep reverb, space, atmosphere |

---

## Artist Name Alternatives

**NEVER use real names — Suno blocks them.** Describe the sound:

| Don't Write | Write Instead |
|-------------|---------------|
| "Depeche Mode" | "dark synth-pop, brooding male vocals, analog synths" |
| "NIN / Trent Reznor" | "dark industrial, grinding synths, distorted vocals" |
| "Siouxsie and the Banshees" | "post-punk goth, commanding female vocals, jangly guitar" |
| "Sisters of Mercy" | "goth rock, deep baritone, drum machine, atmospheric" |
| "Massive Attack" | "trip-hop, dark atmospheric, sparse beats, cinematic" |
| "Portishead" | "trip-hop, smoky female vocals, vinyl crackle, cinematic" |
| "Bauhaus" | "goth rock, angular guitar, deep vocals, dub-influenced" |
| "Joy Division" | "post-punk, cold atmosphere, driving bass, sparse guitar" |
| "The Cure" | "gothic pop, shimmering guitar, reverb-heavy, melancholic" |
| "Cocteau Twins" | "dream pop, ethereal female vocals, cascading guitar, reverb" |
| "Skinny Puppy" | "dark industrial, harsh electronics, sample collage" |
| "Ministry" | "aggressive industrial rock, rapid-fire percussion" |
| "Gary Numan" | "cold synth-pop, robotic vocals, analog synths, dystopian" |
| "Johnny Cash" | "deep baritone, traditional country, train-beat rhythm" |
| "Carly Rae Jepsen" | "upbeat synth-pop, 80s-influenced, breathy female vocals" |
| "Radiohead" | "experimental art rock, falsetto, atmospheric guitar, electronic" |
