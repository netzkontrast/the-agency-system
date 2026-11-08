#!/usr/bin/env bash
# tools/new-project.sh — start a film project from one of the studio's media.
#
#   bash <studio>/tools/new-project.sh <dir> [--medium paint|canvas|three|shader|pathtracer] [--duration S] [--bpm N] [--character]
#   bash <studio>/tools/new-project.sh <dir> --update        # refresh the copied engine files from the studio
#
# paint       painted 2D: p5.js + p5.brush (ink, watercolour, charcoal hatching, boil, paper) — the default
# canvas      plain 2D canvas with springs: kinetic type, explainers, HUDs, title sequences, data stories
# three       three.js 3D, any look through engine/three/passes.js (ink, toon, kuwahara, watercolor, hatch, halftone, riso, dither, crt ...)
# shader      fullscreen fragment shaders (Shadertoy-style uniforms, iTime = t): abstract, generative, visualizers
# pathtracer  physically based 3D (WebGPU path tracer), short films and stills; copied from examples/felt-good-morning
#
# Every medium writes the same project shell: STORYBOARD.md, BUILD_NOTES.md, songmap/, review/, out/ (ignored).
set -euo pipefail
S="$(cd "$(dirname "$0")/.." && pwd)"
dir="${1:?usage: new-project.sh <dir> [--medium paint|canvas|three|shader|pathtracer] [--duration S] [--bpm N] [--character] [--update]}"; shift
medium=paint; dur=15; bpm=120; character=0; update=0
while [ $# -gt 0 ]; do case "$1" in
  --medium) medium="$2"; shift 2;; --duration) dur="$2"; shift 2;; --bpm) bpm="$2"; shift 2;;
  --character) character=1; shift;; --update) update=1; shift;; *) echo "unknown option $1" >&2; exit 2;; esac; done
if [ "$update" = 1 ]; then
  [ -f "$dir/.studio-medium" ] || { echo "$dir is not a studio project (no .studio-medium)" >&2; exit 2; }
  medium="$(cat "$dir/.studio-medium")"
fi
mkdir -p "$dir"
dir="$(cd "$dir" && pwd)"
[ -d "$S/node_modules" ] || (cd "$S" && npm install --silent)

copy_engine() {
  mkdir -p "$dir/engine"
  cp "$S/engine/lib/beat.js" "$S/engine/lib/springs.js" "$S/engine/lib/life.js" "$dir/engine/"
  if [ "$medium" = paint ]; then cp "$S"/engine/paint/{core,timeline,sheets,clawd}.js "$dir/engine/"; fi
  if [ "$medium" = three ]; then cp "$S/engine/three/passes.js" "$dir/engine/"; fi
  if [ "$medium" = shader ]; then cp "$S/engine/shader/runtime.js" "$dir/engine/"; fi
  if [ "$medium" = three ] || [ "$medium" = shader ]; then mkdir -p "$dir/engine/glsl"; cp "$S"/engine/glsl/*.glsl "$dir/engine/glsl/"; fi
  ln -sfn "$S/node_modules" "$dir/node_modules"
}

if [ "$update" = 1 ]; then copy_engine; echo "engine files refreshed in $dir ($medium)"; exit 0; fi
[ -e "$dir/film.html" ] || [ -e "$dir/shots" ] && { echo "$dir already holds a film; use --update to refresh the engine" >&2; exit 2; }
echo "$medium" > "$dir/.studio-medium"
mkdir -p "$dir/songmap" "$dir/review" "$dir/out" "$dir/assets" "$dir/lib"
printf 'out/\nnode_modules\n*.part\n' > "$dir/.gitignore"
[ -f "$dir/songmap.js" ] || echo 'window.SONGMAP = null; // written by <studio>/tools/audio/songmap_js.py' > "$dir/songmap.js"

case "$medium" in
paint)
  copy_engine
  cp "$S/engine/paint/film.html" "$dir/film.html"
  cat > "$dir/config.js" <<EOF
// config.js: project settings. duration in seconds; bpm/offset are the fallback beat when no song map is loaded.
const PROJECT = { duration: $dur, bpm: $bpm, offset: 0 };
EOF
  if [ "$character" = 1 ]; then sed -i.bak 's#<!-- <script src="engine/clawd.js"></script> <script src="engine/sheets.js"></script> -->#<script src="engine/clawd.js"></script> <script src="engine/sheets.js"></script>#' "$dir/film.html" && rm -f "$dir/film.html.bak"; fi
  mkdir -p "$dir/scenes"
  cat > "$dir/scenes/ch01.js" <<'EOF'
// ch01.js: chapter 1. Each shot fn(t, lt, dur) paints the WHOLE frame and is a pure function of t.
// Read <studio>/references/paint-medium.md before drawing (rules, workflow, full API).
(() => {
  shots([
    [0, (t, lt, dur) => {
      boilSeed('ground');
      paint(rectPts(-60, H * .62, W + 120, H * .5), { wash: PAL.clay, fill: PAL.clayDk, fillOp: 70, bleed: .1, ink: null });
      boilSeed('sun');
      const r = 90 + 12 * SONG.pulse(t);
      paint(ellPts(W / 2, H * .42, r, r, 28, 2), { wash: PAL.ochre, ink: PAL.ink, sw: 1 });
      glow(W / 2, H * .42, r * 2.4, '#FFC766', .8);
      if (lt < .3) brushWipe(.5 + lt / .6);
      // the last shot ends on a hold or a fade, not a wipe the film's end cuts in half (the gate flags that as a pop)
    }],
  ]);
})();
EOF
  ;;
canvas)
  copy_engine
  cp "$S/engine/canvas/film.html" "$dir/film.html"
  cat > "$dir/config.js" <<EOF
// config.js: project settings. duration in seconds; bpm/offset are the fallback beat when no song map is loaded.
const PROJECT = { duration: $dur, bpm: $bpm, offset: 0 };
EOF
  ;;
three)
  copy_engine
  cp "$S/engine/three/film.html" "$dir/film.html"
  printf '// config.js: project settings. duration in seconds; bpm/offset are the fallback beat when no song map is loaded.\nconst PROJECT = { duration: %s, bpm: %s, offset: 0 };\n' "$dur" "$bpm" > "$dir/config.js"
  mkdir -p "$dir/scenes"; cp "$S/engine/three/scene.template.js" "$dir/scenes/scene.js"
  ;;
shader)
  copy_engine
  cp "$S/engine/shader/film.html" "$dir/film.html"
  printf '// config.js: project settings. duration in seconds; bpm/offset are the fallback beat when no song map is loaded.\nconst PROJECT = { duration: %s, bpm: %s, offset: 0 };\n' "$dur" "$bpm" > "$dir/config.js"
  mkdir -p "$dir/scenes"; cp "$S/engine/shader/film.template.js" "$dir/scenes/film.js"; cp "$S"/engine/shader/*.template.frag "$dir/scenes/" 2>/dev/null
  for f in "$dir"/scenes/*.template.frag; do [ -e "$f" ] && mv "$f" "${f%.template.frag}.frag"; done
  ;;
pathtracer)
  cp -R "$S/examples/felt-good-morning/." "$dir/"
  ln -sfn "$S/engine/pathtracer" "$dir/engine-pt"
  python3 - "$dir" <<'EOF'
import os, re, sys
root = sys.argv[1]
for base, _, files in os.walk(root):
    if 'node_modules' in base or 'engine-pt' in base: continue
    for f in files:
        if not f.endswith(('.mjs', '.sh', '.md')): continue
        p = os.path.join(base, f); s = open(p).read()
        rel = os.path.relpath(os.path.join(root, 'engine-pt'), base).replace(os.sep, '/')
        n = re.sub(r"(?:\.\./)+engine/pathtracer/", rel + '/', s)
        n = n.replace("engine/pathtracer/tools/", "engine-pt/tools/")
        if n != s: open(p, 'w').write(n)
EOF
  echo "pathtracer project: run 'bash $S/engine/pathtracer/setup.sh' once, then 'node render_local.mjs --dry-run' in $dir"
  ;;
*) echo "unknown medium $medium (paint|canvas|three|shader|pathtracer)" >&2; exit 2;;
esac

[ -f "$dir/STORYBOARD.md" ] || cat > "$dir/STORYBOARD.md" <<'EOF'
# Storyboard

One idea (one sentence):
Payoff (the moment people rewatch):
Playbook: <studio>/playbooks/<name>.md   Medium: <paint|canvas|pathtracer>   Format: 1920x1080, 24 fps, <length>

| # | Time (s) | Section / lyric line (key word @ time) | What happens | Reads (in order) | Transition out | Chapter |
|---|---|---|---|---|---|---|
| 1 | 0.0–4.0 | | | | | ch01 |
EOF
[ -f "$dir/BUILD_NOTES.md" ] || cat > "$dir/BUILD_NOTES.md" <<'EOF'
# Build notes (as built, not as planned)

Every agent reads this first. Append every direction the lead gives during the build, the shared APIs as delivered,
file ownership per chapter, and the render/review commands.

## Owners
| File | Owner |
|---|---|
| film.html, config.js, songmap.js, engine/ | lead (read-only for chapter animators) |

## Directions from the lead
EOF
echo "project ready: $dir ($medium). Scrub: open film.html via 'node $S/tools/serve-project.mjs $dir'. Check: (cd $dir && node $S/tools/render.mjs --sheet=0,1,2,3)"
