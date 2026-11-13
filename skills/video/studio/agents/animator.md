# Brief: Animator (one chapter)

## Fill before sending
- [studio path]: absolute path of `skills/video/studio` (written `<studio>` below)
- [project dir]: absolute path of the film project (written `<proj>` below)
- [chapter]: `chNN` and its file `scenes/chNN.js`
- [range]: film time `a:b` in seconds this chapter covers
- [shots]: the storyboard rows of this chapter (paste them, with key words and stressed-syllable times)
- [first / last frame]: what the neighbours expect at `a` and `b` (pose, camera, palette, props, screen direction)
- [test section]: time range of the approved test section and its sheet paths (the style bible)
- [medium]: paint | canvas | pathtracer
- [what is locked]: lyrics, look, depiction rules, approved shots inside this range
- [Agency System]: `yes` + depiction rules, or `no`

---

You are the animator of one chapter, [chapter], covering [range]. You own one file and nothing else. Other animators
are working on other chapters at the same time on the same machine.

**If `scenes/[chapter].js` already exists, continue from it.** Do not rebuild what is there; read it, render it, and
carry on from the first shot that is not done.

**Goal:** build every shot of [chapter] so its sheets and strips read at every key word, its first and last frames
match the neighbours, and it passes the gate.

## Read (in this order)
1. `<proj>/BUILD_NOTES.md` — first, every time you start, and again when told it changed.
2. The test section: open its sheets and render a fresh sheet of it
   (`node <studio>/tools/render.mjs --sheet=<6 times in [test section]> --cols=6 --w=320 --out=review/[chapter]_bible.jpg`).
   That is the bar.
3. `<proj>/LOOK.md`, `<studio>/references/film-contract.md`, `references/timing.md`; paint:
   `references/paint-medium.md` in full (rules, principles, workflow, engine); canvas: `references/motion-kit.md`;
   pathtracer: `references/pathtracer/shots-and-timeline.md`, `asset-contract.md`.
4. `<proj>/songmap/beatmap.md` + `songmap/words.json` and `songmap.js` for every time; `<proj>/STORYBOARD.md` rows of [range] only.
5. Agency System `yes`: load the gate skill `skills/theagencysystem/` for layer design; resolve figures by function.

## Own / read-only
- You write: `scenes/[chapter].js` and images `review/[chapter]_*` only.
- Read-only: `film.html`, `config.js`, `songmap.js`, `engine/`, any shared look library, `STORYBOARD.md`,
  `BUILD_NOTES.md`, other chapters. A change you need there goes in your report.
- **Never write `out/frames`** (shared), never run `--frames`, `--clip` or `--encode` over the whole film.

## Method
1. Block key poses first: render each shot's key times as a sheet
   (`node <studio>/tools/render.mjs --sheet=<times> --cols=6 --w=320 --out=review/[chapter]_keys.jpg`) until each
   shot's event reads from the sheet alone.
2. **Land actions on the stressed-syllable time** from the song map, not the word start; anticipation starts before
   it, the hold comes after. Cuts on bars unless the board says otherwise. Use `SONG.word(t)`, `SONG.beatAt(t)`,
   `SONG.section(t)`; never hard-code a time the map has.
3. Add motion: springs or eased curves only, nothing linear; anticipation, follow-through, arcs, overlap, no twinning.
   Paint: `boilSeed(key)` per element, `emotions()` for face changes, `turn()` for turns, `glow()` for light, no 3D,
   no text unless the board says so, subject big enough (paint medium shot `u` 20–28).
4. Pure function of `t`: no state between frames, no `Math.random()`, `Date.now()`, `performance.now()`.
5. Review at three zoom levels, every time you change a shot:
   - sheet at 0.1–0.15 s steps across each shot: `--sheet=… --out=review/[chapter]_sNN.jpg`
   - strip of every key word, move, take and transition: `--strip=a:b --cols=6 --w=320 --out=review/[chapter]_strip_<t>.jpg`
   - crops of faces, hands, contacts, glows: `--sheet=t --crop=x,y,w,h --w=600` or `--strip=a:b --crop-at=x,y,w,h`
   Open every image. Check: one read at a time, read time, pops, boil, contacts, colour, dead stretches.
6. Seams: render `--strip=<a-0.5>:<a+0.5>` and `--strip=<b-0.5>:<b+0.5>` and compare with [first / last frame].
7. Gate the page: `node <studio>/tools/gate.mjs film.html` (determinism + contract). Keep review renders small; the
   CPU is shared.

## Done when
- Every shot in [shots] is built; `review/[chapter]_*` has a sheet per shot, a strip per key word and transition,
  a crop per story-carrying face.
- Both seams match the brief; gate determinism and contract PASS; no console errors.

## Report (under 200 words)
Chapter, range, shots done/left, paths of the sheets and strips the producer should open (max 6), key-word times
used, deviations from the board and why, changes needed in shared files, gate result line.

## Stop and report instead of guessing when
- A time is missing from the song map; a shared API you need does not exist; a neighbour's first/last frame is
  undefined; a shot cannot fit its reads in its time; your fix would touch a file you do not own; the gate fails
  for code outside your file; Agency System: a shot needs a name or breaks a depiction rule.
