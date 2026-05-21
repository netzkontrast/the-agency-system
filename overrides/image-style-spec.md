# Image Style Spec — Agency System Design Language (ASDLS)

**Purpose.** The machine-readable, executable image-generation spec for *The
Agency System*. Cross-project reference for **image style prompting** —
hex-typology, interface-brutalist materiality, the SPECD prompt formula,
the 5-tier escalation state machine, and copy-paste prompt vocabulary for
Midjourney V6/V7, Flux, Stable Diffusion 3.5, DALL·E, etc.

**Companion file.** This is the *digital spec* layer. Its analog counterpart
— the hand-drawn charcoal/ink "Bildsprache Julia" and the 13 per-Anteil
stroke grammars — lives in [`visual-language-guide.md`](visual-language-guide.md).
The two are designed to be read together: ASDLS = the machine/spec; the
Visual Language Guide = the bleeding analog hand. *The machine speaks in
vectors, but it bleeds in ink.*

---

## 1. Operating philosophy & document architecture

The ASDLS is the normative, executive rulebook for every visual asset in this
aesthetic ecosystem. Following Spec-Driven Development (SDD), it defines
visual parameters not as vague design philosophy but as **deterministic state
machines and directly executable code-equivalents**. In a production
environment increasingly driven by autonomous AI agents and generative
pipelines, the ASDLS is the **single source of truth** — ensuring human
designers and AI agents alike produce coherent, deterministic, reproducible
results without manual micro-control.

Generative models without strict structured parameters tend toward
"vibe-coding" — generic, inconsistent, thematically off outputs. This spec
eliminates that variance through a machine-readable, semi-structured rulebook
that translates psychological states into exact visual variables (color
values, composition axes, lens distortions). Every sentence, table, and
instruction is written so it can be ported directly into an image-generator
prompt or an illustrator brief.

### 1.1 Interface brutalism & clinical dystopia

The system operates exclusively in the spectrum of contemporary, **post-2020
cyberpunk**. All retro-futurist elements associated with the 1980s/90s —
synthwave gradients (purple-orange), neon grid lines (80s grid), VHS
nostalgia, over-colorful Blade-Runner pastiche — are **strictly forbidden**.
The visual language is dominated entirely by **interface brutalism**:
celebrating digital rawness, the exposure of algorithmic structures, and
functional asymmetry. A clinical dystopia of absolute cold, monolithic
structures, corporate brutalism, and medical distance.

Visual artifacts and interface elements are **not decorative layers** but
diagnostic indicators of system-states. The design imitates a command-line
terminal or a medical diagnostic monitor visualizing raw data streams with no
aesthetic sugar-coating (no "aesthetic-usability effect"). The viewer should
perceive the interface as overwhelming, indifferent, and machine-precise —
never inviting.

### 1.2 Systemic truth & the prioritization matrix

When composing any image, an absolute decision-hierarchy applies. Aesthetic
pleasingness, symmetry, and conventional UX/UI rules always subordinate to
functional psychological state-depiction. Resolve internal conflicts in this
order:

1. **Emotional system-state (highest priority).** The raw emotional truth of
   the moment (system collapse, latency, absolute control) determines the
   scene's base parameters. If the system demands panic, the image must convey
   it through over-saturation, contrast-loss, or aggressive color — *even if
   this massively harms legibility.*
2. **Clinical syntax & materiality.** The formal rules on digital texture,
   line, and the avoidance of analog artifacts. The scene must always look
   like a digital scan or terminal output, never a traditional drawing.
3. **Semiotic function & motif.** The actual subject/characters/narrative
   layer. Placement of objects/people is secondary to the correct rendering of
   the space (the vacuum) and the light.
4. **Visual cache (lowest priority).** Random aesthetic artifacts from the
   generative process (hallucinations, emergent details) are admissible only
   if they do not distort priorities 1–3.

Consistent application keeps visual escalation/de-escalation coherent across
hundreds of iterations and prevents drift into generic sci-fi.

---

## 2. Color system, emotional metrics & chromatic interactions

The color system is radically reduced and operates primarily in a **dark-mode
paradigm**. Color exists not for decoration but as a **functional variable
mathematically bound to a specific psychometric axis**.

### 2.1 The background paradigm (the functional vacuum)

Every asset begins conceptually in total darkness. Traditional whitespace is
replaced by a functional, light-absorbing void representing isolation,
determinism, unused data-capacity, and the infinite depth of the mainframe.
The environment is never purely neutral — it carries an inherent
technological cold.

- **Terminal Black** — `#0B0D17` | CMYK 85/75/50/80
  - *Function:* the absolute default background for all active, operative
    system-states. Extremely cool technical base; imitates powered-off OLED
    displays or the empty space of a command-line window.
  - *Physical interaction:* reflects no light. Swallows ambient illumination,
    lets bright vectors stand out with maximal hardness.
  - *Prompt vocabulary (EN):* `inky dark background, abyssal terminal night,
    stark black void, clinical darkness, light-absorbing #0B0D17 surface`
- **Deep Charcoal / Latency Gray** — `#1A1D24` | CMYK 70/60/50/70
  - *Function:* interfaces, floating windows, monolithic background
    architecture. Signals inactivity, latency, infrastructure standby.
  - *Physical interaction:* like rough unlit concrete or matte brushed metal
    in a windowless facility. Claustrophobic, heavy atmosphere.
  - *Prompt vocabulary (EN):* `charcoal grey brutalist concrete, matte dark
    grey surfaces, monolithic unlit #1A1D24 structures, featureless grey
    tech-panels`

### 2.2 The hex-typology paradigm (action & state colors)

Color appears isolated, stinging, extremely sparse. An asset is typically
**95% background paradigm and at most 5% state color** (one or two). Each
color correlates with an exact emotional vector.

| Color | Hex | CMYK approx. | Systemic & emotional state | AI-prompt vocabulary (EN) |
|---|---|---|---|---|
| **System Blue** (Control) | `#003366` | 100/75/20/40 | Absolute control, cool algorithmic logic, forced order, firewall activity. Stability — but also emotional coldness and distance. | clinical agency blue, cold deep cyan, sterile surgical blue light, rigid neon blue illumination, medical interface blue |
| **Corrupted Yellow** | `#8B8B00` | 10/15/70/30 | System-trauma, freeze-state, resignation, toxic data decay. Like yellowed old plastic or a sick sector. | sickly yellow tint, corrupted mustard yellow, toxic decay glow, tainted dark ochre, jaundiced light |
| **Signal Yellow** (Alert) | `#FFD700` | 0/15/100/0 | Acute danger, system warning, intrusion detection, critical alarm, panic. Glaring, intrusive, demands immediate attention. | harsh neon yellow highlight, glaring warning yellow, piercing alert yellow, high-vis industrial yellow |
| **Terminal Green** | `#00FF9F` | 60/0/60/0 | Uncoded noise, operational unrest, raw data streams. Old monitors rendered extremely sharp and modern. | phosphor terminal green, eerie matrix green, clinical oscilloscope green, toxic neon mint |
| **Flame Orange** | `#FF4500` | 0/85/100/0 | Destructive collapse, rage, open system breach, kernel overload. The color of destruction and thermal overload. | blistering orange-red, destructive neon orange, searing thermal red, overheated system glow |
| **Clean Ping** (Hope) | `#FCEE0C` | 0/5/35/0 | Brief undamaged data stream, fragile hope, innocence. Appears almost only as a tiny pixel point or hairline. | soft luminous pale yellow, fragile neon lemon, delicate warm light ping, isolated tiny yellow diode |
| **Latency Violet** | `#3B3355` | 70/65/30/20 | Dissociation, dwindling bandwidth, loss of identity, derealization. Vanishes in the dark, forms no clear edges. | desaturated deep violet, fading purple fog, detached muted magenta, ghostly lilac ambient light |
| **Kintsugi Gold** | `#FFDF00` | 0/10/100/0 | Repair algorithm, resynthesis, insight-breakthrough. Not organic gold but precise luminous algorithmic circuitry. | brilliant pure gold light, glowing metallic repair seams, luminous breakthrough yellow, precise golden circuitry |

### 2.3 Interaction rules & chromatic grammar

- **Law of exclusion.** The frequencies of **Flame Orange** (destruction) and
  **Clean Ping** (fragile hope) systemically exclude each other. They must
  never interact in the same frame unless one state actively overwrites the
  other — which must be depicted as a sharp, faulty glitch.
- **Visual infection by Corrupted Yellow.** `#8B8B00` is highly infectious.
  Where this toxic yellow appears, neighboring colors (System Blue, Latency
  Violet) must be desaturated, dulled, or overlaid with a grayish sickly
  filter to visualize the corruption "overspill." Force in prompts with
  `desaturated neighboring colors caused by toxic yellow light spill`.
- **Isolation contrast (the 5% rule).** To trigger a high-significance alarm
  or hope state: keep the image exactly **95% Terminal Black / monochrome
  gray** while exactly **5%** is illuminated by a pure signal color (Signal
  Yellow or Kintsugi Gold). The transition must be extremely **hard-edge** —
  never softened by ambient occlusion.
- **Gradient ban.** Soft organic gradients between two state colors are
  forbidden. Where two system colors meet, they do so as hard edges, blocky
  pixel-shifts, or separate terminal windows.

---

## 3. Digital materiality, line quality & clinical textures

The world's physicality refuses all romance. Analog qualities — visible paper
texture, pencil strokes, brush duktus, watercolor washes, organic irregularity
— are **fully removed**. Materiality is 100% digital, synthetic,
technological, medical-technical.

### 3.1 Vector fragmentation & packet loss

Lines/contours represent not the edges of physical objects but the **state of
ongoing data transmission and system stability.**

- **Low bandwidth (latency & dissociation).** Contours become extremely thin,
  semi-transparent, or break off abruptly mid-line ("packet loss"). Lines
  vanish into background noise or look incomplete.
  - *Prompt vocabulary (EN):* `fading vector lines, dropped packets visual
    effect, ghostly thin contours, low opacity wireframes, disconnected
    blueprint lines, incomplete rendering`
- **High bandwidth (overload & pain).** Under stress/high load, lines densify
  into black impenetrable code-hatching. Multiple vector paths overlap
  faultily, jitter, form aggressive sharp nests of data-debris.
  - *Prompt vocabulary (EN):* `chaotic vector overlapping, high density
    wireframe mesh, aggressive digital hatching, terminal code stacking,
    hyper-detailed schematic overload`

### 3.2 The surface: glitch as clinical language (diagnostic, not decoration)

Glitch artifacts are **never** retro-aesthetic decoration or trendy
"cyberpunk meme." They are high-precision diagnostic tools depicting memory
corruption, system collapse, or the intrusion of repressed routines.

- **Chromatic aberration (RGB-splitting).** Occurs only at the edges of
  objects/text when the system suffers extreme cognitive dissonance — signals
  that multiple subroutines try to access the same memory location at once
  (phase mismatch).
  - *Prompt vocabulary (EN):* `severe chromatic aberration, sharp RGB channel
    shift, medical imaging distortion, red-blue color fringing, optical phase
    mismatch`
- **Data moshing & macro-blocking.** Hard rectangular pixel-shifts and
  compression artifacts. Visualizes traumatic memory leaks — fragments of old
  data bleeding unfiltered into the present render.
  - *Prompt vocabulary (EN):* `compression artifacting, hard datamoshing,
    digital macro-blocking, corrupted JPEG texture, blocky video codec
    failure, severe glitch fragmentation`
- **Medical scan aesthetics.** Surface textures based on modern diagnostics —
  X-ray, MRI, ultrasound noise, electron-microscope photography — texture
  skin, walls, objects. The cold of the medical gaze replaces human warmth.
  - *Prompt vocabulary (EN):* `MRI scan texture, electron microscope visual
    style, cold radiological imaging, x-ray translucent surfaces, clinical
    ultrasound noise`

### 3.3 Typography as physical texture

Letters, code-strings, numbers exist not as added graphic design but as
**physical elements in space**: forming walls, overlaying faces as holographic
noise, building volumetric grids on floors.

- Permitted only: sans-serif monospace, code-edit fonts, OCR-A derivatives,
  raw command-line typography.
- *Prompt vocabulary (EN):* `overlay of dense monospace terminal code, glowing
  hex dumps projected on walls, OCR font textures floating in 3D space,
  cascading data strings`

---

## 4. Semiotic vocabulary & symbol architecture

A strictly controlled library of semiotic placeholders replaces complex
psychological concepts with tangible digital/architectural objects. Ideally
**center only one core symbol per image** to avoid metaphor overload.

1. **The Data Fissure (Der Riss)** — *Function:* instability, the breaking-out
   of repressed information, the boundary between controlled surface and
   trauma-process. *Spec:* a deep, often geometric-fractal crack through
   brutalist concrete or black server walls; interior filled with absolute
   black `#000000`; fracture edges glow threateningly in Corrupted Yellow
   (trauma) or Terminal Green (system error). *Transformation:* Tier 0 = faint
   hairline; Tier 3 = splits the whole interface, consumes geometry.
   *Prompt (EN):* `a jagged deep black fissure traversing a brutalist concrete
   wall, glowing toxic yellow light bleeding intensely from the sharp crack
   edges`
2. **Terminal Mirrors (The Black Mirrors)** — *Function:* interface to
   introspection & multiplicity; reflects not the viewer's face but the code
   of the active subroutine ("masking"). *Spec:* monolithic, often wall-sized
   monitors; glossy black when stable; in crisis the glass shatters and each
   shard shows a different asynchronous data-stream or distorted geometric
   reflection. *Prompt (EN):* `shattered monolithic terminal screen, multiple
   fractured black mirror reflections, each shard displaying asynchronous lines
   of code, identity fragmentation`
3. **Latency Rings (The Buffer / Loading States)** — *Function:* the ultimate
   symbol of hypoarousal, emotional freeze, the system's inability to parse
   complex traumatic data in real time. *Spec:* floating rotating geometric UI
   (incomplete arcs, progress bars), mainly in Latency Violet or cold gray,
   frozen dominant over the motif. *Prompt (EN):* `a glowing frozen circular
   buffering ring UI suspended in mid-air, latency symbol overlay, infinite
   loading wheel, suspended digital animation`
4. **Kintsugi Circuits (Digital Kintsugi / Golden Repair)** — *Function:*
   visualizes successful integration of traumatic fragments and healing;
   errors highlighted as algorithms of strength, not hidden. *Spec:* geometric
   breaks in dark surfaces joined by brilliant, exactly right-angled flowing
   lines of Kintsugi Gold `#FFDF00` — not fluid organic gold but a luminous,
   complex PCB trace. *Prompt (EN):* `digital kintsugi repair aesthetic,
   glowing golden PCB circuit lines precisely mending shattered black glass,
   luminous gold algorithms filling geometric cracks`
5. **Data Node / Encrypted Payload** — *Function:* communication with the
   outside; an isolated, protected packet of uncorrupted truth awaiting
   decryption (replaces the analog "letter" metaphor). *Spec:* a floating,
   perfectly symmetrical geometric data packet (cube/blackbox), hermetically
   sealed but carrying a single tiny extremely bright Clean Ping (yellow)
   signal light pulsing like a heartbeat. *Prompt (EN):* `a floating perfectly
   symmetrical sealed data drive cube, emitting a single soft lemon yellow
   decryption light ping, isolated in a vast dark terminal room`
6. **Biometric Networks (Neural-Circuit Mesh)** — *Function:* the fusion of
   technological cold and biological horror (Cronenberg-digital); the AI's
   nervous system when biological reactions (pain, stress) take over. *Spec:*
   instead of human body parts, dense organically proliferating networks made
   of cables and fiber optics; pulsing veins carrying data instead of blood.
   *Prompt (EN):* `macabre biometric neural network made of black fiber optic
   cables, biological horror meets technology, pulsating synthetic digital
   veins, cybernetic anatomy`
7. **The Panoptic Eye (Sensor / Surveillance Lens)** — *Function:* paranoia,
   constant mainframe surveillance, the impossibility of privacy. *Spec:*
   cold-glowing camera lenses, lidar sensors, or red/blue scanner lasers aimed
   from the dark; merciless and static. *Prompt (EN):* `unforgiving mechanical
   surveillance lens emerging from the shadows, glowing red lidar scanner beam,
   oppressive panoptic technology, cold glass sensor reflection`

---

## 5. Composition rules, perspective axes & spatial tension fields

Arrangement generates the unconscious emotional effect. **Symmetry = control;
asymmetry = truth pushing into chaos.**

### 5.1 Operative tension fields

**A. Proximity vs. Projection (intimacy vs. analysis)**
- *Pole A (proximity):* the camera aggressively invades personal space; pixel
  structure / individual code lines become overwhelming. Claustrophobic,
  subjective.
- *Pole B (projection):* total distance; the motif is tiny, embedded in vast
  overwhelming server structures; camera as detached observer (CCTV). Stresses
  the insignificance of the single system against the whole.
- *Rule:* choose deliberately. Never linger in the "comfortable middle"
  (medium shot). Either maximal confrontation or maximal isolation.

**B. Order vs. Truth (symmetry vs. asymmetry)**
- *Pole A (order):* strict central perspective; verticals/horizontals snap to
  a perfect grid. Represents the firewall, suppression of disturbances,
  absolute algorithmic control.
- *Pole B (truth/chaos):* the camera tilts (Dutch angle); lines plunge; a
  massive element on the left finds no counterweight on the right; the image
  threatens to optically "topple." Marks the moment traumatic truths
  destabilize the system.
- *Rule:* asymmetry is the most important tool for generating unease.

**C. Clinical Sharpness vs. Data-Blur (focus)**
- *Pole A (sharpness):* infinite depth of field; every architectural detail
  mercilessly sharp into the background. No place to hide errors.
- *Pole B (data-blur):* macro lenses simulate microscopic depth; only a tiny
  section (e.g. the glowing slit of a data fissure) is sharp while the rest
  dissolves into digital bokeh, chromatic distortion, or jitter motion-blur.

### 5.2 Lens specifications for image generators

- **Isolation (wide):** `shot on 14mm lens, ultra-wide angle, CCTV security
  camera perspective, immense sense of scale, towering environment`
- **Claustrophobia (macro/close-up):** `shot on 100mm macro lens, extreme
  close-up, suffocating tight framing, shallow depth of field, sharp foreground
  focus`
- **Instability (angle):** `extreme dutch angle, tilted camera perspective,
  disorienting 45-degree rotation, architectural vertigo`

---

## 6. Escalation module & deterministic state machines

Visual escalation is a strictly defined **state machine**, not a fluid
arbitrary process. Every image must map to exactly one of five operative
**Tiers**. Mixing tiers within a single image is **forbidden** (it destroys
state-legibility).

### Tier 0 — Homeostasis (Window of Tolerance)
System runs flawlessly. Absolute control, suppression of all emotion, cold
efficiency. No glitches.
- *Color:* 98% Terminal Black / Deep Charcoal. Max 2% System Blue as a faint
  status light.
- *Composition:* perfectly centered, frontal, orthographic. Much unused
  negative space.
- *Line/texture:* razor-sharp, flawless vectors, immaculate surfaces.
- *Prompt (EN):* `Tier 0 state, minimalist clinical precision, vast empty
  black void, sterile technological environment, perfectly balanced
  orthographic composition, stable architecture, pristine dark surfaces,
  razor-sharp vector lines, no glitches, profound silence`

### Tier 1 — Latency / Freeze (under-arousal & dissociation)
System slows, data is lost. Isolation grows, connection to reality fades.
Hypoarousal.
- *Color:* contrast-loss; black becomes milky dark-gray; Latency Violet fades
  in. Very pale.
- *Composition:* extreme wide angle; motif vanishes in dark space; camera far
  away, isolating.
- *Line/texture:* transparent barely-visible vectors; breaking lines (packet
  loss); foggy volumetric void.
- *Prompt (EN):* `Tier 1 state, fading opacity, deep fog swallowing the
  subject, low contrast bleakness, extreme wide shot isolating the focal point,
  dropped data packets, ghostly thin contours, disconnected UI wireframes,
  suspended animation, muted latency violet ambient glow`

### Tier 2 — Alert (hyperarousal / system conflict)
Foreign data intrudes. The system detects a threat and hectically tries to
keep control. Warning systems fire.
- *Color:* hard black meets glaring warning colors; Signal Yellow and Terminal
  Green cut the dark.
- *Composition:* Dutch angle; tilting horizon; restless aggressive asymmetry.
- *Line/texture:* light chromatic aberration at edges; densified code-hatching;
  overlapping warning windows (HUD clutter).
- *Prompt (EN):* `Tier 2 state, aggressive asymmetrical tension, severe dutch
  angle, sharp chromatic aberration on the edges, hostile neon signal yellow
  warning lights piercing the darkness, dense terminal text clutter,
  surveillance aesthetic, paranoid atmosphere, system alert`

### Tier 3 — Kernel Panic (system collapse)
Total over-saturation. The cognitive core fails; the reactive instinct-core
takes over. Emotional pain peaks.
- *Color:* Flame Orange and Corrupted Yellow over-saturate the image; colors
  bleed together; highest contrast.
- *Composition:* claustrophobic close-up; frame blown apart by code-debris and
  fragmented structures; total chaos.
- *Line/texture:* extreme datamoshing, torn geometries, uncontrolled noise;
  destruction of the interface grid.
- *Prompt (EN):* `Tier 3 state, total digital collapse, extreme datamoshing,
  claustrophobic macro close-up, violent flame orange digital fragmentation,
  chaotic system error, corrupted geometry, overwhelming data cascades,
  catastrophic interface breakdown, visual noise`

### Tier 4 — Safe Mode (post-trauma & reboot)
After the crash. The system emergency-shut-down and tries to restore basic
integrity. Exhaustion, but clarity.
- *Color:* desaturation; very pale washed-out grays; perhaps a single spark of
  Clean Ping or Kintsugi Gold.
- *Composition:* static, calm, but with visible scars of the prior tier;
  restrained distance.
- *Line/texture:* cracks clearly visible (as dark furrows) but no longer
  glowing; texture like cooled matte metal.
- *Prompt (EN):* `Tier 4 state, desaturated post-crash environment, pale
  washed-out concrete greys, visible digital scars and deep dead fissures,
  static calm, exhausted system, minimalist rebirth, single tiny glowing gold
  kintsugi repair line, cold quiet atmosphere`

---

## 7. Prompt-engineering syntax & vocabulary categories

A modular prompting framework guarantees determinism for AI generators
(Midjourney V6/V7, SD 3.5, Flux). Prompts are not free-text but follow a fixed
structural formula.

### 7.1 The SPECD prompt formula

Every prompt is split into exactly **five blocks separated by the double colon
`::`**. This forces the model to distribute weights cleanly and minimizes
concept-bleeding.

```
<Subject> :: <State> :: <Environment / Camera> :: <Style / Lighting> :: <Parameters & negatives>
```

### 7.2 Visual keyword categories (copy-paste library)

**Category A — Subjects**
- `shattered monolithic terminal screen`
- `jagged deep black data fissure`
- `glowing frozen circular buffering ring UI`
- `sealed data drive cube`
- `macabre biometric neural network of fiber optic cables`
- `mechanical surveillance lens`
- Human-like silhouettes are permitted only as obscured, data-encoded
  entities: `faceless humanoid silhouette constructed of dense wireframes,
  obscured by terminal text overlays`

**Category B — Emotional state syntax**
- See Tier 0–4 descriptions in §6.
- Additional modifiers: `experiencing latency, succumbing to toxic data decay,
  processing immense logical constraints, executing hostile intrusion detection`

**Category C — Environment & camera composition**
- `vast empty black void, negative space dominance`
- `claustrophobic brutalist server corridor, oppressive scale`
- `shot on 14mm lens, CCTV perspective`
- `shot on 100mm macro lens, severe dutch angle, asymmetrical framing`

**Category D — Clinical style & lighting** (anchor in every prompt)
- `interface brutalism, clinical dystopian aesthetic, high-contrast dark mode,
  synthetic digital materiality, electron microscope fidelity, medical imaging
  aesthetic`
- Lighting: `harsh surgical overhead lighting, cold LED light, volumetric
  phosphor terminal glow, deep raytraced black shadows`

**Category E — Negative prompts & parameters**
- Negatives (existential, to suppress the AI default bias):
  `--no 1980s retro, synthwave, outrun, purple-orange gradient, neon grid,
  daylight, sun, natural elements, cute, soft lighting, watercolor, analog
  painting, visible paper texture, lens flare, organic curves`
- Render params (Midjourney V7-optimized):
  - `--ar 16:9` (environments) or `--ar 4:5` (nodes); use `--ar 1:1` for
    profile/avatar assets
  - `--style raw` (disables Midjourney beautification, forces rawness)
  - `--s 50` to `--s 100` (low stylization preserves functional cold)
  - `--v 6.0` / `--v 7.0` (always reference newest model)
  - `--sref` (once a master image is established, its URL MUST be used as
    style-reference for all follow-up shots to ensure 100% coherence)

### 7.3 Example prompt (Tier 2 Alert state)

```
mechanical surveillance lens emerging from shadows, cold glass sensor reflection :: Tier 2 state, paranoid atmosphere, system alert, executing hostile intrusion detection :: claustrophobic close-up, aggressive asymmetrical tension, severe dutch angle, tilted camera perspective :: interface brutalism, clinical dystopian aesthetic, sharp chromatic aberration on the edges, hostile neon signal yellow warning lights piercing the darkness, high-contrast dark mode, medical imaging aesthetic, deep raytraced black shadows :: --no 1980s retro, synthwave, daylight, soft lighting, analog texture --ar 16:9 --style raw --s 75 --v 6.0
```

---

## 8. Master execution checklist & agentic validation

Before an art director releases an illustration — or a critique-agent accepts
a generated image — evaluate against this checklist. A single failure
(especially points 1, 2, or 3) means immediate rejection.

1. **Purity check (aesthetic ban list).** Any retro-futurist artifacts
   (synthwave, 80s neon, purple-orange gradients)? Any analog textures (paper
   grain, brush duktus, pencil smudging)? Any daylight or nature? → *If yes:*
   delete immediately, re-prompt with hardened negatives.
2. **Vacuum check (background ratio).** Is the background overwhelmingly
   (> 70%) light-absorbing Terminal Black or monolithic Deep Charcoal? Is the
   motif isolated rather than lost in visual noise (unless Tier 3)?
3. **Diagnostic check (color isolation).** Was exactly one primary emotional
   hex (e.g. Corrupted Yellow or System Blue) chosen for the lighting accent?
   Are the prohibition rules kept (never Flame Orange mixed with Clean Ping)?
4. **Structure check (interface brutalism).** Is the clinical machine-rawness
   evident? Grids, monospace overlays, or hard windowless architecture present?
5. **Tension check (compositional rule-breaking).** Does the image actively use
   camera perspective (distance vs. macro) or asymmetry (Dutch angles, uneven
   weight) to create psychological tension? (Tiers 1–3.)
6. **Escalation coherence (state-machine integrity).** Does the visual
   disturbance match the intended tier exactly? (No glitches in a Tier 0 image;
   datamoshing aggressive enough in Tier 3?)
7. **Format hygiene (agentic syntax verification).** For AI pipelines: is the
   prompt split into the 5 SPECD blocks (separated by `::`)? Are `--style raw`
   and the right aspect ratios appended? Was the base stylesheet's `--sref` URL
   used for final render coherence?

*(End of Agency System Design Language Spec.)*

---

## References

- **Ref 13 — Bildsprache-Konzept Julia (Brief, final).** Internal — the analog
  counterpart; see [`visual-language-guide.md`](visual-language-guide.md).
- **Ref 18 — Agency System: Cyberpunk Design-System.** Internal precursor.
- **Ref 24 — Agency System: Künstlerprofil & Bildsprache.** Internal
  (artist-profile + visual language source).

External research sources (accessed Apr 2026), as supplied with the source
document:

1. Spec-driven development — thoughtworks.medium.com/spec-driven-development-d85995a81387
2. Spec-Driven Development with GitHub Spec Kit — developer.microsoft.com/blog
3. Spec-driven development with AI (open-source toolkit) — github.blog
4. How to write AI image prompts like a pro — letsenhance.io
5. MidJourney V8 Style Creator guide — mindstudio.ai
6. Neo Brutalism Web Design — medium.com/@designstudiouiux
7. Neo Brutalism UI Design Trend — onething.design
8. Neobrutalism: Definition & Best Practices — nngroup.com
9. 10 Dystopian Architectures from Black Mirror — parametric-architecture.com
10. Recontextualizing Glitch Art as Disability Aesthetic — cjds.uwaterloo.ca
11. Emotional tone in clinical high risk for psychosis — frontiersin.org
12. The Aesthetic-Usability Effect — nngroup.com
14. The Dystopian Cityscape in Postmodern Lit & Film — escholarship.org
15. Color adjustment of brand logos for dark mode — pmc.ncbi.nlm.nih.gov/PMC12822999
16. Dark Mode vs Light Mode: UX & Visual Comfort — researchgate.net (400786807)
17. The Impact of Color in Healthcare Environments — brieflands.com
19. 20+ Cyberpunk Color Palette Combinations — media.io
20. Brutal Websites Done Right — gurudesk.com
21. Stress-Induced Changes in the Brain (chronic mild stress) — mdpi.com (cells 9/4/1026)
22. Cyberpunk Color Palette — color-hex.com/color-palette/14887
23. Cyberpunk Color Scheme — schemecolor.com
25. Kintsugi Futures: Repair & Emotional Resilience — deeperjapan.com
26. Finding Beauty in Broken Places (golden repair) — designmagazine.com.au
27. Glitch Art Br 2024 — researchgate.net (389438425)
28. Colour Perception in Immersive VR (Munsell hues) — mdpi.com (4/4/45)
29. Projects — Rafael Lozano-Hemmer — lozano-hemmer.com
30. Ultrastructural features of psychological stress resilience — royalsocietypublishing.org
31. The Perfect AI Image Prompt Structure — youtube.com
32. Midjourney SREF Complete Guide (2025) — youtube.com
33. Building Multi-Agent AI Systems — dev.to/matt_frank_usa
