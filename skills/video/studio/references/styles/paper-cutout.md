# Style: Paper cut-out

Flat cut- and torn-paper layers stacked like a collage on an animator's table, with REAL drop shadows between the layers. The shadows are the style: every piece floats a few millimeters above the piece below it, and the soft offset shadow underneath is what sells the physicality. Evidence: an Opus 5.5 flat-layered short ("Claude Opus 5.5 has the best visual design of any model I have tested so far"), a paper-collage reel, and an MIT-licensed open-source paper-animation engine, which proves the whole grammar can be driven deterministically in code: torn edges that boil, fiber texture, drop shadows, rim light, spring-driven rigs, fixed timestep + seeded randomness.

## Why this style exists in our gallery

Same bet as crayon storybook, different physics: **the medium's limits are the charm**. Paper pieces cannot deform, so nothing can go off-model; a character is a stack of stiff shapes pinned at joints, and jerky hinge motion reads as craft, not error. Where crayon wins on childlike warmth, paper cut-out wins on tactility and depth: it looks handmade AND dimensional, and it photographs beautifully as stills (every frame is a collage you could frame). Strong pick for storybook narratives, folk tales, indie-craft product films, and anything where "someone made this with scissors" is the emotional register.

## Design system

- **Ground:** a paper world, edge to edge. The backdrop is itself a sheet (kraft, construction, or watercolor-washed paper), never a flat digital color. Scene depth = 4-8 stacked layers, back to front.
- **Pieces:** every element is one filled path of "paper". Two edge families:
  - **Scissor cut:** clean-ish outline with slight wobble and occasional straight over-cuts at corners, like real scissor strokes.
  - **Torn:** wild ragged perimeter with a pale fiber fringe (the white inner core of the paper exposed along the tear). Use tears for organic/violent things: waves, clouds, smoke, fur, storms.
- **Shadows:** one global light direction for the whole scene. Each layer casts a soft drop shadow onto the layer below, offset along the light direction, with offset and blur growing with the layer's height in the stack. Shadows are multiplied, never pure black. This is non-negotiable; without the shadows it's just flat vector art.
- **Texture:** every piece carries subtle paper grain (fiber noise, slight tone variation across the piece); big washed sheets may show watercolor blotching. Matte only, no gloss, no gradients that read as airbrush.
- **Palette:** construction-paper box: brick red, marigold, teal, leaf green, kraft brown, cream, dusty navy, plus one bright accent per film. Colors are flat per piece; variation comes from texture and shadow, not shading.
- **Characters:** built like the reference's box-bots: a few stiff shapes (body sheet, head sheet, limb strips, dot eyes as tiny punched circles). Emotion via tilt, hop, eye size, and piece spacing. No faces drawn ON pieces beyond simple punched/cut features.
- **Type:** cut-letter captions (each word a small paper strip with its own shadow) or a caption bar that is itself a paper strip laid across the bottom.

## Motion grammar

- **Hinge-and-pivot only.** Limbs are pinned like brads/puppet joints; all motion is rotation around pins plus whole-piece slides and lifts. NEVER deform, bend, squash, or morph a piece. A wave "rolls" by rotating and sliding its strips against each other, not by changing shape.
- **The lift:** for emphasis, a piece rises off the table: shadow offset and blur grow, then snap back on landing. This is the style's squash-and-stretch substitute.
- **Boil:** re-seed the edge jitter of torn pieces at 6-8 fps steps so tears shimmer like stop-motion re-placement; scissor-cut pieces stay stable.
- **Replacement animation:** mouth/eye/hand states are swapped whole pieces (stop-motion logic), not tweens.
- **Camera:** mostly locked, tabletop-flat. Slow push-ins allowed; parallax between layers on pans sells the stack depth.

## Variants

- **Lightbox glow:** the same layered paper lit from BEHIND on a lightbox: layers become translucent silhouettes, deeper stacks = darker, thin single layers glow warm; light bleeds through tear fringes. Night scenes, dream scenes, shadow-theater tales.
- **Pop-up book:** scenes fold up from an open book spread; pieces rotate up around horizontal fold lines (still hinge motion, hinges just lie flat), scene changes = page turns. Great for chaptered stories and travel/history explainers.

## Engine notes

Each element = one filled path plus its paper treatment. Concretely:

1. **Edge roughness:** resample the perimeter to even arc-length, then displace each point along its normal with seeded value noise. Scissor cut: low amplitude (1-2 px at 720p), low frequency, plus rare corner over-shoots. Torn: high amplitude (4-10 px), higher frequency, and draw a second slightly-inset copy of the ragged path in near-white at low alpha FIRST, peeking past the colored path, as the fiber fringe.
2. **Per-layer drop shadow:** before drawing a piece, draw its path again in translucent dark (multiply, ~0.2-0.35 alpha, warm-neutral not black), offset by `lightDir * (base + depth * step)` and blurred more with depth (`ctx.filter = 'blur(Npx)'` or multi-pass offsets). One global `lightDir` per scene. Pieces on the same layer share one shadow pass so overlapping strips don't double-darken.
3. **Paper texture per piece:** clip to the piece's path and overlay (a) fine seeded fiber noise at 2-4% alpha, (b) a very low-frequency tone variation so the sheet isn't uniform, (c) optionally a few long faint fiber streaks along one axis. Pre-render one noise tile per paper color and reuse.
4. **Rigs:** a character is a tree of pieces with pivot points; animate ONLY pivot angles, root position, and lift height. Spring the angles toward targets (lag + follow-through, Papermotion-style: intents drive springs, not keyframes) with a fixed timestep and seeded randomness so renders are deterministic.
5. **Lightbox variant:** switch compositing to dark ground + additive/translucent pieces: each piece drawn at alpha by thickness, stack alpha accumulates to silhouette, tear fringes get a warm glow rim instead of a white fringe, drop shadows off (light comes from behind).

## Story grammar

1. Establish the table: open on the stacked world, let a piece drop or slide into place so the viewer learns "this is paper" in the first two seconds.
2. Danger = torn paper. Calm things are scissor-cut; the storm/monster/night is torn, layered, and looming.
3. The hero is the cleanest cut in the frame; keep it the brightest, simplest piece so it reads in under a second at phone size.
4. One "lift" beat per scene maximum; save the big lift (piece pulled fully off the table) for the climax.
5. Endings love the pop-up close: the scene folds flat, or a final small piece is placed by an implied hand (shadow only, never show a real hand).

**Best for:** folk tales and storybook narratives, craft/indie product films, kids' and family subjects, song visualizers with chaptered scenes, anything tactile or handmade. Prefer it over crayon when you want depth and shadow drama; prefer crayon when you want line-drawn looseness.
