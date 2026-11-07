# Playbook: Brand sting and title sequence

**Use when** the film is a mark, a name or a line-up made to move: a 3–8 s logo sting, a 15–40 s title sequence for
a show, season, festival or event opener, a line-up of speakers or features, a channel intro. **Not when** the
product must be shown working (`product-launch.md`), an idea must be explained (`explainer.md`), or a song carries a
full story (`music-video.md`).

## Inputs to collect

- The mark: logo as vector paths (from the brand's site DOM or the official file), the wordmark font file, colours
  computed from the live site (`references/brand.md`, `references/brand-pass.md`).
- The names in the line-up, exactly spelled, in the approved order; permission for any third-party mark.
- Where it plays: before videos (sting), a stage screen (size, aspect, loop?), a stream overlay, a feed.
- Music: a given track (measure it), a code sting (`tools/music.mjs`), or silence + SFX.

## Defaults

| Item | Sting | Title sequence / opener |
|---|---|---|
| Length | 3–8 s (end on the mark, ≥ 1.5 s hold) | 15–40 s; 2–4 subjects × 4–6 s + title in and out |
| Aspect / size | 16:9 1920×1080; 1:1 and 9:16 versions | as the screen; stage screens often 32:9 or custom `--size=WxH` |
| fps | 60, master `SUB=8` | 60, master `SUB=8` |
| Medium | canvas (`--medium canvas`) | canvas |

Style candidates: `references/styles/title-sequence.md` (default for openers), `chrome-showreel.md`,
`monochrome-launch.md`, `riso-pop.md`, `pixel-art.md`, `paper-cutout.md`, `ink-wash.md` (a seal and brush mark).

## Phase deltas

| # | Phase | What changes |
|---|---|---|
| 1 | Brief | brand pack and tokens file are the brief; claims check is about names and marks (permission). |
| 3 | Pitch | sting: 2–3 ideas, each one sentence ("the dot becomes the i"). Opener: chapter list subject × colour world × signature visual. The one image each idea ends on. |
| 4 | Map | **BPM first:** `python3 <studio>/tools/audio/beatmap.py track.wav` (or the BPM the code sting is fitted to, `node <studio>/tools/music.mjs render <piece.mjs> --seconds <s>` prints it). Every cut, flap lock and slam is a beat index. |
| 5 | Storyboard | per beat, not per second: bar/beat → event → type state. |
| 6 | Test section | the end frame (the mark at rest) plus its 2 s lead-in; then one full chapter. |
| 7 | Build | stings: 1 animator; openers: 1 per 2 subjects, ≤ 2 at once. |
| 9 | Review | for a sting under 10 s the 10-second map is not needed; the reviewer judges frame 0, the arrival and the hold. |

## Team & fan-out

Producer, strategist (only for openers with many names), director, critic, art-director (tokens + type system),
1–2 animators, qa-operator, reviewer, sound (stings usually need a designed hit), copywriter (posts for the opener).

## Craft rules specific to this type

1. **The mark is drawn from its real vector paths**, never redrawn by eye or by an image model; stand-ins (wordmark
   set in the brand font) labelled and swapped before wide release.
2. **One carrier element** across the whole sting (a dot, a stroke, a coin) that ends as part of the mark: the
   throughline object (`references/formats.md`, `references/motion-kit.md` shared elements).
3. **Beat-locked type:** 140–160 BPM feels right for openers; bars of 1.5–1.7 s; flaps lock on the 1 (`SONG.beatAt(t)`,
   `SONG.downbeat(n)`); compute every beat from time and round each, never add rounded counts (drift).
4. **Weight:** hero type and logo on the `heavy` spring (~0.8 s, no overshoot); playful marks may use `playful`;
   opacity and colour never bounce (`references/directed-look.md` §3).
5. One colour world per chapter, hard-cut between them, one accent each (`title-sequence.md`); the finale slows and
   holds.
6. **The last hold:** sting ends ≥ 1.5 s on the mark at rest; an opener ends 2–3 s on the title.
7. Every flash/strobe on a cut counts towards the flash limit; glitch slices on large areas are flashes.
8. Real third-party names or marks only with permission or clear editorial use; no fake co-marks.
9. One hit sound per arrival, landing one frame after its picture; one riser + one impact per film (`tools/sfx.mjs`
   taste rules).

## Gates & bar

- Battery; pops check declares every intentional cut (`--cuts`), everything else eased.
- Flash test (hard) — the most common FAIL for openers with hard-cut colour worlds.
- Mark fidelity: a still of the end frame overlaid on the official logo at 100 %; zero visible drift.
- `text-audit.mjs`: names readable at 360 px; no OVERLAP from marquee type behind hero type.
- **Reviewer locked items:** the mark, colours, names and order.
- **8/10 here:** frame 0 already striking; the mark arrives on a measured beat; the end frame works as a still
  (thumbnail); someone who saw it once can describe the move.

## Pitfalls

- A logo drawn by an image model or retraced by eye.
- Everything arriving at once with overshoot (default look).
- Zoom in straight into zoom out (camera wobble); linear zooms (use log space).
- A sting that ends on the last motion frame: no hold, the mark is never seen.
- Stage screens at non-standard size rendered at 16:9 and stretched.

## Deliverables

Sting: `out/<brand>-sting.mp4` in 16:9, 1:1, 9:16 (+ a lossless PNG sequence via `--frames --png` when it goes
over other footage; check that the page really draws a transparent ground before promising alpha), audio and silent
versions. Opener: master + versions per screen, `POSTS.md`.
Tokens file, gate and review reports.

## Checklist

- [ ] Real vector mark + font file + computed colours in tokens
- [ ] Permissions for third-party names/marks
- [ ] BPM measured; every event a beat index
- [ ] End frame approved first
- [ ] Flash test PASS; mark overlay exact
- [ ] All ratios and alpha version delivered
