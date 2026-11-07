# Style: Animator's pencil test

A classical-animation pencil test played back as the film: rough drawings on aged animation-bond paper, three coloured pencils each with one job, a production slate and a frame counter, stepped timing, and then the moment the animation stops to explain itself. Reference: a hand-drawn-style animation coded in canvas (Sep 2026): a character runs, jumps a log, freezes, and the frame becomes an animator's dissection sheet (onion skins, arc, spacing chart, principle labels) until an APPROVED stamp slams in.

## Why this style exists in our gallery

Every animation principle the viewer has ever half-heard of (anticipation, squash and stretch, arcs, spacing) is made visible, in the tools animators actually used to find them. The film gets to perform AND explain itself in one breath: first the thing moves, then time stops and the page shows you why it moved well. That turn is the hook. It also belongs to the "imperfection is the aesthetic" family that crayon storybook proved: a forgiving, boiling pencil line cannot look off-model, so a code-rigged character with small joint errors reads as a rough, not a bug.

**It doubles as the on-screen form of our character-department motion tests (SKILL.md step 3b).** When we show the user a walk cycle, sit/stand or reach-and-grip test for approval, render it in this style: red clean pass over blue construction, onion skins on, frame counter on. The user reads it as a real animation test, the forgiving pencil hides rig imperfections that would distract in a finished render, and the dissection devices (arc, spacing chart) make the approval conversation concrete ("the arc flattens at 119").

## Design system

- **Ground:** aged animation-bond paper, **#EDE6D8**, with a warm brown vignette at the edges (multiply), a slightly lighter centre (as if lit from a light table), a seeded grain tile and sparse fibres. The paper is a flat sheet: no desk, no peg bar needed, no page turns.
- **Three pencils, one job each (never swap jobs):**
  - **Red / carmine #C23A4F:** the CLEAN current drawing (the character or protagonist in its final line) and the scene title. The eye always lands on red.
  - **Light-blue non-photo #8FB0D0:** construction (centre lines, action line, bounding ellipses, tilt axes), roughs under the clean line, onion skins of previous/next drawings, dashed arcs, and the whole breakdown during the dissection. Loose, overshooting, allowed to be messy.
  - **Graphite grey (~#55575C):** props, background layout (horizon, trees, water, the log), the slate line, labels, circled frame numbers, the spacing chart. Thin and light; background props never get more contrast than the red drawing.
- **Line:** pencil, not ink. Width varies with pressure, ends taper, strokes overshoot corners, the clean line occasionally doubles. Graphite tooth: every pencil layer is masked by a per-pixel grain so the stroke breaks up like graphite on bond.
- **Production slate (top-left, every frame):** graphite hand-lettering `PROD. 2026-A  SEQ. 3  SC. 12`, and under it the scene title in red capitals, underlined with one red pencil stroke. The title names the action, e.g. `RUN + JUMP (LOG)`.
- **Frame counter (bottom-right, every frame):** a handwritten graphite frame number, and under it the timing: `TWOS` or `ONES` (or `ON TWOS` / `ON ONES`). Key frames get the number circled by hand.
- **Lettering:** single-stroke capitals that write on stroke by stroke, slightly uneven baseline and size; no typeset font in frame. The slate's first line is typewriter-ish only by being more regular.
- **The stamp:** an angled (5-10 degrees) purple rubber stamp `APPROVED` with a small line under it (`PENCIL TEST · SC. 12 · <date>`), double-ruled border, ink texture with dropouts and uneven density. It is the only saturated non-pencil colour in the film and appears exactly once.
- **Timing:** STEPPED, always. Cycles on twos (a new drawing every 2 frames at 24 fps), fast action on ones; holds are real holds. Never smooth-interpolate a drawing between poses; the stutter is the style. The counter's TWOS/ONES label changes when the timing does.
- **Format:** square 1:1 is the reference; 16:9 works. 15-40 s. Reads fully muted.

## NOT its neighbour

Nearest style: **hand-drawn sketchbook** (references/styles/sketchbook.md). Sketchbook is about a DRAWING being made: marks arrive in a hand's order, tone is built by hatching, margin notes carry a narrator's thoughts, one sheet slowly fills. This style is about MOTION being made: the drawings are already finished roughs that FLIP, the paper is a production document (slate, counter, stamp), colour is functional (red clean / blue construction / graphite props), and the content is timing and physics, not an idea. If the brief is "watch me think", send it to sketchbook; if it is "watch this move, then see why it works", it belongs here.

## Story grammar (from the reference)

1. **Slate first.** Empty paper, the slate letters itself in, the title writes on in red. Frame counter starts at 1.
2. **Perform.** The protagonist is drawn in (blue construction, then red clean), then performs its action on twos with the background props flipping by in graphite. The counter ticks in steps; key frames get circled as they pass.
3. **The fast bit on ones.** The climactic action (the jump) switches the counter to ONES.
4. **Freeze and dissect.** The action stops mid-air or just after. The red drawing fades to blue; blue onion skins of the key poses appear across the frame; a dashed arc (with small cross-ticks) traces the path; circled frame numbers drop under each key; a spacing chart (a ruler with uneven ticks: close at the ends = ease in/out) writes on under the slate with its caption, e.g. `SPACING · ANTIC → LAND · ON ONES`.
5. **Principle labels write on** with curved graphite arrows to the pose that proves them: ANTICIPATION, SQUASH, STRETCH, ARC, FOLLOW-THROUGH (one at a time, reading order).
6. **One replay in red** over the blue dissection (optional): the clean drawing re-performs the action through its own onion skins.
7. **Punchline:** the purple APPROVED stamp slams in (scale 1.3 to 1 in 3-4 frames, a 1-frame overshoot, a tiny paper shake). Hold. End.

## Engine notes

- **Marks as data, draw-on replay.** Every mark = centreline points + width profile (taper in/out) + pencil (red/blue/graphite) + alpha + jitter seed. A drawing is an ordered mark list; the film draws it on by replaying the list with the mark in hand cut partway along its centreline (construction first, then clean line, then details). Cache completed marks per layer.
- **One layer per pencil.** Draw each pencil's marks on its own offscreen canvas, mask it with the graphite-tooth grain (destination-in with a per-pixel alpha tile, 0.45-1.0), then composite onto the paper with multiply in order blue, graphite, red, stamp. Strokes are rendered on a scratch canvas at full opacity and composited at the stroke's alpha, so round-capped tapered segments never leave overlap dots.
- **Pose library keyed by frame number.** The protagonist's drawings are a table `{frame: pose}` (position, tilt, squash/stretch factor, secondary parts like sail/tail/antenna lag). Playback looks up the last key at or before `floor(t*24 / step) * step` where step is 2 (twos) or 1 (ones). The same table feeds the onion skins, the circled numbers, the dashed arc and the spacing chart, so the dissection is guaranteed to match what was performed. This is also exactly how the character-department motion tests (step 3b) should be stored.
- **Onion skins:** the same pose drawings in blue at 25-40% alpha (older = fainter), drawn loosely with their construction lines; never in red.
- **Boil re-seeded per DRAWING, not per output frame.** The jitter seed is a function of the pose's frame number, so a drawing held on twos (or in a hold) stays still, and a new drawing boils because it is a new drawing. Background props boil on a slow cycle (every 4-6 drawings) or not at all.
- **Dashed arc:** a smooth curve through a chosen point on each key pose (the head, the sail peak), drawn as short blue dashes with small perpendicular ticks at each key.
- **Spacing chart:** a graphite ruler with a base line and ticks placed at the actual normalized positions of the keys along the path (from the pose table), circled numbers above the ones that matter.
- **Lettering writes on:** single-stroke glyph table (capitals, digits, `. - + ( ) · → '`), each glyph a list of polylines in a unit box, jittered per glyph (baseline, size, a degree of rotation). Draw-on order is stroke order; ~2-3 frames per glyph.
- **Stamp slam:** stamp drawn to its own canvas (double-ruled rounded border, big letters with heavy strokes, small line), rotated 5-10 degrees, then masked with a coarse blotchy noise (dropouts where the rubber missed) plus the fine tooth; composite multiply. Animate scale 1.3 → 0.97 → 1.0 over 4 frames with a 1-2 px paper jolt.

**Best for:** animation and motion explainers (the twelve principles, "how a jump works"), character-department approval tests, sports technique breakdowns (a golf swing, a penalty kick dissected), physics of motion, "behind the scenes of how we animated X", and any story that benefits from performing first and explaining second. Prefer sketchbook when the subject is an idea rather than a movement; prefer crayon storybook when characters need colour warmth for a long story.
