#!/usr/bin/env bash
# List [STARTUP] briefs by age. Run periodically when working a topic to check freshness.
set -euo pipefail

J="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}/journals"

if [ ! -d "$J" ]; then
  echo "No journals/ directory at $J" >&2
  exit 1
fi

echo "## [STARTUP] briefs by age"
echo

today_epoch=$(date +%s)

# Find every file containing [STARTUP], extract topic + updated date, output sorted by age.
grep -rl '\[STARTUP\]' "$J" --include='*.md' 2>/dev/null \
  | while IFS= read -r file; do
      topic_line=$(grep -m1 '\[STARTUP\]' "$file" || true)
      [ -z "$topic_line" ] && continue
      topic=$(echo "$topic_line" | sed -E 's/.*\[STARTUP\][[:space:]]+([^[:space:]]+).*/\1/')
      updated=$(grep -m1 -oE 'updated:[[:space:]]*[0-9]{4}-[0-9]{2}-[0-9]{2}' "$file" | sed 's/updated:[[:space:]]*//' || true)
      [ -z "$updated" ] && updated="unknown"
      if [ "$updated" != "unknown" ]; then
        upd_epoch=$(date -d "$updated" +%s 2>/dev/null || echo 0)
        age_days=$(( (today_epoch - upd_epoch) / 86400 ))
      else
        age_days=9999
      fi
      printf "%5d  %-30s  updated %s  %s\n" "$age_days" "$topic" "$updated" "$file"
    done \
  | sort -rn \
  | awk '{
      age=$1
      flag=""
      if (age >= 30 && age < 9999) flag="  *STALE — review*"
      if (age == 9999) flag="  *missing updated: line*"
      $1=""
      printf "  %3d days%s%s\n", age, $0, flag
    }'

echo
echo "Briefs with age >=30 days should be reviewed (and superseded with a fresh entry if still working that topic)."
