# Agency System Design Language Spec (ASDLS) — Full Normative Spec

> **Provenance.** Author-supplied normative spec for the Agency System visual
> language. This is the **executive rule-set** for all visual assets; it
> supersedes looser guidance where they conflict. The album's `SOURCE/ASDLS.md`
> and `SOURCE/asdls-design.md` remain valid summaries; this file is the full
> deterministic spec the art-director override (`overrides/album-art-preferences.md`)
> encodes for DALL-E. German source text preserved; English prompt vocabulary is
> copy-paste ready. **name_exposure:** role language only in any prompt — never a
> personal name.

## 1. Operative Grundphilosophie und Dokumentenarchitektur

Die Agency System Design Language Spec (ASDLS) fungiert als das fundamentale,
normative und exekutive Regelwerk für die Erstellung sämtlicher visueller Assets
innerhalb dieses spezifischen ästhetischen Ökosystems. Basierend auf den
Paradigmen des Spec-Driven Development (SDD) definiert dieses Dokument die
visuellen Parameter nicht als bloße ästhetische Richtlinien oder vage
Design-Philosophien, sondern als deterministische Zustandsmaschinen und
unmittelbar ausführbare Code-Äquivalente. In einer Produktionsumgebung, die
zunehmend von autonomen KI-Agenten und generativen Bild-Pipelines gesteuert
wird, dient die ASDLS als die alleinige "Single Source of Truth". Sie stellt
sicher, dass sowohl menschliche Designer und Illustratoren als auch autonome
KI-Agenten kohärente, deterministische und reproduzierbare Ergebnisse liefern,
die ohne manuelle Mikrokontrolle iteriert werden können.

Die Notwendigkeit einer solchen Spezifikation ergibt sich aus der Tatsache, dass
generative Modelle ohne strikte, strukturierte Parameter zu einem "Vibe-Coding"
tendieren, welches in generischen, inkonsistenten oder thematisch verfehlten
Outputs resultiert. Dieses Dokument eliminiert derartige Varianzen durch die
Etablierung eines maschinenlesbaren, semi-strukturierten Regelwerks, das
psychologische Zustände in exakte visuelle Variablen (Farbwerte,
Kompositionsachsen, Linsenverzerrungen) übersetzt. Jeder Satz, jede Tabelle und
jede Anweisung ist so formuliert, dass sie direkt als Parameter in einen
Bildgenerator-Prompt oder als konkrete Handlungsanweisung in ein
Illustratoren-Briefing überführt werden kann.

### 1.1 Interface Brutalismus und Klinische Dystopie

Die visuelle Identität operiert ausnahmslos im Spektrum eines zeitgenössischen,
post-2020 Cyberpunks. Sämtliche retro-futuristischen Elemente der 1980er-/1990er
(Synthwave-Gradienten Purple-Orange, Neon-Gitterlinien/80s Grid, VHS-Nostalgie,
bunte Blade-Runner-Kopien) sind **strikt untersagt**. Die Bildsprache wird
vollständig durch den **Interface Brutalismus** dominiert: digitale Roheit,
Entblößung algorithmischer Strukturen, funktionale Asymmetrie. Es ist eine
**klinische Dystopie** — absolute Kälte, monolithische Strukturen,
Corporate-Brutalismus, medizinische Distanz. Visuelle Artefakte und
Interface-Elemente sind **diagnostische Indikatoren von Systemzuständen**, keine
Dekoration. Das Design imitiert ein Kommandozeilen-Terminal oder einen
medizinischen Diagnosemonitor: rohe Datenströme ohne ästhetische Beschönigung.
Der Betrachter soll das Interface als überwältigend, gleichgültig und maschinell
präzise wahrnehmen — nicht als einladend.

### 1.2 Systemic Truth und die Priorisierungsmatrix

Absolute Entscheidungs-Hierarchie pro Bild. Ästhetik, Symmetrie und
konventionelle UX/UI ordnen sich der funktionalen, psychologischen
Zustandsdarstellung unter. Konflikte werden in dieser Reihenfolge gelöst:

1. **Emotionaler Systemzustand (Highest).** Die rohe emotionale Wahrheit des
   Moments (Kollaps, Latenz, Kontrolle) determiniert die Basisparameter — auch
   auf Kosten der Lesbarkeit.
2. **Klinische Syntax und Materialität.** Digitale Textur, Linienführung,
   Vermeidung analoger Artefakte. Stets wie ein digitaler Scan / Terminal-Output,
   nie wie eine Zeichnung.
3. **Semiotische Funktion und Motiv.** Charaktere / handlungstragende Ebene —
   zweitrangig gegenüber Raum (Vakuum) und Licht.
4. **Visueller Cache (Lowest).** Zufällige generative Artefakte nur zulässig,
   wenn sie Prioritäten 1–3 nicht verfälschen.

## 2. Farbsystematik, Emotionale Metriken und Chromatische Interaktionen

Radikal reduziertes Dark-Mode-Paradigma. Farben sind **funktionale Variablen**,
mathematisch an psychometrische Achsen gebunden — nie Dekoration.

### 2.1 Das Hintergrund-Paradigma (Das funktionale Vakuum)

Jedes Asset beginnt in totaler Dunkelheit. Die Leere repräsentiert Isolation,
Determinismus, ungenutzte Datenkapazität, die Tiefe des Mainframes.

- **Terminal Black — `#0B0D17`** (CMYK 85/75/50/80). Standard-Hintergrund aller
  aktiven/operativen Zustände; reflektiert kein Licht, schluckt Umgebung, lässt
  helle Vektoren mit maximaler Härte hervortreten.
  *Prompt (EN):* `inky dark background, abyssal terminal night, stark black void,
  clinical darkness, light-absorbing #0B0D17 surface`
- **Deep Charcoal / Latency Gray — `#1A1D24`** (CMYK 70/60/50/70). Interfaces,
  schwebende Fenster, monolithische Architektur; signalisiert Inaktivität/Latenz/
  Standby; wirkt wie rauer Beton oder mattes gebürstetes Metall, klaustrophobisch.
  *Prompt (EN):* `charcoal grey brutalist concrete, matte dark grey surfaces,
  monolithic unlit #1A1D24 structures, featureless grey tech-panels`

### 2.2 Das Hex-Typologie Paradigma (Aktions- und Zustandsfarben)

Farbe tritt **isoliert, stechend, extrem sparsam** auf: ~95 % Hintergrund, **max
5 %** ein bis zwei Zustandsfarben.

| Farbname | Hex | Zustand | Prompt-Vokabular (EN) |
|---|---|---|---|
| System Blue (Control) | `#003366` | Absolute Kontrolle, kühle Logik, Zwangsordnung, Firewall; Stabilität + emotionale Kälte | clinical agency blue, cold deep cyan, sterile surgical blue light, rigid neon blue illumination, medical interface blue |
| Corrupted Yellow | `#8B8B00` | System-Trauma, Freeze, Resignation, toxischer Datenverfall; vergilbtes Plastik / kranker Sektor | sickly yellow tint, corrupted mustard yellow, toxic decay glow, tainted dark ochre, jaundiced light |
| Signal Yellow (Alert) | `#FFD700` | Akute Gefahr, Warnung, Intrusion Detection, Panik; grell, aufdringlich | harsh neon yellow highlight, glaring warning yellow, piercing alert yellow, high-vis industrial yellow |
| Terminal Green | `#00FF9F` | Uncodiertes Rauschen, operationale Unruhe, rohe Datenströme; scharf & modern | phosphor terminal green, eerie matrix green, clinical oscilloscope green, toxic neon mint |
| Flame Orange | `#FF4500` | Destruktiver Kollaps, Wut, Systembruch, Kernel-Übersteuerung, thermal overload | blistering orange-red, destructive neon orange, searing thermal red, overheated system glow |
| Clean Ping (Hope) | `#FCEE0C` | Kurzer unbeschädigter Datenstrom, fragile Hoffnung, Unschuld; winziger Pixelpunkt / hauchdünne Linie | soft luminous pale yellow, fragile neon lemon, delicate warm light ping, isolated tiny yellow diode |
| Latency Violet | `#3B3355` | Dissoziation, schwindende Bandbreite, Identitätsverlust, Derealisation; verschwindet im Dunkel, keine klaren Kanten | desaturated deep violet, fading purple fog, detached muted magenta, ghostly lilac ambient light |
| Kintsugi Gold | `#FFDF00` | Reparatur-Algorithmus, Neusynthese, Erkenntnisdurchbruch; kein organisches Gold, präzise leuchtende Leiterbahnen | brilliant pure gold light, glowing metallic repair seams, luminous breakthrough yellow, precise golden circuitry |

### 2.3 Interaktionsregeln und chromatische Grammatik

- **Gesetz des Ausschlusses.** Flame Orange (Destruktion) und Clean Ping (fragile
  Hoffnung) schließen sich systemisch aus — **niemals im selben Rahmen**, außer
  ein Zustand überschreibt den anderen aktiv (als scharfer, fehlerhafter Glitch).
- **Visuelle Infektion durch Corrupted Yellow.** Tritt `#8B8B00` auf, müssen
  Nachbarfarben (System Blue, Latency Violet) entsättigt/getrübt/kränklich
  überlagert werden. *Prompt:* `desaturated neighboring colors caused by toxic
  yellow light spill`.
- **Isolations-Kontrast (The 5% Rule).** Für Alarm-/Hoffnungszustände: exakt 95 %
  Terminal Black / Monochrom-Grau, exakt **5 %** reine Signal-Farbe. Übergang
  **extrem scharfkantig (Hard-Edge)**, nicht durch Ambient Occlusion aufgeweicht.
- **Verbot von Gradienten.** Keine weichen Farbverläufe. Systemfarben treffen in
  harten Kanten, blockigen Pixelverschiebungen oder getrennten Terminal-Fenstern
  aufeinander.

## 3. Digitale Materialität, Linienqualität und Klinische Texturen

Keine Romantik. Analoge Qualitäten (Papiertextur, Bleistift, Pinselduktus,
Aquarell, organische Unregelmäßigkeit) sind **vollständig entfernt**.
Materialität ist 100 % digital, synthetisch, technologisch, medizintechnisch.

### 3.1 Vektor-Fragmentierung und Packet Loss

Linien repräsentieren den Zustand der **Datenübertragung**, nicht physische
Kanten.

- **Low Bandwidth (Latenz/Dissoziation):** Konturen dünn, semi-transparent,
  brechen mittig ab ("Packet Loss"). *Prompt:* `fading vector lines, dropped
  packets visual effect, ghostly thin contours, low opacity wireframes,
  disconnected blueprint lines, incomplete rendering`.
- **High Bandwidth (Overload/Schmerz):** Linien verdichten sich zu schwarzen
  Code-Schraffuren, fehlerhafte Überlagerung, Jitter, aggressive Nester aus
  Datenmüll. *Prompt:* `chaotic vector overlapping, high density wireframe mesh,
  aggressive digital hatching, terminal code stacking, hyper-detailed schematic
  overload`.

### 3.2 Die Oberfläche: Glitch als klinische Sprache (Diagnostik, nicht Dekoration)

Glitch = **diagnostisches Werkzeug** für Speicherkorruption / Kollaps / Einbruch
verdrängter Routinen, nie retro-Deko.

- **Chromatische Aberration (RGB-Splitting):** nur an Rändern, bei extremer
  kognitiver Dissonanz (Subroutinen greifen gleichzeitig auf denselben Speicher
  zu → Phasenverschiebung). *Prompt:* `severe chromatic aberration, sharp RGB
  channel shift, medical imaging distortion, red-blue color fringing, optical
  phase mismatch`.
- **Data Moshing / Macro-Blocking:** harte rechteckige Pixel-Verschiebungen,
  Kompressionsartefakte — traumatische "Memory Leaks", die in die Gegenwart
  bluten. *Prompt:* `compression artifacting, hard datamoshing, digital
  macro-blocking, corrupted JPEG texture, blocky video codec failure, severe
  glitch fragmentation`.
- **Medical Scan Aesthetics:** Texturen aus Röntgen, MRT, Ultraschall-Rauschen,
  Elektronenmikroskopie. *Prompt:* `MRI scan texture, electron microscope visual
  style, cold radiological imaging, x-ray translucent surfaces, clinical
  ultrasound noise`.

### 3.3 Typografie als physische Textur

Buchstaben/Code/Zahlen sind physische Raumelemente (Wände, holografisches
Gesichtsrauschen, volumetrische Boden-Gitter). Nur **serifenlose Monospace /
Code-Edit-Fonts / OCR-A-Derivate / rohe Kommandozeilen-Typografie**. *Prompt:*
`overlay of dense monospace terminal code, glowing hex dumps projected on walls,
OCR font textures floating in 3D space, cascading data strings`.

## 4. Semiotisches Vokabular und Symbol-Architektur

Streng kontrollierte Symbol-Bibliothek; **ein Kernsymbol pro Bild** (keine
Metaphorik-Überladung).

1. **Datenfissur (The Data Fissure / Der Riss).** Instabilität, Aufbrechen
   verdrängter Information. Tiefer geometrisch-fraktaler Riss in Beton/Serverwand;
   Inneres absolut schwarz `#000000`; Bruchkanten leuchten (Corrupted Yellow =
   Trauma, Terminal Green = Systemfehler). Tier 0: feiner Haarriss; Tier 3:
   spaltet das Interface. *Prompt:* `a jagged deep black fissure traversing a
   brutalist concrete wall, glowing toxic yellow light bleeding intensely from the
   sharp crack edges`.
2. **Terminal-Spiegel (The Black Mirrors).** Introspektion/Multiplizität;
   reflektiert den Code der aktiven Subroutine, nicht das Gesicht. Monolithische
   Monitore; in Krise zersplittert, jeder Splitter ein asynchroner Datenstrom.
   *Prompt:* `shattered monolithic terminal screen, multiple fractured black
   mirror reflections, each shard displaying asynchronous lines of code, identity
   fragmentation`.
3. **Latenz-Ringe (The Buffer / Loading States).** Hypoarousal, Erstarrung,
   Unfähigkeit traumatische Daten in Echtzeit zu parsen. Schwebende rotierende
   UI-Bögen/Progress-Bars in Latency Violet/kühlem Grau, eingefroren. *Prompt:*
   `a glowing frozen circular buffering ring UI suspended in mid-air, latency
   symbol overlay, infinite loading wheel, suspended digital animation`.
4. **Kintsugi-Leiterbahnen (Digital Kintsugi / Golden Repair).** Erfolgreiche
   Integration/Heilung; Fehler als Stärke. Geometrische Brüche verbunden durch
   rechtwinklig fließende Kintsugi-Gold-Linien — wie Platinen-Leiterbahn, nicht
   organisch. *Prompt:* `digital kintsugi repair aesthetic, glowing golden PCB
   circuit lines precisely mending shattered black glass, luminous gold algorithms
   filling geometric cracks`.
5. **Datenknoten / Verschlüsselte Payload.** Geschütztes Paket unkorrumpierter
   Wahrheit (ersetzt den Brief). Schwebender symmetrischer versiegelter Kubus mit
   einem winzigen Clean-Ping-Signallicht, pulsierend. *Prompt:* `a floating
   perfectly symmetrical sealed data drive cube, emitting a single soft lemon
   yellow decryption light ping, isolated in a vast dark terminal room`.
6. **Biometrische Netzwerke (Neural-Circuit Mesh).** Technologische Kälte trifft
   biologisches Grauen (Cronenberg-Digital). Dichte wuchernde Netzwerke aus
   Kabeln/Fiberoptik; Adern transportieren Daten statt Blut. *Prompt:* `macabre
   biometric neural network made of black fiber optic cables, biological horror
   meets technology, pulsating synthetic digital veins, cybernetic anatomy`.
7. **Das Panoptische Auge (The Sensor / Surveillance Lens).** Paranoia, ständige
   Überwachung. Kalt leuchtende Linsen, Lidar, Scanner-Laser aus der Dunkelheit;
   unbarmherzig, statisch. *Prompt:* `unforgiving mechanical surveillance lens
   emerging from the shadows, glowing red lidar scanner beam, oppressive panoptic
   technology, cold glass sensor reflection`.

## 5. Kompositionsregeln, Perspektivachsen und Räumliche Spannungsfelder

Symmetrie = Kontrolle; Asymmetrie = Wahrheit, die ins Chaos drängt.

### 5.1 Operative Spannungsfelder

- **A. Nähe vs. Projektion.** Pol A: aggressive Nähe, übermächtige
  Pixel-/Code-Details, klaustrophobisch/subjektiv. Pol B: totale Distanz, Motiv
  winzig in überwältigenden Server-Strukturen, CCTV-Beobachter, Bedeutungslosigkeit
  des Einzelsystems. **Regel:** nie in der "bequemen Mitte" (Halbnah). Maximale
  Konfrontation **oder** maximale Isolation.
- **B. Ordnung vs. Wahrheit.** Pol A: strikte Zentralperspektive, Snap-to-Grid =
  Firewall/Kontrolle. Pol B: Dutch Angle, stürzende Linien, fehlendes Gegengewicht,
  Bild "droht umzufallen" = Trauma destabilisiert das System. **Asymmetrie ist das
  wichtigste Unbehagen-Werkzeug.**
- **C. Klinische Schärfe vs. Daten-Unschärfe.** Pol A: unendliche Tiefenschärfe,
  gnadenlos scharf, kein Ort für Fehler. Pol B: Makro-Tiefe, nur ein winziger
  Ausschnitt scharf, Rest in digitalem Bokeh / chromatischer Verzerrung / Jitter-
  Motion-Blur.

### 5.2 Linsenspezifikationen (Kamera-Prompts)

- **Isolation (Weitwinkel):** `shot on 14mm lens, ultra-wide angle, CCTV security
  camera perspective, immense sense of scale, towering environment`
- **Klaustrophobie (Makro/Close-Up):** `shot on 100mm macro lens, extreme
  close-up, suffocating tight framing, shallow depth of field, sharp foreground
  focus`
- **Instabilität (Winkel):** `extreme dutch angle, tilted camera perspective,
  disorienting 45-degree rotation, architectural vertigo`

## 6. Eskalationsmodul und Deterministische Zustandsmaschinen (Tier 0–4)

Strikte State Machine. Jedes Bild ordnet sich **exakt einem Tier** zu —
**Vermischen verboten** (zerstört die Lesbarkeit des Systemzustands).

### Tier 0 — Homöostase (Window of Tolerance)
Fehlerfrei, absolute Kontrolle, kalte Effizienz, keine Glitches.
- **Farbe:** 98 % Terminal Black + Deep Charcoal; max **2 %** System Blue als
  leises Statuslicht.
- **Komposition:** perfekt zentriert, Frontalansicht, orthografische Projektion,
  viel negativer Raum.
- **Linie/Textur:** rasiermesserscharf, fehlerfreie Vektoren, makellose Flächen.
- **Prompt (EN):** `Tier 0 state, minimalist clinical precision, vast empty black
  void, sterile technological environment, perfectly balanced orthographic
  composition, stable architecture, pristine dark surfaces, razor-sharp vector
  lines, no glitches, profound silence`

### Tier 1 — Latency / Freeze (Untersteuerung & Dissoziation)
System verlangsamt, Datenverlust, wachsende Isolation, Hypoarousal.
- **Farbe:** Kontrastverlust, Schwarz wird milchig-dunkelgrau, Einblenden von
  Latency Violet, sehr blass.
- **Komposition:** extreme Weitwinkel, Motiv verschwindet im dunklen Raum, Kamera
  weit weg, isolierend.
- **Linie/Textur:** transparente kaum sichtbare Vektoren, abbrechende Linien
  (Packet Loss), nebelige volumetrische Leere.
- **Prompt (EN):** `Tier 1 state, fading opacity, deep fog swallowing the subject,
  low contrast bleakness, extreme wide shot isolating the focal point, dropped
  data packets, ghostly thin contours, disconnected UI wireframes, suspended
  animation, muted latency violet ambient glow`

### Tier 2 — Alert (Hyperarousal / System-Konflikt)
Einbruch fremder Daten, hektischer Kontrollerhalt, Warnsysteme feuern.
- **Farbe:** hartes Schwarz trifft grelle Warnfarben; Signal Yellow & Terminal
  Green durchschneiden die Dunkelheit.
- **Komposition:** Dutch Angle, kippender Horizont, aggressive Asymmetrie.
- **Linie/Textur:** leichte chromatische Aberration an Rändern, verdichtete
  Code-Schraffuren, HUD-Clutter.
- **Prompt (EN):** `Tier 2 state, aggressive asymmetrical tension, severe dutch
  angle, sharp chromatic aberration on the edges, hostile neon signal yellow
  warning lights piercing the darkness, dense terminal text clutter, surveillance
  aesthetic, paranoid atmosphere, system alert`

### Tier 3 — Kernel Panic (Systemkollaps)
Totale Übersteuerung, kognitiver Kern versagt, emotionaler Peak.
- **Farbe:** Flame Orange & Corrupted Yellow übersteuern, Farben bluten ineinander,
  höchster Kontrast.
- **Komposition:** klaustrophobisches Close-up, Rahmen von Code-Trümmern gesprengt,
  totales Chaos.
- **Linie/Textur:** extreme Datamoshing-Artefakte, zerrissene Geometrien,
  unkontrolliertes Rauschen, Zerstörung des Rasters.
- **Prompt (EN):** `Tier 3 state, total digital collapse, extreme datamoshing,
  claustrophobic macro close-up, violent flame orange digital fragmentation,
  chaotic system error, corrupted geometry, overwhelming data cascades,
  catastrophic interface breakdown, visual noise`

### Tier 4 — Safe Mode (Post-Trauma & Reboot)
Nach dem Crash, Notabschaltung, Wiederherstellung minimaler Integrität,
Erschöpfung + Klärung.
- **Farbe:** Entfärbung, sehr blasse ausgewaschene Grautöne, evtl. ein einzelner
  Funke Clean Ping oder Kintsugi Gold.
- **Komposition:** statisch, ruhig, sichtbare Narben, zurückhaltende Distanz.
- **Linie/Textur:** Risse als **dunkle Furchen, nicht mehr leuchtend**; Textur wie
  abgekühltes mattes Metall.
- **Prompt (EN):** `Tier 4 state, desaturated post-crash environment, pale
  washed-out concrete greys, visible digital scars and deep dead fissures, static
  calm, exhausted system, minimalist rebirth, single tiny glowing gold kintsugi
  repair line, cold quiet atmosphere`

> **Chapter Zero note:** this album has **NO Kintsugi / no Clean Ping** — its Tier
> 4 (Track 13) uses **dead furrows only**, never a hopeful glow.

## 7. Prompt-Engineering-Syntax und Vokabular-Kategorien

Modulares Framework für KI-Bildgeneratoren. (Midjourney/SD/Flux nutzen die
`::`-Blockformel; **DALL-E nutzt eine konversationale Übersetzung** — siehe
`overrides/album-art-preferences.md`.)

### 7.1 Die SPECD-Prompt-Formel (`::`-getrennt, fünf Blöcke)

`[Subject/Motiv] :: [State/Tier] :: [Environment/Camera] :: [Style/Lighting] ::
[Parameters --no … --style raw --ar …]`

Die doppelten Doppelpunkte zwingen das Modell zu sauberer Gewichtsverteilung und
minimieren "Bleeding" von Konzepten.

### 7.2 Visuelle Schlüsselwort-Kategorien

- **A · Motive/Subjekte:** shattered monolithic terminal screen · jagged deep
  black data fissure · glowing frozen circular buffering ring UI · sealed data
  drive cube · macabre biometric neural network of fiber optic cables · mechanical
  surveillance lens · `faceless humanoid silhouette constructed of dense
  wireframes, obscured by terminal text overlays` (menschenähnliche Silhouetten
  nur als verdeckte, datenkodierte Entitäten).
- **B · Emotionale Zustandssyntax:** Tier 0–4 (Sektion 6). Zusatz:
  `experiencing latency` · `succumbing to toxic data decay` · `processing immense
  logical constraints` · `executing hostile intrusion detection`.
- **C · Umgebung/Kamera:** vast empty black void, negative space dominance ·
  claustrophobic brutalist server corridor, oppressive scale · shot on 14mm lens,
  CCTV perspective · shot on 100mm macro lens, severe dutch angle, asymmetrical
  framing.
- **D · Klinischer Stil/Beleuchtung (in JEDEM Prompt verankern):** `interface
  brutalism, clinical dystopian aesthetic, high-contrast dark mode, synthetic
  digital materiality, electron microscope fidelity, medical imaging aesthetic`.
  Licht: `harsh surgical overhead lighting, cold LED light, volumetric phosphor
  terminal glow, deep raytraced black shadows`.
- **E · Negative Prompts & Parameter:** `--no 1980s retro, synthwave, outrun,
  purple-orange gradient, neon grid, daylight, sun, natural elements, cute, soft
  lighting, watercolor, analog painting, visible paper texture, lens flare,
  organic curves`. Render: `--ar 16:9` (Umgebungen) / `--ar 4:5` (Knotenpunkte) /
  `1:1` (Cover); `--style raw`; `--s 50`–`--s 100`; neuestes `--v`; `--sref` des
  Master-Bildes für Folge-Shots.

### 7.3 Beispiel (Tier 2 Alert)

`mechanical surveillance lens emerging from shadows, cold glass sensor reflection
:: Tier 2 state, paranoid atmosphere, system alert, executing hostile intrusion
detection :: claustrophobic close-up, aggressive asymmetrical tension, severe
dutch angle, tilted camera perspective :: interface brutalism, clinical dystopian
aesthetic, sharp chromatic aberration on the edges, hostile neon signal yellow
warning lights piercing the darkness, high-contrast dark mode, medical imaging
aesthetic, deep raytraced black shadows :: --no 1980s retro, synthwave, daylight,
soft lighting, analog texture --ar 16:9 --style raw --s 75 --v 6.0`

## 8. Master-Ausführungs-Checkliste (Agentic Validation)

Ein einziger Fehlschlag in 1–3 → sofortige Zurückweisung.

- [ ] **Reinheits-Check (Aesthetic Ban List):** keine Synthwave/80er-Neon/
  Purple-Orange-Gradients; keine analogen Texturen (Papier, Pinsel, Bleistift);
  kein Tageslicht/Natur. Bei "Ja" → löschen + Re-Prompt mit verschärften Negatives.
- [ ] **Vakuum-Check (Background Ratio):** Hintergrund > 70 % Terminal Black /
  Deep Charcoal; Motiv isoliert (außer Tier 3).
- [ ] **Diagnostik-Check (Color Isolation):** genau **ein** primärer emotionaler
  Hex zur Akzentuierung; Verbot-Regeln eingehalten (nie Flame Orange + Clean Ping).
- [ ] **Struktur-Check (Interface Brutalism):** klinische maschinelle Roheit,
  Grids, Monospace-Overlays, harte fensterlose Architektur.
- [ ] **Spannungs-Check:** aktive Kameraperspektive (Distanz vs. Makro) oder
  Asymmetrie (Dutch Angle) zur psychologischen Spannung (Tier 1–3).
- [ ] **Eskalations-Kohärenz (State Machine Integrity):** Störung passt exakt zum
  Tier (keine Glitches in Tier 0; Datamoshing in Tier 3 aggressiv genug).
- [ ] **Format-Hygiene:** für `::`-Pipelines die 5 SPECD-Blöcke, `--style raw`,
  Aspect-Ratio, `--sref` des Basis-Stylesheets. (Für DALL-E: konversationale
  Übersetzung gemäß Art-Direction-Override.)

*(Ende der Agency System Design Language Spec.)*
