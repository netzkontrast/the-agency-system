# ASDLS Visual Design System

_Extracted from the `<style>` blocks of `kapitel-0.html` ("ASDLS palette").
This is the **design layer** of the the-agency-system: a coherence-driven
visual language where every colour, type choice, and animation maps to the
chapter's KOH (Kohärenz / coherence) state. Voices are referenced by
**function/role only** — no personal names appear in any visual element._

ASDLS = **A**gency **S**ystem **D**esign **L**anguage **S**pec (working name on
the page title bar: "Kapitel 0 — Maximal Edition · ASDLS").

---

## 1. Colour palette (CSS custom properties)

All defined in the `:root` block, comment-tagged `/* ASDLS palette */` and
`/* ASDLS state colors */`.

### Surface / ink (the neutral substrate)

| Property | Hex | Semantic role |
|---|---|---|
| `--terminal-black` | `#0B0D17` | Base void / page background; the "Nichts" |
| `--charcoal` | `#1A1D24` | Secondary dark surface |
| `--bg` | `#0B0D17` | Active background (alias of terminal-black) |
| `--bg-alt` | `#14161f` | Raised panel / alternate surface |
| `--ink` | `#e8e6df` | Primary body text |
| `--ink-soft` | `#a8a397` | Secondary / muted text |
| `--ink-mute` | `#5a554a` | Labels, HUD keys, faint metadata |
| `--rule` | `#1f222b` | Hairline borders / dividers |

### State colours (the coherence telemetry palette)

Each maps to a point on the KOH arc — calm system → critical collapse → forced
re-coherence.

| Property | Hex | Semantic role |
|---|---|---|
| `--system-blue` | `#003366` | AEGIS / control architecture (deep, cold) |
| `--system-blue-glow` | `#4a7fb5` | Tier-0 dot · homeostasis (calm blue) |
| `--corrupted` | `#8B8B00` | Corruption / degraded-signal markers |
| `--signal` | `#FFD700` | Alert / HUD value / progress bar (gold-yellow) |
| `--terminal-green` | `#00FF9F` | Logic / analysis (the rationalist; LEX cluster) |
| `--flame` | `#FF4500` | **Collapse peak** · Tier-3 · fighter (NYX) · climax takeover |
| `--clean-ping` | `#FCEE0C` | Klick / protocol-fire flash; Kael's final clean line |
| `--latency` | `#3B3355` | Tier-1 dot · latency state (purple-grey) |
| `--kintsugi` | `#FFDF00` | **Kintsugi gold** · Tier-4 · shatter-reveal · echo/resonance (SILAS) |

### Coherence → tier → colour mapping

The chapter quantises KOH into 5 tiers (used by `.tier-N .dot`, HUD, and the
glitch system). Lower coherence = hotter colour.

| Tier | KOH band | State label | Dot colour |
|---|---|---|---|
| 0 | ≥ 0.80 (nominal) | HOMÖOSTASE | `--system-blue-glow` `#4a7fb5` |
| 1 | latency | LATENZ | `--latency` `#3B3355` |
| 2 | alert | ALERT | `--signal` `#FFD700` |
| 3 | critical | KERNEL PANIC | `--flame` `#FF4500` (with glow) |
| 4 | re-cohered | SAFE MODE | `--kintsugi` `#FFDF00` |

---

## 2. Typography

| Property | Value | Role |
|---|---|---|
| `--serif` | `'Cormorant Garamond', Georgia, serif` | Prose / narration / most voice blocks |
| `--mono` | `'JetBrains Mono', ui-monospace, monospace` | HUD, logs, stamps, margin notes, system telemetry |
| `--display` | `'Space Grotesk', system-ui, sans-serif` | Cover H1, section headings, drop caps, NYX (fighter), Kael's end-line |
| `--sans` | `'Inter', system-ui, sans-serif` | Kael (host) terminal-sterile prose (`.v-kal`) |

Webfonts (`Cormorant Garamond`, etc.) are embedded as `@font-face` woff2
resources in the bundle.

### Reading measure & rhythm

| Property | Value | Role |
|---|---|---|
| `--measure` | `38rem` | Reading column max width (user-tunable 28–50rem) |
| `--fs-body` | `18px` | Body font size (user-tunable) |
| `--leading` | `1.7` | Body line-height |

Cover H1 scales `clamp(3rem, 9vw, 8rem)` at line-height `0.95`; subhead
`clamp(1.2rem, 2.4vw, 1.7rem)`; section H2 `clamp(1.2rem, 4vw, 2.2rem)`.
`.first-letter::first-letter` is a 4em display drop-cap.

---

## 3. Layout classes

| Selector | Role |
|---|---|
| `main` | Centred container, `max-width: 1280px`, 24px padding, `z-index:1` over canvas backdrops |
| `.text-layout` | 3-col grid: `minmax(180px,1fr) minmax(0,var(--measure)) minmax(180px,1fr)` — left gutter / reading column / right margin |
| `.text-col` | The central reading column (the prose) |
| `.margin-left` / `.margin-right` | Side gutters that hold the marginalia notes |
| `.margin-note` (`.left-side`) | Mono coherence/state annotations placed beside each section; absolutely positioned by section offset |
| `.section` (`+ .section`) | Section wrapper (8em gap between sections); carries `data-tier`, `data-koh`, and a glitch class `g1`–`g4` |
| `.section-marker` | Header row: `§ NN` num + H2 heading + tier badge |
| `.section-marker .tier` (`.tier-0`…`.tier-4`) | Tier badge with coloured `.dot` |

### HUD (fixed coherence telemetry, top-right)

`.hud` — fixed `top:64px; right:24px`, mono, 9px, uppercase, `letter-spacing:0.2em`.
Rows: `.row` with `.k` (key, muted) + `.v` (value, `--signal` gold) and an
80×4px `.bar` whose `::after` fill width tracks coherence. Populated live by
`updateHud()` (see `dynamics.md`).

### Progress bar

`.progress` — fixed full-width 2px bar at `top:0`, gradient
`--signal → --clean-ping`, `box-shadow` glow; width = scroll percentage.

### Cover

| Selector | Role |
|---|---|
| `.cover` | Full-viewport grid `auto 1fr auto`; `::after` draws a framed border with a 2px `--signal` left edge |
| `.cover .head-row` / `.stamp` | Top status row; `.hot` = `--clean-ping`, `.corrupt` = `--corrupted` |
| `.cover h1` | Display title; `.glitch` child uses `::before`/`::after` RGB-split clones with `glitch-a`/`glitch-b` keyframes; `.it` = italic serif accent |
| `.cover .subhead` | Serif subtitle, max 30em |
| `.cover .foot-row` | Mono metadata grid; `.v.warn` = `--signal`, `.v.crit` = `--flame` |

### Colophon (page foot)

`.colophon` — mono, 10px, uppercase, `letter-spacing:0.25em`, centred, top
hairline rule. `.codes` is a flex row of `--ink-soft` code spans (the closing
credits/signatures of the chapter).

---

## 4. Voice block styling

Voice (alter) lines render as `.voice-block` cards. **No labels / no names** —
identity is conveyed entirely through colour, corner brackets, glyph marks, and
motion. Voice→class map (from the render script):

| Code | Class | Function (role) | `--voice-c` colour | Glyph mark (`.vb-mark`) |
|---|---|---|---|---|
| `kik` | `.vk` | child-freeze (frostbite) | `rgba(168,192,216,…)` ice-blue | `/ / /` |
| `lia` | `.vl` | ambivalent (paradox) | `rgba(212,160,200,…)` mauve | `⤬ ⤬` |
| `rhy` | `.vr` | caregiver (warmth) | `rgba(240,168,120,…)` amber | `◌ ◌ ◌` |
| `nyx` | `.vn` | fighter (kinetic) | `rgba(255,69,0,…)` flame | `▮ ▮ ▮` |
| `mor` | `.vm` | collapsed (sinking) | `rgba(107,104,130,…)` purple-grey | `▼ ▼` |
| `sil` | `.vs` | mirror/echo (Silas) | `rgba(255,223,0,…)` kintsugi gold | `◌ ✦ ◌` |

Shared block structure:

| Selector | Role |
|---|---|
| `.voice-block` | The card; `max-width:30em`, serif `1.08rem`, `line-height:1.65`; sets `--voice-c` per class |
| `.voice-block .vb-bg` + `svg` | Per-voice atmospheric SVG generated in JS (ice crystals / RGB scanlines / pulse rings / fissures / sinking lines / radiating mesh) |
| `.vb-tl .vb-tr .vb-bl .vb-br` | The four **corner brackets** (2px `currentColor` L-shapes, offset ±10/±16px) framing the card |
| `.vb-mark` | The glyph mark (mono, 13px) that stands in for a speaker label; flickers via `mark-flicker` |
| `.vb-tag` | Mono 9px micro-tag |

Per-voice typographic deviations: `.vn` (fighter) switches to display font,
normal style, tighter line-height (staccato feel); `.vm` (collapsed) drops to
`0.98rem` with looser `1.85` leading (sinking, spread-out); `.vs` (echo) adds a
golden `text-shadow` glow.

### Host & mirror prose (non-card voices)

| Selector | Role |
|---|---|
| `.v-frg` | Fragment / proto-self prose (`--ink`, the default narrating "Ich") |
| `.v-aeg.prose` / `.v-aeg.log` | AEGIS system voice / telemetry logs (mono) |
| `.v-kal` | Kael (host) — sans, weight 300, sterile/clean terminal prose |
| `.v-kal.kael-end` | Kael's closing line — display font, `--clean-ping`, 1.4rem ("Ich bin pünktlich.") |

---

## 5. Glitch, climax & break-element CSS

Coherence-scaled corruption. The render script assigns `g1`–`g4` per section
from KOH (`glitchClass()`):

```
g1: koh < 0.80  — subtle chromatic edge on prose, mild bracket jitter
g2: koh < 0.50  — RGB-split text shadow, packet-loss scanlines on bg
g3: koh < 0.30  — full chromatic aberration, datamosh blocks, vector jitter
g4: koh < 0.22  — climax: full-page glitch takeover (kollaps + trennung)
```

| Selector / keyframe | Role |
|---|---|
| `.datamosh` (`.mh .mv .mj .mb`) | Corruption blocks (horizontal / vertical / jitter / block); animated by `mosh-h`, `mosh-v`, `mosh-jitter`, `mosh-block` |
| `chroma-pulse` (keyframe) | RGB chromatic-aberration cycle (`steps(8)`), applied at g3 and during climax |
| `.climax-bars` / `.cb-row` | Tier-3 horizontal corruption bands |
| `.macroblock` | Tier-3 macro-block corruption grid |
| `.climax-scanband` | Fixed full-width 4px gradient scan bar (flame→green→transparent), `mix-blend:screen`, runs `scanband`; speeds up `3.2s → 1.8s → 1.2s` across show/deep/peak |
| `body.climax::after` | Full-page g4 overlay; intensifies via `.show` / `.deep` / `.peak` (scanshift + climax-breath/-flicker) |
| `body.shake #shake-frame` / `.text-col` | Whole-page tremor at peak (`shake-frame` keyframe) |
| `body.calm` …| The reversal: kills every animation/glitch, fades datamosh/scanband/cracks to opacity 0 over 1.8–2.4s — the post-shatter stillness |
| `.section-break` | "— ende protokoll · re-init —" cinematic divider in `--flame` |
| `.kael-prelude` | Framed flame banner: "[ KOH_1.0 · COMPLETE · FRAGMENT ELIMINATED · 2.3 × 10⁻³ s ]" |
| `#crack-overlay` (`.show`) | Fixed full-screen layer that holds the animated kintsugi crack SVG (see `dynamics.md`) |

### Per-voice background & block-glow animations

Atmospheric motion bound to each voice's `.vb-bg svg`, plus an ambient
whole-block glow:

| Voice (class) | bg animation | Feel |
|---|---|---|
| child-freeze `.vk` | `bg-breathe-cold` 3.5s + `block-glow-kik` | slow icy breathe |
| ambivalent `.vl` | `bg-scan-lia` 2.0s + `block-glow-lia` | horizontal scan drift |
| caregiver `.vr` | `bg-pulse-rhys` 2.8s + `block-glow-rhy` | warm pulse |
| fighter `.vn` | `bg-jitter-nyx` 0.18s `steps(3)` + `block-glow-nyx` | violent jitter/skew |
| collapsed `.vm` | `bg-sink-moros` 5s alternate + `block-glow-mor` | downward sink/fade |
| mirror/echo `.vs` | `bg-rotate-slow` 14s + `block-glow-sil` | slow golden rotation |

`mark-flicker` gives each `.vb-mark` glyph an occasional drop in opacity
(staggered by `--vb-pulse` / `--vb-delay`).

### Resonance scenes & viewport gating

`.resonance-scene` — full-bleed atmospheric `<canvas>` backdrops inserted
between sections, labelled `TIER N · <STATE> · → § idx`. Animations are
viewport-gated: an IntersectionObserver tags `.section` with `.vp-near`
(within 300px) / `.vp-far` so only visible canvases run their RAF loop
(performance guard).

### User tweaks panel

`#tweaks-root` exposes a live editor (`--measure`, `--fs-body`, `--leading`,
toggles for glitch / marginalia / hud / diagrams). Defaults sit in an
`EDITMODE-BEGIN…END` block: measure 38, fontSize 18, leading 1.7, all toggles on.
