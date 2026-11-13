# Playbook: Lyric video

**Use when** the words are the picture: every sung line becomes a typographic scene, each word arriving on its sung
syllable, with a visual metaphor for its meaning. Typical for a release-week video before or beside the full clip.
**Not when** the picture tells a story and words are optional (`music-video.md`), the album forbids text on screen
(then `.srt` + `visualizer-loop.md`), or there is no vocal.

## Inputs to collect

- Master audio and the **real lyrics** (streaming text, with structure tags); language and script (RTL?).
- Fonts the person or brand owns, or OFL fonts (licence files go in the project); the hook line(s).
- Owner's taste / album look; which words must never be shown (explicit, names under name_exposure).
- Platforms: YouTube 16:9, plus 9:16 for Shorts/Reels?

## Defaults

| Item | Default |
|---|---|
| Length | the full song |
| Aspect / size | 16:9 1920×1080; 9:16 recompose if ordered (`social-vertical.md`) |
| fps | 30 (60 for fast kinetic styles); master with `SUB=8` subframe blur where type flies (`references/pipeline.md`, Export) |
| Medium | canvas: `bash <studio>/tools/new-project.sh <dir> --medium canvas --duration <s> --bpm <n>` |
| Style candidates | `references/styles/kinetic-lyric.md` (default), `title-sequence.md` (anthem, hard-cut colour worlds), `ascii-terminal.md`, `monochrome-launch.md`, `riso-pop.md` (printed matter), `sketchbook.md` (handwritten lines that write themselves) |

## Phase deltas

| # | Phase | What changes |
|---|---|---|
| 3 | Pitch | per line: key word(s), meaning, one metaphor (word rides a curve, rolls on a counter, mirrors for an opposite). Two contrasting worlds named (e.g. black + one hot accent; paper "document" world). |
| 4 | Map | **word-level and syllable-level precision is the product.** `bash <studio>/bin/studio songmap song.wav --lyrics lyrics.txt`; inspect every line's alignment; re-align lines the aligner garbles from the vocal stem alone. Every word: start, stressed syllable, end. |
| 5 | Storyboard | one row per line: time, scene, metaphor, key word + stress time, type mode (slam / karaoke / roll / handwritten), transition. |
| 6 | Test section | the first chorus (15–30 s): it fixes type system, sizes at 360 px and the hook treatment. |
| 7 | Build | the film reads a `LYRICS` array `{t0, t1, text, key, scene}` generated from `SONG.line(i)`; never hand-typed times. |
| 11 | Deliver | + `.srt` (the same text, for accessibility), + chorus cut. |

## Team & fan-out

Producer, director, songmap-analyst (critical), critic, art-director (type system), animators, integrator,
qa-operator, reviewer, copywriter. No sound role unless SFX are wanted (rarely: the song is the sound).
Chapters: one per section, 20–45 s each; ≤ 2 animators at once; the type system (`lib/type.js`: faces, sizes,
lit/cool colours, entry moves) is owned by the art director and read-only for animators.

## Craft rules specific to this type

1. **Each word arrives when it is sung** (`SONG.word(t)`), lit, then cools; no word sits half-lit
   (`references/words.md`). Impacts on the stressed syllable.
2. **Show short lines whole:** up to ~7 words on screen in full, 2–3 big rows, key words lit. Fragments mean
   nothing to someone who does not know the song.
3. **Sizes at 1080p:** lead-in rows 75–85 px, the point row ≥ 100 px, nothing to be read under ~70 px; hero type
   ≥ 90 px. Readable at 360 px wide (`text-audit.mjs` measures that).
4. **Hold a finished line ≥ 1.2 s**; reading time ≈ 0.3 s/word + 0.5 s (`references/timing.md`).
5. **Hooks slam, verses run as a karaoke strip** — never both for one line (`references/music-video.md`).
6. **The chorus word escalates** each return: bigger treatment, new metaphor, new colour world.
7. **Text never moves while it is read** except a slow creep; motion happens on entry and exit (springs: `heavy`
   for hero type, `snappy` for small labels; never linear).
8. One kind of move per sentence; words stay where they land (`references/words.md`, the stacked first line).
9. Words that land whole on a beat are pops for the gate: give each a 3–4 frame fade, declare only the real hits.
10. RTL: `ctx.direction = 'rtl'`, reading order right to left, final letter forms checked on every frame.
11. Two worlds alternate for rhythm; the bridge strips to one word on a plain ground.

## Gates & bar

- Battery + **`text-audit.mjs` must be clean of FAIL** (SMALL, FLASH, OVERLAP, BROKEN, EDGE); WARNs explained.
- Lyric diff: every on-screen line equals the streaming lyrics (spelling, order, no missing line); script it from
  `text-audit.mjs --json text.json` against `lyrics.txt`.
- Sync spot check: strips (`node <studio>/tools/render.mjs --strip=a:b`) around 10 random words; word lit within
  ±1 frame of its stress.
- Flash test (hard): colour-world hard cuts and glitch slices count as flashes.
- **Reviewer locked items:** the lyrics, the fonts if brand-owned, the song.
- **8/10 here:** readability 8+ at 360 px muted; every chorus return visibly bigger; no line on screen a beat early
  or late; variety: a new metaphor or layout every 2–4 s.

## Pitfalls

- Karaoke boxes and words sliding while being read are on the default-look ban list (`references/directed-look.md`).
- Whisper text instead of the real lyrics (it mishears sung words).
- Two big lines rolling at once print over each other for a few frames at the band seam.
- A long line squeezed small to fit: break it into rows instead.
- A name or explicit word that the brief forbids reaching the screen through an unreviewed line.

## Deliverables

`out/<name>-lyric.mp4` (and `-9x16.mp4` if ordered), `<name>.srt`, chorus cut, `POSTS.md`, gate report with text
audit and lyric diff, review room on the cut.

## Checklist

- [ ] Streaming lyrics in `lyrics.txt`; RTL/fonts settled, licences in project
- [ ] Song map with stress times; every line inspected
- [ ] Line table: key word, metaphor, type mode
- [ ] Chorus test section approved at 360 px
- [ ] `text-audit` FAIL-free; lyric diff zero
- [ ] Flash test PASS; reviewer ≥ 8 or 3 rounds
- [ ] `.srt`, chorus cut, posts delivered
