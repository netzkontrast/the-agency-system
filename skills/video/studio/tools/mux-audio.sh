#!/bin/bash
# Mux an audio track (already cut to length) into a video without re-encoding the picture.
# Usage: mux-audio.sh <video.mp4> <audio.wav|mp3> <out.mp4>
ffmpeg -y -v error -i "$1" -i "$2" -map 0:v -map 1:a -c:v copy -c:a aac -b:a 256k -shortest -movflags +faststart "$3" && echo "wrote $3"
