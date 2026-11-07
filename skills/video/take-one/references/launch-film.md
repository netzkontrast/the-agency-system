# Launch and product films: the shape that works

For a film that launches a product, an app, a brand or a feature. It comes from studying launch films with hundreds of thousands to millions of views, and from building one of our own through twenty-one cuts with its owner. A style file says how frames look; this says what goes where.

## The order
1. **Hook**, 3 to 5 s, under a tenth of the film: the viewer's own situation, shown, in a few big words. One clear story with one set of people, not a run of handsome pictures.
2. **Name the product**, right after the hook, with the full frame for about a second.
3. **Show it working on one example.**
4. **Features, each shown on that same example**, one per shot.
5. **The example at scale or out in the world**: the result where real people would meet it.
6. **End card**, about 4 to 5 s: the mark, the name, one line, and where to get it from the first second.

Total 30 to 60 s for a feed. The product and its result fill at least half.

## What the strong ones share
- **One hero example for the whole film.** The same product, the same people, in every shot.
- **The real-looking part is the result**, and it sits inside a calm designed frame. It is never the whole film.
- **The product is shown as small pieces, one per shot**: one control, one prompt box, one number, with a large cursor. A whole screen at once is a screenshot. For a product the person can log into, capture the real thing (`references/real-product.md`).
- **Few words, always big.** Two to five on screen at a time.
- **A plain ground**, light or near black, taken from the brand. The colour comes from the results.
- **Things on top of the pictures**: type that passes behind a person, a word that is the window onto the shot, a line that holds while pictures change behind it. Pictures with captions under them read as a template.

## What went wrong on ours, so check for it
- **The explaining part wore the default look.** The ad was praised; the stretch that explains the product was called "like every AI video, the same pattern, the same structure": one panel layout repeated for each of twelve jobs. Two restyles of the same layout (a paper desk, a lit 3D stage) did not win the owner over either: the repeat was the problem, not the styling. Design that stretch with `references/directed-look.md` before building it, starting from real launch films and the film's own real material.
- **One layout for too long.** If a stretch of more than ten seconds keeps the same frame (a bar on top, a panel, a line bottom left), break it with the result at full frame.
- **A sag in the middle.** Several same-shaped sentences in a row. Merge neighbours into one build and give the time to the strongest beat.
- **The same effect twice.** Each repeat of a pattern (four colours, three reasons) gets its own treatment.
- **The people never come back.** If it opens on people, let them be seen again near the end.
- **A long tail.** After the payoff, everything is short.
- **A film inside the film** needs a clear door: a line or a visible player, or viewers lose where they are.
- **Trust.** Nothing on screen the product does not really do. A number that looks invented costs more than it gains.

## A shorter cut of a film that exists

When the full film feels long, or the brief is a teaser. Learned by cutting our own 85 s launch film down through seven takes, five fresh reviewers (6.5, 7, 7, 7, 7) and the owner's notes between them. None of the short silent cuts passed. What follows is what each round taught.

**The order that held**
1. **The result first, from frame one**, inside a calm frame, 3 s, under one line that makes the viewer ask how. Open on a face if the piece has one: a product close-up read as "a render", a person read as a shoot.
2. **What the person does.** One prompt, typed, the only typed text in the film. The prompt names what the result shows: "make a launch film" followed by a headphone ad lost the viewer, the brand's name in the prompt did not.
3. **The name, early.** A cut that kept the name for the last three seconds was told: "leave before second 25 and you never learn what made it."
4. **The work, shown, each job with its turn.** A list of twelve names was "the one templated moment: twelve equal labels, nothing working". Half a second a job was "too fast", "rushed". One to three seconds each, with the job's real work in the frame, is the film.
5. **The gate.** The reviewer scores the cut, finds it short and sends it back. It is the beat that makes the promise believable, so it gets four seconds, not one and a half.
6. **The result again, at the whole frame, on the music's drop.** The payoff in the same box as the opener read as no payoff.
7. **The step back**, when the outer film was made the same way as the inner one: the picture shrinks back into its frame, then that whole screen shrinks into the same frame under the same headline. It needs both screens to share one layout, or the second frame is only a border.
8. **End card**, the name on the hit.

**What else it cost us to learn**
- **Shorter is not better.** The 28 s cut scored the same 7 as the 20 s one and the owner's note was one line: too fast. Ask how long the story needs before asking how short it can be.
- **Do not drop the voice to save time.** The long film had a narrator the owner had chosen. The short cuts left her out, nobody was asked, and the owner had to ask twice why. If the film has a voice, the short cut is built on her lines: each picture lasts as long as its line takes to say.
- **Proof that arrives after half the film is late**, however good the rest (proof at 53 %: 7).
- **A real stretch of the finished piece beats a re-cut of flashes.** Let it play on its own beat grid, with its own voice.
- **One headline line for the whole film**: one place, one size, its words roll while the pictures change under it. It replaced four layouts and the note "mechanical flips".
- **Cut the music as little as you can.** One stretch of the track whose own shape (quiet, build, drop, break, drop, last hit) carries the film's turns beat the same track cut into six. Repeat a few bars of its intro if the film needs a longer run-up.
- **A hit must be seen.** A full-frame flash on the clap hid the clap; two inverted frames with the object still on screen keep the flash and show the hit.
- **Footage of your own screens, shown small, needs its own crop for each moment.** One crop for all twelve left the work floating "small in empty black".
- **Nothing inside a frame may be cut by the frame.** A card, a panel, a label or a row of thumbnails that touches the player's edge reads as a mistake, however good the crop felt ("the right part of the black screen is cut", three notes in one round). Do not crop by eye: `scripts/content-box.py <video> <start> <seconds> --rest` measures the content box of a moment and prints the crop that keeps a clear margin round it; let the strip be shorter than the player rather than cut. A long timeline may run off the edge in a close-up that is moving; a box with a border may not.
- **Two films side by side read as a comparison, not as "this is inside that".** Our two-player frame for "it made that video, and the one you're watching" was called "very confusing". What read: one thing at a time. First the inner film alone in the player, over the line that made it. Then one step back: that whole screen becomes the picture in the same player, over its own line, and rewinds through everything the viewer has seen. Name each film by the line that made it; a file name under a player explained nothing.
- **A film shown inside the film is shown whole, with its own sound.** Four seconds of the ad, four portraits with one word each, "does not feel like an ad". Seven seconds that opened on the product with its name said aloud, then the people, with the narrator coming back over the rest, was no better: "it says just random words". What the owner had liked in the long film was the whole 15 s spot, with its full voice and its own music, and nobody talking over it. So give it its length, stop the narrator and the outer film's music for it, and use its own finished sound untouched (`audio.md`, "A finished film inside the film"). Say what it does to the length before building: ours went from 63 s to 71.5 s. After it ends, the outer film may play it again small (in a post, in a player) from its first full picture.
- **The first frame carries the first words, and the first shot really moves.** Our opening scored 7 four takes running: stills with a push, then one still made into a depth shot. The notes were the same from the owner and from the reviewer: it does not move, and frame 0 has no words. What changed it: real footage of the finished product (clean: the "workshop" picture with dust and scuffs read to the owner as rust), the first words on frame 0, the big word landing on the music's downbeat.
- **A pictogram of people needs heads apart from shoulders, and an overlap.** Three equal columns with a dot on each read as a bar chart ("no crew" was called that). Two figures behind and one in front in the accent colour read as a group.
- **Inside a player, a row that stands still gets the same margin left and right; a strip that slides fades out before the edge.** A face cut in half by the player's edge and a label chopped as it slid out were both called out in one review.
- **The opening gets its own shot, not one borrowed from the film inside the film.** We opened two takes on the ad's own product shot because it was the cleanest moving shot we had. A reviewer then counted the same close-up four times (opening, inside the ad, in the post, at the end of the rewind) and said the rewind "lands on a near twin of the ad's own shot". The fix was the same product in the maker's world (workbench, sketches, tools), one free picture and one short render: the opening now says "you built this", and the return to the first frame cannot be taken for the ad. With that shot and a giant word on every spoken beat, the hook went from 7 (four reviewed takes running) to 8 and the take was the first to pass.
- **Do not open on the finished result if the film's turn is the reveal of that result.** Showing the ad in the first seconds and again at the reveal read as "showing this and then the final video again". Open on what the viewer has (the thing they built), keep the result for its moment.

## Before pitching: the competitor study (the strategist's job)
For any product in a category the viewer already knows, and always when the person asks for it:
1. Find the two or three closest competitors and, for each, its main product or launch video (its site, its own channel, its ads).
2. Look, do not guess: a contact sheet and a few full frames of each (`scripts/contact-sheet.sh <video>`), its length, how fast it cuts, what the first three seconds show, who is on screen, how the product is shown, how it ends.
3. Write `COMPETITORS.md` in the project: one short block per film, then two lines: what this category always does, and where this film will do the same or differ and why.
4. Say those two lines in the pitch.

"In a similar style to the competitors" means the category's structure, pace and kind of shots. The look (colours, type, logo, lines) stays the brand's own, from the brand pack in step 1b, not from the style gallery. Never use a competitor's pictures or lines. The strongest competitor film is the reference for the bar check in step 5; with no reference at all, skip the side-by-side and say so.
