# Interactive Dynamics — Kapitel 0 (ASDLS edition)

_Conceptual map of the `<script>` behaviours in `kapitel-0.html`. Describes
**what each behaviour does, what triggers it, and which narrative moment it
serves** — not the source code. The whole chapter is one coherence simulation:
the page's KOH (Kohärenz) value drives every animation, and the reader's scroll
position is the playhead._

The interactivity lives in four script units:

- **Boot / cover engine** — the opening canvas sequence and the "Initiieren" gate.
- **Render + HUD + glitch engine** — builds the chapter DOM, runs the scroll
  telemetry, and orchestrates the climax state machine.
- **Kintsugi shatter library** (`window.playKintsugiShatter`) — the reusable
  shard-break animation.
- **End-shatter trigger** — the IntersectionObserver that fires the shatter at
  the crisis line.

---

## 1. Boot / cover · KOH-ignition sequence

**What:** A full-screen `<canvas>` boots a particle simulation. ~80 particles
are grouped into **8 story clusters** mapped to alters: fragment (centre void),
aegis (system blue), nyx/fighter (flame), kiko/child-freeze (frostbite blue),
rhys/caregiver (amber), silas/echo (kintsugi gold), moros/collapsed
(purple-grey), lex/rationalist (terminal green). A KOH meter, boot log, waveform,
and the chapter title ride on top.

**Phases (time-driven, from page load):**

| Phase | t (s) | KOH behaviour | Beat |
|---|---|---|---|
| `boot` | 0–2.5 | 0 | Terminal boot log types out ("VAKUUM-SUBSTRAT aktiv", "ANTEILE 11 · registriert") |
| `scatter` | 2.5–5.5 | 0 | Particles drift freely in the void |
| `cohere` | 5.5–11 | rises to **0.998**, then Juna arrives → drops to **0.21** | Clusters form (coherence), then a perturbation tears it apart |
| `klick` | 11–12 | ~0.21 + flash | The **Protocol fires** — violent particle burst + clean-ping flash |
| `emerge` | 12–17 | recovers 0.21 → 0.998 | Title breaks through the chaos (blur + chromatic aberration settle) |
| `ready` | 17+ | 0.998 with micro-flicker | Gentle breathing; "Initiieren" button fades in |

The waveform's colour/amplitude/noise track KOH (calm blue → alert yellow →
critical flame). Ghost glyph fragments (`◈ ⤬ ▮▮▮ ◌✦◌`) spawn while coherence is
disturbed.

**Trigger:** Auto-runs on load; `body.cover-active` locks scroll. RAF stops the
instant the user clicks **Initiieren** (CPU guard).

**Serves:** The cover IS the chapter in miniature — homeostasis, the JUNA
perturbation, the KOH_1.0 protocol fire, and forced recovery. Clicking
Initiieren freezes the canvas to a still image and hands off to
`playKintsugiShatter` to break into the reading view.

---

## 2. Scroll-driven HUD coherence telemetry (`updateHud`)

**What:** A fixed top-right HUD shows the current section's KOH value
(`#hud-koh`), the section counter (`#hud-sec`, "NN / 14"), and the tier number
(`#hud-tier`, colour-coded per tier). A top progress bar tracks scroll percent.

**Trigger:** `window` scroll, RAF-throttled (a `_ticking` flag prevents layout
thrash). Determines the "current section" by which `.section.offsetTop` is above
the point one-third down the viewport, then reads that section's `SECTION_META`.

**Serves:** Turns the reader's scroll into the chapter's vital-signs monitor —
the coherence arc (0.998 → 0.18 → forced 1.00) is legible at a glance, and the
HUD is what the climax/calm state machine keys off.

---

## 3. Per-voice background animations

**What:** Each voice block carries a generated SVG backdrop (`voiceBackgroundSVG`)
plus a CSS background animation, so each alter "moves" differently:

| Voice (function) | Animation class | Motion / meaning |
|---|---|---|
| child-freeze | `bg-breathe-cold` | sparse ice crystals, slow icy breathe |
| ambivalent | `bg-scan-lia` | flickering RGB scanlines drifting sideways (paradox) |
| caregiver | `bg-pulse-rhys` | warm pulse rings + soft connecting lines |
| fighter | `bg-jitter-nyx` | jagged fissures, fast violent jitter/skew |
| collapsed | `bg-sink-moros` | descending gradient + sinking lines, fading down |
| mirror/echo (Silas) | `bg-rotate-slow` | radiating golden mesh, slow rotation (phantom echo) |

**Trigger:** Always on while the block is in/near the viewport (viewport-gated by
the `.vp-near`/`.vp-far` IntersectionObserver). A whole-block ambient glow
(`block-glow-*`) pulses underneath.

**Serves:** Gives each alter a non-verbal somatic signature — the design layer's
"no names" rule means identity is carried by motion, colour, and glyph, never a
label.

---

## 4. Glitch state machine (coherence-scaled corruption)

**What:** Two layers of corruption:

- **Per-section static glitch** — at render time each `.section` gets a class
  `g1`–`g4` from its KOH (`glitchClass`): g1 subtle chroma, g2 RGB-split +
  scanlines, g3 datamosh blocks + full aberration, g4 full-page takeover.
  Sections with tier ≥ 2 also inject `datamoshBlocks()` (mh/mv/mj/mb corruption
  rects); tier 3 adds `climaxOverlay()` (cb-row bars + macroblock grid).
- **Dynamic climax escalation** — `updateHud` adds/removes body classes as the
  reader scrolls through the crisis sections.

**Trigger / escalation (driven by which section is current):**

| Reader location | Body classes | Intensity |
|---|---|---|
| `schrecken` / `kaskade` (pre-climax) | (clean) + ghost spawns | mild |
| `kollaps` | `climax show` | datamosh, chroma-pulse, scanband 3.2s; ghost 0.45 |
| `trennung` < 30% | `climax show deep` | scanband 1.8s; ghost 0.70 |
| `trennung` 30–65% | `climax show deep peak` + **`showCracks()`** | scanband 1.2s; ghost 0.88 |
| `trennung` > 65% | `climax show deep peak shake` + cracks | scanband + page tremor; ghost 1.0 |

**Observers:** `vpObserver` gates section animations (`.vp-near`/`.vp-far`,
300px rootMargin); resonance-scene canvases use their own IntersectionObserver to
run RAF only when visible.

**Serves:** The reader literally watches the system lose coherence — corruption
intensity rises section by section until the autopoietic collapse at `kollaps`
and the surgical KOH_1.0 partition at `trennung`.

---

## 5. Kintsugi shatter-reveal

**What:** `window.playKintsugiShatter({sourceEl, onReveal, onComplete, shardCount=14})`
clones a full-screen element, generates ~14 radiating crack lines from centre,
splits the clone into shard polygons, paints golden (`--kintsugi`) crack seams,
then flings the shards outward — revealing what's behind. The crack SVG itself
lives in `#crack-overlay` (`.show`), built by `buildCrackSVG()` / `makeFissure()`
and toggled by `showCracks()` / `hideCracks()`.

**Two trigger sites:**

1. **Cover → reading view.** Clicking **Initiieren** freezes the cover canvas and
   shatters it away to enter the chapter.
2. **Chapter-end crisis peak.** A separate IntersectionObserver watches the
   hidden paragraph containing **"Ich falle… in unzählige Scherben…"**
   (`findTriggerParagraph` tags it `.shatter-reveal` / `data-shatter-trigger`).
   It fires once, ~250px before the line enters view (so the break starts before
   the reader sees blank space) and only after the cover is dismissed. A dark
   overlay fades in (320ms), holds (600ms), the page scrolls the hidden line near
   the top, then the overlay shatters into kintsugi gold. `onReveal` switches the
   body to **`calm`** (kills all glitch/shake/climax) and, after an 800ms hold,
   adds `.revealed` to fade the hidden line in behind the gold — followed by the
   `KOH_1.0 · COMPLETE` prelude.

**Serves:** The thematic hinge of the chapter. The fragment shatters "in
countless shards" — but the break is rendered as **kintsugi** (broken-and-gilded),
turning catastrophic partition into the birth of Kael (the host) and the forced
coherence of 1.00. The shatter is also what calms the page: panic resolves into
stillness.

---

## 6. Audio hooks

**None.** `playKintsugiShatter` is named with a "play" verb but is **purely
visual** — there is no `AudioContext`, oscillator, or `Audio()` element anywhere
in the scripts. The "shatter" is animation only; any sonic association lives in
the album's audio, not in this HTML.
