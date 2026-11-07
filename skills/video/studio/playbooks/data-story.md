# Playbook: Data story

**Use when** numbers that change on screen are the story: a counter, a chart that grows and turns, a map that fills,
a timeline of values, a before/after. 20–90 s. **Not when** the numbers only decorate an idea (`explainer.md`), the
story rests on documents and quotes (`documentary.md`), or the figures are a product's own UI (`product-launch.md`).

## Inputs to collect

- **The data file** (CSV/JSON) with source, retrieval date, unit, and licence; or the person's yes to labelled
  example data. No figure comes from memory.
- The one finding in one sentence ("X doubled while Y stayed flat"), the audience, where it posts.
- Brand pack if any; locale (decimal separator, date format, currency).
- What may be rounded, and how (state it on screen if it changes the reading).

## Defaults

| Item | Default |
|---|---|
| Length | 20–45 s feed; up to 90 s for a multi-finding piece |
| Aspect / size | 16:9 1920×1080; 4:5 1080×1350 and 9:16 recomposes common for feeds |
| fps | 60, master `SUB=8` (counters and chart moves) |
| Medium | canvas: `bash <studio>/tools/new-project.sh <dir> --medium canvas --duration 30` |
| Style candidates | `references/styles/explainer.md`, `editorial-hud.md`, `dark-premium.md`, `monochrome-launch.md`, `ascii-terminal.md` (data as characters), `riso-pop.md` (printed-chart satire), `pixel-art.md` |

## Phase deltas

| # | Phase | What changes |
|---|---|---|
| 1 | Brief | strategist: data file, source line, finding sentence, **claims check on every figure**. Data copied into `assets/data/` untouched; transformations in a script, not by hand. |
| 3 | Pitch | the finding, the 3–5 numbers the viewer must remember, one chart form per finding and why; the "data guard" (below) named. |
| 4 | Map | VO via `python3 <studio>/tools/vo.py vo.json`, or the music's beat grid (`bash <studio>/bin/studio songmap track.wav`) when counters land on hits. |
| 5 | Storyboard | per shot: which values are on screen, from which rows, chart state before/after, the read order (axis → bars → the outlier → the label). |
| 6 | Test section | the main chart transition plus its label at 360 px. |
| 8 | Gates | + data audit (below). |

## Team & fan-out

Producer, strategist (data owner), director, critic, art-director (chart system: axes, type, colour for one series
vs the rest), 1 animator per 30 s (≤ 2), integrator, qa-operator, reviewer, sound (ticks on counters sparingly),
copywriter (source line in posts).

## Craft rules specific to this type

1. **Data guard:** every on-screen figure is read from a data slot (`DATA.get('row', 'col')`) that throws on a
   missing key; no literal numbers in scene code (`references/formats.md`, levers). A value that fails renders as a
   BROKEN token, which `text-audit.mjs` fails.
2. **Real or labelled:** sourced figures carry a source line; illustrative figures carry a visible "Example data"
   label readable at 360 px for as long as they are up.
3. **One chart that changes,** not N charts: bars become a line, the axis rescales on a spring, the highlighted series
   keeps its colour through every change (the shared-element rule from `references/motion-kit.md`).
4. **Counters:** interpolate linearly in value only (directed-look allows linear for counters), ease the start and
   stop; the final value holds ≥ 1.2 s at full contrast; formatted with locale separators; never a value outside the
   data during the roll.
5. **Readability at 360 px:** axis labels ≥ 46 px at 1080p (text-audit WARN under 4.3 % of frame height), key value
   ≥ 90 px; max 2 series emphasised, the rest grey; label lines directly, no legends to decode.
6. **Axes honest:** bars start at zero; a truncated axis shows a break; log scales labelled "log"; time axes evenly
   spaced by time, not by row.
7. One read at a time: axis, then data, then the point; the takeaway line arrives after the visual that proves it.
8. Maps: one projection, equal-area for comparisons, colour scale with a labelled key the first time.
9. Rounding and units shown once on screen; percent vs percentage points kept distinct in words.

## Gates & bar

- Battery + `text-audit.mjs --json text.json` (no BROKEN, no SMALL FAIL) + `edge-audit.mjs`.
- **Data audit (hard):** script compares every number string in `text.json` against the data file (after the declared
  rounding); every mismatch is a FAIL. Source line present on every sourced chart.
- Strips of every counter roll (`node <studio>/tools/render.mjs --strip=a:b`): no flicker of digits, no NaN frame.
- **Reviewer locked items:** the data and the finding. Data-accuracy axis judged with the source list in
  `WORDS-AND-SOUND.md`.
- **8/10 here:** data accuracy 10 (anything less is a FAIL); a muted stranger states the finding with the right
  direction and magnitude; every must-read number readable on the 360 px sheet.

## Pitfalls

- A timing script that moved a counter's start value with the times ("1 became −1.1", NaN for a beat;
  `references/pipeline.md`).
- Twelve small multiples nobody can read on a phone.
- Colour reassigned between charts so the viewer loses the series.
- A dramatic truncated axis.
- An invented "about 40 %" to fill a gap.

## Deliverables

`out/<name>.mp4` (+ 4:5 / 9:16), data file and transform script, source list (`SOURCES.md`), `POSTS.md` with the
source line, gate report incl. data audit, review report, room.

## Checklist

- [ ] Data file + source + date in `assets/data/`
- [ ] Finding in one sentence; 3–5 key numbers named
- [ ] Data guard in code; no literal numbers
- [ ] Axes honest; rounding stated
- [ ] Data audit zero mismatches; no BROKEN text
- [ ] 360 px sheet read; reviewer ≥ 8 with accuracy 10
