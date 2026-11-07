#!/bin/bash
# The storyboard, drawn: tile one rough frame per shot into a single sheet the person can read at a glance.
#   storyboard-sheet.sh <folder of frames, named in shot order> <out.png> [columns=4]
# Frames are pencil sketches from an image model (pictures route) or blockout frames rendered from the page (code route).
set -u
dir=${1:?folder of frames}; out=${2:?out.png}; cols=${3:-4}; T=$(mktemp -d); i=0
for f in $(ls "$dir" | grep -i -E '\.(png|jpg|jpeg|webp)$' | sort); do ffmpeg -v error -y -i "$dir/$f" -vf "scale=480:270:force_original_aspect_ratio=decrease,pad=480:270:(ow-iw)/2:(oh-ih)/2:color=0x101010" "$T/s$(printf %03d $i).png"; i=$((i + 1)); done
[ $i -eq 0 ] && { echo "no frames in $dir"; exit 1; }
ffmpeg -v error -y -i "$T/s%03d.png" -vf "tile=${cols}x$(( (i + cols - 1) / cols )):padding=6:margin=6:color=0x202020" -frames:v 1 "$out" && echo "storyboard sheet: $out ($i shots, read left to right, top to bottom)"; rm -rf "$T"
