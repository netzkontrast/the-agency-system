# Style: ASCII / CRT terminal

Everything on screen is built from monospace characters glowing on a CRT: green or amber phosphor on near-black, scanlines, slight barrel curvature, phosphor bloom, a blinking cursor. Figures, seas, charts, whole scenes are character density fields; log lines and prompts are the narration. Reference: procedural demoscene-style terminal work. The raw numbers are modest, but the style is cheap to execute flawlessly in code and the audience is exactly ours.

## Why this style exists in our gallery

Dev-tool launches live in this house. For a product whose home is the terminal, the medium is the message: the film looks like the place the product lives, so the audience recognizes it as "for me" in the first half-second. And like crayon, it is an imperfection-proof bet: a character grid cannot be off-model, a density field cannot tear at a joint, and every frame is trivially deterministic. It is the default recommendation for CLI/agent products and anything aimed at developers.

## Design system

- **Ground:** near-black with a faint phosphor ambient (#0A0806 in the amber world, #04080A-ish in the green world), corner vignette, scanlines over everything.
- **ONE color per world:** green #33FF66 or amber #FFB000, chosen once for the whole film. Every "shade" is a brightness step of that hue (dim char up to near-white hot core). The single declared exception: a red alert line (#FF5555 family) as ONE line of terminal chrome at the crisis beat, never in the scene field itself.
- **The grid:** everything lives on a character grid, e.g. 160x45 cells at 16:9 (8x16 px cells at 1280x720). Nothing is ever drawn off-grid.
- **Density ramp:** brightness maps to character weight through a fixed ramp like `" .:-=+*#%@"`. Calm = sparse `.:-` textures; force and danger = walls of `@#%`. Brightness picks the character AND its phosphor intensity together.
- **Scenes as density fields:** figures, water, skies, charts are rendered as luminance first, then translated to characters. A protagonist is a small bright glyph cluster against a dimmer field; findability comes from contrast, not outline.
- **CRT artifacts:** scanlines every 2-3 px, phosphor bloom (bright chars halo), slight barrel curvature, and in motion a subtle flicker and refresh shimmer. Restraint: artifacts season the frame, they never obscure a character.
- **UI chrome as a real terminal:** a genuine prompt line (`user@host:~$ command`), timestamps (`[HH:MM:SS]`), log lines, exit codes, a blinking block cursor. Chrome rows are real text on the same grid, brighter than the scene field.
- **Type:** the terminal IS the type system. One monospace face, nothing else, ever.
- **Format:** 16:9 for X/LinkedIn; also strong in 1:1. Must read fully muted (the log lines carry it).

## Story grammar

1. Commands and log lines ARE the narration: the story advances by what gets typed and what the system prints back. The prompt is the protagonist's voice.
2. Every line arrives by typewriter reveal; the cursor blinks while the system "thinks". Silence = a blinking cursor on an empty line.
3. Scene beats render as density fields behind/between the chrome; a scene can bloom out of a command's output.
4. Danger is density: the threat is a towering wall of `@#%`; the hero stays a tiny bright cluster that keeps pointing forward.
5. The red alert line marks the single crisis beat, and it is used exactly once.
6. Callback ending: the film ends on a fresh prompt with a blinking cursor. The terminal is ready again.

## Engine notes

- **Two-stage render:** draw the scene into a small offscreen 2D canvas (square-ish pixels, e.g. 160x90), scale-sample it down to one pixel per grid cell (160x45), read the luminance buffer, and map each cell through the density ramp to its character and through the same value to its phosphor brightness.
- **Grid:** e.g. 160x45 cells at 1280x720 (8 px wide, 16 px tall, the ~1:2 cell aspect of a real terminal). Draw the scene in a square-pixel space and compress vertically at sampling time so shapes keep their proportions.
- **Phosphor bloom via layered draws:** render all characters to an offscreen layer, then composite it with `lighter` several times: one downscale-upscale pass (quarter size drawn back full-frame, low alpha) for the wide halo, a small offset ring for the tight glow, then the sharp layer on top. No ctx.filter, no CSS filters.
- **Scanlines:** 1 px black lines at ~0.2-0.3 alpha every 2-3 px, drawn after the bloom.
- **Barrel curvature via per-row x-offset:** each text row drawn with its own horizontal scale toward center, `scale = 1 - k*dy^2` with k around 0.02-0.04 (dy = row distance from vertical center, normalized). Add a corner vignette to sell the tube.
- **Color:** one phosphor per world (green #33FF66 or amber #FFB000). Brightness = lerp black -> phosphor for the lower range, phosphor -> near-white (e.g. #FFEBB8 for amber) for the hottest cells. Red #FF5555 exists only as the declared one-line alert exception.
- **Chrome rows** are real strings placed on grid cells (they replace scene cells), at 2-3 brightness tiers: prompt bright, logs dim, alert red.
- **Motion:** typewriter at 15-40 chars/s with seeded jitter, cursor blink ~530 ms square wave, scene fields animated by re-evaluating the luminance scene per frame; add a per-cell brightness jitter of a few percent per frame for phosphor life. Seeded randomness only, fully deterministic.

**Best for:** dev-tool and CLI/agent launches, "watch the system think" narratives, changelog and release films, benchmark/chart moments, retro-computing subjects, any audience that lives in a terminal.
