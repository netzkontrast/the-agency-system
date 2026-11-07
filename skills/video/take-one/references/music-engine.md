# Code music engine (v1)

Instrumental music written as a score and synthesized in pure JavaScript. No samples, no API, no credits. The same score and seed always produce the same WAV, byte for byte. It's fitted to the film's exact length by solving the tempo, so the last note lands where the picture ends.

Adapted from anidoodle (github.com/alexgreensh/anidoodle), Apache License 2.0, Copyright 2026 Alex Greenshpun. Every file under `scripts/music/` carries that header.

## When to use it, and when to use Suno

| Use the code engine | Use Suno |
|---|---|
| A bed under narration or captions | Anything with a voice or sung lyrics |
| A sting or button at a cut (a few bars, `hit: true`) | A full "song" that carries the film |
| A seamless loop for a web page or a looping post | A genre texture code can't fake (distorted guitars, real drums, choirs) |
| The film's length will change again (re-fit is free) | The user wants to direct the music himself in Suno's UI |
| Sync matters: notes land on exact frames | |

Code piano, strings, harp and soft lo-fi electronic sound good. Code does not do a convincing rock band, orchestral brass, or a human voice. Don't promise those.

## CLI

```bash
node scripts/music.mjs render <piece.mjs> --seconds 45 --out bed.wav   # fit to 45 s, 48 kHz 32-bit float WAV
node scripts/music.mjs render <piece.mjs> --out loop.wav               # a plan.loop piece renders as a seamless loop
node scripts/music.mjs check  <piece.mjs> [--seconds N]                # must print PASS before anyone listens
node scripts/music.mjs meter  <file.wav|mp4>                           # meter any file
```

`<piece.mjs>` default-exports a Piece or a function returning one. `file.mjs#name` picks another export. Every render happens twice and the two are compared sample by sample (it prints `deterministic: yes`).

`check` runs: bar math (a bad bar throws while the score loads), the key/mode histogram against each section's declared key and mode, tempo against the style's range, no close thirds below C3 in piano parts, a determinism check, the master target (LUFS and true peak), onsets per beat, and a cross-check against ffmpeg `ebur128` (it must agree within 1 dB).

Mux the WAV with `scripts/mux-audio.sh`. A loop ships as WAV (MP3 encoder padding clicks at the seam).

**When the film needs an exact tempo.** `render` prints the tempo it solved ("tempo 99.9 bpm"). The fit lands the piece's end on `--seconds`, so a score written at 100 can come out a few beats a minute off. If the cut is on a beat grid, read that line, nudge `--seconds` until it prints the tempo you need, and trim or fade the tail in the mix. One film asked for 40.8 s and got 102.7 bpm; 41.87 s gave 99.9.

## The notation (`line`)

```js
import { line } from "./scripts/music/plan.mjs";
line(startBeat, "Eb4:1 | C5:2 Bb4:.5 Ab4:.5 | [Ab2 Eb3]:1 r:2", { role: "melody", v: 0.7, bpb: 3 });
```

| Token | Meaning |
|---|---|
| `C5:2` | note C5, 2 beats long |
| `F#4:.5` `Bb3:1/3` | sharps/flats; durations as decimals or fractions (triplets `1/3`) |
| `[C4 E4 G4]:1` | a chord; its notes roll by `roll` seconds each (default 12 ms) |
| `r:1.5` | rest |
| `G5:1@0.8` | per-note velocity multiplier (times the line's `v`) |
| `\|` | barline. **Every bar must sum to `bpb`**, the last one too |

Options: `role` (melody, inner, bass, accomp, color, drum), `v` (0.7 = mezzo), `bpb` (beats per bar: 3/4 = 3, 4/4 = 4, 6/8 = 2, 12/8 = 4), `pickup` (the first bar may be this many beats), `roll`, `kind` (drum variant: `o` = open hat), `hit: true` (a single sting bar shorter than the meter).

A wrong bar throws and names the fix: `bar 1 sums to 2.5 beats, meter wants 4: "G4:2 A4:.5" (a line that ends mid-bar writes its rest: "G4:2 A4:.5 r:1.5")`. A gap is always written, never silent.

## A Piece

```js
{
  title, seed, tail /* seconds of ring after the last onset */,
  harmony: [{ t: beat, name: "Am9" }],        // drives the piano pedal (lifts at each change)
  plan: {
    style: "nocturne",                        // tables.mjs STYLES: sets tempo range, room, master
    tempo: 64, meter: "3/4", phraseBars: 4, swing: 0.57 /* 0.5 = straight */, loop: false,
    pickupBeats, rubato, ritard,              // optional: rubato 1 = +-2.5 % phrase arch; ritard end-tempo ratio
    sections: [{ id, bars, mood, key: "G", mode: "major", melody: ["hook"], dyn: [0.4, 0.6],
                 optional, repeatable, pickup, variations: ["octaveDouble", "octaveUp", "thin"], ending }],
  },
  parts: [{ id, inst, role, notes, gainDb, pan, send /* room send */, opts }],
  shortForm: () => Piece,                     // used automatically when the film is too short
  fx: { duck: { by: "kick", parts: ["pad"], depth, release }, tape: { wowCents, wowHz, flutterCents, flutterHz, drive }, clean },
  stemTargets: { kick: -14, lead: -17 },      // stem RMS dBFS targets (+-3 dB)
}
```

**Instruments (v1):** `piano` (modal: inharmonic partials, 2-3 detuned strings with two-stage decay, hammer spectrum and strike comb, knock, 40-mode soundboard, dampers, sustain pedal, sympathetic strings), `strings` (5 detuned PolyBLEP saws, bow attack, delayed vibrato; opts `attack release bright width`), `harp` / `guitar` (extended Karplus-Strong), `musicBox`, `ePiano` (FM), `warmPad` (7 chorused saws; `cut attack release spread`), `softPluck` (`decay bright pan delay feedback delayMix`), `sub`, `bass` (saturated, audible on phones), `kick`, `snare` (`rim: true` for ghosts), `hat` (`pan`, `crush`), `vinyl`.

**Performance** (automatic): velocity from the section's `dyn` curve times a phrase arch (peak near 62 % of the phrase), metric accents, AR(1) timing (about 7 ms) and velocity noise, a piano melody lead of 12-28 ms, legato overlap, swing, a closing ritard, and a breath before a sudden hush. Mechanical parts set `opts: { grid: true }`.

**Master:** gentle styles use one static gain to -16 LUFS, capped at -1 dBTP, never a compressor. If the cap stops it short, the loudness goes down (fix it in the notes: stagger the bass an eighth after the downbeat, roll the climax chord, don't double the climax note). Dense styles (lofi, drive) run -14 LUFS through a 1.5 ms look-ahead limiter.

**Fitting:** `fitToDuration` tries every drop of the `optional` sections and every repeat of the `repeatable` group (with variations), solves the tempo that lands the last onset at `seconds - tail`, and keeps the tempo within the style's range +-10 % and +-18 % of the written tempo. Nothing in a score hard-codes the film's length.

## The two demos (`scripts/music/pieces/`)

**`first-light.mjs`: a gentle bed in G, piano and strings, 3/4.** A hook that rises a third and settles by step, a theme with a half cadence and then a full cadence, a four-bar build that climbs to B5 over Am with an eighth-note left hand, a hush, a coda through a borrowed Cm (the Eb), and home. Strings enter at bar 5 as a sustained choir. It has a short form (intro plus theme) for films of 25-33 s.

- 45 s: fitted to 69.4 bpm, full form. -17.9 LUFS, LRA 8.7 LU, -1.05 dBTP (ffmpeg: -17.9 / -1.10), 1.00 onsets/s, centroid 681 Hz. The short-term loudness arcs from -23.8 up to -14.1 at the climax and back down to -26.2. The gentle master is peak-capped: piano treble attacks give a crest of about 17 dB, so it lands 1.9 dB under -16 rather than adding a compressor.
- It fits 30 s (short form, 57 bpm), 45 s, 60 s (theme doubled), 90 s and 120 s (theme and build restated with variations).

**`night-drive.mjs`: a 120 bpm half-time lo-fi loop, 8 bars = exactly 16.000 s.** Am, Fmaj9, Cmaj9, Em7 twice. A kick-ducked warm pad, FM e-piano offbeat stabs, a soft pluck hook through a dotted-eighth ping-pong delay, a sine sub, a snare on 3, swung (0.57) eighth hats, and vinyl and tape wow snapped to whole cycles per loop. The tail is folded back onto bar 1, so it loops without a seam.

- -14.0 LUFS, LRA 1.9 LU, -3.36 dBTP (ffmpeg: -14.0 / -3.40), 4.19 onsets/s (2.1 per beat), centroid 1262 Hz. All stems are within 3 dB of their targets.

Copy a demo as the starting shape for a new score. Write your own melody and changes: a reused tune isn't a new score.

## Limits (v1)

- No mood-table picker yet: you choose style, key, mode and tempo yourself (use `tables.mjs` MOODS as the guide).
- The windowed ghost, reverb and masking guards and the novelty check aren't ported yet. `check` reports onsets per beat for the whole piece only. Run the masking check by hand for melody-led beds (render the melody alone vs the rest, 500 Hz-4 kHz).
- Under about 22 s, First Light plays too fast and truncates (it needs a phrase-length form). Between 33 and 40 s it rings the tail longer.
- Meters are not ears. A PASS says the math is right, not that the music moves anyone. Listen to 8 seconds around the most important mood change before shipping.
