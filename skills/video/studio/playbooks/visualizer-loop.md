# Playbook: Visualizer and loop

**Use when** the picture should breathe with the audio rather than tell a story: a full-length visualizer built from
a few plates plus audio-reactive motion, a Spotify Canvas (3–8 s, 9:16, seamless), a Reels/TikTok loop, an
ambient piece for a stream or a gallery screen. **Not when** the song needs a story, an arc or acted lines
(`music-video.md`), or the words are the picture (`lyric-video.md`).

## Inputs to collect

- Master audio (for a visualizer) or the song section the loop should stand for (for a Canvas: usually the hook).
- The cover art and album look (a loop must sit next to the cover in the player), owner's taste, depiction rules.
- Platforms: Spotify Canvas (9:16, 3–8 s, no text, no logos, plays muted under the player UI), YouTube visualizer
  (16:9 full song), Reels/TikTok (9:16 with sound).
- How many tracks need loops (an album suite reuses its shared library here).

## Defaults

| Item | Visualizer | Canvas / loop |
|---|---|---|
| Length | the full song | 3–8 s, a whole number of bars when tied to tempo (bar = 4 × 60/BPM s) |
| Aspect / size | 16:9 1920×1080 | 9:16 1080×1920 (`--aspect=9:16`) |
| fps | 24 on twos (paint) or 30 (canvas) | 24 (paint, on twos) or 30 |
| Medium | paint or canvas | paint (`LOOPS`) or canvas |
| Plates | 2–5 painted or drawn plates, one per section family | 1 plate, one movement |

Style candidates: `references/styles/ink-wash.md`, `painterly-glow.md`, `watercolor.md`, `paper-cutout.md` (layered
parallax), `pixel-art.md` (stepped loops), `ascii-terminal.md` (audio-as-characters), `riso-pop.md`.

## Phase deltas

| # | Phase | What changes |
|---|---|---|
| 1 | Brief | short; platform specs above are the brief. No claims check. |
| 3 | Pitch | one image per plate and one motion vocabulary (breath, pulse, drift, shimmer) mapped to audio drivers. No storyboard of lines. |
| 4 | Map | visualizer: full `bash <studio>/bin/studio songmap song.wav` (lyrics optional). Loop: `python3 <studio>/tools/audio/beatmap.py` on the chosen window for BPM and bar length. |
| 5 | Storyboard | a **section map**, not a shot list: section → plate → which `SONG.*` drivers move which layer → transition at the section seam. Critic still reads it (dead stretches, no escalation). |
| 6 | Test section | visualizer: the first chorus (30 s). Loop: the loop itself is the test. |
| 7 | Build | one animator usually suffices; split a visualizer by section group only if > 4 plates. |
| 9 | Review | loops: the reviewer watches it repeated 5×; seam and boredom are the questions. |

## Team & fan-out

Producer, art-director (plates, palette), 1 animator (2 for a long visualizer with many plates), songmap-analyst
(visualizer), qa-operator, reviewer, copywriter (Canvas needs no post; visualizer needs one). No director-level
critic round for a single Canvas loop; keep it for visualizers > 60 s.

## Craft rules specific to this type

1. **Audio drives motion through the song map, never through a live analyser.** Frames stay pure functions of `t`:
   `SONG.pulse(t)` for breath and punches, `SONG.beatAt(t)` / `SONG.barAt(t)` for cycles, `SONG.section(t)` to
   switch plates, `SONG.hit('drop')` for the one big change. Per-frame spectrum bands, if needed, are precomputed to
   JSON and read by frame (`references/audio.md`, the audio-reactive HUD).
2. **Motion budget per layer:** background drifts 1–3 % per bar, midground breathes with `SONG.pulse`, one accent
   reacts to hits. Punch sizes from `references/motion-kit.md` (+0.012/beat, +0.03/bar after the drop); nothing
   punches in quiet sections.
3. **A visualizer still escalates:** later choruses get more layers, more light, a widened palette; the bridge strips
   to one layer; the end rhymes with the start. A full song on one plate with one motion fails the variety axis.
4. **Seamless loop = period divides the length.** In the paint medium define `LOOPS.name = t => {...};
   LOOPS.name.len = <s>;` and render it with `node <studio>/tools/render.mjs --clip --query=loop=name
   --aspect=9:16 --out=out/canvas.mp4`. Every cyclic term uses `sin(2π·k·t/len)` with integer k; boil seeds repeat
   on the same cycle; frame `len·fps` equals frame 0 (check with a strip across the seam).
5. **Canvas specifics:** no text, no logos, no fast cuts; keep essentials inside the middle (player UI covers top and
   bottom), avoid hard flashes; loop length 3–8 s; one movement that is satisfying on the tenth repeat.
6. Plates are drawn or painted in code; generated plates only with the person's yes and price (`references/real-shots.md`).
7. Transitions between plates on bar lines at section starts (`SONG.downbeat(n)`); brush wipe or a shared element.
8. Audio for a looped post ships as WAV-backed mux; a code bed loops cleanly with `node <studio>/tools/music.mjs render <piece.mjs> --out loop.wav` (`references/music-engine.md`).

## Gates & bar

- Battery (`bash <studio>/bin/studio gate <dir>`), with long deliberate stills declared as `HOLDS`; dead-air check is
  the most likely FAIL on a visualizer — a whole section with < 1 % change is dead, not calm.
- **Loop seam check:** `--strip` over the last 6 and first 6 frames; first and last frame identical in hash
  (frame `len·fps` vs 0); played 5× in a row without a visible jump.
- Flash test (hard) on every loop: pulses on large bright fields count.
- **Reviewer locked items:** the cover/album look, the song, no-text rule for Canvas.
- **8/10 here:** motion visibly locked to the music (sound-sync axis from the measured beat list), something new
  every 10–20 s in a visualizer, a loop nobody can find the seam of, and nothing a muted viewer misses.

## Pitfalls

- `Math.random` or a time-accumulating particle system: breaks determinism and the seam.
- Pulse on every beat at full size: reads as shaking (keep under ~3 % scale).
- A loop whose length is not a whole number of bars when the motion is tempo-locked: the seam stutters on repeat.
- MP3 audio on a looping post: encoder padding clicks at the seam.
- One plate for four minutes.

## Deliverables

Visualizer: `out/<name>-visualizer.mp4` 16:9 with the song, `POSTS.md`. Loops: `out/<name>-canvas.mp4`
(9:16, H.264, no audio for Spotify Canvas), `out/<name>-loop-reel.mp4` with audio if ordered, loop length and bar
count in the delivery note, gate report with seam and flash results.

## Checklist

- [ ] Platform spec chosen (Canvas / Reel / visualizer)
- [ ] Section map: plate × drivers × transition
- [ ] All motion from `SONG.*`; no live audio analysis
- [ ] Loop length = whole bars; seam hash equal
- [ ] Gate (dead air declared) + flash test PASS
- [ ] Viewed 5× in a row; reviewer ≥ 8
