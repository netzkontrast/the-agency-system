# Style: Kinetic lyric video

The song's words are the visuals. Every lyric line becomes its own typographic scene with a visual metaphor for its meaning. No characters needed. Reference: a take on the P(doom) song (Sep 2026, 2:36, 60 fps): "I also gave it a try with a different style".

## How to design it

- **Start from the lyrics with timestamps** (transcribe, then have the user correct them). For each line, write: the key word(s), the meaning, and one visual metaphor (the word rides a crashing curve, wraps around a black hole bending a grid, mirrors itself for an opposite, rolls on a counter for a number, sits on a diagram for a technical idea, extrudes into a 3D corridor for "nowhere to go").
- **Words arrive exactly when sung.** Word-level timing from the transcription (or beat-snap by hand). The hook/chorus word gets the biggest treatment each time it returns, escalating.
- **Two worlds for contrast:** mostly black with one hot accent (orange ~#FF5A1F); a paper-white "technical document" world (mono headers like `APPENDIX C — LEGACY ARCHITECTURES`, ruled lines, diagram boxes with hatching) for verses that are about ideas.
- **Type system:** a heavy grotesk for the sung words (huge, often filling the frame), mono labels and data readouts around them, one italic serif word for soft moments, outlined type for echoes.
- **Effects vocabulary:** words on warped perspective grids, extruded 3D letters, particle bursts, counters and odometers, glitch slices, a single glowing object for the big emotional line.
- HUD corner marks and tiny meta readouts make every frame feel engineered.

## Hebrew and RTL

For Hebrew lyrics: use a strong Hebrew display face (e.g. Heebo Black, Rubik, Secular One, Assistant ExtraBold, Frank Ruhl Libre for the serif moment) from Google Fonts, set `ctx.direction = 'rtl'`, and animate words in reading order right-to-left. Check every frame for correct letter order and final forms.

## Engine

Canvas 2D (WebGL for grids/3D type if wanted) via `scripts/new-canvas-project.sh`. Drive everything from a `LYRICS` array of `{t0, t1, text, key, scene}` and the song's BPM.
