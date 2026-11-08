# The shader medium (fullscreen fragment shaders)

Abstract, generative, procedural and audio-reactive pictures: fluid ink, reaction-diffusion, raymarched SDF worlds,
domain-warped smoke, kaleidoscopes, noise landscapes, beat-driven visualizers, Canvas loops. Every pixel is computed
by GLSL from `iTime = t`. The runtime is the studio's own (`engine/shader/runtime.js`, WebGL2, no dependencies).

```bash
bash <studio>/tools/new-project.sh <dir> --medium shader --duration 30
```

It writes `film.html`, `engine/runtime.js`, `engine/glsl/*.glsl`, and `scenes/film.js` with two passes (a feedback
trail pass and a shown pass on paper).

## A film is a list of passes

```js
// scenes/film.js
export default {
  fps: 24, warmup: 1.5,             // warmup: seconds re-simulated before each frame when any pass feeds back
  step: 0,                          // set 12 for stepped looks (the gate then judges stillness per drawing)
  passes: [
    { name: 'sim',  frag: 'scenes/sim.frag', feedback: true },                    // iChannel0 = its own previous frame
    { name: 'main', frag: 'scenes/main.frag', inputs: ['sim', 'assets/paper.png'] }, // iChannel0 = sim, iChannel1 = image
  ],
};
```

Each pass is Shadertoy-shaped: `void mainImage(out vec4 fragColor, in vec2 fragCoord)`. Uniforms provided:

| Uniform | Meaning |
|---|---|
| `iTime` | film time `t` in seconds |
| `iResolution` | `vec3(W, H, 1)` |
| `iFrame`, `iFps` | frame index and rate |
| `iBeat`, `iBar`, `iPulse` | from the song map: `SONG.beatAt(t)`, `SONG.barAt(t)`, `SONG.pulse(t)` (0 without one) |
| `iChannel0..3` | the inputs: earlier passes of this frame, images in `assets/`, and for a feedback pass its own previous frame first |

Intermediate passes render to half-float targets; the last pass is shown.

## Includes (the studio GLSL library)

```glsl
#include "engine/glsl/hash.glsl"     // hash11/12/22/13 (PCG, integer-exact)
#include "engine/glsl/noise.glsl"    // snoise (Ashima, MIT), vnoise, fbm2, warp2
#include "engine/glsl/sdf.glsl"      // sdCircle, sdBox, sdRoundBox, sdSegment, sdRing, smin, rot2, fillAA, strokeAA
#include "engine/glsl/color.glsl"    // palette (cosine), hsv2rgb, sRGB, luma, blend modes, hex()
#include "engine/glsl/dither.glsl"   // bayer2/4/8, ditherLevels
```

Each file is included once, however often it is named.

## Determinism

- No clocks, no `Math.random` — everything from `iTime`, `iFrame`, coordinates and hashes.
- **Feedback** (trails, fluid, reaction-diffusion, cellular automata) depends on history. The runtime clears the
  feedback targets and re-simulates `warmup` seconds at a fixed `dt = 1/fps` before every frame, so each frame
  depends on `t` only, and parallel workers agree. Cost: `warmup × fps` extra passes per frame — keep it short (a
  trail that fades to 1/e in 0.5 s needs ~1.5 s). A simulation that must remember the whole film (a painting that
  builds up for 3 minutes) is baked instead: render the sim pass sequentially once to PNG frames, then read them as
  an image **sequence** input, e.g. `inputs: ['assets/bake/%05d.png']` — the runtime loads frame `round(t × fps)` for
  every rendered frame. Footage works the same way (`ffmpeg -i clip.mp4 -vf fps=24 -start_number 0 assets/clip/%05d.png`).
- Grain and boil: hash with `floor(iTime * 24.0)` (or `* 12.0` on twos), never a running counter.

## Craft notes

- Anti-alias SDF edges with `fillAA(d, px)` where `px = 1.0 / iResolution.y` in your units; never `step()`.
- Work in linear light and convert once at the end (`toSRGB`), or stay in sRGB consistently.
- Motion on the music: scale and colour with `iPulse`, cut patterns on `floor(iBar)`, big changes on downbeats.
- Flashes: a full-frame brightness change on every beat fails the flash gate above 3 per second. Pulse a part of the
  frame, or soften the envelope (`iPulse` with a slower decay).

## Licences for shader code

Copy only code whose licence allows it, and keep its notice: Ashima/Stegu webgl-noise (MIT), Inigo Quilez article
snippets (MIT per his site; his Shadertoy art is not), hg_sdf (under its MIT option), `glsl-*` packages (MIT/BSD),
CC0 blue-noise textures. **Never paste** Shadertoy code (default CC BY-NC-SA 3.0), lygia (Prosperity licence), The Book
of Shaders (all rights reserved). Re-implement techniques from papers and articles instead.
