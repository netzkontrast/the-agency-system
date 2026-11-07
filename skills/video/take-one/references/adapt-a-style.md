<!-- Adapted from anidoodle (github.com/alexgreensh/anidoodle), Apache License 2.0, Copyright 2026 Alex Greenshpun -->

# Learn a style from a reference

The user shares a link or a video: "I love this look, can we do this?" The rule: **borrow the hand, never the picture.** A hand is a way of making marks: what touches the paper, what the edge does, the order things go down, the ground, the palette, how it moves. The reference's subject, composition, characters and text are not material; none of that crosses over.

Numbers help you look; they never decide. Every statistic of an image mixes subject, layout, lighting and medium: a mostly empty frame reads "light key, few edges" whatever hand drew it, and lettering reads as "line". Anidoodle proved this the hard way: in both of their documented adapt-a-style runs, the statistical nearest style was wrong. The verdict is a written recipe and the two PAPER BOAT frames rendered in the new hand.

## The workflow

1. **Get the pixels.** Download the video (or save the image). Contact-sheet it:
   ```bash
   scripts/contact-sheet.sh <video> [outdir]
   ```
   which writes a 6x4 sheet across the whole length plus 3 full frames (`frame-0.15.png`, `frame-0.5.png`, `frame-0.8.png`). Reference material stays in a study folder outside the skill, never in the skill (the gallery shows only our own renders).

2. **Analyze 2-3 frames** (visually different ones: a wide, a busy, a dark):
   ```bash
   node scripts/analyze-style.mjs <frame.png> --json <outdir>/profile.json
   # or straight off the video: node scripts/analyze-style.mjs <video> --frame 240
   ```
   It prints the palette (OKLab k-means, ground and darkest ink, area shares), value key and contrast, line presence and width, stroke direction and coherence (structure tensor on the grain), stroke length, speckle, edge hardness and pooled rims, spectrum slope, and a periodic-lattice (halftone) detector, then a prose summary. Exclude what is not the hand, UI and captions above all: `--exclude x,y,w,h;x,y,w,h`, or `--crop x,y,w,h` to a clean region.

3. **LOOK before you trust a number.** Open a frame at full size AND a 3x crop of a busy region, and write down what you see: what touched the surface, how wet or dry, what one unit mark is, what the edges do, what order things went down in. Only then read the profile, for what the eye misses: an exact ground hex, a stroke direction, a halftone pitch, whether edges pool. Where your eyes and the numbers disagree, the eyes win and you say so.

4. **Write the recipe as a style file**, `references/styles/<id>.md`, in our house format (exemplar: `references/styles/crayon-storybook.md`: reference credit line up top, "why this style exists", Design system, story grammar if the reference teaches one, Engine notes, "Best for"). The design system must fill these slots, in words a builder can execute:
   - **Medium, physically:** what touches the surface, how wet, what the ground does back.
   - **Marks:** the unit mark, its size, what varies along it.
   - **Edge:** hard, soft, lost, pooled, torn; where the edge darkens or disappears.
   - **Order:** what goes down first and what last. The order is half the hand.
   - **Palette:** the colours **with hex values**, the ground, and the value range they live in.
   - **Light:** one named source and what it does to the marks.
   - **Motion grammar:** how this hand moves: boil rate, what animates vs what holds, camera behaviour, transition devices, pacing/beat length.
   - **Not its neighbour:** name the nearest style already in our gallery (`SKILL.md` step 2 table) and the one or two things that make this one differ. If nothing real differs, it is not a new style; fold the lesson into the existing file instead.

5. **Provenance, in the style file's header block:** the source link, who brought it, the date, and the line "no reference pixel is copied; only tools read the image". The reference's subject, composition, characters, signature motifs and text are never reproduced; a living artist's signature motifs never cross over. Render code never opens the reference file.

6. **PROVE it: render the two PAPER BOAT frames** per `assets/previews-src/BOAT-BRIEF.md` (frame A "setting out", frame B "the storm peak", all code, deterministic) before the gallery card ships. This is the side-by-side test on a DIFFERENT subject: same hand, new picture. Self-review per the brief (full size and 360 px wide, honest 1-10 per frame); running `analyze-style.mjs` on your own frames next to the reference's profile is a good diagnostic, but iterate on the recipe, not on the numbers. Two or three rounds is normal.

7. **Ship it:** add the gallery card (`assets/gallery.html` + the two jpgs in `assets/previews/`), add the style row to the SKILL.md step 2 table, and **add the `examples/INDEX.md` row** for the reference (link, stats, style, how it was made, lesson), per the INDEX header.

## The no-copy rule

- Never trace, re-lay-out or re-stage the reference. New subject, new composition, always; the boat brief enforces this by construction.
- No reference pixel is copied; only tools read the image (`contact-sheet.sh`, `analyze-style.mjs`, your eyes on the frames).
- A small statistical distance cannot certify "a convincing adaptation", and no distance can certify "not a copy". The recipe in words plus the boat frames are the only verdicts.
