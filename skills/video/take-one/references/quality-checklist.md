# Quality checklist (walk it before showing the user anything)

Render a contact sheet at 360 px wide per frame (phone size) and full frames of key moments, and check with real eyes, not memory of the code.

## Critique rubric (score every round, from the exported MP4)

Score each axis 1-10:

| Axis | What 8+ means |
|---|---|
| Hook (first 2 s) | frame 0 is striking and the premise is clear by 2 s |
| Readability at 360 px | every must-read word readable on the 360 px sheet, for long enough |
| Motion quality | springs and eases, no linear moves, no pops, blur on fast moves in the master |
| Variety | something new (a layout, a scale, a colour field, a device) every 2-4 s |
| Composition | one focal point per frame, clean space for type, nothing crowding an edge |
| Data accuracy | every figure real and sourced, or labelled "Example data" |
| Sound sync | hits, cuts and hook words land on the measured frame or beat |

Then name **the 3 worst problems with timestamps** ("0:07.2 the handoff text blurs for 4 frames"), fix them, re-export and score again. **Loop until every axis is 8+.** Keep the reference comparison too (frames side by side with the reference, one 1-10 score, the three biggest gaps closed or priced); the rubric finds the bugs, the reference sets the bar.

**The agency bar, for a launch or product film.** When the person gave no reference, the bar is what agency-made launch films do (`references/directed-look.md`). In the part that explains the product, an 8 on variety and composition means:
- [ ] the real thing is on screen (the product's own screen, its footage, its output), not an invented picture of it
- [ ] no layout comes back more than twice in a row, and a list is not one matching frame per item
- [ ] two tones and one accent across the whole part
- [ ] the film's best picture is shown at full frame, not kept inside a box
- [ ] the words leave the picture room, and still read at 360 px

A part that fails the first two reads as a template however polished it is. Name it in the three worst problems, with the times it runs from and to.

**12-frame strips around every fast move.** For each whip, handoff, flood and slam, render 12 consecutive frames around it (`node frames.mjs 0 <t-6/fps>,...,<t+5/fps>`) and read the strip. It catches what a contact sheet at 1-2 s spacing never shows: text blurring or doubling through a handoff, a flood that reads as a one-frame flash, an element that appears without an ease.

**Idea**
- [ ] One idea, statable in a sentence. Every shot serves it.
- [ ] A payoff worth rewatching or sharing, held long enough to land.
- [ ] Nothing in it the user didn't ask for or approve (themes, targets, characters, claims).

**First second**
- [ ] Frame 0 is striking or a convincing "still" that comes alive. No blank or loading frame.

**Legibility (phone, muted)**
- [ ] Every must-read word is readable at 360 px wide. Hero type ≥ 90 px at 1080p; nothing essential under ~40 px.
- [ ] High contrast on every frame with text. No grey-on-grey.
- [ ] Nothing important covered by HUD, bubbles, other text or the frame edge.
- [ ] The story reads with sound off.
- [ ] Headline or tagline type never lands on top of live content (board, UI, footage). Time the camera so the type gets clean space first (whiteboard-product film: pull out before the word is sung).
- [ ] Nothing captured or photographed is shown enlarged past its native pixels (check the scale factor at every zoom, not only at the keyframes).

**Nothing pulls the viewer out**
- [ ] No drawing looks off at full size: natural neck/shoulder joins, believable joints and head tilts, faces readable at every angle, no mannequin stiffness, no lumps that read as something else (a bunched hood read as a hunchback). Where the drawing can't carry an angle, change the framing or pose.

**Faces**
- [ ] The main character's face (hairline to chin) is never covered by a panel, board, card, slam, band, caption or HUD block, in every aspect ratio delivered. Tracking brackets may frame a face; nothing solid sits on it. Avoid covering any other face too.
- [ ] Proven by the face audit (`scripts/audit-faces.mjs`, see pipeline.md), not by eye alone: zooms, jump-ins and the 9:16 recompose move the face under overlays you placed for another framing.
- [ ] UI shown on a phone or screen in a photo sits exactly inside that screen (mask + perspective), with fingers in front and the detection frame hugging the device.

**Design system**
- [ ] One background family, one accent, fonts each with a single job, consistent across all scenes.
- [ ] Nothing looks like a web page or 2000s Flash (plain default shapes, system fonts where a designed one was planned).

**Generated footage (if used)**
- [ ] No two generated clips start from the same frame (continue from a last frame or pick a different start).
- [ ] Every generation input was in color; the grade/look is applied in post, never baked into the input.
- [ ] Singing shots verified in sync by measurement (compare clip soundtrack to the real vocal), not by eye; cutaways don't need sync.

**Motion and timing** (see timing.md)
- [ ] One read at a time; every read has time.
- [ ] Anticipation before big actions, holds after meanings, variety in speed.
- [ ] No pops: characters and objects ease, squash, overshoot; faces change through a take.
- [ ] No linear motion: every move is a spring or an ease with a named preset (`timing.md`); stepped art steps on purpose.
- [ ] Every scene handoff carries a shared element across or is a declared hard cut; floods clear the farthest corner in 0.3-0.35 s (`motion-kit.md`).
- [ ] Transitions connect scenes; no dead frames.

**Real product (if shown)**
- [ ] The product is full of on-story content (photos, faces, screens, product shots), not just default UI or text.
- [ ] Brand pass done: real typeface, colors, logo files, headline and CTA from the live site (`brand-pass.md`).

**Technical**
- [ ] The quality gate passes (`node <skill>/scripts/gate.mjs film.html`, add `--mp4 out.mp4 --holds "a-b"` once exported). Run it before showing the user anything rendered — frames or MP4 — not after: it proves determinism by machine (cold-forward vs warmed-reverse hashes, and it names the frame that poisons a stale cache), scans the source for clocks/`Math.random`/filters, and measures dead air on the export. "Looks deterministic" is not a claim; a green gate is.
- [ ] Gate check 4 (pops) is green: every frame-difference spike is a declared cut (`--cuts`), the rest fixed.
- [ ] The master is exported with `SUB=8` for smooth-motion styles (kinetic, explainer, title, chrome, mono); never for stepped art (pipeline.md).
- [ ] No console errors; `renderFrame(t)` deterministic (same t, same pixels, any order).
- [ ] No halos on keyed sprites, no floating feet, lighting matches the scene.
- [ ] Final export 1920x1080 (or requested aspect), 60 fps, H.264, under 512 MB; audio aligned.

**Honesty**
- [ ] The caption's claims ("one prompt", "one-shotted", "no images") are literally true for the exported file.
- [ ] Every illustrative figure (a made-up revenue chart, a sample dashboard, a demo balance) carries a visible "Example data" label on screen, readable at 360 px. Unlabelled numbers are claims.
- [ ] Only real integrations are shown: every partner logo, connector and "works with" chip exists in the product today.
- [ ] A remake of someone's launch video credits the original on screen or in the caption and uses no fake co-marks (their logo beside yours).
