#!/bin/bash
# tools/doctor.sh : check that this machine has what Video Studio needs, and say what each missing piece is for.
# Usage: bash <studio>/tools/doctor.sh        exit 0 = ready for the code-only route; 1 = something required is missing
ok()   { printf "  ok       %-18s %s\n" "$1" "$2"; }
miss() { printf "  MISSING  %-18s %s\n" "$1" "$2"; }
opt()  { printf "  optional %-18s %s\n" "$1" "$2"; }
need=0
echo "Video Studio: machine check"
echo "Required (every film):"
if command -v node >/dev/null 2>&1; then v=$(node -p "process.versions.node.split('.')[0]"); if [ "$v" -ge 18 ]; then ok node "$(node -v)"; else miss node "found $(node -v), needs 18 or later"; need=1; fi; else miss node "install Node 18 or later (nodejs.org)"; need=1; fi
command -v npm >/dev/null 2>&1 && ok npm "$(npm -v)" || { miss npm "comes with Node; each film project installs playwright-core with it"; need=1; }
command -v ffmpeg >/dev/null 2>&1 && ok ffmpeg "$(ffmpeg -version 2>/dev/null | head -1 | cut -d' ' -f3)" || { miss ffmpeg "joins the frames and mixes the sound (macOS: brew install ffmpeg)"; need=1; }
command -v ffprobe >/dev/null 2>&1 && ok ffprobe "" || { miss ffprobe "ships with ffmpeg"; need=1; }
S="$(cd "$(dirname "$0")/.." && pwd)"
if [ -d "$S/node_modules/p5.brush" ] && [ -d "$S/node_modules/playwright-core" ]; then ok "studio packages" "p5, p5.brush, playwright-core in $S/node_modules"
elif command -v npm >/dev/null 2>&1 && (cd "$S" && npm install --silent >/dev/null 2>&1); then ok "studio packages" "installed now (npm install in $S)"
else miss "studio packages" "run: (cd $S && npm install)"; need=1; fi
chrome=$(node "$S/tools/lib/browser.mjs" 2>/dev/null | node -e 'let s="";process.stdin.on("data",d=>s+=d).on("end",()=>{try{console.log(JSON.parse(s).chrome||"")}catch{console.log("")}})')
if [ -n "$chrome" ]; then ok "Chrome/Chromium" "$chrome (draws every frame; override with CHROME_PATH)"
elif [ -d "/Applications/Google Chrome.app" ]; then ok "Google Chrome" "draws every frame"
else miss "Chrome/Chromium" "the frames are drawn in Chrome; install it (google.com/chrome) or set CHROME_PATH"; need=1; fi
echo "  note     GPU: without one, set STUDIO_GL=soft (software WebGL, ~20-30 s per 1080p painted frame); check with: node $S/tools/gpu_probe.mjs"
echo "Optional (only some films):"
if command -v python3 >/dev/null 2>&1; then ok python3 "$(python3 -V 2>&1 | cut -d' ' -f2)"
  python3 -c "import numpy, scipy" 2>/dev/null && ok "numpy + scipy" "bar map (audio/beatmap.py), flash test, stress times" || opt "numpy + scipy" "bar map, flash test and lyric stress times:  python3 -m pip install numpy scipy"
  python3 -c "import stable_whisper" 2>/dev/null && ok "stable-ts" "aligns the known lyrics word by word (audio/align_lyrics.py)" || opt "stable-ts" "word times for a music video's lyrics:  python3 -m pip install stable-ts"
  python3 -c "import demucs" 2>/dev/null && ok "demucs" "vocal stem for alignment and stress times" || opt "demucs" "cleaner lyric timing from the vocal stem:  python3 -m pip install demucs"
  python3 -c "import beat_this" 2>/dev/null && ok "beat_this" "stronger beat/downbeat tracking (audio/beat_this_track.py)" || opt "beat_this" "stronger beats/downbeats for soft or drifting songs:  python3 -m pip install beat-this"
  python3 -c "import iris_pse_detection" 2>/dev/null && ok "iris-pse-detection" "second opinion on flashes (flash_test.py --iris)" || opt "iris-pse-detection" "EA IRIS flash analysis as a second opinion:  python3 -m pip install iris-pse-detection"
else opt python3 "needed for music mapping, voice cutting and video clips (songmap.py, vo.py, clip.py)"; fi
command -v whisper-cli >/dev/null 2>&1 && ok whisper-cli "checks that each cut voice line says its text" || opt whisper-cli "checks a recorded voice against the script (whisper.cpp); without it, voice lines are placed unchecked"
if [ "$(uname)" = "Darwin" ]; then command -v swift >/dev/null 2>&1 && ok swift "cut-outs, for type behind a person (matte.swift)" || opt swift "needed for cut-outs (type behind a person); comes with Xcode command line tools"
else opt swift "cut-outs (type behind a person) work on macOS only; other routes are unaffected"; fi
command -v nvidia-smi >/dev/null 2>&1 && ok "NVIDIA GPU" "$(nvidia-smi --query-gpu=name --format=csv,noheader | head -1)" || opt "GPU" "path-traced films want a real GPU (Apple, NVIDIA, AMD): see references/pathtracer/rendering.md"
echo "Not checked here: paid services (pictures, video, voice, music). The skill asks before it uses any, and works without them."
[ $need -eq 0 ] && echo "Ready: the code-only route will run on this machine." || echo "Not ready: install what is marked MISSING, then run this again."
exit $need
