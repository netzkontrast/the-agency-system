# The film contract

Every film in the studio — whatever its medium — is a web page that obeys this contract. Every tool
(`tools/render.mjs`, `gate.mjs`, `text-audit.mjs`, `plate-audit.mjs`, `edge-audit.mjs`, `audit-faces.mjs`,
`frames.mjs`, `export.mjs`, the review pack) drives the page only through it.

## Required

| Global | Meaning |
|---|---|
| `window.FILM_DURATION` | length in seconds |
| `window.renderFrame(t)` | draws the exact frame for time `t` (seconds). May be `async`. **A pure function of `t`:** no state carried from one frame to the next, randomness only from a seeded source (`hash(i)`, `rng(seed)`, p5's seeded `random()`), never `Math.random()`, `Date.now()`, `performance.now()` or `localStorage` in the draw path. Frames are rendered in any order, in parallel, by several pages at once. |
| `window.READY = true` | set only after fonts (`document.fonts.ready`), images and pre-baked data are loaded |

## Optional

| Global | Meaning | Used by |
|---|---|---|
| `window.FILM_CANVAS` | the canvas to capture (default: the largest canvas on the page) | every capture tool |
| `window.FILM_STEP` | drawings per second for stepped art (12 = on twos). Holds are then the look, not dead air | `gate.mjs` |
| `window.FILM_TO_SCREEN(x, y)` | world point → screen pixel through this frame's camera | `render.mjs --crop-at` |
| `window.HOLDS = [[a, b], …]` | deliberate still stretches (seconds) | `gate.mjs` dead air |
| `window.CUTS = [t, …]` | deliberate hard cuts (seconds) | `gate.mjs` pops |
| `window.FOOTAGE = [[a, b, fps], …]` | lower-frame-rate footage inside the film | `gate.mjs` pops |
| `window.FACES = (t) => [[x, y, w, h], …]` | face boxes that nothing may cover | `text-audit.mjs`, `audit-faces.mjs` |
| `window.TEXT_AUDIT_SKIP` | set `true` while drawing a film-inside-the-film | `text-audit.mjs` |

## Size and format

The renderer opens the page as `film.html?render=1&w=<width>&h=<height>` (plus `&portrait=1` when taller than wide,
and any `--query=` extras). The page draws at that size. A vertical version is a **recompose** (its own layout per
shot, `references/vertical.md`), not a crop: read `w`/`h` and place things for that frame.

## Preview

Outside the renderer (`navigator.webdriver` false) the page may run its own `requestAnimationFrame` preview loop and
show scrub controls outside the canvas. Clock reads that only time the tool itself carry the comment
`// studio:host-timing`, which the gate's contract scan accepts.

## Media

| Medium | Template | Notes |
|---|---|---|
| paint | `engine/paint/film.html` + `engine/paint/*.js` | p5.js + p5.brush; sets `FILM_CANVAS`, `FILM_STEP = 12`, `FILM_TO_SCREEN`. Rules: `references/paint-medium.md` |
| canvas | `engine/canvas/film.html` | plain 2D canvas + `engine/lib/springs.js`; type, HUD, explainers, data |
| pathtracer | `engine/pathtracer/` (Node driver, not a page) | its own renderer (`references/pathtracer/`), same principle: `sceneFor(i)` is a pure function of the frame index |

All page media load `engine/lib/beat.js` after `songmap.js`, so `SONG.beatAt(t)`, `SONG.word(t)`, `SONG.section(t)`
time the picture to the measured song (`references/songmap.md`).
