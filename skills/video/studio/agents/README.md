# Agents: the studio's subagent briefs

One brief per role in the team table of `../SKILL.md`. The producer (the main session) never hands a subagent the
conversation; it hands it one of these briefs, filled in. Every brief has the same shape: **Fill before sending** ·
Goal · Read / do not read · Own / read-only · Method · Done · Report · Stop.

## Roster

| Role | Brief | Spawned in phase | Weight | Max at once | Owns (writes) |
|---|---|---|---|---|---|
| Strategist | `strategist.md` | 1 Brief (and brand pass before 3 when a brand is in the film) | light | 1 | `BRIEF.md`, `BRAND-BRIEF.md` |
| Director | `director.md` | 3 Pitch, 5 Storyboard (and revisions after each critique), architecture before 7 | heavy | 1 per film | `STORYBOARD.md`, `BUILD_NOTES.md`, `film.html`, `config.js`, chapter stubs `scenes/chNN.js` (stubs only), `review/storyboard*` |
| Song-map analyst | `songmap-analyst.md` | 4 Map (re-run when the master audio changes) | light | 1 | `songmap/*.json`, `songmap.js`, `songmap/beatmap.md` + `songmap/words.json` |
| Critic | `critic.md` | 5 Storyboard: a new one per storyboard round | heavy | 1 | `review/critique-N.md` |
| Art director | `art-director.md` | 2 Route (style pick), 6 Test section (library, model sheets, LOOK.md); spot frame reviews in 7 | heavy | 1 | `LOOK.md`, `lib/look.js` (or the file the director names), `assets/look/`, `review/look_*` |
| Animator | `animator.md` | 6 Test section (one), 7 Build (one per chapter) | heavy (light for small fixes) | 2 | `scenes/chNN.js` (its own), `review/chNN_*` |
| Integrator | `integrator.md` | end of 7 (seams), 11 (master render) | heavy | 1 | `out/*.mp4`, `out/frames/`, `review/seams.md`, `review/seam_*` |
| QA operator | `qa-operator.md` | 8 Gates, again on the master in 11 | light | 1 per cut | `review/gate-N.md`, `review/gate-N/` |
| Fresh reviewer | `reviewer.md` | 9 Review: a NEW agent every round, max 3 rounds | heavy | 1 | `review/review-N.md` |
| Sound | `sound.md` | 4 (music fit, voice script) and 11 (SFX, mix, loudness) | light | 1 | `audio/*`, `audio/MIX.md` |
| Copywriter | `copywriter.md` | 11 Deliver (subtitle text source can start after 4) | light | 1 | `POSTS.md`, `out/*.srt`, `out/DELIVERY.md` (draft) |
| Vertical editor | `vertical-editor.md` | 11 Deliver (or a parallel track from 6 when the vertical is planned from day one) | heavy | 1 | `PV(...)` vertical values in its own chapter-scoped edits as assigned, `out/*-9x16.mp4`, `out/*-4x5.mp4`, `review/vertical_*` |

"Max at once" is per role; across the whole studio **at most two heavy agents run at the same time**. Light agents
(QA, song map, copy, sound) may run beside them. Small fixes after a review go to a lighter model.

## How to spawn one

1. **Copy the brief** (the whole file below its title line).
2. **Fill every `[bracketed]` field** in "Fill before sending" and wherever else one appears. Paths absolute. Leave
   no bracket unfilled; write `none` where a field does not apply. Do not add conversation history, your opinions
   of the work, earlier scores or the storyboard to briefs whose "do not read" list forbids them (critic and reviewer).
3. **Spawn** with the Agent tool: `subagent_type: general-purpose`, the filled brief as the prompt, one agent per
   brief. Independent agents go out in one message so they run together, never more than two heavy ones.
4. **Before the fan-out of phase 7**, the director has pre-registered every chapter (`<script src="scenes/chNN.js">`
   in `film.html`) and written `BUILD_NOTES.md`; the approved test section exists. Without these, do not spawn
   animators.
5. **Mid-build directions** from the person go into `BUILD_NOTES.md` at once (their words, dated); running agents are
   told "re-read BUILD_NOTES.md" in a follow-up message rather than restarted.
6. **Check the report before trusting it.** Open every path it names; look at every image it lists (sheets, strips,
   crops) with the Read tool; run `git diff --stat` or compare file lists to confirm it wrote only the files it owns.
   A claimed pass, score or render that you cannot find on disk did not happen.
7. **Post the job line** ("Animator ch03: chorus 2 built, the lantern now escalates; strips at review/ch03_*.") and
   decide the next step yourself.

## Interrupted agents

Every brief that writes files says "if your file already exists, continue from it". When a run is interrupted, spawn
the same filled brief again; the agent picks up from its file and `BUILD_NOTES.md`.

## Agency System projects

If the film belongs to the Agency System artist (its albums, novel or design layer), fill the "Agency System"
field of every brief with `yes`, the album's `VIDEO-CONCEPT.md` path and its depiction rules. Each agent then loads
the gate skill `skills/theagencysystem/` itself. **name_exposure is binding:** no personal name from the novel layer
in any frame, file name, subtitle, caption, post or prompt; functions/roles only. Depiction rules are locked for
every role, including the critic and the reviewer (tell the reviewer what is locked; do not tell it why).
