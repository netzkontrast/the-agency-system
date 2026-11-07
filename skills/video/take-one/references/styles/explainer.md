# Style: Clean kinetic explainer

A 15-30 s product or idea explainer that feels like a top design studio made it. Reference: a product explainer for a workflow tool (Sep 2026): white page, one blue, giant type, a dithered mascot, UI cards that assemble.

## Design system (decide all of it before building, then never deviate)

- **Background:** off-white (#FAFAF8 range). One full-bleed accent-color scene is allowed as a punctuation beat, and one black scene near the end for the tagline.
- **One accent color** (that explainer used royal blue ~#2563EB). Everything else is black and greys. The accent marks only what matters: the key word, the button, the checkmark, the chart's last bar.
- **Three fonts, each with one job:**
  - a bold geometric sans (Inter Display / Geist / Satoshi style) for the message, very large (120-200 px at 1080p);
  - a **handwritten-feeling italic serif for exactly one word per line** ("Got something to *sell?*", "a store in *minutes.*", "*Handled.*"). This contrast is the signature move;
  - a small monospace for labels that make it feel engineered: `// 01 — hook` top-left, `BRAND 00:00:10:30` running timecode top-right, `// checkout` on cards.
  Google Fonts may be loaded (the page is served over local http during render). Wait for `document.fonts.ready` before setting `window.READY`.
- **A mascot or character, dithered to 1-bit** (ordered Bayer dithering, black dots on white). Source it as an image (image model, the user's logo character, or their photo) and dither it in code at load time. It reacts: looks at the text, winks, speaks a tiny bubble ("psst..."). It is the warmth in a cold UI world.
- **UI cards** for the product: white cards, 1 px grey border, 16-24 px radius, generous padding, real-looking numbers ($149.00, 4242 4242 4242 4242, EU VAT ✓). A bento grid of 4-6 cards that fills in piece by piece is the classic "it's all handled" beat.

## Motion

- Type arrives **word by word, in sync with the idea** ("Got" / "something" / "to *sell?*"), each word a fast ease-out with a slight rise; the italic word lands last with a little overshoot.
- One idea per scene, 1.5-3 s each. Cuts are clean: slide, push, a mask wipe, or one fast whip ("Apple Pay" streaking across) for energy, then calm again.
- The mascot moves subtly all the time (breathing, blinking, glance) so the frame never feels dead.
- Numbers count up; checkboxes tick; charts grow; a stamp word ("*Handled.*") slams in at an angle over the grid.
- All of it on springs (`timing.md` presets: `snappy` for cards and ticks, `heavy` for the stamp word, `playful` for the mascot). Export the master with `SUB=8` so whips and flying type carry real motion blur.

## Launch grammar (type and product moves from the best launch videos)

- **Focus-pull word reveals:** each word arrives from a blur (draw it 2-3 times at small offsets with falling alpha, converging to one sharp copy over ~0.3 s) instead of sliding in. Reads as a lens, not a slide.
- **In-place word swaps:** one word in a held sentence changes ("Built for *teams.*" → "*founders.*" → "*you.*"): the old word lifts and fades, the new one rises into the same baseline, the sentence never moves.
- **Inline icons inside sentences:** a real icon or logo sits in the line of type at cap height, as a word ("Send it to [Slack icon] in one click"). Real integrations only.
- **One sentence across 2-3 beats:** "Your whole team" / (card grid assembles) / "in one place." The picture fills the pause in the sentence; the viewer reads it as one thought.
- **The component macro:** lift one real control onto a clean field at 3-5x, perform the interaction, show the result, spring back into the full UI (`real-product.md`).
- Any number on a card that isn't the product's real data carries a small **"Example data"** label.

## Beat sheet template (15 s)

| Time | Beat |
|---|---|
| 0-3 | Hook question to the viewer, mascot reacts ("Got something to *sell?*") |
| 3-5 | The things they have (cards pop in: courses, ebooks, apps) on the accent background |
| 5-8 | The product turns it into the solution, shown in a phone or window ("turns it into a store in *minutes.*") |
| 8-12 | Bento grid: every painful thing, handled, cards filling in, then the stamp word |
| 12-14 | Tagline on black ("You *create.* We handle the rest.") |
| 14-15 | Logo + one line + URL; mascot peeks in |

## Engine

Plain canvas 2D (or HTML/CSS drawn to canvas) via `scripts/new-canvas-project.sh`. Draw type with `ctx.fillText` using the loaded fonts; UI cards as rounded rects with real text. Keep everything crisp: integer-pixel strokes, no blur except deliberate motion blur on the whip.
