# Style: Monochrome launch film

Stark black-and-white product launch film with liquid-chrome materials and quant-editorial texture. Reference: "Frontier Traders" (Sep 2026): 30 s, 4K, "Opus 5.5 one shotted this whole video in 20 mins".

## Design system

- **Palette: pure #000 and pure #FFF only.** Secondary type in grey (#999). No accent color anywhere, with ONE exception: a single prestige moment where a material carries color (the reference fans out membership cards and one is gold). The restraint is what makes that moment land.
- **Section inversion is the rhythm.** Hard cuts between full-black worlds and full-white worlds, roughly alternating. Black = atmosphere and matter; white = data and proof.
- **Type:** big lowercase grotesque sans. Two-word lines split across the frame ("across ... solana", "get rewarded ... for what you do", one part white/black, the other grey). Tiny mono captions for secondary lines. Type is always flat on the frame, never in the scene.
- **Black-world matter (the wow):** liquid chrome curtains and ripples, a particle Earth of city lights, halftone/dither photographic silhouettes (a figure emerging from ripple-dither), dot-grid rain, metallic 3D logo renders. All monochrome, all tactile.
- **White-world data (the proof):** multi-series line charts as background texture with one bold hero series, dashed crosshair callouts with a live ticking number ($2,071.79 → $2,077.80), dot-grid blocks, thin rules. Reads like a quant terminal art-directed by a fashion magazine.
- **Icon-scatter storytelling:** small white tiles with product glyphs scattered across a black tile grid ("your activity gets scattered"), then consolidating into order. The motion IS the message; entropy → order is the arc. Same with dash-fields that align into a grid.
- **Photographic inserts** as b/w luxury stock (a car interior at night, a private jet, a Renaissance painting for "Global Community"): 1-2 s each, deadpan prestige, slightly ironic. Model-made or real b/w photography; keep them desaturated to pure mono.
- **3D product objects:** metallic logo, membership cards fanned in tiers. Simple geometry + studio lighting + chrome/foil material; monochrome hides 3D imperfections.

## Structure (30-40 s)

1. Logo tease in matter (chrome, particles) with the category line.
2. The problem told by scatter (icons/dots dispersing) in the black world.
3. Invert to white: the product name, huge.
4. Proof beats in the white world: charts, live numbers, feature names ("Trading Rewards", "VIP tiers"), each 2-3 s.
5. The prestige moment (the one color: gold card, tier fan).
6. Community/scale insert (the painting, the globe).
7. Logo lockup repeated as an end grid.

## Why it works

- Monochrome + chrome flatters generated and code-drawn assets equally; there is no palette to mismatch.
- The inversion rhythm gives cutting energy without any camera moves.
- Live numbers and charts make an abstract product feel real and expensive.

**Best for:** fintech/crypto/trading launches, premium dev tools, anything that wants "expensive Swiss editorial" without a brand palette. A natural fit when the brand's colors are weak or undecided: mono sidesteps the question.

**Engine:** code-only is fully viable (chrome via layered sine displacement + specular ramps, dither via ordered-dither shader on any grey image, charts and counters native). Model assets optional for the photographic inserts and chrome close-ups.
