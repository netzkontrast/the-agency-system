# Gate battery — /tmp/claude-0/-home-user/0b1fe73e-918d-5978-8b74-a8ee10efa833/scratchpad/e2e — 2026-11-08T09:34:47Z
## render gate (determinism, contract, dead air, pops)
```
QUALITY GATE   /tmp/claude-0/-home-user/0b1fe73e-918d-5978-8b74-a8ee10efa833/scratchpad/e2e/film.html   viewport 1920x1080

1. DETERMINISM  the same t, drawn two different ways, is the same frame
----------------------------------------------------------
  PASS  12 sampled frames hash-identical, cold-forward vs warmed-reverse   t 0..7.97s
  PASS  no console errors while drawing
  ----  stepped art: 12 drawings per second   stillness is judged per drawing, and the whole film counts as footage at that rate for pops

2. CONTRACT  the draw path cannot reach a clock, chance or storage
----------------------------------------------------------
  PASS  no forbidden call in 6 file(s) (film.html, config.js, songmap.js, beat.js, passes.js, scene.js)
  PASS  randomness is seeded: 1 rng()/rand()/hash() call sites   no seed derived from a clock
  ----  vendor libraries (checked at runtime by check 1, not scanned)   d3.min.js, lottie.min.js, alea.js
  ----  host clock in the preview loop (allowed)   film.html:49 Math.random replaced by a per-frame seeded stream | film.html:53 performance.now

3. DEAD AIR  something visibly moves in every half second
----------------------------------------------------------
  PASS  no unexplained identical frames 1/30 s apart   192 frames at 24 fps
  PASS  no 12-frame (half-second) window under 0.5% changed area   none
  ----  192 frames measured   median changed 8.38%  min 2.20%

4. POPS  no frame jumps 3x more than its neighbours unless it is a declared cut
----------------------------------------------------------
  ----  declared footage: 0-8s at 12 fps
  PASS  no undeclared frame-difference spikes (> 3x neighbours)   0 spike(s), all declared cuts

==========================================================
GATE: PASS   7/7 checks
```
## text audit
```
TEXT AUDIT   film.html   1920x1080, 8.0 s, a sample every 0.1 s, 0 pieces of text   (no window.FACES: the face check did not run)
TEXT AUDIT: PASS
```
## edge audit
```
EDGE AUDIT   film.html   1920x1080, 8.0 s, a sample every 0.1 s, held cut 0.8 s or more
EDGE AUDIT: nothing cut
```
## plate audit
```
PLATE AUDIT   film.html   1920x1080, 8.0 s, a sample every 0.1 s, 0 big pictures or clips
  no picture covering a fifth of the frame was drawn: nothing to measure (a code-only film?)
PLATE AUDIT: PASS
```
## flash test
```
FLASH TEST  /tmp/claude-0/-home-user/0b1fe73e-918d-5978-8b74-a8ee10efa833/scratchpad/e2e/out/film-v7.mp4  192 frames @ 24.00 fps  (area >= 25%, limit 3/s)
  general flashes: 0 total, worst 0 in one second
  red flashes:     0 total, worst 0 in one second
FLASH: PASS
```
## loudness
```
=== film-v7.mp4 ===
duration    8.00 s  (decoded to stereo float 48 kHz via ffmpeg)
integrated  -14.1 LUFS   ffmpeg ebur128 -14.1 LUFS   delta 0.03 LU  AGREE
LRA         0.2 LU     ffmpeg 0.3 LU
true peak   -3.1 dBTP   ffmpeg 0.0 dBTP   sample peak -3.1 dBFS
centroid    249 Hz mean / 212 Hz energy-weighted
--- verdict (film: mixed film final audio: -14 LUFS +/-1, true peak <= -1 dBTP) ---
loudness    PASS  -14.1 LUFS vs -14 +/-1
true peak   PASS  -3.1 dBTP vs <= -1 dBTP

RESULT: PASS
```
