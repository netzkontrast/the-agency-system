# Video-Konzept — *Lass mich, lass mich atmen*

> **Status:** Entwurf v0.2 (2026-11-07) — wartet auf Bestätigung (Phase-7-Gate analog zum
> `album-conceptualizer`). Keine Produktion vor Bestätigung.
> **Pipeline:** [`Plan/140-video-domain/spec.md`](../../../../../Plan/140-video-domain/spec.md)
> **Engine:** `netzkontrast/ClaudeAnimationBase` — p5.js + p5.brush, flaches 2D, gemalte
> Pinselstriche, „kochende“ Tuschelinien (12 Zeichnungen/s), Papierkorn, Kamera, Licht
> per `glow()`, jedes Bild eine reine Funktion der Zeit, paralleles fortsetzbares Rendern
> in Headless Chrome. Regeln und Werkzeuge: `ANIMATION_GUIDE.md` im Engine-Repo.
> **Quellen-DNA:** `DESIGN.md` §5 (Gelb-Inventar), §6.1.1 (DNA-Dichte-Raster), §14 Phase 5
> (Album Art: Gelb + Schwelle + Polyphonie); `overrides/visual-language-guide.md`;
> `overrides/image-style-spec.md`.
>
> *v0.1 plante mit dem Path-Tracer aus `higgsfield-video-engineer` (20–43 s pro Bild). Das
> ist für Songs von 3–5 Minuten zu teuer und ästhetisch zu fotorealistisch. v0.2 wechselt
> auf ClaudeAnimationBase.*

---

## 0. Die eine Idee

**Ein Raum, dreizehn Zustände — gemalt.** Das Album ist eine Suite, keine Sammlung — also
ist auch das Video-Werk *ein* Ort: der gelbe, flache Raum hinter der Schwelle. Jeder Track
zeigt denselben Raum in einem anderen Zustand (Licht, Atem, Riss, Frost, Reparatur). Kein
Track erfindet einen neuen Ort.

Warum ClaudeAnimationBase so gut passt: Der Visual-Language-Guide verlangt *„Die Maschine
spricht in Vektoren, aber sie blutet in Tinte“* — Kohle, Graphit, Tusche, Aquarell auf
rauem Papier, zitternde Linien. Genau das ist das Medium des Kits:

| Visual-Language-Guide | ClaudeAnimationBase |
|---|---|
| analoger Strich, Papier als Körper | `paint()` / `inkLine()` mit p5.brush, `makePaper()`-Korn |
| Vector Jitter (zitternder Duktus) | Boil: Linien werden 12× pro Sekunde neu gezeichnet (`BOIL`, `jit()`) |
| Pigment-Verschmieren, Aquarell, das ausblutet | `fill` mit `bleed`, Wash-Ebenen |
| Kohle/Graphit-Felder, Schraffur | `hatch` mit Pinsel `charcoal` |
| Trauma-Gelb trifft Frostbite-Cyan → kränkliches Grün | p5.brush mischt wie Pigment: Gelb über Blau *wird* grün |
| Licht als eigene Kategorie | `glow()` — das einzige additive Element, liegt unter dem Papierkorn |
| flaches Bunker-Brutal, keine Perspektive | Regel 1: alles flach 2D, Tiefe nur durch Überlappung, Größe, Farbe |

Die Glitch-Grammatik wird als gemalte Fehler umgesetzt, nicht als digitaler Filter:
manueller RGB-Split (Tuschelinie schwarz, dazu versetzte rote und cyan Linien),
Block-Radierung (rechteckige Papier-Washes über der Zeichnung), Struktur-Erosion
(Linien brechen ab).

## 1. Harte Regeln

Die Regeln aus `ANIMATION_GUIDE.md` gelten (handgemacht, lebendig, ein Stück, kein Text,
Übergänge immer, in jeder Szene passiert etwas, Timing für den Zuschauer). Wo das Album
mehr verlangt, gilt zusätzlich:

1. **Nichts wird gezeigt, was der Song benennt.** Kein Kind in Gefahr, kein Täterkörper,
   keine Gewalt, keine Sexualisierung, keine Erstickungs-Darstellung an einer Figur. Die
   Wahrheit tragen *Objekte* (Kissen, Tür, Wand, Akte, Licht, Atem-Nebel), nie ein
   Körper.
2. **Kein Maskottchen, keine Figuren für Stimmen.** Clawd und das Figuren-Kapitel des
   Guides werden nicht verwendet. Die „Darsteller“ sind Objekte und Licht. Die
   Guide-Regeln *lebendig*, *Ursache → Reaktion* und *Antizipation* gelten für sie
   genauso: Die Tür zögert, bevor sie aufgeht; das Kissen atmet; der Lichtstreifen zuckt
   vor dem Alarm. Stimmen erscheinen als **Licht- und Schattenqualitäten** (Richtung,
   Temperatur, Härte, Puls). Polyphonie = mehrere Schattenebenen gleichzeitig.
3. **name_exposure:** Kein Personenname aus der Novel-Ebene in Bild, Dateinamen,
   Beschreibungen oder Prompts. Visuelle Anteile-Besetzung und Stimmen-Besetzung werden
   nicht vermischt.
4. **Kein Text (Guide-Regel 2) — mit einer Ausnahme.** Lyrics werden gespielt, nicht
   geschrieben. Einzige Ausnahme: T12 — die drei Kernsätze dürfen per `letter()` als
   Schreibmaschinenschrift auf der Akte erscheinen, jeweils einmal, und nur aus den
   Streaming Lyrics (nie aus der Suno-Lyrics-Box mit Phonetik).
5. **Lichtblitz-Sicherheit:** Alarm- und Flacker-Momente (T01-Intro, T07, Gelb-Flackern)
   müssen einen Blitz-Test bestehen (≤ 3 Blitze/s flächig; Rot-Sättigungsgrenze).
   Blocking-Gate in der QA. Achtung: `flash()` und das Boil-Flimmern auf großen gelben
   Flächen zählen mit.
6. **Content-Warnung** vor jedem Video als gemalte Tafel (2–3 s, ruhig, ohne
   Musik-Hit) und in jeder Plattform-Beschreibung. Für T03/T05/T07/T09 zusätzlich
   Altersbeschränkung auf YouTube prüfen. (Die Tafel ist die zweite erlaubte
   Text-Ausnahme.)
7. **Fürsorge im Prozess:** Reviews für T05 und T07 nur mit Pause/Grounding; ein Track pro
   Session.

## 2. Formate

Mit ClaudeAnimationBase ist ein volles Musikvideo für **jeden** Track realistisch. Die
Stufen aus v0.1 werden deshalb einfacher:

| Format | Was | Länge | Wofür |
|---|---|---|---|
| **Musikvideo** | voller Song, 16:9, 1920×1080, 24 fps | 3:00–5:30 | YouTube — alle 13 |
| **Canvas-Loop** | ein Moment als nahtloser Loop (`LOOPS` im Kit), 9:16 | 3–8 s | Spotify Canvas, Reels |
| **Teaser** | Ausschnitt aus dem Musikvideo, an Taktgrenzen geschnitten | 15–30 s | Release-Woche |

**Renderzeit:**

- *Gemessen* (hier im Cloud-Container, **ohne GPU**, Software-WebGL, 4 CPU-Kerne): ca. 26–32 s
  pro Bild beim Demo des Kits. Das ist der schlechteste Fall und nicht repräsentativ.
- Laut README hängen die Kosten vor allem an den Aquarell-Füllungen. Ohne dedizierte GPU
  rechnet man in Sekunden pro Bild, mit GPU deutlich schneller. Echte Zahlen kommen aus dem
  Pilot auf der Zielmaschine.
- Spar-Hebel: `onTwos()` (12 Zeichnungen/s) — jedes zweite Bild ist identisch und muss nur
  einmal gerendert werden. Dazu kommen parallele Worker (`--frames --workers=N`) und
  Aquarell-Füllungen nur dort, wo sie das Bild tragen.

## 3. Album-weite Bildsprache

| Album-Motiv (README) | Im Video | Treiber |
|---|---|---|
| Herzschlag 60 BPM (T01-Intro, T13-Outro) | `glow()` der Raumlampe pulsiert, Papier-Wash atmet mit | Beat-Raster aus `beatmap.json` |
| Gelb-Rauschen / HF-Glitch | gemalter RGB-Split, Block-Radierungen, abbrechende Linien | Hochton-Onsets, Dichte nach DESIGN §6.1.1 |
| [breath]-Marker | weicher Aquarell-Nebel dehnt sich aus und zieht sich zusammen | Atem-Zeitpunkte aus dem Lyrics-Timing |
| Kissen-Faden (T02, T06, T09) | dasselbe gemalte Kissen, vergilbter Faden als Tuschelinie | — |
| Doppeltes „Lass mich“ | Doppelschatten: zwei Lichtquellen, ein Objekt | Refrain-Takte |
| Schriller Alarm (T01, T07) | Signal-Gelb als harte Pastell-Linie durch Void-Black, blitz-getestet | Hits / Drop |
| Polyphonie | mehrere Schattenebenen an der Rückwand | Zahl gleichzeitiger Stimmen pro Abschnitt |

**Palette** (ersetzt `PAL` des Kits; Werte aus `image-style-spec.md`): Grund in
Papier/Kohle/Graphit, Tusche statt Schwarz. Gelb erscheint nur als Licht (`glow`) oder als
historisierte Objektfarbe:

- Corrupted Yellow `#8B8B00` — Gift, Starre
- Signal Yellow `#FFD700` — Alarm
- Clean Ping `#FCEE0C` — nur als winziger Lichtpunkt
- Kintsugi Gold `#FFDF00` — Reparaturnähte, erst ab T11

**Farbbogen über das Album** (Guide-Regel 7, „ein Stück“): T01–T05 schmutziges Ocker,
T07 Signal-Gelb auf Schwarz, T08 kaltes Gelb mit Cyan, ab T11 warmes Brückenlicht, T13
Morgengelb.

**Kontinuität:** Der Riss, der in T07 in die Papierwand geht, bleibt in T08–T10 sichtbar,
wird in T11 mit Kintsugi-Gold gefüllt und ist in T13 noch da — nicht verschwunden,
repariert. **T13 reimt sich auf T01** (Guide: „das Ende reimt sich auf den Anfang“):
derselbe Blick auf die Schwelle, derselbe Herzschlag. Aber die Tür steht offen, und es ist
Tag.

## 4. Track für Track (Treatment-Keime)

Jede Zeile ist ein Keim für den Treatment-Schritt. Zustand S0–S4 nach
`skills/theagencysystem/references/state-axis.md` ist ein Vorschlag.

| # | Track | BPM | Zustand | Kernbild / Endbild | Übergang hinein |
|---|---|---|---|---|---|
| 01 | Eingetreten | 60→90 | S2 → S1 | Gelber Lichtstreifen unter der Tür. Die Tür zögert und öffnet sich, die Kamera geht über die Schwelle. Der Herzschlag-Puls beschleunigt mit dem Tempo. Endbild: im Raum, Ecke im Schatten. | Aufblende aus Papier |
| 02 | Lass mich, lass mich atmen | 105 | S2 | Das Kissen formatfüllend, der Faden vergilbt. Der Atem-Nebel wird gestaucht, auf „atmen“ dehnt er sich gegen alles aus. Die Wände zittern auf der Kick. Doppelschatten im Refrain. | Match-Cut von der Ecke |
| 03 | Es war nie leer | 85 | S1 | Gelbe Partikel schweben wie 2024. Bei der Erkenntnis ordnen sie sich zu gesichtslosen Tusche-Umrissen. Fremdes Licht für die Introjekt-Stimme. | Iris aus einem Partikel |
| 04 | Nicht meine Fehler | 95 | S2 → S1 | Gekritzelte, unlesbare Schuld-Handschrift auf vergilbter Tapete. Pro Strophe reißt eine Bahn ab (gemalter Riss, Aquarell blutet). Am Ende kahle Wand. | Cut auf Aktion (Tapete reißt) |
| 05 | Fremde Gewalt | 80 | S1 | Licht von *außerhalb* des Raums, fremde Farbe. Schatten ohne zugehöriges Objekt. Kein Drum-Kit → fast keine Schnitte, eine lange Kamerafahrt. | langsame Blende |
| 06 | Das Kissen (sie schläft) | 70 | S0 | **Eine Einstellung, kein Schnitt.** Das eingedrückte Kissen, ruhiger Nebel, Nachtlicht. Niemand hält Wache. | Kamera trägt aus T05 hinüber |
| 07 | WARUM | 115 | S3 | Signal-Gelb, die Wände beben (`shakeXY`), das Papier reißt auf dem Drop. Zwei kollidierende Lichter (heiß/tief vs. kalt/hoch), Gelb-Blackout-Flackern. **Blitz-Gate.** | harter Smash-Cut (bewusst) |
| 08 | Auch ich bin Eis | 75 | S1 | Raureif wächst als Kohle-Schraffur über das Papier, kalte Wintersonne. Attacca aus T07: derselbe Riss, jetzt gefroren. | Match-Cut auf den Riss |
| 09 | Don't Let It Stop | 70 | S1 | Die endlose gelbe Leere von 2024 als Aquarell-Fläche. Die Kamera zoomt zurück, bis die Leere als Kasten im Raum erkennbar wird: als Falle benannt. | Wash aus Gelb |
| 10 | Raus? | 90 | S2 | Notausgang-Licht, Tür einen Spalt offen. Die Kamera schiebt sich zur Tür und geht **nicht** hindurch. Hauptlicht aus (das Ich schweigt). | Pinsel-Wipe |
| 11 | Durch. Fühlen. | 100 | S4 | Alle Lichtquellen gleichzeitig an, warmes Brückenlicht. Der Riss füllt sich mit Kintsugi-Gold. Polyphoner Höhepunkt = maximale Schattenebenen. | Licht flutet aus dem Türspalt |
| 12 | Anerkannt, getrennt | 65 | S4 | Eine vergilbte Akte. Die drei Kernsätze erscheinen per `letter()` als Schreibmaschinenschrift (Text-Ausnahme, §1.4). Die Akte schließt sich. | Iris auf die Akte |
| 13 | Ich bin hier / Das war | 60 | S4 → S0 | Gelblicht durch Vorhänge, Morgen. Herzschlag wie in T01, die Tür offen. Der reparierte Riss ist da. Einmal, kurz vor Schluss, ein einzelner Clean-Ping-Punkt. Stille am Ende. | Aufblende aus Papier (Reim auf T01) |

## 5. Gemeinsame Bibliothek (einmal bauen, 13× nutzen)

Gemalte Funktionen in `video/lib/*.js`, nach den Kit-Regeln: rein von `t` abhängig,
eigener `boilSeed` pro Element.

| Modul | Inhalt | Tracks |
|---|---|---|
| `room.js` | `room(t, state)` — Raum mit Rückwand-Zustand (heil, gerissen, gefroren, Kintsugi), Ecke, Vorhänge | alle |
| `threshold.js` | `door(t, angle)`, `lightStrip(t, k)` | 01, 10, 13 |
| `pillow.js` | `pillow(t, press, thread)` | 02, 06, 09 |
| `file.js` | `fileFolder(t, open)`, Schreibmaschinen-`letter()` | 12 |
| `breath.js` | `breath(t, density)` — Aquarell-Nebel mit Dichte-Kurve | alle |
| `particles.js` | gelbe Partikel → Umriss-Morph | 03, 09 |
| `wall-fx.js` | `tear()`, `frost()`, `kintsugi()` | 07, 08, 11, 13 |
| `glitch.js` | gemalter RGB-Split, Block-Radierung, Erosion | alle |
| `palette.js` | Album-`PAL` aus `image-style-spec.md` | alle |
| `beat.js` | `beatAt(t)`, `downbeat(n)`, `pulseMap(t)` aus `beatmap.json` (auch Tempo-Rampen wie T01) | alle |

## 6. Reihenfolge

1. **Dieses Konzept bestätigen** (oder überarbeiten).
2. **Pilot T02**, sobald die Suno-Generierung von T02 steht (sie ist ohnehin der erste
   Track). Zuerst nur die erste Strophe plus den ersten Refrain (~45 s). Der Pilot prüft
   den Look (Kohle/Tusche/Gelb), `beat.js` mit echter Bar-Map, die Renderzeit auf der
   Zielmaschine und den Review-Ablauf mit Contact Sheets.
3. Danach volle Länge T02, dann die übrigen Tracks in Album-Reihenfolge.

## 7. Offene Fragen

- Zielmaschine für das Rendern (Mac M-Serie? NVIDIA?). Hier im Cloud-Container gibt es
  keine GPU.
- 9:16 nur für Canvas-Loops — oder auch eigene Hochformat-Fassungen der Videos?
- Soll die CW-Tafel einheitlich für alle 13 gestaltet werden (empfohlen)?
