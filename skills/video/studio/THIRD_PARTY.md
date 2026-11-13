# Third-party code and credits

The Video Studio is built from three open-source repositories, merged into one layout and then changed. This file is
the one place that records where its parts came from, under which licence, and what it needs at render time. Licence
texts are in `LICENSES/`.

## The three upstream repositories

| Upstream | Commit | Licence (text in `LICENSES/`) | What it gave the studio |
|---|---|---|---|
| [netzkontrast/take-one](https://github.com/netzkontrast/take-one) (Tal Siach) | `830621cce11127a30120d7878570eb8acaaa5bad` | MIT: `take-one-LICENSE-MIT.txt` | the process and most of the craft: references, styles, tools, the style gallery, the review room, the examples index |
| [netzkontrast/ClaudeAnimationBase](https://github.com/netzkontrast/ClaudeAnimationBase) (John Heibel; fork of github.com/JohnHeibel/ClaudeAnimationBase) | `0ac8bf2b31942376cb6b8c4074715595d512acd2` | MIT: `ClaudeAnimationBase-LICENSE-MIT.txt` (identical upstream copy: `ClaudeAnimationBase-LICENSE-MIT-upstream.txt`) | the paint medium (p5.js + p5.brush) and its guide |
| [netzkontrast/higgsfield-video-engineer](https://github.com/netzkontrast/higgsfield-video-engineer) (Higgsfield AI) | `082bfd7b7b0b863799fa9afcdfeb3e84ba72e015` | MIT: `higgsfield-video-engineer-LICENSE-MIT.txt` | the WebGPU path tracer, its route and the path-traced example film |

The name and the logo of the take-one upstream are not used: they were not licensed with its code. The studio's own
name is Video Studio and its logo is `gallery/logo/video-studio-logo.svg` / `video-studio-mark.svg`.

## Which studio folders came from which upstream

| Studio path | From | Upstream path | Changes |
|---|---|---|---|
| `references/` (all but the rows below) | take-one | `references/` | paths moved to the new layout; vendor-promotional wording removed; parts of the upstream `SKILL.md` folded into `references/pitch.md`, `brand.md`, `character-life.md`, `quality-checklist.md`, `reviewer-brief.md`, `captions.md` |
| `references/styles/` | take-one | `references/styles/` | the watercolor style now uses the in-studio paint medium instead of a clone |
| `tools/` (audits, `gate.mjs`, `frames.mjs`, `export.mjs`, `render-parallel.sh`, `new-canvas-project.sh`, `music/`, `music.mjs`, `sfx.mjs`, `review-room/`, `review-pack.sh`, `storyboard-sheet.sh`, Python helpers) | take-one | `scripts/` | browser launch moved to `tools/lib/browser.mjs`; the gate takes `--step` / `window.FILM_STEP` |
| `engine/lib/springs.js`, `engine/lib/life.js` | take-one | `scripts/springs.js`, `scripts/life.js` | moved |
| `gallery/` (`gallery.html`, `previews/`, `previews-src/`) | take-one | `assets/gallery.html`, `assets/previews/`, `assets/previews-src/` | the upstream logo replaced by the studio's own (`gallery/logo/`) |
| `examples/INDEX.md` | take-one | `examples/INDEX.md` | a section for films made in the studio added |
| `engine/paint/` (`core.js`, `timeline.js`, `sheets.js`, `clawd.js`, `config.js`, `film.html`, `emotions.jpg`, `views.jpg`, `render.legacy.mjs`) | ClaudeAnimationBase | `src/*.js`, `studio.html`, `docs/*.jpg`, `render.mjs` | `studio.html` became `film.html` (film contract); the Clawd character is optional; the beat can follow a song map |
| `references/paint-medium.md` | ClaudeAnimationBase | `ANIMATION_GUIDE.md` | paths and commands for the studio |
| `examples/paint-demo/demo.js` | ClaudeAnimationBase | `src/scenes/demo.js` | comment path only |
| `engine/pathtracer/` (`src/`, `web/`, `bin/`, `tests/`, `proofs/`, `proofs-images/`, `examples/`, `README.md`, `NOTICE.md`, `setup.sh`, `requirements.*`, `package*.json`, `tools/encode.sh`, `tools/rp`, `tools/rp_pool.mjs`, `tools/rp_pod/`) | higgsfield-video-engineer | `skills/code-based-films/engine/`, `…/setup.sh`, `…/requirements.*`, `…/tools/encode.sh`, `…/tools/rp*` | moved under one folder |
| `references/pathtracer/` | higgsfield-video-engineer | `skills/code-based-films/SKILL.md` (now `README.md`) and `…/references/` | front matter removed, retitled "Path-traced route", paths for the studio |
| `examples/felt-good-morning/` | higgsfield-video-engineer | `examples/felt-good-morning/` | engine imports point at `engine/pathtracer/` |
| `tools/audio/beatmap.py` | higgsfield-video-engineer | `skills/code-based-films/tools/beatmap.py` | moved |

Written for the studio itself (no upstream): `SKILL.md`, `agents/`, `playbooks/`, `bin/`, `references/film-contract.md`,
`references/pitch.md`, `tools/render.mjs`, `tools/new-project.sh`, `tools/lib/browser.mjs`, the other files in
`tools/audio/`, `engine/canvas/film.html`, `engine/lib/beat.js`, `examples/paint-demo/README.md`.

## Code adapted from other open work (inside the take-one upstream)

| What | Files here | Upstream | Licence |
|---|---|---|---|
| anidoodle (Alex Greenshpun): code music engine, sound-effect kit, render gate, audio meter, style analyzer, the adapt-a-style method, the ink-wash brush and seal | `tools/music/*.mjs` and the kit set-up of the pieces in `tools/music/pieces/`, `tools/music.mjs`, `tools/sfx.mjs`, `tools/gate.mjs`, `tools/audio-check.mjs`, `tools/analyze-style.mjs`, `references/music-engine.md`, `references/adapt-a-style.md`, parts of `references/styles/ink-wash.md` and `gallery/previews-src/ink/boat.html` (adapted) | github.com/alexgreensh/anidoodle | Apache-2.0: `LICENSES/anidoodle-LICENSE-Apache-2.0.txt`, `LICENSES/anidoodle-NOTICE.txt` |
| Claude Animation Base guide (John Heibel): the "model the viewer" timing rules | `references/timing.md` (prose adapted, credited in its first line) | github.com/JohnHeibel/ClaudeAnimationBase | MIT: `LICENSES/ClaudeAnimationBase-LICENSE-MIT.txt` |

The files adapted from anidoodle stay under the Apache License 2.0, with its NOTICE. Everything else from the three
upstreams stays under its MIT licence, including the gallery preview images and the music pieces.

## Ideas credited, no code copied

| What | Where | Upstream | Licence |
|---|---|---|---|
| Closed-form springs, launch-video motion moves, the axes of the review score and the subframe motion-blur filter (Raphael Aubry) | `engine/lib/springs.js` (own implementation), `references/motion-kit.md`, `references/timing.md`, the rubric in `references/quality-checklist.md`, one filter line in `tools/export.mjs` | github.com/howseen-ai/claude-motion-design | MIT |
| Character life: blinks placed on head turns with their timings, pose chains that never stop dead, follow-through as a delayed copy of the parent (rossark0) | `references/character-life.md`, `engine/lib/life.js` (own implementation) | github.com/rossark0/rossark-motion-skill | MIT |
| Asking of every shot whether it is a page or a picture, and measuring a film's text with a script (Tejas Makwana) | `references/page-or-picture.md`, `tools/text-audit.mjs` (own script; its corner test uses the same thresholds) | github.com/Tejashmakwana/motionmaxxing | Apache-2.0 |
| Banning the default look by name, a number in place of every adjective, and the easing, spring and stagger numbers (Florence, "Opus 5.5 Motion Lab") | `references/directed-look.md`, sections 1 and 3 (own words) | x.com/flxrnc/status/2105311836190978392 | A published guide; ideas only, none of its text or prompts |

## The path tracer's own notice

`engine/pathtracer/NOTICE.md` lists the engine's runtime dependencies (puppeteer-core, Chrome, three.js in one proof),
the optional Python packages, and the published methods and constants it implements (AgX and ACES tone-mapping fits
with their MIT notices, Sobol direction numbers, GGX, MIS, delta tracking, SAH BVH, à-trous denoiser and others), with
their sources. It travels with the engine.

## Fonts

`examples/felt-good-morning/fonts/Fredoka.ttf` is under the SIL Open Font License 1.1; its licence text is beside it
(`examples/felt-good-morning/fonts/OFL.txt`). No other font files ship in the studio. Films load the fonts their brand
or style calls for; keep each font's licence with the project that uses it.

## Needed at render time (not shipped here)

- Node (20 or later for the page tools; 22.12 or later for the path tracer) and `playwright-core` (Apache-2.0) for the
  page tools, installed into the studio's `node_modules` by `bin/studio doctor` (`tools/doctor.sh`) and linked into each project by
  `tools/new-project.sh`; `puppeteer-core` (Apache-2.0) for the path tracer, installed by `engine/pathtracer/setup.sh`.
  They drive the Chrome or Chromium already on the machine (`tools/lib/browser.mjs`); no browser is downloaded.
- p5.js (LGPL-2.1) and p5.brush (MIT) for the paint medium, installed as npm packages in `node_modules`, not bundled.
- `ffmpeg` and `ffprobe` on the PATH.
- Optional, only when a film needs them: whisper.cpp and demucs (word times and vocal stems for a song), Python 3 with
  numpy and scipy (`tools/songmap.py`, `tools/audio/`, the path tracer's tools), and any paid image, video, voice or
  music service the person chooses. The studio never spends on one without a yes to the price.

## Work we studied

Films and posts that taught something are credited, with links to their makers, in `examples/INDEX.md`. Nothing of
theirs is copied here: no frames, no prompts, no code.
