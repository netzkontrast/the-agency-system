#!/bin/bash
# Reverse-engineer a reference video: a 6x4 contact sheet across its whole length + 3 full frames.
# Usage: contact-sheet.sh <video> [outdir]
v="$1"; o="${2:-./ref-$(basename "${v%.*}")}"; mkdir -p "$o"
d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$v" | tr -d '\r')
ffmpeg -y -v error -i "$v" -vf "fps=24/$d,scale=480:-1,tile=6x4:padding=4" -frames:v 1 "$o/sheet.png"
for f in 0.15 0.5 0.8; do t=$(LC_ALL=C awk -v d="$d" -v f="$f" 'BEGIN { printf "%.3f\n", d * f }'); ffmpeg -y -v error -ss "$t" -i "$v" -frames:v 1 -vf scale=1280:-1 "$o/frame-$f.png"; done
ffprobe -v error -show_entries stream=width,height,r_frame_rate:format=duration -of default=nw=1 "$v"
echo "wrote $o/sheet.png and 3 frames"
