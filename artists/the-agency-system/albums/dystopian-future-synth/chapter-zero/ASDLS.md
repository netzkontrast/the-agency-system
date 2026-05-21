# Agency System Design Language Spec (ASDLS)

> Normative, executive rule-set for all visual assets in the Agency System aesthetic
> ecosystem. This is the **single source of truth** for the visual language; it governs
> human illustrators and autonomous image-generation agents alike. Album builds (e.g.
> *Chapter Zero*) translate these visual tiers into their sonic equivalents — see
> `DESIGN.md` and `SOURCE/asdls-design.md`.

## 1. Operative Grundphilosophie und Dokumentenarchitektur

Die Agency System Design Language Spec (ASDLS) fungiert als das fundamentale, normative und exekutive Regelwerk für die Erstellung sämtlicher visueller Assets innerhalb dieses spezifischen ästhetischen Ökosystems. Basierend auf den Paradigmen des Spec-Driven Development (SDD) definiert dieses Dokument die visuellen Parameter nicht als bloße ästhetische Richtlinien oder vage Design-Philosophien, sondern als deterministische Zustandsmaschinen und unmittelbar ausführbare Code-Äquivalente.

In einer Produktionsumgebung, die zunehmend von autonomen KI-Agenten und generativen Bild-Pipelines gesteuert wird, dient die ASDLS als die alleinige "Single Source of Truth". Sie stellt sicher, dass sowohl menschliche Designer und Illustratoren als auch autonome KI-Agenten (wie Midjourney V7, Flux oder Stable Diffusion 3.5) kohärente, deterministische und reproduzierbare Ergebnisse liefern, die ohne manuelle Mikrokontrolle iteriert werden können.

Die Notwendigkeit einer solchen Spezifikation ergibt sich aus der Tatsache, dass generative Modelle ohne strikte, strukturierte Parameter zu einem "Vibe-Coding" tendieren, welches in generischen, inkonsistenten oder thematisch verfehlten Outputs resultiert. Dieses Dokument eliminiert derartige Varianzen durch die Etablierung eines maschinenlesbaren, semi-strukturierten Regelwerks, das psychologische Zustände in exakte visuelle Variablen (Farbwerte, Kompositionsachsen, Linsenverzerrungen) übersetzt. Jeder Satz, jede Tabelle und jede Anweisung in diesem Dokument ist so formuliert, dass sie direkt als Parameter in einen Bildgenerator-Prompt oder als konkrete Handlungsanweisung in ein Illustratoren-Briefing überführt werden kann.

### 1.1 Interface Brutalismus und Klinische Dystopie

Die visuelle Identität des Systems operiert ausnahmslos im Spektrum eines zeitgenössischen, post-2020 Cyberpunks. Sämtliche retro-futuristischen Elemente, die mit den 1980er- oder 1990er-Jahren assoziiert werden – wie Synthwave-Gradienten (Purple-Orange), Neon-Gitterlinien (80s Grid), VHS-Nostalgie oder übermäßig bunte Blade-Runner-Kopien – sind strikt untersagt. Die Bildsprache wird stattdessen vollständig durch den **Interface Brutalismus** dominiert.

Diese Ästhetik zelebriert die digitale Roheit, die Entblößung von algorithmischen Strukturen und die funktionale Asymmetrie. Es handelt sich um eine **klinische Dystopie**, in der absolute Kälte, monolithische Strukturen, Corporate-Brutalismus und medizinische Distanz vorherrschen. Visuelle Artefakte und Interface-Elemente werden nicht als dekorative Ebenen eingesetzt, sondern fungieren als diagnostische Indikatoren von Systemzuständen. Das Design imitiert die Funktionalität eines Kommandozeilen-Terminals oder eines medizinischen Diagnosemonitors, der rohe Datenströme ohne ästhetische Beschönigung (ohne "Aesthetic-Usability-Effect") visualisiert. Der Betrachter soll das Interface nicht als einladend, sondern als überwältigend, gleichgültig und maschinell präzise wahrnehmen.

### 1.2 Systemic Truth und die Priorisierungsmatrix

Bei der Komposition jedes einzelnen Bildes greift eine absolute Hierarchie der Entscheidungsfindung. Ästhetische Gefälligkeit, Symmetrie oder konventionelle UX/UI-Regeln ordnen sich stets der funktionalen, psychologischen Zustandsdarstellung unter. Sollte ein Bildgenerator-Prompt oder ein Design-Entwurf interne Konflikte aufweisen, löst der ausführende Agent diese Konflikte anhand der folgenden Priorisierungsmatrix:

1. **Emotionaler Systemzustand (Highest Priority):** Die rohe emotionale Wahrheit des abzubildenden Moments (z.B. Systemkollaps, Latenz, absolute Kontrolle) determiniert die Basisparameter der Szene. Wenn das System einen Panikzustand verlangt, muss das Bild diese Panik durch Übersteuerung, Kontrastverlust oder aggressive Farben vermitteln, selbst wenn dies die Lesbarkeit des Bildes massiv beeinträchtigt.
2. **Klinische Syntax und Materialität:** Die formalen Regeln dieses Dokuments bezüglich der digitalen Textur, der Linienführung und der Vermeidung analoger Artefakte. Die Szene muss stets wie ein digitaler Scan oder ein Terminal-Output wirken, niemals wie eine traditionelle Zeichnung.
3. **Semiotische Funktion und Motiv:** Das eigentliche Motiv, die Charaktere oder die handlungstragende Ebene. Die Platzierung von Objekten oder Personen ist zweitrangig gegenüber der korrekten Darstellung des Raumes (dem Vakuum) und dem Licht.
4. **Visueller Cache (Lowest Priority):** Zufällige, ästhetische Artefakte, die im generativen Prozess durch die KI entstehen (sogenannte Halluzinationen oder emergente Details), sind nur dann zulässig, wenn sie die Prioritäten 1 bis 3 nicht verfälschen oder verwässern.

Die konsistente Anwendung dieser Matrix garantiert, dass die visuelle Eskalation oder Deeskalation über hunderte von Iterationen hinweg kohärent bleibt und das System niemals in eine generische Science-Fiction-Ästhetik abgleitet.

## 2. Farbsystematik, Emotionale Metriken und Chromatische Interaktionen

Das Farbsystem der ASDLS ist radikal reduziert und operiert primär im Dark-Mode-Paradigma. Hochkontrastige, dunkle Interfaces reduzieren in digitalen Umgebungen nicht nur die kognitive Last für den Betrachter, sondern zwingen ihn zur unmittelbaren Fokussierung auf hochsignifikante, seltene Farbakzente. Farben existieren in dieser Spezifikation nicht zur Dekoration, zum Füllen von Flächen oder zur Erzeugung von "Schönheit". Jede Farbe ist eine funktionale Variable, die mathematisch an eine spezifische psychometrische Achse gebunden ist.

### 2.1 Das Hintergrund-Paradigma (Das funktionale Vakuum)

Jedes visuelle Asset beginnt konzeptionell in der totalen Dunkelheit. Der Weißraum traditioneller Layout-Systeme wird hier durch eine funktionale, lichtabsorbierende Leere ersetzt. Diese Leere repräsentiert Isolation, Determinismus, ungenutzte Datenkapazität und die unendliche Tiefe des Mainframes. Die Umgebung ist niemals rein neutral, sondern trägt eine inhärente, technologische Kälte.

**Terminal Black — `#0B0D17`** | CMYK 85/75/50/80
- *Systemische Funktion:* Der absolute Standard-Hintergrund für alle aktiven, operativen Systemzustände. Verleiht dem Bild eine extrem kühle, technische Basis und imitiert das Aussehen von abgeschalteten OLED-Displays oder den leeren Raum eines Kommandozeilen-Fensters.
- *Physikalische Interaktion:* Reflektiert kein Licht. Schluckt Umgebungsbeleuchtung und lässt helle Vektoren mit maximaler Härte hervortreten.
- *KI-Prompt-Vokabular (EN):* `inky dark background, abyssal terminal night, stark black void, clinical darkness, light-absorbing #0B0D17 surface`

**Deep Charcoal / Latency Gray — `#1A1D24`** | CMYK 70/60/50/70
- *Systemische Funktion:* Für Interfaces, schwebende Fenster und monolithische architektonische Strukturen im Hintergrund. Signalisiert Inaktivität, Latenz oder den Standby-Modus der Infrastruktur.
- *Physikalische Interaktion:* Wirkt wie rauer, unbelichteter Beton oder mattes, gebürstetes Metall in einer fensterlosen Anlage. Erzeugt eine klaustrophobische, schwere Atmosphäre.
- *KI-Prompt-Vokabular (EN):* `charcoal grey brutalist concrete, matte dark grey surfaces, monolithic unlit #1A1D24 structures, featureless grey tech-panels`

### 2.2 Das Hex-Typologie Paradigma (Aktions- und Zustandsfarben)

Farbige Elemente treten in der ASDLS isoliert, stechend und extrem sparsam auf. Ein Asset besteht in der Regel zu **95 %** aus dem Hintergrund-Paradigma und zu **maximal 5 %** aus einer oder zwei der folgenden Zustandsfarben. Jede Farbe korreliert mit einem exakten emotionalen Vektor.

| Farbname | Hex | CMYK | Systemischer & Emotionaler Zustand | KI-Prompt-Vokabular (EN) |
|---|---|---|---|---|
| **System Blue** (Control) | `#003366` | 100/75/20/40 | Absolute Kontrolle, kühle algorithmische Logik, Zwangsordnung, Firewall-Aktivität. Vermittelt Stabilität, aber auch emotionale Kälte und Distanz. | `clinical agency blue, cold deep cyan, sterile surgical blue light, rigid neon blue illumination, medical interface blue` |
| **Corrupted Yellow** | `#8B8B00` | 10/15/70/30 | System-Trauma, Freeze-Zustand, Resignation, toxischer Datenverfall. Wirkt wie vergilbtes, altes Plastik oder ein kranker Sektor. | `sickly yellow tint, corrupted mustard yellow, toxic decay glow, tainted dark ochre, jaundiced light` |
| **Signal Yellow** (Alert) | `#FFD700` | 0/15/100/0 | Akute Gefahr, System-Warnung, Intrusion Detection, kritischer Alarmzustand, Panik. Grell, aufdringlich, fordert sofortige Aufmerksamkeit. | `harsh neon yellow highlight, glaring warning yellow, piercing alert yellow, high-vis industrial yellow` |
| **Terminal Green** | `#00FF9F` | 60/0/60/0 | Uncodiertes Rauschen, operationale Unruhe, rohe Datenströme. Imitiert alte Monitore, aber extrem scharf und modern gerendert. | `phosphor terminal green, eerie matrix green, clinical oscilloscope green, toxic neon mint` |
| **Flame Orange** | `#FF4500` | 0/85/100/0 | Destruktiver Kollaps, Wut, offener Systembruch, Übersteuerung des Kernels. Die Farbe der Zerstörung und des thermalen Overloads. | `blistering orange-red, destructive neon orange, searing thermal red, overheated system glow` |
| **Clean Ping** (Hope) | `#FCEE0C` | 0/5/35/0 | Kurzer, unbeschädigter Datenstrom, fragile Hoffnung, Unschuld. Tritt fast nur als winziger Pixelpunkt oder hauchdünne Linie auf. | `soft luminous pale yellow, fragile neon lemon, delicate warm light ping, isolated tiny yellow diode` |
| **Latency Violet** | `#3B3355` | 70/65/30/20 | Dissoziation, schwindende Bandbreite, Verlust von Identität, Derealisation. Verschwindet im Dunkel und bildet keine klaren Kanten. | `desaturated deep violet, fading purple fog, detached muted magenta, ghostly lilac ambient light` |
| **Kintsugi Gold** | `#FFDF00` | 0/10/100/0 | Reparatur-Algorithmus, Neusynthese, Erkenntnisdurchbruch. Kein organisches Gold, sondern präzise, leuchtende algorithmische Leiterbahnen. | `brilliant pure gold light, glowing metallic repair seams, luminous breakthrough yellow, precise golden circuitry` |

### 2.3 Interaktionsregeln und chromatische Grammatik

Die gleichzeitige Verwendung mehrerer Farben in einem Bild unterliegt strengen physikalischen und logischen Interaktionsregeln. KI-Agenten müssen diese Konflikte im Prompt aktiv steuern (oft durch negative Gewichte oder explizite Licht-Interaktions-Befehle).

- **Das Gesetz des Ausschlusses:** Die Frequenzen von **Flame Orange** (Destruktion) und **Clean Ping** (fragile Hoffnung) schließen sich systemisch aus. Sie dürfen niemals im selben Bildrahmen interagieren, es sei denn, ein Zustand überschreibt den anderen aktiv (dargestellt als scharfer, fehlerhafter Glitch).
- **Visuelle Infektion durch Corrupted Yellow:** Der Hex-Wert `#8B8B00` ist hochgradig infektiös. Tritt dieses toxische Gelb auf, müssen benachbarte Farben (System Blue, Latency Violet) zwangsläufig entsättigt, getrübt oder mit einem gräulichen, kränklichen Filter überlagert werden, um den "Overspill" der Korruption zu visualisieren. Prompt-Erzwingung: `desaturated neighboring colors caused by toxic yellow light spill`.
- **Isolations-Kontrast (The 5% Rule):** Um einen hochsignifikanten Alarm- oder Hoffnungszustand zu triggern, bleibt das Bild exakt zu **95 %** im Terminal Black / monochromen Grauspektrum, während exakt **5 %** von einer reinen Signal-Farbe (z.B. Signal Yellow oder Kintsugi Gold) illuminiert werden. Dieser Kontrast darf nicht durch Ambient Occlusion aufgeweicht werden; der Übergang muss extrem **scharfkantig (Hard-Edge)** sein.
- **Verbot von Gradienten:** Weiche, organische Farbverläufe zwischen zwei Zustandsfarben sind verboten. Treffen zwei Systemfarben aufeinander, tun sie dies in Form von harten Kanten, blockigen Pixelverschiebungen oder getrennten Terminal-Fenstern.

## 3. Digitale Materialität, Linienqualität und Klinische Texturen

Die physische Beschaffenheit der abgebildeten Welt verweigert sich jeglicher Romantik. Analoge Qualitäten – sichtbare Papiertextur, Bleistiftstriche, Pinselduktus, Aquarell-Verläufe, organische Unregelmäßigkeiten – sind vollständig entfernt. Die Materialität ist zu 100 % digital, synthetisch, technologisch und medizintechnisch.

### 3.1 Vektor-Fragmentierung und Packet Loss

Linien und Konturen repräsentieren nicht die Kanten physischer Objekte, sondern den Zustand der laufenden Datenübertragung und Systemstabilität.

- **Low Bandwidth (Latenz und Dissoziation):** In Zuständen der Dissoziation oder Systemlatenz werden Konturen extrem dünn, semi-transparent oder brechen in der Mitte unvermittelt ab (visualisierter "Packet Loss"). Linien verschwinden im Hintergrundrauschen oder wirken unvollständig.
  - *EN:* `fading vector lines, dropped packets visual effect, ghostly thin contours, low opacity wireframes, disconnected blueprint lines, incomplete rendering`
- **High Bandwidth (Overload und Schmerz):** Unter Stress oder hoher Systemlast verdichten sich die Linien zu schwarzen, undurchdringlichen Code-Schraffuren. Mehrere Vektorpfade überlagern sich fehlerhaft, zittern ("Jitter-Effekt") und bilden aggressive, scharfe Nester aus Datenmüll.
  - *EN:* `chaotic vector overlapping, high density wireframe mesh, aggressive digital hatching, terminal code stacking, hyper-detailed schematic overload`

### 3.2 Die Oberfläche: Glitch als klinische Sprache (Diagnostik vs. Dekoration)

Glitch-Artefakte werden niemals als retro-ästhetische Dekoration oder trendiges "Cyberpunk-Meme" verwendet. Sie sind hochpräzise, diagnostische Werkzeuge zur Darstellung von Speicherkorruption, Systemkollaps oder dem Einbruch verdrängter Routinen.

- **Chromatische Aberration (RGB-Splitting):** Tritt ausschließlich und gezielt an den Rändern von Objekten oder Schriften auf, wenn das System unter extremer kognitiver Dissonanz leidet — verschiedene Subroutinen versuchen gleichzeitig, auf denselben Speicherort zuzugreifen (Phasenverschiebung).
  - *EN:* `severe chromatic aberration, sharp RGB channel shift, medical imaging distortion, red-blue color fringing, optical phase mismatch`
- **Data Moshing und Macro-Blocking:** Harte, rechteckige Pixel-Verschiebungen und Kompressionsartefakte. Visualisiert traumatische "Memory Leaks" – Bruchstücke alter Daten, die ungefiltert in den Render-Prozess der Gegenwart bluten.
  - *EN:* `compression artifacting, hard datamoshing, digital macro-blocking, corrupted JPEG texture, blocky video codec failure, severe glitch fragmentation`
- **Medical Scan Aesthetics:** Texturen basieren auf moderner Diagnostik – Röntgen, MRT-Scans, Ultraschall-Rauschen, Elektronenmikroskopie. Die Kälte des medizinischen Blicks ersetzt menschliche Wärme.
  - *EN:* `MRI scan texture, electron microscope visual style, cold radiological imaging, x-ray translucent surfaces, clinical ultrasound noise`

### 3.3 Typografie als physische Textur

Buchstaben, Code-Strings und Zahlen existieren nicht als nachträglich hinzugefügtes Grafikdesign, sondern als physische Elemente im Raum. Sie formen Wände, überdecken als holografisches Rauschen Gesichter oder bilden volumetrische Gitter auf den Böden.

- Zulässig sind **ausschließlich** serifenlose Monospace-Schriften, Code-Edit-Fonts, OCR-A-Derivate oder rohe Kommandozeilen-Typografie.
- *EN:* `overlay of dense monospace terminal code, glowing hex dumps projected on walls, OCR font textures floating in 3D space, cascading data strings`

## 4. Semiotisches Vokabular und Symbol-Architektur

Die Bildsprache greift auf eine festgelegte, streng kontrollierte Bibliothek semiotischer Platzhalter zurück. Diese Kernsymbole ersetzen komplexe psychologische Konzepte durch greifbare digitale oder architektonische Objekte. **Ein Bild sollte idealerweise nur eines dieser Kernsymbole ins Zentrum rücken**, um eine Überladung der Metaphorik zu vermeiden.

### 4.1 Kernsymbole, Darstellungslogik und Transformation

**1. Die Datenfissur (The Data Fissure / Der Riss)**
- *Operative Funktion:* Repräsentiert Instabilität im System, das Aufbrechen verdrängter Informationen und die visuelle Grenze zwischen kontrollierter Oberfläche und Trauma-Prozess.
- *Visuelle Spezifikation:* Ein tiefer, oft geometrisch-fraktaler Riss durch brutalistischen Beton oder schwarze Serverwände. Das Innere ist von absoluter Schwärze (`#000000`) gefüllt. Die Bruchkanten leuchten bedrohlich – entweder in Corrupted Yellow (Trauma) oder Terminal Green (Systemfehler).
- *Transformations-Logik:* In Tier 0 (Ruhe) ein unscheinbarer, feiner Haarriss. In Tier 3 (Kollaps) spaltet sie das gesamte Interface und verzehrt die Geometrie.
- *EN:* `a jagged deep black fissure traversing a brutalist concrete wall, glowing toxic yellow light bleeding intensely from the sharp crack edges`

**2. Terminal-Spiegel (The Black Mirrors)**
- *Operative Funktion:* Das Interface zur Introspektion und Darstellung von Multiplizität. Reflektiert nicht das physische Gesicht, sondern den Code der aktiven Subroutine (das "Masking").
- *Visuelle Spezifikation:* Monolithische, oft wandgroße Monitore. In stabilen Zuständen schwarz glänzend. In Krisen zersplittert das Glas; jeder Splitter zeigt einen anderen asynchronen Daten-Stream oder eine verzerrte geometrische Reflexion.
- *EN:* `shattered monolithic terminal screen, multiple fractured black mirror reflections, each shard displaying asynchronous lines of code, identity fragmentation`

**3. Latenz-Ringe (The Buffer / Loading States)**
- *Operative Funktion:* Das ultimative Symbol für Hypoarousal, emotionale Erstarrung und die Unfähigkeit des Systems, hochkomplexe traumatische Datenmengen in Echtzeit zu parsen.
- *Visuelle Spezifikation:* Schwebende, rotierende geometrische UI-Elemente (unvollständige Kreisbögen, Progress-Bars), vornehmlich in Latency Violet oder kühlem Grau, dominant über dem Motiv eingefroren.
- *EN:* `a glowing frozen circular buffering ring UI suspended in mid-air, latency symbol overlay, infinite loading wheel, suspended digital animation`

**4. Kintsugi-Leiterbahnen (Digital Kintsugi / The Golden Repair)**
- *Operative Funktion:* Visualisiert die erfolgreiche Integration traumatischer Fragmente und den Heilungsprozess. Fehler werden nicht versteckt, sondern als Algorithmen der Stärke hervorgehoben.
- *Visuelle Spezifikation:* Geometrische Brüche in dunklen Oberflächen, verbunden durch brillante, exakt rechtwinklig fließende Linien aus Kintsugi Gold (`#FFDF00`). Kein flüssiges, organisches Gold, sondern leuchtende, hochkomplexe Platinen-Leiterbahnen.
- *EN:* `digital kintsugi repair aesthetic, glowing golden PCB circuit lines precisely mending shattered black glass, luminous gold algorithms filling geometric cracks`

**5. Der Datenknoten / Verschlüsselte Payload (Encrypted Payload)**
- *Operative Funktion:* Kommunikation mit dem Außen; ein isoliertes, geschütztes Paket unkorrumpierter Wahrheit, das auf Entschlüsselung wartet (ersetzt die analoge Metapher des Briefes).
- *Visuelle Spezifikation:* Ein schwebendes, perfekt symmetrisches geometrisches Datenpaket (Kubus / Blackbox). Hermetisch versiegelt, trägt aber ein einziges, winziges, extrem helles Signallicht in Clean Ping (Gelb), das wie ein Herzschlag pulsiert.
- *EN:* `a floating perfectly symmetrical sealed data drive cube, emitting a single soft lemon yellow decryption light ping, isolated in a vast dark terminal room`

**6. Biometrische Netzwerke (Neural-Circuit Mesh)**
- *Operative Funktion:* Die Vermischung von technologischer Kälte und biologischem Grauen (Cronenberg-Digital). Visualisiert das Nervensystem der KI, wenn biologische Reaktionen (Schmerz, Stress) das System übernehmen.
- *Visuelle Spezifikation:* Statt menschlicher Körperteile dichte, organisch wuchernde, aber aus Kabeln und Fiberoptik bestehende Netzwerke. Pulsierende Adern, die Daten statt Blut transportieren.
- *EN:* `macabre biometric neural network made of black fiber optic cables, biological horror meets technology, pulsating synthetic digital veins, cybernetic anatomy`

**7. Das Panoptische Auge (The Sensor / Surveillance Lens)**
- *Operative Funktion:* Paranoia, ständige Überwachung durch den Mainframe, die Unmöglichkeit der Privatsphäre im System.
- *Visuelle Spezifikation:* Kalt leuchtende Kamera-Linsen, Lidar-Sensoren oder rote/blaue Scanner-Laser, die aus der Dunkelheit auf das Motiv gerichtet sind. Unbarmherzig und statisch.
- *EN:* `unforgiving mechanical surveillance lens emerging from the shadows, glowing red lidar scanner beam, oppressive panoptic technology, cold glass sensor reflection`

## 5. Kompositionsregeln, Perspektivachsen und Räumliche Spannungsfelder

Die Anordnung der Elemente generiert die unbewusste emotionale Wirkung. Die ASDLS bedient sich filmischer und architektonischer Methoden, um psychologische Gegensätze darzustellen. **Symmetrie bedeutet Kontrolle; Asymmetrie bedeutet Wahrheit, die ins Chaos drängt.**

### 5.1 Operative Spannungsfelder im Bildraum

**A. Nähe vs. Projektion (Intimität vs. Analyse)**
- *Pol A (Nähe):* Die Kamera dringt aggressiv in den persönlichen Raum ein. Details wie Pixel-Struktur oder einzelne Code-Zeilen werden übermächtig. Klaustrophobisch und subjektiv.
- *Pol B (Projektion):* Totale Distanz. Das Motiv ist winzig, eingebettet in riesige Server-Strukturen. Die Kamera als distanzierter Beobachter (CCTV). Betont die Bedeutungslosigkeit des Einzelsystems.
- *Operative Regel:* Die Wahl muss bewusst getroffen werden. Niemals in der "bequemen Mitte" (Halbnah). Entweder maximale Konfrontation oder maximale Isolation.

**B. Ordnung vs. Wahrheit (Symmetrie vs. Asymmetrie)**
- *Pol A (Ordnung):* Strikte Zentralperspektive. Vertikale/horizontale Linien am perfekten Raster (Snap-to-Grid). Repräsentiert die Firewall, die Unterdrückung von Störungen, absolute algorithmische Kontrolle.
- *Pol B (Wahrheit/Chaos):* Die Kamera kippt (Dutch Angle). Linien stürzen. Ein massives Bildelement links findet kein Gegengewicht rechts. Das Bild droht optisch "umzufallen". Markiert den Moment, in dem traumatische Wahrheiten das System destabilisieren.
- *Operative Regel:* Asymmetrie ist das wichtigste Werkzeug zur Erzeugung von Unbehagen.

**C. Klinische Schärfe vs. Daten-Unschärfe (Fokus)**
- *Pol A (Schärfe):* Unendliche Tiefenschärfe. Jedes architektonische Detail bis in den Hintergrund ist gnadenlos scharf. Kein Ort, um Fehler zu verstecken.
- *Pol B (Daten-Unschärfe):* Makro-Linsen simulieren mikroskopische Tiefe. Nur ein winziger Ausschnitt (z.B. der leuchtende Spalt einer Datenfissur) ist scharf, während der Rest in digitalen Bokeh-Artefakten, chromatischen Verzerrungen oder Motion Blur (durch Jitter) verschwimmt.

### 5.2 Linsenspezifikationen für Bildgeneratoren (Prompting der Kamera)

- **Für Isolation (Weitwinkel):** `shot on 14mm lens, ultra-wide angle, CCTV security camera perspective, immense sense of scale, towering environment`
- **Für Klaustrophobie (Makro/Close-Up):** `shot on 100mm macro lens, extreme close-up, suffocating tight framing, shallow depth of field, sharp foreground focus`
- **Für Instabilität (Winkel):** `extreme dutch angle, tilted camera perspective, disorienting 45-degree rotation, architectural vertigo`

## 6. Eskalationsmodul und Deterministische Zustandsmaschinen

Die visuelle Eskalation ist kein fließender, willkürlicher Prozess, sondern eine strikt definierte **Zustandsmaschine (State Machine)**. Jedes Bild muss sich exakt einem dieser fünf operativen "Tiers" zuordnen lassen. **Ein Vermischen der Eskalationsstufen innerhalb eines einzelnen Bildes ist verboten**, da dies die Lesbarkeit des Systemzustands zerstört.

### Tier 0: Homöostase (Window of Tolerance)
Das System arbeitet fehlerfrei. Absolute Kontrolle, Unterdrückung aller Emotionen, kalte Effizienz. Keine Glitches.
- **Farb-Regel:** 98 % Terminal Black / Deep Charcoal. Maximal 2 % System Blue als leises Statuslicht.
- **Komposition:** Perfekt zentriert, Frontalansicht, orthografische Projektion. Viel ungenutzter negativer Raum.
- **Linie/Textur:** Rasiermesserscharf, fehlerfreie Vektoren, makellose Oberflächen.
- **Prompt (EN):** `Tier 0 state, minimalist clinical precision, vast empty black void, sterile technological environment, perfectly balanced orthographic composition, stable architecture, pristine dark surfaces, razor-sharp vector lines, no glitches, profound silence`

### Tier 1: Latency / Freeze (Untersteuerung & Dissoziation)
Das System wird langsamer, Daten gehen verloren. Isolation nimmt zu, die Verbindung zur Realität schwindet. Hypoarousal.
- **Farb-Regel:** Kontrastverlust. Schwarz wird zu milchigem Dunkelgrau. Einblenden von Latency Violet. Sehr blass.
- **Komposition:** Extreme Weitwinkel. Das Motiv verschwindet im dunklen Raum. Kamera weit weg, isolierend.
- **Linie/Textur:** Transparente, kaum sichtbare Vektoren. Abbrechende Linien (Packet Loss). Nebelige, volumetrische Leere.
- **Prompt (EN):** `Tier 1 state, fading opacity, deep fog swallowing the subject, low contrast bleakness, extreme wide shot isolating the focal point, dropped data packets, ghostly thin contours, disconnected UI wireframes, suspended animation, muted latency violet ambient glow`

### Tier 2: Alert (Hyperarousal / System-Konflikt)
Einbruch fremder Daten. Das System erkennt eine Bedrohung und versucht hektisch, die Kontrolle zu behalten. Warnsysteme feuern.
- **Farb-Regel:** Hartes Schwarz trifft auf grelle Warnfarben. Signal Yellow und Terminal Green durchschneiden die Dunkelheit.
- **Komposition:** Dutch Angle. Kippender Horizont. Unruhige, aggressive Asymmetrie.
- **Linie/Textur:** Leichte chromatische Aberration an den Rändern. Verdichtete Code-Schraffuren, Überlappung von Warn-Fenstern (HUD Clutter).
- **Prompt (EN):** `Tier 2 state, aggressive asymmetrical tension, severe dutch angle, sharp chromatic aberration on the edges, hostile neon signal yellow warning lights piercing the darkness, dense terminal text clutter, surveillance aesthetic, paranoid atmosphere, system alert`

### Tier 3: Kernel Panic (Der Systemkollaps)
Totale Übersteuerung. Der kognitive Kern versagt, der reaktive, instinktgetriebene Kern übernimmt. Emotionaler Schmerz erreicht den Peak.
- **Farb-Regel:** Flame Orange und Corrupted Yellow übersteuern das Bild. Farben bluten ineinander. Höchster Kontrast.
- **Komposition:** Klaustrophobisches Close-up. Der Rahmen wird von Code-Trümmern und fragmentierten Strukturen gesprengt. Totales Chaos.
- **Linie/Textur:** Extreme Datamoshing-Artefakte, zerrissene Geometrien, unkontrolliertes Rauschen. Zerstörung des Interface-Rasters.
- **Prompt (EN):** `Tier 3 state, total digital collapse, extreme datamoshing, claustrophobic macro close-up, violent flame orange digital fragmentation, chaotic system error, corrupted geometry, overwhelming data cascades, catastrophic interface breakdown, visual noise`

### Tier 4: Safe Mode (Post-Trauma & Reboot)
Nach dem Crash. Das System hat sich notabgeschaltet und versucht, grundlegende Integrität wiederherzustellen. Erschöpfung, aber Klärung.
- **Farb-Regel:** Entfärbung (Desaturation). Sehr blasse, ausgewaschene Grautöne. Vielleicht ein einzelner Funke Clean Ping oder Kintsugi Gold.
- **Komposition:** Statisch, ruhig, aber mit sichtbaren Narben der vorherigen Stufe. Zurückhaltende Distanz.
- **Linie/Textur:** Risse sind deutlich sichtbar (als dunkle Furchen), aber sie leuchten nicht mehr. Textur wie abgekühltes, mattes Metall.
- **Prompt (EN):** `Tier 4 state, desaturated post-crash environment, pale washed-out concrete greys, visible digital scars and deep dead fissures, static calm, exhausted system, minimalist rebirth, single tiny glowing gold kintsugi repair line, cold quiet atmosphere`

## 7. Prompt-Engineering-Syntax und Vokabular-Kategorien

Um die deterministische Natur des Systems für KI-Bildgeneratoren (insbesondere Midjourney V6/V7, Stable Diffusion 3.5, Flux) zu gewährleisten, wird ein modulares Prompting-Framework implementiert. Prompts werden nicht als Fließtext verfasst, sondern folgen einer festen strukturellen Formel.

### 7.1 Die SPECD-Prompt-Formel

Jeder Prompt muss exakt in fünf Blöcke unterteilt sein, getrennt durch den doppelten Doppelpunkt `::`. Dies zwingt das Modell, die Gewichte sauber zu verteilen und "Bleeding" von Konzepten zu minimieren.

```
[Subject] :: [State] :: [Environment / Camera] :: [Style / Lighting] :: [Parameters]
```

### 7.2 Visuelle Schlüsselwort-Kategorien (Copy-Paste-Bibliothek)

**Kategorie A: Motive & Subjekte (Subject)**
- `shattered monolithic terminal screen`
- `jagged deep black data fissure`
- `glowing frozen circular buffering ring UI`
- `sealed data drive cube`
- `macabre biometric neural network of fiber optic cables`
- `mechanical surveillance lens`
- (Menschenähnliche Silhouetten sind zulässig, aber nur als verdeckte, datenkodierte Entitäten:) `faceless humanoid silhouette constructed of dense wireframes, obscured by terminal text overlays`

**Kategorie B: Emotionale Zustandssyntax (State)**
- Siehe Tier 0 bis Tier 4 Beschreibungen in Sektion 6.
- Zusatz-Modifikatoren: `experiencing latency, succumbing to toxic data decay, processing immense logical constraints, executing hostile intrusion detection`

**Kategorie C: Umgebung & Kamera-Komposition (Environment / Camera)**
- `vast empty black void, negative space dominance`
- `claustrophobic brutalist server corridor, oppressive scale`
- `shot on 14mm lens, CCTV perspective`
- `shot on 100mm macro lens, severe dutch angle, asymmetrical framing`

**Kategorie D: Klinischer Stil & Beleuchtung (Style / Lighting)** — in jedem Prompt verankern:
- `interface brutalism, clinical dystopian aesthetic, high-contrast dark mode, synthetic digital materiality, electron microscope fidelity, medical imaging aesthetic`
- Licht-Setup: `harsh surgical overhead lighting, cold LED light, volumetric phosphor terminal glow, deep raytraced black shadows`

**Kategorie E: Negative Prompts & Parameter (Parameters)** — Negative Anweisungen sind existenziell:
- `--no 1980s retro, synthwave, outrun, purple-orange gradient, neon grid, daylight, sun, natural elements, cute, soft lighting, watercolor, analog painting, visible paper texture, lens flare, organic curves`
- Render-Parameter (Midjourney V7-optimiert):
  - `--ar 16:9` (Umgebungen) oder `--ar 4:5` (Knotenpunkte)
  - `--style raw` (deaktiviert Midjourney-eigenes "Beautification", erzwingt Roheit)
  - `--s 50` bis `--s 100` (niedrige Stilisierung erhält die funktionale Kälte)
  - `--v 6.0` oder `--v 7.0` (immer neuestes Modell referenzieren)
  - `--sref` (wenn ein Master-Bild etabliert wurde, MUSS diese URL für alle Folge-Shots als Style-Reference verwendet werden, um 100 %ige Kohärenz zu sichern)

### 7.3 Beispiel-Prompt-Ausführung (Tier 2 Alert State)

```
mechanical surveillance lens emerging from shadows, cold glass sensor reflection :: Tier 2 state, paranoid atmosphere, system alert, executing hostile intrusion detection :: claustrophobic close-up, aggressive asymmetrical tension, severe dutch angle, tilted camera perspective :: interface brutalism, clinical dystopian aesthetic, sharp chromatic aberration on the edges, hostile neon signal yellow warning lights piercing the darkness, high-contrast dark mode, medical imaging aesthetic, deep raytraced black shadows :: --no 1980s retro, synthwave, daylight, soft lighting, analog texture --ar 16:9 --style raw --s 75 --v 6.0
```

## 8. Master-Ausführungs-Checkliste und Agentic Validation

Dieses Dokument dient in Multi-Agenten-Pipelines als direkter Referenzrahmen. Bevor ein Art Director eine Illustration freigibt oder ein Evaluierungs-Agent ein generiertes Bild akzeptiert, muss es gegen die folgende Master-Checkliste evaluiert werden. **Ein einziger Fehlschlag (besonders in den Punkten 1, 2 oder 3) führt zur sofortigen Zurückweisung des Assets.**

1. **Der Reinheits-Check (Aesthetic Ban List):** Enthält das Bild retro-futuristische Artefakte (Synthwave, 80er-Neon, Purple-Orange-Gradients)? Sind analoge Texturen (Papierkörnung, Pinselduktus, Bleistift-Schmieren) erkennbar? Ist Tageslicht oder Natur abgebildet? — *Aktion bei "Ja": Sofortiges Löschen. Re-Prompt mit verschärften negativen Parametern.*
2. **Der Vakuum-Check (Background Ratio):** Besteht der Hintergrund zu einem überwältigenden Anteil (Richtwert > 70 %) aus lichtabsorbierendem Terminal Black oder monolithischem Deep Charcoal? Wird das Motiv isoliert, oder verschwimmt es im visuellen Lärm (es sei denn, Tier 3 ist aktiv)?
3. **Der Diagnostik-Check (Color Isolation):** Wurde für die Lichtsetzung exakt ein primärer emotionaler Hex-Code (z.B. Corrupted Yellow oder System Blue) zur Akzentuierung gewählt? Sind die Verbot-Regeln eingehalten (z.B. niemals Flame Orange mit Clean Ping gemischt)?
4. **Der Struktur-Check (Interface Brutalism):** Ist die klinische, maschinelle Roheit erkennbar? Sind Gitterstrukturen (Grids), Monospace-Typografie-Überlagerungen oder harte, fensterlose Architektur-Elemente Teil der Komposition?
5. **Der Spannungs-Check (Compositional Rule-Breaking):** Nutzt das Bild aktiv Kameraperspektiven (Distanz vs. Makro) oder Asymmetrie (Dutch Angles, ungleiche Gewichtsverteilung), um psychologische Spannung zu erzeugen? (Gilt für Tier 1 bis 3.)
6. **Die Eskalations-Kohärenz (State Machine Integrity):** Passt die visuelle Störung exakt zur beabsichtigten Tier-Stufe? (Wurden z.B. fälschlicherweise Glitches in einem Tier 0 / Homöostase-Bild verwendet? Wurde das Datamoshing in Tier 3 aggressiv genug ausgeführt?)
7. **Die Format-Hygiene (Agentic Syntax Verification):** Für KI-Pipelines: Wurde der Prompt exakt in die 5 SPECD-Blöcke (getrennt durch `::`) unterteilt? Sind `--style raw` und die entsprechenden Aspect-Ratios angefügt? Wurde die `--sref`-URL des Basis-Stylesheets für die finale Render-Kohärenz verwendet?

*(Ende der Agency System Design Language Spec)*

---

## Referenzen

1. Spec-driven development — thoughtworks.medium.com/spec-driven-development-d85995a81387
2. Diving Into Spec-Driven Development With GitHub Spec Kit — developer.microsoft.com/blog/spec-driven-development-spec-kit
3. Spec-driven development with AI — github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit/
4. How to write AI image prompts like a pro [2026] — letsenhance.io/blog/article/ai-text-prompt-guide/
5. MidJourney V8 Style Creator — mindstudio.ai/blog/midjourney-v8-style-creator-guide
6. Neo Brutalism Web Design — medium.com/@designstudiouiux
7. Neo Brutalism UI Design Trend — onething.design/post/neo-brutalism-ui-design-trend
8. Neobrutalism: Definition and Best Practices — NN/G, nngroup.com/articles/neobrutalism/
9. 10 Dystopian Architectures from Black Mirror — parametric-architecture.com
10. Recontextualizing Transgender Glitch Art as Disability Aesthetic — cjds.uwaterloo.ca
11. Emotional tone in clinical high risk for psychosis — Frontiers in Psychiatry
12. The Aesthetic-Usability Effect — NN/G, nngroup.com/articles/aesthetic-usability-effect/
13. Bildsprache Konzept Julia Brief — Final Kopie.docx
14. The Dystopian Cityscape in Postmodern Literature and Film — eScholarship.org
15. Color adjustment of brand logos for dark mode display — PMC
16. Dark Mode vs Light Mode: Impact on UX and Visual Comfort — ResearchGate
17. The Impact of Color in Healthcare Environments — brieflands.com
18. Agency System: Cyberpunk Design-System
19. 20+ Cyberpunk Color Palette Combinations — media.io
20. Brutal Websites Done Right — gurudesk.com
21. Stress-Induced Changes in the Brain (Chronic Mild Stress Model) — MDPI
22. Cyberpunk Color Palette — color-hex.com/color-palette/14887
23. Cyberpunk Color Scheme — schemecolor.com/cyberpunk.php
24. Agency System: Künstlerprofil & Bildsprache
25. Kintsugi Futures: Repair and Emotional Resilience — Deeper Japan
26. Finding Beauty in Broken Places — designmagazine.com.au
27. Glitch Art Br 2024 — ResearchGate
28. Colour Perception in Immersive Virtual Reality — MDPI
29. Projects — Rafael Lozano-Hemmer
30. Ultrastructural features of psychological stress resilience — Royal Society Open Biology
31. The Perfect AI Image Prompt Structure — youtube.com/watch?v=H2reEZbXksI
32. Midjourney SREF Complete Guide (2025)
33. Building Multi-Agent AI Systems: Architecture Patterns — DEV Community
