# Storyboard — Track 13 „Ich bin hier / Das war“

One idea (one sentence): the same room as in track 1, but the door stands open and it is day, and the film holds still while the song says that it is here.
Payoff (the moment people rewatch): the stressed "war" at 50.3 s, when the gold seam in the paper wall takes the light once, and the last view that returns to the opening image of track 1 with the demand gone.
Playbook: skills/video/studio/playbooks/music-video.md   Medium: paint (p5.brush, from the album concept)   Format: 1920x1080, 24 fps, 138 s
Source: `songmap/words.json`, MEASURED from the real audio (`audio/13-ich-bin-hier-das-war.mp3`, 138.12 s; faster-whisper heard the words, `songmap/align.py` snapped them to the streaming lyrics; the 60 bpm heartbeat phase is 0.45 s). v2 of this board: v1 was planned on an estimated map and the real song is laid out differently (long instrumental stretches at 8.6–21.5 s, 95–102 s and 108–125 s; the last refrain line repeats at 125 s). Every time below is read from the song map (`SONG.line(i).t / .end / .key.stress`), so a re-measured map retimes the film.
Lyrics on screen: none. `out/film.srt` carries the words for muted viewers (streaming lyrics only). Locked: no bodies, no names, the child's line is a light and never a figure.

## Look in four lines
- Flat 2D on paper, ink lines that boil at 12 drawings/s, light only through `glow()`, grain on top.
- Palette: paper `#F3EBDC`, ink `#2B2233`, morning yellow `#F2C14E` (light), Kintsugi gold `#FFDF00` (the seam only), Clean Ping `#FCEE0C` (one point, once).
- The room: a threshold (open door, left), a curtain with a light strip (right), a lamp (the heartbeat), a smooth pillow on the floor, a window, a paper wall with one gold seam.
- No alarm, no Signal Yellow, no hit: the heartbeat grid (1 beat = 1 s) is the only pulse, and it slows to nothing at the end.

| # | Time (s) | Section / lyric line (key word @ stress time) | What happens | Reads (in order) | Transition out | Chapter |
|---|---|---|---|---|---|---|
| 1 | 0.0–1.7 | Intro, no voice yet | Fade up from blank paper onto the threshold: open door left, curtain right, lamp above; the lamp glow pulses on every beat | 1 paper becomes a room; 2 a light is breathing | continuous | ch01 |
| 2 | 1.7–8.6 | line 0 "Der Puls ist langsam. Der Puls ist meiner." (meiner @ 7.71) | Same view, very slow push in. The glow pulse follows the beat; on "meiner" the pulse is larger and the paper wash breathes once with it | 1 the room has a pulse; 2 it is the speaker's own | slow ease | ch01 |
| 3 | 8.6–21.5 | Instrumental, 13 s, no voice | The room is shown once, slowly: the camera slides from the door across to the curtain (8.6–15); then the light strip beside the curtain widens like an inhale (15–21.5). Beat glow only | 1 the door; 2 the cloth; 3 the light grows | slow ease | ch01 |
| 4 | 21.5–27.0 | line 1 "Das Gelb hängt in den Vorhängen. Es ist nur Licht." (Licht @ 25.94) | Close on the curtain folds with yellow behind them. On "Licht" the glow stops pulsing and lies even, plain daylight | 1 yellow in the cloth; 2 it is only light | wash over | ch01 |
| 5 | 27.0–32.3 | line 2 "Kein Faden auf dem Mund. Kein Druck, der mich erstickt." (Druck @ 30.17) | Close on the pillow on the floor, smooth; a yellowed thread lies beside it as an ink line. On "Druck" the thread slides off the frame and does not come back | 1 the pillow, bare; 2 the thread is gone | wash over | ch01 |
| 6 | 32.3–38.4 | line 3 "Ich atme ein. Ich atme aus. Niemand verhandelt mit." (aus @ 34.90) | A breath fog (soft watercolour wash) opens on "ein", closes on "aus". One light, one shadow; no second shadow anywhere | 1 breath you can see; 2 nobody bargains | ease out | ch01 |
| 7 | 38.4–44.6 | line 4 "Der Raum ist still. Und ich bin hier." (hier @ 44.14) | The camera pulls back to the whole room and slows to a stop exactly as "hier" lands; nothing moves except the beat glow | 1 the whole room; 2 it is still; 3 it holds | hold into refrain | ch01 |
| 8 | 44.6–46.9 | Refrain line 5 "Ich bin hier." (hier @ 46.17) | Wide, level with the threshold. A slow glow breath. No push, no move | 1 here | dissolve | ch02 |
| 9 | 46.9–48.9 | line 6 "Das war." (war @ 48.24) | Dissolve to the paper wall with its gold seam. On "war" the seam takes the light once: a slow gold glint runs along it and fades | 1 a crack, repaired; 2 it is still there | slide | ch02 |
| 10 | 48.9–56.5 | line 7 "Kein Sieg. Kein Ende. Nur das hier und das, was war." (war @ 56.05) | One frame holds both: the room on the left, the wall on the right. The light strip crosses from the room onto the wall. No flare; the seam stays at 60 % brightness | 1 now and then in one picture; 2 no triumph | dissolve | ch02 |
| 11 | 56.5–61.5 | line 8 "Ich bin hier." (hier @ 58.15) | Back to the room, slightly closer than shot 8; held; the glow breathes | 1 here, closer | wash | ch02 |
| 12 | 61.5–65.5 | line 9 "Ich hab nach Luft gefragt. Ich hab es laut verlangt." (verlangt @ 64.85) | The window pane with breath fog on the glass. On "verlangt" a brush wipe clears the glass; nothing is demanded | 1 fogged glass; 2 it clears | wipe | ch02 |
| 13 | 65.5–70.2 | line 10 "Jetzt frag ich nicht mehr. Die Luft ist einfach da." (da @ 69.84) | The window is open; the curtain moves a little. On "da" it lifts once and settles | 1 open window; 2 air that nobody asked for | dissolve | ch02 |
| 14 | 70.2–74.1 | line 11 "Das, was war, bleibt wahr. Und es bleibt hinter mir." (mir @ 73.87) | The gold seam again; the camera drifts sideways and the seam slides out of frame left, behind the view | 1 it stays true; 2 it is behind | slide | ch02 |
| 15 | 74.1–78.6 | line 12 "Ich dreh mich nicht mehr um. Ich bin hier." (hier @ 78.07) | The threshold from the front; the camera does not turn around. On "hier" it settles | 1 no turning; 2 here | hold | ch02 |
| 16 | 78.6–82.5 | Refrain 2 lines 13–14 "Ich bin hier. Das war." (hier @ 80.08, war @ 82.16) | Same words, new picture: a light travels across the seam and the gold takes it, the room faintly mirrored in the paper | 1 the light moves; 2 the seam holds it | wash | ch03 |
| 17 | 82.5–90.5 | line 15 "Kein Sieg. Kein Ende. Nur das hier und das, was war." (war @ 89.98) | The light spreads over the wall, warm, held at 60 %, no flare | 1 warm; 2 not triumphant | dissolve | ch03 |
| 18 | 90.5–92.8 | line 16 "Ich bin hier." (hier @ 92.16) | Back at the door frame; the room empties of detail: paper, ink, a door | 1 here, with less | fade | ch03 |
| 19 | 92.8–102.3 | Bridge line 17 "Ich bin auch hier." (auch @ 94.15), then instrumental to 102.3 | Everything gone but one thing: a tiny Clean Ping point in the window corner appears once on "auch" and stays alone on the paper through the quiet 7 s after; one more shadow layer on the wall, bright | 1 empty; 2 one light; 3 it joins and stays | slow dissolve | ch03 |
| 20 | 102.3–108.4 | Outro lines 18–19 "Ich bin hier. Das war." (hier @ 104.27, war @ 108.22) | The opening view of shot 1 returns, door open, the point beside the frame; the glow pulses on the beat | 1 the first image again | continuous | ch03 |
| 21 | 108.4–125.1 | Instrumental, 16.7 s, no voice | The long exhale: the room at day, the light lies on the wall and the floor; the curtain breathes twice; the lamp pulse and the point share the beat. Slow drift of the camera away from the door. Nothing is demanded | 1 the room at rest; 2 the curtain breathes; 3 the camera backs away | slow ease | ch03 |
| 22 | 125.1–132.5 | Outro repeat lines 20–21 "Ich bin hier. Das war." (hier @ 128.23, war @ 132.25) | The threshold again, from the front, as in shot 15; on "hier" the point brightens a little and holds; on "war" the room is paper-quiet | 1 here again; 2 that was | fade | ch03 |
| 23 | 132.5–138.0 | Stille: instrumental outro, no voice | The lamp's pulse slows (every 2 s, then 4 s), one last breath fog, then the picture goes to paper. From 136 s blank paper (a declared hold). No "Lass mich" anywhere: only the breath | 1 the pulse slows; 2 the page is blank | end | ch03 |

## Rules this storyboard keeps
- Every line has one picture that carries it when it is sung; the action lands on the stressed syllable of the key word, not on the start of the word.
- Strophes are close, refrains wide, the bridge empty. The two refrains repeat the words and change the picture.
- Counterpoint, not literal: strong words over small, quiet pictures.
- The doubled "Lass mich" of track 2 is refused: one light source, one shadow, silence at the end.
- No flash, no light jump: every light change eases over ≥ 0.25 s, and the beat glow uses `SONG.pulseSoft`.
- The film ends on a declared hold (blank paper, 136–138 s).
- Chapters: ch01 = shots 1–7 (0–44.6 s), ch02 = shots 8–15 (44.6–78.6 s), ch03 = shots 16–23 (78.6–138 s).
