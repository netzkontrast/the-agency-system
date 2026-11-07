# Timing: model the viewer

Adapted from the Claude Animation Base guide (JohnHeibel, MIT), which named the failure exactly: generated animation moves at one brisk speed, events pile up, and moments end before anyone understands them. You know what happens because you wrote it. The viewer sees it once, at full speed, for the first time, probably on a phone, possibly muted.

- **Write the reads.** For each shot, list in order what the viewer must understand. Each is a read. Every read needs time to find it, time to understand it, and a moment to register before the next begins. Small, distant, fast or subtle things take longer than big, central, obvious ones.
- **One read at a time.** Two things at once means the viewer gets one. Put a cause and its reaction in sequence.
- **Fast actions, slow meanings.** A motion can be very quick if anticipated; its meaning needs a hold. Rush what doesn't matter, linger on what does. That contrast is rhythm; one constant speed is flat.
- **Lead the eye.** Viewers look at what moves, is bright, big, or being looked at. Get the eye to the right place before an important read.
- **Let the reads set the length.** A shot is as long as its reads need. The last shot too: the payoff needs time to land before the video ends (2-3 s hold).
- **Text on screen:** roughly 0.3 s per word to read plus 0.5 s to register, minimum 1.2 s for anything that must be read. A punchline gets more.
- **The first second decides the scroll.** Frame 0 must already be striking (or deliberately look like a still screenshot that then comes alive).
- **Cut on rhythm.** If there's music, set the tempo and land cuts and impacts on beats; drops on big reveals, silence before a punchline.

## Motion curves: springs, never linear

- **Linear motion = never.** Nothing that moves (position, scale, camera, a mask edge) interpolates linearly; it reads as a PowerPoint slide. Stepped art (pixel, pencil test, crayon boil) steps on purpose, which is not the same thing.
- **Springs by default** (`springs.js`, closed form, safe in any frame order, see pipeline.md). Pick by what is moving:

| Preset | Stiffness/damping | For | Feel |
|---|---|---|---|
| `snappy` / `ui` | 320/30 | buttons, toggles, chips, UI cards, checkmarks | arrives in ~0.4 s, a hair of overshoot |
| `camera` / `container` | 170/26 | camera moves, panels, windows, bento cells | settles clean in ~0.55 s, no bounce |
| `heavy` / `type` / `logo` | 120/24 | hero type, logos, big stamps | ~0.8 s, weight, no overshoot |
| `playful` / `mascot` | 180/12 | mascots, characters, a pop-in with personality | ~20% overshoot, bounces |

- **Retarget, don't restart.** When something changes destination mid-move, add a key to `Spring.to`; one spring per target change, summed, keeps the momentum.
- Size the reads to the settle: a word landing on `heavy` needs its ~0.8 s settle plus the reading time above.

More motion moves (log-space zooms, beat punches, handoffs, floods) are in `motion-kit.md`.
