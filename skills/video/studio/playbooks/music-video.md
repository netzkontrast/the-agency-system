# Playbook: Music video

**Use when** a finished song (often a Suno track) gets a full-length clip timed to its words and bars: a story, a
symbolic world or a character acting the lyric. **Not when** the words themselves are the picture (`lyric-video.md`),
the picture only breathes with the audio (`visualizer-loop.md`), every track of an album shares one world
(`album-suite.md` wraps this playbook), or only a 15–30 s cut is wanted (`teaser-cutdown.md`).

## Inputs to collect

- The master audio (WAV preferred; MP3 ≥ 256 kbps) and its exact length. Never cut from a preview stream.
- **The real lyrics** with structure tags ([Verse], [Chorus], [Bridge]): the person's text or the streaming lyrics.
  Never the phonetic text from a Suno lyrics box (`SKILL.md`, Map).
- Owner's taste: `TASTE.md`, the album's `VIDEO-CONCEPT.md`, or a reference clip; depiction rules that are locked.
- Where it posts (YouTube 16:9, plus a 9:16 short?), whether a social cut is wanted, a deadline, the render machine
  (GPU Mac / NVIDIA / cloud container without GPU).
- Lyrics on screen: none, `.srt` only, soft captions, or painted hook words (decide at the pitch, below).

## Defaults

| Item | Default |
|---|---|
| Length | the song, unedited (3:00–5:30); trim only a dead lead-in (`SONG_IN` offset, `references/audio.md`) |
| Aspect / size | 16:9, 1920×1080; vertical short planned from day one (`references/vertical.md`) |
| fps | 24, art on twos (`FILM_STEP = 12`, render with `--twos`) |
| Medium | paint: `bash <studio>/tools/new-project.sh <dir> --medium paint --duration <s> --bpm <n>` |
| Style candidates | `references/styles/painterly-glow.md` (symbolic, emotional), `watercolor.md` (character story), `ink-wash.md` (sparse, melancholic), `riso-pop.md` (satire, one gag per line), `sketchbook.md` / `crayon-storybook.md` (intimate), `paper-cutout.md`, `teaching-song.md` (the song explains something), `kinetic-lyric.md` (only if the pitch turns into a lyric video) |

Render-time estimate for the first reply: drawings = seconds × 24 (× 0.5 on twos) × measured s/drawing. Measure
s/drawing on the test section, quote ranges until then: ≈ 1.5 s/frame wall-clock with ~10 workers on a 12-core Mac
(a 3:30 song ≈ 2.1 h, ≈ 1.1 h on twos); 20–30 s/frame in a GPU-less container (≈ 28–42 h: build and review there,
master elsewhere). Token budget: several times the 0.4–0.7 M of a 30 s film; say the number before starting.

## Phase deltas

| # | Phase | What changes for a music video |
|---|---|---|
| 1 | Brief | short: audience, platform, lyric-on-screen decision, locked depiction rules. No claims check. |
| 3 | Pitch | one arc for the whole song (e.g. dawn → stars), the bridge as the turn, the ending rhyming with frame 0; the chorus escalation plan in one line per chorus. Concept check steps 1, 3, 5, 6 only (`references/concept-check.md`). |
| 4 | Map | **mandatory, before any storyboard timing.** `bash <studio>/bin/studio songmap song.wav --lyrics lyrics.txt` → stem separation, `tools/audio/beatmap.py` (bars, sections, drop), `tools/audio/align_lyrics.py` (forced alignment of the known lyrics), `tools/audio/songmap_js.py` → `songmap.js`. Check tempo drift (`references/audio.md`, "A song whose tempo drifts"). |
| 5 | Storyboard | one row per lyric line, grouped by section: time, image, key word + its **stressed-syllable** time, reads, transition, chapter. Drawn sheet: `bash <studio>/tools/storyboard-sheet.sh`. |
| 6 | Test section | 30–45 s, usually verse 1 + chorus 1; it becomes the style bible. Measure render speed here. |
| 7 | Build | chapters per section group (below); every action word's time copied into each animator brief. |
| 11 | Deliver | + 15–30 s chorus cut (`teaser-cutdown.md`), + share copy (CRF 24), + `.srt` if chosen. |

No phase is skipped. Phase 9 always asks the reviewer for the 10-second map (song > 60 s).

## Team & fan-out

Producer, director, **songmap-analyst** (always), critic, art-director, animators, integrator, qa-operator, reviewer,
copywriter; sound only if the mix needs work beyond loudness; vertical-editor if a 9:16 short is ordered.

- **Chapter split rule:** one chapter per section group, cut on a bar line at a section start: intro+V1 · PC+C1 ·
  V2 · C2 · bridge · final chorus+outro. A 3:30 song gives 5–7 chapters of 25–50 s. Never split inside a line.
- Each chapter's first and last frame are drawn in `STORYBOARD.md` so neighbours match.
- **≤ 2 animators at once** (usage ran out overnight with five). Pre-register every `scenes/chNN.js` stub first.
- The art director builds the shared library (palette, recurring motif objects, character model sheets as `LOOPS`)
  before the second animator starts.

## Craft rules specific to this type

1. **Land hits on the stressed syllable**, not the word start (Hebrew final stress came 0.3–0.45 s late; hits
   landed 7–11 frames early). `words.json` carries both; start = anticipation, stress = impact.
2. Every line gets an image that carries its meaning *at the moment it is sung*; write the key word per row.
3. **Verses intimate** (close, still), **choruses open** (wider, moving, light), **the bridge strips down**.
4. **Chorus escalation:** the same words over images that grow (hope → attempt → true). A returning chorus never
   reuses its pictures (`plate-audit` REPEAT); one round of reused chorus pictures cost most of a point.
5. **Spend the strongest picture at its place.** Shown early, it empties the later payoff.
6. Cuts on bars (`SONG.downbeat(n)`), big turns on lyric turns, holds while the voice holds; beat punches only in
   loud sections (`SONG.pulse(t)`, `references/motion-kit.md`: +0.012/beat, +0.03/bar after `SONG.hit('drop')`).
7. Counterpoint sometimes beats literal: brave words over a small, shaky real step.
8. One motif with setup and payoff (a line of light, a closed window); first frame ↔ last frame rhyme.
9. **Lyrics on screen, decide once:** (a) none, acted (the paint medium's default: `references/paint-medium.md`
   rule 2); (b) **`.srt` only**, `bash <studio>/bin/studio srt` (`tools/audio/srt.py`) — the safe default for
   painted films; (c) soft captions on a canvas layer above the paint, each word on its `SONG.word(t)` time;
   (d) painted hook words only. Hooks slam, verses run as karaoke — **never both for the same line**. RTL needs
   `direction = 'rtl'` and a font with the script.
10. Story clock or progress motif (00 → 08 of 08) gives a long clip a spine.

## Gates & bar

- Standard battery: `bash <studio>/bin/studio gate <dir>`; plus `bash <studio>/bin/studio flash out/cut.mp4`
  (hard) and `bash <studio>/bin/studio loudness out/cut.mp4` — but the song's own master is never re-limited;
  only check it sits ≤ −1 dBTP after mux.
- **Map gate:** `songmap.js` length = master length ± 1 frame; spot-check 5 stressed syllables by strip
  (`node <studio>/tools/render.mjs --strip=a:b`) against the vocal energy.
- `plate-audit.mjs` on any film with plates: no REPEAT across choruses, no HOLD ≥ 8 s.
- **Reviewer locked items:** the song, the lyrics, the route (painted, so figures are stylized), album depiction
  rules. Sound-sync axis judged from the word list with times in `WORDS-AND-SOUND.md`.
- **8/10 here:** every chorus has a new escalating image; every key word lands within ±1 frame of its stress; no
  10-second block below 7 on the map; the bridge is visibly the turn; the story reads muted.

## Pitfalls

- Whisper text for sung words (it mishears and drops lines): text always from the real lyrics, times from alignment.
- A bare beat grid on a drifting song: a third of a beat off by 32 s.
- Pictures that flash by while a chat or screen must be read (`references/before-the-first-cut.md` §5).
- Big lyric bands competing with the picture: big type is for the hook only.
- Two sessions directing the same film overwrite `cast.js`/`film.html`: one owner per film.
- Animators writing `out/frames` (shared); they render only `review/chNN_*`.
- Trusting a cloud-container render ETA for the master.

## Deliverables

`out/<name>.mp4` (1080p24, song muxed), `-v2`… per notes round; `<name>-share.mp4` (CRF 24); chorus cut
15–30 s; optional 9:16 short; `<name>.srt` if chosen; `POSTS.md`; `songmap/` and `songmap.js`; `STORYBOARD.md`;
`review/gate-N.md`, `review/review-N.md`; delivery note (shot list per section, score, known flaws, what was
hand-tweaked); review room opened on the cut.

## Checklist

- [ ] Real lyrics in hand; streaming text, not phonetic
- [ ] Song map built; length ± 1 frame; tempo drift checked
- [ ] Lyrics-on-screen decision written in `BUILD_NOTES.md`
- [ ] Storyboard per line with key word + stress time; critic clean
- [ ] Chorus escalation table filled (one new image per return)
- [ ] Test section 30–45 s approved; s/frame measured; ETA told
- [ ] Chapters pre-registered; ≤ 2 animators at once
- [ ] Gate + flash + plate audit PASS; reviewer ≥ 8 or 3 rounds
- [ ] Master, share copy, chorus cut, `.srt`, `POSTS.md`, room open
