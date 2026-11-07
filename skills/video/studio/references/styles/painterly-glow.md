# Style: Painterly glow music video

A song told in moving oil-paint: every surface is made of swirling directional brushstrokes (like Van Gogh's skies), deep night blues and teals, and one glowing warm figure (orange, ember-lit from inside) moving through symbolic scenes. Reference: a full Suno-style song turned into a clip (Sep 2026, 6:12, 30 fps).

## Design system

- **Brushstroke texture everywhere:** backgrounds are fields of short, thick, curved strokes that follow a flow field (curl noise or a hand-designed vector field). The strokes drift slowly, so even still shots breathe. Skies swirl, water streaks horizontally, grass rises vertically.
- **Palette:** deep navy, teal, violet dusk; **one glowing warm hero color** (orange/amber) for the protagonist, fire, lanterns, light. Glow is additive with soft bloom.
- **The protagonist:** a simple, faceless or near-faceless figure made of rough painterly strokes, lit from within (embers or sparks inside the body). Other people are dark silhouettes with small glowing lights. Emotion through posture and light, not faces.
- **Symbols over literal scenes:** each lyric line becomes an image (a heart carved in a clay oven, a spiral galaxy of sparks, a boat over deep water with a figure sinking, a stage lit by footlights, a ring of flames, a moon face). Dreamlike, not literal.
- **Light as story:** sparks rising, a meteor crossing, lanterns, a single flame. Big moments are the brightest.
- **No or minimal text.** Lyrics can appear sparingly as painted words, not subtitles, if the user wants them.

## Engine

The watercolor engine (ClaudeAnimationBase, p5.brush) can do painterly strokes; or a canvas/WebGL flow-field brush renderer (thousands of short curved strokes drawn along a vector field, colored by sampling a painted base layer, re-seeded slowly so strokes shimmer). Precompute the stroke field per scene; every frame a pure function of t.

## Fits

Emotional songs, ballads, anthems, spiritual or reflective lyrics. For upbeat comedic songs prefer watercolor character or kinetic lyric.
