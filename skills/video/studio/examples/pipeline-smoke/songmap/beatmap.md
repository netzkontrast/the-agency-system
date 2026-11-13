# Beat map — song.wav
window: start 0.0 s in file, 8.0 s, 24 fps (film t=0 ↔ file 0.0 s)

**BPM 120.06** · beat 11.99 f (0.4998 s) · bar 47.98 f (1.999 s) · tempogram alone 120.19 · downbeat phase 3 (confidence 0.004) · beat_this downbeat agreement None · **TEMPO LOW-CONFIDENCE — alternative 60.03 BPM; verify half/double by ear on the kicks, then rerun with --bpm**

Tempo candidates (score = on/off-beat contrast full+kick+snare, grid fit, prior):

| bpm | score | contrast full | kick | snare | on-beat hit frac | binary subdiv | seeds |
|---|---|---|---|---|---|---|---|
| 120.06 | 11.71 | 4.975 | 5.693 | 4.978 | 0.94 | -0.013 | tempogram kick_autocorr |
| 60.03 | 1.956 | -0.223 | 0.075 | -0.136 | 1.0 | 5.413 |  |

Drop: none in window (flat loop)
Grid shifted 16.3 ms to the measured attacks of strong beats.

## Sections (bar map)

| section | bars | t | frames | RMS dB | density target |
|---|---|---|---|---|---|
| hook | 1 | -0.467–1.532 | f-11–f37 | -17.9 | 4–9 ev/s |
| full | 3 | 1.532–7.507 | f37–f180 | -18.3 | 3–5 ev/s |
| release | 1 | 7.507–9.506 | f180–f228 | -23.3 | ≈1 ev/s (one held bar) |

## Bars

| bar | t | frame | RMS dB | low dB | onsets/s | section | flags |
|---|---|---|---|---|---|---|---|
| 1 | -0.467 | -11 | -17.9 | -24.4 | 1.31 | hook | partial |
| 2 | 1.532 | 37 | -18.1 | -24.9 | 2.0 | full |  |
| 3 | 3.532 | 85 | -18.1 | -24.9 | 2.0 | full |  |
| 4 | 5.532 | 133 | -18.6 | -25.4 | 2.03 | full |  |
| 5 | 7.507 | 180 | -23.3 | -27.3 | 2.03 | release |  |

## Top-10 transients (hit these ±1 f with the biggest images)

| rank | t | frame | score | off nearest beat (f) | on downbeat |
|---|---|---|---|---|---|
| 10 | 0.507 | 12 | 0.933 | -0.6 |  |
| 7 | 1.007 | 24 | 0.968 | -0.6 |  |
| 3 | 1.500 | 36 | 0.992 | -0.8 | yes |
| 1 | 2.000 | 48 | 1.006 | -0.8 |  |
| 5 | 2.500 | 60 | 0.988 | -0.8 |  |
| 9 | 4.507 | 108 | 0.941 | -0.6 |  |
| 6 | 5.000 | 120 | 0.97 | -0.8 |  |
| 4 | 5.500 | 132 | 0.991 | -0.8 | yes |
| 2 | 6.000 | 144 | 0.996 | -0.8 |  |
| 8 | 6.500 | 156 | 0.952 | -0.8 |  |

## Stops / silences (scene boundary: ONE growing gesture into the next downbeat)

none

## Risers

none

## Pickups (onset 2–4 f before a downbeat — a big change may arrive here and settle on the downbeat)

none

## Grids

beats (f): 1 13 25 37 49 61 73 85 97 109 121 133 145 157 169 180

downbeats (f): 37 85 133 180

