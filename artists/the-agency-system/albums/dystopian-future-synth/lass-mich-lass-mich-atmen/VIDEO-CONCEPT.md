# Video-Konzept — *Lass mich, lass mich atmen*

> **Status:** Entwurf v0.1 (2026-11-07) — wartet auf Bestätigung (Phase-7-Gate analog zum
> `album-conceptualizer`). Keine Produktion vor Bestätigung.
> **Pipeline:** [`Plan/140-video-domain/spec.md`](../../../../../Plan/140-video-domain/spec.md)
> **Engine:** `netzkontrast/higgsfield-video-engineer` (Skill `code-based-films`: eigener
> WebGPU-Path-Tracer, jedes Bild aus Code, generierte Bilder nur als Zielvorlage)
> **Quellen-DNA:** `DESIGN.md` §5 (Gelb-Inventar), §6.1.1 (DNA-Dichte-Raster), §14 Phase 5
> (Album Art: Gelb + Schwelle + Polyphonie); `overrides/visual-language-guide.md`;
> `overrides/image-style-spec.md`.

---

## 0. Die eine Idee

**Ein Raum, dreizehn Zustände.** Das Album ist eine Suite, keine Sammlung — also ist auch
das Video-Werk *ein* Set: der gelbe, flache Raum hinter der Schwelle, gebaut als
**Papier-/Karton-Diorama** im Miniaturmaßstab. Jeder Track zeigt denselben Raum in einem
anderen Zustand (Licht, Nebel, Material, Riss, Reparatur). Kein Track erfindet einen neuen
Ort.

Warum Papier: Der Visual-Language-Guide sagt *„Das Papier wird zum Körper; der Stift wird
zum Seismographen der Seele.“* Die Higgsfield-Engine kann genau das physikalisch:
`diffuseTransmission` (dünnes, durchleuchtetes Papier), Karton, Filz, Nebel- und
Emissions-Volumen, Tiefenschärfe auf Zentimeter-Sets. Die analoge Glitch-Grammatik
(manueller RGB-Split, Pigment-Verschmieren, zitternder Duktus, Struktur-Erosion) wird als
eigener 2D-Post-Pass in numpy geschrieben — ebenfalls eigener Code, kein Fremd-Asset.

## 1. Harte Regeln (zusätzlich zu den Engine-Regeln)

1. **Nichts wird gezeigt, was der Song benennt.** Kein Kind in Gefahr, kein Täterkörper,
   keine Gewalt, keine Sexualisierung, keine Erstickungs-Darstellung an einer Figur. Die
   Wahrheit trägt das *Objekt* (Kissen, Tür, Wand, Akte, Licht, Atem-Nebel), nie ein
   Körper. Das ist nicht nur Schutz — es ist die Poetik des Albums (Gelb als
   historisierte Objektfarbe).
2. **Keine Figuren für Stimmen.** Stimmen erscheinen als **Licht- und Schattenqualitäten**
   (Richtung, Temperatur, Härte, Puls), nie als Personen. Polyphonie = mehrere
   Schattenebenen gleichzeitig (Cover-Konzept §14 Phase 5).
3. **name_exposure:** Kein Personenname aus der Novel-Ebene in Titelkarten, Untertiteln,
   Beschreibungen, Dateinamen oder Prompts für Styleframes. Funktionsnamen nur intern.
   Die visuelle Anteile-Besetzung (Visual-Language-Guide) und die Stimmen-Besetzung
   werden **nicht** vermischt.
4. **Lyrics im Bild nur aus den Streaming Lyrics** (Standarddeutsch/-englisch), nie aus
   der Suno-Lyrics-Box mit Phonetik.
5. **Lichtblitz-Sicherheit:** Alarm- und Strobe-Momente (T01-Intro, T07, Gelb-Flackern)
   müssen einen Blitz-Test bestehen (≤ 3 Blitze/s, flächig; Rot-Sättigungsgrenze).
   Blocking-Gate in der QA.
6. **Content-Warnung** vor jedem Video als Texttafel (2–3 s, ruhig, ohne Musik-Hit) und
   in jeder Plattform-Beschreibung. Für T03/T05/T07/T09 zusätzlich Altersbeschränkung
   auf YouTube prüfen.
7. **Fürsorge im Prozess:** Review-Sessions für T07 und T05 nur mit Pause/Grounding;
   ein Durchlauf pro Session. Die Pipeline darf Reviews nicht „durchjagen“.

## 2. Formate (Stufen)

| Stufe | Was | Länge | Wofür | Tracks |
|---|---|---|---|---|
| **A — Loop/Canvas** | 1 Einstellung, nahtloser Loop, 9:16 | 3–8 s | Spotify Canvas, Reels-Loop | alle 13 |
| **B — Clip** | Higgsfield-Normalformat: Story in 4–8 Einstellungen, auf die Bar-Map geschnitten | 15–30 s | Teaser, Social, Release-Woche | alle 13 |
| **C — Musikvideo** | voller Song, 16:9 | 3:00–5:30 | YouTube | **T02, T07, T13** (die drei Eckpfeiler aus §14 Phase 5) |
| **V — Visualizer** | voller Song, 1–3 langsame Kamerafahrten + 2D-Post auf der Bar-Map | voller Song | YouTube „Official Visualizer“ | die übrigen 10, optional |

**Rechenbudget (Richtwert, Engine-README):** ~20 s pro Final-Frame auf einer RTX 4090,
~43 s auf einem M4 Max.

- Stufe B, 20 s × 24 fps = 480 Frames → ~2,7 GPU-h pro Track, ~35 GPU-h für 13.
- Stufe C, 4:00 × 24 fps = 5 760 Frames → ~32 GPU-h pro Track. **Deshalb Stufe C
  „auf Zweiern“ (12 Bilder/s, jedes Bild 2× gehalten):** halbiert das Budget *und*
  liefert den Stop-Motion-/Papier-Handgriff, den der Visual-Language-Guide will.
- Stufe V: wenige gerenderte „Plates“ mit langsamer Kamera bei 12 fps, Bewegung im
  Rest per 2D-Post (Atem-Nebel-Puls, Gelb-Rauschen, RGB-Split, Herzschlag-Licht als
  Belichtungs-Kurve).

## 3. Album-weite Bildsprache

| Album-Motiv (README) | Im Video | Treiber aus der Bar-Map |
|---|---|---|
| Herzschlag 60 BPM (T01-Intro, T13-Outro) | Lichtpuls der Raum-Hauptlampe, Belichtung ±0,3 EV | Beat-Raster bei 60 BPM |
| Gelb-Rauschen / HF-Glitch | 2D-Post: RGB-Versatz (Fineliner schwarz, Kugelschreiber rot/cyan), Block-Radierungen | Onsets im Hochton-Band, Dichte nach DESIGN §6.1.1 |
| [breath]-Marker | Nebelvolumen dehnt sich aus und zieht sich zusammen (Dichte-Kurve) | markierte Atem-Zeitpunkte aus dem Lyrics-Timing |
| Kissen-Faden (T02, T06, T09) | dasselbe Papierkissen-Asset, vergilbter Faden | — |
| Doppeltes „Lass mich“ | Doppelschatten: zwei Lichtquellen, ein Objekt | Refrain-Takte |
| Schriller Alarm (T01, T07) | Signal-Gelb `#FFD700` als harte Lichtkante, blitz-getestet | Hits / Drop |
| Polyphonie | mehrere Schattenebenen an der Rückwand | Anzahl gleichzeitiger Stimmen pro Abschnitt |

**Farbe** (aus `image-style-spec.md`): Grundstimmung Kohle/Graphit/Void-Black; Gelb
erscheint nur als Licht oder historisierte Objektfarbe — Corrupted Yellow `#8B8B00`
(Gift, Starre), Signal Yellow `#FFD700` (Alarm), Clean Ping `#FCEE0C` (nur als winziger
Lichtpunkt), Kintsugi Gold `#FFDF00` (Reparaturnähte, erst ab T11).

**Durchgehende Kontinuität:** Der Riss, der in T07 ins Papier der Rückwand geht, bleibt
in T08–T10 sichtbar, wird in T11 mit Kintsugi-Gold gefüllt und ist in T13 noch da —
nicht verschwunden, repariert. Das ist die visuelle Fassung von „anerkannt, getrennt“
statt Heilungsnarrativ.

## 4. Track für Track (Treatment-Keime)

Jede Zeile ist ein Keim für den `video-treatment`-Schritt, kein fertiges Treatment.
Zustand S0–S4 nach `skills/theagencysystem/references/state-axis.md` ist ein Vorschlag
und wird im Treatment bestätigt.

| # | Track | BPM | Raum-Zustand | Kernbild / Endbild | Stufe |
|---|---|---|---|---|---|
| 01 | Eingetreten | 60→90 | S2 → S1 | Gelber Lichtstreifen unter der Tür; die Kamera geht über die Schwelle. Herzschlag-Licht beschleunigt mit dem Tempo-Ramp. Endbild: im Raum, Ecke im Schatten. | B, V |
| 02 | Lass mich, lass mich atmen | 105 | S2 | Das Kissen formatfüllend, vergilbter Faden. Der Atem-Nebel wird gestaucht, auf „atmen“ dehnt er sich gegen alles aus. Kartonwände vibrieren auf der Kick. Doppelschatten im Refrain. | A, B, **C** |
| 03 | Es war nie leer | 85 | S1 | Gelbe Partikel (Emissions-Volumen) schweben wie 2024 — bei der Erkenntnis ordnen sie sich zu gesichtslosen Papier-Umrissen. Fremdes Licht für die Introjekt-Stimme. | A, B, V |
| 04 | Nicht meine Fehler | 95 | S2 → S1 | Schuld-Sätze als Handschrift auf vergilbter Tapete. Pro Strophe blättert eine Bahn ab (Papier-Sim), am Ende kahle Wand, eine Zeile übrig. | A, B, V |
| 05 | Fremde Gewalt | 80 | S1 | Licht von *außerhalb* des Raums, fremde Farbtemperatur. Schatten ohne zugehöriges Objekt. Kein Drum-Kit → fast keine Schnitte, eine lange Fahrt. | A, B, V |
| 06 | Das Kissen (sie schläft) | 70 | S0 | **Eine Einstellung, kein Schnitt.** Das eingedrückte Kissen, ruhiger Nebel, Nachtlicht. Niemand hält Wache. | A, B, V |
| 07 | WARUM | 115 | S3 | Signal-Gelb, die Wände beben, das Papier reißt auf dem Drop. Zwei kollidierende Lichter (heiß/tief vs. kalt/hoch), Gelb-Blackout-Flackern. **Blitz-Gate.** | A, B, **C** |
| 08 | Auch ich bin Eis | 75 | S1 | Raureif-Material wächst über Papier, kalte Wintersonne auf der flachen Wand. Langsam, attacca aus T07 (gleicher Riss, jetzt gefroren). | A, B, V |
| 09 | Don't Let It Stop | 70 | S1 | Die endlose gelbe Leere von 2024 als unendlicher Nebel — die Kamera fährt zurück, bis die Leere als Kasten im Raum erkennbar wird: als Falle benannt. | A, B, V |
| 10 | Raus? | 90 | S2 | Notausgang-Licht, Tür einen Spalt offen. Die Kamera schiebt sich zur Tür und geht **nicht** hindurch. Hauptlicht aus (das Ich schweigt). | A, B, V |
| 11 | Durch. Fühlen. | 100 | S4 | Alle Lichtquellen gleichzeitig an, warmes Brückenlicht. Der Riss aus T07 füllt sich mit Kintsugi-Gold. Polyphoner Höhepunkt = maximale Schattenebenen. | A, B, V |
| 12 | Anerkannt, getrennt | 65 | S4 | Eine vergilbte Akte. Die drei Kernsätze erscheinen als Schreibmaschinen-Typografie (Streaming Lyrics), die Akte schließt sich. | A, B, V |
| 13 | Ich bin hier / Das war | 60 | S4 → S0 | Gegenwart: Gelblicht durch Vorhänge, Morgen. Der Herzschlag-Puls wie in T01. Der reparierte Riss ist da. Einmal, kurz vor Schluss, ein einzelner Clean-Ping-Punkt (das Kind, jetzt in der Gegenwart). Stille am Ende. | A, B, **C** |

## 5. Gemeinsame Asset-Bibliothek (einmal bauen, 13× nutzen)

| Asset | Inhalt | Wird gebraucht in |
|---|---|---|
| `set/room` | flacher Raum aus Karton, Rückwand als austauschbares Papier (heil / gerissen / gefroren / Kintsugi) | alle |
| `set/threshold` | Türrahmen, Tür (Winkel als Parameter), Lichtspalt | 01, 10, Cover-Bezug |
| `prop/pillow` | Papier-/Stoffkissen, Eindruck als Parameter, vergilbter Faden | 02, 06, 09 |
| `prop/file` | Akte, Seiten, Schreibmaschinen-Typo | 12 |
| `fx/breath` | Nebelvolumen mit Dichte-Kurve | alle |
| `fx/particles` | gelbe Emissionspartikel → Umriss-Morph | 03, 09 |
| `fx/frost`, `fx/tear`, `fx/kintsugi` | Material-Zustände der Rückwand | 07, 08, 11, 13 |
| `post/analog-glitch` | numpy-Pass: RGB-Split, Block-Radierung, Zitter-Linie, Erosion | alle |
| `post/type` | Titel und Lyrics mit OFL-Schrift | 12, Titelkarten, CW-Tafel |

## 6. Reihenfolge

1. **Dieses Konzept bestätigen** (oder überarbeiten).
2. **Pilot T02, Stufe B (20 s).** T02 wird ohnehin zuerst auf Suno generiert
   (Persona-Kalibrierung). Der Pilot prüft Engine, Look, Papier-Material, Glitch-Post
   und Render-Zeiten auf der vorhandenen Hardware.
3. Danach entscheiden: Stufe C für T02/T07/T13, Stufe A+B für alle.

## 7. Offene Fragen

- Welche GPU steht lokal zur Verfügung (Mac M-Serie, NVIDIA)? Runpod ja/nein?
- 16:9 als Hauptformat für Stufe C, 9:16 nur für A — oder umgekehrt?
- Sollen Lyrics in Stufe C eingeblendet werden (Lyric-Video-Anteile) oder nur in T12?
- Credits/Titelkarte: welche OFL-Schrift (Hausschrift für das Album)?
