# Style: Image-to-game cinematic

An image model makes the art (so it looks AAA); Opus turns the still images into a real, animated, often playable game. The hook: the video opens on a still that looks like a screenshot, then it comes alive. Reference: one of our own films (Sep 2026), a Mortal Kombat-style fight built in one prompt from four images.

## Assets (made first, with an image model: GPT image via ChatGPT, Nano Banana via Higgsfield, etc.)

Write the image prompts for the user; they generate. Ask for:
1. **The hook screen** (16:9): e.g. a character-select screen, title screen, level map. All UI crisp and separated.
2. **Pose sheets**, one per character: 6 full-body poses in one row, identical scale and lighting, evenly spaced on a **flat light-grey background with clear gaps**, all facing the same way (player faces right, opponent faces left). Example set: stance, punch, high kick, block, hit, victory / knocked down. Without pose sheets characters can only slide like cut-outs.
3. **The empty stage** (16:9) matching the hook screen, with a clear floor.
If the user appears in it, attach their photo to each prompt. Never invent the opponent, theme or target: ask.

## What the build prompt must ask for

- Key out the grey background in code (color-distance keying, soft anti-aliased edges, no halo), auto-detect poses by empty column gaps (cut touching figures along the emptiest seam), anchor each pose by its feet.
- Light the sprites into the scene: warm tint matching the stage, contact shadow, faint floor reflection.
- Make it feel animated, not like swapped cut-outs: tweens with anticipation and recoil, motion smears, squash on impact, idle breathing, hit-stop freezes, decaying screen shake, sparks, slow motion on the finisher.
- Game UI drawn in code in the hook screen's style: health bars with a damage trail, timer, combo counter, slam-in announcements.
- A playable mode after the cinematic (keyboard), reusing the same systems. "You can play it" is a strong share hook.
- Serve images over local http (canvas reading local files taints it); expose `window.READY = true` after processing.

## Comedy that lands

- If a character talks, **each attack is a line** (a special move shouted), and every line fails on screen (blocked, dodged, turned back). The best joke contradicts the situation: the loser, knocked out, still pitching.
- Speech bubbles: smooth oval, bold black text 56-66 px, no shake, held ≥ 1.4 s, never over the HUD, names or faces. Pin the final punchline bubble by hand next to the character's head; auto-placement drifts.
- End on a held beat (2.5 s+) with the music faded out so the last line lands in silence.

## Pacing

~40 s for a full fight: hook still (1 s) → wake up → select → VS → ROUND 1 / FIGHT → 4-5 exchanges → special move → FINISH → victory → punchline hold. The first cut at 30 s was too fast to read; 40 s with room around each joke worked.
