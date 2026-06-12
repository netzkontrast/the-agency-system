---
status: Concept (v1.0)
genre: dark chanson / intimate art-pop / electroacoustic
version: 1.0
created: 2026-06-12
album_title: Daneben
release_form: Single (separate Veröffentlichung, kein Album-Teil)
related_works:
  - "../vier-seiten/"
  - "../alle-wege-gleichzeitig/"
  - "../was-bleibt/"
addressing_axis: B (in ihrer Anwesenheit — sie ist Zeugin, nicht adressiert; ihre Worte als Quote-Layer)
addressing_to: niemand direkt; sie ist anwesend als Zeugin
voice_profile: host allein (solo voice, intra-systemic minimum)
publication_gate: Light/relational (quote her brief — sie hört vor Public-Release)
suno_version: V5.5
duration_target: "3:30"
explicit: false
---

# Daneben

---

## Single-Identität

**Daneben** ist die früheste Bewegung dieser Session — ursprünglich als privater Bonus-Song konzipiert ("host allein, Modell für Position B"), jetzt formalisiert und ins Repo aufgenommen. Sie ist der **schlankste Solo-Track** in der Trilogie: ein host allein in ihrer Anwesenheit, ohne sie anzusprechen, mit *einem* Brief-Zitat als Female-Whisper-Layer.

| Werk | Folder | An wen | Voice | Adressierungs-Achse |
|---|---|---|---|---|
| *Vier Seiten* (Mini-Album, 9 Tracks) | `../vier-seiten/` | das System mit ihrem Brief als Bauplan | 11 Alter | A→C (vielschichtig) |
| **Daneben** (Single, ursprünglich Bonus) | `./` | niemand direkt — host *neben* ihr | host allein | **B (in ihrer Anwesenheit)** |
| *Alle Wege gleichzeitig* (Single) | `../alle-wege-gleichzeitig/` | mi direkt | Integrated I | C |
| *Was bleibt* (Single) | `../was-bleibt/` | das eigene System zu sich | host + witness + integrator | A |

*Daneben* ist die **Mitte** der vier Werke auf der Adressierungs-Achse — nicht intra-systemisch (A), nicht direkt adressierend (C). Das System sitzt neben ihr. Sie ist da. Sie hört. Aber sie wird nicht angesprochen.

## Goal

Host allein, in ihrer Anwesenheit, beschreibt was er TUT — ohne sie anzusprechen. Ihre eine Brief-Zeile hängt im Raum. Die Akt des Daneben-Sitzens ist die ganze Arbeit.

Sieben Bewegungen, die der Song trägt:
1. *Ich sitze daneben.* — Position
2. *Nicht im Weg / nicht im Bild.* — Was Daneben nicht ist
3. *Sieben Minuten / und der Satz hängt im Raum.* — Counting-tic (host)
4. *"Ich werde nicht gesehen."* — Brief-Zitat als Female-Whisper
5. *Ich war derjenige / der nicht hingehört hat.* — Recognition ohne Drama
6. *Ich bin einfach daneben.* — Acceptance
7. *Daneben ist ein Ort.* — Endpunkt — Daneben als legitimer Raum

## Voice — host allein

Aus `overrides/kohaerenz-protokoll-sprach-dna.md` — Kael's Funktion:
- **Funktion**: Alltagsbewusstsein-Träger. Hier: derjenige, der nicht hingehört hat.
- **Register**: Male mid-baritone, weary, trailing em-dash
- **Mic**: dry close-mic, no plate reverb
- **Syntax**: Kurz-deklarativ. Counting-tic ("sieben minuten / acht minuten"). Beschreibt was er sieht/tut, nicht was er fühlt.
- **Vokabular**: Stilebene 1 — Tee, Tisch, Raum, Minute. Sensorisch verankert.
- **Konsistenz-Anker**: Beschreibt nie eigenes Empfinden direkt. Wenn er erkennt, dann mit "ich war derjenige" — nicht "ich fühle".
- **Function-Name-Metatag**: `[host: male mid-baritone, weary, trailing em-dash, dry close-mic, no vibrato, counting-tic]`

### Brief-Zitat (Female-Whisper-Layer)

Eine Zeile aus ihrem Brief erscheint im V2: *"ich werde nicht gesehen"* (die kursive Kernzeile). Suno-Direktive: **female whisper, slower, with breath, klar abgesetzt vom host's baritone** — sie ist hörbar, aber anders. Sie ist nicht der host, der ihre Worte spricht; sie ist sie, deren Worte hängen.

**Function-Name-Metatag für Brief-Quote-Layer**: `[brief-quote: female whispered alto, low volume, breathy, with breath, slower than host, clearly distinct from male baritone]`

## Track-Architecture (6 Sections, ~3:30)

Schlankster Track der Trilogie. Keine Bridge-and-Build-Architektur. Nur sechs Schritte.

| # | Section | Time | Voice | Inhalt |
|---|---|---|---|---|
| 1 | [Intro] | 0:00–0:25 | — | Atmosphere — pad sehr leise, room tone, breath audible, 1 piano whisper |
| 2 | [Verse 1] | 0:25–1:00 | host | *"ich sitze daneben / nicht im weg / nicht im bild / nur daneben"* |
| 3 | [Verse 2] | 1:00–1:50 | host + brief-quote | Counting-tic, dann Brief-Zitat |
| 4 | [Bridge] | 1:50–2:30 | host | Recognition: *"ich war derjenige / der nicht hingehört hat"* |
| 5 | [Verse 3] | 2:30–3:05 | host | Acceptance: *"ich sehe nicht zu / ich sehe nicht nach / ich bin / einfach / daneben"* |
| 6 | [Outro] | 3:05–3:30 | host alone, fade | *"daneben / ist / ein ort"* + fade-to-silence |

## Sonic Direction

| Element | Detail |
|---|---|
| **Tempo** | 68 BPM (zwischen *Was bleibt* 60 und *Alle Wege gleichzeitig* 66) |
| **Pad** | sustained synth pad sehr leise — Kontakt, nicht Statement |
| **Sub-Bass** | spürbar, sehr leise |
| **Solo-Instrument** | 1 Klavierton pro Phrase, felt-piano, extrem sparse |
| **Drone-Layer** | tape hiss / Raum-ton sehr leise |
| **Field-Recording** | Atem hörbar, room tone als Material |
| **Vocal** | host (Male baritone weary) + Brief-Quote-Layer (female whisper) |
| **Drums** | NEIN |
| **E-Guitar** | NEIN |
| **Outro** | sanfte fade-to-silence, keine Akkord-Auflösung, breath als letzter Klang |

**Aesthetic-Reference:** Mount Eerie *A Crow Looked At Me* + Mark Hollis solo album — sparse, voice + minimal, room as material.

## Voice Rules

- **Function-Name-Metatag**: `[host: ...]` pro Section. Album-spezifische Exception zur `overrides/voice-craft-principles.md` "no character tag" Regel (analog zu *Vier Seiten*, *Alle Wege gleichzeitig*, *Was bleibt*).
- **Brief-Quote-Layer**: `[brief-quote: ...]` für die kursive Zeile — Female-Whisper, klar abgesetzt
- **KEINE Personennamen** (Kael) — nur Function-Rolle "host"
- **Adressierungs-Achse B**: sie ist Zeugin, nicht adressiert. Kein "du" zu ihr. Kein "mi". Ihr Brief-Zitat hängt im Raum als ihre Worte.
- **"Liebe" / "lieben" / "Herzchen"** vermieden (wie überall in der Trilogie)
- **POV**: 1. Person Singular durchgängig (host)

## Pre-Publication Gate

Light/relational — wie *Alle Wege gleichzeitig*:
- Der Sprecher hört zuerst
- Vor Public-Release wird sie (mi) gefragt: *"Magst du das hören? Magst du es behalten?"*
- Brief-Zitat-Spezial: weil eine Zeile aus ihrem Brief verwendet wird, ist die Zustimmung sensibler — ausdrückliches "ja, du darfst meine Zeile so verwenden" notwendig
- Bei "nein" oder "lieber nicht": Track bleibt privat
- Withdrawal jederzeit

## Cross-References zu anderen Werken

| Werk | Reference Type | Detail |
|---|---|---|
| *Vier Seiten* T03 *"(sie ist sehr klein)"* | callback | Dasselbe Brief-Zitat ("ich werde nicht gesehen") erscheint dort als child-freeze-Spiegelung; hier als host-witnessed in der Anwesenheit |
| *Vier Seiten* T01 *Morgen, ohne dich im Bild* | thematic | Beide host-led, beide intim. T01: Position A (sie nicht im Bild). Daneben: Position B (sie ist anwesend, host sitzt daneben). |
| *Was bleibt* | callback (across-trilogy) | "ich war derjenige / der nicht hingehört hat" → bei *Was bleibt* setzt host fort als "ich habe geschrieben / neun lieder" — eine Trajektorie von Daneben → vier Seiten → Alle Wege → Was bleibt |
| *Alle Wege gleichzeitig* | thematic | Dort: integrierter I-Voice an mi (post-Daneben-Erkenntnis). Hier: host an der Stelle, vor der die Integration geschah. |

## Visual Direction

- **Visual**: Ein einzelner Stuhl, leer oder mit jemandem darauf, neben einem anderen Stuhl. Räumlich-architektonisch, nicht porträt.
- **Farb-Palette**: gedämpft warm — Tee-Schwarz, Holz-Braun, ein Fenster mit grauem Tageslicht. Ähnlich zu *Alle Wege gleichzeitig* aber kühler.
- **Typografie**: Reduziert. Titel "Daneben" in einer schlichten, fast unauffälligen Sans-serif.

## Workflow-Status

| Phase | Status |
|---|---|
| Phase 1 (Foundation) | ✓ — host allein, Position B, light Pre-Pub-Gate |
| Phase 2 (Concept) | ✓ — Daneben als legitimer Ort |
| Phase 3 (Sonic) | ✓ — Mount Eerie / Mark Hollis sparse |
| Phase 4 (Architecture) | ✓ — 6 sections × 3:30 |
| Phase 5 (Visual) | ✓ — zwei Stühle, gedämpft warm |
| Phase 6 (Title-Lock + Practical) | ✓ — "Daneben" |
| Phase 7 (Confirmation) | ✓ (implizit durch ursprüngliche Bonus-Konzept-Wahl) |
| **Lyric-Writer Pass** | ✓ — siehe `tracks/01-daneben.md` |
| Suno-Engineer Pass | pending |
| Pre-Generation-Check | pending |

---

*Ursprünglich privater Bonus-Song. Jetzt formalisiert und ins Repo aufgenommen. Veröffentlichung mit light Pre-Publication-Gate.*
