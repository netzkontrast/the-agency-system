#!/usr/bin/env python3
# scripts/cutseq.py : a subject cut-out for each of a clip's first frames, so a word can sit BEHIND a person who moves.
# Usage (from the film folder): python3 <skill>/scripts/cutseq.py <name> [frames=15]
#   reads assets/seq/<name>/fNNN.jpg (made by scripts/clip.py), writes assets/cut/seq/<name>/fNNN.png (alpha = the subject, scripts/matte.swift; macOS only, compiled on first use)
#   and assets/cutseq.js (which clips have cut-outs and for how many frames)
import sys, os, subprocess, json, re
if len(sys.argv) < 2: sys.exit('usage (from the film folder): python3 cutseq.py <name> [frames=15]   (macOS only; run clip.py first)')
name = sys.argv[1]; n = int(sys.argv[2]) if len(sys.argv) > 2 else 15
src, dst = f'assets/seq/{name}', f'assets/cut/seq/{name}'; os.makedirs(dst, exist_ok=True)
for f in os.listdir(dst):
    if f.endswith('.png'): os.remove(os.path.join(dst, f))
HERE = os.path.dirname(os.path.abspath(__file__)); MATTE = os.path.join(HERE, 'matte')
if not os.path.exists(MATTE): subprocess.run(['swiftc', '-O', os.path.join(HERE, 'matte.swift'), '-o', MATTE], check=True)      # the Mac's own subject cut-out, built once
done = 0
for i in range(n):
    a, b = f'{src}/f{i:03d}.jpg', f'{dst}/f{i:03d}.png'
    if not os.path.exists(a): break
    r = subprocess.run([MATTE, a, b, '1920'], capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(b): print('NO CUT-OUT for', a, r.stdout.strip(), r.stderr.strip()[:200]); sys.exit(1)
    done += 1
mf = 'assets/cutseq.js'
m = json.loads(re.search(r'window\.CUTSEQ=(\{.*\});', open(mf).read()).group(1)) if os.path.exists(mf) else {}
m[name] = done; open(mf, 'w').write('// written by scripts/cutseq.py: clips that have a subject cut-out for their first frames, name -> number of frames\nwindow.CUTSEQ=' + json.dumps(m) + ';\n')
print(f'{name}: {done} cut-outs -> {dst}')
