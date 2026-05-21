# Image-Prompting Spec — Agency System (the HOW)

**Purpose.** This is the **prompt-construction** spec for *the Agency System*
visual layer: how to assemble a buildable, deterministic image/cover-art prompt
for Midjourney V7, Flux, Stable Diffusion 3.5, DALL·E, etc. It owns the SPECD
prompt formula, the copy-paste keyword library, per-state palette/hex with the
5%-rule applied, camera-lens prompting, and the `name_exposure` rule for art
prompts. It is cross-project and album-agnostic — usable for covers, promo, and
novel illustration alike.

**This file does NOT re-explain the conceptual grammar.** The state machine,
glitch-as-symptom semantics, per-function visual fingerprints, and the
materiality/interface-brutalism philosophy live in
[`visual-language-guide.md`](visual-language-guide.md). Read that first to
understand *what* a state means; come here to learn *how* to write the prompt
that renders it. Underlying canon: `state-axis.md`,
`skills/theagencysystem/references/cross-cutting/{specd-formula,color-thermodynamics,semiotic-symbols,composition-rules}.md`.

---

## 0. CRITICAL — name_exposure (function/role language only)

**A personal name must NEVER enter an art prompt.** Every prompt and every
example in this file uses **function/role language only**. Personal names live
ONLY in internal `DESIGN.md §7`, the SOURCE files, and the cast bridge
(`skills/theagencysystem/references/resolver.yaml`) — never in a lyric, Suno
metatag, promo field, or image prompt. A name leaking into any rendered or
output field is a **CRITICAL** defect.

Refer to the cast by role in every Subject block: *the host*, *the watch*, *the
logic-voice*, *the collapsed one*, *the protector*, *the integrator*, *the
small-voice*, *the mirror-echo*, *the sweep*, *the signal*. Human-like figures
are permitted only as obscured, data-encoded entities — never a named portrait.

---

## 1. The SPECD prompt formula

Every prompt splits into **exactly five blocks separated by the double colon
`::`**. This forces the model to distribute weights cleanly and minimizes
concept-bleeding. Order is fixed.

```
<Subject> :: <State> :: <Environment / Camera> :: <Style / Lighting> :: <Parameters & negatives>
```

| Block | Holds | What goes here |
|---|---|---|
| **1 · Subject** | One core semiotic symbol or data-encoded entity, named by **role only** | `jagged deep black data fissure`, `mechanical surveillance lens`, `the host as a faceless humanoid silhouette of dense wireframes`. Center *one* symbol — avoid metaphor overload. |
| **2 · State** | The tier (T0–T4) + emotional-state modifiers | `Tier 2 state, paranoid atmosphere, executing hostile intrusion detection`. State modifiers: `experiencing latency`, `succumbing to toxic data decay`, `processing immense logical constraints`. |
| **3 · Environment / Camera** | Vacuum, scale, lens, framing, angle | `vast empty black void, negative space dominance`, `shot on 14mm CCTV perspective`, `shot on 100mm macro lens, severe dutch angle`. |
| **4 · Style / Lighting** | The fixed clinical anchor (in EVERY prompt) + glitch + light | `interface brutalism, clinical dystopian aesthetic, high-contrast dark mode, synthetic digital materiality` + glitch term + lighting. |
| **5 · Parameters & negatives** | `--no` ban list, aspect, `--style raw`, `--s`, `--v`, `--sref` | See §5. The negatives are existential — they suppress the model's default retro/synthwave bias. |

---

## 2. Keyword library (copy-paste)

### A · Subjects (semiotic symbols — see visual-language-guide.md for meaning)
- `shattered monolithic terminal screen` (the black mirrors — multiplicity)
- `jagged deep black data fissure` (Der Riss — instability/trauma eruption)
- `glowing frozen circular buffering ring UI` (latency rings — freeze)
- `sealed data drive cube emitting one tiny ping` (encrypted payload — truth)
- `macabre biometric neural network of fiber optic cables` (neural mesh)
- `mechanical surveillance lens` (the panoptic eye — paranoia)
- `geometric breaks joined by glowing golden PCB circuit lines` (kintsugi circuits — repair)
- Figures: `faceless humanoid silhouette constructed of dense wireframes, obscured by terminal text overlays` (role-named only)

### B · Lens / camera (§4 for full prompting)
- Isolation: `shot on 14mm lens, ultra-wide angle, CCTV security camera perspective, immense sense of scale`
- Claustrophobia: `shot on 100mm macro lens, extreme close-up, suffocating tight framing, shallow depth of field`
- Instability: `extreme dutch angle, tilted camera perspective, disorienting 45-degree rotation, architectural vertigo`

### C · Materiality (anchor at least one)
- `interface brutalism, clinical dystopian aesthetic, synthetic digital materiality`
- `electron microscope fidelity, medical imaging aesthetic, MRI scan texture, x-ray translucent surfaces`
- `dense monospace terminal code overlay, glowing hex dumps projected on walls, OCR font textures in 3D space`
- Line state: `fading vector lines, dropped packets, ghostly thin contours` (low bandwidth) / `chaotic vector overlapping, aggressive digital hatching, schematic overload` (high bandwidth)

### D · Lighting
- `harsh surgical overhead lighting`, `cold LED light`, `volumetric phosphor terminal glow`, `deep raytraced black shadows`

### E · Glitch terms (diagnostic, never decorative)
- `severe chromatic aberration, sharp RGB channel shift, optical phase mismatch` (cognitive dissonance)
- `compression artifacting, hard datamoshing, digital macro-blocking, blocky codec failure` (memory leak / collapse)
- Reserve glitch by state: none at T0; mild edge chroma at T1–T2; full datamosh at T3; dead non-glowing fissures at T4.

---

## 3. Palette / hex per state + the 5%-rule

**The 5%-rule:** the frame is ~95% background paradigm (Terminal Black
`#0B0D17` / Deep Charcoal `#1A1D24`) and **≤5% one state colour**. Transitions
are **hard-edge** — gradient ban, no ambient-occlusion softening. Pick the
state colour from the active state, set it as the lighting accent in block 4,
and keep it confined to ≤5% of the frame.

| State | Tier | State colour | Hex | Apply in prompt as |
|---|---|---|---|---|
| **S0 · Homöostase** | T0 | System Blue | `#003366` | `cold deep System Blue #003366 status light, ≤2% of frame, sterile surgical blue` |
| **S1 · Latenz / Freeze** | T1 | Latency Violet | `#3B3355` | `muted Latency Violet #3B3355 ambient glow, fading edges, low contrast` |
| **S2 · Alert / Konflikt** | T2 | Signal Yellow | `#FFD700` | `hostile neon Signal Yellow #FFD700 warning light piercing the dark, hard-edge` |
| **S3 · Kollaps-Peak** | T3 | Flame / Corrupted | `#FF4500` / `#8B8B00` | `violent Flame Orange #FF4500 over-saturation` (+ Corrupted Yellow `#8B8B00` decay) |
| **S4 · Repair / Integration** | T4 | Kintsugi Gold | `#FFDF00` | `single tiny Kintsugi Gold #FFDF00 repair seam, precise PCB circuitry, not organic gold` |

Background base in every prompt: `light-absorbing #0B0D17 terminal black void`
or `monolithic #1A1D24 deep charcoal brutalist concrete`.

**Two chromatic laws to honor in a prompt:**
- **Law of exclusion** — Flame Orange `#FF4500` and Clean Ping `#FCEE0C` never
  share a frame (unless one *overwrites* the other as a sharp glitch).
- **Corrupted Yellow is infectious** — where `#8B8B00` appears, dull/desaturate
  neighbors: append `desaturated neighboring colors caused by toxic yellow light spill`.

---

## 4. Composition + camera-lens prompting

**Symmetry = control; asymmetry = truth pushing into chaos.** (Grammar:
[`visual-language-guide.md`](visual-language-guide.md).) When you build block 3,
choose one pole of each tension field — never the comfortable middle (no medium
shots):

- **Proximity vs. Projection** — `shot on 100mm macro, suffocating tight
  framing` (intimacy/claustrophobia) **or** `shot on 14mm CCTV perspective,
  motif tiny in vast server structure` (analytic isolation).
- **Order vs. Truth** — `perfectly balanced orthographic composition,
  snap-to-grid verticals` (firewall control, S0) **or** `extreme dutch angle,
  uncounterweighted mass, image threatens to topple` (destabilizing truth, S2–S3).
- **Sharpness vs. Data-blur** — `infinite depth of field, mercilessly sharp`
  **or** `macro depth, one slit sharp, rest dissolves into digital bokeh / jitter`.

Negative space is the active vacuum that isolates the entity — prompt it
explicitly (`vast negative space dominance`), never leave framing to chance.

---

## 5. Parameters & negatives (block 5)

- **Negatives (existential — always include):**
  `--no 1980s retro, synthwave, outrun, purple-orange gradient, neon grid,
  daylight, sun, natural elements, cute, soft lighting, watercolor, analog
  painting, visible paper texture, lens flare, organic curves`
- **Aspect:** `--ar 16:9` (environments) · `--ar 4:5` (nodes/payloads) ·
  `--ar 1:1` (avatar/profile) · `--ar 4:5` or `--ar 1:1` for cover art.
- `--style raw` (always — disables beautification, forces rawness).
- `--s 50`–`--s 100` (low stylization preserves functional cold; ~75 default).
- `--v 7.0` (reference the newest model).
- `--sref <url>` — once a master image is established, its URL MUST be reused as
  the style-reference for every follow-up shot to lock 100% coherence.

---

## 6. Worked example prompts (role-form only — NO names)

**S2 · Alert — the protector function (defensive vigilance):**
```
mechanical surveillance lens emerging from shadows, cold glass sensor reflection :: Tier 2 state, hypervigilant protector posture, executing hostile intrusion detection :: claustrophobic close-up, aggressive asymmetrical tension, severe dutch angle :: interface brutalism, clinical dystopian aesthetic, sharp chromatic aberration on edges, hostile neon Signal Yellow #FFD700 warning light piercing the darkness, deep raytraced black shadows :: --no 1980s retro, synthwave, daylight, soft lighting, analog texture --ar 16:9 --style raw --s 75 --v 7.0
```

**S4 · Repair — the integrator function (safe mode / resynthesis):**
```
geometric breaks in a dark surface joined by glowing golden PCB circuit lines :: Tier 4 state, integrator resynthesis, exhausted clarity after collapse :: static calm composition, restrained distance, vast negative space dominance :: interface brutalism, digital kintsugi repair aesthetic, desaturated washed-out concrete greys, single tiny Kintsugi Gold #FFDF00 repair seam, cold quiet atmosphere :: --no 1980s retro, synthwave, daylight, organic curves, visible paper texture --ar 1:1 --style raw --s 60 --v 7.0
```

---

## 7. Buildable-prompt checklist

Before sending a prompt, confirm:

1. **Five blocks** present, separated by `::`, in order (Subject · State ·
   Environment/Camera · Style/Lighting · Parameters).
2. **Role language only** — zero personal names in any block (CRITICAL).
3. **One symbol** centered in block 1 (no metaphor overload).
4. **Tier matches state** — block 2 tier = the active S0–S4 state; glitch
   intensity in block 4 matches that tier (none at T0, full datamosh at T3).
5. **5%-rule applied** — background = `#0B0D17`/`#1A1D24`; exactly one state
   colour at ≤5%, hard-edge; chromatic laws honored (no Flame + Clean Ping).
6. **Clinical anchor** present in block 4 (`interface brutalism, clinical
   dystopian aesthetic, dark mode`).
7. **Tension chosen** — block 3 picks a pole (macro/wide, symmetry/dutch),
   never a medium shot.
8. **Block 5 complete** — negatives + `--style raw` + aspect + `--s` + `--v 7.0`
   + `--sref` for follow-up shots.

For the underlying grammar (why each rule exists), see
[`visual-language-guide.md`](visual-language-guide.md).
