# Build notes (as built, not as planned)

Every agent reads this first. Append every direction the lead gives during the build, the shared APIs as delivered,
file ownership per chapter, and the render/review commands.

## Owners
| File | Owner |
|---|---|
| film.html, config.js, songmap.js, engine/ | lead (read-only for chapter animators) |

## Directions from the lead
- Chapters: ch01 = shots 1–7 (0–44 s), ch02 = shots 8–15 (44–100 s), ch03 = shots 16–21 (100–138 s). film.html loads
  scenes/ch01.js, ch02.js, ch03.js in that order; every shot is a pure function of t; every event time comes from SONG
  (SONG.word, SONG.line(i).key.stress, SONG.pulseSoft for the heartbeat glow).
- Shared look (owner: the lead): lib/look.js (palette, room props: door, curtain, lamp, pillow, window, wall+seam, ping).
  Chapter files only call these helpers.
- Render: cd <proj> && STUDIO_GL=soft node <studio>/tools/render.mjs --sheet=... (no GPU in the cloud; ~0.5 s per drawing).
  Gate: bin/studio gate . --mp4 out/film.mp4 (determinism, dead air with --step 12 / FILM_STEP, pops, text, edge, plate, flash).
- v2 (measured song map, 2026-11-08): the audio file exists (audio/13-ich-bin-hier-das-war.mp3, 138.12 s). STORYBOARD.md is
  re-timed to the measured map: 23 shots, ch01 = shots 1-7 (0-44.6 s), ch02 = 8-15 (44.6-78.6 s), ch03 = 16-23 (78.6-138 s).
  Shot boundaries must be computed from SONG at load time (line i: SONG.line(i).t / .end / .key.stress; lines 0-21: 0 intro,
  1-4 verse 1, 5-8 refrain, 9-12 verse 2, 13-16 refrain 2, 17 bridge, 18-19 outro, 20-21 outro repeat). Never hard-code a time.
- audio/ is not committed (binary outside Git LFS): put the album's MP3 at audio/13-ich-bin-hier-das-war.mp3 (it came from the user's Google Drive, 'Ich bin hier _ Das war.mp3', 138.12 s); songmap/transcribe.py + align.py re-measure the song map from it (needs faster-whisper, soundfile, librosa).
