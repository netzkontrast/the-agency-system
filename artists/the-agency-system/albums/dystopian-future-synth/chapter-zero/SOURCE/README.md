# Kapitel 0 — SOURCE/

Extracted source material for **"Kapitel 0 — Maximal Edition · ASDLS"**, the
interactive HTML chapter of the *the-agency-system* novel (a DID-system concept
expressed across novel / music / design layers). This folder splits the single
~1 MB interactive document into domain-specific, human-readable reference files
plus the verbatim original.

The chapter dramatises one **coherence (KOH) arc** — a proto-self holds against
the Nichts, differentiates into emotional parts, is perturbed by JUNA, collapses
(0.18), and is surgically partitioned by Protocol KOH_1.0 (0.00 → forced 1.00),
from which the host **Kael** wakes.

## Files in this folder

| File | What it contains | When to consult |
|---|---|---|
| `kapitel-0.html` | The raw original interactive source (verbatim copy of the styled chapter — prose, CSS, JS, fonts, all bundled). | When you need the exact, runnable artifact or to re-extract anything. The canonical source of truth. |
| `kapitel-0.md` | The decoded **German prose** — all 14 sections in narrative order (narration + voice lines + system logs). | When working with the actual text: lyric adaptation, quotation, translation, plagiarism scans. Novel layer — names allowed; never paste into music/design outputs. |
| `asdls-design.md` | The **visual design system** from the `<style>` blocks: full colour palette (hex + semantic role), typography, layout classes (`.hud`, `.progress`, `.cover`, `.text-layout`), per-voice `.voice-block` styling + corner brackets, and the glitch / climax / animation CSS. | When building the design layer, deriving art-direction colour/type, or reproducing the coherence-driven visual language. |
| `dynamics.md` | The **interactive behaviours** from the `<script>` blocks, described conceptually: boot/cover KOH-ignition, scroll-driven HUD telemetry (`updateHud`), per-voice background animations, the glitch state machine, climax escalation, and the kintsugi shatter-reveal. | When you need to understand how the page *behaves* — triggers, narrative moments — without reading the code. |
| `section-meta.md` | The decoded `SECTION_META` map as a table: per section → id, KOH value, tier/state label, signature colour, annotation. Traces the coherence arc 0.998 → 0.18 → forced 1.00. | Load-bearing reference for the chapter's emotional/structural arc, tier→colour mapping, and section ordering. |
| `cast.md` | The voice codes (`frg`, `aeg`, `nar`, `kik`, `lia`, `rhy`, `nyx`, `lex`, `arg`, `mor`, `sil`, `kal`, `obv`) → function/role → novel name, each with verbatim fingerprint lines. Notes which of the canonical Eleven are absent. | When attributing lines to alters, checking voice consistency, or bridging novel names ↔ design/music functions. |
| `ASDLS.md` | The full **Agency System Design Language Spec** (verbatim): the S0–S4 / Tier 0–4 state machine, the polyphonic hex typology + 5%-rule, glitch grammar (chromatic aberration, data moshing, vector jitter, packet loss), the one-tier-per-image and Flame-never-with-Clean-Ping constraints, motion/no-gradient rules. | The authoritative design-language contract. Load when deriving any art-direction, colour, motion, or state-visual decision — and to settle tier/colour disputes. |
| `masterkonzept.md` | The **visual master concept** (German): ASDLS → analog "Bildsprache Julia" synthesis. Philosophical grounding, the analog-glitch-as-somatic-symptom typology table, polyphonic colour thermodynamics, and per-alter (×13) tool/line/colour/composition grammars. | When translating the design contract into emotionally-grounded analog art direction, or sourcing per-alter visual texture. Companion to `ASDLS.md`. |
| `Sprachdns.md` | The **voice / language DNA** (English translation): per-function speech fingerprints — register, syntax, cadence, lexical tics, silences — for the system's voices across states. | When writing or reviewing lyrics/voice lines: to keep each function's idiolect faithful. Pull texture here; obey the name_exposure hard rule (function-only in music/design). |

## How this folder was produced

All files were extracted from `kapitel-0.html` (a verbatim copy of the project's
top-level `index.html`). That file is a self-contained "bundler" wrapper: the
real document lives as a JSON-escaped string under a `<script
type="__bundler/template">` tag, and its assets (fonts + the five
`window.KP0_PART1…PART5` prose arrays) are gzip+base64 entries in a
`__bundler/manifest` block.

Production steps:

1. **Decoded the bundler template** → a clean 155 KB HTML document.
2. **CSS and JS were plain text** in that document. `asdls-design.md` was
   distilled from the `:root` palette block and the main `<style>` rules;
   `dynamics.md` from the four `<script>` units (boot engine, render+HUD+glitch
   engine, `playKintsugiShatter` library, end-shatter trigger).
3. **`SECTION_META`** was read directly from its `const SECTION_META = {…}`
   declaration and rendered into `section-meta.md`, ordered by the true
   narrative sequence (`KP0_PART1…PART5` concatenation).
4. **The prose `window.KP0_PART*` arrays** were gzip-decompressed from the
   manifest to recover the `{v,t,x}` blocks; `cast.md`'s fingerprint samples were
   pulled from those blocks, mapped to functions/names via
   `skills/theagencysystem/references/resolver.yaml`. (The full decoded prose
   already lives in `kapitel-0.md`.)

Read-only on the source: nothing outside this `SOURCE/` folder was modified.
