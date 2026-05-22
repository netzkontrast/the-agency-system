#!/usr/bin/env bash
# tools/cleanup-merged-branches.sh
#
# Delete all branches on the netzkontrast/the-agency-system remote that
# are NOT linked to an open PR. Safe by default: dry-run; pass --force
# to actually execute the deletions.
#
# Auth: requires gh CLI authenticated with `repo` scope OR a
# GITHUB_TOKEN env var with delete_ref permission.
#
# Why this script and not an orchestrator-driven cleanup: the Claude
# orchestrator's GitHub auth (via MCP) is read+merge but does NOT
# include branch deletion. So the user runs this locally with their
# own credentials when they want to clean up.
#
# Usage:
#   tools/cleanup-merged-branches.sh                  # dry-run
#   tools/cleanup-merged-branches.sh --force          # execute
#   tools/cleanup-merged-branches.sh --keep PATTERN   # extra keep-pattern (regex)

set -euo pipefail

REPO="netzkontrast/the-agency-system"
DEFAULT_KEEP="Master"   # protected branch — never delete

FORCE=0
EXTRA_KEEP=""
while [ $# -gt 0 ]; do
  case "$1" in
    --force)  FORCE=1; shift ;;
    --keep)   EXTRA_KEEP="$2"; shift 2 ;;
    --help|-h)
      grep '^#' "$0" | sed 's/^# //;s/^#//'
      exit 0 ;;
    *) echo "Unknown arg: $1" >&2; exit 2 ;;
  esac
done

command -v gh >/dev/null || { echo "ERROR: gh CLI not found. Install: https://cli.github.com/" >&2; exit 1; }

# Resolve current open PR head refs (always kept)
echo "Fetching open PR heads…" >&2
OPEN_PR_HEADS=$(gh pr list --repo "$REPO" --state open --json headRefName --jq '.[].headRefName')

# Build keep pattern
KEEP_PATTERN="^($DEFAULT_KEEP"
while IFS= read -r ref; do
  [ -z "$ref" ] && continue
  KEEP_PATTERN="$KEEP_PATTERN|$(printf '%s' "$ref" | sed 's/[.[\^$*+?(){}|]/\\&/g')"
done <<< "$OPEN_PR_HEADS"
if [ -n "$EXTRA_KEEP" ]; then
  KEEP_PATTERN="$KEEP_PATTERN|$EXTRA_KEEP"
fi
KEEP_PATTERN="$KEEP_PATTERN)\$"

# List remote branches
echo "Listing remote branches…" >&2
ALL_BRANCHES=$(gh api "repos/$REPO/branches" --paginate --jq '.[].name')

# Compute delete set
DELETE_SET=$(echo "$ALL_BRANCHES" | grep -Ev "$KEEP_PATTERN" || true)

if [ -z "$DELETE_SET" ]; then
  echo "Nothing to delete — only protected + open-PR branches remain."
  exit 0
fi

echo
echo "Branches to keep (protected + open PR heads):"
echo "$ALL_BRANCHES" | grep -E "$KEEP_PATTERN" | sed 's/^/  ✓ /'

echo
echo "Branches to DELETE:"
echo "$DELETE_SET" | sed 's/^/  ✗ /'
COUNT=$(echo "$DELETE_SET" | wc -l)
echo
echo "Total: $COUNT branches"

if [ "$FORCE" != "1" ]; then
  echo
  echo "DRY RUN. Pass --force to execute."
  exit 0
fi

echo
read -r -p "Proceed with deletion of $COUNT branches? [y/N] " ans
[ "$ans" = "y" ] || [ "$ans" = "Y" ] || { echo "Aborted."; exit 1; }

deleted=0
failed=0
while IFS= read -r branch; do
  if gh api -X DELETE "repos/$REPO/git/refs/heads/$branch" >/dev/null 2>&1; then
    deleted=$((deleted+1))
    printf '  deleted: %s\n' "$branch"
  else
    failed=$((failed+1))
    printf '  FAILED:  %s\n' "$branch" >&2
  fi
done <<< "$DELETE_SET"

echo
echo "Done. Deleted: $deleted · Failed: $failed"
