# Style: Cinematic animated short

A wordless short film with a real emotional arc, in a soft stylized-3D picture-book look, letterboxed like cinema. Reference: "Goodnight, Keeper" (Sep 2026, ~3 min): a girl signals goodnight with a flashlight to her grandfather, the lighthouse keeper; years pass; in the end she becomes the keeper.

This style is about story first. The drawing only has to be warm and consistent; the feeling does the work.

## Story craft (the part that makes people share it)

- **One relationship, one motif.** Two characters and a repeated gesture between them (the flashlight blink and the beam answering). The motif appears 3+ times and changes meaning by the end.
- **Time as a character.** Show years passing through physical marks, not text: tally marks filling a wall, a growing child, seasons, an aging face, objects that wear out.
- **Setup and payoff.** Every object introduced early returns (the scarf, the box labeled with her name, the lantern). The final image rhymes with the first.
- **A turn.** Absence, loss or a storm in the middle; the ending resolves it with a role reversal or a return.
- **No dialogue.** Title card at the start and end only. Emotion through posture, pacing, light and music.
- Structure (~90-180 s): 0 title over establishing shot → 1 the ritual (childhood) → 2 time passing montage → 3 separation → 4 the storm/turn → 5 return → 6 the ritual reversed → title again.
- Before building, pitch the story in 5 sentences to the user and wait for approval. This is the checkpoint that matters most for this style.

## Look

- **Letterbox 2.39:1** inside the 16:9 frame (black bars), cinematic framing: wide establishing shots, over-the-shoulder, close-ups on faces and hands.
- **Stylized 3D / soft vector:** simple rounded characters with big readable silhouettes, flat-shaded with soft gradient light, gentle rim light. Characters stay on-model across ages (same hair, same signature item).
- **Palette by emotion:** moonlit blues and violets for night and longing, warm lamp-orange interiors for safety, a pink dawn for hope, grey-green storm.
- **Light is the storytelling tool:** the lighthouse beam, a lamp, a flashlight glow (additive light, soft bloom), moon and stars.
- Weather and particles (snow, rain, sea spray) for scale, not decoration.

## Engine

Canvas 2D with layered parallax, or Three.js for real 3D staging (load it from a CDN such as `https://cdn.jsdelivr.net/npm/three@0.170/build/three.module.js`; the page is served over http). Keep every frame a pure function of t. For a film this long, split into scene files and brief parallel subagents with a shared character sheet and palette (see the watercolor style's notes on chapters).

## Music

A tender piano or strings track carries this style; cut so the ritual moments land on quiet phrases and the storm on the swell. Offer a Suno prompt ("tender solo piano, slow, nostalgic, sparse, cinematic, builds to strings, instrumental").
