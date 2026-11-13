# Playbook: Album suite

**Use when** every track of an album (or an EP) gets its own video inside **one visual world**: one place, one
palette, one set of motif objects, each track a different state of that world. **Not when** a single song stands
alone (`music-video.md`), only loops or visualizers are wanted for the album (`visualizer-loop.md`, though it can
share this suite's library), or the album needs one long continuous film (treat as `music-video.md` with chapters).

## Inputs to collect

- Album folder path, track list in album order, every master WAV, every streaming-lyrics text.
- The album's `README.md` (arc, motifs), art direction and cover; the album-level **`VIDEO-CONCEPT.md`** (write it if
  missing, phase 3 below). Example: `artists/the-agency-system/albums/dystopian-future-synth/lass-mich-lass-mich-atmen/VIDEO-CONCEPT.md`.
- Release plan: which tracks release when (singles first?), the platforms, whether Canvas loops and teasers are wanted
  per track.
- Depiction rules, content-warning needs, tracks that need care in review (pauses, one track per session).
- Render machine and how many render hours per week it really has.

## Defaults

| Item | Default |
|---|---|
| Per-track length | the full song (3:00–5:30), 16:9 1920×1080, 24 fps on twos |
| Per-track extras | Canvas loop 3–8 s 9:16 (`visualizer-loop.md`), teaser 15–30 s (`teaser-cutdown.md`) |
| Medium | paint (`--medium paint`); one medium for the whole suite |
| Style candidates | one style for all tracks: `references/styles/ink-wash.md`, `painterly-glow.md`, `watercolor.md`, `sketchbook.md`, `paper-cutout.md`, `riso-pop.md`; the album's own visual guide overrides any style file |
| Parallelism | **two tracks in production at most**, one of them in Build at a time |

## Phase deltas

The suite runs once at album level (A-phases), then each track runs `music-video.md` with the deltas below.

| # | Phase | What changes |
|---|---|---|
| 0 | Intake | Agency System projects: invoke `skills/theagencysystem/` first; answer its gate; load only the snippets the active function × state × layer needs. Size the whole album (tracks × render hours × tokens). |
| 1 | Brief | one album brief: platforms per format, release order, CW policy. Per track: one paragraph only. |
| 2 | Route | **once**: medium, style, palette for the album. Not re-opened per track. |
| 3 | Pitch | the album pitch is `VIDEO-CONCEPT.md`: the one idea ("one room, N states"), hard rules, formats, album-wide image language (motif → driver), per-track treatment seeds, shared library, order, open questions. **(hard)** the person confirms it before any track starts. Per-track pitch = its treatment seed expanded, short. |
| 4 | Map | per track, `bash <studio>/bin/studio songmap <track>.wav --lyrics <track>.txt`; one `songmap/` folder per track. |
| 6 | Test section | **only for the pilot track** (usually track 1 or the first single): 30–45 s that become the style bible of the whole album. Later tracks build a 10–15 s look check against it instead. |
| A | Library | after the pilot's test section: the art director builds the shared library once (room/set, motif objects, palette, glitch or texture functions, `beat.js` helpers), versioned; tracks read it, never edit it. |
| 9 | Review | the reviewer gets the album's locked rules plus the previous track's final frame for continuity. |
| 11 | Deliver | per track, in release order; plus an album contact sheet (one frame per track, `tools/contact-sheet.sh`) to prove one world. |

## Team & fan-out

Album level: producer, strategist (release order, CW, platforms), director (VIDEO-CONCEPT, continuity table),
art-director (library owner), copywriter (CW texts, posts per release). Per track: the `music-video.md` team.

- **Two tracks at most in parallel**, and at most two heavy agents at once across both (`SKILL.md`, Cost).
- Chapter split per track as in `music-video.md` (section groups, bar-line seams).
- Only the art director edits `lib/`; a track that needs a new library function asks for it in `BUILD_NOTES.md`; the
  addition must render the pilot pixel-identical with defaults (prove with a checksum of ~30 frames).

## Craft rules specific to this type

1. **One world, many states.** No track invents a new place. A state change (light, breath, crack, frost, repair) is
   the track's identity; write it as one line per track in `VIDEO-CONCEPT.md`.
2. **Continuity motifs:** a table motif → which tracks → how it changes (the same object cracked in track 4, mended in
   track 11). Each motif is set up, varied and paid off across the album, not inside one track.
3. **Track seams rhyme:** each track's last frame is the next track's first frame state, so the album plays as one
   piece in order; standalone, each still opens striking (frame 0 rule).
4. Album-wide drivers come from measurement: heartbeat pulses from `SONG.pulse(t)`, breath marks from word times,
   polyphony density from section data (`SONG.section(t)`); never hand-placed.
5. **Content warnings:** a calm card (2–3 s, no music hit) at the start where the album's rules require it, the same
   design for every track, plus the same line in every post (`POSTS.md`).
6. **Flash discipline:** alarm or flicker moments are designed under the limit (≤ 3 large or red flashes per
   second); boil on large saturated fields counts. The flash test is run per track, not per album.
7. Agency System: **name_exposure is binding** — functions/roles only in every frame, file name, `.srt`, caption,
   prompt and post. Voices appear as light and shadow qualities, never as named characters.
8. **Depiction rules are locked** (e.g. "objects, not bodies"): what the song names is never shown on a figure; the
   critic and every reviewer receive them verbatim.
9. Lyrics on screen: one decision for the whole album (`.srt` only is the safe default); text exceptions, if any,
   listed per track in `VIDEO-CONCEPT.md`, from streaming lyrics only.

## Gates & bar

- Per track: the full `music-video.md` gates (battery, map ± 1 frame, plate audit, flash test **hard**).
- Album gate before each release: frame 0 and last frame of adjacent tracks side by side; palette and library version
  match the pilot; CW card identical; name scan of every text output (frames via `text-audit.mjs --json`, `.srt`,
  `POSTS.md`, file names) against the resolver's name list — zero hits.
- **Reviewer locked items:** album look, depiction rules, lyrics, CW card, name_exposure.
- **8/10 here:** each track scores 8+ alone, and a stranger shown three random tracks' contact sheets says "same
  world" while naming each track's different state.

## Pitfalls

- Re-deciding style per track: the suite drifts by track 3. Route once.
- Building the library before the pilot's test section is approved: it encodes an unapproved look.
- Three or more tracks open at once: usage and the render machine run out, quality drops on all of them.
- Care-sensitive tracks reviewed back to back: one per session, with a pause.
- A name slipping in through a file name or a post although every frame is clean.
- Phonetic Suno lyrics leaking into `.srt` or posts.

## Deliverables

Album: `VIDEO-CONCEPT.md` (confirmed), shared `lib/` (versioned), continuity table, album contact sheet, release
calendar. Per track: everything in `music-video.md` Deliverables, plus Canvas loop and teaser if ordered, CW card,
CW line in posts, gate report with flash and name scan.

## Checklist

- [ ] Gate skill run (Agency System); depiction rules and name_exposure copied into `BUILD_NOTES.md`
- [ ] `VIDEO-CONCEPT.md` confirmed by the person
- [ ] Pilot track test section approved = album style bible
- [ ] Library built once, versioned, pilot pixel-identical after additions
- [ ] Continuity table: every motif set up, varied, paid off
- [ ] ≤ 2 tracks in production; release order fixed
- [ ] Per track: map, storyboard, critic, gates, flash test, reviewer
- [ ] Album gate: seams, palette, CW card, zero name hits
