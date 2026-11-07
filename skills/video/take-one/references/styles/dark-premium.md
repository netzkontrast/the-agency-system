# Style: Dark premium explainer

Near-black canvas, one warm metallic accent, cinematic light. For serious AI and B2B concepts. Reference: a concept video for an AI infrastructure company (Sep 2026), which had the right look but a 2-minute runtime, a dozen ideas, and small low-contrast text. This style file is that look with the fixes.

## Design system

- **Background:** near-black with depth (#0B0B0F to #15151C radial), a faint film grain, subtle vignette.
- **One accent:** warm gold/amber (#F5B544 range) used for light, the key word, the hero object. Optional second hue only for "before" states (a cold grey-blue).
- **Type:** a clean sans, large and bright (#F4F1EA), 90-160 px for statements; **one italic serif accent word per line in the accent color** ("What if it worked *like that?*"); small mono labels for structure (`// the old way`, `01 · Start`).
- **Hero object:** one glowing, tactile object that represents the product (a card, a key, a core, a lens). It gets the light, the particles, the close-ups.
- **UI cards:** frosted dark cards with 1 px light borders, used sparingly and **big**. That video's failure: grids of tiny cards unreadable on a phone.

## Hard fixes (why the reference didn't land)

- **One idea, 30-45 s.** Pick the single sentence the video must leave behind and cut every scene that doesn't serve it. Two minutes and twelve concepts lose everyone.
- **Contrast:** statement text is near-white on near-black, never grey on grey. Test every frame at phone size (360 px wide contact sheet).
- **Max one read per beat,** 2-3 s per beat. No dense diagrams; show a transformation instead (dull → glowing, many → one).
- **A human anchor** if possible: a character, a face, or a relatable before/after, because abstract particles don't carry emotion.

## Beat sheet template (35 s)

| Time | Beat |
|---|---|
| 0-4 | A famous, instantly recognizable hook (for example a line from a film everyone knows, typed in a terminal) |
| 4-8 | The question it raises ("What if it worked *like that?*") |
| 8-15 | The old way, shown as pain in one visual (slow, costly, frozen) |
| 15-26 | The hero object appears in light; the one transformation that is the product |
| 26-32 | The payoff line, huge ("No *waiting.*") |
| 32-35 | Logo + tagline, the hero object glowing |

## Engine

Canvas 2D (or WebGL2 for glow/particles) via `scripts/new-canvas-project.sh`. Glows are additive (`globalCompositeOperation = 'lighter'`), grain is a static seeded noise layer, depth of field is a blur on background layers only.
