# Pipeline smoke run (2026-11-08)

An 8-second abstract music clip taken through the **whole** studio pipeline, with the subagent briefs used as
written, to prove the chain end to end and to find what breaks. Medium: three (toon + ink + boil + paper + grain +
fade). Song: a synthetic 120 bpm test track with two sung lines (word times supplied through `--from-words`, because
stable-ts was not installed in the cloud container). Machine: cloud container **without GPU** (SwiftShader).

| Phase | What ran | Result |
|---|---|---|
| 0–2 Intake, brief, route | producer | `BRIEF.md`; playbook `music-video.md`; medium three |
| 4 Map | `bin/studio songmap audio/song.wav --lyrics … --from-words …` → `beatmap.py`, `align_lyrics.py`, `songmap_js.py`; audio mastered to −14 LUFS with `audio-check.mjs` | 16 beats, 4 bars, 10 words with stress times |
| 5 Storyboard + critic | `STORYBOARD.md`, drawn sheet (`render.mjs --stills` + `bin/studio storyboard`), a **new critic subagent every round** (`agents/critic.md`) | rounds 1–5 REVISE (one blocking item each, all real: hero not the chosen shape, a last frame reading as a face, neighbours in the hold, a stray speck), **round 6 CLEAR** |
| 7 Build | scene built from the song map (anticipation 0.15 s before "atmen", push settling on "hier", kicks on downbeats) | — |
| 8 Gates | `bin/studio gate . --mp4 …` | take 1: 1 FAIL (undeclared end hold) → declared → PASS; take 3: 1 FAIL (pops on beats) → fixed → **PASS on all six: render gate, text, edge, plate, flash, loudness** |
| 9 Review | `bin/studio pack …` + `WORDS-AND-SOUND.md` filled + a **new reviewer subagent every round** (`agents/reviewer.md`) | take 1: 5/10 RETURN · take 2: 6/10 RETURN · take 3: 5/10 RETURN → **stopped at the 3-round limit**, delivered with the score (rule in `SKILL.md`) |
| 11 Master | `render.mjs --clip --audio`, `srt.py --end 8` | `film-take3-640.mp4` (preview copy), `review/film.srt` |

Render speed here (no GPU, 960×540, 3 workers): 96 drawings on twos in 18 s; 192 frames on ones in about 35 s.

## What the run fixed in the studio

- `SONG.pulseSoft()` added to `engine/lib/beat.js`: `SONG.pulse()` has an instant attack, and positions driven by it
  jumped in one frame on every beat — the gate measured the pops. Use `pulse` for light/colour, `pulseSoft` for motion.
- `FX.fade` added (19th pass): a paper veil inside the scene was re-inked by the ink pass and left a cartoon-like
  outline at the end (both a critic and the reviewer saw it). Fades go last in the pass chain.
- three/shader templates pass `holds` and `cuts` from `setup()` to the gate (`window.HOLDS`, `window.CUTS`).
- `render.mjs` fails at once with the page's error message instead of waiting out the whole timeout.
- `srt.py --end`: no cue for a line sung after the film ends.
- Briefs: the song-map report path (`songmap/beatmap.md` + `songmap/words.json`).

## What the reviewers said (take 3), unresolved

The hook (4/10): a fade-in from paper and little motion before the first sung word; nothing marks the stressed "ich"
at 4.00 (the push builds instead of hitting); 2.8–4.0 s is thin and two shapes slide off the edges. The piece is an
abstract test loop, so these are craft notes, not studio defects — but they are exactly the kind of note the
reviewer is there for, and the scores were reported as they were.
