#!/usr/bin/env python3
# scripts/clip.py : turn a rendered video clip into frames the film can draw exactly (one picture per film frame, 30 a second).
# Usage (from the film folder): python3 <skill>/scripts/clip.py <clip.mp4> <name> [start seconds=0] [seconds=3] [frame width=1920]
#   -> assets/seq/<name>/f000.jpg ... and assets/seq.js (which clips exist and how many frames each has)
import sys, os, subprocess, json, re
if len(sys.argv) < 3: sys.exit('usage (from the film folder): python3 clip.py <clip.mp4> <name> [start seconds=0] [seconds=3] [frame width=1920]')
src, name = sys.argv[1], sys.argv[2]; start = float(sys.argv[3]) if len(sys.argv) > 3 else 0; dur = float(sys.argv[4]) if len(sys.argv) > 4 else 3
WIDE = int(sys.argv[5]) if len(sys.argv) > 5 else 1920          # frame width to keep: more than 1920 when the film crops into the shot (the source must really have it)
d = f'assets/seq/{name}'; os.makedirs(d, exist_ok=True)
for f in os.listdir(d):
    if f.endswith('.jpg'): os.remove(os.path.join(d, f))
# every source frame becomes one film frame (no frame is repeated or dropped), so a 24 fps clip plays a quarter faster and stays perfectly smooth
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(start), '-i', src, '-vf', f'scale={WIDE}:{WIDE * 9 // 16}:flags=lanczos', '-fps_mode', 'passthrough', '-frames:v', str(int(round(dur * 30))), '-q:v', '2', '-start_number', '0', f'{d}/f%03d.jpg'], check=True)
n = len([f for f in os.listdir(d) if f.endswith('.jpg')]); mf = 'assets/seq.js'
m = json.loads(re.search(r'window\.SEQ=(\{.*\});', open(mf).read()).group(1)) if os.path.exists(mf) else {}
m[name] = n; open(mf, 'w').write('// written by scripts/clip.py: video clips as frame sequences, name -> number of frames (30 a second)\nwindow.SEQ=' + json.dumps(m) + ';\n')
print(f'{name}: {n} frames -> {d}')
