#!/bin/bash
# Parse-check every script (npm run check). Lives in a file so npm can run it on Windows too, where npm scripts go through cmd.exe.
for f in tools/*.mjs tools/music/*.mjs tools/review-room/*.mjs gallery/previews-src/snap.mjs; do node --check "$f" || exit 1; done
for f in tools/*.sh; do bash -n "$f" || exit 1; done
echo all scripts parse
