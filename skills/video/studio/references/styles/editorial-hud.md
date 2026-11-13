# Style: Editorial HUD film

A fashion-campaign film with an intelligence layer on top: photoreal, film-grained footage of one consistent character across several "looks", overlaid with a code-drawn HUD (mono labels, data panels, tracking brackets, a countdown, a news ticker) and giant kinetic words. Reference: an Opus 5.5 film (Sep 2026, 5 min, 24 fps): "Gave Opus 5.5 donald's prompt, Midjourney, and a moodboard. 12 hours later, woke up to this."

It's a hybrid: an image/video model makes the beauty, Opus directs and draws the intelligence layer.

## Design system

- **Footage:** editorial fashion photography in motion. One recurring character (same face, hair, signature detail such as a colored streak or a hair clip), a styling concept (uniform + hardware: harness, straps, tags), locations that tell the story (runway, car interior, server hall, spa, empty lot). Film grain, halation, slightly crushed blacks, 24 fps.
- **HUD, all code, drawn over the footage:**
  - small monospace labels in the corners: `LOOK 11 / 11`, `MODEL 01 · LOOK 11`, `ESCAPE VELOCITY · SS27`, a running timecode;
  - a thin frame of tick marks and coordinates at the edges;
  - **one accent color, a hot orange-red** (#FF4A1C range), used for tags ("A PROMISE, NOT A PRODUCT"), dotted scan paths, and key digits;
  - data panels (dark translucent boxes, 1 px borders): a spec title, a big number in the accent ("SLICE 114 / 120"), a small chart;
  - a persistent counter as the story's clock ("07 MONTHS TO ESCAPE");
  - tracking brackets that follow the face or an object (keyframe their positions per shot);
  - **a bottom ticker** of topical, satirical data ("TOKENS BURNED 321,084,500 · NVDA ▲ 5.3% · WAYMO RECALL 3,900 ...").
- **Headlines:** a clean bold grotesk in white, 2-line statements top-left ("Lower me into / the golden light."), with a typed-on caption line underneath in mono.
- **Kinetic words:** a condensed display face, huge, slamming in one word at a time ("LOCK", "ESCAPE", "ZERO-DAY.", "STARGATE:"), sometimes split-flap or letter-spaced.

## Production pipeline

1. **Moodboard + character:** agree the character, styling and 6-11 "looks" (locations/moments) with the user. Collect or generate a moodboard.
2. **Footage from a model:** the user generates stills (Midjourney, Nano Banana, GPT image) with a consistent character reference, then animates them into short clips (Seedance, Kling, Midjourney video, via Higgsfield or directly). Write every image/video prompt for them; quote credits before spending any. Aim for 3-6 s clips, 16:9, same grade.
3. **Edit the footage** into a timeline (ffmpeg concat with cuts on beats), conform to 24 fps, add grain if clips differ.
4. **HUD as a transparent overlay:** build `film.html` that draws ONLY the HUD on a transparent canvas (`clearRect`, no background), with the edit's shot list and timings, then export with alpha:
   ```bash
   ALPHA=1 node export.mjs 24 hud.mov
   ffmpeg -i footage.mp4 -i hud.mov -filter_complex overlay -c:v libx264 -crf 14 -pix_fmt yuv420p -movflags +faststart final.mp4
   ```
   For tracking brackets, eyeball the subject's position in each shot from extracted frames and keyframe them.
5. Music: a moody electronic track; cut so kinetic words land on hits.

## Length

The reference ran 5 minutes, which works as an art piece for an audience that already follows the creator. For reach, cut a 30-60 s version: 5-6 looks, one clock, one ending line.

## Faces and vertical

- The HUD frames the hero; it never sits on her. Tracking brackets may outline a face; panels, boards, reports, cards and slams go in the free space around her (face audit in `references/pipeline.md`).
- For 9:16 follow `references/vertical.md`: per-photo framing, type above the head or below the chin, compact strips instead of wide panels.

## Stills-only variant (zero video credits), and its ceiling

An app-builder music video (Sep 2026) was made with 21 stills from an image model on an unlimited plan, at no extra cost, and all motion in code. It works and it's fast, but be honest about the ceiling: our own review against the reference scored it about 7/10, mainly because nothing in the photos moves.

**Making stills feel alive**
- **Burst pairs:** generate a second still with the first as the reference: "Recreate the reference photograph as the exact same shot a split second later ... The only change: she breaks into a laugh." Framing and light stay nearly identical, so cutting between them on 8th notes under flash pops reads as motion. Same trick for a jump cut to a new expression mid-shot.
- Cut on the beat, jump in on a sung word, a slow push plus a little handheld shake, a small scale pulse on each kick after the drop, flash pops on hits, halftone and grain on everything, an audio-reactive HUD waveform.
- No single still held past about 4 s without a cut, a burst or a jump-in. The long holds (a 7 s wall shot, an 8 s outro on report panels) were the flattest parts.

**Prompts that made the plates usable**
- Identity: the first approved portrait is the reference for every later shot, plus a fixed line for face, hair and wardrobe ("identical face: freckles, dark curly hair loosely tied up, cream canvas workwear jacket"). It held across 20 images.
- Room for type: "framed on the RIGHT third, the left half clean negative space".
- UI plates: "the screen glowing plain blank white, flat to the lens", so code can put the app on it (masks + perspective, `references/pipeline.md`).
- "No text, no letters, no logos, no pins or badges": code draws the brand marks exactly (real logo paths, the hero's signature pin).
- A lighting arc as the story's turn: night (teal-navy, direct flash, desk lamp) for the problem, bleached daylight for the solution. Watch the white half: a grade that lifts it too much goes milky and loses punch.

**Getting to 9+**
Price 4-6 short video clips (Seedance or similar, 3-5 s each) for the hero moments, with the approved stills as start frames: her turn to camera on the hook, a hand pressing send, the door opening, the room laughing. Everything else can stay stills + code. Offer this at the pitch with the credit cost; video is not covered by Unlimited.
