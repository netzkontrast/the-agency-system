#!/bin/bash
# Build the pack a fresh reviewer reads: what a stranger would see, and nothing about how it was made.
#
#   review-pack.sh <cut.mp4> <pack_dir> [--beats "0,1.5,4.8,..."] [--strips "9.2-11.6,66.0-67.2"] [--text "4.8,9.6,..."]
#
# Writes into <pack_dir>:
#   sheet_1fps_partN.png   one frame per second of the whole film, 40 per sheet
#   beats_gridN.png        frames at the story beats, 9 per grid (default: 36 evenly spaced)
#   full_t<time>.png       every 5th beat at full size
#   strip_<a>-<b>.png      12 consecutive frames across each fast move or key transition you list
#   phone_360px.png        the frames that carry words, at phone width (default: the beats)
#   WORDS-AND-SOUND.md     a form to fill in: who it is for, the words with times, the sound report
# Then hand the folder to a new agent with references/reviewer-brief.md.
set -u
V=${1:?cut.mp4}; P=${2:?pack dir}; shift 2; beats=""; strips=""; text=""
while [ $# -gt 0 ]; do case "$1" in --beats) beats=$2; shift 2;; --strips) strips=$2; shift 2;; --text) text=$2; shift 2;; *) echo "unknown option $1"; exit 2;; esac; done
# times are plain numbers and ranges of numbers; anything else stops here, before any of it is used
num='[0-9]+(\.[0-9]+)?'
ok() { [ -z "$1" ] || printf '%s' "$1" | grep -Eq "^$2(,$2)*$"; }
ok "$beats" "$num" || { echo "--beats takes times in seconds, like 0,1.5,4.8"; exit 2; }
ok "$text" "$num" || { echo "--text takes times in seconds, like 4.8,9.6"; exit 2; }
ok "$strips" "$num-$num" || { echo "--strips takes ranges in seconds, like 9.2-11.6,66.0-67.2"; exit 2; }
[ -f "$V" ] || { echo "no such film: $V"; exit 2; }
# the pack folder is emptied only when it is new, empty, or a pack this script made before
if [ -e "$P" ] && [ -n "$(ls -A "$P" 2>/dev/null)" ] && [ ! -f "$P/WORDS-AND-SOUND.md" ]; then echo "$P holds other files; give a new folder for the pack"; exit 2; fi
rm -rf "$P"; mkdir -p "$P"; T=$(mktemp -d)
dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$V" | tr -d '\r'); D=${dur%.*}
k=0; s=0; while [ $s -lt "$D" ]; do k=$((k + 1)); ffmpeg -v error -y -ss $s -t 39.9 -i "$V" -vf "fps=1,scale=400:-1,tile=8x5:padding=4:color=gray" -frames:v 1 "$P/sheet_1fps_part$k.png"; s=$((s + 40)); done
# the sums are done in awk, which every system with bash has, so the pack needs nothing beyond ffmpeg
if [ -z "$beats" ]; then beats=$(LC_ALL=C awk -v d="$dur" 'BEGIN { for (i = 0; i < 36; i++) printf "%s%.1f", (i ? "," : ""), d * i / 35.5; print "" }'); fi
IFS=',' read -ra B <<< "$beats"; i=0
for t in "${B[@]}"; do ffmpeg -v error -y -ss "$t" -i "$V" -frames:v 1 -vf scale=640:-1 "$T/b$(printf %03d $i).png"; [ $((i % 5)) -eq 0 ] && ffmpeg -v error -y -ss "$t" -i "$V" -frames:v 1 "$P/full_t$t.png"; i=$((i + 1)); done
g=0; j=0; while [ $j -lt ${#B[@]} ]; do g=$((g + 1)); ffmpeg -v error -y -start_number $j -i "$T/b%03d.png" -frames:v 9 -vf "tile=3x3" -frames:v 1 "$P/beats_grid$g.png" 2>/dev/null; j=$((j + 9)); done
IFS=',' read -ra S <<< "$strips"
for r in "${S[@]:-}"; do [ -z "$r" ] && continue; a=${r%-*}; b=${r#*-}; len=$(LC_ALL=C awk -v a="$a" -v b="$b" 'BEGIN { printf "%.3f\n", b - a }'); ffmpeg -v error -y -ss "$a" -t "$len" -i "$V" -vf "fps=12/$len,scale=480:-1,tile=4x3:padding=3:color=gray" -frames:v 1 "$P/strip_$a-$b.png"; done
[ -z "$text" ] && text=$beats; IFS=',' read -ra X <<< "$text"; i=0
for t in "${X[@]}"; do [ $i -ge 20 ] && break; ffmpeg -v error -y -ss "$t" -i "$V" -frames:v 1 -vf scale=360:-1 "$T/p$(printf %03d $i).png"; i=$((i + 1)); done
ffmpeg -v error -y -i "$T/p%03d.png" -vf "tile=5x$(( (i + 4) / 5 ))" -frames:v 1 "$P/phone_360px.png" 2>/dev/null
cat > "$P/WORDS-AND-SOUND.md" <<FORM
# The film: ${dur%.*} s. FILL IN: format, where it posts.
Audience: FILL IN (who it is for). It will often be seen muted, on a phone, once.

## Words spoken or sung, with film times
FILL IN, one line per phrase:  <time>  <words>

## Sound report (the reviewer cannot hear it)
FILL IN from scripts/audio-check.mjs and scripts/songmap.py: loudness and true peak; where the music is quiet, where it hits hardest; any sound effects and where they land.

## Beat times in beats_grid*.png, in order
$beats

## Files
sheet_1fps_part*.png (one frame per second), beats_grid*.png (9 per grid, times above), full_t*.png (full size), strip_*.png (12 frames across a fast move, range in the name), phone_360px.png (frames with words at phone width). The film itself: $(basename "$V").
FORM
rm -rf "$T"; echo "pack in $P: $(ls "$P" | wc -l | tr -d ' ') files. Fill in WORDS-AND-SOUND.md before handing it over."
