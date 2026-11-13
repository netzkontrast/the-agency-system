# Playbooks

One file per project type. Read the matching playbook before the pitch (`SKILL.md`, phase 2). Every playbook has the
same sections: use when / not when · Inputs to collect · Defaults · Phase deltas (against the phases 0–11 in
`SKILL.md`) · Team & fan-out · Craft rules · Gates & bar · Pitfalls · Deliverables · Checklist.

| Playbook | One line | Default medium | Typical length / aspect |
|---|---|---|---|
| [`music-video.md`](music-video.md) | a full song → a clip timed to words, stressed syllables and bars; chapters per section group | paint | 3–5 min, 16:9 |
| [`album-suite.md`](album-suite.md) | one visual world across every track: album `VIDEO-CONCEPT.md`, shared library, continuity, release order | paint | per track as music video |
| [`lyric-video.md`](lyric-video.md) | the words are the picture: kinetic type on the sung syllables | canvas | full song, 16:9 |
| [`visualizer-loop.md`](visualizer-loop.md) | full-length visualizers from a few plates + `SONG.*` motion; Canvas loops 3–8 s 9:16 | paint or canvas | song / 3–8 s |
| [`explainer.md`](explainer.md) | one idea or mechanism in 15–60 s (teaching up to ~100 s) | canvas | 15–60 s, 16:9 |
| [`product-launch.md`](product-launch.md) | a launch film with the real product captured, on brand | canvas | 30–60 s, 16:9 + tall |
| [`brand-title.md`](brand-title.md) | stings, title sequences, openers, line-ups, beat-locked type | canvas | 3–8 s / 15–40 s |
| [`animated-short.md`](animated-short.md) | a character story, wordless or nearly; rig and motion tests first | paint | 30 s–3 min |
| [`documentary.md`](documentary.md) | true stories from verified sources: archival plates, quotes, maps, timelines | canvas or paint | 1–3 min (longer in parts) |
| [`data-story.md`](data-story.md) | real sourced numbers (or labelled example data) that change on screen | canvas | 20–90 s |
| [`social-vertical.md`](social-vertical.md) | 9:16 / 4:5 originals and recomposes, first-second hook, safe areas, captions | any | 15–60 s, 9:16 / 4:5 |
| [`teaser-cutdown.md`](teaser-cutdown.md) | the best section of a finished film, bar-aligned, with an end card | as source | 6 / 15 / 30 s |
| [`pathtraced-short.md`](pathtraced-short.md) | physically lit 3D in code (felt, paper, glass, smoke) on a GPU | pathtracer | 15–30 s, 4:3 |

## Picker: six questions

Answer in order; the first "yes" that routes wins. Then check the "not when" paragraph of the chosen playbook.

1. **Is there a song the film must follow from start to end?**
   - More than one track, one world for all of them → `album-suite.md`
   - The sung words are the picture → `lyric-video.md`
   - The picture only breathes with the music (no story), or it is a 3–8 s loop → `visualizer-loop.md`
   - Otherwise → `music-video.md`
2. **Does a finished film already exist, and the job is a shorter or taller version of it?**
   - Shorter (6–30 s) → `teaser-cutdown.md`; taller or 4:5 → `social-vertical.md` (both when both)
3. **Is it about a product, a brand or an event?**
   - The product must be seen working → `product-launch.md`
   - Only the mark, the name or a line-up moves → `brand-title.md`
4. **Is it true, and does every claim need a source?**
   - Documents, quotes, archival pictures, maps → `documentary.md`
   - Numbers and charts are the story → `data-story.md`
5. **Is there a character who acts a story?**
   - Physically lit 3D materials, short, a GPU is available → `pathtraced-short.md`
   - Otherwise → `animated-short.md`
6. **Is it one idea someone must understand?** → `explainer.md`

Nothing fits: take the nearest playbook, say what you changed, and after delivery offer to save it as a new playbook
(`SKILL.md`, Playbooks). A vertical-first brief of any type also follows `social-vertical.md` for layout and safe areas.

## Shared notes

- Agency System projects always start with the gate skill `skills/theagencysystem/`; name_exposure and the album's
  depiction rules bind every playbook, not only `album-suite.md`.
- The flash test is a hard gate in every playbook.
- `<studio>` in every command is `skills/video/studio/`.

## Media for any look

Every playbook names a default medium. Any playbook can use any of the five media — `paint`, `canvas`, `three`, `shader`,
`pathtracer` — when the look calls for it: `references/style-recipes.md` maps a look to a medium, a pass chain and
libraries; `references/libraries.md` lists what is installed and how to drive it by t.
