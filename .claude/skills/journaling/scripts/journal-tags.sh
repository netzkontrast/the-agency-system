#!/usr/bin/env bash
# Audit tag usage across all journal entries.
# Output: frequency table of [TAG] occurrences, sorted descending.
set -uo pipefail

J="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}/journals"

if [ ! -d "$J" ]; then
  echo "No journals/ directory at $J" >&2
  exit 1
fi

echo "## Tag frequency across $J"
echo

# Match [WORDS-IN-CAPS] tag prefixes. Skip .embedding binary files.
counts=$(find "$J" -name '*.md' -type f -print0 \
  | xargs -0 grep -oh '\[[A-Z][A-Z-]*\]' 2>/dev/null \
  | sort \
  | uniq -c \
  | sort -rn \
  | awk '{printf "  %4d  %s\n", $1, $2}')

if [ -z "$counts" ]; then
  echo "  (no tagged entries yet)"
else
  echo "$counts"
fi

echo
echo "Canonical ontology: [LEARNING] [TOKEN-COST] [GOTCHA] [DECISION] [USER-PREF] [STARTUP] [BLOCKER]"
echo "Anything else above is drift — see .claude/skills/journaling/SKILL.md"
