# Vertical 9:16 (Reels, TikTok, Shorts): recompose, don't crop

Learned on an app-builder music video (Sep 2026). A center crop of a 16:9 film loses the subject, buries type under the platform UI and puts panels on faces. Rebuild the layout per shot instead; keep the timing identical.

## One timeline, two layouts

- Same `film.html`, same shot list and word timings. The page reads `?portrait=1` and sets `W=1080, H=1920`.
- Every layout number goes through `PV(landscapeValue, verticalValue)`. The landscape value stays exactly as approved, so the vertical can't break the master.
- Textures sized to the frame: grain and halftone canvases get the portrait aspect, or they stretch.
- Render: `W=1080 H=1920 node frames.mjs 1 <times>`, export with `W=1080 H=1920 node export.mjs 24 out.mp4` (export adds `?portrait=1` when H > W).

## Framing photos (stills or footage)

- A 16:9 photo covering 9:16 shows only about a third of its width. Pick the visible third per photo: a focal x in plate units (the subject's center), clamped so the photo still covers the frame.
- Plate coordinates stay in the photo's own space (e.g. 1920x1080 units) with separate x and y scale (generated stills are rarely exactly 16:9). Every tracked box, screen quad and face box maps through the same transform in both layouts.
- To free space under the chin, anchor the zoom at the bottom of the photo: the face rides up and the jacket or table below becomes clean space for type.
- A wide shot with the subject on one side can pan: the first half on the environment (the wall of notes), a cut on the beat to the subject.

## Where things go

- Essentials (type, captions, cards, boards) inside x 56-940, y 250-1480 on 1080x1920. The top bar, the caption and handle block at the bottom, and the button column on the right cover the rest. HUD decoration can live there.
- Never on the main character's face (see the face audit in pipeline.md). Free space in a portrait is above the head or below the chin; put big type there, over a gradient scrim if the photo is busy.
- Two-line slams become one line under the chin when the face fills the frame.
- A blank object in the photo (a card, a sign, a screen) is the best place for a word: "I will." written on the blank card she holds read better than type beside it.
- Wide panels (a counter, a report, a confirmation card) become compact full-width strips above or below the subject, not centered blocks.
- Karaoke strips auto-shrink to fit about 900 px wide.

## Check

- Contact sheet of the vertical at the same times as the landscape one, then larger frames of every shot with type near a face or an edge.
- Face audit in 9:16 (and again in 16:9 if you touched shared code).
- Sample the exported MP4 itself (a frame every 2 s) before delivering.

## A film built round a player (a headline over a wide screen): what the tall layout became

Learned on the short Take One launch film (12 Oct 2026): a headline line over a 16:9 player on paper, twelve small objects in a row inside the player, a 15 s wide ad shown whole, and an ending where the whole screen becomes a video in the player.

- **Draw the player's inside once.** Do not re-lay every number inside the player. Keep the wide film's numbers for everything inside it and wrap that drawing in one transform (`stage()`: translate to the tall player's corner, scale by tall width / wide width, translate back by the wide player's corner). Only what sits outside the player gets tall values.
- **The headline gets a second line, not a smaller size.** One line across a 884 px column forces about 75 px type. Two lines hold 92 px: a long line is split by hand ("a launch / needs a video"), and a numbered item puts its number alone on the upper line, large and in the accent colour, with the name under it. Each line rolls inside its own clip band, the bands share no row (keep about 14 px of ground between them), and a change is out, then in: the old lines leave in 0.09 s and only then do the new ones rise. Two lines rolling at once print on each other for five frames where one band ends and the next begins, and a reviewer stepping through frames sees it.
- **Use the height for the thing the wide film had to keep small.** The row of twelve objects left the player and became a grid of two rows under it, twice the size, with three states (waiting pale, done dark, at work raised). An object that flies from the dark screen onto the paper is drawn twice with two clips: light inside the screen, dark outside it.
- **A wide film inside the film becomes a band across the full width, high in the frame.** It cannot fill a tall frame without cutting its words, but it does not have to stay in the column either: as the room goes dark the player rises and grows from the column (884 px) into a band 1080 x 608 at y 290 to 898, half as large again. High, because the apps' buttons sit on the right from about y 880 down and would cover the band's right end anywhere lower (at full width in the middle of the frame, the last letter of the brand's name sat under them); not above 285, because a feed preview keeps only the middle 4:5. The band rises over the headline, so the headline comes back under it once it has landed, with the progress line between them and the line that made the film under that. When it ends, the next move starts from the band, and the next headline waits until the band has left its place.
- **If the inner film opens inside a small player of its own, crop into that player.** An ad cut from a longer film may start with its picture in a window with a file name and a progress line: in the tall band that is a player inside a player, a 14 px label and two progress lines. Read the rectangle and its easing from the source page, check them against the frames (they matched within 2 px), and draw that rectangle of each source frame across the whole band, computing the crop at the source's frame rate (30 a second), not the film's, or it shivers.
- **"The screen becomes a video in the player" needs a tall player**: the nested picture has the frame's own shape. Use a second rectangle for it; do not squeeze a tall screen into the wide player.
- **A wide clip as a tall opening, without paying for a new one:** lay it in whole (scaled so the subject keeps a margin at both sides), low in the frame; carry its out-of-focus wall on upward as one sampled colour with a gradient over the clip's top 230 px, and its floor or table downward by drawing its last rows out; put the type on the wall. It reads as one tall room. Say what a tall shot of its own would cost.
- **Scenes that are centred (a title, a slate, an end card) stay on the frame's true centre**; scenes built on the column sit 42 px left of it. Nobody sees the shift; the right edge belongs to the apps' buttons.
- **Prove the wide film did not change.** Before the first tall edit, save a checksum of thirty-odd wide frames; after, render them again. Expect one or two text-heavy frames to differ by a few pixels at 1 or 2 levels when frames are rendered in a different order (the browser's own anti-aliasing); render those alone, old page and new page, and they must be identical.

What a fresh reviewer then caught on that tall cut (7 overall on the first try), and what fixed each:
- **The subject of the first shot sat under the apps' buttons and caption.** The safe column is for the product too, not only for type: scale the laid-in shot so the whole subject ends left of x 925 and above y 1470.
- **A word's tail fell on a pale part of the picture.** Deepen the fade where type crosses from the added wall into the clip (alpha about 0.93 through the first 120 px), and keep 46 px between a line and the much larger line under it, or their letters fuse.
- **The added wall was flat and the carried-on floor was streaked.** Lay one soft warm light over wall and clip alike (blend "lighter", after the fade, so no line shows where one becomes the other). Carry a floor on by drawing its last rows into a canvas 24 px wide and laying that back large: a smooth run of its colour instead of stretched streaks.
- **Fifteen seconds of a small window on flat black.** Give the dark a job with words the film already has: the headline stays above the player (turning light as the room turns dark) and the line that made the inner film stands under it.
- **A headline rose in under a screen that was still shrinking over its place.** Start the headline when the moving thing has cleared it (0.36 s into a 0.5 s move), not on the scene's first frame.
- **The text audit failed tall films for text that is 22 px on a phone**: it measured against the frame's height. It now measures on a phone 360 px wide (`scripts/text-audit.mjs`), which gives a wide film the same verdicts as before.

What the second fresh reviewer caught (7 again), and what could and could not be fixed without new pictures:
- **A line on screen said "one line" over a prompt typed on two.** When the tall column forces a wrap, check what the words above it claim. The prompt went back to one line at 50 px in a box as wide as the column.
- **Footage inside the player looked small.** Measure before promising a zoom: `scripts/content-box.py` on each strip. Ten of eleven strips already filled the player's width, so only their height was empty, and a zoom would have cut cards at the player's edge. One strip (a picture with room on both sides) could be drawn a quarter larger. Say this plainly instead of cropping: a wide strip in a wide player inside a tall frame is small by geometry.
- **The nested tall screen was the smallest picture in the film.** A tall frame inside a tall frame, with a headline above and a prompt line under it, is about 400 px wide whatever you do. If the ending depends on it, plan the tall cut's ending at the storyboard, not at the recompose.
- **What holds a restacked tall cut at 7** is the opening and the inner film: both were made wide. The reviewer's route to 8 both times was a first shot made tall from the start (taller, closer, real camera movement). Price that shot at the pitch of the tall version, before the free recompose, so the person chooses knowing the ceiling.
- **Third reviewer, same 7 overall, composition up to 8**: with the ad edge to edge, it caught the brand's last letter under the buttons and the small opening window above. Both are fixed by the two rules above. A restacked tall cut with a wide opening and a wide inner film tops out at 7; say so before starting, with the price of a tall opening shot.

## A teaser Reel cut from wide footage: the three-band wall

Learned on the Take One teaser Reel (12 Oct 2026, 32 s, comment-a-word ask). The footage was all wide: a 15 s ad, strips of the studio at work, a gallery of wide stills.

- **Three wide bands fill a tall frame.** 3 x 608 px plus 24 px of ground between and round them is 1920. Top and bottom are pictures; the middle band is a card that carries every word. Words then never sit on a moving picture, and they are always inside the free zone (x 64 to 940, y 656 to 1264). Text on the card is set as large as the card allows (three lines of about 170 px).
- **Open on ONE picture across the whole frame, then cut to the bands on the first beat.** A fresh reviewer scored the bands-from-frame-0 opening 7: "the proof is two small strips". Find the highest-resolution source of the best shot: a 4K clip gives a sharp 1215 x 2160 tall crop (`crop=1216:2160:X:0,scale=1080:1920`, `minterpolate` to 60 fps). The words go on it from frame 0, under the face.
- **Never show a shot twice.** Count the footage against the seconds before laying it out (nine ad shots were 12.5 s; two bands needed 13 s by second 6.5). When the result runs out, show the making: each strip of the studio with its job's name. That also answered "it never shows the skill working".
- **The ask early, on its own card, then a strip along the card's foot.** Second 6.5, an orange card; the word to type is the strongest contrast on it (dark on a paper plate, not cream on orange); say what they get ("and I'll send you the skill"). A tag laid over the seam covered a picture's title; a strip inside the card covers nothing.
- **Make the ending the answer to a promise.** "Wait for the last thing it made" at second 8.7, "And the last thing it made? The video you're watching right now." at 21. The step back and rewind then pay off something the viewer was told to wait for.
- **When variants flip past, say what stays the same**, on screen ("same scene"), and count them large. A name on the card must match what BOTH pictures show for as long as it is up: the named look in both bands (its two pictures), not one band flipping on.
- **Put the big move on the music's section change** (the rewind starts exactly where the outro begins), and plan the cut from an uncut stretch of the track that ends on its last hit: here Reel 0 = the middle of the first drop, the breakdown fell under the promise, the second drop under the flips, the last hit on the clap.
- **Effects under a loud drop are buried**: the mixer refuses them. Drop them (keys, swishes) instead of raising them over a voice.
- **A strip that holds still for two frames fails the gate** when the card beside it is still too: give every strip a slow creep.
- **For Instagram:** deliver a 30 fps copy (the app plays 30), the first frame as the cover with its words inside the middle 3:4, and tick the AI label when the people look real.
- **What the second review (8 overall, hold 7) still caught on that Reel:** the one picture that tells a story (a score going from 6.8 to 8.6) sat in the bottom band, under the caption: put the picture that matters in the TOP band. The ask vanished during the reveal, when the viewer is most convinced: keep it on screen there too. As the ask landed, the pictures fell from glossy shots to dark panels: let the ask land on the best pictures, even if that means one shot comes a second time in the other band. And once a count has reached its end, the next beat must start at once: the question and its answer were pulled 0.6 s earlier.

## A teaser Reel modelled on Reels that won: the light stage (Take One teaser, take four, 12 Oct 2026)

The first teaser (three bands, cards, a twist at the end) passed two fresh reviews at 7 and 8 and its owner still found it weak:
the still images did not impress, and the hook did not show what the skill had made. What the owner asked for next is now the first step for any Reel:
**look at Reels on the same subject that got a lot of views before anything is planned.** A reviewer's score does not stand in for that.

What the winners had, and what the rebuilt Reel took from them:

- **The sentence that opens is news and a gain:** "Claude can now ...", with "free" inside it. Not a riddle.
- **The made thing fills the first second.** Two shots cut tall from the 4K sources fill the whole frame (0 to 1.0 s), then the picture
  steps back into a card. Measure where the face and the product sit in the wide shot and centre the crop on them; a zoom-in settle
  eats the margins, so a face near the crop's edge gets cut ("see the images are not cut on the side").
- **A large card beats a full-width band.** A 952 x 1000 card cut from 1076-high clips is sharp with no upscaling and gives the
  picture 46% of the screen; a 16:9 band gives it 32%. Only 4K sources are sharp at full frame.
- **Every phrase has its own picture, and a real one where there is one:** the sketch of a shot wiped into the shot itself, the ad
  and the film playing in cards with their labels ABOVE them (a label on a picture covered the film's own headline).
- **Spoken words as captions, a few at a time, the word being said in a box.** Whole-take word times from the transcriber were
  off by up to half a second; cutting the take into sentences at its pauses and timing the words inside each sentence was accurate.
- **One ask, at the end,** with the word large, a comment box typing it and the message arriving on the music's last hit.
- **Words stay out of the app's column of buttons** (x beyond 940 from about y 880 down): a wordmark on a plate at y 950 ran under it
  until it was made smaller. Measure the rightmost pixel of every line that sits low.
- **A viral-score tool is not a judge.** Higgsfield's Virality Predictor gave 48 and 47 to two winning Reels, 48 to the rejected first
  cut and 43 to 46 to the rebuilt one; its values are scaled inside each clip, so it cannot rank cuts. Its line for the eye, second by
  second, did show where the screen had only graphics. Use that, quote no target, and say so if a target is asked for.
- **A file cannot be loaded into a web page from a tab that has never been shown** (the browser defers media there). Upload through
  the service's own connector or ask the person to click the tab once.
- **Say what the product is from its own page, on the day.** The teaser spent a whole beat on a count of styles; its owner pointed out
  that the skill is not about a count of styles, it adapts to the brand, the intent and the goal of the project, and that it has a
  review room for notes pinned on frames. The README had said both for hours. Read the product's current page before the
  script is written, and again before the voice is recorded.
- **Show the real tool, captured, when the beat is about a tool.** The review room beat is the real page, shot by a headless browser
  (a short script written for that film: seek the cut, click the picture, type the note, save; one PNG per state at three
  times the size), with only a cursor drawn over it. A page laid out for a wide screen does not fit a tall frame: show its parts
  one after the other, large (the frame with its pin, then the note box zoomed until the typed note is about 40 px high).
- **A note added to the middle of a one-line function cuts off the code after it.** Two patches of the form `...;   // why`
  swallowed a `g.save(); ... clip()` and a plate; the film still rendered and passed the gate, with a plate missing. Put a note
  on its own line, and after any patch look at a frame of the thing patched.
