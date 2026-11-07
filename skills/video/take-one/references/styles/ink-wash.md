# Style: Ink wash (sumi-e)

Chinese/Japanese ink painting (水墨 / sumi-e) on absorbent rice paper: diluted ink strokes that bleed and breathe, vast negative space, one cinnabar-red seal. Evidence the look travels: an Opus 5.5 ink-landscape piece and another Opus 5.5 boat journey through Japanese landscapes — misty mountains dissolving into blank air, water carried by reflection alone, one small boat against emptiness. Recipe informed by anidoodle (Apache-2.0).

## Why this style exists in our gallery

It is our only style where **the paper is the light** and emptiness is the composition. Watercolor and crayon fill the frame; sumi-e leaves most of it bare and makes the few marks carry everything. Because every mark is one uncorrectable gesture, it renders fast (dozens of strokes, not thousands), scales to any subject that can be reduced to gesture, and its native motion grammar — the painting drawing itself stroke by stroke — is mesmerizing on a feed with zero character-animation risk.

## Design system

- **MEDIUM, physically:** one soft brush of real hairs, loaded from an inkstone and reloaded rarely, on unsized xuan (rice) paper that drinks ink the instant it touches. Nothing can be corrected or covered. Each hair holds its own ink and spends it with travel, so a stroke starts wet-dark and ends in dry-brush "flying white" (飞白): streaks of bare paper running WITH the stroke, split hairs splaying at the lift. Wherever the brush slows (touch-down, a pause, the lift) the ink bleeds a soft halo into the paper fibres, with fine feathers wicking outward — the tell of absorbent paper. Edges are soft-feathered where wet, broken and bristled where dry, never a clean outline.
- **THE FIVE INKS (墨分五色):** tone ONLY by dilution — scorched (jiao 1.0), thick (nong 0.82), heavy (zhong 0.6), light (dan 0.38), clear (qing 0.2). Diluted sumi cools toward blue-grey as the carbon thins (#0f0d0c → #39414a); it never goes brown. **Depth is dilution:** the near thing is thick ink, the far thing is clear, the farthest is barely a breath.
- **MARKS:** every mark is one gesture with a pressure envelope — a leaf touches at a point, presses to full width, lifts to a point; a hull is one confident side-laid drag that breaks into flying white; a mountain is one wet flank of the brush. No hatching, no scribble, no outline-then-fill.
- **ORDER (half the hand):** near before far within a subject, structure before detail — stalks, then nodes, then branches, then leaves; hull, then mast, then rigging. Wet washes (mist, sky) go down early so crisp marks sit on top. Dry accents (moss dots, spray flicks) near the end. **The seal is stamped last, always.**
- **PALETTE:** warm unbleached xuan paper (#f3ede0) with long pale fibres and bark flecks in the sheet; one ink at five dilutions; and exactly ONE color: the cinnabar seal (#b8352b). Nothing else, ever.
- **PAPER / NEGATIVE SPACE:** the paper IS the light, the water, the sky, the mist, the lit side of everything. Aim for 60-80% of the frame left bare or near-bare. Mist is an absence: shapes simply stop where the mist begins.
- **THE SEAL:** a baiwen (white-line) seal — invented seal-script glyphs cut INTO the stone, so they print as paper inside a red block with a worn, chipped border, paste pressed unevenly. One per composition, in a corner, balancing the emptiness. It is the only red in the frame.
- **LIGHT:** diffuse, one implied direction. Sumi-e carries light by leaving paper, not by cast shadow: the lit crown is the brush's dry lift, the lit belly is bare paper. A sun or lantern is a pale near-clear ring or a gap left in a wash.
- **MOTION GRAMMAR:** two devices, both native. (1) **Strokes draw themselves:** the film is the painting being painted — each mark grows along its centreline at a hand's pace, touch-down bleeds, travel, lift, then the slow points keep soaking a moment after the brush leaves. Finished marks never change. (2) **Mist reveals:** clear-ink washes thin or thicken to disclose and swallow shapes; a mountain "arrives" by the mist withdrawing, not by moving. Camera moves are slow horizontal handscroll pans (emaki), if any. Never squash-and-stretch, never bounces: things enter by being painted or unveiled.
- **FORMAT:** 16:9 or vertical hanging-scroll crops both read; must survive muted (it is silent by nature — score with solo shakuhachi/guqin-feeling sparse music).

## Engine notes

- **Brush = hairs, not a line.** A stroke is: hand-placed control points (smoothed + resampled), a width, a pressure-knot profile, a dilution, and per-hair state. Each of ~10-40 hairs gets its own ink load (edge hairs more on a side-laid stroke, tip hairs more on a pointed one, high variance when half-loaded = streak mode); load decays per px of travel; a hair skips (bare paper) where load loses to paper-tooth noise — that IS flying white. Draw hairs at the dilution's tone in ONE multiply pass: ink does not stack with itself inside a stroke, only where a second stroke crosses.
- **Bleed layer under the hairs:** at declared slow points, a wobbly-edged blob (radius ~ local width) plus 10-24 single-fibre feather lines wicking outward, all blurred 2-4px, multiply, low alpha; plus a faint halo a hair wider than the stroke wherever the brush was still wet. Wet-into-wet (mist, storm sky) = the same stroke with heavy blur and lowered alpha.
- **Paper first, grain last:** fibres and flecks drawn under everything; a light paper-grain modulation over everything.
- **Self-drawing films:** keep an ordered op list (one op per stroke); finished ops composite once into a cached bitmap, only the stroke in hand redraws each frame, cut partway along its centreline. Frame 0 is bare paper; the last frame equals the still exactly. Time per stroke ~ length + a constant per brush lift.
- **Determinism:** seeded rng per stroke; same seed, same fibres, same flying white.

## Not its neighbour

- **Watercolor** (our western picture-book style): watercolor is COLOR laid in transparent overlapping pools with hard pooled rims, filling the frame, characters acting with faces. Sumi-e is one ink where tone is dilution, marks are single calligraphic gestures with flying white, the frame stays mostly empty, and figures are stroke-economy silhouettes. If it has more than one color (plus the seal) or a colored wash, it has drifted to watercolor.
- **Painterly glow** (Van Gogh oil): that style is opaque impasto strokes covering every pixel with additive glow. Sumi-e is transparent, subtractive (multiply), and mostly paper.

**Best for:** journeys and landscapes, solitude and scale, poems and proverbs, martial-arts or nature subjects, meditative brand films, anything where restraint reads as confidence. Weak for: dense UI/product demos, dialogue comedy, anything needing many colors.
