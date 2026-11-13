# Critique, round 1: storyboard (8 s pipeline smoke test)

Read: `STORYBOARD.md`, `review/storyboard-sheet.png` (frames t = 1.0, 2.6, 4.6, 6.5, 7.8), `songmap/beatmap.md`,
`songmap/words.json`, `BRIEF.md`; craft refs per the critic brief. Locked: song, lyrics, abstract shapes only, 8 s.

## Retelling (as a viewer)
Seven paper-and-ink shapes bob on a paper floor while a voice sings "lass mich, lass mich atmen". On "atmen" they
all burst outward at once, like a breath out. Then the camera pushes in on one shape, which keeps turning, and the
picture fades to blank paper.
The retelling works from the board. **From the sheet it breaks at sentence 3:** the shape the camera chooses is
the orange icosahedron, not the teal knot (see BLOCKING #1).

## Scores (1–10)
- Idea: 6. One clear gesture (breath out on the word). It is honest for a smoke test but thin as a film.
- Arc: 5. Crowd, breath, one chosen, gone. There is no inhale to set up the breath and no rhyme from open to close.
- Timing/readability: 6. The reads are one at a time, but the final hold is too short and lands off the release bar.
- Escalation: 5. Not applicable (no returning chorus in 8 s); scored on build alone. Nothing tightens before the release.
- Sync plan: 7. "atmen" sits on its stress (2.5 s = transient #5, on beat) and "ich" sits on 4.0. "hier" (5.0) and the release downbeat (7.507) are unused.

## Page or picture (per shot)
| # | P/G | E/S | note |
|---|---|---|---|
| 1 | P | S | "drift and bob" is a state |
| 2 | P | E | breath out |
| 3 | P | E→S | push-in (event), then 1.8 s of "keeps turning" (state) |
| 4 | P | E | fade |
0 pages, 1 of 4 states (25 %). Under the one-third line; passes.

## BLOCKING
**#1 · shot 3 · 00:04.0–00:07.0 · the sheet contradicts the board on the film's one choice.** The board says the
camera "holds on the teal knot", and BRIEF's takeaway is "a camera that finds one shape on 'ich'". On the sheet at 4.6 s
the teal shape is cropped at the right edge behind the yellow icosahedron, and the orange icosahedron fills the
lower left. At 6.5 s the orange icosahedron is centred and big, and the teal knot is a cut-off sliver in the top-left
corner. A viewer will name the orange shape as the chosen one, or will not know that a choice was made. The breath
out at 2.6 s also throws the teal knot half off the left edge (cut by frame, before-the-first-cut §6), so the chosen
shape leaves the frame at the payoff. **Fix:** make the push target the teal knot's world position at 4.0 s (or
retarget the spring to follow it). The teal knot ends centred and fills about a third of the frame by 5.0 s. No other
shape is bigger or more central in the held frame, so push the orange icosahedron out of shot or keep it small. In
shot 2, keep the teal knot's breath-out vector inside frame. Re-draw the sheet at 4.6/6.5 to prove it. (Or, if the
orange icosahedron is the intended choice, change the board; either way the two must agree.)

## NOTES
**#2 · shot 1 · 00:00.0–00:02.35 · no setup for the payoff; the opening is a state.** The breath out has no inhale
before it, and "drift and bob" is a state. **Fix:** make "lass mich" and "lass mich" two small contractions (shapes
draw in a little toward centre, stressed syllables 1.5 s and 2.04 s; 1.5 is also the bar-2 downbeat). The breath out
at 2.5 then pays off a held-in tension. The anticipation at 2.35 becomes the last and deepest inhale.

**#3 · shot 1 · 00:00.0–00:01.0 · the chosen shape has no setup.** The teal knot is the largest shape at 1.0 s, but
nothing marks it. **Fix:** one small, distinct beat for it in shot 1, for example it bobs a half-beat late or turns
while the others only bob. The choice at 4.0 then pays off something the eye already met.

**#4 · shot 2 · 00:02.35–00:03.1 · two motions at once.** The orbit continues ("continuous camera") while every shape
springs outward. The eye gets the camera move and the expansion together. **Fix:** ease the orbit to near-stop from
2.2 s to 3.1 s so the expansion is the only motion, then resume the orbit for 3.1–4.0 (the voice holds "atmen" to 3.1).

**#5 · shot 3 · 00:04.0–00:05.2 · the push lands after "hier", not on it.** The push of 1.2 s settles at 5.2 s. The
stress of "hier" is 5.0, so the line's last word gets nothing. **Fix:** push 4.0→5.0 on the `camera` spring (~0.55 s
settle, so start the retarget so it is at rest by 5.0). The arrival lands on "hier".

**#6 · shots 3–4 · 00:05.2–00:07.9 · the final payoff holds under 2 s, and the fade is off the release bar.** The
hold is 5.2→7.0 = 1.8 s, and the fade starts at 7.0, half a bar before the release section (downbeat 7.507). The last
read (the dissolve) is about 0.9 s. **Fix:** with #5 the hold runs 5.0→7.5 (2.5 s). Start the fade on the release
downbeat 7.507 and end it at 7.95, so the release bar *is* the dissolve. The chosen shape is the last thing to fade.

**#7 · shot 3 · 00:05.0–00:07.5 · stillness as safety.** "It keeps turning" is a state for 2.5 s. **Fix:** give the
hold one small event tied to the beat. For example, the knot makes one slow breath of its own on the bar-4 downbeat
(5.532, transient #4). That makes it a solo echo of the group breath and keeps it alive.

**#8 · shots 1/4 · 00:00.0 and 00:07.9 · the ending does not rhyme with the opening, and frame 0 is a hard start.**
The film ends on blank paper but starts cold on the full scene (paint-medium rule 6: no hard first frame). **Fix:**
open from the same blank paper and bring the shapes up in 0.5 s on beat 2 (0.507, transient #10). The film then runs
paper → crowd → one → paper, and frame 0 still reads within the first second.

**#9 · all · muted viewer.** Locked: the German lyrics. The takeaway depends on hearing "atmen" and "ich", and the
board plans no subtitles (none planned; the medium allows no painted words by default). Muted, the viewer sees shapes
expand and a camera choose, with no reason. **Fix:** producer's call. Plan a `.srt` (`studio srt`) from
`songmap/words.json`, or accept it, since this is an internal smoke test.

**#10 · board · tempo low-confidence.** `beatmap.md` flags 120 vs 60 BPM as low-confidence. The plan relies on
120-BPM beats (half-beat bobs, the 7.507 downbeat). **Fix:** confirm 120 by ear once (the kicks at 0.5 s spacing) before
animating. If it is 60, the bob rate halves.

Checked and clean: no handoff seams (one chapter, ch01; the shot 2→3 camera is continuous). No text, faces, names or
claims. No bodies (abstract only, per BRIEF). Every time is in or derived from the song map. No chorus or bridge
falls in the 8 s window ("das war", the chorus, starts at 8.0, at the film's end).

## Keep
- The breath out landing on the stressed syllable of "atmen" (2.5 s, on beat, 0.15 s anticipation).
- One gesture per shot, and one chapter with no cuts.
- The paper floor, ink lines and the seven-colour set. They read clearly at thumbnail size on the sheet.
- The fade to paper as the ending gesture (move it onto the release bar, #6).

## Verdict
**REVISE**: 1 blocking, 9 notes.
