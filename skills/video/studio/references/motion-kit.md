# Motion kit: moves that read as designed

Small, proven mechanics from the launch-video studies (Raphael Aubry's pipeline, uxmiles, apoorveth; Sep 2026). All are pure functions of t, so they keep the render contract. Pair with the spring presets in `timing.md`.

## Zooms in log space

Scale is multiplicative: a linear tween from 1x to 8x spends almost all its time in the last doubling and feels like it lurches. Interpolate the log and exponentiate:
```js
const zoom = (t, z0, z1, p) => Math.exp(Math.log(z0) + (Math.log(z1) - Math.log(z0)) * Spring.unit(t, p));
```
Each doubling then takes the same time. **No back-to-back in/out:** a zoom in straight into a zoom out reads as a camera wobble; put a hold, a cut or a lateral move between them, or keep zooming the same way (the one-continuous-zoom format).

## Beat punches

A punch is a tiny scale kick on the beat that decays, so the frame breathes with the music without anyone noticing a zoom:
```js
// beats: times in seconds (from the song map); after the drop, bars punch harder
const punch = (t) => beats.reduce((s, b, i) => t < b ? s : s + (b >= DROP && i % 4 === 0 ? 0.03 : 0.012) * Math.exp(-(t - b) / 0.12), 0);
g.scale(1 + punch(t), 1 + punch(t));   // around the frame centre
```
+0.012 per beat, +0.03 per bar after the drop, exponential decay (~0.12 s). Bigger reads as a shake. Nothing punches in the quiet sections.

## Shared elements across handoffs

At a scene change, one element carries across: the button that was clicked becomes the next scene's card, the counter's number flies into the headline, the dot becomes the logo's i. It is interpolated (spring, log-space size) from its rect in scene A to its rect in scene B while everything else crossfades or wipes around it. The eye follows the thing it was already looking at, so the cut never makes the viewer search. Rule: every handoff names its carrier, or it is a declared hard cut (the gate's pop check lists the rest).

## Flood circle transitions

A colour flood grows from the click point (or the carried element) to fill the frame:
- The radius must reach the **farthest corner**: `R = Math.hypot(max(x, W - x), max(y, H - y)) * 1.05`. Sized to the width only, a corner stays uncovered for a frame and flickers.
- **0.3-0.35 s**, eased out (`snappy` spring or a cubic ease-out). Faster reads as a flash (and trips the gate's pop check); slower drags.
- Render the next scene inside the circle as a clip, not after it, so the flood reveals rather than covers.

## A fast rewind or scrub through the film

When the film replays itself fast (a rewind inside a player, a scrub along a timeline), each frame jumps a second or more of film, so a dark shot, a light shot and a dark shot land on three frames in a row: a strobe. A fresh reviewer counted four flashes in a second on ours, brightness inside the player going from 4 % to 60 % and back.

- Draw each frame of the rewind as the **average of about ten moments** of the film, spread over the stretch that **five frames** cover, not only its own. Neighbouring frames then share four fifths of what they show and brightness can only drift. Averaging over the frame's own stretch alone does nothing for the flash: each frame still sits inside one shot.
- To average, point the drawing context at a spare canvas, draw the scene at one moment, and add it to an accumulation canvas with alpha `1/(k+1)` for the k-th moment. This needs the page's context variable to be `let`, and scenes that do not reset the transform themselves.
- Measure it: mean brightness inside the player for every frame of the rewind; no change of more than about 0.1 from one frame to the next, and no two opposite changes above 0.1 in a row. Ours went from 0.57 to 0.11.
- Ease in and out, so the first and last moments are sharp and readable; let the thing that explains the rewind (a line of text, a label) stand still for a second before it starts.

## Seek-compatible libraries only

Any animation library in film.html must be driven by t, not by its own clock (toolbox.md): Anime.js with `autoplay: false` then `anim.seek(t * 1000)`, Theatre.js with `sequence.position = t` for hand-tuned camera paths. Never a library that only plays in real time.
