#!/usr/bin/env python3
# scripts/songmap.py : a map of a music track without hearing it: tempo, where the beats fall, how loud each half second is
# (all / bass / top), where it goes silent, and its last hit. Usage: python3 <skill>/scripts/songmap.py <track.wav> [bpm guess=120]
import sys, subprocess
if len(sys.argv) < 2: sys.exit('usage: python3 songmap.py <track.wav|mp3> [bpm guess=120]')
try:
    import numpy as np
    from scipy.signal import butter, sosfilt
except ImportError: sys.exit('songmap.py needs numpy and scipy:  python3 -m pip install numpy scipy')
src = sys.argv[1]; guess = float(sys.argv[2]) if len(sys.argv) > 2 else 120.0
SR = 22050
x = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', src, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout, dtype=np.float32).astype(np.float64)
dur = len(x) / SR
if dur < 5: sys.exit(f'{src}: {dur:.1f} s is too short to map (it needs at least 5 s of music)')
# onset strength: positive spectral flux at a 10 ms hop
hop, win = 220, 1024; nfr = (len(x) - win) // hop
S = np.abs(np.fft.rfft(np.stack([x[i * hop:i * hop + win] for i in range(nfr)]) * np.hanning(win), axis=1))
flux = np.maximum(0, np.diff(np.log1p(20 * S), axis=0)).sum(axis=1); flux = np.concatenate([[0], flux]); fps = SR / hop
o = flux - np.convolve(flux, np.ones(41) / 41, mode='same'); o = np.maximum(o, 0)
# tempo: the beat period whose comb picks up the most onset energy, searched finely around the guess
best = None
for bpm in np.arange(guess - 12, guess + 12.001, 0.05):
    per = 60 / bpm * fps; ph_best = None
    for ph in np.linspace(0, per, 40, endpoint=False):
        idx = np.round(ph + per * np.arange(int((len(o) - ph) / per))).astype(int); idx = idx[idx < len(o)]
        s = (o[idx] + 0.5 * o[np.minimum(idx + 1, len(o) - 1)] + 0.5 * o[np.maximum(idx - 1, 0)]).sum() / len(idx)
        if ph_best is None or s > ph_best[0]: ph_best = (s, ph)
    if best is None or ph_best[0] > best[0]: best = (ph_best[0], bpm, ph_best[1] / fps)
_, bpm, phase = best
print(f'{src}: {dur:.2f} s   tempo {bpm:.2f} bpm   first beat at {phase:.3f} s (beats every {60/bpm:.4f} s)')
# loudness per half second: all, bass (<150 Hz), top (>6 kHz), in dB relative to the track's loudest half second
def band(lo, hi):
    sos = butter(4, [lo, hi], btype='band', fs=SR, output='sos') if lo and hi else butter(4, hi or lo, btype='low' if hi and not lo else 'high', fs=SR, output='sos')
    return sosfilt(sos, x)
def rms(y, t0, t1): a = y[int(t0 * SR):int(t1 * SR)]; return np.sqrt((a * a).mean() + 1e-12)
lowx, topx = band(None, 150), band(6000, None)
step = 0.5; rows = []
for i in range(int(dur / step)):
    rows.append((rms(x, i * step, (i + 1) * step), rms(lowx, i * step, (i + 1) * step), rms(topx, i * step, (i + 1) * step)))
rows = np.array(rows); ref = rows[:, 0].max()
def bar(v, r): d = 20 * np.log10(v / r + 1e-9); return ' ' if d < -40 else '.' if d < -24 else ':' if d < -15 else '+' if d < -8 else '#'
for name, c, r in (('all ', 0, ref), ('bass', 1, rows[:, 1].max()), ('top ', 2, rows[:, 2].max())):
    print(name, ''.join(bar(v, r) for v in rows[:, c]))
print('     ' + ''.join(str((i // 20) % 10) if i % 20 == 0 else ('|' if i % 4 == 0 else ' ') for i in range(len(rows))), ' (one character = 0.5 s, | every 2 s, digit every 10 s)')
# silences (all below -40 dB for 0.25 s or more) and the last hit
fr = 0.05; e = np.array([rms(x, i * fr, (i + 1) * fr) for i in range(int(dur / fr))]); q = 20 * np.log10(e / ref + 1e-9) < -40
gaps, s = [], None
for i, v in enumerate(list(q) + [False]):
    if v and s is None: s = i
    if not v and s is not None:
        if (i - s) * fr >= 0.25: gaps.append((round(s * fr, 2), round(i * fr, 2)))
        s = None
print('silences:', gaps)
strong = np.where(o > 0.45 * o.max())[0]
print('last strong hit at %.2f s; strongest hits at' % (strong[-1] / fps), [round(i / fps, 2) for i in np.argsort(o)[-8:][::-1]])
