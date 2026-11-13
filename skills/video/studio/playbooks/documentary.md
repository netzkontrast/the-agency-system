# Playbook: Documentary

**Use when** the film tells a true story from sources: an event, a person's record, a history, a case; with archival
plates, quotes on screen, maps and timelines, and verified facts. Includes music videos for documentary albums (run
`music-video.md` and add this playbook's source rules). **Not when** the film states an opinion without sources
(`explainer.md` with `references/styles/manifesto.md`), or the numbers are the whole story (`data-story.md`).

## Inputs to collect

- The sources: documents, articles, transcripts, archival photos/footage, with URL or archive reference, date,
  author, licence or permission for every item. For an album: its `SOURCES.md` / `RESEARCH.md`.
- Verification status per fact (for documentary albums: `Verified (date)` on every track before lyrics; the same
  applies to every on-screen fact here).
- Living people shown or named: consent or public-record basis; what must be blurred or anonymised.
- Length, platform, narrator or not, content warnings needed.

## Defaults

| Item | Default |
|---|---|
| Length | 60–180 s feed piece; up to ~8 min for a long-form chapter (in parts) |
| Aspect / size | 16:9 1920×1080; 4:5 for feed cut-downs |
| fps | 24 (archival feel; declare clip frame rates with `window.FOOTAGE`) |
| Medium | canvas for archival, maps and quotes (`--medium canvas`); paint for reconstructed scenes nobody filmed (clearly drawn, never photo-real) |
| Style candidates | `references/styles/manifesto.md` (fact, story, turn), `editorial-hud.md` (records and overlays), `ink-wash.md` / `sketchbook.md` (drawn reconstruction), `monochrome-launch.md`, `dark-premium.md` |

## Phase deltas

| # | Phase | What changes |
|---|---|---|
| 1 | Brief | strategist builds `SOURCES.md`: one row per claim → source, date, quote verbatim, verification status, licence of any plate. **(hard)** no unverified fact enters the script. |
| 3 | Pitch | the story's spine (cold open with one hard, dated fact → context → the turn → what it means), every line tagged with its source row. Mark reconstructions vs records. |
| A | Archive | collect plates at native resolution into `assets/archive/<id>` with a sidecar line (source, date, licence, crop allowed?). Face boxes for every photo with people (`window.FACES`). |
| 4 | Map | VO script placed with `python3 <studio>/tools/vo.py vo.json`; or song map for a documentary music video. |
| 5 | Storyboard | per shot: record or reconstruction, source row, quote/caption text, map/timeline state. Critic also checks that no shot implies more than its source says. |
| 6 | Test section | the cold open + the first map or timeline move. |
| 8 | Gates | + source audit (below). |
| 11 | Deliver | + `SOURCES.md` published as a description/credits list; + attribution end card. |

## Team & fan-out

Producer, **strategist (source owner)**, director, critic, art-director, 1–2 animators (chapters by story act; map and
timeline module owned by one animator), integrator, qa-operator, reviewer, sound (VO and restraint), copywriter
(description with sources, CW).

## Craft rules specific to this type

1. **No invented facts, quotes, dates, numbers or names.** Every claim on screen or in VO maps to a row in
   `SOURCES.md`; anything the team wrote is marked as interpretation.
2. **Quotes on screen are verbatim**, with speaker and date; trimmed quotes show `…`; never paraphrase inside quote
   marks. Hold time 0.3 s/word + 1 s (it is read as a document).
3. **Archival plates at native pixels or below** (`plate-audit` UPSCALE FAIL ≥ 1.2×); never mix frames for slow
   motion (BLEND); never colourise or "restore" without saying so on screen.
4. **Reconstruction looks reconstructed:** drawn or diagrammatic, never a generated photo that could pass as a record.
5. **Attribution:** a small credit line on each archival plate (source, year) readable at 360 px for ≥ 1.2 s, plus a
   full credits card.
6. **Maps:** one base map style for the whole film, the camera moves in log space between scales, place names spelled
   as in the sources, a scale or orientation cue on first appearance; borders and names as of the depicted date.
7. **Timelines:** one axis, one direction, dates on the axis; the "now" marker moves on a spring; never compress the
   axis without a visible break.
8. People: faces never covered by type (face audit); anonymised people blurred in every frame they appear.
9. Content warnings as a calm card and in the description where the subject needs it; flashes from archival footage
   count towards the flash limit.
10. Under a narrator, fewer sounds (`references/audio.md`).

## Gates & bar

- Battery + `text-audit`, `plate-audit`, `edge-audit`, `audit-faces.mjs`, flash test (hard), `audio-check` with
  `--stems` when voiced; transcribe the final mix and compare every line to the script.
- **Source audit (hard):** every on-screen text string (`text-audit.mjs --json`) and every VO line matched to a
  `SOURCES.md` row; zero orphans; every plate has a licence line.
- **Reviewer locked items:** quotes, facts, archival plates (they cannot be "improved"). Reviewer asked to flag any
  moment that implies more than is shown.
- **8/10 here:** data-accuracy axis 10 (anything less is a FAIL, not a score); a stranger retells the story correctly;
  every quote readable muted; no stretch over ~6 s of type without a picture.

## Pitfalls

- A strong line in the script with no source behind it ("everyone knew…").
- Upscaled scans that look soft on a phone; mixed frames ghosting faces.
- A generated "archival" photo.
- VO cut inside words (the 8-minute documentary lesson in `references/voice.md` §20).
- Maps with today's borders on a historic date.

## Deliverables

`out/<title>.mp4` (+ 4:5 cut), `<title>.srt`, `SOURCES.md` (published), credits card, CW text, `POSTS.md` with
sources, gate report incl. source audit, review report, room.

## Checklist

- [ ] `SOURCES.md` complete; every fact verified and dated
- [ ] Permissions/licences for every plate; consent or basis for every person
- [ ] Script lines tagged with source rows
- [ ] Reconstructions visibly drawn
- [ ] Source audit zero orphans; plate audit clean
- [ ] Flash test PASS; CW where needed
- [ ] Credits and attribution delivered
