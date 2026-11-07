# Audio

## Measure, don't guess (run before every delivery)

Run the meter on the final mix (or the exported MP4 itself) before showing the user anything:

```bash
node scripts/audio-check.mjs final.mp4                        # film mix (default target)
node scripts/audio-check.mjs master.wav --target dense        # music master, dense style
node scripts/audio-check.mjs master.wav --target gentle       # music master, gentle style
node scripts/audio-check.mjs mix.wav --stems vocals.wav other.wav   # vocal-masking check
```

It decodes through ffmpeg (so you meter what a player hears) and reports integrated LUFS (BS.1770-4), LRA (EBU 3342), 4x-oversampled true peak, and spectral centroid, each cross-checked against ffmpeg's own `ebur128`. If the two LUFS numbers disagree by more than 0.5 LU the tool exits 2: that is a metering bug, not a mix note.

The numbers must be:
- **Film final audio:** integrated near **-14 LUFS** (within 1 LU), true peak **<= -1 dBTP**.
- **Music master:** **-14 LUFS** for dense styles, **-16 LUFS** for gentle styles, true peak **<= -1 dBTP** either way.
- **Vocals/dialogue over music:** with `--stems`, the vocal stem must beat everything else by **>= 3 dB in 500 Hz-4 kHz in >= 80 %** of its active seconds. Below that, the words are likely masked; raise the vocal or dip the music in that band. (Integrated LUFS of the whole mix can look right while one part is buried: loudness says how loud the whole is, never which part is wrong.)
- Centroid is reported, never gated: it tells you brightness (a music-box piece should sit well above 1 kHz; ~400 Hz means a pad or rumble took over).

If loudness misses target, the tool prints the gain to apply; after any gain change re-run it, because the peak moves too. Fix a hot peak by lowering gain or limiting, never by shipping it: encoders clip inter-sample peaks above -1 dBTP.

## Instrumental beds, stings and loops in code (`scripts/music.mjs`)

When the film needs no vocals, compose the music as a score in code: it's deterministic, fitted exactly to the film's length, and needs no credits and no user round-trip. See `references/music-engine.md` for the notation, the instruments, and the two demo pieces. Use Suno (below) when the film needs a voice or a sung hook.

## Music from Suno (user generates, you cut)

Give the user a Custom-mode prompt with Instrumental on. Structure tags go in the Lyrics box. Don't name real artists or franchises (Suno blocks them); describe the sound.

Example (fighting game):
```
Style: 90s arcade fighting game techno, aggressive industrial techno, 140 BPM, pounding kick drum, distorted synth stabs, dark gothic choir hits, martial arts gongs, taiko drums, epic battle energy, instrumental
Lyrics:
[Intro] [ominous gong, dark choir]
[Build] [fast rising synth arpeggio]
[Drop] [full techno beat, heavy and relentless]
[Break] [everything drops out, heartbeat drum only]
[Outro] [huge choir hit and gong]
```
Ask for the full-length track (Suno clips can be ~20 s; use Extend for a break + outro).

## Cutting music to the story

1. Map the track's structure from its loudness envelope:
   ```bash
   python3 - <<'EOF'
   import subprocess,struct,math
   raw=subprocess.run(['ffmpeg','-v','error','-i','track.wav','-ac','1','-ar','8000','-f','s16le','-'],capture_output=True).stdout
   s=struct.unpack('<%dh'%(len(raw)//2),raw);w=2000
   for i in range(0,len(s),w):
       c=s[i:i+w];r=math.sqrt(sum(x*x for x in c)/len(c))/32768;db=20*math.log10(r+1e-9)
       print(f"{i/8000:5.2f}s {db:6.1f} "+'#'*int(max(0,db+40)))
   EOF
   ```
2. Plan placements: the drop on the big reveal ("FIGHT!"), a muffled low-passed rumble under slow motion, the full hit back on the impact, **silence (fade out) right before the final punchline**. Loop sections in whole bars (bar = 4 × 60/BPM s) to avoid audible seams.
3. **Find the drop by measurement, never from the auto beat grid.** Compute low-band (kick/bass, under ~150 Hz) energy per bar on the beat grid; the drop is the bar where it jumps (typically 6-10 dB over the bar before). Then refine inside that bar in **20 ms windows** of the same low band to the first window of the jump: that is `drop_in_song`. Auto grids and "section" detectors land a beat or a bar off on drops, and a drop that misses the reveal by 100 ms feels broken. Start the song at `drop_in_song - drop_in_film` (the film's reveal time), so the measured drop lands on the reveal's frame.
4. **Place recorded foley by its measured peak, not its file start.** A recorded whoosh, slam or click has lead-in silence and a build; its sync point is its loudest instant. Find it (`argmax` of the absolute sample value, or of 5 ms RMS for a smoother read) and delay the file by `hit_time - peak_offset`. File-start placement lands every recorded hit 20-200 ms late. (`sfx.mjs` cues already carry their sync point; this is for recorded and downloaded sounds.)
5. Build it with `scripts/mux-audio.sh` (edit the segment list) or an ffmpeg `filter_complex` of `atrim` + `adelay` + `afade` + `amix=normalize=0:duration=longest`, then `apad=whole_dur=<len>` and `loudnorm=I=-14:TP=-1.0`. Do not use a bare `apad` before `atrim` (it never ends).

### Three things a listener heard that the meters did not (the Take One launch film)

The maker cannot hear. These came from the owner's ears on a cut that passed every meter.

- **A repeat spliced into a quiet intro is heard at once** ("there was a weird cut in the music here, no?"). Looping "in whole bars" is not enough where nothing covers the join. Never repeat or remove bars in an exposed, quiet part. If the film needs the track longer or shorter, change the film's timing first; if the music must be cut, cut it at the end of a phrase going INTO a quiet part, or inside a full drop. Map the phrases before cutting: compare each bar's spectrum with every other bar (a simple correlation of log band energies); bars that match (0.9 and over) show the phrase shape (ours was A B C D A B), and the phrase end is where a cut can hide.
- **The best fit used one cut in 58 seconds.** Start the track at its own first beat and let its shape carry the film's turns: quiet intro under the thinking, its build under the last quiet beat, its drop on the first big picture, its break on the verdict, its second drop on the result, its last hit on the logo. Move the film's beats to the music's, not the other way round. A music-free second or two before the track enters (a hard cut to silence, keys being typed) makes its entry a moment.
- **Under a voice, fewer sounds.** "A sound for every visual event" is for a film without a narrator. Under one, the owner heard a bell on "A composer writes the music" as "an alarm" and a run of interface ticks under "A sound designer adds every sound" as plain bad. Keep the sounds of things that are pressed, typed, moved or cut (a thud, keys, a swish, paper), and one pop as each new thing takes its turn. Drop bells, chimes, sparkles and any run of ticks. When a line names music or sound, let the music itself answer it.
- **When a shot is about sound, let its sounds be heard, on the music's grid.** After asking for fewer sounds, the same owner asked for these: a lane where a sound designer drops marks labelled hit, whoosh, click, air wanted each mark heard, "even if it's subtle". Three things made that work on paper: each sound matches its label (four different kinds, never a run of one tick); the footage is re-timed so the marks land on the music's half beats (a mark every 0.2 s over a 120 bpm track is off the grid and reads as noise; every 0.25 s is an eighth note); and those sounds are mixed as their own layer over the music, about 6 dB under the voice, not ducked with the bed (`sfx.mjs mix` with a silent bed gives the layer alone). Say in the delivery note that it needs the owner's ear.

## A finished film inside the film

When the film shows another finished film whole (the ad the product made, a customer's spot), that film keeps its own finished sound, untouched. Do not rebuild it from its parts in the new mix: the balance of its voice, music and effects is what was approved, and a rebuild is a different mix. First done for the short Take One launch film (11 Oct 2026), after the owner said of a rebuilt seven-second version "it says just random words".

- **Take it from the lossless final mix** of the film it was approved in: the WAV the MP4 was muxed from, not the MP4's own audio. Prove it is the same sound as the approved file: cross-correlate the two over the stretch; 0.99 or more at zero lag is the same mix.
- **Lay it in after the new film's master**, so the new limiter never touches it: master the new film with silence where the inner film plays, then add the inner film's sound with a 4 ms fade in and a fade out over its last 90 ms.
- **Set its level by the voice, not by a meter.** Take a recorded line that is in both final mixes, find it in each (cross-correlate the clip against the mix) and read the least-squares gain at the best match; move the inserted sound by the difference. Ours was 0.3 dB. If no line is shared, match the narrator's level in the new film to the inner film's own voice the same way.
- **Nothing of the new film plays over it:** no narrator, none of the new film's effects. A transition whoosh that used to rise under the inner film's last second moves to after its last word; print the new film's own level under the insert and expect silence.
- **The new film's music must not run into it.** End the music at a phrase end on the inner film's first frame; bring music back later from silence, at a phrase start. Do not look for a clever join: the inner film has its own music, and a reset is what makes it read as its own thing.
- **Effects that sat on music are exposed when the music is taken out from under them.** After the insert there may be a stretch with no music; lower the effects there by about 3 dB and tell the person that stretch needs their ear.
- Then run the loudness check on the whole film and transcribe the whole mix again. **A transcription of a long mix can skip a line that is there** (ours dropped a whole sentence that followed a loud hit): before treating a line as missing, transcribe ten seconds round it on their own.

## A song whose tempo drifts

Before cutting a song to a grid, check that its tempo is steady: measure where its pulse falls (the phase of its eighth note, taken as a weighted circular mean of onset strength) in ten-second windows at the tempo you measured. A steady song keeps it within about 10 ms from start to end (two of ours: 5 and 8 ms). One generated track wandered by 250 ms and its two tempo readings disagreed (129.1 and 127.9): it was speeding up by about 1.5 % over its length. One stretch factor would have put its beats a third of a beat off the picture's cuts by the end of a 32 s stretch.

Fix it by following the pulse instead of assuming a tempo: unwrap that phase through the track, turn it into a map from song time to grid time, stretch the song in four-second pieces each by its own factor (ffmpeg `atempo`), and join the pieces with 60 ms crossfades. Then measure the pulse of the result again; ours held within 4 ms. Only after that read off the drop, the breaks and the last hit.

Two more things that measuring taught: a mono downmix made by ffmpeg reads about 3 dB hotter than the two channels, so compare songs channel by channel, and bring candidates to the same level before the owner compares them (the louder one tends to win for the wrong reason). And a song may have no last hit at all: if its groove simply stops on a held chord, let it swell in and stop on the film's hit, and let the hit's own sound do the rest.

## When the film has two pieces of music

A film that shows another film whole has two candidates for its own music: the inner film's song, or a second song.

- **The inner film's song is the benchmark.** If it is the better song, the owner will prefer to hear it everywhere. Ours said it in one line: "the ad music is so good that even if you hear it in all the video it's a better experience ... we need to elevate the song of the video". A second song only earns its place if it is as good to the owner's ear.
- **Give the second song a different job, not a smaller copy of the first.** The owner's brief for ours: "upbeat and uplifting ... but not to take away from the video ad sound". So: a brighter mood, a lighter low end (the inner film's hits then land harder), a different groove family, and the relative key (C major against the ad's A minor), so the change at the inner film's first frame is a turn of mood and not a clash.
- **You cannot hear it. The owner picks.** Make two styles, two takes each, give four links in one message, download only the pick (downloads are metered on most plans; read credits and downloads on the account page before and after, and say both). Until the pick, keep the cut that already works.
- A word or a call in the music (the product's name, "action") fights a narrator who speaks through most of the film. If the owner wants it, give it to the narrator as one short line where she is silent anyway.

## Sound effects: code-synthesized by default (`scripts/sfx.mjs`)

Hits, whooshes, UI ticks, pops, presses, swishes, risers, impacts, chimes, paper and ink are now **synthesized in code** (adapted from anidoodle, Apache-2.0): free, deterministic per seed, no ElevenLabs needed. Frames are deterministic, so hit times are known exactly; address every cue by integer film frame.

```
node scripts/sfx.mjs list                                  # 10 kinds x variants, target levels, uses
node scripts/sfx.mjs one impact boom 3 out.wav             # audition one (KEY=C BPM=90 env for tuned kinds)
node scripts/sfx.mjs mix plan.json music-bed.wav mixed.wav # place a cue plan over the music
```

`plan.json`: `{ fps, bpm?, key?, seed, cues: [{ kind, frame, variant?, snap? }] }`. The frame is the sound's **sync point**: the hit, the PASS-BY of a whoosh, the END of a riser (its build is rendered before the frame; too early throws). Fractional frames throw. Each cue gets its own seed from (kind, frame, occurrence), so inserting a cue never changes the others. The bed ducks under cues (40 ms attack, 280 ms release, 1.2 s after an impact, capped 9 dB), the mix goes through a look-ahead -1 dBTP ceiling, and any cue more than 6 dB under the ducked bed throws "buried cue" (a cue nobody hears is a bug, not a choice). Taste rules print as warnings: one riser + one impact per film; at most 2 cues in any 100 ms; effects only on real direction changes; transitions get only `whoosh:soft` / `swish` — never a sharp swoosh; typing is one `tick` per character.

**ElevenLabs (or Higgsfield `generate_audio`) stays for voice, announcers, and organic one-offs** the kit can't make (animals, crowds, real-world foley). Credits cost money: quote first.

## Timing a music video to the vocals (proven on a family song video)

1. Isolate vocals: `python -m demucs --two-stems=vocals -o sep song.mp3` (demucs installed in a Python environment).
2. Word timestamps: `whisper-cli -m <path to ggml-large-v3-turbo.bin> -f song16k.wav -l <lang> -ml 1 -sow` (whisper.cpp with the large-v3-turbo model) (the words are rough for sung lyrics; the times are good). Use the user's real lyrics for the text.
3. Onsets: read the vocals stem's loudness in 50 ms windows and mark rises above ~-30 dB; these are the exact hits ("Hai!", names, claps).
4. Tempo from onset autocorrelation; set the engine's bpm and offset so the beat grid sits on the vocal onsets.
5. Put **every word that triggers an action** in the brief's timeline (not only the big hits). Anything left out gets estimated by the animator and usually lands early or late.

## Stressed syllables, not word starts (Hebrew lesson)

Word timestamps mark where a word **starts**. The loud, on-beat moment is the **stressed syllable**, which in Hebrew (often final-stressed: שמחה, מצליח, הכול) comes 0.3-0.45 s later. Land impacts on the stressed syllable, measured from the vocal stem's loudness, or every hit lands 7-11 frames early. Record both times in the song map (start for mouth/anticipation, stress for the hit).

## A song written for the film (app-builder music video lesson)

The strongest thing in the app-builder music video was a Suno song whose lyrics were the film's own lines. The user loved hearing the story sung ("i love the lyrics with the voice") and the whole video was built on it.

**Write it for the storyboard.**
- Offer two tracks with the same arc so one edit fits both: an instrumental and a sung version.
- Lyrics = the on-screen lines: the problem ("Twenty-three requests, zero booked"), the turn ("Someone should" / "I will"), the payoff ("Booking confirmed, seat one of eight"), and the brand line.
- Put `[Break] [one beat of total silence]` before each chorus. Suno honored it, and those silences became the two best moments in the film (an a cappella "I will", a whispered brand name).
- Spell the brand the way it should be sung (a name with digits is written out, "Brand Forty-Four", not "Brand44").
- Give the prompt field by field, in Suno's Custom-mode order: Lyrics box, Styles box, Exclude styles, vocal gender, Weirdness (about 30%), Style Influence (about 75%), title. The user asked for exactly this format.

**Map it before cutting.**
- Measure the tempo; never trust the prompt. Asked for 120 BPM, Suno delivered 121.42 (instrumental) and 120.03 (vocal).
- Detect it on the demucs instrumental stem (`no_vocals.wav`), not the mix: onset autocorrelation for the period, then the phase that maximizes low-band (kick) onsets.
- Write every cut and action as a beat index, `B(k) = phase + k * beat`, and every sung action as a word time from the song map. Re-cutting to another take becomes a data change.
- Whisper drops and mishears sung words ("Booking" came out "Looking", a line vanished). Use the user's lyrics text with whisper's times, and snap word starts to phrase onsets found in the vocal stem's loudness.
- To cut a short pilot from a long song, splice at bar lines (4 beats) and jump to the song's real ending for the final hit.

**Let the song drive the picture.**
- Hook words slam in on the sung word; the drop lands on the story's reveal; the silences carry the turns.
- An audio-reactive HUD costs minutes: compute per-frame log-spectrum bands (about 44) from the song into a JSON file and let the HUD waveform read it, so the graphics breathe with the music.

## Mapping a user's sung track fast (whiteboard-product film lesson)

- `whisper-cli -ml 1` word times drift badly on singing (words start early, phrases merge). What worked: phrase segments from whisper, plus **windowed probes**, running whisper with `-ot <ms>` from successive offsets and reading which word comes first after each offset; plus a 0.1 s vocal-energy map of the demucs vocal stem printed as text. Together they pin each line within about 0.2 s.
- Measure tempo and phase on the instrumental stem, then check structure from the mix's loudness per second: intro, beat entry, chorus, the silent break, the drop.
- **Loop or CTA.** Ending on the song's own silence gives a seamless loop; spending the song's drop on the brand's CTA gives a stronger finish for a brand piece. The user chose the CTA ("it would have been better to finish with a cta"). Offer both at the pitch.
- Trim a quiet lead-in (start the film where the song starts to matter) and shift every timeline value by one constant (`SONG_IN`).

## Mapping a track you cannot hear

`python3 <skill>/scripts/songmap.py track.wav [bpm guess]` prints the tempo, where the first beat falls, loudness for every half second (all, bass, top), the silences and the last strong hit (needs numpy and scipy). Use it to put the track's drop on the film's turn, its silence on the quiet line and its last hit on the end card. To fit a track to the film's beat grid, stretch it by a few percent at most (`ffmpeg -af atempo=`); more than that is heard.
