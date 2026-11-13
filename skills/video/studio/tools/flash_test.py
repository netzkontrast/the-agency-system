#!/usr/bin/env python3
"""flash_test.py — photosensitive-seizure screen for a finished cut: general flashes and red flashes per second.

Usage:  python -I flash_test.py <cut.mp4> [--json review/flash.json] [--width 192] [--area 0.25] [--limit 3] [--iris]

A screening approximation of the WCAG 2.x / ITU-R BT.1702 thresholds, run on every delivery (a hard gate):
  * general flash: a pair of opposing changes in relative luminance of 10 % or more of the maximum, where the darker
    state is below 0.80, over at least --area of the frame (default 25 %, the "10° of the visual field" stand-in);
  * red flash: a pair of opposing transitions involving saturated red (R / (R + G + B) >= 0.8) whose change in
    (R - G - B) * 320 is more than 20, over the same area;
  * FAIL when any one-second window holds more than --limit (3) flashes of either kind.
Frames are measured downscaled (--width px wide) from the decoded video, so small sparkles do not count but a large
strobe does. A pass here is a screen, not a certificate: for broadcast, also run a certified analyser. --iris runs
EA's IRIS through the iris-pse-detection package when it is installed and adds its verdict.
Needs numpy and ffmpeg/ffprobe. Exit status 1 on FAIL.
"""
import argparse, json, os, subprocess, sys


def die(msg):
    sys.exit(f'flash_test: {msg}')


def probe(path):
    r = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height,r_frame_rate',
                        '-of', 'json', path], capture_output=True, text=True)
    if r.returncode:
        die(f'ffprobe failed on {path}')
    s = json.loads(r.stdout)['streams'][0]
    num, den = (int(x) for x in s['r_frame_rate'].split('/'))
    return s['width'], s['height'], num / (den or 1)


def frames(path, w, h):
    import numpy as np
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-nostdin', '-i', path, '-vf', f'scale={w}:{h}:flags=area', '-pix_fmt', 'rgb24',
                          '-f', 'rawvideo', '-'], stdout=subprocess.PIPE)
    size = w * h * 3
    while True:
        b = p.stdout.read(size)
        if len(b) < size:
            break
        yield np.frombuffer(b, np.uint8).reshape(h, w, 3).astype(np.float64) / 255.0
    p.wait()


def lin(c):
    import numpy as np
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def transitions(series, area):
    """series: list of (sign, fraction) per frame step; a transition counts when its area fraction >= area."""
    out = []
    for i, (up, down) in enumerate(series):
        if up >= area:
            out.append((i + 1, +1))
        elif down >= area:
            out.append((i + 1, -1))
    return out


def flashes(trans):
    """A flash is a pair of opposing transitions; count each completed pair at the frame it completes."""
    out, last = [], None
    for f, s in trans:
        if last is not None and s != last[1]:
            out.append(f)
            last = None
        else:
            last = (f, s)
    return out


def worst_window(flash_frames, fps):
    best, best_at, j = 0, 0, 0
    for i, f in enumerate(flash_frames):
        while flash_frames[j] < f - fps + 1:
            j += 1
        if i - j + 1 > best:
            best, best_at = i - j + 1, flash_frames[j]
    return best, best_at / fps if fps else 0


def iris(path):
    try:
        import iris_pse_detection  # noqa: F401
    except ImportError:
        return {'available': False}
    r = subprocess.run([sys.executable, '-m', 'iris_pse_detection', path], capture_output=True, text=True)
    return {'available': True, 'exit': r.returncode, 'tail': r.stdout[-600:]}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('video')
    ap.add_argument('--json')
    ap.add_argument('--width', type=int, default=192)
    ap.add_argument('--area', type=float, default=0.25)
    ap.add_argument('--limit', type=int, default=3)
    ap.add_argument('--iris', action='store_true')
    a = ap.parse_args()
    import numpy as np
    W, H, fps = probe(a.video)
    w = a.width
    h = max(2, int(round(H * w / W / 2)) * 2)
    gen, red, prevY, prevR, prevRed, n = [], [], None, None, None, 0
    for fr in frames(a.video, w, h):
        n += 1
        L = lin(fr)
        Y = 0.2126 * L[..., 0] + 0.7152 * L[..., 1] + 0.0722 * L[..., 2]
        s = fr.sum(axis=2) + 1e-9
        satred = (fr[..., 0] / s) >= 0.8
        R = np.clip((L[..., 0] - L[..., 1] - L[..., 2]) * 320, 0, None)
        if prevY is not None:
            d = Y - prevY
            dark = np.minimum(Y, prevY) < 0.8
            big = np.abs(d) >= 0.1
            gen.append((float(np.mean(big & dark & (d > 0))), float(np.mean(big & dark & (d < 0)))))
            dr = R - prevR
            rr = (np.abs(dr) > 20) & (satred | prevRed)
            red.append((float(np.mean(rr & (dr > 0))), float(np.mean(rr & (dr < 0)))))
        prevY, prevR, prevRed = Y, R, satred
    if n < 2:
        die('fewer than two frames decoded')
    gf, rf = flashes(transitions(gen, a.area)), flashes(transitions(red, a.area))
    gmax, gat = worst_window(gf, fps) if gf else (0, 0)
    rmax, rat = worst_window(rf, fps) if rf else (0, 0)
    ok = gmax <= a.limit and rmax <= a.limit
    rep = {'video': a.video, 'fps': fps, 'frames': n, 'area': a.area, 'limit_per_second': a.limit,
           'general': {'flashes': len(gf), 'worst_per_second': gmax, 'worst_at_s': round(gat, 2), 'frames': gf[:50]},
           'red': {'flashes': len(rf), 'worst_per_second': rmax, 'worst_at_s': round(rat, 2), 'frames': rf[:50]},
           'verdict': 'PASS' if ok else 'FAIL'}
    if a.iris:
        rep['iris'] = iris(a.video)
    print(f"FLASH TEST  {a.video}  {n} frames @ {fps:.2f} fps  (area >= {a.area:.0%}, limit {a.limit}/s)")
    print(f"  general flashes: {len(gf)} total, worst {gmax} in one second{f' at {gat:.2f}s' if gmax else ''}")
    print(f"  red flashes:     {len(rf)} total, worst {rmax} in one second{f' at {rat:.2f}s' if rmax else ''}")
    if a.iris:
        print(f"  IRIS: {rep['iris']}")
    print(f"FLASH: {rep['verdict']}")
    if a.json:
        os.makedirs(os.path.dirname(os.path.abspath(a.json)), exist_ok=True)
        json.dump(rep, open(a.json, 'w'), indent=1)
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
