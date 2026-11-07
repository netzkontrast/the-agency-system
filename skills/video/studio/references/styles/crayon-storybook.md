# Style: Crayon storybook

A child's-picture-book history told in crayon and ballpoint on cream paper. Reference: "The history of dinosaurs in under one minute" (Sep 2026): "Claude Sonnet 5.5 drew every frame of this animation in JavaScript", 47 s, 2160x2160 square.

## Why this style exists in our gallery

Our watercolor-realism attempt failed because pushing a code character toward anatomy exposes every joint in motion. This style is the opposite bet, and it wins: **imperfection is the aesthetic**. A wobbly contour can't be off-model, a scribble fill can't tear at a joint, a hop with squash reads as charm, not error. When the subject is characters who must move a lot, this is now the default recommendation over realism.

## Design system

- **Ground:** warm cream paper (#ECE8DC family), bare. No texture overlay needed; the marks carry the texture.
- **Line:** ONE thin blue ballpoint contour (#2B3A7E-ish), loose and wobbly, occasional double-stroke, gaps where the hand lifted. Line boil: re-jitter the wobble on 2s or 3s (not every frame), like a child's flipbook.
- **Fill:** crayon scribble masses laid AFTER the line and disobeying it: overshoot, undershoot, visible directional strokes, unfilled patches. Big areas = side-of-crayon broad strokes. The sun is a concentric orange scribble spiral. Catastrophe = black crayon scrubbed over the whole sky, ragged bottom edge.
- **Palette:** a small crayon box: teal green, orange, marigold yellow, warm red, earth brown, black. Each character owns 1-2 crayons.
- **Caption strip:** a handwritten-script caption bottom-center of EVERY frame. In the reference it is the timeline ("230 million years ago" → "0 million years ago") and it is the story's spine. The final caption is the payoff line ("still here.").
- **Characters:** tiny bodies, one big eye with a highlight, emotion through posture and eye size only. Babies = bigger head, bigger eye. No fingers, no anatomy. Squash-and-stretch hops, tail drags, pop-up hatches.
- **Format:** square 1:1 (feed-native), ~45-60 s, must read fully muted (the captions carry it).

## Story grammar (from the reference)

1. One protagonist lineage carried across eras/chapters; the caption device marks time jumps.
2. Scale beats: the tiny hero next to something enormous (baby under the sauropod's leg).
3. The catastrophe is a texture change, not a new style: the same crayons, scrubbed dark.
4. Quiet aftermath beats (empty paper, one fern) before the recovery.
5. **Callback ending**: the film ends where it began, transformed (egg → egg in a nest), plus a two-word closer.

## Engine notes

- Strokes as data: each mark = centreline + width + crayon color + jitter seed; refill scribbles by seeded hatching inside (or past) a blob path.
- Crayon texture: stroke alpha modulated by a seeded grain tile so pressure varies along the stroke; ends fade like wax lifting.
- Ballpoint: near-constant thin width, slight darkening where strokes cross.
- Boil on 2s/3s: re-seed jitter at 8-12 fps steps while animating position at full fps.
- Captions: a handwriting font is acceptable; a drawn-on path per caption is better (draw-on in reading order).

**Best for:** history/evolution explainers, "X in under a minute", kids' subjects, science stories, anything where characters move a lot and warmth beats polish. Strong default for family films.
