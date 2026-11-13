# From the first line to the pitch: brief, look, route, music

`SKILL.md` gives the phases (intake, brief, route, pitch) and their gates. This page is the craft inside them: how to
read a short request, which look to choose, how to lay out the route with prices, and what the pitch message holds.
Playbooks (`playbooks/*.md`) say what differs per project type; read the matching one first.

## The first reply

One line from the person is enough to start. The first reply is short: one sentence on what you understood, the rough
size and cost (`SKILL.md`, Cost), the run-or-stages question, and one line on notes (the review room, a page on their
own computer where they click on a frame and leave a note; people who are not told it exists never find it).

- If their message already answers the question ("just make it", or they ask to see each step), do not ask it again:
  say which way you are going, give the size, and ask only for the go on that.
- The first reply may carry **one** more question, only if the answer changes what film gets made (which company a
  name means, what the product actually is). Everything else you would have asked (format, where it posts, who
  audits the brand) you decide, state in a line and mark as yours.
- On a run, everything a person would otherwise be shown on the way (the test picture, the character's motion, the
  cut before moving shots are paid for) you judge yourself, in the same order, and say what you decided. Moving shots
  are still paid for only after the picture cut passes your own review.
- Either way the first take is not the last word: treat notes as the next take, not as a failure.

## The brief

Get, from the conversation or with at most one question: the **subject**, **who it is for and where it posts** (this
sets length and aspect) and **any assets** (logo, product screenshots, photos, a song, a character). For a brand or a
product, the brand pack comes first (`references/brand.md`, "Before the pitch"). For a product, offer the real-product
route up front (`references/real-product.md`). If the person gave a reference video or link, study it first (below,
"A new style from a reference").

**What is true today: check it yourself, before the pitch.** When the request names a feature, a number or a claim
("it works with agents", "twice as fast", "free forever"), look for it on the product's own site and help pages, and
write three lines in the brief: what the product really does today, what the request says, and the gap. If the claim
is not there, say so in the first lines of the pitch and ask the one question that settles it: does it exist, is it
coming, or is this a spec film for a direction? Do not build on a feature you could not find without that answer.
Every screen that shows something the product does not do yet is an illustration: say which ones in the delivery
note, so nobody posts it as a product capture. On one product ad the requested feature was nowhere on the brand's
site; four cold readers marked the storyboard down because it "felt invented", and one question to the owner (it was a
coming feature) settled what three rounds of rewriting could not.

**The one takeaway:** the single sentence a viewer should remember ("Sound for every hour."). Watch for brief traps
that produce long, dense, forgettable videos, and push back gently:
- **Many goals at once** ("introduce us, explain the product, how it works, the innovation, why it's disruptive").
  Pick one; the rest go in the caption or a second video.
- **Long length for a feed** (2+ minutes for an explainer). Offer 30–45 s; keep long only for story films or art
  pieces.
- **"Show off the motion design"** as a goal. Craft serves the message; it isn't the message.
- **"Explain how it works, but keep the secret sauce."** Don't draw a vague mechanism. Show the **effect** instead:
  before vs. after, the pain vs. the relief, many things becoming one.

## The look

For a brand, a product or a launch, the look comes from the brand and the idea, not from the style menu: say which
look you chose and why, and move on (`references/brand-pass.md`); a style file is at most a reference for structure
and motion. For a song, a story or an open subject, open the gallery (`<studio>/gallery/gallery.html`; `open` on
macOS, `xdg-open` on Linux, `start` on Windows) so the person can see the styles, name the two or three that fit and
your pick in plain text, and let them choose. On a run, pick and say so. Read only the chosen style's file.

**The part that explains the product is where a film gets called "AI-looking".** Before designing it, read
`references/directed-look.md`: choose the way of explaining that fits the film's goal, show the real thing each step
made instead of an invented picture of it, turn a list into one picture that changes, and only then style it.

**The gallery shows only the studio's own renders, never frames from other people's videos** (reference videos stay
in a study folder outside the studio). Every card carries the same story, THE PAPER BOAT, in two frames (A: setting
out at first light, boat lower-left heading right; B: the storm peak, one big diagonal wave from upper right) rendered
in that style. Sources live in `gallery/previews-src/<id>/boat.html`, with the shared brief at
`gallery/previews-src/BOAT-BRIEF.md` and the renderer `gallery/previews-src/snap.mjs`. When adding a style: write the
style file, add the card, render the two boat frames from the brief before the card ships; the render doubles as the
style file's proof that it works (`references/adapt-a-style.md`).

| Style | File | Best for |
|---|---|---|
| Watercolor character | `references/styles/watercolor.md` | stories, music videos, anything with a character and a journey |
| Clean kinetic explainer | `references/styles/explainer.md` | a product or idea in 15–30 s, SaaS, launches |
| Image-to-game cinematic | `references/styles/image-game.md` | "the model built a game from my images", featuring a real person |
| Manifesto film | `references/styles/manifesto.md` | announcing a company, initiative or thesis: fact, story, turn, numbered vision, callback |
| Dark premium explainer | `references/styles/dark-premium.md` | serious tech/AI concepts, B2B, investor-facing |
| Editorial HUD film | `references/styles/editorial-hud.md` | brand films and art pieces: model-generated fashion footage + code HUD overlay |
| Broadcast title sequence | `references/styles/title-sequence.md` | lineups, comparisons, multi-feature launches, event openers; beat-locked kinetic type |
| Kinetic lyric video | `references/styles/kinetic-lyric.md` | music videos where the words are the visuals; Hebrew/RTL notes inside |
| 3D teaching song | `references/styles/teaching-song.md` | a song that teaches a book/course/product, lyrics demonstrated in a 3D world of the subject |
| Painterly glow music video | `references/styles/painterly-glow.md` | emotional songs: brushstroke skies, a glowing figure, symbolic scenes |
| Cinematic animated short | `references/styles/animated-short.md` | wordless emotional stories, 1–3 min, letterboxed, story pitched and approved first |
| Monochrome launch film | `references/styles/monochrome-launch.md` | fintech/crypto/premium-tool launches: b/w section inversions, liquid chrome, quant charts, one gold moment |
| Crayon storybook | `references/styles/crayon-storybook.md` | history/science "X in under a minute", kids' subjects, family films; safe when characters must move a lot |
| Paper cut-out | `references/styles/paper-cutout.md` | songs, histories, warm brand stories; layered paper with real shadows, puppet-pivot motion |
| Pixel art film | `references/styles/pixel-art.md` | nostalgia, game-flavored spots, lofi loops; hard grid, dithered palettes, sprites on ticks |
| Hand-drawn sketchbook | `references/styles/sketchbook.md` | intimate stories and build-up explainers; self-drawing line and hatching |
| Glossy chrome showreel | `references/styles/chrome-showreel.md` | launches and brand stings; liquid metal on poster fields, beat-locked vignettes |
| ASCII / CRT terminal | `references/styles/ascii-terminal.md` | dev-tool launches, technical audiences; character-density scenes, prompts as narration |
| Ink wash (sumi-e) | `references/styles/ink-wash.md` | contemplative, heritage, calm-authority pieces; brush dilutions, negative space, one seal |
| Animator's pencil test | `references/styles/pencil-test.md` | craft/process reveals, character reveals; doubles as the character motion test |
| Riso pop | `references/styles/riso-pop.md` | satire, meme-dense music videos, AI commentary; three-ink halftone overprint, one gag per line |

The paint medium (`references/paint-medium.md`) and the path-traced route (`references/pathtracer/README.md`) are
media, not styles: most painted looks above can be made in the paint medium; felt, paper, clay, glass and smoke in 3D
are the path tracer's.

**A new style from a reference.** If the person brings a video they love that fits none of these, reverse-engineer
it: extract a contact sheet (`bash <studio>/tools/contact-sheet.sh <video>`), read a few full frames, and write down
its design system (background, accent, fonts and their jobs, texture, motion, pacing, beat length). Build to that. If
it is good, offer to save it as a style: follow `references/adapt-a-style.md` (analyze 2–3 frames with
`tools/analyze-style.mjs`, look before trusting numbers, write the recipe with provenance, prove it with the two PAPER
BOAT frames, then add the gallery card, the row in the table above and the `examples/INDEX.md` row).

## The pitch

Run `references/concept-check.md` on the leading idea first, and `references/page-or-picture.md` on its storyboard.
It is the cheapest place to catch a film nobody wants to watch: two films that passed every technical check were both
rejected as having nothing to say.

Before any code, show:
- **The one idea** in a sentence, and the payoff (the moment people rewatch or share).
- **The words, timed, before the storyboard.** If the film has a voice, write every spoken line first and count it:
  about two words a second plus the gaps between lines. The shot times come from that count. A voice written after
  the storyboard moved one film from a pitched 33 seconds to 41, and every shot had to be re-timed twice.
- **The storyboard**: a table of shots with times, what happens, the reads the viewer must get, any on-screen words,
  and the transition out.
- **Length and format** (default 15–40 s, 16:9; add 4:5 or 9:16 when it posts there, `references/vertical.md`).
- **The route, best first** (below), with prices and the expected ceiling of each.
- **Music** (below).
- For comedy: the lines or gags, each tied to a moment. A line is funny when it **contradicts what's happening on
  screen** (a knocked-out salesman still asking "So... next Tuesday?"), not when it's just a familiar phrase.
- **The format** (`references/formats.md`): a linear film is not the only shape. When it fits, offer an interactive
  artifact filmed in use, a one-continuous-zoom piece, a "the film draws itself" reveal, a model-vs-model duel, or
  production receipts in the caption (measure tokens/hours/cost during the build so the receipts are real).

Offer 2–3 ideas if the subject is open. In stages, wait for a yes or edits on all of it: this checkpoint is cheap,
rebuilding a finished film is not. On a run, post the idea and storyboard as a note, marked as your choices, and wait
only for the route and its cost; if the best route is free, say so and keep going.

Put the pitch in a normal message and let the person read it before asking anything. A question dialog sent right
after it can cover it ("did you show me something? I didn't see"); ask follow-ups in plain text.

### The route

Read `references/toolbox.md`. First decide what would make the best film for this subject as if cost did not matter,
and pitch that. It is usually a mix: code for type, motion, the product's screens and the finishing; real-looking
pictures where the film needs people, places or the product out in the world; moving shots from a video model on the
few hero moments. Then lay out the routes, one line each, with what the film looks like on that route, its expected
ceiling and its price read from the real price list:

1. **Code plus pictures plus moving shots** (a video model): costs credits; say how many shots and the total.
2. **Code plus real-looking pictures** made for this film by an image model; code gives them motion. Before the pitch,
   check what the person already has: Codex on a ChatGPT plan (`codex --version`, `references/toolbox.md`), an image
   or video service connected in the session, a logged-in service in their browser. Say in plain words what they have
   and what it gives them. If they have none and the idea needs pictures, name the kinds of service that would do it
   with what each costs, neutrally (`references/services.md`); the person chooses. They always log in themselves:
   never type a password or a code. Do not drive a website whose terms restrict automated use. Stock or
   free-licensed photos from the web are not this route: never offer them in its place.
3. **Code only**, in the style that suits the idea best: free.

Judge by what the person wants the film to be, not by what is free. A film meant to look filmed (people, places, the
product out in the world) usually needs real-looking pictures or moving shots to reach 8 or more; code alone tops out
about 7 there. An illustrated, painted or kinetic-type film is the exception, where code is the best look. When the
idea does not need pictures or moving shots, do not bring up these services at all.

For a product that lives on a screen, whichever route is chosen is built on captures of the real product
(`references/real-product.md`): free, and it needs their login and a browser you can drive. Say so with the routes.

Recommend the one you believe in and say why, then ask the one services question from `references/services.md`: which
services are OK to use and whether there is a cap. Do not quietly fall back to the free route because it is free: a
person who is never offered the better film cannot choose it. If they have no budget, pitch the best film no money
can make, and say what the paid route would have added. Never spend credits without a yes on the number.

**The expected ceiling of each route**, in one line each (e.g. "code + free stills: strong, about 7/10 against this
reference; + 5 video clips for the hero moments: about 9, costs N credits"). The person picks the ambition knowing the
price.

### Music at the pitch

- **A product or launch film, or a request for just "music":** pitch an instrumental, either from a song service
  (they generate it from your prompt, or you drive their logged-in account with their yes on the cost) or a bed
  composed in code, free (`tools/music.mjs`, `references/music-engine.md`), fitted to the film's exact length.
- **A story or a film built on its words:** the default is sung. Offer a song whose lyrics are the film's own lines
  (the story sung, hook words on the beats), with an instrumental as the fallback. On a whiteboard-product film the
  person had to ask why the song had no sung lyrics; the sung version then drove the whole edit.
- **The person brings the song** (music videos, album work): the song is fixed; map it before the storyboard
  (`SKILL.md`, Map).
- Sound effects alone read as "no sound" to a viewer. Offer hits on visual events in the pitch (`references/audio.md`).

## The storyboard, drawn

After the yes on the pitch and before the build, draw every shot: one rough frame per shot, in order, on one sheet. A
table says what happens; a drawn frame shows whether the shot works, and fixing a frame on the sheet costs seconds.
- **Pictures route:** a quick pencil sketch per shot from the image model, in the framing of the final shot, at its
  cheapest or free setting (part of the services question). The real picture is then made from each approved sketch,
  keeping its composition.
- **Code route:** a blockout frame per shot rendered from the page (`render.mjs --stills`): the ground, the big shapes,
  where the type sits. No polish.
- Tile them with `bash <studio>/tools/storyboard-sheet.sh <frames folder> storyboard.png` and show the sheet. In
  stages, wait for a yes or edits. On a run, read it yourself the way a stranger would, fix what does not read, and
  post the sheet with the director's line.

## Why these rules exist (lessons from real attempts)

- **Nice is not enough.** A clean UI parody, a code-drawn watch, a 2-minute product explainer: all "good", none
  stopped the scroll. What worked had one idea, a strong look, a character or face, and a payoff.
- **The viewer sees it once, at full speed, on a phone, often muted.** Timing and legibility fail far more often than
  drawing does.
- **The person's name is on it.** Never add a theme, joke, character or target they didn't ask for (a surprise
  opponent character once derailed a whole project). Offer ideas, mark yours as yours, let them choose.
- **Claims must be true.** "One prompt" and "one-shotted" only if literally so. Hand edits are fine; the caption just
  says so.
- **The person's reference is the style.** A brief written by another tool is an input, not the look. The first pilot
  of an app-builder music video followed a helper's toned-down brief ("limited panels, no countdowns") and came out
  as a flat brand page; the person's reference was a dense editorial HUD film. Put the reference and the brief side by
  side; where they disagree on the look, the reference wins or you ask. But keep the brief's brand facts (palette,
  fonts, lines): they are why the final film looked 1:1 like the brand's own marketing video.

## From good to mind-blowing (what actually moved the score)

An app-builder music video built with code plus 21 free stills scored an honest 7/10 against its reference. These are
the gaps that held it there and the levers that close them. Plan them at the pitch, not after the render.
- **Show, don't tell: the real product is the star (product videos).** A code-redrawn copy of the UI is telling; the
  real product doing the thing is showing, and it reads as "this is real" in the first second. A physical product's
  star is the brand's own product pictures, used as they are and as the reference for any generated picture of it
  (`references/real-shots.md`), never a code redraw of the object. For a product on a screen, default to the
  real-product route (`references/real-product.md`); code adds only what the product can't: camera, cursor
  characters, type, sound, the payoff. Headlines then caption what the viewer is already seeing.
- **What's inside the product tells the story.** A real product showing only text is still telling. Fill it with the
  story's visuals the way the brand's own marketing shots do, and answer the hook visually in the first reveal.
- **Motion where the viewer looks.** Stills that zoom, shake and cut cap a photoreal film at about 7. Put real motion
  on the 4–6 hero moments: short video-model clips (price them), code-animated characters, or at minimum burst frames
  (`references/styles/editorial-hud.md`). Tell the person this ceiling when they choose the route.
- **Music drives the edit.** Cut on the song's measured beat grid, land hook words exactly when they're sung, and put
  the story's turns on the song's silences (`references/audio.md`).
- **Sound design by default.** Hits on every visual event (flash pops, flap clatter, key clicks, the send, the logo).
  Code knows every frame, so they land exactly. Offer them in the pitch.
- **Score it against the reference before the person does.** Frames side by side with the reference, a 1–10 score,
  and the three biggest gaps either closed or priced (`references/quality-checklist.md`).
- **Details viewers feel without naming them:** a punchy grade (no milky whites), no still held past about 4 s without
  a cut or burst, faces always clear, UI sitting exactly in its screen, the brand's real fonts, colors and logo.
