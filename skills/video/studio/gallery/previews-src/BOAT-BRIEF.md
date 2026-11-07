# The one-story preview pack: THE PAPER BOAT

Every style card in the gallery shows the SAME tiny story, two frames, rendered by us in that style. This proves the style file works and shows only our own work.

## The story
A small paper boat sets out at first light, meets a storm at sea, and (beyond these two frames) comes home. The boat is a folded paper boat: a hull and a triangular sail-peak, no face, no limbs. It is the protagonist; give it attitude through tilt, position and light, never anatomy.

## The two frames (fixed formula for every style)
- **Frame A — "setting out":** calm water, morning light, the boat lower-left third heading right, horizon visible, a feeling of quiet beginning. Big sky.
- **Frame B — "the storm peak":** the boat small against one big diagonal wave (or the style's equivalent of overwhelming force), dramatic sky, one light source fighting through. The boat still points forward.

## Rules
1. 16:9, render at 1280x720, export JPG quality ~88.
2. Everything drawn in code (canvas/SVG/WebGL). No model images, no photos, no frames from anyone's video, no CSS filters.
3. Deterministic: seeded randomness only; the same code gives the same pixels.
4. Obey YOUR style file completely: its palette, marks, light, type rules, motion grammar (frozen at its most characteristic moment). The boat is translated INTO the style; the style never bends to the boat. Type/captions/HUD only if your style calls for them, and then with the style's real devices.
5. Phone check: both frames must read at 360 px wide. The boat must be findable in under a second in both.
6. Composition is shared across all styles (A: boat lower-left heading right; B: boat small, wave diagonal from upper right) so the gallery reads as one system.

## Render
Write `boat.html` in your style folder: full-window `<canvas id="c">` 1280x720, and `window.drawFrame(which)` where `which` is "a" or "b" draws the complete frame synchronously (or sets window.DONE=true when finished if async). Set `window.READY = true` (or a promise) when loaded. Then:

```bash
cd <your style folder> && NODE_PATH=<dir containing node_modules with playwright-core>/node_modules node ../snap.mjs boat.html
```

which writes `a.png` and `b.png` beside it. Convert your final picks to the gallery files yourself:

```bash
ffmpeg -y -v error -i a.png -q:v 3 <style-id>-a.jpg && ffmpeg -y -v error -i b.png -q:v 3 <style-id>-b.jpg
```

## Self-review before finishing (mandatory)
Look at both frames full size AND at 360 px wide with real eyes. Ask: would a stranger name this style's medium correctly from the frame alone? Is the boat alive (tilt, wake, light) or a pasted icon? Does frame B feel dangerous? Fix and re-render until yes; 2-4 rounds is normal. Your final message must state your honest 1-10 score per frame and what you'd fix next.
