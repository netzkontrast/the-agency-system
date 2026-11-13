# Playbook: Social vertical

**Use when** the delivery is a 9:16 (Reels, TikTok, Shorts) or 4:5 (feed) film: an original made tall, or a recompose
of a wide film. Hooks in the first second, safe areas, captions. **Not when** the job is only to pick the best 15–30 s
of a finished film without relayout (`teaser-cutdown.md`; it hands over here for the tall version), or the vertical is
a Spotify Canvas loop (`visualizer-loop.md`).

## Inputs to collect

- Source: a finished wide film and its `film.html` (recompose), or a brief for a tall original.
- Platform list: Reels, TikTok, Shorts (9:16), feed (4:5); sound-on or muted-first; posting account's caption style.
- The hook sentence (news and a gain, not a riddle), the one ask if any.
- Captions: burned in, `.srt` upload, or both; language(s).
- Reels on the same subject that got many views: look at 3–5 before planning (`references/vertical.md`, the light stage).

## Defaults

| Item | Default |
|---|---|
| Length | 15–45 s (Reels/TikTok), ≤ 60 s Shorts; same timing as the wide film when recomposing |
| Size | 9:16 1080×1920 (`--aspect=9:16`); 4:5 1080×1350 (`--aspect=4:5`) |
| fps | as the master; plus a 30 fps copy for Instagram |
| Medium | the source film's medium; tall originals in canvas |
| Safe area (9:16) | essentials in x 56–940, y 250–1480; nothing right of x 940 below y ~880 (app buttons); the middle 4:5 holds the feed preview (keep key words below y 285) |
| Style candidates | as the source film; for originals `references/styles/explainer.md`, `editorial-hud.md`, `riso-pop.md`, `kinetic-lyric.md` |

## Phase deltas

| # | Phase | What changes |
|---|---|---|
| 1 | Brief | platform specs, captions decision, competitor Reels studied (contact sheets with `bash <studio>/tools/contact-sheet.sh <video>`). |
| 3 | Pitch | say the ceiling: a restacked tall cut with a wide opening tops out at ~7; price a tall-made first shot to reach 8. |
| 5 | Storyboard | one tall layout per shot (not per film): where the subject sits, where the words sit, what moves. |
| 6 | Test section | first 3 s + the densest word shot, checked on a phone-size sheet. |
| 7 | Build | recompose in the same `film.html`: every layout number through `PV(landscape, vertical)`; checksum ~30 wide frames before and after to prove the master did not change. |
| 11 | Deliver | 9:16 + 4:5 + 30 fps copy + cover frame + `.srt`. |

## Team & fan-out

Vertical-editor (owner of the tall layouts), producer, copywriter (captions, hook line, posts), qa-operator, reviewer;
director and critic only for tall originals. One agent per film; the tall cut is not split into chapters unless > 60 s.

## Craft rules specific to this type

1. **Recompose, never crop:** a centre crop loses the subject and buries type under the UI (`references/vertical.md`).
   Same shot list, same timings, per-shot focal x for photos, textures sized to the tall frame.
2. **The first second:** the made thing fills the frame from frame 0 with the first words on it; the hook sentence is
   up by 0.8 s; then step back into the layout on the first beat.
3. **Type:** 2 lines at 92 px beat 1 line at 75 px in an 884 px column; line changes are out-then-in (old out in
   0.09 s, then new rises), never two lines rolling at once.
4. **Faces:** free space is above the head or below the chin; nothing solid on a face (`audit-faces.mjs` in 9:16 and
   again in 16:9 if shared code changed).
5. **Captions:** spoken words a few at a time, the word being said highlighted; time words per sentence cut at
   pauses (whole-take times drift up to 0.5 s). Burned captions inside the safe area; `.srt` always delivered too.
6. **Wide material in a tall frame:** three 608 px bands, or one large card (952×1000 from 1076-high clips is sharp
   and takes 46 % of the screen); words on a card, not on moving pictures.
7. **Never show a shot twice;** count footage against seconds before laying out.
8. **The ask** early on its own card and kept on screen during the reveal; one ask only.
9. **Instagram:** 30 fps copy; cover = first frame with its words inside the middle 3:4; tick the AI label when people
   look real.
10. A strip that holds still beside a still card fails the dead-air gate: give every strip a slow creep.

## Gates & bar

- Battery on the tall render; `text-audit.mjs` (measures on a 360 px-wide phone); `edge-audit.mjs`;
  `audit-faces.mjs` per aspect.
- **Safe-area check:** the rightmost pixel of every low line < x 940; a still of each shot with the platform UI
  overlay mask.
- Wide master unchanged: checksums of ~30 frames identical after the recompose.
- Sample the exported MP4 itself (one frame every 2 s) before delivering.
- **Reviewer locked items:** the source film's look and words.
- **8/10 here:** hook clear at 1 s muted, nothing under the app UI, every word readable at phone size, the subject
  (product, face) never cut by the frame or covered by buttons.

## Pitfalls

- The subject of the first shot under the right-hand buttons (scale it to end left of x 925, above y 1470).
- A player-inside-a-player label from an inner film (crop into the inner player).
- A word's tail on a pale part of the picture: deepen the fade (alpha ~0.93 in the first 120 px).
- Text audit verdicts trusted for words inside pictures (it cannot see them).
- A viral-score tool used as a judge.

## Deliverables

`out/<name>-9x16.mp4`, `out/<name>-4x5.mp4`, `out/<name>-9x16-30fps.mp4`, cover PNG, `<name>.srt`, `POSTS.md` per
platform, wide-master checksum proof, gate report per aspect.

## Checklist

- [ ] Winning Reels on the subject studied
- [ ] Ceiling and price of a tall first shot said
- [ ] `PV()` recompose; wide checksums unchanged
- [ ] Hook up by 0.8 s; first frame has words
- [ ] Safe area + face audit per aspect
- [ ] Captions burned and `.srt`; 30 fps copy; cover frame
