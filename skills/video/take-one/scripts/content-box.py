#!/usr/bin/env python3
# scripts/content-box.py : where the content of a stretch of footage sits, and the crop that shows all of it with a clear margin.
#
# Use it before cropping any footage that goes inside a frame in the film (a screen recording in a player, a product screen in a
# device, a strip of an earlier film). A crop chosen by eye cuts a card, a panel or a label at the frame's edge sooner or later,
# and a viewer reads that as a mistake. This measures instead.
#
# Usage: python3 <skill>/scripts/content-box.py <video> <start s> <seconds> [options]
#   --fit WxH        the space the footage must fit in the film, in film pixels (default 1344x598)
#   --margin X,Y     clear margin to keep round the content, in source pixels (default 60,45)
#   --keep Y0-Y1     only look between these source rows (leave out a header row or a caption you will blank)   (default: all rows)
#   --bg N           how bright a pixel must be to count as content, 0 to 255 (default 48: for dark user interfaces;
#                    for a light ground use --light and it counts pixels darker than 255-N)
#   --light          the ground is light
#   --rest           measure only the second half of the stretch (the resting layout), not what flies in
#
# It prints the content box, and one ffmpeg line: pad (when the margin runs past the source's edge), crop and scale. When the
# content is wider than the space, the strip comes out shorter than the space: place it centred, never stretch or cut it.
# A long timeline may run off the edge in a close-up that is moving; a box with a border may not.
import sys, subprocess
import numpy as np

a = sys.argv[1:]
if len(a) < 3: sys.exit('usage: python3 content-box.py <video> <start s> <seconds> [--fit WxH] [--margin X,Y] [--keep Y0-Y1] [--bg N] [--light] [--rest]')
src, ss, ln = a[0], float(a[1]), float(a[2])
def opt(name, default):
    return a[a.index(name) + 1] if name in a else default
FW, FH = (int(v) for v in opt('--fit', '1344x598').lower().split('x'))
MX, MY = (int(v) for v in opt('--margin', '60,45').split(','))
BG = int(opt('--bg', '48')); LIGHT = '--light' in a; REST = '--rest' in a
probe = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'csv=p=0', src], capture_output=True, text=True).stdout.strip().split(',')
W, H = int(probe[0]), int(probe[1])
K0, K1 = (int(v) for v in opt('--keep', f'0-{H}').split('-'))
raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(ss), '-t', str(ln), '-i', src, '-vf', 'fps=6', '-f', 'rawvideo', '-pix_fmt', 'gray', '-'], capture_output=True).stdout
n = len(raw) // (W * H)
if n == 0: sys.exit('no frames decoded: check the start time and the length')
f = np.frombuffer(raw, dtype=np.uint8).reshape(n, H, W)
if REST: f = f[n // 2:]
m = ((f < 255 - BG) if LIGHT else (f > BG)).any(axis=0); m[:K0] = False; m[K1:] = False
if not m.any(): sys.exit('nothing but ground in that stretch: lower --bg, or check --keep')
ys, xs = np.nonzero(m); x0, x1, y0, y1 = int(xs.min()), int(xs.max()) + 1, int(ys.min()), int(ys.max()) + 1
bw, bh = x1 - x0, y1 - y0
print(f'source {W}x{H}, {len(f)} frames measured{" (resting half)" if REST else ""}')
print(f'content box: x {x0}..{x1}  y {y0}..{y1}   ({bw} x {bh})')
sw, sh = FW / (bw + 2 * MX), FH / (bh + 2 * MY); s = min(sw, sh)        # the scale that fits the content and its margin into the space
if sw <= sh: cw, ch = bw + 2 * MX, bh + 2 * MY                        # the width decides: the strip comes out shorter than the space
else: ch = bh + 2 * MY; cw = round(FW / s)                            # the height decides: widen the crop to the space's shape
out_h = min(FH, round(ch * s / 2) * 2)
cx, cy = round((x0 + x1) / 2 - cw / 2), round((y0 + y1) / 2 - ch / 2)
pad_l, pad_r = max(0, -cx), max(0, cx + cw - W); pad_t, pad_b = max(0, -cy), max(0, cy + ch - H)
vf = []
if pad_l or pad_r or pad_t or pad_b: vf.append(f'pad=iw+{pad_l + pad_r}:ih+{pad_t + pad_b}:{pad_l}:{pad_t}:color=black')
vf.append(f'crop={cw}:{ch}:{cx + pad_l}:{cy + pad_t}'); vf.append(f'scale={FW}:{out_h}:flags=lanczos')
print(f'scale {s:.3f}: the content will be {round(bw * s)} x {round(bh * s)} px in a {FW} x {out_h} strip' + (f' (the space is {FW} x {FH}: centre the strip in it)' if out_h < FH else ''))
print('ffmpeg -vf "' + ','.join(vf) + '"')
if cy < K0 or cy + ch > K1: print(f'the crop reaches rows outside --keep ({K0}-{K1}): blank them first, for example drawbox=x=0:y=0:w=iw:h={K0}:color=black:t=fill')
if pad_l or pad_r or pad_t or pad_b: print('the margin runs past the source edge: the pad is black, so draw the strip "lighten" over a dark ground (or pad with the ground colour)')
