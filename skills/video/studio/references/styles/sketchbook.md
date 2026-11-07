# Style: Hand-drawn sketchbook

Line-first monochrome intimacy: pen, pencil and charcoal lines that DRAW THEMSELVES on paper grain, hatching and cross-hatching for tone, handwritten margin notes, and at most one pale accent wash per scene. Evidence for the category: "What do you love?" (Sep 2026), 28 s, 2160x2160, 24 fps. Honest note on the reference: that video is warm cut-paper/gouache with color (its look belongs to a paper-cut-out style, not this one) — what it proves for THIS style is the pull of hand-made-on-paper intimacy, marks arriving in a hand's order, and its best device, the handwritten note on lined paper that writes itself and carries the story. This style takes that intimacy and strips it to line and tone.

## Why this style exists in our gallery

Crayon storybook won by making imperfection the aesthetic through waxy COLOR scribble fills. This is the other half of that bet: **line and tone only**. No fills to go off-model, no color to manage — just a pen thinking on paper. It reads as a mind at work, which makes it the honest choice for ideas, process, memory and explanation: the viewer watches the drawing being decided, construction lines and all. Where crayon is a child's picture book, this is an adult's notebook. It is also the cheapest style to iterate (one ink, one ground) and the strongest at draw-on reveals, because a line arriving IS the animation.

## Design system

- **Ground:** warm paper white (#F5F1E6 family) with real tooth: a seeded grain tile multiplied over everything at low alpha, plus sparse fiber flecks. The paper is a character; large areas stay bare.
- **Line:** the hand is one of three tools, declared per film and never mixed mid-scene without a story reason:
  - **Pen** (fine ink, #232830-ish): near-constant thin width, darkening where strokes cross, gaps where the hand lifted.
  - **Pencil** (graphite #3A3E45 at ~50% alpha): softer, wider, pressure varies along the stroke; construction lines live here.
  - **Charcoal** (#26241F, soft and wide): side-of-stick drags for tone masses; kneaded-eraser lifts drawn as destination-out streaks at partial alpha, so every lift is streaky and leaves grey residue (charcoal specifics informed by anidoodle, Apache-2.0).
- **Tone:** NEVER a flat fill. Hatching (one direction) for mid tones, cross-hatching (2-3 angles, 25-35 degrees apart) for darks, scribble loops for chaos, side-of-charcoal for atmosphere. Highlights are paper left untouched — protect a bare patch around whatever must stay bright.
- **Accent wash:** at most ONE watery color per scene (pale ochre for morning, grey-indigo for weather...), laid loose past the line with a darker pooled rim and granulation from the grain. Most frames have none; when it appears it means something.
- **Margin notes:** small handwritten words in the page margins — a label, a doubt, a date, an arrow to the thing. Drawn as single-stroke jittered letterforms in the same ink as the drawing (a handwriting font is acceptable; drawn letterforms are better and animate as writing). The notes are the caption track AND the narrator's voice.
- **Construction honesty:** faint pencil scaffolding (boxes, centerlines, horizon ticks) is drawn first and LEFT VISIBLE under the ink. Erasing it is off-style; the thinking stays on the page.
- **Format:** 16:9 or square both work; must read fully muted (the drawing order + margin notes carry it).

## Named variants (declare one per film)

1. **One-line drawing:** a single unbroken contour draws the whole subject without lifting; the line's journey is the film. No hatching, one or two margin words. Best for portraits, love letters, logos.
2. **Whiteboard explainer:** marker-weight pen on white, diagrams + arrows + boxed words, hand-drawn UI and graphs; tone via marker hatch only. The classic "let me draw you the idea" register.
3. **Urban sketch pen-and-wash:** confident ink first, wobbly perspective, then loose accent washes that overshoot the line; location + date handwritten in a corner. Best for places, travel, memory.
4. **Charcoal:** tone-first — side-of-stick masses, then edges cut with the stick's corner, lights LIFTED OUT with the kneaded eraser (streaky, grey residue stays). The most cinematic variant; best for weather, night, grief, drama.

## NOT its neighbour

Nearest style: **crayon storybook**. That style is waxy COLOR scribble fills disobeying a ballpoint line, square kids'-book framing, characters with one big eye. This style has no fills and (almost) no color: tone is built from line density and charcoal, subjects are drawn as a sketcher draws (construction, contour, hatch), and the register is a private notebook, not a picture book. If the brief wants color-crayon warmth and bouncy characters, send it there; if it wants thought, process, place or drama in monochrome, it belongs here.

## Story grammar

1. The page is the world: the film lives on one sheet (or a small number of page-turns), and the camera moves like eyes over a desk.
2. Drawing order is narrative order: what the hand draws first is what the narrator thought of first. Hesitation (a stroke stopping mid-air) and correction (a re-drawn line next to a rejected one) are story beats.
3. Margin notes advance the plot; the drawing illustrates it. The last note is the payoff line.
4. Danger/climax = the page going dark: hatching densifying until only a protected patch of bare paper holds the subject.
5. The accent wash marks the emotional turn — its first appearance is an event.

## Engine notes

- Marks as data: every mark = centreline points + a width profile (taper in/out) + tool + alpha + a jitter seed. The still is the full ordered mark list; the film replays the same list over a cached composite of finished passes, with the mark in hand cut partway along its centreline (mechanic informed by anidoodle, Apache-2.0).
- Draw-on ordered like a real hand: faint construction lines first, then contour, then hatching, then notes. Time per mark proportional to its length plus a constant per pen lift.
- Jitter: perpendicular smooth-noise offset of the centreline, amplitude by tool (pencil > pen); width and alpha modulated along the stroke by a seeded grain so pressure varies; pen darkens ~15% where strokes cross (multiply).
- Hatching: generate parallel strokes across a region at a base angle with per-stroke angle/spacing jitter, clipped to the region; cross-hatch = 2-3 passes at offset angles; density maps to tone.
- Paper grain: one seeded noise tile, composited multiply over the finished frame at low alpha; wash granulation reuses the same tile so pigment settles into the same tooth.
- Boil: re-seed the jitter (not the geometry) on 2s-3s, i.e. at 8-12 fps steps, while position/camera animate at full fps. Cached composites must key on the boil frame or the boil freezes.
- Charcoal lifts: destination-out streak strokes at 0.4-0.7 alpha over the tone mass — never a clean erase; residue is the point.
- Wash: blobby path filled at low alpha in multiply, a darker thin rim stroke along its edge (pooling), edges overshooting the ink line on purpose.

**Best for:** ideas and explainers with a thinking-out-loud voice, personal essays, travel and memory pieces, storyboards-as-the-product, dramatic monochrome story beats, anything where watching the drawing get made IS the content. Prefer crayon storybook when the subject is characters in constant motion who need color warmth.
