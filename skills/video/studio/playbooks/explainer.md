# Playbook: Explainer

**Use when** one idea, one mechanism or one feature must be understood in 15–60 s (teaching pieces up to ~100 s):
how a thing works, why it matters, what changes. **Not when** the film launches a product with real captures
(`product-launch.md`), the subject is a true story from sources (`documentary.md`), the numbers are the story
(`data-story.md`), or a song carries the teaching (`music-video.md` with `references/styles/teaching-song.md`).

## Inputs to collect

- The one takeaway in one sentence, the audience, where it posts, how long they will watch.
- The person's own words, script or notes; the facts and numbers with their sources (no invented claims).
- Voice or no voice (`references/voice.md`; a voice costs credits — price first); music (code bed by default).
- Brand pack if a brand appears (`references/brand-pass.md`, `references/brand-brief.md`).
- What a muted viewer must still get.

## Defaults

| Item | Default |
|---|---|
| Length | 15–30 s feed, 30–60 s landing page, up to ~100 s for a teaching piece (`references/formats.md`, length exception) |
| Aspect / size | 16:9 1920×1080; 9:16 or 4:5 recompose if ordered |
| fps | 60 for kinetic type and UI, master with `SUB=8`; 24 for paint |
| Medium | canvas: `bash <studio>/tools/new-project.sh <dir> --medium canvas --duration 30` |
| Style candidates | `references/styles/explainer.md` (default), `dark-premium.md` (serious B2B), `manifesto.md` (60–90 s statement), `sketchbook.md` / `paper-cutout.md` / `crayon-storybook.md` (warm, hand-made), `ascii-terminal.md` (developer audience), `pencil-test.md` (explain a motion) |
| Sound | code bed `node <studio>/tools/music.mjs render <piece.mjs> --seconds <s>`, SFX `node <studio>/tools/sfx.mjs mix plan.json bed.wav mixed.wav` |

## Phase deltas

| # | Phase | What changes |
|---|---|---|
| 1 | Brief | the strategist writes the takeaway and **claims check**: every fact sourced or marked as the person's. |
| 3 | Pitch | run `references/concept-check.md` in full and `references/page-or-picture.md`: mark each shot P/G and E/S; more than a third pages or states → change the board before building. Words written and counted first (≈ 2 words/s). Pick a way to explain from `references/directed-look.md` and say why. |
| 4 | Map | the **voice script** is the map: record or draft VO, then `python3 <studio>/tools/vo.py vo.json` → `audio/vo.wav` + `assets/vo.js` line starts. Without voice, the word timing from `references/timing.md` is the map. Music bed fitted after the picture timing. |
| 5 | Storyboard | one row per read: time, event, the reads in order, the on-screen words, carrier element into the next shot. |
| 6 | Test section | the hook plus the first mechanism beat (8–12 s). |
| 7 | Build | 30 s → 1 animator; 60–100 s → 2–4 chapters by idea step. |

## Team & fan-out

Producer, strategist, director, critic, art-director, 1–2 animators, integrator, qa-operator, reviewer, copywriter;
sound when there is VO or SFX. Chapters per idea step (problem · mechanism · result · end), each starts on a shared
element carried from the last.

## Craft rules specific to this type

1. **One read at a time;** cause, then reaction. Fast actions, slow meanings (`references/timing.md`).
2. **A process is one object that changes,** not N matching frames: a list that gains and loses parts, one word
   naming each step (`references/directed-look.md`, "Nobody lists").
3. **Every shot an event**, not a state ("it sorts the pile", not "a sorted pile").
4. **Ban the default look by name** at the top of `film.html`: soft-shadow cards, pills with numbers, icon grids,
   gradient clouds, everything popping with overshoot (`references/directed-look.md` §1); replace adjectives with
   numbers (§3).
5. On-screen words: 2–5 at a time, large, no full stops; key words when spoken and shown; every stretch with a voice
   has words (`references/words.md`).
6. **Text timing:** 0.3 s/word + 0.5 s, minimum 1.2 s for anything that must be read.
7. **Springs by role** (`references/timing.md`): `snappy` UI, `camera` panels, `heavy` hero type; zooms in log space;
   every handoff names its carrier or is a declared hard cut (`references/motion-kit.md`).
8. **First second:** frame 0 striking and the premise up by ~0.8 s; last read held 2–3 s.
9. After an aside, name the subject again; "that" for the thing shown, "this" for the film.
10. Example figures carry a visible "Example data" label (readable at 360 px).

## Gates & bar

- Battery + `text-audit.mjs` (FAIL-free) + `edge-audit.mjs`; `audio-check.mjs out/cut.mp4 --stems vo.wav bed.wav`
  when voiced (voice ≥ 3 dB over the rest in 500 Hz–4 kHz for ≥ 80 % of active seconds); transcribe the final mix
  and compare every line (`references/voice.md` §19).
- Page-or-picture count re-done on the stills; written in `review/gate-N.md`.
- **Reviewer locked items:** the takeaway, brand look, the person's own words.
- **8/10 here:** a stranger retells the idea correctly in one sentence after one muted viewing; no layout returns
  more than twice in a row; every number sourced or labelled.

## Pitfalls

- Twelve items in twelve identical panels (the pattern viewers named "every AI video").
- Restyling the same skeleton (paper desk, lit 3D stage) instead of changing what is shown.
- A sag in the middle: same-shaped sentences in a row; merge them.
- VO cut at whisper word times, chopping words; use `tools/vo.py` and transcribe every placed line.
- A sound under every visual event under a narrator (bells, tick runs): keep only pressed/typed/moved sounds.

## Deliverables

`out/<name>.mp4` (+ `-9x16` / `-4x5` if ordered), `<name>.srt` when voiced, `POSTS.md`, script with sources, gate
report, reviewer score, review room on the cut.

## Checklist

- [ ] Takeaway in one sentence; claims sourced
- [ ] Concept check + page-or-picture counts in the pitch
- [ ] Words written and timed before the board
- [ ] Ban list at the top of `film.html`
- [ ] VO placed with `tools/vo.py`; final mix transcribed
- [ ] text/edge audits clean; gate PASS; reviewer ≥ 8
