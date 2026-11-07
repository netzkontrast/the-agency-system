# Style: Manifesto film

A 60-90 s documentary-style statement for a serious idea: a problem told as a short true story, a turn, then the vision as a numbered list, ending on the name. Reference: "Open Alignment", an open-source AI-safety manifesto film (Sep 2026, 84 s, 24 fps).

This is the right format for B2B/AI concepts (it's what a long concept video for an AI product should have been): serious, dense with facts, yet readable on a phone because every frame carries one line.

## Story structure (the part that makes it work)

1. **Cold open with a hard fact** in huge type: "1,200 AI AGENTS / ESCAPED THEIR SANDBOX." "17,600 ACTIONS OVER 4 DAYS." Dated, specific, alarming.
2. **Context, fast:** how we got here (a visual metaphor that returns later: a rider on a horse = steering a powerful thing; "For a while, alignment looked solved." → "Then we scaled RL.").
3. **The gap:** who is doing what, and what's missing ("Frontier labs are building safety for their own models." / "The open ecosystem, where most AI gets fine-tuned...").
4. **Proof it matters:** one concrete story (the hooded attacker, a terminal where closed models refuse and the open one works: "SO WE RAN AN OPEN ONE.").
5. **The turn:** "IT'S TIME TO BUILD" → the name slams in full-frame on the accent color.
6. **The vision as a numbered list** 01-06, one pillar per frame, each with its own image.
7. **Callback:** the opening metaphor returns resolved ("Full speed. Still steered." with the horse, now in the accent color).
8. **End card:** the name + one line ("Let's build it, in the open, together.") + logo.

## Design system

- **Black, off-white paper, and one accent (signal yellow ~#FFD21F).** Alternate black and paper scenes for rhythm; one full-yellow frame for the name reveal and a few pillars.
- **Type:** a heavy grotesk in caps for statements (two lines max, second line in the accent); an **italic serif for narration** ("For a while, alignment looked solved."); mono for labels, dates and meta in the corners (`OPEN ALIGNMENT`, `FORENSICS · JUL 2026`, `OBSERVED 02/04`) and for terminal windows.
- **Imagery = photos turned into drawings:** silhouettes, line-art edge tracings, posterized/halftone figures, a figure filled with glitter-like particles. Made in code from source images (edge detection, threshold, halftone, contour tracing), or drawn directly. The source images can be stock/archival photos the user has rights to, or generated (Nano Banana), but the treatment is always graphic, never a raw photo.
- **Terminal windows and UI cards** as proof, with real-looking commands and colored results.
- Thin corner brackets, a hairline frame, a red vertical rule for alerts.

## Rhythm

~24 shots in 84 s (one every ~3.5 s): slower than a hype reel, because every frame is a sentence to read. Words build line by line; the second line lands in yellow on the beat. A low, tense score that opens up at the turn.

## Engine

Canvas 2D via `scripts/new-canvas-project.sh`. Image treatments (Sobel edges, threshold, ordered-dither halftone, particle fill of a mask) are computed at load time from files in `assets/`; if there are no source images, draw the silhouettes as paths.
