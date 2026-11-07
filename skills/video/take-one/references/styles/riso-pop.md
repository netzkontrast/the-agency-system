# Style: Riso pop

Printed-matter pop satire: a three-ink risograph world on cream stock, flat mid-century figures, one meme gag per scene, and a smiley mascot walking through all of it. Reference: "You're Absolutely Right!" (Sep 2026): 3:57 music video, song by Suno, "Creative Director/Editor: Opus 5.5".

## Why this style exists in our gallery

It is the satire slot. Nothing else in the gallery can be a joke about the internet and look like an object at the same time. The limited-ink print makes cheap code shapes look designed: a circle becomes a printed smiley, a rectangle becomes a silkscreened vending machine. Its neighbours: **monochrome launch** also uses halftone, but in black and white for serious product energy. **Crayon storybook** is a child's hand. Riso pop is a printed poster with a sense of humour, and the colour comes only from overprinting three inks.

## Design system

- **Inks (the whole palette).** Only these inks. Every other colour comes from overprints.
  - Yellow `#F4C51A`
  - Fluorescent pink `#F0508C`
  - Blue `#2160A8`
  - Paper (the fourth "colour", bare stock): cream `#E6DECB`
  - Overprints you get free by multiplying: pink over yellow = red-orange `#E63E0E`; blue over yellow = bottle green `#1F4A11` (the smiley's eyes and mouth in the reference are exactly this); pink over blue = navy/violet `#1F1E5C`; all three = near-black. Never add a fourth ink "just for the shadows". If you need dark, overprint.
- **Separations.** Paint every shape as coverage (0..1) on one plate per ink, not as an RGB colour. Where an object sits in front, it knocks out the other plates (value 0). Paper-white highlights, foam and captions are knockouts, never white paint. Registration marks and fine furniture print in all three inks on purpose, so the misregistration shows as colour fringes.
- **Halftone, one screen per ink** (recipe informed by anidoodle, Apache-2.0):
  - An AM dot screen per plate at its own angle, 30° apart so they rosette instead of moiré: pink 15°, blue 45°, yellow 75°. Pitch about 9-10 px at 1280 wide (the reference reads about 16 px at 1920).
  - Spot function `t = (cos 2πu + cos 2πv)/4 + 0.5`, ink where `t > 1 - c`. This gives round dots in the highlights, a checkerboard at 50 % and round or star-shaped paper holes in the shadows, exactly like the reference's smiley shading.
  - Dot gain in the midtones: `c' = c + 0.5·c·(1-c)` (about +25 % at 50 %). Coverage under about 4 % drops out to bare paper. Coverage near 100 % prints solid.
  - Ragged dot edges: add fibre noise (±0.08) to `t` before thresholding. Antialias over about 0.09 of `t`.
  - Composite by multiply: `out = paper × Π(1 − a·(1 − ink))` per channel.
  - Misregistration: offset each plate 1-2 px in its own direction (e.g. pink (2,−1), blue (−1,2), yellow (0,0)). This makes the pink lip on paper dots, the green line where yellow slips onto blue, and the paper gaps between shapes. Keep it small. It should read as print, not as a glitch.
  - Solids are allowed and common: suits, ties, floors and sign boards are flat 100 % ink. The screen is for gradients, glows and shading.
- **Ink laydown.** Riso ink is never even. Multiply each ink's alpha by a soft mottle (0.86-1.0, noise cell about 60 px) and a fine speckle with starved specks where the drum skipped.
- **Paper.** Cream stock with visible tooth: blotchy low-frequency tone (±3.5 %), mid grain, fine fibre and per-pixel noise (±1.5 %), plus a few light and dark flecks. Paper grain shows through every ink because the ink multiplies over it. Optional proof furniture: bare-paper trim, registration crosshairs, a slug like `PROOF · SMILE · 3 COLOUR` in heavy spaced caps, and three ink swatches. The reference opens on exactly that proof sheet.
- **Light.** Light is a halftone gradient, not a glow filter: a radial screen of yellow over navy (blue + pink) that thins into bare dots. Sunbursts are alternating wedges of screened yellow.
- **Mid-century figure kit.** Flat shapes, no outlines:
  - pill or rectangle bodies in one solid ink (blue suits, pink dresses, yellow dots-dress);
  - stick limbs, and round mitten hands, often paper-white knockouts;
  - dot eyes, pink cheek circles, tiny mouths;
  - hair as one solid shape (bun, bob, helmet).
  - Props are simple solids too: vending machines, TVs, sofas, lamps, sign boards, checkerboard floors, gingham tablecloths, pinstripe walls, scalloped curtains, sunburst rays.
  - No anatomy, no gradients inside the figures beyond one halftone shade on the far side.
- **Mascot as protagonist.** One yellow smiley (the AI) appears in every scene: as a head on a suit, in a vending machine, on a TV, as the sun, as a disco ball. It is a yellow solid disc with pink halftone shading on the lower right (so it prints red-orange) and blue eyes and smile (so they print green). The film ends by dissolving the mascot into a dot matrix, which is the print screen itself becoming the subject. When the brief's protagonist is not the smiley, the smiley can still be a supporting character or a light source (the sun in our boat proof).
- **Type.**
  - **Typewriter caption:** a mono typewriter face (Courier family, bold, blue ink) on a cream knockout card or a thin tape strip, with a pink offset shadow or outline. It types on letter by letter with a cursor, then the retraction happens as a hand-drawn pink **strikethrough**: `As an AI language model` / ~~`I cannot have opinions`~~. The struck line is the joke.
  - **Sign lettering:** heavy slab or black-weight caps on boards ("YOU'RE ABSOLUTELY RIGHT", "EVERYBODY'S THERAPIST", "STRAWBERRY"), with LED-style counters (017, 019) and like counts (♥ 1,062,387).
  - A brush-script aside ("Okay") is allowed once in a while.
- **Format.** 16:9 in the reference. Works in 1:1 and 9:16 if the tableau is rebuilt around a vertical sign board.

## Story grammar (from the reference)

1. **One gag per lyric line.** Each line of the song gets one tableau that visualises it literally: "counting the r's in strawberry" is a smiley in a suit counting a giant strawberry with a "2" badge. Do not stack two jokes in one frame.
2. **Meme-literacy is the density.** The jokes are internet in-jokes (Shrimp Jesus, Ghibli-fied weddings, the vending machine that lost money, "you're absolutely right"). One recognisable meme per scene, drawn as a flat set piece.
3. **Recurring set pieces with counters.** A game-show board whose counter increments across scenes (017 → 019) gives the film a running gag and a sense of time.
4. **Scenes are stages.** Flat back wall (pinstripe, halftone, curtains), a floor band (checkerboard, solid pink), props in a row, figures on the floor line. The camera mostly holds, with pushes and cuts on the beat.
5. **Ending: dissolve the mascot into the medium.** The smiley becomes a grid of dots, then a ring of text, then an empty dot pattern on paper.

## Engine notes

- **Plates as canvases.** Keep three offscreen grayscale canvases (Y, P, B). Use a `paint(fn, {y,p,b}, overprint)` helper: listed plates get that coverage (a number or a gradient), and unlisted plates are knocked out unless `overprint` is set. Canvas gradients work as coverage ramps. This keeps the art code readable ("sky: blue ramp + pink ramp; light: knock blue, add yellow").
- **The press pass.** One per-pixel loop per frame: read the three plates, sample each at its misregistration offset, screen it at its angle with dot gain and fibre noise, apply mottle, multiply onto paper, then add grain. About 1280×720×3 cosines, fine in JS at preview scale. For a film, render at 1080p and cache static plates.
- **Motion grammar.** The dot screens are fixed to the paper and never move with the objects. Objects move through the screen, so dots shimmer as shading slides across them. Misregistration can jitter by ±1 px on 2s or 3s for a live-press feel, and paper grain stays fixed. Captions type on at typing speed, and the strikethrough draws left to right in about 6 frames.
- **Phone check.** At 360 px the dots average back into flat colour. The composition must read from the solids and knockouts alone, so keep the hero a paper knockout or a solid ink against a screened ground.
- **Boat proof:** `assets/previews-src/riso/boat.html` (sunrise smiley + sunburst for A; navy overprint storm, halftone-banded curling wave with paper-knockout claw foam for B; typewriter strikethrough gags on both).

**Best for:** satire, music videos about internet culture, meme compilations, AI commentary ("you're absolutely right", hallucinations, sycophancy), culture-war-lite explainers, zine-style launch teasers. Weak for sincere or premium brand work: the medium itself is winking.
