# The song map

A music video is cut to the song, not to a guess of it. The song map is everything the film needs to know about the
track — bars, sections, the drop, every sung word with its start, end and **stressed** moment — measured once and
loaded by the film as `songmap.js` (read through `SONG.*`, `engine/lib/beat.js`). The agent cannot hear: it measures.

## One command

```bash
bash <studio>/bin/studio songmap song.wav --dir <project> --lyrics lyrics.txt [--lang de] [--beat-this] [--stems auto|demucs|none]
```

It runs, in the project folder:

1. `tools/audio/beatmap.py song.wav --out songmap/beatmap.json` — tempo, beat grid, downbeat phase, bars, energy
   sections (hook, full, stop, build, drop, release), the drop, stops, pickups, risers, top hits. Also writes
   `songmap/beatmap.md` to read. numpy + scipy.
2. *(optional, `--beat-this`)* `tools/audio/beat_this_track.py` — beats and downbeats from **beat_this** (MIT, code and
   weights), stronger on soft onsets, swing and ramps. Its beats replace beatmap.py's; sections and the drop stay.
3. *(with `--lyrics`)* `tools/audio/align_lyrics.py` — vocal stem (demucs `htdemucs` two-stem when installed), then
   **forced alignment of the known lyrics** with stable-ts `model.align()` (not transcription), then the stressed moment
   of each word (the loudness peak of the vocal inside the word), lines, sections from `[Verse]`/`[Chorus]` tags and
   each line's key word (`*marked*` in the lyrics file, else the loudest word).
4. `tools/audio/songmap_js.py` — merges both into `songmap.js` (`window.SONGMAP = {…}`).

Any other aligner (whisperX, Montreal Forced Aligner, a hand-corrected list) plugs in with
`--from-words raw.json` (`[{"word", "start", "end"}, …]`).

## The lyrics file

The person's real lyrics — for a released song the **streaming lyrics** — never a phonetic spelling written for a
generation model. One sung line per line; `[Section]` tags; `*key*` marks the word an action lands on:

```
[Verse 1]
I keep the *window* open
[Chorus]
lass mich, lass mich *atmen*
```

## Rules that came from real films

- **Stress, not start.** A word's start is where the mouth opens; the hit is on the stressed syllable, often 0.2–0.45 s
  later (final-stressed words especially). Use `SONG.word(t).stress` / `line.key.stress` for impacts, `t` for
  anticipation.
- **Put every action word in the storyboard** with its time. Anything left out gets estimated by an animator and lands
  early or late.
- **Check tempo drift** before trusting a grid: a generated track can wander by 250 ms over its length. beat.js follows
  the measured beats, so the picture stays in sync even when the tempo moves; never cut long passages to a fixed BPM.
- **Re-map after mastering** if the master's length or start changed (`ffprobe` both; the gate battery compares the
  picture length with the audio).
- **Big events on downbeats, the story's turn on the drop or the silence**, holds when the voice holds.

## In the film

```js
const k = SONG.line(4).key;                 // { w, t, stress }
const hit = spring(t, k.stress);            // the action lands on the stressed syllable
const bar = Math.floor(SONG.barAt(t));      // which bar we are in
const glow = SONG.pulse(t, 8);              // 1 on each beat, decaying
const sec = SONG.section(t)?.name;          // 'Chorus', 'drop', …
```

## Subtitles

```bash
bash <studio>/bin/studio srt --words songmap/words.json --out out/film.srt          # one cue per line, readable timing
bash <studio>/bin/studio srt --words songmap/words.json --out out/film.ass          # karaoke (\k per word) for burn-in
```

Uploading the `.srt` lets muted viewers follow without type in the picture.

## Mapping a track you cannot hear (quick look)

`python3 <studio>/tools/songmap.py track.wav [bpm guess]` prints tempo, first beat, loudness per half second (all,
bass, top), silences and the last hit — enough to place a drop and an end card on an instrumental bed.
