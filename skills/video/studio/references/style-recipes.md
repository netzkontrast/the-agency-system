# Style recipes

A catalogue for realising almost any visual style in the studio. Every recipe obeys the film contract
(`references/film-contract.md`): a frame is a pure function of `t`, randomness only from seeds, `READY` after assets.
Medium manuals: `references/paint-medium.md`, `references/three-medium.md`, `references/shader-medium.md`,
`references/pathtracer/README.md`; the canvas medium is `engine/canvas/film.html` + `engine/lib/springs.js`.

```bash
bash <studio>/tools/new-project.sh <dir> --medium paint|canvas|three|shader|pathtracer [--duration S] [--bpm N]
```

## How to pick a medium

| The look is mostly… | Medium | Why |
|---|---|---|
| flat, hand-drawn, painted, brushy characters | **paint** | p5.brush: `paint()`, `inkLine()`, watercolour `fill`, `hatch`, boil on twos, additive `glow()` |
| type, UI, HUD, diagrams, data, vector, collage, sprites, pixel grids | **canvas** | full 2D control; add roughjs, perfect-freehand, d3, pixi.js, lottie, animejs, opentype.js |
| 3D space with any stylisation (cel, ink, oil, print, CRT, low-poly, neon) | **three** | real camera and light, then `FX.*` passes from `engine/three/passes.js` |
| abstract, generative, visualizer, fluid, feedback, raymarched, kaleidoscopic | **shader** | per-pixel GLSL from `iTime`, `iPulse`; feedback with warm-up re-simulation |
| physically lit materials: felt, clay, glass, metal, paper miniatures | **pathtracer** | WebGPU path tracer, principled + craft BSDFs, denoiser |

Rules of thumb: pick the medium by what carries the *structure* of the picture, not its surface. A painterly 3D
camera move is three + `kuwahara`, not paint. A hand-drawn chart is canvas + roughjs, not paint. If the camera never
leaves a plane, you do not need three.

### Combining media

- **Live layer inside a canvas film.** The canvas page has the same importmap. Build a `THREE.WebGLRenderer` on an
  offscreen `<canvas>` (`preserveDrawingBuffer: true`), call your three `update(t)` + `composer.render(0)` inside
  `renderFrame(t)`, then `g.drawImage(glCanvas, 0, 0)` and composite type/HUD on top. Same for a shader layer: copy
  `engine/shader/runtime.js` into `engine/`, `createFilm(offCanvas, film, { W, H, SONG })`, `renderFrame(t)`, drawImage.
  Call `setFxTime(composer, t, W, H)` yourself — only `engine/three/film.html` does it for you.
- **Transparent overlay.** Draw only the HUD/type on a cleared canvas and export with alpha (see `styles/editorial-hud.md`),
  then composite in ffmpeg over footage or another studio render.
- **Pre-rendered pass as texture.** Render a heavy layer once: `node <studio>/tools/render.mjs --frames --png
  --film=layer.html --fps=24` → `out/frames/`. Load frame `Math.round(t*24)` as an `Image` (canvas) or
  `THREE.TextureLoader` (three) — preload the set in setup, never fetch inside `renderFrame` without awaiting it.
  Use it for path-traced plates under canvas type, long feedback sims, or a paint layer mapped onto a 3D card.
- **Paint → three.** Render paint frames to PNG, map them on planes for a paper-theatre diorama with a real camera.
- **Shader → paint.** A shader flow field rendered to PNG becomes the vector field a paint scene samples (read pixels once
  in setup into a Float32Array).
- Keep one master clock: every layer reads the same `t` and the same `SONG`.

## The 21 house styles

| Style file | Medium | Key passes / libs / technique |
|---|---|---|
| [animated-short](styles/animated-short.md) | canvas parallax or three | soft stylised 3D, letterbox, story-first; use the local three medium, not a CDN build |
| [ascii-terminal](styles/ascii-terminal.md) | canvas | scene → 160×90 luminance → 160×45 glyph grid, `lighter` bloom stack, scanlines, per-row barrel |
| [chrome-showreel](styles/chrome-showreel.md) | canvas (or three) | per-facet chrome ramps, per-pixel liquid metal; three `MeshPhysicalMaterial` + gradient PMREM env; beat-locked cuts |
| [crayon-storybook](styles/crayon-storybook.md) | canvas (or paint) | strokes as data, seeded scribble fill, wax grain alpha, boil 8–12 fps |
| [dark-premium](styles/dark-premium.md) | canvas | near-black radial, one gold accent, `lighter` glows, seeded grain, vignette |
| [editorial-hud](styles/editorial-hud.md) | canvas overlay + model footage | transparent HUD layer, mono labels, tracking brackets, ticker, 24 fps |
| [explainer](styles/explainer.md) | canvas | springs, giant type, one accent, UI cards, dithered mascot |
| [image-game](styles/image-game.md) | canvas + image-model stills | still → playable; sprites cut from served images |
| [ink-wash](styles/ink-wash.md) | canvas (or paint) | hair-brush strokes, bleed blobs, draw-on op list, cached composite, seal |
| [kinetic-lyric](styles/kinetic-lyric.md) | canvas | `SONG.word(t)` timing, one metaphor per line, 60 fps |
| [manifesto](styles/manifesto.md) | canvas | Sobel/threshold/ordered-dither image treatments at load, one line per frame |
| [monochrome-launch](styles/monochrome-launch.md) | canvas | #000/#FFF only, sine-displacement chrome, ordered dither, section inversion |
| [painterly-glow](styles/painterly-glow.md) | paint or canvas | flow-field brushstrokes, navy/teal + one warm glowing hero, additive bloom |
| [paper-cutout](styles/paper-cutout.md) | canvas | torn/scissor edges by normal displacement, per-layer offset shadows, fibre tiles, 8 fps boil |
| [pencil-test](styles/pencil-test.md) | canvas | marks as data, three pencils per layer + multiply, pose table on twos, onion skins |
| [pixel-art](styles/pixel-art.md) | canvas | 320×180 logical canvas, `imageSmoothingEnabled=false`, Bayer B4/B8, palette tables |
| [riso-pop](styles/riso-pop.md) | canvas (three: `FX.riso`) | three grey plates + press pass, screens fixed to paper, misregistration on twos |
| [sketchbook](styles/sketchbook.md) | canvas | self-drawing marks, hatching density = tone, paper multiply, one pale wash |
| [teaching-song](styles/teaching-song.md) | three + canvas overlay | subject-world 3D, karaoke labels; use the local three medium |
| [title-sequence](styles/title-sequence.md) | canvas | beat-locked type reel, HUD frame, BPM bar counter |
| [watercolor](styles/watercolor.md) | paint | p5.brush wash + fill, ink outline, boil, `glow()` |

## Recipes

Notation. Three FX chains are written in order, options as passed: `FX.ink({threshold:.12})` etc.; `film.html`
appends `OutputPass` last. Passes run **before** OutputPass, i.e. in linear light before ACES tone mapping and sRGB
encoding: colours given as pass options (`paper.tint`, `riso.inkA`, `ink.color`) come out lighter and slightly
desaturated. Lower them ~20 % or set `renderer.toneMapping = THREE.NoToneMapping` in `setup` for print looks where
exact ink colours matter. Keep a handle on any pass you animate (`const gl = FX.glitch(); … gl.uniforms.u_amount.value = …`).

### Cel, line and drawn 3D

**1. Anime cel / toon with outlines** — three
- Recipe: `MeshToonMaterial` + 3-step `gradientMap` (`[60,160,255]`, NearestFilter); inverted-hull outline (clone mesh,
  `MeshBasicMaterial({color:'#1a1416', side: BackSide})`, scale along normals 1.02–1.04) for hero silhouettes;
  passes `FX.ink({threshold:.1, width:1, keep:1})`, `FX.toon({bands:3, softness:.03})`, `FX.grade({sat:1.15})`, `FX.grain({amount:.02})`.
- Motion: characters on twos (`step: 12`, quantise pose time `tq = Math.floor(t*12)/12`), camera smooth on ones.
- Palette: bright saturated mids, shadow colour = hue-shifted toward blue/violet, not darker grey.
- Pitfalls: Sobel ink also traces texture noise — keep albedo flat; quantising the camera too makes it stutter.

**2. Ligne claire (clear line, flat colour, no hatching)** — three or canvas
- Three: `MeshBasicMaterial` flat colours (no shading) + `FX.ink({threshold:.05, width:1.2, color:[.05,.05,.06], keep:1})`, `FX.paper({strength:.08})`.
  Shadows only as flat darker colour patches (separate meshes), never gradients.
- Canvas: closed paths, `lineWidth` constant 2.5 px at 1080p, `lineJoin='round'`, fills from a 6–8 colour table.
- Motion: slow, wide camera; smooth springs (`camera` preset); figures on twos.
- Palette: pale sky, ochre, desert pinks, teal; ink near-black blue.
- Pitfalls: variable line weight kills the look; avoid gradients and grain above 0.02.

**3. Painterly anime background** — three or paint
- Three: geometry for layout only, textured with soft gradients; `FX.kuwahara({radius:5})`, `FX.watercolor({edge:.35, granulation:.2, bleed:1})`,
  `FX.grade({lift:[.02,.03,.05], gain:[1.05,1.02,.95], sat:1.1})`, `FX.paper({strength:.1})`, `FX.vignette({strength:.25})`.
- Paint: `paint(pts,{fill:col, fillOp:120, bleed:.12, tex:.5, ink:null})` layers back to front; clouds as 3–5 overlapping fills.
- Motion: parallax pans (layers at 0.2/0.5/1.0 speed), leaves and grass sway via `Math.sin(t*1.3+hash(i)*6)`; no boil on backgrounds.
- Palette: cumulus whites, saturated summer greens, cobalt sky; warm late-light gain.
- Pitfalls: `kuwahara` radius > 6 is slow and smears edges; keep foreground characters out of it (render them in a second composer or in paint over the plate).

**4. Woodblock print (ukiyo-e-like)** — three or canvas
- Three: flat `MeshBasicMaterial` areas + `FX.ink({threshold:.08, width:1.5, color:[.1,.08,.1], keep:1})`, `FX.posterize({levels:5})`,
  `FX.paper({strength:.25, tint:[.93,.88,.76]})`, `FX.grain({amount:.03, size:2})`.
- Canvas: keyblock outline layer + 4–6 colour blocks each offset 1–2 px (misregistration), bokashi gradients as linear gradients inside clip paths,
  wood grain = seeded stripes `snoise(x*0.002, y*0.05)` at 6 % alpha multiply.
- Motion: held tableaux, slow 2D pans, water and snow animated on threes (8 fps).
- Palette: Prussian blue, vermilion, pale indigo, ochre, soft pink on warm paper.
- Pitfalls: real perspective fights the look — use orthographic cameras or flattened stages.

**5. Linocut** — three or shader
- Three: `FX.ink({threshold:.12, width:2, keep:0})` → `FX.dither({levels:2, scale:3, mono:1})` → `FX.paper({strength:.2})`.
- Shader: threshold `luma` against carved gouge marks: `step(.5, luma + .25*sin(dot(p,dir)*0.35 + snoise(p*.01)*4.))` along contour-following `dir`.
- Motion: on threes (8 fps, `step: 8`); jitter the gouge pattern per drawing only.
- Palette: one ink (black or deep red) on cream, optional second block colour.
- Pitfalls: mid-greys must die — threshold hard, no anti-aliased grey ramps.

**6. Etching / engraving** — three
- Recipe: `FX.hatch({spacing:4, angle:.4, layers:4, color:[.12,.1,.08]})`, `FX.ink({threshold:.1, width:1, keep:1})`, `FX.paper({strength:.22, tint:[.95,.92,.84]})`, `FX.vignette({strength:.3})`.
  For curved engraving lines, use a `ShaderMaterial` that hatches along UV v (`fract(vUv.y*120.)`) with thickness by shade.
- Motion: slow camera, no boil (engraving is precise), 24 fps smooth.
- Palette: sepia ink on cream; one red for a seal.
- Pitfalls: hatch spacing < 3 px aliases at 1080p and shimmers when downscaled for phones.

**7. Pencil sketch** — paint or three
- Paint: `inkLine(pts, .6, '#3a3632', 'HB')`, tone with `paint(region,{hatch:{d:5, a:.8, o:{rand:.1}, b:'2B', c:'#4a4440', w:.5}, ink:null})`.
- Three: `FX.ink({threshold:.1, keep:0, color:[.25,.24,.23]})`, `FX.hatch({spacing:5, angle:.8, layers:3, color:[.3,.28,.26]})`, `FX.boil({fps:12, amount:1})`, `FX.paper({strength:.15})`.
- Motion: boil on twos, `FILM_STEP 12`; construction lines first on reveals.
- Palette: graphite greys on off-white; optional single coloured-pencil accent.
- Pitfalls: hatch replaces colour entirely — composite colour accents in a second pass or canvas overlay.

**8. Charcoal** — paint
- Recipe: `inkLine(pts, 2.5, '#1d1b1a', 'charcoal')`; masses `paint(pts,{hatch:{d:3, a:1.1, b:'charcoal', c:'#222', w:1.2}, ink:null})`;
  smudges as `fill` grey `#5b5652` `fillOp 60 bleed .25 tex .9`; erase highlights with `wash: PAL.paper`.
- Motion: on twos, boil amount high; reveals drawn in gestures.
- Palette: carbon black, warm grey, toned paper `#e9e2d4`.
- Pitfalls: thousands of strokes exceed 1.5 s/frame — cache static backgrounds by drawing them once per drawing time.

**9. Chalkboard** — canvas
- Recipe: board `#1f2a24` + seeded smudge layer (`snoise` blobs at 4 % white); chalk strokes as perfect-freehand outlines
  (`getStroke(pts,{size:7, thinning:.1, smoothing:.6})`) filled `#ece9df`, then `destination-out` speckle mask from a seeded noise tile at 25 %.
- Motion: strokes draw on in hand order (cut stroke at `k = clamp((t-t0)/dur)`), springs for diagrams.
- Palette: chalk white, pale yellow, pink, light blue.
- Pitfalls: speckle must be fixed to the board, not re-rolled per frame.

**10. Blueprint** — canvas or three
- Canvas: `#103a6b` ground, grid every 24 px at 12 % white + every 120 px at 25 %; lines 1.5 px `#d8ecff`; dimension arrows; roughjs off (precise).
- Three: `EdgesGeometry` → `LineSegments` `#d8ecff` over a dark-blue scene + `FX.grain({amount:.02})`, `FX.vignette({strength:.2})`.
- Motion: draw-on via `setDrawRange(0, Math.floor(k*count))`; smooth camera.
- Palette: cyanotype blue, white; one orange callout.
- Pitfalls: line width in WebGL is always 1 px — use `Line2`/`LineMaterial` from addons for thicker lines.

### Paint and fine-art surfaces

**11. Oil painting** — three (or shader/canvas)
- Recipe: `FX.kuwahara({radius:6})`, `FX.posterize({levels:12})`, `FX.paper({strength:.12, scale:2, tint:[.95,.9,.82]})` (canvas weave), `FX.grade({sat:1.15})`, `FX.vignette({strength:.3})`.
- Motion: smooth camera; strokes shimmer if radius changes — keep it constant per shot.
- Palette: earth pigments, deep shadows, impasto highlights.
- Pitfalls: Kuwahara ignores stroke direction; for visible directional strokes use canvas flow-field strokes (see recipe 39).

**12. Gouache** — three or paint
- Three: `FX.kuwahara({radius:3})`, `FX.posterize({levels:7})`, `FX.ink({threshold:.2, width:1, color:[.2,.15,.15], keep:1})`, `FX.paper({strength:.2})`.
- Paint: `wash` fills at 255 opacity (opaque), `ink: null` or `sw:.5`, a few `fill` shadows at `fillOp 80`.
- Motion: on twos.
- Palette: chalky, slightly desaturated mids, matte (no specular).
- Pitfalls: specular highlights read as digital — `roughness: 1` on all materials.

**13. Watercolor wash** — paint or three
- Paint: see `styles/watercolor.md`; washes `fill`, `bleed:.2, tex:.7`.
- Three: `FX.watercolor({edge:.7, granulation:.45, bleed:2})`, `FX.ink({threshold:.15, keep:1, color:[.25,.2,.2]})`, `FX.paper({strength:.22})`.
- Motion: boil 12 fps on line, washes steady.
- Palette: transparent pigments, white = paper.
- Pitfalls: dark values die in watercolour — build darks by layering, not black.

**14. Pointillism** — shader or canvas
- Shader: jittered grid `cell = floor(p/8.)`, centre `cell*8.+hash22(cell)*8.`, sample the source (iChannel0) at the centre, draw `fillAA(sdCircle(...,3.2), px)` with the colour pushed to its nearest of 8 pure hues.
- Canvas: draw source to offscreen, then 60k dots via `hash(i)` positions, colour sampled from `getImageData` buffer.
- Motion: dots fixed to the canvas (like the screen of riso), source moves under them; or dots re-seeded per drawing on threes.
- Palette: complementary dot pairs (orange/blue, violet/yellow).
- Pitfalls: dots that move with objects look like particles, not paint.

**15. Stained glass** — canvas (d3)
- Recipe: `const vor = d3.Delaunay.from(pts).voronoi([0,0,W,H])`; per cell `g.beginPath(); vor.renderCell(i, g); g.fillStyle = col(i); g.fill()`;
  leading `g.lineWidth=6; g.strokeStyle='#1b1714'; vor.render(g); g.stroke()`; light pass: radial gradient `lighter` at 30 %.
  Seed points from a seeded rng; animate light, not cells.
- Motion: slow light sweep (sun through glass), `glow` blooms on beats.
- Palette: cobalt, ruby, amber, emerald; leading near-black.
- Pitfalls: moving points re-triangulate and cells pop — keep `pts` static or move them a few px with `snoise`.

**16. Mosaic** — shader
- Recipe: Voronoi tiles via `hash22` per cell (3×3 neighbour search), tile colour = source sampled at the tile seed, grout = `smoothstep(.02,.0, d2-d1)` where d1/d2 are nearest/second-nearest distances.
- Motion: stable tiles; reveal tiles by `hash12(cell) < k`.
- Palette: stone tones, smalti golds.
- Pitfalls: anti-alias grout with `fwidth`, or it crawls.

**17. Embroidery / cross-stitch** — canvas or shader
- Canvas: logical grid 120×68, each cell two crossed stroked diagonals (lineWidth 0.35×cell, `lineCap='round'`), thread colour from a 12-colour table,
  per-stitch highlight line at 30 % white; fabric ground = woven tile (alternating 1 px offsets).
- Motion: stitches appear in row order; whole image holds — motion via stitch count, not movement.
- Palette: DMC-like thread table on unbleached linen.
- Pitfalls: never scale the grid mid-shot; quantise everything to stitches.

**18. Paper cut-out layers** — canvas (see `styles/paper-cutout.md`), or three
- Three variant: planes `MeshLambertMaterial({map: paperTex, side: DoubleSide})`, real shadows (shadowMap 2048, `PCFSoftShadowMap`), key light 30°, layers 2–5 cm apart; passes `FX.paper({strength:.12})`, `FX.grain({amount:.02})`.
- Motion: on threes or twos, hinge rotations only.
- Pitfalls: cut edges with alpha maps need `alphaTest: .5` to cast correct shadows.

### Craft and miniature 3D

**19. Claymation look** — three
- Recipe: `MeshStandardMaterial({roughness:.9, metalness:0})` + `onBeforeCompile` fbm bump (thumbprint), soft key (DirectionalLight + `shadow.radius 8`),
  big hemisphere fill; passes `FX.toon({bands:6, softness:.2})`, `FX.grain({amount:.03})`, `FX.vignette({strength:.25})`.
- Motion: everything on twos, `step: 12`; add per-drawing micro-jitter of 0.002 units to positions (`hash(Math.floor(t*12))`) = replacement boil.
- Palette: plasticine primaries, slightly desaturated, warm key.
- Pitfalls: smooth 24 fps motion instantly reads as CG.

**20. Low-poly flat shading** — three
- Recipe: `IcosahedronGeometry(r, 1)` etc., `MeshLambertMaterial({flatShading:true})`, one strong key + soft hemi; `FX.grade({sat:1.1})`, `FX.vignette({strength:.2})`; `renderer` antialias on.
- Motion: smooth springs on camera; vertex wobble via seeded noise on twos for wind.
- Palette: 5-colour gradient ramp per object (culori `interpolate([...],'oklch')`).
- Pitfalls: indexed geometry with shared normals won't look faceted — `toNonIndexed()` or flatShading.

**21. Isometric diorama** — three
- Recipe: `OrthographicCamera`, rotation `(-Math.atan(1/Math.SQRT2), Math.PI/4, 0)` order 'YXZ', base slab with soil sides; `FX.toon({bands:4})`, `FX.ink({threshold:.12, keep:1})`, `FX.paper({strength:.06})`.
- Motion: tilt-shift: addons `BokehPass` ({focus, aperture:.002, maxblur:.01}) or two-band blur; time-lapse lights via `t`.
- Pitfalls: ortho frustum must be recomputed from `W/H` for vertical recompose.

**22. Product turntable** — three
- Recipe: studio env from `RoomEnvironment` + `PMREMGenerator`, `MeshPhysicalMaterial` (clearcoat 1, roughness .2), key softbox (RectAreaLight 6, `RectAreaLightUniformsLib.init()`), rim, shadow-catcher plane `ShadowMaterial({opacity:.25})`;
  passes `FX.grade({gain:[1.02,1,0.98]})`, `FX.vignette({strength:.15})`, `FX.grain({amount:.015})`.
- Motion: `rotation.y = Spring.to(t, keys, 'heavy')` or `t*2π/8`; one specular sweep per hero beat.
- Pitfalls: GLTF models load in `setup` (await); `mixer.setTime(t)` for rigged parts.

**23. Physically-lit felt / clay / glass miniature** — pathtracer
- Recipe: felt `{baseColor, roughness:1, sheenColor:[.9,.85,.8], sheenRoughness:.4}`; clay `{subsurface:.6, clay:{strength:.5, cell:.004, period:.0006}, edgeSheen:.2}`;
  paper `{diffuseTransmission:.5}`; glass `{transmission:1, ior:1.5, roughness:0}`; wax/gummy `{mfp:.02, translucencyColor:[1,.6,.4]}`.
  Brighten `baseColor` ~10–20 % for sheen/subsurface energy loss. Shallow depth of field from the camera; 64–256 spp + denoiser for previews.
- Motion: miniature physics — on twos for stop-motion feel; `sceneFor(i)` pure in frame index.
- Pitfalls: start from `examples/felt-good-morning/`; caustic paths through thin glass need `shadowTransparency:true`.

### Retro, neon and screen looks

**24. Synthwave / outrun grid** — shader or three
- Shader: horizon split `uv.y < .45`; ground grid `strokeAA(abs(fract(vec2(x/z, 1./z + iTime*.8)) - .5) ...)` with perspective `z = (.45-uv.y)`; sun = disc with horizontal cut bands `step(.5, fract(uv.y*30.))` below its centre; sky `palette()` magenta→purple.
- Three: `GridHelper` scrolled by `position.z = (t*speed) % cell`, sun sphere emissive, `UnrealBloomPass(new THREE.Vector2(W,H), 1.2, .4, .2)`, `FX.crt({curve:.03, scan:.2, mask:.1})`.
- Motion: constant forward drive on the bar, cuts on `floor(iBar)`.
- Palette: `#ff2a6d`, `#d1f7ff`, `#05d9e8`, `#1a0b2e`.
- Pitfalls: modulo the grid scroll by exactly one cell or it jumps.

**25. Vaporwave** — canvas + three
- Recipe: pastel gradient sky, checkerboard floor (three `Plane` + checker texture), marble bust stand-in (generic sculpted primitive), Windows-ish UI frames in canvas,
  `FX.chroma({amount:2})`, `FX.posterize({levels:16})`, `FX.grain({amount:.03})`.
- Motion: slow, floaty, looping rotations; slowed tempo.
- Palette: `#ff71ce`, `#01cdfe`, `#05ffa1`, `#b967ff`, `#fffb96`.
- Pitfalls: no logos, no real brand UI.

**26. Neon glow / cyberpunk night** — three
- Recipe: dark scene, emissive tubes (`MeshBasicMaterial` colours > 1 via `color.multiplyScalar(4)`), wet-floor `MeshStandardMaterial({roughness:.15, metalness:.6})` + `Reflector` from addons;
  passes `new UnrealBloomPass(new THREE.Vector2(W,H), 1.6, .5, .85)`, `FX.chroma({amount:1.8})`, `FX.grade({lift:[.02,0,.05], gain:[1,.95,1.1], sat:1.2})`, `FX.grain({amount:.04})`, `FX.vignette({strength:.4})`.
- Motion: neon flicker from `hash11(floor(t*24)+id) > .97`, rain streaks analytic; camera dolly smooth.
- Palette: cyan + magenta + one sodium amber; black base.
- Pitfalls: bloom threshold too low smears everything; flicker must respect the flash gate (≤ 3/s full-frame).

**27. Film noir** — three
- Recipe: one hard SpotLight (`penumbra .1`, shadows 4096) through venetian-blind geometry, fog `FogExp2('#000', .08)`;
  `FX.grade({lift:[0,0,0], gamma:[.85,.85,.85], gain:[1.15,1.15,1.15], sat:0})`, `FX.grain({amount:.08, size:1.5})`, `FX.vignette({strength:.5, softness:.4})`.
- Motion: slow push-ins, long holds (`HOLDS`), smoke via billboarded noise sprites.
- Palette: monochrome, crushed blacks; optional single red.
- Pitfalls: `sat:0` kills that red — composite it after the grade with a mask, or set `sat:.08` and grade red objects hot.

**28. 70s/80s film stock** — three or canvas
- Recipe: `FX.grade({lift:[.04,.03,.01], gamma:[1.05,1,.92], gain:[1.05,.98,.88], sat:.85})`, `FX.chroma({amount:1.2})`, `FX.grain({amount:.07, size:2})`, `FX.vignette({strength:.35})`.
  Gate weave: offset the camera's view by `setViewOffset(W,H, 1.5*snoise(floor(t*24)*.3), 1*snoise(...+9), W, H)` per frame; dust/scratch flecks from `hash(frame)` drawn in canvas or a custom pass.
- Motion: 24 fps, handheld via low-freq `snoise(t*.5)` rotation 0.3°.
- Palette: warm highlights, teal-green shadows, halation (a weak red bloom: UnrealBloomPass strength .3 tinted via grade).
- Pitfalls: weave must be a function of the frame index, not accumulated.

**29. VHS / analog video** — shader (post) or three
- Recipe (custom pass or shader, from `tex`): luma/chroma split — blur chroma horizontally 6 px, shift +2 px; per-line jitter `x += (hash(vec2(row, floor(iTime*30.)))-.5)*.002`; tracking band `smoothstep` at `y = fract(iTime*.13)`; head-switch noise bottom 2 %; `FX.crt({curve:.0, scan:.25, mask:0})`, `FX.grain({amount:.06})`.
- Motion: 30/60i feel; drop-outs on beats.
- Palette: bleeding reds, lifted blacks `lift ~.06`, timestamp OSD in mono.
- Pitfalls: real interlace combing breaks the gate's still checks — declare `HOLDS` honestly.

**30. CRT terminal** — canvas (see `styles/ascii-terminal.md`) or three
- Three variant: render a canvas text texture on a plane, `FX.crt({curve:.1, scan:.4, mask:.25})`, `UnrealBloomPass(v, .8, .3, .2)`, `FX.vignette({strength:.45})`.
- Motion: typing at 30–60 cps from `t`, cursor blink `floor(t*2)%2`.
- Palette: P1 green `#33ff66` or amber `#ffb000` on `#050805`.

**31. 1-bit / dithered monochrome** — three, shader or canvas
- Three: `FX.grade({gain:[1.1,1.1,1.1]})`, `FX.dither({levels:2, scale:2, mono:1})` (nothing after it but OutputPass).
- Shader: `#include "engine/glsl/dither.glsl"`, `col = ditherLevels(vec3(luma(c)), floor(fragCoord/2.), 2.)`.
- Motion: on twos; dither pattern fixed to the screen.
- Palette: `#000`/`#fff` or paper `#f2efe6`/ink `#1a1a1a` (map after thresholding).
- Pitfalls: tone mapping after the pass is harmless for 0/1, but `FX.grain` after dither reintroduces greys.

**32. Four-colour handheld palette** — three or canvas
- Recipe: `FX.pixelate({size:6, levels:4})`, then a custom palette-map pass: `idx = floor(luma*3.999)` → `[#0f380f,#306230,#8bac0f,#9bbc0f][idx]`; or canvas 160×144 logical canvas with Bayer B4 between the 4 tones.
- Motion: 12 fps sprite animation, integer-pixel camera.
- Pitfalls: the palette map must come after OutputPass colour encoding — add it as the last custom pass with `NoToneMapping`.

**33. Pixel art** — canvas (see `styles/pixel-art.md`); three variant `RenderPixelatedPass(6, scene, camera)` + `FX.posterize({levels:6})` for 3D pixel dioramas.

### Print and graphic design

**34. Halftone comic (wordless panels)** — three or canvas
- Three: `FX.ink({threshold:.1, width:1.5, keep:1})`, `FX.posterize({levels:4})`, `FX.halftone({cell:7, angle:.26, cmyk:1})`, `FX.paper({strength:.15, tint:[.97,.94,.86]})`.
- Canvas: panel grid with 12 px gutters, each panel a clipped sub-render (`g.save(); g.clip(panelPath); drawShot(t, i); g.restore()`), panels reveal on bars; motion lines and impact bursts as SFX shapes, no lettering.
- Motion: on twos, impact frames held 2–4 drawings.
- Pitfalls: speech balloons are excluded by design; text-free storytelling needs bigger acting.

**35. Risograph zine** — three or canvas (see `styles/riso-pop.md`)
- Three: `FX.riso({inkA:[.97,.33,.48], inkB:[.12,.38,.78], offset:[3,-2]})`, `FX.halftone({cell:5, cmyk:0})` optional before it, `FX.grain({amount:.03})`.
  Animate `offset` per drawing: `riso.uniforms.u_offset.value = [2+hash(k), -1-hash(k+1)]`, `k=floor(t*8)`.
- Palette: fluorescent pink + blue, or yellow + teal, on cream.
- Pitfalls: inks from options are tone-mapped — use `NoToneMapping` (see notation).

**36. Swiss poster typography** — canvas
- Recipe: 12-column grid (margins 6 % W), one grotesk family, sizes from a modular scale 1.333; `opentype.js` paths for exact kerning; flush-left ragged-right; two colours + black.
- Motion: springs `snappy`/`heavy`, elements slide along grid lines only, cuts on bars.
- Pitfalls: centring and decorative type break the system; keep text ≥ 4 % of H for phones.

**37. Kinetic typography** — canvas
- Recipe: `SONG.word(t)` drives entry; per-glyph paths from opentype (`font.getPath(ch, x, y, size)` → `new Path2D(p.toPathData())`), animate scale/position/rotation per glyph with `Spring.unit(t - word.t, 'snappy')`; stressed words (`word.stress`) 1.5× size.
- Motion: 60 fps, smooth; holds on line ends.
- Pitfalls: wait for `document.fonts.ready` and font ArrayBuffers before `READY`; never `fillText` in fonts not loaded.

**38. Data viz / infographic** — canvas (d3)
- Recipe: scales `d3.scaleLinear().domain([0,max]).range([H-120, 120])`, shapes via `d3.line().context(g)`/`d3.arc().context(g)`; animate by interpolating data with `k = Spring.unit(t-t0,'camera')`:
  `const v = d3.interpolateArray(a, b)(k)`; axes drawn by hand with `scale.ticks(5)`.
- Motion: one change per beat or per narrated sentence; the number counts up with `d3.format(',.0f')(lerp)`.
- Palette: greys + one accent for the point.
- Pitfalls: never `.transition()`; label ≥ 28 px at 1080p.

**39. Map journeys** — canvas (d3-geo)
- Recipe: GeoJSON in `assets/` (convert once; topojson-client is not installed); `const proj = d3.geoOrthographic().scale(H*.45).translate([W/2,H/2]).rotate([-lon,-lat])`, `const path = d3.geoPath(proj, g)`;
  route `d3.geoInterpolate(A, B)(k)` with `k = Spring.unit(t-t0,'camera')`; projection morph: `d3.geoProjection((l,p)=>{const a=d3.geoEquirectangularRaw(l,p), b=d3.geoOrthographicRaw(l,p); return [a[0]+(b[0]-a[0])*m, a[1]+(b[1]-a[1])*m];})` with `m` from t (rebuild per frame).
- Motion: rotate the globe to the next point, then draw the arc; `clipAngle(90)` for orthographic.
- Pitfalls: `geoPath` with context draws but does not fill/stroke — call `g.beginPath(); path(feature); g.fill()`.

**40. Lottie motion graphics** — canvas (lottie)
- Recipe: `const anim = lottie.loadAnimation({ renderer:'canvas', loop:false, autoplay:false, animationData, rendererSettings:{ context:g, clearCanvas:false } })`;
  `renderFrame`: clear, `anim.goToAndStop((t - t0) * anim.frameRate, true)`. `READY` after the `DOMLoaded` event.
- Motion: whatever the file holds; retime with a mapping `t → frame`.
- Pitfalls: expressions using `time` or `random()` in the JSON can be non-deterministic; image assets must be embedded or served locally.

### Generative and procedural

**41. Generative flow fields** — canvas (simplex-noise) or shader
- Recipe: `const n3 = createNoise3D(Alea('flow'))`; N = 4000 particles; position is **integrated analytically per frame from t = 0 at fixed dt** or, cheaper, baked: precompute paths once in setup (`steps = duration*24`) into Float32Arrays and draw trail segments `[f-12, f]`.
  Angle `a = n3(x*.0015, y*.0015, t*.05) * Math.PI*2`.
- Motion: slow; field evolves at 0.05/s.
- Palette: culori ramp along particle age (`interpolate(['#0b132b','#5bc0be','#f5f5f5'],'oklch')`).
- Pitfalls: integrating inside `renderFrame` from the previous frame breaks determinism — bake in setup.

**42. Reaction-diffusion** — shader (feedback)
- Recipe: sim pass `feedback: true`, Gray–Scott on RG: `A += (Da*lapA - A*B*B + f*(1-A))*dt`, `B += (Db*lapB + A*B*B - (k+f)*B)*dt` with `Da 1.0, Db .5, f .055, k .062, dt 1`; run 8 substeps by stacking 8 identical sim passes or bake;
  seed B from `hash12` blobs at `iFrame == 0`-equivalent (when the read is zero). Show pass maps B through `palette()`.
- Warm-up: patterns need hundreds of steps — bake (render sim sequentially to PNGs, see `references/shader-medium.md`) rather than warmup > 3 s.
- Pitfalls: half-float targets are fine; `CLAMP_TO_EDGE` wrap means edges behave as boundaries — design for it.

**43. Fluid ink in water** — shader
- Cheap: no sim — `warp2(warp2(p*1.5, t*.1), t*.07)` domain warp twice, ink density `smoothstep(.45,.6, fbm2(q*3.))`, multiply over paper.
- Feedback: advect `prev = texture(iChannel0, uv - vel*dt)` with `vel` from curl of `snoise`, decay `*.985`, inject ink on beats (`iPulse`); `warmup: 2`.
- Pitfalls: decay ≥ .995 means long memory → warmup too short shows the "clean start"; then bake.

**44. Raymarched SDF worlds** — shader
- Recipe: 3D SDFs written inline (sdf.glsl is 2D); 96 steps, `eps .001`, normals by central differences, soft shadows (IQ technique), `smin(a, b, .3)` from `sdf.glsl` to blend; fog `mix(col, fogCol, 1.-exp(-.02*d*d))`; camera from `iTime` via look-at matrix.
- Motion: camera paths as closed-form curves; morphs by `smin` k on `iPulse`.
- Palette: `palette(t, vec3(.5), vec3(.5), vec3(1.), vec3(0.,.33,.67))` + toSRGB once.
- Pitfalls: 1080p at 96 steps is heavy in SwiftShader — preview at `?w=960&h=540`.

**45. Particle swarms (analytic)** — shader or three
- Recipe: each particle `i` is `pos(i, t)` closed-form: `base = hash22(vec2(i))`, `p = base + .2*vec2(snoise(base*3.+t*.2), snoise(base*3.+9.-t*.2))`; three: `Points` with a `ShaderMaterial` whose vertex shader computes position from `aSeed` and `uTime`; set `uTime = t` in `update`.
- Motion: flocking feel by shared low-frequency noise; bursts on `SONG.pulse`.
- Pitfalls: never integrate velocities on the CPU per frame.

**46. Glitch art on beats** — three or shader
- Three: `const gl = FX.glitch({amount:0, seed:3})` in the chain after the look passes, `FX.chroma({amount:1})` after it;
  `update`: `gl.uniforms.u_amount.value = SONG.section(t)?.kind === 'drop' ? SONG.pulse(t, 12) * .8 : 0`.
- Shader: row displacement `if (hash12(vec2(row, floor(iBeat))) < iPulse*.4) uv.x += ...`.
- Motion: glitches only on chosen beats; clean frames otherwise.
- Pitfalls: `FX.glitch` re-rolls at 12 Hz internally, independent of beats — the beat gating is your `amount`. Respect the flash gate.

**47. Double exposure** — canvas
- Recipe: silhouette (portrait image or three render) as mask; landscape drawn inside via `g.globalCompositeOperation = 'screen'` over a light ground, or `destination-in` mask then `multiply` the face on top at 60 %.
- Motion: landscape drifts slowly inside the static silhouette; crossfade via springs.
- Pitfalls: needs high-contrast silhouette; real photos must be licensed (`references/real-shots.md`).

**48. Photo collage** — canvas
- Recipe: cut-outs from mattes (`tools/matte.swift` on macOS, or pre-cut PNGs), rough paper borders (recipe 18 edges), tape pieces, offset shadows; halftone the photos at load (Sobel/dither in `manifesto.md`).
- Motion: on threes, pieces slap in with `playful` springs and a 1–2° rotation settle.
- Pitfalls: photos carry rights and faces — use `FACES` for the text audit.

### Agency System worked example: emotional-technological resonance

Charcoal, graphite and ink on paper, one yellow light, and an analogue glitch grammar (manual RGB split, block erasure,
jitter, erosion) that marks system strain. Music/design layer: refer to voices by **function/role only**; no
personal names in frames, file names, captions or prompts (`skills/theagencysystem/`, name_exposure).

**Paint version (default).**
```js
// scenes/ch01.js — inside the chapter's draw(t)
paint(rectPts(-50,-50,W+100,H+100), { wash: '#e8e2d5', ink: null });                       // toned paper
glow(cx, cy, 260 + 40 * SONG.pulse(t, 4), '#ffd23f', 0.55);                                // the one yellow light, under the drawing
paint(figurePts, { hatch: { d: 3.5, a: 1.1, o: { rand: .15 }, b: 'charcoal', c: '#1f1d1c', w: 1.1 }, ink: '#141312', sw: 1.4, br: 'charcoal' });
inkLine(gesturePts, 0.7, '#2b2826', 'HB');                                                  // graphite construction
inkLine(contourPts, 1.6, '#0f0e0e', 'ink');                                                 // ink commitment
```
Glitch grammar as 2D-context operations on `FILM_CANVAS` after the painting is finished for the frame (use a
2D overlay canvas if the p5 canvas is WebGL), keyed to the drawing `k = Math.floor(t*12)` and gated by `SONG.pulse(t, 8)`:
- **Manual RGB split:** copy the frame to an offscreen canvas; redraw it twice with `globalCompositeOperation='lighter'`
  through red-only and blue-only `multiply` fills, offset ±(2–6 px)·pulse horizontally. Only on strain beats.
- **Block erasure:** `n = floor(6*pulse)` rectangles at `hash(k*7+i)` positions, 40–200 px wide, 6–24 px tall, filled with the paper colour (not black): the system *deletes*, it does not corrupt.
- **Jitter:** shift 1–3 horizontal bands by `(hash(k+i)-.5)*12` px using `drawImage` slices.
- **Erosion:** `destination-out` a seeded noise mask whose threshold rises across the section (`k_er = (t - sec.t)/(sec.end - sec.t)`): the drawing wears away into paper, then is redrawn.
- Motion: on twos, `FILM_STEP 12`; glitches on twos too (never per output frame).
- Palette: carbon `#141312`, graphite `#4a4644`, paper `#e8e2d5`, light `#ffd23f`. Yellow appears only as light, never as a fill.

**Three version (3D space, same look).**
```js
const glitch = FX.glitch({ amount: 0, seed: 11 }), chroma = FX.chroma({ amount: 0 });
passes: [ new UnrealBloomPass(new THREE.Vector2(W, H), 0.9, 0.5, 0.88),   // only the emissive yellow crosses .88
  FX.ink({ threshold: .1, width: 1.4, color: [.06, .055, .05], keep: 1 }),
  FX.hatch({ spacing: 5, angle: .9, layers: 3, color: [.1, .095, .09] }),  // replaces colour: see pitfall
  FX.boil({ fps: 12, amount: 1.4 }), FX.paper({ strength: .24, tint: [.95, .92, .84] }),
  glitch, chroma, FX.grain({ amount: .05, size: 1.5 }) ],
// update(t): const s = SONG.pulse(t, 8) * strain(t); glitch.uniforms.u_amount.value = .7 * s; chroma.uniforms.u_amount.value = 6 * s;
```
- Materials grey `MeshStandardMaterial({roughness:1})`; the yellow light is an emissive mesh + PointLight `#ffd23f`.
- Pitfall: `FX.hatch` outputs only paper + ink, so the yellow vanishes. Either drop `hatch` and keep `ink` + `boil`, or
  render the light separately (second RenderPass of a light-only layer, blended `screen` in a 6-line custom ShaderPass after `paper`).
- Block erasure in three: a 5-line custom `ShaderPass` — `if (h21(floor(vUv*vec2(24.,48.)) + k) < amount*.3) gl_FragColor = vec4(paperTint,1.)`.

## Determinism rules per library

| Library | Drive it by `t` like this | Never |
|---|---|---|
| springs.js | `Spring.to(t, keys, preset)`, `Spring.unit(t - t0, preset)` — closed form | step a spring per frame |
| beat.js | `SONG.pulse(t, k)`, `beatAt`, `barAt`, `word(t)`, `section(t)` | cache "last beat" in a variable |
| animejs v4 | `import { createTimeline } from 'animejs'; const tl = createTimeline({ autoplay: false }); tl.add(obj, { x: 400, duration: 800, ease: 'outExpo' }, 0);` then in `renderFrame`: `tl.seek(t * 1000, true)` and draw from `obj` | `autoplay`, `engine` ticking, callbacks with side effects |
| lottie-web | `loadAnimation({ autoplay: false, loop: false, renderer: 'canvas', … })`, `anim.goToAndStop(t * anim.frameRate, true)`; READY after `DOMLoaded` | `play()`, `setSpeed` |
| pixi.js v8 | `const app = new Application(); await app.init({ width: W, height: H, autoStart: false, preserveDrawingBuffer: true, antialias: true })`; set every property from `t`; `app.renderer.render(app.stage)`; `FILM_CANVAS = app.canvas`; `app.ticker.stop()` | `ticker.add` motion, `deltaTime` |
| roughjs | `rough.canvas(c)`; every shape gets `{ seed: id }` (stable per object; `seed: id*1000 + Math.floor(t*12)` to boil on twos) | omit `seed` (random every call) |
| perfect-freehand | `getStroke(points, { size, thinning, smoothing, streamline, simulatePressure: false, last: true })` with stored pressure; cut `points` by progress for draw-on | sample pointer input at render time |
| simplex-noise v4 | `createNoise2D(Alea('seed'))` (Alea is a classic global; load `node_modules/alea/alea.js`) | `createNoise2D()` with no PRNG (uses `Math.random`) |
| culori | pure functions: `interpolate(colors, 'oklch')(k)`, `formatHex` | — |
| opentype.js | `opentype.parse(await (await fetch(url)).arrayBuffer())` in setup; `getPath(...).toPathData()` per frame | load fonts after READY |
| d3 (classic global) | scales, shapes, `d3.interpolate*` evaluated at `k(t)`; `d3.Delaunay`; `geoPath(proj, ctx)` | `.transition()`, `d3.timer`, force simulations live (bake them, below) |
| three | set every transform/uniform in `update(t)`; `mixer.setTime(t)`; `composer.render(0)`; `setFxTime` | `Clock`, `getDelta`, `mixer.update(dt)`, `AfterimagePass` or any pass keeping the previous frame |
| troika-three-text | not installed: `npm i troika-three-text` in the studio and add importmap entries for it and its deps (`troika-three-utils`, `troika-worker-utils`, `webgl-sdf-generator`, `bidi-js`); set `.text` in `update`, then `await new Promise(r => text.sync(r))` before rendering | render before `sync` resolves |
| postprocessing (pmndrs) | its own `EffectComposer`; set time uniforms from `t`; `composer.render(0)` | rely on its internal clock (`deltaTime`) for noise/glitch effects |
| shader runtime | uniforms from `t`; hashes from `floor(iTime*24.)` | running counters; long warmups instead of baking |
| physics (any engine) | fixed-step sim run once offline (Node script or setup at `dt = 1/240`), baked to `assets/sim.json` (`frames[f] = [x,y,a,…]`); `renderFrame` lerps between `floor(t*fps)` and `+1` | step physics inside `renderFrame` |
| p5 / p5.brush | `random()`/`jit()` reseeded by the engine per drawing; `boilSeed(key)` per element; `hash(i)` for stable values | `Math.random`, `millis()` |
| pathtracer | `sceneFor(i)` pure in frame index; fixed spp and seed per frame | progressive accumulation across frames |

Shader feedback: the runtime re-simulates `warmup` seconds at `dt = 1/fps` before every frame; anything with memory
longer than ~3 s is baked to PNG frames once and read as images (preload the sequence; the runtime's `inputs` are
loaded once at start, so a per-frame image sequence needs a small extension or a canvas/three host).

## Licences

May be copied into the repo (keep the notice in the file header and `THIRD_PARTY.md`):

| Source | Licence |
|---|---|
| Ashima / Stegu webgl-noise (simplex, `snoise`) | MIT |
| Inigo Quilez article snippets (smin, palettes, SDF primitives, soft shadows) | MIT (articles only, not his Shadertoy art) |
| hg_sdf (Mercury) | its MIT option of the dual licence |
| `glsl-*` stack.gl packages (glsl-noise, glsl-fxaa, glsl-film-grain …) | MIT / BSD — check each package |
| Christoph Peters blue-noise textures | CC0 |
| three, postprocessing, d3, roughjs, perfect-freehand, simplex-noise, alea, culori, opentype.js, animejs, pixi.js, lottie-web | MIT / Zlib / ISC / BSD / Apache (installed deps; do not vendor-edit) |

Must not be copied (re-implement the technique from papers instead):

| Source | Why |
|---|---|
| lygia | Prosperity licence (non-commercial) unless a commercial licence is bought |
| Shadertoy shaders | default CC BY-NC-SA 3.0 unless the author states otherwise |
| The Book of Shaders code | all rights reserved |
| GSAP | proprietary standard licence (free to use, not open source); not a studio dependency |
| Remotion | company licence required for teams; not a studio dependency |
| nice-color-palettes data | CC BY-NC-SA |
| Essentia (audio analysis) | AGPL |
| @theatre/studio | AGPL (the `@theatre/core` runtime is Apache-2.0; the studio editor is not) |

Palettes: derive your own with culori or from artwork you own; style names in deliverables describe techniques, never
studios, franchises or living artists.
