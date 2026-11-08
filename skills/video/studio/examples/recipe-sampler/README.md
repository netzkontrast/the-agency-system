# Recipe sampler

Proof that the style recipes in `references/style-recipes.md` render: three small projects, one frame per recipe,
contact sheets in `gallery/`. Built and checked in a container without a GPU (`STUDIO_GL=soft`, SwiftShader).

| Project | Medium | Recipes (number · `?recipe=` id) | Sheet |
|---|---|---|---|
| `three/` | three | 1 `anime-cel` · 2 `ligne-claire` · 4 `woodblock` · 6 `etching` · 11 `oil` · 13 `watercolor` · 19 `claymation` · 20 `low-poly` · 24 `synthwave` · 26 `neon` · 27 `noir` · 28 `film-stock` · 31 `1-bit` · 32 `four-colour` · 34 `halftone` · 35 `riso` · 46 `glitch` | `gallery/recipes-three.jpg` |
| `shader/` | shader | 24 `synthwave` · 41 `flow-field` · 42 `reaction-diffusion` · 43 `fluid-ink` (domain warp) · 43 `fluid-ink-fb` (feedback) · 44 `raymarch` · 45 `swarm` · 31 `1-bit` · 46 `glitch` | `gallery/recipes-shader.jpg` |
| `canvas/` | canvas | 15 `stained-glass` · 41 `flow-field` · 37 `kinetic-type` | `gallery/recipes-canvas.jpg` |

29 recipe frames in all, every one looked at and readable.

- `three/scenes/scene.js` — one still-life (torus knot, box, icosahedron on a ground plane, key + rim light, camera
  orbit from `t`) and a `RECIPES` registry. Each entry has its materials, FX chain and options as written in the
  recipe. The deviations are commented in the entry and listed below.
- `shader/scenes/film.js` — a `RECIPES` registry of pass lists; the `.frag` files in `shader/scenes/` are the sampler's
  own GLSL plus the studio includes (`engine/glsl/*.glsl`). No Shadertoy, lygia or Book of Shaders code.
- `canvas/scenes/recipes.js` — a `RECIPES` registry with `setup` (seeded data, bakes, the font) and `draw(g, t)`.
  `canvas/assets/dejavu-sans-bold-subset.ttf` is DejaVu Sans Bold cut down to the letters of RESONANCE (5.7 KB; DejaVu
  fonts licence: free to redistribute and modify, see dejavu-fonts.github.io/License.html).

## Recreate the node_modules links

The projects need the studio's `node_modules` linked into each folder. Those links are not checked in. Recreate them
(this also refreshes the copied `engine/` files):

```bash
for m in three shader canvas; do bash <studio>/tools/new-project.sh <studio>/examples/recipe-sampler/$m --update; done
```

## Render one recipe

```bash
cd <studio>/examples/recipe-sampler/three          # or shader/ or canvas/
STUDIO_GL=soft node <studio>/tools/render.mjs --stills=2 --size=480x270 --query=recipe=noir --out=review/noir
```

Without `?recipe=` each project uses its `DEFAULT_RECIPE` constant (top of `scene.js` / `film.js` / `recipes.js`).
`tools/gate.mjs` cannot pass a query, so switch that constant to gate another recipe.

## Render times (one still, 480×270, SwiftShader)

| three | ms | shader | ms | canvas | ms |
|---|---|---|---|---|---|
| ligne-claire | 300 | synthwave | 53 | kinetic-type | 350–390 |
| low-poly | 380 | glitch | 71 | stained-glass | 1200–1400 |
| most looks (ink, hatch, toon, dither, halftone…) | 430–580 | raymarch | 119 | flow-field (4000 trails) | 2200–2400 |
| synthwave (bloom + crt) | 690–760 | fluid-ink | 122 | | |
| film-stock (bloom + 5 passes) | 750 | 1-bit (raymarch + dither) | 143 | | |
| oil (kuwahara r6) | 840–970 | flow-field | 162 | | |
| neon (bloom + Reflector) | 1000–1150 | fluid-ink-fb (warmup 2 s) | 345 | | |
| | | swarm (400 particles) | 424 | | |
| | | reaction-diffusion (warmup 3 s × 8 substeps) | 4800 | | |

At 1920×1080: three `neon` 2650 ms, three `synthwave` 1460 ms.

## Gate results (`node <studio>/tools/gate.mjs film.html --samples 4`, 1920×1080, determinism + contract)

All 11 gate runs passed, 4/4 checks each. The checks: 4 frames hash-identical, cold-forward against warmed-reverse
(t 0..3.97 s); no console errors; no forbidden call in the draw path; randomness seeded. Dead air and pops were
skipped, because no mp4 was rendered.

| Project | Recipe (DEFAULT_RECIPE) | Result | Gate wall time |
|---|---|---|---|
| three | anime-cel | PASS 4/4 (stepped: 12 drawings/s) | 17 s |
| three | neon | PASS 4/4 | 35 s |
| three | riso | PASS 4/4 | 12 s |
| three | film-stock (gate weave + dust per frame index) | PASS 4/4 | 22 s |
| shader | synthwave | PASS 4/4 | 8 s |
| shader | fluid-ink-fb (feedback, warmup 2 s) | PASS 4/4 | 68 s |
| shader | swarm (two passes) | PASS 4/4 | 51 s |
| shader | raymarch | PASS 4/4 | 10 s |
| canvas | stained-glass | PASS 4/4 | 12 s |
| canvas | flow-field (bake in setup) | PASS 4/4 | 36 s |
| canvas | kinetic-type | PASS 4/4 | 4 s |

reaction-diffusion was not gated. At 1080p its 3 s × 8-substep warm-up runs to minutes per frame on SwiftShader.

Before the UMD switch (problem 14), the first canvas gate run hung in "1. DETERMINISM" waiting for READY.

## Problems found in style-recipes.md (and nearby)

`style-recipes.md` itself was not edited. Each problem is listed with what the sampler did instead.

1. **`FX.toon` blacks out mid-tones (recipes 1, 19, 21, 46).** The pass quantises *linear* luma with `floor`, so
   every pixel darker than linear `1/bands` becomes pure black. With `bands: 3` that is everything below linear .33
   (about .6 in sRGB). Recipe 1's red and teal objects rendered solid black. The sampler leaves `FX.toon` out of
   recipes 1 and 46, because MeshToonMaterial's 3-step ramp already makes the bands. Claymation (`bands: 6`) gets by
   with a bright palette. Fix in the pass: quantise `pluma` and give the darkest band a value above 0.
2. **Recipe 46 never fires without a song map.** `SONG.section(t)?.kind === 'drop'` is always false when
   `section()` returns null. The sampler treats "no map" as a drop. The recipe should say so, or gate on
   `SONG.pulse` alone.
3. **Recipe 6 has the passes in the wrong order.** It lists `hatch` then `ink`, but `ink` after `hatch` traces every
   hatch line and the frame turns almost solid ink. With `ink` first and `hatch` after it, the ink lines fall into
   the densest hatch layer and read as engraving.
4. **Recipe 11, and any `posterize`/`pixelate` levels.** They quantise in linear light, before OutputPass. Dark
   tones get very coarse steps, and gradients (a specular falloff, a dark ground) break into stripes of a different
   hue per channel: the oil frame showed pink, yellow and green bands on a brown floor. The sampler uses a mid-value
   palette and `roughness: 1`. Woodblock's `posterize 5` turns the teal box navy.
5. **Bloom (recipes 24, 26, 28) depends on frame size.** UnrealBloomPass blurs over a fixed mip chain, so at
   480×270 the glow covers a much larger part of the frame than at 1080p (compared side by side). Judge bloom at
   final size. In recipe 24, `threshold .2` makes every lit surface bloom; only the grid and sun should glow.
6. **Recipe 26's numbers wash the frame out.** Emissive `color × 4` with bloom strength 1.6 fills the frame with
   haze at both 480 and 1080. The sampler uses × 1.5 and thin tubes (knot tube .03, wireframe icosahedron). "Wet-floor
   `MeshStandardMaterial` + `Reflector`" does not say how to combine the two; the sampler puts a 55 %-opaque standard
   plane over a Reflector.
7. **Recipe 32 asks for something film.html cannot do.** "The palette map must come after OutputPass" is not
   possible: `film.html` always appends OutputPass last. What works is `NoToneMapping` plus a last custom pass that
   writes the palette colours already converted to *linear*, so the sRGB encode gives the exact hexes.
8. **Recipe 19: `shadow.radius 8` needs `renderer.shadowMap.type = PCFShadowMap`** (PCFSoft ignores the radius),
   and the recipe never says to enable `renderer.shadowMap`. The three template does not enable it either.
9. **Recipe 41's particles collapse.** Integrating particles through a plain noise-angle field (it is not
   divergence-free) gathers them into a few sink lines within about 2 s. The frame went from a full field to a few
   threads. The sampler gives each particle a 1–2.5 s life and a seeded rebirth, and colours it by age; curl noise
   would also work. The field scale `.0015` assumes 1080p pixels, so the sampler integrates in a 1920×1080 design
   space.
10. **Recipe 42: "stack 8 identical sim passes" does not work as written.** A feedback pass only reads its *own*
    previous frame. What works: give every sim pass `feedback: true` (only feedback targets are cleared before the
    warm-up; a non-feedback intermediate keeps stale state between frames and breaks determinism), and give sim1
    `inputs: ['sim8']`, which still holds the previous frame's last substep. With a 3 s warm-up, a frame at t = 2 s
    gets 384 steps: the pattern is still at the ring stage, and it costs 4.8 s per frame at 480×270. That confirms
    the recipe's own "bake it" advice.
11. **Recipe 44's fog is far too thick.** `1 - exp(-.02 d²)` fogs half the subject at d = 6, which is a normal camera
    distance. The density depends on scene units; the sampler uses .002.
12. **Recipe 24's shader grid expression is wrong.** `strokeAA(abs(fract(vec2(...)) - .5) ...)` passes a vec2 to a
    float function, and `abs(fract - .5)` is the distance from the cell centre, not from the line. Use per axis:
    `d = .5 - abs(fract(g) - .5)` with `fwidth(g)` as the pixel size. The sun bands' `step(.5, fract(uv.y*30.))`
    contradicts the shader manual's "never `step()`" rule; the sampler uses smoothstep.
13. **Recipe 37's opentype import fails.** The importmap's `opentype.mjs` has no default export, so it needs
    `import * as opentype from 'opentype.js'`. Also, `SONG.word(t)` is null without a song map, so the recipe needs
    a fallback word, as the sampler has.
14. **Gate bug: `tools/gate.mjs` serves `.mjs` as `application/octet-stream`.** The browser refuses the module, so
    any film that imports `culori` or `opentype.js` (both importmap entries point at `.mjs`) never reaches READY under
    the gate; it hangs until the 10-minute soft-GL timeout. `tools/serve.mjs`, which render.mjs uses, maps `.mjs`
    correctly. The canvas sampler therefore loads `culori.umd.js` and `opentype.js` as classic scripts.
15. **The d3 path in the templates is wrong.** The commented d3 tag in the film.html templates names
    `node_modules/d3/dist/d3.min.js`, but the installed d3 ships only `d3.js`. Recipe 15's "classic d3 script tag"
    hits this.
16. **The song map never sees the project's bpm.** `engine/lib/beat.js` reads `root.PROJECT`, but `config.js`
    declares `const PROJECT`, which is not a `window` property. Without a song map the beat is therefore always
    120 bpm whatever `--bpm` says, and three's `ctx.PROJECT` (`window.PROJECT`) is undefined.
17. **Minor:**
    - Recipe 35: the optional `halftone({cmyk:0})` before `riso` turns both plates into the same grey dots and the
      print reads pale. The sampler leaves it out.
    - Recipe 28: "halation tinted via grade" cannot tint only the bloom.
    - Recipe 27 gives no SpotLight intensity; with physical light units it needs about 200 at decay 2.
    - Recipe 1: "scale along normals 1.02–1.04" for the hull needs a vertex push (`onBeforeCompile`), and a box's
      split normals crack at its corners.

## Status after the sampler

- **1 fixed in the pass.** `FX.toon` now cuts its bands in perceptual luma (`pluma`), and each band takes its
  centre value, so the darkest band is never black. Recipe 1 here uses `FX.toon` again, as the recipe writes it.
- **2–13, 17 fixed in `references/style-recipes.md`**, with the working settings from this sampler. Recipe 24 (three) was re-rendered with the corrected numbers (bloom threshold .85, grid and sun ×1.5): only grid and sun glow, the subjects stay clean.
- **14 fixed.** `tools/gate.mjs` serves `.mjs`, `.wasm`, `.ttf` and `.otf` with the right types.
- **15 not reproduced.** The studio's pinned d3 (`node_modules/d3/dist/`) ships `d3.min.js`, and
  `engine/lib/libs-check.html` loads it. Check a project's `node_modules` link if the tag fails.
- **16 fixed.** `engine/lib/beat.js` reads the `const PROJECT` from `config.js` when there is no
  `window.PROJECT`, so `--bpm` sets the fallback beat. The three medium's `ctx.PROJECT` is set the same way.
