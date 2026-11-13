# Playbook: Animated short

**Use when** a character carries a wordless or lightly worded story, 30 s–3 min: a ritual, a turn, a payoff; a mascot
film; a story clip without a song to follow. **Not when** the story is timed to a sung lyric (`music-video.md`), the
look must be physically lit 3D (`pathtraced-short.md`), or the film explains a product (`explainer.md`).

## Inputs to collect

- The premise or the person's story; who the character is (an existing mascot, the person themselves, or new).
- Character references (drawings, photos with permission), what must stay on-model, what is off-limits.
- Length, platform, whether any words may appear (title card only is the default).
- Music: a given track (measure it) or a code score fitted to the cut (`tools/music.mjs`).

## Defaults

| Item | Default |
|---|---|
| Length | 30–90 s for feeds; up to 3 min for a story with time passing |
| Aspect / size | 16:9 1920×1080; letterbox 2.39:1 inside for cinema feel; 1:1 or 9:16 if ordered |
| fps | 24, drawings on twos (`FILM_STEP = 12`, `--twos`) |
| Medium | paint with the character rig: `bash <studio>/tools/new-project.sh <dir> --medium paint --duration <s> --character` |
| Style candidates | `references/styles/animated-short.md` (structure and story craft), `watercolor.md`, `crayon-storybook.md`, `paper-cutout.md`, `pencil-test.md`, `pixel-art.md`, `sketchbook.md` |

## Phase deltas

| # | Phase | What changes |
|---|---|---|
| 3 | Pitch | logline ("___ wants ___, but ___, so ___"), the story in 5 sentences, one motif with setup and payoff, the final image rhyming with the first. Concept check steps 1, 3, 5, 6. **The checkpoint that matters most for this type.** |
| A | Character department | **after the pitch, before the storyboard is drawn:** rig, model sheet, pose library, motion tests. See craft rules 1–4. |
| 4 | Map | music bar map (`python3 <studio>/tools/audio/beatmap.py`) or none; for a code score, time the picture first and fit the music after (`references/music-engine.md`). |
| 5 | Storyboard | the paint storyboard format (`references/paint-medium.md`, Workflow §1): per shot the event, the character's reaction, the reads with start–end, transition in/out. Drawn sheet: `bash <studio>/tools/storyboard-sheet.sh`. |
| 6 | Test section | the hero shot (the turn or the payoff) fully built, plus one motion test strip per key action. |
| 7 | Build | chapters by story act (ritual · time passing · separation · turn · return · reversal). |

## Team & fan-out

Producer, director, critic, art-director (world, palette, model sheets), **one rig owner** (an animator role with the
character files), animators per act (≤ 2 at once), integrator, qa-operator, reviewer, sound (score + SFX on contacts).

- Freeze new rig option names in every brief before fan-out (`accessory:'…'`, `beard:0..1`); the rig owner may only
  ADD options and must prove the approved cast renders pixel-identical with defaults (`references/music-video.md`,
  parallel build lessons).
- Chapter animators never edit the rig file; they request options in `BUILD_NOTES.md`.

## Craft rules specific to this type

1. **Rig first:** silhouette readable at thumbnail size; on-model across ages and angles (same hair, one signature
   item); the drawn turn uses the medium's views, not 3D rotation (`references/paint-medium.md`, Views and turns).
2. **Pose library** as `LOOPS` (`?loop=emotions`, `?loop=views` pattern): neutral, the 4–6 emotions the story needs,
   the signature gesture; render each with `node <studio>/tools/render.mjs --sheet=… --query=loop=<name>`.
3. **Motion tests before scenes:** walk, the signature gesture, one take, one hold with breathing — each as a strip
   (`--strip=a:b`) read frame by frame for anticipation, follow-through, contacts.
4. **Character life** (`references/character-life.md`, helpers in `engine/lib/life.js`): blink on head turns, never
   on a timer (110/40/190 ms); eyes lead the head by ~0.1 s; limbs chained with `flow`, child parts `settle`; held
   objects drawn from the hand every frame; left and right never mirrored.
5. **Event in every shot; one read at a time;** reaction only after the viewer has seen the cause (the demo's ending
   table in `references/paint-medium.md`).
6. **Story reads without words.** If a beat needs a caption, redesign the beat. Title card at start and end only.
7. Time passing through physical marks (tally marks, seasons, wear), not text.
8. Transitions at every seam (brush wipe, iris); every shot paints the whole frame; `boilSeed(key)` per element.
9. Palette by emotion; light as the storytelling tool; the final image held 2–3 s.

## Gates & bar

- Battery with `FILM_STEP = 12` (holds on twos are the look, not dead air).
- **Character sheet gate** before the storyboard is drawn: model sheet + pose library + motion-test strips approved
  (by the person in stages; by you against `references/quality-checklist.md` "Nothing pulls the viewer out" on a run).
- Crops of every face that carries the story (`--crop`, `--crop-at`) at full size.
- **Reviewer locked items:** the character design, the wordless route, the story beats the person approved.
- **8/10 here:** the reviewer's one-sentence retelling matches the logline; no mannequin poses, no snapping faces;
  contacts hold (feet, hands); the motif changes meaning by the end.

## Pitfalls

- Building scenes before motion tests: every chapter then fixes the same walk.
- A tiny character in a big landscape for the whole film; timid poses.
- Both arms or several characters moving in sync; everything at one brisk speed.
- Re-boil jitter on still elements after a moving one (missing `boilSeed`).
- Changing the person's own likeness without a before/after strip and a backup.

## Deliverables

`out/<title>.mp4` (+ ratios if ordered), model sheet and pose-library renders, motion-test strips, `STORYBOARD.md`,
score/mix report, `POSTS.md`, gate and review reports, review room.

## Checklist

- [ ] Story in 5 sentences approved
- [ ] Rig + model sheet + pose library as loops
- [ ] Motion tests read frame by frame
- [ ] Storyboard with reads; critic clean
- [ ] Hero shot approved as style bible
- [ ] ≤ 2 animators; rig changes add-only, pixel-identical
- [ ] Gate PASS; reviewer ≥ 8 or 3 rounds
