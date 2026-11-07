#!/bin/bash
# Render a long film in parallel pieces and join them (picture only; add sound with mux-audio.sh).
# Run it from the project folder (the one with film.html, export.mjs and node_modules).
#
#   render-parallel.sh <fps> <duration_s> <out.mp4> [workers=3] [piece_s=12]
#   SUB=4 render-parallel.sh 60 78 master.mp4        # subframe motion blur on every piece
#
# Why: one browser renders about 4 to 8 frames a second at 1080p, so a 75 s film at 60 fps is ten minutes
# or more in a single process. Pieces are whole seconds long so each one prints progress at once, and a
# piece whose browser never starts (an empty log after 60 s) is started again. Three workers is a safe
# default on a laptop: every worker is a full Chrome, and six of them have run a 16 GB machine out of memory.
set -u
fps=${1:?fps}; dur=${2:?duration in seconds}; out=${3:?output mp4}; workers=${4:-3}; piece=${5:-12}
work="$(dirname "$out")/.pieces-$(basename "$out" .mp4)"; rm -rf "$work"; mkdir -p "$work"
# sums with fractions are done in awk, which every system with bash has (bc is missing on Windows and on a bare Linux)
lt() { LC_ALL=C awk -v a="$1" -v b="$2" 'BEGIN { exit !(a + 0 < b + 0) }'; }
starts=(); t=0; while lt "$t" "$dur"; do starts+=("$t"); t=$((t + piece)); done
n=${#starts[@]}
run_piece() { local i=$1 s=${starts[$1]} e; e=$(LC_ALL=C awk -v s="${starts[$1]}" -v p="$piece" -v d="$dur" 'BEGIN { e = s + p; if (e < d + 0) print e; else print d }')
  START=$s END=$e node export.mjs "$fps" "$work/p$i.mp4" > "$work/p$i.log" 2>&1 & echo $! > "$work/p$i.pid"; }
next=0; running=()
while [ $next -lt $n ] || [ ${#running[@]} -gt 0 ]; do
  while [ ${#running[@]} -lt "$workers" ] && [ $next -lt $n ]; do : > "$work/p$next.log"; date +%s > "$work/p$next.t0"; run_piece $next; running+=("$next"); next=$((next + 1)); done
  sleep 4; still=()
  for i in "${running[@]}"; do p=$(cat "$work/p$i.pid")
    if kill -0 "$p" 2>/dev/null; then
      if [ ! -s "$work/p$i.log" ] && [ $(( $(date +%s) - $(cat "$work/p$i.t0") )) -gt 60 ]; then kill "$p" 2>/dev/null; sleep 1; date +%s > "$work/p$i.t0"; run_piece "$i"; echo "piece $i restarted (its browser never started)"; fi
      still+=("$i")
    fi
  done
  running=("${still[@]:-}"); [ -z "${running[0]:-}" ] && running=()
done
: > "$work/list.txt"
for i in $(seq 0 $((n - 1))); do
  if ! ffprobe -v error -show_entries format=duration -of csv=p=0 "$work/p$i.mp4" > /dev/null 2>&1; then echo "piece $i failed: last lines of its log:"; tail -c 600 "$work/p$i.log" | tr '\r' '\n' | grep -v '^frame=' | tail -8; exit 1; fi
  echo "file 'p$i.mp4'" >> "$work/list.txt"
done
ffmpeg -v error -y -f concat -safe 0 -i "$work/list.txt" -c copy "$out" || exit 1
got=$(ffprobe -v error -count_packets -select_streams v -show_entries stream=nb_read_packets -of csv=p=0 "$out" | tr -d '\r'); want=$(LC_ALL=C awk -v d="$dur" -v f="$fps" 'BEGIN { printf "%d\n", d * f + 0.000001 }')
echo "wrote $out: $got frames (expected about $want)"; [ "$got" -ge $((want - 2)) ] || { echo "frame count is short: a piece stopped early, read its log in $work"; exit 1; }
rm -rf "$work"
