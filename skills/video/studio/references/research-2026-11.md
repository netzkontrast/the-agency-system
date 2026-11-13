# Upstream tools worth adopting (research, November 2026)

A survey of open-source projects that could make the studio faster or better. Licences and release dates were read
from the npm and PyPI registries in November 2026; re-check before adopting. **Adopted** means the studio already
uses it (optionally); **next** means planned; **avoid** means a licence problem for an MIT suite.

| Area | Project | Licence | Status | What it gives |
|---|---|---|---|---|
| Beats / downbeats | [beat_this](https://github.com/CPJKU/beat_this) | MIT (code + weights) | **adopted** — `tools/audio/beat_this_track.py`, `studio songmap --beat-this` | state-of-the-art beats and downbeats without DBN post-processing |
| Lyric alignment | [stable-ts](https://github.com/jianfch/stable-ts) | MIT | **adopted** — `tools/audio/align_lyrics.py` | `model.align(audio, known_text)`: word times for the *given* lyrics |
| Stem separation | [demucs](https://github.com/adefossez/demucs) | MIT | **adopted** (optional) | htdemucs vocal stem for alignment and stress |
| Stem separation | [python-audio-separator](https://github.com/nomadkaraoke/python-audio-separator) | MIT | next | MDX / Roformer vocal models, cleaner vocals than htdemucs |
| Alignment, 2nd opinion | [whisperX](https://github.com/m-bain/whisperX), [Montreal Forced Aligner](https://github.com/MontrealCorpusTools/Montreal-Forced-Aligner) | BSD-2, MIT | plug-in via `--from-words` | wav2vec2 CTC alignment; MFA is most precise on speech |
| Flash safety | [IRIS (EA)](https://github.com/electronicarts/IRIS), [iris-pse-detection](https://github.com/tokoroten/iris-pse-detection) | BSD-3, MIT | **adopted** as second opinion — `flash_test.py --iris` | luminance, red-flash and pattern analysis per frame |
| Flash safety, test media | traceRERC/pse-test-media | — | next | pass/fail benchmark clips to regression-test `flash_test.py` |
| Subtitles | [pysubs2](https://github.com/tkarabela/pysubs2) | MIT | not needed — `tools/audio/srt.py` writes SRT/VTT/ASS karaoke itself | ASS `\k` karaoke tags |
| Capture speed | [mediabunny](https://github.com/Vanilagy/mediabunny) | MPL-2.0 (fine unmodified) | next | WebCodecs `VideoEncoder` + MP4 muxing inside the page: no PNG round trip, roughly 5–20× faster capture; keep ffmpeg as fallback (headless Chromium may lack an H.264 encoder) |
| Capture determinism | [puppeteer-capture](https://github.com/alexey-pelykh/puppeteer-capture) | MIT | optional | `HeadlessExperimental.beginFrame` virtual time (the film contract already makes frames pure functions of t) |
| Parallel rendering | [Revideo](https://github.com/midrender/revideo) | MIT | idea adopted | chunked render across workers + concat — `render.mjs --frames --workers=N` resumable frames |
| Timeline ideas | Motion Canvas (MIT), Theatre.js (Apache-2.0) | — | later | generator timelines, an editable keyframe UI for the review room |
| Drawing | [p5.brush](https://github.com/acamposuribe/p5.brush) | MIT | **adopted** 2.2.3 (v3.0 is out: check the API before upgrading) | the paint medium |
| Drawing | [perfect-freehand](https://github.com/steveruizok/perfect-freehand) | MIT | next | pressure-sensitive ink strokes beside p5.brush |
| Drawing | roughjs, paper.js | MIT | optional | sketchy primitives, vector booleans |
| Loudness | [pyloudnorm](https://github.com/csteinmetz1/pyloudnorm) | MIT | not needed — `tools/audio-check.mjs` measures BS.1770 LUFS, true peak, LRA | — |

## Avoid (licence)

| Project | Why |
|---|---|
| Remotion | company licence (free only for individuals and teams up to 3); read its docs for ideas, never vendor its code |
| lygia (shader library) | Prosperity / Patron licence, non-commercial unless sponsored; write our own grain/ink/glitch shaders |
| aubio | GPLv3 |
| essentia | AGPL |
| madmom models | CC BY-NC-SA (non-commercial); its code is BSD but the models are what matter |
| BeatNet | CC BY 4.0 — usable with attribution, but beat_this is better and MIT |

## Second survey: animation, 3D and shader libraries (November 2026)

Adopted from it — and shipped with the studio — are three.js + addons, pmndrs postprocessing (Zlib), pixi.js 8,
animejs 4, lottie-web, d3, roughjs, perfect-freehand, opentype.js, simplex-noise, alea and culori, plus the studio's
own three.js stylisation passes, GLSL library and shader runtime. Every library, its licence and how to drive it
deterministically by `t`: `references/libraries.md`. Which look uses which: `references/style-recipes.md`.

Key findings that shaped the design:
- three's WebGPU renderer + TSL is a second backend (EffectComposer and ShaderMaterial do not work on it); the
  studio stays on WebGLRenderer, which is bit-stable under SwiftShader. Some addons call `Math.random`; the three
  medium replaces it with a stream seeded per frame.
- Feedback shaders (trails, fluids, reaction-diffusion) are history-dependent: the shader runtime re-simulates a
  fixed warm-up window before every frame; long histories are baked.
- Physics: only Rapier's `-deterministic` builds are cross-platform deterministic; everything else is baked to a
  per-frame cache.
- Shader code: copy only MIT/BSD/CC0 sources (Ashima noise, Inigo Quilez article snippets, hg_sdf under MIT, glsl-*
  packages, CC0 blue noise); re-implement anything from Shadertoy, lygia or The Book of Shaders.
