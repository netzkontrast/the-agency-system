#!/bin/bash
# scripts/doctor.sh : check that this machine has what Take One needs, and say what each missing piece is for.
# Usage: bash <skill>/scripts/doctor.sh        exit 0 = ready for the code-only route; 1 = something required is missing
ok()   { printf "  ok       %-18s %s\n" "$1" "$2"; }
miss() { printf "  MISSING  %-18s %s\n" "$1" "$2"; }
opt()  { printf "  optional %-18s %s\n" "$1" "$2"; }
need=0
echo "Take One: machine check"
echo "Required (every film):"
if command -v node >/dev/null 2>&1; then v=$(node -p "process.versions.node.split('.')[0]"); if [ "$v" -ge 18 ]; then ok node "$(node -v)"; else miss node "found $(node -v), needs 18 or later"; need=1; fi; else miss node "install Node 18 or later (nodejs.org)"; need=1; fi
command -v npm >/dev/null 2>&1 && ok npm "$(npm -v)" || { miss npm "comes with Node; each film project installs playwright-core with it"; need=1; }
command -v ffmpeg >/dev/null 2>&1 && ok ffmpeg "$(ffmpeg -version 2>/dev/null | head -1 | cut -d' ' -f3)" || { miss ffmpeg "joins the frames and mixes the sound (macOS: brew install ffmpeg)"; need=1; }
command -v ffprobe >/dev/null 2>&1 && ok ffprobe "" || { miss ffprobe "ships with ffmpeg"; need=1; }
if [ -d "/Applications/Google Chrome.app" ] || command -v google-chrome >/dev/null 2>&1 || command -v google-chrome-stable >/dev/null 2>&1 || [ -f "/c/Program Files/Google/Chrome/Application/chrome.exe" ]; then ok "Google Chrome" "draws every frame"; else miss "Google Chrome" "the frames are drawn in Chrome; install it (google.com/chrome)"; need=1; fi
echo "Optional (only some films):"
if command -v python3 >/dev/null 2>&1; then ok python3 "$(python3 -V 2>&1 | cut -d' ' -f2)"
  python3 -c "import numpy, scipy" 2>/dev/null && ok "numpy + scipy" "mapping a music track (songmap.py)" || opt "numpy + scipy" "needed to map a music track you cannot hear:  python3 -m pip install numpy scipy"
else opt python3 "needed for music mapping, voice cutting and video clips (songmap.py, vo.py, clip.py)"; fi
command -v whisper-cli >/dev/null 2>&1 && ok whisper-cli "checks that each cut voice line says its text" || opt whisper-cli "checks a recorded voice against the script (whisper.cpp); without it, voice lines are placed unchecked"
if [ "$(uname)" = "Darwin" ]; then command -v swift >/dev/null 2>&1 && ok swift "cut-outs, for type behind a person (matte.swift)" || opt swift "needed for cut-outs (type behind a person); comes with Xcode command line tools"
else opt swift "cut-outs (type behind a person) work on macOS only; other routes are unaffected"; fi
echo "Not checked here: paid services (pictures, video, voice, music). The skill asks before it uses any, and works without them."
[ $need -eq 0 ] && echo "Ready: the code-only route will run on this machine." || echo "Not ready: install what is marked MISSING, then run this again."
exit $need
