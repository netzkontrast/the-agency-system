#!/usr/bin/env bash
# SessionStart hook: surface recent journal context token-cheaply via file grep.
# No MCP calls — just hands the agent a short briefing of what's already known.
set -euo pipefail

J="${CLAUDE_PROJECT_DIR:-.}/journals"
[ -d "$J" ] || { echo "## Journal: no entries yet — see .claude/skills/journaling/SKILL.md"; exit 0; }

echo "## Recent journal context"
echo

echo "### [STARTUP] briefs (last 30 days)"
startup_count=0
# Use find -mtime where available; fall back gracefully.
while IFS= read -r f; do
  [ -z "$f" ] && continue
  topic=$(grep -m1 '\[STARTUP\]' "$f" 2>/dev/null | sed -E 's/.*\[STARTUP\][[:space:]]+([^[:space:]]+).*/\1/' || true)
  updated=$(grep -m1 -oE 'updated:[[:space:]]*[0-9]{4}-[0-9]{2}-[0-9]{2}' "$f" 2>/dev/null | sed 's/updated:[[:space:]]*//' || echo unknown)
  [ -z "$topic" ] && continue
  echo "  - $topic (updated $updated) — $f"
  startup_count=$((startup_count + 1))
done < <(find "$J" -name '*.md' -mtime -30 -print 2>/dev/null | xargs -I{} grep -l '\[STARTUP\]' {} 2>/dev/null)

[ "$startup_count" -eq 0 ] && echo "  (none — write one when a topic accumulates 3+ tagged entries)"
echo

echo "### Recent [LEARNING] entries (last 3 days)"
learning_count=$(find "$J" -name '*.md' -mtime -3 -print 2>/dev/null \
  | xargs grep -h '\[LEARNING\]' 2>/dev/null \
  | head -10 \
  | sed 's/^/  /' \
  | tee /dev/stderr \
  | wc -l) 2>/dev/null || learning_count=0
[ "$learning_count" -eq 0 ] && echo "  (none in window)"
echo

echo "**Next:** invoke \`Skill('journaling')\` for the full session-start procedure, or \`/journal-brief <topic>\` to distill scattered entries on a topic into a [STARTUP] brief."
