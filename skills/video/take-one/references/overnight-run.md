# The overnight run (the method behind the most viral Opus 5.5 videos)

One creator, 23 Sep 2026: "I made this with one prompt using Opus 5.5 / I spoke to my computer for 5 mins, claude worked for 12 hours, and I woke up to this." Another creator then reused that prompt with Midjourney and a moodboard for the editorial HUD film.

## What the prompt does (the reusable pattern)

1. **A proven base to build on:** point Opus at an existing repo that already solves rendering (that run used JohnHeibel/PDoomVideo: p5.brush, headless Chrome, ffmpeg). Here: ClaudeAnimationBase or this skill's canvas scripts.
2. **A clear target + fixed constraints:** remake X with the exact same audio; style direction in a few vivid words (there: a K-pop idol version of the character, AI Twitter memes, huge kinetic lyrics).
3. **Tools, with a budget:** an image model (fal) for character/set designs; a video model (Seedance 2.5) with the song as audio reference for lip-sync and choreography; ElevenLabs for sound design. That run allowed up to about $2K of credits. Always agree a budget with the user; never assume one.
4. **The rotoscope trick:** generate reference footage with the video model, then **redraw everything in JavaScript on top of it** so only the drawing shows. Video-model motion, code-drawn look. This is why the movement feels real and the style stays consistent.
5. **Self-review loops, explicitly:** build loops that check sync, rewatch, screenshot, iterate until it's right ("make no mistakes").
6. **Time:** let it run unattended for hours. Higher effort and longer runs produce more ambitious films.

The prompt was dictated by voice in about 5 minutes ("word vomited"). A rough, rich brief beats a polished short one.

## The look it produced (risograph music video)

Risograph print on warm paper: navy ink as black, one hero color (orange sunflower hair), hot pink / mustard / teal / red accents. Giant condensed words the character bursts through; lyrics on torn paper labels with one pink-underlined word; mono data; italic serif asides; marker notes. Two running counters carry the story (a date stamp 2019 → 2026, a P(doom) meter 8% → 99.9%). Every lyric line is a visual in-joke for the audience (AI Twitter memes). ~98 cuts in 2:21 (one every 1.4 s), two strobe bursts, ends on a pencil sketch that rhymes with the opening.

## The brief

Use `overnight-brief-template.md`: the structure of that prompt, generalized, with [brackets] to fill with the user.

## When to use this mode

When the user wants something epic (a music video, a 1-3 min film) and can let it run for hours with tools and a budget. Write the brief with them (target, audio, style words, tools, budget, what "done" means), confirm the budget and the checkpoint (storyboard approval, or truly unattended), then launch at the highest effort and check in on contact sheets.
