#!/usr/bin/env bash
# Aggregate journal entries matching <topic> for review before authoring a [STARTUP].
# Usage: journal-distill.sh <topic>
# Output: date | tag-line for every match, grouped by file.
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: $0 <topic>" >&2
  exit 1
fi

TOPIC="$1"
J="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}/journals"

if [ ! -d "$J" ]; then
  echo "No journals/ directory at $J" >&2
  exit 1
fi

echo "## Entries matching: $TOPIC"
echo

# Find .md files mentioning the topic (case-insensitive), then extract any tagged lines.
matches=$(grep -rli "$TOPIC" "$J" --include='*.md' 2>/dev/null || true)

if [ -z "$matches" ]; then
  echo "No entries matching '$TOPIC'."
  exit 0
fi

count=0
while IFS= read -r file; do
  date=$(basename "$(dirname "$file")")
  time=$(basename "$file" .md | cut -d- -f1-3)
  echo "### $date $time — $file"
  grep -n '\[[A-Z][A-Z-]*\]' "$file" 2>/dev/null | sed 's/^/  /' || true
  echo
  count=$((count + 1))
done <<< "$matches"

echo "---"
echo "Files matched: $count"
if [ "$count" -ge 3 ]; then
  echo
  echo "*Threshold reached (3+ entries).* Consider authoring or updating a [STARTUP] brief."
  echo "See .claude/skills/journaling/SKILL.md §The [STARTUP] Pattern."
fi
