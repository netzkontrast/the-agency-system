#!/usr/bin/env python3
# scripts/plate.py : a still's background with the subject taken out, so the subject can move in front of it.
#
# One photograph becomes a shot with depth: cut the subject out (matte.swift), fill its place in the picture (this script),
# then draw three layers that move apart as the camera pushes in or slides: the plate, anything that belongs between (a word),
# the cut-out. The subject only ever moves a little off its own place, so only a thin rim of the fill is seen; it is filled
# with the colours round the hole, blurred more the deeper into it. This is not a clean plate for a subject that leaves.
#
# Usage: python3 <skill>/scripts/plate.py <photo> <cut-out.png> <out.jpg> [--grow 16] [--quality 92]
#   <cut-out.png>  the same size as the photo, its alpha the subject (from: swift <skill>/scripts/matte.swift photo.jpg cut.png)
#   --grow N       how far past the cut-out's edge the hole reaches, in pixels (default 16: past its soft edge, so none of the
#                  subject's colour is sampled into the fill). Raise it when a rim of the subject's colour shows in the plate.
# Needs numpy, scipy, Pillow. See references/real-shots.md, "A still as a shot with depth".
import sys
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, binary_dilation

a = sys.argv[1:]
if len(a) < 3: sys.exit('usage: python3 plate.py <photo> <cut-out.png> <out.jpg> [--grow 16] [--quality 92]')
def opt(name, default): return a[a.index(name) + 1] if name in a else default
GROW, Q = int(opt('--grow', '16')), int(opt('--quality', '92'))
img = np.asarray(Image.open(a[0]).convert('RGB')).astype(np.float32)
cut = Image.open(a[1]).convert('RGBA')
if cut.size != (img.shape[1], img.shape[0]): sys.exit(f'the cut-out is {cut.size[0]}x{cut.size[1]} and the photo is {img.shape[1]}x{img.shape[0]}: they must be the same size')
hole = binary_dilation(np.asarray(cut)[:, :, 3] > 6, iterations=GROW)
if not hole.any(): sys.exit('the cut-out is empty: nothing to take out')
valid = (~hole).astype(np.float32)
out = None
s = max(img.shape[:2]) / 6.0
sig = []
while s >= 5: sig.append(s); s /= 2          # coarse first, then finer fills laid over it where they are sure
for s in sig:
    den = gaussian_filter(valid, s)
    num = np.stack([gaussian_filter(img[:, :, c] * valid, s) for c in range(3)], axis=2)
    f = num / np.maximum(den, 1e-4)[:, :, None]
    w = np.clip(den / 0.28, 0, 1)[:, :, None]
    out = f if out is None else w * f + (1 - w) * out
edge = gaussian_filter(hole.astype(np.float32), 3)[:, :, None]   # a soft seam between the photograph and the fill
res = img * (1 - edge) + out * edge
Image.fromarray(np.clip(res, 0, 255).astype(np.uint8)).save(a[2], quality=Q)
print(f'wrote {a[2]}: {res.shape[1]}x{res.shape[0]}, the hole is {hole.mean() * 100:.1f}% of the frame')
print('the fill is only good for a rim: keep the subject within about 3% of the frame of its own place (scale and slide together)')
