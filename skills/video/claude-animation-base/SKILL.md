---
name: claude-animation-base
description: Paint a hand-made 2D animation (p5.js + p5.brush — ink lines that boil, watercolour, charcoal hatching, paper grain) where every frame is a pure function of time, review it with contact sheets and frame strips, and render it to MP4 with music. Use as the drawing medium for music videos in the video domain (Spec 140); take-one drives the process around it.
---

# Claude Animation Base (ported)

Ported from [`netzkontrast/ClaudeAnimationBase`](https://github.com/netzkontrast/ClaudeAnimationBase)
— see `skills/video/README.md` for the commit and licence. Everything in this folder except
this `SKILL.md` is the upstream repo unchanged.

## Read first

1. **`ANIMATION_GUIDE.md` in this folder, in full**, before drawing anything. It holds the
   rules (handmade, alive, one piece, no text, transitions always), the workflow
   (storyboard → build → contact sheet / strip / crop review → render) and the full engine
   API (`paint`, `inkLine`, `glow`, `camBegin`, `shots`, timing helpers).
2. For an **Agency System** album, the album's `VIDEO-CONCEPT.md` overrides the guide where
   it says so (no mascot: `clawd.js` is not used; objects and light are the performers; two
   text exceptions; flash-safety gate). Load the gate skill `skills/theagencysystem/` first.
3. For the process around a full music video (song map, critic, test section, fresh
   reviewer, review room) use `skills/video/take-one/` — `references/music-video.md`.

## Run

Needs Node.js, Chrome/Chromium and ffmpeg.

```bash
cd skills/video/claude-animation-base   # or an album's own copy of the kit
npm install
node render.mjs --sheet=0.5,1,1.5,2 --out=out/check/a.jpg   # contact sheet
node render.mjs --clip --out=out/video.mp4                   # whole video, one worker
node render.mjs --frames --workers=4 && node render.mjs --encode --audio=song.mp3 --out=out/video.mp4
```

Open `studio.html` in Chrome to scrub.

## Known issues (found while test-rendering in a cloud container)

- **Chrome detection:** `render.mjs` takes the first path that exists. Where
  `/usr/bin/google-chrome` is only a wrapper script, the page never loads. Pass
  `--chrome=/opt/pw-browsers/chromium-*/chrome-linux64/chrome` (Playwright's Chromium) or
  set `CHROME_PATH`.
- **Navigation timeout:** with no GPU (`--soft-gl`), page start-up can exceed the fixed
  30 s / 60 s timeouts in `openPage()`. Raise them for software rendering.
- **Speed:** without a GPU, about 26–32 s per 1080p frame of the demo on 4 CPU cores.
  Take One measured about 1.5 s per frame with 11 workers on a 12-core Mac.

These and the further kit changes the video domain needs (bar map instead of a fixed BPM,
several tracks per kit, de-duplicating frames on twos, 9:16) are listed in
`Plan/140-video-domain/spec.md` §6.
