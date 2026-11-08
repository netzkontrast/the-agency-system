# Storyboard v3 — Track 13 „Ich bin hier / Das war“ (picture, lyrics, sound, production)

One idea (one sentence): the same room as in track 1, but the door stands open and it is day, and the film holds still while the song says that it is here.
Payoff (the moment people rewatch): the stressed "war" at 50.3 s, when the gold seam in the paper wall takes the light once, and the last view that returns to the opening image of track 1 with the demand gone.
Playbook: skills/video/studio/playbooks/music-video.md   Medium: paint (p5.brush, from the album concept)   Format: 1920x1080, 24 fps, 138 s
Source: `songmap/words.json`, MEASURED from the real audio (`audio/13-ich-bin-hier-das-war.mp3`, 138.12 s; faster-whisper heard the words, `songmap/align.py` snapped them to the streaming lyrics; the 60 bpm heartbeat phase is 0.45 s). v2 of this board: v1 was planned on an estimated map and the real song is laid out differently (long instrumental stretches at 8.6–21.5 s, 95–102 s and 108–125 s; the last refrain line repeats at 125 s). Every time below is read from the song map (`SONG.line(i).t / .end / .key.stress`), so a re-measured map retimes the film.
Lyrics on screen: YES, animated word by word to the measured word times (the user asked for it; see "Lyrics animation" below). Source of every word: the streaming lyrics, never the Suno box. `out/film.srt` stays as a separate subtitle file. Locked: no bodies, no names, the child's line is a light and never a figure.

## Look in four lines
- Flat 2D on paper, ink lines that boil at 12 drawings/s, light only through `glow()`, grain on top.
- Palette: paper `#F3EBDC`, ink `#2B2233`, morning yellow `#F2C14E` (light), Kintsugi gold `#FFDF00` (the seam only), Clean Ping `#FCEE0C` (one point, once).
- The room: a threshold (open door, left), a curtain with a light strip (right), a lamp (the heartbeat), a smooth pillow on the floor, a window, a paper wall with one gold seam.
- No alarm, no Signal Yellow, no hit: the heartbeat grid (1 beat = 1 s) is the only pulse, and it slows to nothing at the end.

| # | Time (s) | Section / lyric line (key word @ stress time) | What happens | Reads (in order) | Transition out | Chapter |
|---|---|---|---|---|---|---|
| 0 | 0.0–2.3 | Silence (the audio starts at 2.35 s) | Content-warning board, painted on paper, calm: three short lines (see below), no motion except the paper grain. It leaves with a slow fade into the threshold | 1 a notice; 2 it fades | fade | ch01 |
| 1 | 2.3–2.4+ | Intro, first heartbeat at 2.4 s | The threshold appears under the fading board: open door left, curtain right, lamp above. The lamp starts to pulse on the FIRST beat after 2.35 s (not before) | 1 paper becomes a room; 2 a light is breathing | continuous | ch01 |
| 2 | 2.4–8.6 | line 0 "Der Puls ist langsam. Der Puls ist meiner." (meiner @ 7.71) | Same view, very slow push in. The glow pulse follows the beat; on "meiner" the pulse is larger and the paper wash breathes once with it | 1 the room has a pulse; 2 it is the speaker's own | slow ease | ch01 |
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

## Content warning board (shot 0, 0.0–2.3 s)
Painted, quiet, on the paper, ink letters; no music yet. Text (German, neutral, no names):
„Dieses Album handelt von sexualisierter Gewalt in der Kindheit und ihren Folgen.“ / „Hör nur zu, wenn du dich sicher fühlst.“ / „Hilfe und Hinweise stehen in der Beschreibung.“
Each line fades in 0.5 s apart, all gone by 2.3 s. The same board design is meant for all 13 videos (open decision in VIDEO-CONCEPT.md).

## Lyrics animation (the typographic system)
**Idea.** The words are breath. They arrive when they are sung, settle when the stressed syllable lands, and leave the way the air leaves the room: softly, never by a cut. They are painted like the rest of the film (ink on paper, a little boil), not a subtitle layer pasted on top.

**Type.** A calm italic serif for the sung words (EB Garamond Italic, SIL OFL, shipped as a font file in `assets/fonts/`, never linked from a CDN). Key words (the stressed word of each line) are set one size larger and upright. Sizes at 1080p: body line 64 px, key word 84 px, refrain hero 150 px, bridge 48 px. Colour: ink `#2B2233` on paper scenes; paper `#F3EBDC` on dark scenes (the bridge and the final fade); the key word carries a morning-yellow glow (`#F2C14E`, via `glow()`), never a hard yellow fill.

**Placement (text-safe).** All text inside x 160–1760 and y 120–960 (a 160 px frame). Strophes: lower third, left-aligned at x 200, baseline y 860, two rows maximum. Refrains: centred, mid-frame. The bridge: small, next to the light point. Text never covers the door, the light point or the seam; if a shot's prop sits in the lower third, the line moves to the upper third for that shot.

**Motion rules.**
- A word appears at `word.t − 0.12 s`: it rises 14 px, from 0 to full opacity over 0.45 s (ease-out), with a 0.6 px ink wobble at 12 drawings per second.
- At `word.stress` the word is "set": a 3 % scale settle over 0.3 s (no bounce, no overshoot).
- A line stays until `line.end + 0.9 s`, then leaves word by word in reading order over 0.8 s, each word dissolving to paper (opacity and a slight upward drift, no cut).
- Beat glow never touches the letters; only the key word's glow follows `SONG.pulseSoft`, and only in the intro.
- No flash, no strobe, no scale jump over 8 % per frame. Reading time: at least 0.3 s per word plus 0.5 s.

**Per line.**
| Line | Words | Key (stress) | Treatment |
|---|---|---|---|
| 0 | Der Puls ist langsam. Der Puls ist meiner. | meiner (7.71) | Both „Puls“ swell 4 % on the heartbeat (`pulseSoft`); „meiner“ lands larger, upright, with the first yellow glow |
| 1 | Das Gelb hängt in den Vorhängen. Es ist nur Licht. | Licht (25.94) | „Gelb“ is tinted morning yellow; on „Licht“ the tint leaves the other words and the glow lies even under the line |
| 2 | Kein Faden auf dem Mund. Kein Druck, der mich erstickt. | Druck (30.17) | A thin ink thread runs under „Faden“; on „Druck“ the thread slides out to the left and is gone; „erstickt“ is set smaller and fades first, letter by letter from the end, like an exhale |
| 3 | Ich atme ein. Ich atme aus. Niemand verhandelt mit. | aus (34.90) | Letter-spacing opens on „ein“ (0 to +14 %) and closes on „aus“ (back to 0); „Niemand verhandelt mit.“ stands small and still |
| 4 | Der Raum ist still. Und ich bin hier. | hier (44.14) | Slow reveal; every word is still while the camera pulls back; „hier“ is set larger and holds until the refrain takes over |
| 5 | Ich bin hier. | hier (46.17) | Refrain hero, centred, 150 px, three words one after the other; holds 1.5 s |
| 6 | Das war. | war (48.24) | Set smaller, under the hero line; on „war“ a thin gold light runs once through the letters (the seam glint) |
| 7 | Kein Sieg. Kein Ende. Nur das hier und das, was war. | war (56.05) | Two rows, calm; „Kein Sieg.“ and „Kein Ende.“ appear lighter (60 % ink) than „Nur das hier und das, was war.“, which settles fully; no triumph |
| 8 | Ich bin hier. | hier (58.15) | The hero line returns, a little lower than in line 5, same size; it leaves with the room's breath |
| 9 | Ich hab nach Luft gefragt. Ich hab es laut verlangt. | verlangt (64.85) | „laut verlangt“ is set larger and darker; the brush wipe of the shot clears the window and takes the two words with it |
| 10 | Jetzt frag ich nicht mehr. Die Luft ist einfach da. | da (69.84) | „Die Luft ist einfach da.“ floats up 20 px as it appears (air); „da“ settles on the lifted curtain |
| 11 | Das, was war, bleibt wahr. Und es bleibt hinter mir. | mir (73.87) | The line slides slowly left with the seam, parallax-style; „hinter mir.“ ends partly out of the frame on the left and fades there |
| 12 | Ich dreh mich nicht mehr um. Ich bin hier. | hier (78.07) | The line stays perfectly still while the picture moves; „hier“ settles |
| 13–14 | Ich bin hier. Das war. | hier (80.08), war (82.16) | Same words, new picture: set small and low, left; a gold light travels through the letters as it travels across the seam |
| 15 | Kein Sieg. Kein Ende. Nur das hier und das, was war. | war (89.98) | Warm, held at 60 % ink; the light on the wall lies over the words like a window frame, no flare |
| 16 | Ich bin hier. | hier (92.16) | Hero line, but smaller than in the first refrain (110 px): the room is emptier |
| 17 | Ich bin auch hier. | auch (94.15) | Small (48 px), paper colour on the dark paper, next to the Clean Ping point; „auch“ appears exactly when the point appears, and brightens with it |
| 18–19 | Ich bin hier. Das war. | hier (104.27), war (108.22) | Large, centred, the same typeface as the opening; they hold through the whole last quiet |
| 20–21 | Ich bin hier. Das war. | hier (128.23), war (132.25) | One row, centred; on „war“ the whole line dissolves to paper with the breath fog (word by word from the right) and is gone by 133 s |

**Between lines.** No text during instrumentals 8.6–21.5, 95–102, 108–125 and from 133 s on, so the pictures carry the film there (only line 18–19 stays on screen through the first half of 108–125 s, fading out by 112 s).

## Colour and light script
| Time | Light | Paper | Mood |
|---|---|---|---|
| 0–2.3 | none | cold paper `#F3EBDC` | notice |
| 2.4–21 | one lamp, 60 bpm pulse, thin morning strip through the curtain | paper, slight grey | held breath |
| 21.5–44.6 | morning yellow behind the cloth, plain daylight from „Licht“ on | warmer paper | the room as it is |
| 44.6–59 | day, level | clean | here |
| 61–79 | grey-blue glass, then clear | cool to neutral | asking, then not asking |
| 78.6–92.8 | warm light travelling over the seam | warm | no triumph |
| 92.8–102 | one point (Clean Ping) in the dark paper `#2B2233`-tinted | night paper | the child joins |
| 102–125 | the biggest light of the film (the music swells here): warm over wall and floor, 60 % | warm | rest |
| 125–137 | falling, the point beside the frame | paper | that was |
| 137–138 | none | blank paper | silence |

## Camera
Level with the threshold throughout; no handheld, no whip, no zoom over 8 % per second. Moves: slow push (shot 2), slide door to curtain (shot 3), pull-back (shot 7), sideways drift (shot 14), back-away (shot 21). Every move ends on a still with the sung word.

## Sound-design cues (the audio is the finished Suno track; the film adds nothing but timing)
- Heartbeat grid 60 bpm, phase 0.45 s, first audible beat 2.4 s; the lamp pulse starts there.
- Biggest swell 95–125 s (the picture's biggest light); sub-bass drone 133–137 s (the last breath fog).
- Final mix: do not raise the level (true peak is −1.0 dBFS); the film is muxed with the track as is.

## Deliverables
1. **Music video** 16:9, 1920×1080, 24 fps, 138 s, with the track; H.264 + AAC, −14 LUFS check (the track is −13.3 LUFS, no change).
2. **Subtitle file** `out/film.srt` (separate, for platforms that want captions).
3. **Teaser** 9:16 vertical, 20 s: the refrain 2 picture to the bridge (80–100 s), recomposed for 1080×1920.
4. **Canvas loop** 9:16, 6 s: the lamp pulse and the light strip (loops on the beat).
5. **Still** 3000×3000 for the album page: shot 15, the threshold with the open door.

## Production plan and risks
| Step | Who | Gate |
|---|---|---|
| Song map measured (done) | director | words matched 131/136 |
| Storyboard v3 | director | critic round |
| Pictures: ch01–ch03 | animator | contact sheets at every key word |
| Lyrics layer | typographer | text audit, reading time, safe zone |
| Integration, render | integrator | gate battery (determinism, dead air, pops, text, edge, plate, flash) |
| Review | fresh reviewer, max 3 rounds | scores on every axis; the person decides when the score stalls |
| Master and delivery | integrator | −14 LUFS check, mux with the track |

Risks: (1) the render has no GPU here (about 5 drawings per second at 960×540), so the full film takes a long time to render; (2) animated text on top of painted washes can break contrast (check `plate-audit`); (3) the repeated last line makes two nearly equal endings: shot 22 must feel like a settling, not a second ending; (4) the high voice at 130.7 s is unconfirmed (check by ear).
