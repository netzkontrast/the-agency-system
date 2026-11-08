# Libraries: what the studio ships, how to drive each one by `t`

Every film draws frame `t` as a pure function of `t`. A library is only usable if it can be **seeked**: autoplay
off, ticker off, time set explicitly, then one render. These are installed with the studio (`npm install` in
`<studio>`, done by `bin/studio doctor`), mapped in every page template through `engine/lib/importmap.json`, and
checked by `node <studio>/tools/libs-check.mjs`.

## Installed

| Library | Licence | Import | Drive it by t | Good for |
|---|---|---|---|---|
| three 0.186 + `three/addons` | MIT | `import * as THREE from 'three'` | set every transform/uniform in `update(t)`; `mixer.setTime(t)`; composer `render(0)` | any 3D, stylised via `FX` (`references/three-medium.md`) |
| postprocessing (pmndrs) | **Zlib** (keep notice) | `from 'postprocessing'` | its EffectComposer; set time uniforms from t; seed Noise/Glitch | DoF, SSAO, LUTs, ASCII, scanlines, merged effects |
| pixi.js 8 | MIT | `from 'pixi.js'` | `new Application()` + `init({ autoStart: false, preserveDrawingBuffer: true })`, `app.ticker.stop()`, set state, `app.renderer.render(app.stage)` | fast 2D sprites, filters, thousands of objects |
| animejs 4 | MIT | `from 'animejs'` | `createTimeline({ autoplay: false })`, then `tl.seek(t * 1000, true)` (true = no callbacks) | keyframed UI and type motion, staggers |
| lottie-web | MIT | classic: `<script src="node_modules/lottie-web/build/player/lottie.min.js">` → `lottie` | `loadAnimation({ autoplay: false, renderer: 'canvas' })`, `anim.goToAndStop(t * fps, true)` | After Effects / Lottie motion graphics |
| d3 7 | ISC | classic: `node_modules/d3/dist/d3.min.js` → `d3` | **never** `.transition()`; `d3.interpolate(a, b)(ease(seg(t, t0, t1)))`, redraw | charts, scales, maps (`d3.geoPath`, projections), `d3.Delaunay` (Voronoi, stained glass) |
| roughjs | MIT | `from 'roughjs'` | always pass `seed` (stable per element; change it per drawing for a boil) | sketchy hand-drawn shapes |
| perfect-freehand | MIT | `from 'perfect-freehand'` | pure function of points: animate the point list by t | pressure ink strokes, write-on lettering |
| opentype.js 2 | MIT | `from 'opentype.js'` | glyph paths; write-on via path length × progress(t) | type as shapes, morphs, outlines |
| simplex-noise 4 | MIT | `from 'simplex-noise'` | `createNoise2D(Alea(seed))` — never the default (Math.random) | flow fields, organic motion |
| alea | MIT | classic: `node_modules/alea/alea.js` → `Alea` | `Alea(seed)()` | seeded random numbers |
| culori 4 | MIT | `from 'culori'` | pure functions | OKLCH interpolation, palettes, contrast |
| p5 + p5.brush | LGPL-2.1 (unmodified) / MIT | paint medium | `noLoop`, seeded `randomSeed`/`noiseSeed`, `redraw()` at t | painted 2D (`references/paint-medium.md`) |

The studio's own: `engine/three/passes.js` (18 stylisation passes), `engine/glsl/*.glsl` (hash, noise, sdf, color,
dither), `engine/shader/runtime.js` (fullscreen shader films), `engine/lib/beat.js` (song map), `engine/lib/springs.js`
(closed-form springs), `engine/lib/life.js` (character blinks, breath).

## Add when a film needs it (`npm install <name>` in `<studio>`, then add it to `engine/lib/importmap.json`)

| Library | Licence | Drive it by t | Use |
|---|---|---|---|
| troika-three-text | MIT | `await text.sync()` in `update` | crisp SDF text in 3D |
| three-custom-shader-material | MIT | uniforms from t | extend three's PBR materials with GLSL |
| three-mesh-bvh, three-gpu-pathtracer | MIT | fixed samples per frame, `reset()` between frames | fast raycast; path-traced three scenes |
| n8ao | ISC | — | high-quality ambient occlusion |
| @dotlottie/dotlottie-web (ThorVG) | MIT | `autoplay: false`, `setFrame(f)` | faster Lottie, dotLottie files |
| harfbuzzjs | MIT | shape once, draw glyph ids | Hebrew/Arabic shaping with per-glyph control |
| @dimforge/rapier2d-deterministic / rapier3d | Apache-2.0 | fixed-step simulation from t = 0, **bake** transforms per frame to JSON, look up `cache[frame]` | physics that is identical on every machine |
| matter-js, planck, cannon-es | MIT | same: bake to a cache | simpler physics, same browser build only |
| paper, two.js, zdog, konva | MIT | set state, manual `update()/draw()` | vector booleans, pseudo-3D flat, scene graphs |
| twgl.js / regl / OGL | MIT / MIT / Unlicense | — | alternative WebGL helpers (the shader medium needs none) |
| @theatre/core | Apache-2.0 | `sheet.sequence.position = t` | keyframes authored in a UI (never ship `@theatre/studio`, AGPL) |
| meyda (Node, offline) | MIT | per-frame RMS / bands / onsets → JSON | audio-reactive layers beyond `SONG.pulse` |
| mediabunny | MPL-2.0 (unmodified) | WebCodecs decode by timestamp | video frames inside a film; faster encode |
| rembg (BiRefNet / u2net weights) | MIT code; check each model | offline, PNG + alpha sequences | cut-outs, collage, double exposure |

Video inside a film, the simple way: pre-extract frames with ffmpeg at the film's fps
(`ffmpeg -i clip.mp4 -vf fps=24 assets/clip/%05d.webp`) and draw `frames[floor(t * 24)]`.

## Never

| What | Why |
|---|---|
| GSAP | proprietary "standard no-charge" licence (changeable by its owner, not redistributable under MIT) |
| Remotion | company licence above 3 people |
| lygia | Prosperity licence (non-commercial unless sponsored) |
| Shadertoy code | default CC BY-NC-SA 3.0 — re-implement, never paste |
| The Book of Shaders code | all rights reserved |
| @theatre/studio | AGPL-3.0 |
| essentia, aubio | AGPL / GPL |
| madmom models, nice-color-palettes data, old MODNet forks | CC BY-NC-SA (non-commercial) |
| Rive state machines with live inputs, any `.transition()`, autoplay, ticker, `requestAnimationFrame` time, `Math.random` | not seekable / not deterministic |
