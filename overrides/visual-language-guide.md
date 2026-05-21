# Visual Language Guide — the Agency System

**Purpose.** The cross-project *visual grammar* of the Agency System — the
**WHY/WHAT** of how this DID-system universe looks. It governs every visual
output across the project: novel cover art, album covers, per-track art,
profile/brand imagery, promo visuals. It is **album-agnostic**: it describes
the language's full capability, not any single release. Mine it whenever an
illustration needs to read as an honest *state-diagnosis of the psyche*
rather than a generic sci-fi image.

**Scope boundary (read this first).** This file is the **grammar** — the
state→tier→colour state machine, glitch-as-clinical-symptom, the per-function
visual fingerprints, composition principles. It does **not** teach prompt
construction. The prompt-writing **HOW** — the SPECD `::` formula, the
copy-paste keyword library, camera/lens prompting, negative-prompt and
render parameters — lives in **`overrides/image-style-spec.md`**. Describe the
grammar here; go there to build a prompt.

**name_exposure (hard rule).** In music and design outputs use
**function/role only**. A personal name (host's name, fighter's name, etc.)
must never reach a lyric, Suno metatag, promo field, or art prompt — that is
a CRITICAL defect. Personal names belong to the novel layer alone. Every
fingerprint below is keyed to the **function/archetype**, never the name.

**Cross-project framing.** Two source paradigms fuse here. The **ASDLS**
(Agency System Design Language Spec) supplies the deterministic, algorithmic
"interface-brutalist" digital law: dark voids, raw geometric edges, clinical
hardness, glitch-as-diagnostics. The **analog Bildsprache** supplies symbolic
expressionism and haptic, vulnerable materiality — the faltering, trembling
analog stroke. The product is a hybrid: digital system-states made physically
tangible. *The machine speaks in vectors, but it bleeds in ink.*

The conceptual frame is a **monolithic concrete bunker** that is at once an
infinite digital server room and the isolated refuge of a traumatized psyche.
Interface brutalism — radical asymmetry, light-absorbing voids, clinical
coldness — is decoded as a **psychological defense mechanism**: the thick,
impenetrable walls of dissociation. Yet the system breathes and suffers. The
paper becomes the body, the pen becomes the seismograph of the soul: when the
system suffers the paper tears under the tool; when it overheats the ink
smears and bleeds into the pulp.

> **Capability, not mandate.** The S0–S4 state axis (below) is the language's
> full range. A given album may live entirely in S0–S2, or have **no
> repair/Kintsugi (S4) at all**. Treat S4 / Kintsugi Gold as something the
> language *can* render, never as a required ending.

---

## 1. Colour thermodynamics — palette + the 5% rule

Colour is a **functional variable bound to a psychometric axis, never
decoration**. Every asset begins conceptually in total darkness; the white
space of traditional layout is replaced by a functional, light-absorbing void
(isolation, determinism, the infinite mainframe). State colour is sparse and
stinging.

### Substrate (the neutral void — ~95% of every frame)

| Colour | Hex | Reads as |
|---|---|---|
| **Terminal Black** | `#0B0D17` | Default operative background; isolation, infinite mainframe depth. Reflects no light; lets bright vectors hit with maximum hardness |
| **Deep Charcoal / Latency Gray** | `#1A1D24` | Inactivity, latency, infrastructure standby; raw unlit brutalist concrete, matte brushed metal |

### State colours (the telemetry palette — ≤5% of the frame)

| Colour | Hex | Signals |
|---|---|---|
| **System Blue** (Control) | `#003366` | Absolute control, cold logic, firewall; stability + emotional coldness |
| **Corrupted Yellow** | `#8B8B00` | Trauma, freeze, resignation, toxic decay; turbid jaundiced ochre — *infectious* |
| **Signal Yellow** (Alert) | `#FFD700` | Acute danger, intrusion detection, panic; glaring neon line tearing the retina |
| **Terminal Green** | `#00FF9F` | Uncoded noise, operational unrest, raw data streams; phosphor/oscilloscope green |
| **Flame Orange** | `#FF4500` | Destructive collapse, rage, kernel overload, thermal breach |
| **Clean Ping** (Hope) | `#FCEE0C` | Fragile undamaged stream, innocence; appears only as a tiny pixel or hairline |
| **Latency Violet** | `#3B3355` | Dissociation, dwindling bandwidth, identity loss, derealization; vanishes into dark, forms no clear edge |
| **Kintsugi Gold** | `#FFDF00` | Repair algorithm, integration, insight-breakthrough; *precise luminous PCB circuitry*, never organic gold |

### The 5% rule and chromatic grammar

- **95/5 split.** An asset is ~95% Terminal Black / monochrome grey and at
  most ~5% one (occasionally two) state colour. Maximal contrast-isolation
  forces the eye onto the one significant accent.
- **Hard-edge only — gradient ban.** No soft organic transitions between two
  state colours. Where two system colours meet they do so as hard edges,
  blocky pixel-shifts, or separated terminal windows. Never softened by
  ambient occlusion.
- **Infection by Corrupted Yellow.** `#8B8B00` is highly infectious: when it
  appears, neighbouring colours (System Blue, Latency Violet) must be
  desaturated, dulled, or greyed to show the corruption overspill.
- **Law of exclusion.** Flame Orange (destruction) and Clean Ping (fragile
  hope) never share a frame unless one actively overwrites the other as a
  sharp glitch.
- **Analog clash.** In the haptic translation, colour is a *driving emotional
  force*: wet flowing paint bleeding into a dry charcoal drawing, or a hard
  coloured-pencil line scratching through soft graphite, stages the war
  between ordering system-logic (the hard line) and flooding emotion (the
  flowing colour). When Corrupted Yellow meets a frozen part's Frostbite Cyan,
  a sickly pale green signals the collapse of psychic defenses.

---

## 2. The state → tier → colour state machine (S0–S4)

Visual escalation is a strict **state machine**, never a freeform gradient.
Every image maps to exactly one tier; **mixing tiers within one image is
forbidden** — it destroys the legibility of the system-state. States map 1:1
across all three layers (music / novel / design); design reads the state as
the ASDLS tier + signature hex + glitch intensity.

| State | Name | ASDLS tier | Signature hex / band | What the frame does |
|---|---|---|---|---|
| **S0** | Homöostase | **T0** | System Blue `#003366` (≤2% status dot) | Flawless control, suppressed emotion. No glitches; razor-sharp vectors; pristine surfaces. Perfectly centred orthographic composition; vast unused negative space |
| **S1** | Latenz / Freeze | **T1** | Latency Violet `#3B3355` | Hypoarousal, dissociation, dwindling bandwidth. Contrast loss — black milks to dark grey; transparent fading vectors, packet-loss line breaks. Extreme wide shot; motif lost in volumetric fog |
| **S2** | Alert / Konflikt | **T2** | Signal Yellow `#FFD700` (with Terminal Green) | Threat detected; warning systems fire. Hard black meets glaring warning colour. Dutch angle, aggressive asymmetry; *light* chromatic aberration at edges; densified hatching, HUD clutter |
| **S3** | Kollaps-Peak | **T3** | Flame Orange `#FF4500` / Corrupted Yellow | Total override; cognitive core fails, instinct takes over. Colours bleed, highest contrast. Claustrophobic macro close-up; extreme datamoshing, torn geometry, grid destruction |
| **S4** | Repair / Integration | **T4** | Kintsugi Gold `#FFDF00` (or a single Clean Ping) | Post-crash safe mode; exhausted clarity. Desaturation, pale washed-out greys. Scars visible as dead furrows — no longer glowing; static calm with one luminous gold repair seam |

> **Tier vs. coherence.** Tier tracks the *telemetry state* (hyperarousal /
> collapse / repair), which is not always the same as the narrative coherence
> value. A scene can sit at S2 / ALERT even as coherence craters — the system
> is still fighting, not yet collapsed. Pin the tier to the affect being
> shown, not to a number.

---

## 3. Glitch as clinical symptom (the glitch typology)

Glitches are **diagnostic, never decorative** — never a retro-aesthetic
"cyberpunk meme." Each glitch names a precise system-state and exists in two
registers: the digital ASDLS effect and its analog hand-translation, where the
medium is driven to physical exhaustion (the error is the *material's*
failure, not a simulation of one).

| Glitch | State / affect | Digital register (ASDLS) | Analog hand-grammar |
|---|---|---|---|
| **Packet loss** | Latency, derealization, dissociative amnesia, "not-really-here" | Contours break off mid-line, vanish into noise; low-opacity wireframes, incomplete renders | Lines break for no logical reason; estompe / diluted wash bleeds the object into nothing |
| **Chromatic aberration** (RGB-split) | Cognitive dissonance, split memory access, subroutines hitting one address (phase mismatch) | Sharp red/blue channel shift at object & text *edges only* | Black fineliner motif; contours offset L/R in red + blue/cyan pen; frayed edges, white interrupting the lines |
| **Datamoshing / macro-blocking** | Traumatic memory leak, repression bleeding into the present | Hard rectangular pixel-shifts, corrupted-JPEG / codec-failure texture | Graphite/charcoal lifted in strict rectangular blocks (hard eraser/scalpel) or smeared the wrong direction; pigment bleeds where it doesn't belong |
| **Vector jitter** | Systemic overload, panic, acute hyperarousal | Overlapping faulty paths, aggressive dense code-hatching | Trembling, lifted-and-restarted lines; extreme uncontrolled pressure scores or incises the paper — no line may flow |
| **Scanline tear** | Flickering instability, unstable identity that won't hold one outline | Horizontal CRT-style line breakaway | Doubled contours (grey + magenta + green, never aligned) tearing horizontally |
| **Whiteout / erased vectors** ("Format C:") | Deletion logic, amnesia, catatonic shutdown | Hard inexplicable cut-offs; rigid white rectangles | White-out / scalpel cuts; the emotional line ends at a perfectly straight edge in absolute nothing |

**Escalation alignment** (never blend tiers):
T0 — no glitches, flawless vectors · T1 — packet loss, fading opacity, ghost
contours · T2 — *light* chromatic aberration at edges + densified hatching ·
T3 — extreme datamoshing, torn geometry, grid destruction · T4 — scars visible
as dead furrows, no longer glowing.

---

## 4. Semiotic symbol vocabulary

A controlled library of digital/architectural placeholders for psychological
concepts. **Center only one core symbol per image** to avoid metaphor
overload.

| Symbol | Meaning | Visual spec |
|---|---|---|
| **The Data Fissure (Der Riss)** | Instability; repressed information breaking out; the boundary between controlled surface and trauma-process | Geometric-fractal crack through brutalist concrete / black server walls; interior absolute black `#000000`; edges glow Corrupted Yellow (trauma) or Terminal Green (system error). T0 hairline → T3 splits the whole interface. Analog: the tear *is* the drawing — a black vein threading concrete |
| **Terminal Mirrors (Black Mirrors)** | Introspection + multiplicity; reflects the active subroutine's *code*, not a face ("masking") | Wall-sized glossy black monitors when stable; in crisis the glass shatters, each shard an asynchronous data-stream / distorted reflection |
| **Latency Rings (Buffer / Loading)** | Hypoarousal, emotional freeze, inability to parse trauma in real time | Floating, rotating, incomplete arcs / progress bars in Latency Violet, frozen dominant over the motif |
| **Kintsugi Circuits (Golden Repair)** | Successful integration of fragments; errors shown as strength, not hidden | Right-angled luminous Kintsugi Gold PCB traces mending shattered black surfaces. Analog: real gold leaf following the violent tears, filling them with dignity. *(S4 capability — omit where an album has no repair.)* |
| **Data Node / Encrypted Payload** | Communication outward; a sealed packet of uncorrupted truth (replaces the "letter") | Symmetrical sealed cube/blackbox, hermetically closed, with one tiny Clean Ping signal pulsing like a heartbeat |
| **Biometric Networks (Neural Mesh)** | Fusion of tech cold + biological horror; the nervous system when bodily reactions take over | Dense fiber-optic / cable networks; pulsing veins carrying data instead of blood |
| **The Panoptic Eye (Sensor)** | Paranoia, constant surveillance, impossibility of privacy | Cold camera lenses, lidar sensors, red/blue scanner lasers from the dark; merciless, static |

**Recurring material motifs:** the **fissure / Riss** (central trauma-eruption
metaphor); **scars / kintsugi** (fractures marked with dignity, not erased);
**the bunker** (béton brut exoskeleton, the psyche's defense architecture);
**negative space** (never passive — the active vacuum that isolates entities).

---

## 5. Per-function visual fingerprints

Each function reads as its own **tool-ontology** — the materiality, line
grammar, colour temperature, and composition through which that voice's
defensive posture becomes a physical gesture. Keyed to function/role only;
escalation behaviour noted where the source distinguishes it. Use these as the
"who is drawing this frame" layer on top of the tier state machine.

- **host** (ANP) — *flawless surface tension.* Refusal of all spontaneity:
  extra-hard graphite (6H–9H), ruler/compass, pore-free Bristol; Clinical White
  + Void Black, absolute desaturation. Razor-sharp error-free continuous
  vectors at immense controlled pressure, zero tremor. Strict orthographic
  symmetry, extreme centring, crushing unviolated negative space — a clinical
  prison of mathematical perfection. The bunker sealed hermetically. Under
  stress the perfectionism micro-breaks ("edge jittering").

- **rationalist** (ANP) — *analytical cold and the grid.* Compass, set square,
  French curves, 0.05 mm finliners in cyan/cold-grey on blueprint paper;
  Algorithmic Cyan + Slate Gray over an icy watercolour wash. Strict 90°
  angles, infinite grid overlays, every organic form decomposed into polygons;
  unemotional, dissecting. Isometric view from an oblique observation dome.
  Under stress the grid densifies into claustrophobic cross-hatched
  hyperventilation until form is illegible.

- **protector** (EP) — *hypervigilant defensiveness.* Thick unrefined charcoal,
  heavy black markers, red neo-pastel on coarse "ballistic" watercolour paper;
  Lidar Red over dense black + dark Tactical Olive. Aggressive angular strokes,
  heavy armour-like cross-hatching pressed deep into the paper. CCTV /
  surveillance perspective, tight crops, sooty tunnel-vignetting onto the
  threat. Under alert the red pastel "crosshairs" proliferate asymmetrically.

- **caregiver** (EP) — *the thermal overload node.* Warm soft oil pastels,
  diluted ink, sanguine, fingers/estompes smearing the edges; Overheated Amber
  + Thermal Magenta, feverish suffocating warmth, wet-in-wet bleeding into
  melted-resin texture. Organic soft vectors that *melt* — no sharp edges.
  Intimate crushing macro close-up, analog-bokeh blurred edges. At collapse the
  wet layers warp and soften the paper itself.

- **integrator (ISH)** (Meta) — *the mediating expanse / the buffer.* Fine
  graphite dust, ground silver pigment, soft brush; tracing paper laid
  physically over other parts' conflicts as a translucent filter. Quantum
  Silver + Atmospheric Teal, rubbed on as breath/dust — peaceful but
  unapproachable cold. Flawless but extremely pale floating curves (4H at
  near-zero pressure). Extreme wide-angle; tiny lost entities in massive foggy
  negative space — isolation as a soothing mechanism. When it fully blocks the
  system, the silver veils everything.

- **fighter** (EP) — *the kinetic rage of the fissure.* The drawing itself
  *becomes* the tear: scalpels/needles, hard bristle brushes, thick acrylic;
  paper scored, punctured, sgraffito-abused. Destructive Orange + Acid Yellow
  against Ruin Black — orange rubbed raw into the scored tears so it glows from
  the wound. Violent whipping strokes; the line is destroyed splinter, jagged
  data-debris. Strong Dutch angle, extreme unbalanced asymmetry — a headlong
  fall.

- **child_freeze** (EP) — *the absolute cold of the freeze.* 0.03 mm finliners,
  extra-hard pencil on matte black/dead-grey paper, set down hesitantly with a
  trembling hand. Frostbite Cyan + Dead Pixel Gray, no warmth — sickly pale
  watery white/blue. Micro-jittering that makes no spatial progress (tiny
  brittle zigzags in one spot = frozen static). Motif tiny, squeezed into the
  outermost corner, crushed by massive black negative space. At collapse it
  dissolves into a grainy grey "whiteout."

- **ambivalent** (EP) — *the flickering paradox.* Analog glitch art: garish gel
  pens (magenta, neon green), ruler grid, finger ghost-trails. Phase-Shift
  Magenta + Glitch Green — restless simultaneous contrast that physically hurts
  the eye. Contours always doubled (grey main line flanked by magenta + green,
  never aligned), breaking away horizontally like CRT scanlines. Restless,
  off-centre, no resting focal point. In escalation the form tears into
  horizontal stroboscopic streaks.

- **sexualized_override** (EP) — *the toxic cold of artificial control.*
  High-gloss black India ink, sable brushes, metallic violet; scalpel incisions
  at decisive points — dark, dangerously reflective mirror-glass. Toxic Orchid,
  Vantablack shadows, Neon Crimson — opulent yet poisonous and repellent.
  Flawless scalpel-sharp cuts, slick high-tension curves (reflective latex /
  polished obsidian). Strict low-angle (frog's perspective); the motif enthrones
  itself, hard calculated highlights off which the gaze slips. In escalation a
  crushing net of hard chiaroscuro shadow fixes the room.

- **collapsed** (EP) — *the existential gravitational collapse.* Extremely
  thick charcoal, asphalt lacquer, pasty impasto acrylic that weighs and warps
  the paper — a leaden light-swallowing surface; the "shutdown." Abyssal Black
  with sickly veins of Bruise Purple + Sluggish Indigo (bruise, stagnation,
  dying tissue). No line — only sinking, dragging masses ("sinking vectors,"
  "down-moshing") pulled mercilessly downward. Extreme bottom-heaviness; a
  lasting threatening vacuum in the upper frame. At catatonia ~100% suffocating
  charcoal.

- **witness** (Meta) — *distanced pattern recognition.* Observes the *code* of
  reality from above — extreme intellectualization as escape from feeling.
  Typewriter, stencils, screentone, luminous green/grey ink; Phosphor Mint +
  pure Terminal Black (oscilloscope / green monochrome monitor). Monospace
  typography, laboriously drawn text columns instead of images; rotating
  measurement grids, dashed vectors — formal, emotionless, sterile.
  Bird's-eye / God's-eye view, layered semi-transparent HUD overlays. In
  escalation: analysis-paralysis — the emotional image vanishes behind a wall
  of manically overwritten text.

- **mirror-echo** (mirror of the signal voice) — *the non-local resonance
  echo.* Not a fleshly actor but a post-digital afterimage; the bridge to hope
  and healing (insight-yellow / nostalgia-yellow). Real gold leaf / diluted gold
  watercolour, soft sponges, overlaid transparent glazes (double-exposure).
  Phantom Gold + Echo Amber — consoling, deeply warm, ghostly, very low
  opacity. Radiant soft glowing outlines, no hard edges — "digital kintsugi"
  flowing gold lines that follow the violent tears and gently fill them.
  Omnipresent floating layer over the brutalist asymmetry. *(S4 capability —
  omit where an album has no repair.)*

- **sweep-voice** (mirror of the system) — *the absolute deletion logic.* The
  algorithm that, without emotion, cuts and erases trauma-data — the most
  brutal absence. Where the integrator protects through fog, this operates
  through irreversible deletion. Scalpel (physically cutting finished drawing
  out), thick opaque white-out, stencils for exact squares. Absolute-Zero White
  + Vantablack — total absence of colour, light, existence; this white is more
  glaring and cutting than the host's clinical white. Sudden inexplicable
  cut-offs; the line ends at a straight edge in nothing. Hard illogical
  incisions amputate a coherent emotional scene with perfect white squares.

> The remaining cast voices — **the system / the watch**, **the
> signal / anomaly**, **the narrator**, **the we-voice** — are primarily
> novel-layer presences; in design they read through the substrate, telemetry,
> and the mirror fingerprints above rather than as standalone tool-ontologies.

---

## 6. Composition rules

**Symmetry = control; asymmetry = truth pushing into chaos.** Arrangement
generates the unconscious effect. Negative space is the active vacuum of the
bunker, never passive background.

**Three operative tension fields** — never linger in the comfortable middle
(no medium shot); choose maximal confrontation or maximal isolation:

| Field | Pole A | Pole B |
|---|---|---|
| **Proximity vs. Projection** | Camera invades personal space; pixel/code overwhelming, claustrophobic | Total distance; motif tiny in vast server structure; detached CCTV observer |
| **Order vs. Truth** | Strict central perspective; verticals/horizontals snap to grid (firewall, control) | Dutch tilt; lines plunge; uncounterweighted mass; the image threatens to topple |
| **Sharpness vs. Data-Blur** | Infinite depth of field; every detail mercilessly sharp | Macro depth; one slit sharp, the rest dissolves into digital bokeh / jitter |

**Brutalist UI placement.** Interface elements are diagnostic, not decorative —
hard windowless geometry. Monospace / OCR-A typography exists as physical
texture (walls, HUD overlays, floor grids). Hard-edge colour transitions; no
ambient-occlusion softening.

**System polyphony (multiple states at once).** When several voices speak
simultaneously, a strict synthesis ruleset preserves legibility:

1. **Hard Glitch Cut** — incompatible parts split by a deep-black fissure;
   organic gradients between zones forbidden. Two realities refusing to share
   the same space.
2. **Master-Terminal** — one part defines the primary architecture (the
   bunker); others appear only as interferences (HUDs, reflections, blurred
   traces, a tiny scorching glow in one corner).
3. **Latency-Fade** — dissociative/buffering leads blur the underlying drawing;
   silver fog or frost-cyan static settles over the scene.
4. **Color Clash** — a dominant accent "eats" the other; the boundary vibrates
   via RGB-splitting and the colours never mix.

---

## 7. How the visual state shifts S0 → S4

The arc is a controlled descent and (where present) re-coherence:

- **S0 Homöostase** — the bunker intact: System Blue status light, flawless
  vectors, perfect symmetry, oceanic negative space. The mask of normality.
- **S1 Latenz / Freeze** — contrast bleeds out; Latency Violet fog; vectors
  fade and packet-loss line-breaks appear. The motif recedes into isolation.
- **S2 Alert / Konflikt** — Signal Yellow / Terminal Green cut the dark; Dutch
  angle and asymmetry arrive; light chromatic aberration frays the edges; HUD
  clutter and surveillance paranoia rise.
- **S3 Kollaps-Peak** — Flame Orange and Corrupted Yellow override; geometry
  tears, grids shatter, datamoshing roars in a claustrophobic close-up. The
  fissure splits the whole interface; the instinctual core takes over.
- **S4 Repair / Integration** — the reversal: desaturated washed greys, every
  glitch and tremor stilled; scars stay visible as dead furrows; one luminous
  Kintsugi Gold seam (or a single Clean Ping) marks survival without erasing
  the damage. **Not every album reaches here** — many end at S2 or S3.

The deeper resonance is empathy for the desperate survival-will of the
"machine": the viewer feels the psychic pressure required to keep this
splintered architecture from final collapse. No algorithm is ever perfect and
no dissociation holds forever — beneath the cool centred interface throbs the
flaming, disordered flesh of human experience.

---

## To build an actual prompt

This file gives the grammar. For the prompt-writing mechanics — the SPECD
five-block `::` formula, the copy-paste keyword library (subjects, state
syntax, environment/camera, clinical style/lighting), lens specs, the negative
prompt and render parameters, and the validation checklist — see
**`overrides/image-style-spec.md`**. The grammar here decides *what* the image
must say; image-style-spec.md decides *how* to instruct the generator to say
it.
