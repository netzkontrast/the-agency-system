# Style: Watercolor character

Hand-painted watercolor and ink, like a picture book that moves. A character acts out a small story; linework "boils" like hand-drawn animation. Reference: the Opus 5.5 music video "I'm Upping My P(doom)" (github.com/JohnHeibel/PDoomVideo).

## Engine: the paint medium

This style runs on the studio's paint medium (p5.js + p5.brush), already inside the studio; nothing is downloaded.

```bash
bash <studio>/tools/new-project.sh <project-dir> --medium paint [--character] --duration 30
```

Then **read `references/paint-medium.md` in full before drawing anything**. It is the real instruction set for this
style: the medium (p5.brush `paint()` / `inkLine()`, never plain p5 shapes), no text, something happens in every scene,
timing, transitions, the character API (views, 31 emotions, hats, dances, emotes; loaded with `--character`), the
engine (`config.js` for duration and the fallback bpm, the song map through `engine/beat.js`, chapters in
`scenes/`), and the review commands.

Render and review from the project folder:
```bash
node <studio>/tools/render.mjs --sheet=0.5,1.5,3,4.5 --cols=4 --w=480 --out=review/a.jpg   # contact sheet
node <studio>/tools/render.mjs --strip=2.0:2.5 --cols=6 --w=320 --out=review/strip.jpg      # every frame of a moment
node <studio>/tools/render.mjs --clip --audio=assets/song.mp3 --out=out/video.mp4           # final MP4
```

## Adapting it to the user's subject

- The medium ships with an optional sample mascot (`--character`). For the user's own video, ask whether to keep it or design their character (a mascot, a stylized version of them, their product as a creature). A new character is painted with the same tools and rules so it belongs.
- Characters are the emotional anchor: faces act (take, squash, emote) instead of snapping between moods.
- Text is off by default. If the user needs words (a product name, a tagline at the end), paint them with `letter()`, one or two words, once.

## Notes from the source author

- Storyboard first, then build. Give broad direction ("cute, fun colors, something happening in every shot, be brave") and let the model invent scenes; it's strong at gags.
- Higher reasoning effort gives more extravagant, detailed scenes. Build this style at the highest effort available.
- Watercolor fills are GPU-heavy. Apple Silicon handles them; budget about 1-2.5 s per frame. Fewer, bigger shapes render faster than thousands of small ones.
- Long films: one chapter file per subagent, a shared guide and storyboard, shared files read-only, each agent checks its own contact sheets.
