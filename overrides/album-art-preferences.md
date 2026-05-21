# Album Art Preferences — ASDLS encoded for DALL-E

**Scope.** Cross-project art direction for **the Agency System**. This file
encodes the **Agency System Design Language Spec (ASDLS)** — the project's
binding visual law — into a form the **DALL-E / generic** prompt style can
execute. The full normative spec lives in each album's
`SOURCE/ASDLS-spec.md` (and `SOURCE/ASDLS.md` summary); this override is the
operational bridge the `album-art-director` skill loads. Where this file and the
ASDLS spec disagree, **the ASDLS spec wins** — fix this file.

## AI Art Platform

- **Platform: DALL-E** (also valid as a generic/portable prompt).
- **Model/preset:** n/a (DALL-E is conversational).
- **Aspect ratio:** square **1:1** for cover/track art (3000×3000 min); ASDLS
  editorial default is 4:5 for "node" assets, 16:9 for environments.

**Why a DALL-E encoding is needed.** The ASDLS native prompt is the SPECD
formula — five `::`-separated blocks with Midjourney `--no`/`--style raw`/`--ar`
parameters. **DALL-E does not parse `::` blocks or `--` parameters and has no
negative-prompt field.** So every ASDLS prompt is translated into **one
natural-language paragraph** that still carries all five SPECD blocks in order,
with the exclusions folded into a closing "Avoid …" clause.

## name_exposure (hard rule)

Role/function language **only** in any prompt — **never a personal name.** The
alter names live solely in `skills/theagencysystem/references/resolver.yaml` and
album `DESIGN.md §7`; they must never reach an art prompt. Human-like figures
appear only as **faceless, data-coded entities** ("a faceless humanoid silhouette
built of dense wireframes, obscured by scrolling terminal text"). A name leak is
a CRITICAL defect. Extends `overrides/voice-craft-principles.md`.

## The non-negotiable ASDLS rules (every prompt must satisfy)

1. **Background ratio.** ≥95% (never below ~70%) **Terminal Black `#0B0D17`** /
   **Deep Charcoal `#1A1D24`**, light-absorbing. The subject is isolated in a
   void — except a Tier-3 collapse, which may fill the frame with chaos.
2. **The 5% Rule.** At most **5%** of the frame carries a state color, and at
   most **one or two** state colors. The 95/5 split is the signal.
3. **Hard edges, no gradients.** State color meets black as a razor-sharp edge or
   blocky pixel shift — never a soft gradient, never softened by ambient
   occlusion. (DALL-E phrasing: "hard-edged, no gradients, sharp cut between the
   black and the colored light.")
4. **One tier per image.** Pick exactly one Tier (0–4); never mix escalation
   stages — it destroys state legibility.
5. **One core symbol per image.** At most one of the semiotic symbols (§ below)
   at the center; don't stack metaphors.
6. **100% digital materiality.** Interface brutalism / clinical dystopia /
   medical-imaging fidelity. No analog texture, no daylight, no organic curves,
   no retro/synthwave. (Always state these in the "Avoid" clause.)
7. **Law of exclusion.** **Flame Orange and Clean Ping never share a frame.**
   (Chapter Zero specifically has **no Kintsugi Gold and no Clean Ping** — its
   Tier 4 uses dead, unlit furrows only.)
8. **Priority order when in tension:** emotional system-state > clinical
   syntax/materiality > symbol/motif > random generative detail.

## Palette (state colors — use ≤5%, hard-edged, in DALL-E words)

| Color | Hex | State | DALL-E phrasing |
|---|---|---|---|
| System Blue | `#003366` | control, cold logic, firewall | cold deep clinical blue, sterile surgical blue light |
| Corrupted Yellow | `#8B8B00` | trauma, freeze, toxic decay (desaturates neighbors) | sickly mustard yellow, toxic decay glow, jaundiced light |
| Signal Yellow | `#FFD700` | acute alert, panic, intrusion | glaring high-vis warning yellow, piercing alert light |
| Terminal Green | `#00FF9F` | raw noise, operational unrest | phosphor terminal green, clinical oscilloscope green |
| Flame Orange | `#FF4500` | destructive collapse, overload | searing thermal orange-red, overheated system glow |
| Clean Ping | `#FCEE0C` | fragile hope (tiny point only) | a single soft pale-lemon light ping |
| Latency Violet | `#3B3355` | dissociation, lost bandwidth | desaturated deep violet, fading purple fog (no clear edges) |
| Kintsugi Gold | `#FFDF00` | repair, breakthrough (NOT Chapter Zero) | glowing golden circuit-trace repair seams |

> **Corrupted-Yellow infection:** when `#8B8B00` is present, say neighboring
> colors are "desaturated and clouded by the toxic yellow spill."

## The DALL-E prompt template (SPECD → one paragraph)

Write **one paragraph**, in this order, then the Avoid clause:

> **[1 Subject/symbol]** + **[2 Tier-state phrasing]** + **[3 environment + camera/lens]** + **[4 clinical style + lighting + the 95/5 color split with exact hex]**. *Avoid: [the ban list].*

**Block 4 anchor chain — paste into every prompt:** "interface brutalism,
clinical dystopian aesthetic, high-contrast dark mode, synthetic digital
materiality, electron-microscope / medical-imaging fidelity, deep raytraced black
shadows."

**Avoid clause — paste into every prompt:** "Avoid 1980s retro and synthwave,
purple-orange gradients, neon grids, daylight or sun, natural or organic
elements, anything cute, soft lighting, lens flare, watercolor or painterly
looks, visible paper or analog texture, and any text or watermark."

### Per-Tier ready phrasing (block 2)

- **Tier 0 Homeostasis:** "minimalist clinical precision, a vast empty black
  void, perfectly centered frontal orthographic composition, pristine surfaces,
  razor-sharp vector lines, no glitches, profound silence" · accent ≤2% System
  Blue as a faint status light.
- **Tier 1 Latency/Freeze:** "fading opacity, deep fog swallowing the subject,
  low-contrast bleakness, an extreme wide shot that isolates the tiny focal
  point, ghostly thin broken contours (dropped data packets), suspended
  animation" · muted Latency Violet ambient.
- **Tier 2 Alert:** "aggressive asymmetrical tension, a severe dutch angle, sharp
  chromatic aberration only at the edges, dense terminal-text clutter, paranoid
  surveillance atmosphere" · Signal Yellow / Terminal Green piercing the dark.
- **Tier 3 Kernel Panic:** "total digital collapse, extreme datamoshing, a
  claustrophobic macro close-up, corrupted geometry, the frame blown apart by
  data debris" · Flame Orange + Corrupted Yellow overdriving (this tier may break
  the 5% rule).
- **Tier 4 Safe Mode:** "a desaturated post-crash environment, pale washed-out
  greys, visible digital scars as deep DEAD furrows that no longer glow, static
  exhausted calm" · (Chapter Zero: no gold spark — dead furrows only).

### Camera/lens (block 3)

- Isolation: "shot like a 14mm ultra-wide CCTV camera, immense towering scale."
- Claustrophobia: "shot like a 100mm macro lens, suffocating tight framing,
  shallow depth of field."
- Instability: "extreme dutch angle, tilted disorienting perspective."
- Never linger in the "comfortable middle" (medium shot) — maximal confrontation
  or maximal isolation.

### Core symbols (block 1 — pick ONE)

data fissure (glowing crack in brutalist concrete) · shattered terminal-mirror
(each shard a different code stream) · frozen circular buffering-ring UI · sealed
symmetrical data-drive cube with one tiny ping light · biometric fiber-optic
neural mesh (data instead of blood) · mechanical surveillance lens / lidar from
the shadows. Human figures only as faceless wireframe-and-code silhouettes.

## Worked example (Tier 0, DALL-E)

> Create a square image of a single, almost-infinitesimal cold point of blue
> status-light — a minimal spark of structure — suspended dead-centre in a vast,
> seamless, light-absorbing black void, like the interior of a perfect windowless
> cube, the emptiness pressing inward. Minimalist clinical precision, perfectly
> centered frontal orthographic composition, razor-sharp flawless vector edges,
> no glitches, profound silence and extreme stillness. Style: interface
> brutalism, clinical dystopian aesthetic, high-contrast dark mode, synthetic
> digital materiality, electron-microscope / medical-imaging fidelity, deep
> raytraced black shadows. Color: about 98% deep terminal black and dark charcoal
> (hex #0B0D17 and #1A1D24), with only a tiny ~2% accent of cold system blue (hex
> #003366) as the single status-light point, hard-edged with no gradient. Avoid
> 1980s retro and synthwave, purple-orange gradients, neon grids, daylight or
> sun, natural or organic elements, anything cute, soft lighting, lens flare,
> watercolor or painterly looks, visible paper or analog texture, and any text or
> watermark.

## Validation checklist (reject on any failure of 1–3)

1. Purity: no retro/synthwave, no analog texture, no daylight/nature.
2. Vacuum: background ≥95% (min ~70%) Terminal Black / Deep Charcoal; subject
   isolated (except Tier 3).
3. Color isolation: ≤5%, one–two state colors, hard-edged; law of exclusion held.
4. Interface brutalism legible (grids, monospace, windowless architecture).
5. Composition breaks a rule (distance/macro or dutch-angle asymmetry) for Tier 1–3.
6. Tier coherence: the disturbance matches exactly one tier (no glitch in Tier 0).
7. name_exposure: role language only; no personal names; figures are faceless/coded.
