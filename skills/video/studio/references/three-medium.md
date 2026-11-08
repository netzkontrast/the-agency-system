# The three medium (three.js)

3D in any look: toon and cel, ink-and-paper, painterly, engraved, printed, pixel, CRT, filmic. The geometry is
three.js; the look comes from the light, the materials and a chain of the studio's own stylisation passes
(`engine/three/passes.js`). Start a project with:

```bash
bash <studio>/tools/new-project.sh <dir> --medium three --duration 20
```

It writes `film.html` (importmap for three, addons and the studio libraries), `engine/passes.js`, and
`scenes/scene.js` (a toon scene with key + rim light, ink + boil + paper + grain passes).

## The contract

`scenes/scene.js` exports `async setup(ctx)` and returns `{ scene, camera, passes, update, step? }`.

| ctx | |
|---|---|
| `THREE` | the module |
| `renderer` | WebGLRenderer, pixel ratio 1, sRGB output, ACES tone mapping, `preserveDrawingBuffer: true` |
| `W`, `H` | the frame size the renderer asked for (`?w=&h=`); compose for it (vertical is a recompose) |
| `FX` | the pass catalogue (below) |
| `SONG` | the song map (`SONG.pulse(t)`, `SONG.word(t)`, `SONG.line(i).key.stress` …) |
| `rng(seed)` | seeded random numbers for building the scene |

- `update(t, ctx)` sets **every** animated value from `t`: positions, rotations, camera, light, material uniforms,
  morph weights. Never accumulate (`x += v * dt`), never read a clock.
- glTF animation: `mixer.setTime(t)` (not `mixer.update(dt)`); load models in `setup` and `await` them.
- The composer renders with delta 0; `setFxTime()` feeds `t` to the studio passes. `Math.random` is replaced by a
  stream seeded per frame, so addons that use it (GlitchPass, noise) stay deterministic.
- Text: `troika-three-text` (install it into the studio when needed) — `await text.sync()` inside `update` before the
  frame is captured. Or draw text in a canvas texture.
- Return `holds: [[a, b]]` for deliberate still stretches (an end card, blank paper) and `cuts: [t]` for hard cuts,
  so the gate's dead-air and pop checks know they are intended.
- Return `step: 12` when the look is stepped (the `boil` pass, animation on twos); the gate then judges stillness per
  drawing, and `render.mjs --twos` halves the render.

## The pass catalogue (`FX.*`, our own GLSL, MIT)

Order: structure → medium → surface → (OutputPass is added last by `film.html`).

| Structure | Medium | Surface |
|---|---|---|
| `ink` Sobel edge lines (`keep: 0` = lines only) | `halftone` CMYK or mono dot screen | `paper` procedural fibre |
| `toon` light bands | `riso` two-ink misregistration | `grain` per-frame film grain |
| `kuwahara` oil / gouache | `dither` Bayer 8×8, any levels | `vignette` |
| `watercolor` edge darkening, granulation, bleed | `pixelate` + palette snap | `chroma` radial aberration |
| `hatch` cross-hatching by luminance | `posterize` | `grade` lift/gamma/gain/saturation |
| `boil` hand-drawn line wobble at `fps` | `crt` curvature, scanlines, mask | `glitch` beat-driven blocks |
|  |  | `fade` to a colour (last in the chain) |

`gallery/fx-catalogue.jpg` shows every pass alone on the same scene (default options; chroma, grain, boil and glitch
turned up so they read at thumbnail size).

Each takes an options object (see the header of `engine/three/passes.js` for every option and default):

```js
passes: [FX.kuwahara({ radius: 5 }), FX.watercolor({ edge: .7 }), FX.paper({ strength: .22 }), FX.grain({ amount: .04 })]
```

Animate options per frame in `update`: `myGlitch.uniforms.u_amount.value = SONG.pulse(t, 10) * .6`.

three's own addons work in the same chain: `UnrealBloomPass` (neon, glow), `BokehPass` (depth of field),
`SAOPass`/`GTAOPass` (contact shadows), `OutlinePass` (selected-object outlines), `SMAAPass`, `RenderPixelatedPass`,
`HalftonePass`, `AfterimagePass` — **avoid** `AfterimagePass` and anything else that keeps a previous frame (it breaks
"any frame alone"). The pmndrs `postprocessing` library (Zlib licence; import `postprocessing`) merges effects into one
pass and adds depth of field, SSAO, LUTs, ASCII, scanlines; use its `EffectComposer` instead of three's in a scene that
needs it, and set any time uniform from `t`.

## Materials that read as drawn

- **Toon:** `MeshToonMaterial` with a 3–5 step `gradientMap` (NearestFilter), plus `FX.ink`. Outline by inverted hull
  (a back-face copy scaled along normals, flat ink colour) when the Sobel lines are too thin.
- **Flat / low-poly:** `MeshLambertMaterial({ flatShading: true })`, one strong key light.
- **Clay:** `MeshStandardMaterial({ roughness: .9 })`, soft area-like key, `FX.toon({ bands: 6, softness: .2 })`, on twos.
- **Paper diorama:** planes with `MeshLambertMaterial` + paper texture, `side: DoubleSide`, back light for translucency.
- **Custom shading:** `ShaderMaterial` or `onBeforeCompile`; GLSL helpers from `engine/glsl/` can be pasted in
  (noise, sdf, color, dither).

## Toon materials and light pulses

`MeshToonMaterial` quantises light into bands. A small change of light intensity flips whole bands at once, which
the gate measures (and a viewer sees) as a pop. Pulse scale or position on the beat (`SONG.pulseSoft`), not the
lights; if light must move, move it slowly (≥ 0.5 s) or animate a non-toon layer.

## Light has shape

Key + rim on every hero, real shadows (`renderer.shadowMap.enabled = true`, `light.castShadow = true`, shadow map 2048),
contact under objects (SAO/GTAO or a soft blob). Exposure per shot, not one flat grade over the film.

## Cost and checks

On a GPU a 1080p frame with 4–6 passes renders in tens of milliseconds; in a container without a GPU (SwiftShader)
expect 0.2–2 s. `kuwahara` with radius > 6 and `watercolor` are the heavy passes. Run `bin/studio gate <dir>`:
determinism is checked on real renders, and the contract scan follows the module imports into `scenes/` and `engine/`.
