# Playbook: Teaser and cut-down

**Use when** a finished (or approved) film needs a shorter version: a 15–30 s teaser for release week, a 6/15/30 s
ad set, a chorus cut of a music video, a trailer for a long piece. **Not when** there is no finished source yet (make
the film first with its playbook), or the short needs a tall relayout (do this cut first, then `social-vertical.md`).

## Inputs to collect

- The source cut (`out/<name>-vN.mp4`), its `film.html`, `songmap/` and `STORYBOARD.md`, the master audio.
- Target lengths and ratios, platforms, release date, the one action (pre-save link, premiere date) — only as given.
- Whether the voice or narrator must stay (ask; never drop it silently).
- The owner's favourite moment.

## Defaults

| Item | Default |
|---|---|
| Lengths | 15 s and 30 s; 6 s bumper on request |
| Ratios | 16:9 from the master; 9:16 / 4:5 through `social-vertical.md` |
| fps | the master's |
| Medium | none new: re-render ranges of the source `film.html` or splice the master; new frames only for the end card |
| Style | the source film's; no new style |

## Phase deltas

| # | Phase | What changes |
|---|---|---|
| 1–2 | Brief, Route | one paragraph; route is fixed by the source. |
| 3 | Pitch | **which section and why** (best section = strongest picture + strongest musical moment: usually the first chorus or the drop), in/out points as bar numbers, end card text. Offer two candidate windows. |
| 4 | Map | reuse the source map; in/out on downbeats: `SONG.downbeat(n)` times from `songmap.js` (or `python3 <studio>/tools/songmap.py track.wav`). |
| 5 | Storyboard | a cut list: source in/out (bars), any splice, end card timing. Critic only if more than one splice. |
| 6 | Test section | skipped. |
| 7 | Build | re-render only the window from the source page into a separate project copy (`node <studio>/tools/render.mjs --frames --range=<a>:<b>`, then `--encode --audio=<trimmed.wav> --out=…`), or a frame-index splice of the master; end card as a new scene. |
| 9 | Review | one fresh reviewer round is usually enough; the 10-second map is not needed under 60 s. |

## Team & fan-out

Producer, vertical-editor (owns cut-downs), integrator (splices, audio), qa-operator, reviewer, copywriter (teaser
posts). One agent; no chapters.

## Craft rules specific to this type

1. **Bar-aligned in and out:** start on a downbeat at a phrase start, end on the section's last hit or a downbeat with
   a 1–2 bar tail; never inside a word (check word ends from `words.json`).
2. **Cut the music as little as you can:** one uncut stretch whose own shape (build, drop, last hit) carries the
   teaser; splice only at phrase ends going into a quiet part or inside a full drop, never in an exposed quiet intro
   (`references/audio.md`, "Three things a listener heard").
3. **Frame 0 must work alone:** if the chosen window starts on a soft frame, start a bar earlier or add a 0.5 s cold
   open from the strongest picture of that window.
4. **Shorter is not better:** ask how long the story needs; 28 s and 20 s silent cuts scored the same 7
   (`references/launch-film.md`, shorter cut).
5. **Keep the voice** if the film has one: each picture lasts as long as its line.
6. **End card:** 3–5 s, the name, one line, the given date or link from its first second, landing on the last hit;
   built in the source film's type system.
7. **Never repeat a shot** to fill time; prefer a real uninterrupted stretch over a re-cut of flashes.
8. Lyrics in a music teaser: same decision as the source (`.srt` / captions / none), trimmed to the window.
9. Proof early: the payoff or the best picture before the middle of the teaser.

## Gates & bar

- Battery on the cut (`bash <studio>/bin/studio gate <dir>`), pops at splices declared or fixed.
- Splice check: PSNR of untouched regions vs the master > 40 dB (a one-frame slip drops it far lower;
  `references/pipeline.md`, re-render only what changed).
- `bash <studio>/bin/studio loudness out/teaser.mp4`: −14 LUFS ±1, ≤ −1 dBTP; the ending tail fades, no click.
- Flash test (hard) again: a short window can concentrate the source's flashes.
- **Reviewer locked items:** everything from the source film; only the window, splice and end card are open.
- **8/10 here:** someone who sees only the teaser knows what it is and when/where to get it; the music sounds uncut;
  the window holds its best picture at full frame.

## Pitfalls

- Cutting by seconds instead of bars: the downbeat lands a frame off and every hit feels late.
- `-c copy` joins cut off-keyframe (a frame of the next shot one frame early); count packets or re-encode.
- A new end card in a different font than the film.
- Dropping the narrator or the chorus lyric captions without asking.
- An invented release date or link.

## Deliverables

`out/<name>-teaser-15.mp4`, `-30.mp4` (+ `-6.mp4`), tall versions via `social-vertical.md`, `.srt` trimmed, `POSTS.md`
for the release week, cut list with bar numbers, gate and loudness report.

## Checklist

- [ ] Window chosen by section + bars; two candidates offered
- [ ] In/out on downbeats; no word cut
- [ ] Music uncut or spliced at a phrase end
- [ ] End card from given facts only
- [ ] Splice PSNR > 40 dB; loudness; flash PASS
- [ ] Tall versions handed to vertical-editor
