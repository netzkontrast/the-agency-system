---
title: "Lass mich, lass mich atmen"
track_number: 1
instrumental: false
explicit: false
suno_url: ""
sheet_music:
  pdf: ""
  musicxml: ""
  midi: ""
---

# Lass mich, lass mich atmen

## Track Details

| Attribute | Detail |
|-----------|--------|
| **Track #** | 01 |
| **Title** | Lass mich, lass mich atmen |
| **Album** | [Lass mich, lass mich atmen](../README.md) |
| **Status** | In Progress |
| **Suno Link** | — |
| **Stems** | No |
| **Instrumental** | No |
| **Explicit** | No |
| **POV** | first-person (Survivor-Heute mit Damals-Echo) |
| **Role** | — |
| **Fade Out** | 5s |
| **Target Duration** | 3:00–3:45 |
| **Sources Verified** | N/A |

<!--
SOURCE VERIFICATION: Required for tracks with source material (quotes, real events, etc.)
- ❌ Pending = Sources added, awaiting human verification
- ✅ Verified (DATE) = Human has checked all URLs, quotes, dates, names
- N/A = Track has no external source material

Human must verify BEFORE track moves to production. See CLAUDE.md for verification workflow.
-->





## Concept

Standalone-Single. Wütende Forderung gegen eine erstickende Präsenz, die sich nicht eindeutig adressieren lässt — das **Du** ist polysemisch offen über vier isomorphe Lesarten: die Erinnerung, der wiederkehrende Traum, der innere Teil der jede Nacht weckt, und der Körper selbst (Atemwegsverengung). Jede Zeile trägt mindestens zwei dieser Lesarten gleichzeitig; keine darf den vermeintlichen Ursprung nennen.

Der Song schreit von der ersten Zeile an mit permanent knapper Luft und verbraucht im finalen Refrain seinen letzten Atem. Erst das gesprochene Outro holt die Luft zurück — als Eigentumsanspruch, nicht als Ankunft. „Ich schlafe" bleibt bewusst ausgespart, weil das gerade nicht erreichbar ist.

Verarbeitet biografisches Material. Konkrete Hintergrundinhalte sind nicht dokumentiert (`overrides/voice-craft-principles.md`); die Lyric trägt die abstrahierten Bilder. Das Bild des Kissens darf ambivalent gelesen werden: als das, was erstickt, *und* als das, auf dem versucht wird zu schlafen.

## Mood & Imagery

**Zentrale Bilder:**

- **Eine zweidimensionale gelbe Fläche** — flach, stumm, kein Rand. V1 als Bild der erstickenden Präsenz, V2 wiederkehrend „über mir".
- **Druck von allen Seiten** — die Erstickung kommt nicht nur von oben; sie umgreift. Korrektur der naiven Kissen-Vorstellung.
- **Das Kissen, ambivalent** — V2 setzt es einmal ein („das Kissen wird zu warm"). Dasselbe Objekt, das damals erstickte, ist heute das Bett-Kissen.
- **Hypnagoger Fall, der nicht aufhört** — Pre-Chorus nimmt den universellen Einschlaf-Schreck als Einstieg, fügt das persönliche Hell hinzu („nur dass es bleibt").
- **Luzider Traum ohne Entkommen** — strukturelle Klammer: bewusst, dass es nicht real ist, *und* kein Aufwachen-Können.
- **„Meine Luft"** — Eigentumsanspruch über die elementarste Ressource. Outro-Hook, Reclamation ohne Anspruch auf Auflösung.

**Atmosphäre:** Doomy, langsam, schwer. Keine Atempause, kein Erholungspunkt. Der Song gibt erst im gesprochenen Outro Luft frei — und auch dann nur sich selbst, nicht dem Hörer.

## Musical Direction

- **Tempo**: 100–110 BPM — schwer, doomy. Jeder Atemzug hängt länger in der Luft.
- **Feel**: Cyclisch — jeder Refrain ist gleich hart, kein graduelles Anschwellen. Permanente Atemknappheit ab V1. Bridge ist der einzige Bruch im Kreislauf.
- **Instrumentation**: Tiefer dub-Bass à la Jah Wobble (PiL) als Hauptträger, drohendes Gewicht im unteren Spektrum. Sparse post-punk drum kit, tribal/hypnotisch (Martin Hannett-Schule cavernous). Vereinzelte angular Guitar-Stabs mit flange/delay. Im Bridge: Beat-Drop, Sub-Bass hält, gefilterter Atem-Sample als Loop, dann hydraulische Industrial-Pulse-Eskalation bis zum Final-Chorus.
- **Vocal**: Male baritone tief, gravelly, kehlig. Animalisch-rau, Hals hörbar. Permanent knapper Atem. Inline-Doubling im Refrain: erstes „Lass mich" geflüstert/eingedrückt (Damals-Stimme), zweites „lass mich atmen" gebrüllt (Heute-Stimme).
- **Outro**: Gesprochen, exhausted, dry close-mic, [breath]-Marker vor jedem Satz. Musik fast komplett weg — nur Sub-Drone oder Stille.

<!-- SERVICE: suno -->
## Suno Inputs

### Style Box
*Copy this into Suno's "Style of Music" field:*

```
Male baritone deep gravelly kehlig, throat audible, animalistic raw, breathless intensity from line one, German vocals, voice forward, dry close-mic. Post-punk, gothic rock. 105 BPM, doomy, cavernous. Melodic dub-influenced deep bass leading harmony, threatening weight in low register. Sparse tribal post-punk drum kit, hypnotic pulse. Occasional angular guitar stabs with flange and delay. Bridge layer with filtered breath-sample loop and machine-pulse hydraulic build. Late-70s cavernous reverb-rich production with dub-style spaciousness. Dynamic range, restrained, contemporary.
```

**Suno V5 Settings:**

| Setting | Value |
|---|---|
| Model | V5 |
| Weirdness | ~35 |
| Style Influence | ~75 |
| Audio Influence | N/A (no reference audio) |
| Instrumental | Off (vocal track) |
| Persona | None |

### Exclude Styles
*Negative prompts — append to Style Box when pasting into Suno (e.g. "no drums, no electric guitar"):*

```
no autotune, no maximalist production, no sidechain pump
```

### Lyrics Box
*Copy this into Suno's "Lyrics" field:*

<!-- INSTRUMENTAL TRACKS: If instrumental: true, use only section tags (no sung lyrics).
     Example: [Intro]\n\n[Main Theme]\n\n[Bridge]\n\n[Outro]\n\n[End]
     Set "Instrumental: On" in Suno. -->

<!-- VOCAL TRACKS: WARNING: Suno sings EVERYTHING literally including parenthetical directions.
     NEVER use (whispered), (softly), (screaming), (spoken), (laughing), etc.
     Use metatags like [Whispered] or put delivery notes in the Style Box instead. -->

```
[Verse 1]
[male baritone deep, gravelly, kehlig, throat audible, breathless from line one, dry close-mic]

Etwas drückt von allen Seiten
gelb und flach — kein Rand
warm wie kein Trost — zu nah
näher als ein Gesicht je dürfte

[Pre-Chorus]
[same voice, fragmenting, hypnagogic panic, accelerating]

Ich fall. Ich fall.
Wie beim Einschlafen — nur dass es bleibt.
Es hört nicht auf.

[Chorus]
[full chest, animalistic raw scream, throat audible, breath thin]

[Whispered] Lass mich [Belted] lass mich atmen
geh runter, geh weg, geh aus
keine Frage. Kein Bitte.
Ich will den nächsten Zug Luft.

[Verse 2]
[same dark baritone, kehlig, breathless, slightly more frayed than V1]

Im Hals ein altes Geräusch
das Kissen wird zu warm
keine Worte, kein Bild, nur Druck
und über mir wieder das Gelb

[Pre-Chorus]
[fall sensation returning, dissociating into the room]

Ich fall. Ich fall.
Wie beim Einschlafen — nur dass es bleibt.
Ich bin hier — irgendwo.

[Chorus]
[same intensity as first chorus, no escalation, cyclic hardness]

[Whispered] Lass mich [Belted] lass mich atmen
geh runter, geh weg, geh aus
keine Frage. Kein Bitte.
Ich will den nächsten Zug Luft.

[Bridge]
[beat drops, drums out, sub-bass holds, filtered breath sample loops underneath, voice raw and unaccompanied, hydraulic industrial pulse builds across the section]

Ich will Nächte ohne dich
egal ob du Stimme bist
egal ob du Traum bist
egal ob du Erinnerung bist
egal ob du in meiner Brust hängst
raus aus mir. Raus.

[Chorus]
[everything returns with doubled weight, voice cracking, lungs nearly empty]

[Whispered] Lass mich [Belted] lass mich atmen
geh runter, geh weg, geh aus
keine Frage. Kein Bitte.
Ich will den nächsten Zug Luft —
lass mich. Lass mich.

[Outro]
[Spoken, exhausted, dry close-mic, near-whisper, music drops to minimal sub-drone or silence]

[breath] Meine Luft.
[breath] Sie gehört mir.
[breath] Ich atme.

[End]
```
<!-- /SERVICE: suno -->

<!-- VOCAL TRACKS ONLY: Remove this section for instrumental tracks -->

## Streaming Lyrics

*For distributor submission (Spotify, Apple Music, etc.). No section tags, repeats written out, plain text.*

```
Etwas drückt von allen Seiten
Gelb und flach, kein Rand
Warm wie kein Trost, zu nah
Näher als ein Gesicht je dürfte

Ich fall. Ich fall
Wie beim Einschlafen, nur dass es bleibt
Es hört nicht auf

Lass mich lass mich atmen
Geh runter, geh weg, geh aus
Keine Frage. Kein Bitte
Ich will den nächsten Zug Luft

Im Hals ein altes Geräusch
Das Kissen wird zu warm
Keine Worte, kein Bild, nur Druck
Und über mir wieder das Gelb

Ich fall. Ich fall
Wie beim Einschlafen, nur dass es bleibt
Ich bin hier, irgendwo

Lass mich lass mich atmen
Geh runter, geh weg, geh aus
Keine Frage. Kein Bitte
Ich will den nächsten Zug Luft

Ich will Nächte ohne dich
Egal ob du Stimme bist
Egal ob du Traum bist
Egal ob du Erinnerung bist
Egal ob du in meiner Brust hängst
Raus aus mir. Raus

Lass mich lass mich atmen
Geh runter, geh weg, geh aus
Keine Frage. Kein Bitte
Ich will den nächsten Zug Luft
Lass mich. Lass mich

Meine Luft
Sie gehört mir
Ich atme
```

<!-- END VOCAL ONLY -->

## Production Notes

- 100–110 BPM. Live-feel drum kit (post-punk sparse, nicht programmiert), tribal/hypnotisch.
- Dub-Bass tief und drohend (Jah Wobble / PiL-Schule), führt die Harmonie im unteren Spektrum. Macht den Raum eng statt melodisch.
- Vocal close-mic, dry, audibles Hals-Ringen erwünscht. Kein Reverb-Bad — die Trockenheit IST die Klaustrophobie.
- Bridge: Beat-Drop für 4–8 Takte, Atem-Sample-Loop layered (gefilterte Hauch-Texturen, kein Field-Recording-Klischee), dann hydraulischer Industrial-Pulse baut sich auf bis zum Final-Chorus.
- Final-Chorus: Stimme darf brechen. Letzte Zeile „lass mich. Lass mich." bewusst stimmlich am Ende der Lunge.
- Outro: Musik fast komplett raus, gesprochen über Sub-Drone oder Stille.
<!-- SERVICE: suno -->
- **Suno V5 Risiko-Notiz:** Inline [Whispered]/[Belted] Tags im Refrain sind die maximale Mechanik-Sichtbarkeit. Wenn Suno sie mitsingt statt als Direktive zu verstehen, im nächsten Run als Dynamic-Style-Anweisung in der Style-Box auslagern und im Refrain nur den Text lassen.
- **[breath]-Marker im Outro:** Suno V5 rendert das normalerweise als hörbare Einatmung. Wenn sie geschluckt werden, im Mastering ein echtes Inhalations-Sample vor jedem Satz manuell einfügen.
- **German vocals explizit** in der Style-Box — sonst kippt V5 in deutsch-akzentuiertes Englisch.
<!-- /SERVICE: suno -->

<!-- VOCAL TRACKS ONLY: Remove these sections for instrumental tracks -->

## Pronunciation Notes

**This table is a mandatory checklist, not passive documentation.** Every entry below MUST be applied as phonetic spelling in the Suno Lyrics Box. Before finalizing: read each row, search the Suno lyrics for the standard spelling, and confirm the phonetic version is used.

| Word/Phrase | Pronunciation | Reason |
|-------------|---------------|--------|
| — | — | Komplett deutscher Song; Style-Box muss „German vocals" explizit nennen. Keine phonetische Substitution in Suno-Lyrics nötig — Suno V5 trifft Deutsch korrekt, wenn die Sprache im Style-Prompt steht. Falls einzelne Wörter im ersten Run misslingen (z.B. „Geräusch", „dürfte", „Erinnerung"), per Track-spezifischer Phonetik in dieser Tabelle nachsteuern und in Suno-Lyrics substituieren. |

<!-- SERVICE: suno -->
## Phonetic Review Checklist

**Review before generating on Suno:**

- [x] **Proper nouns scanned**: keine im Track
- [x] **Foreign names**: keine — komplett deutsch
- [x] **Homographs checked**: keine deutschen Homographen in den Lyrics
- [x] **Acronyms**: keine
- [x] **Numbers**: keine
- [x] **Tech terms**: keine
- [x] **German vocals**: muss in Style-Box explizit stehen (sonst V5 → englischer Akzent)

**Proper nouns in this track:**
| Word | Current | Phonetic | Fixed? |
|------|---------|----------|--------|
| — | — | — | — |
<!-- /SERVICE: suno -->

<!-- END VOCAL ONLY -->

## Generation Log

Mark keepers with ✓ in the Rating column. Checkpoint verification looks for at least one ✓ per track.

| # | Date | Model | Result | Notes | Rating |
|---|------|-------|--------|-------|--------|
| — | — | — | — | — | — |

<!-- OPTIONAL: SoundCloud Waveform Art - Delete if not using this feature -->

## Waveform Art

### ChatGPT Prompt
*Use this prompt with ChatGPT/DALL-E to generate waveform background art (2480x800px):*

```
Generate a wide cinematic image at 2480x800 pixels for use as a SoundCloud waveform background.

[SCENE DESCRIPTION]

Style: [style keywords]
Color palette: [colors]
Mood: [mood keywords]

Important: The image will have an audio waveform overlaid on top, so avoid fine details in the center-middle area.
```

### Waveform Art Link
| Generated | Link |
|-----------|------|
| — | — |

<!-- END WAVEFORM ART -->
