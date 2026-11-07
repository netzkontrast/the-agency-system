#!/bin/bash
# Parse-check every script (npm run check). Lives in a file so npm can run it on Windows too, where npm scripts go through cmd.exe.
for f in scripts/*.mjs scripts/music/*.mjs scripts/review-room/*.mjs assets/previews-src/snap.mjs; do node --check "$f" || exit 1; done
for f in scripts/*.sh; do bash -n "$f" || exit 1; done
echo all scripts parse
