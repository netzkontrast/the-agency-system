#!/bin/bash
# Install git hooks for agency-system plugin

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Define target paths
HOOKS_TARGET_DIR="$HOME/.claude/hooks/agency-system"

echo "Installing agency-system hooks to $HOOKS_TARGET_DIR..."

mkdir -p "$HOOKS_TARGET_DIR"

if [ -f "$SCRIPT_DIR/hooks.json" ]; then
    cp "$SCRIPT_DIR/hooks.json" "$HOOKS_TARGET_DIR/"
    echo "✓ Installed hooks.json"
fi

if [ -f "$SCRIPT_DIR/validate_track.py" ]; then
    cp "$SCRIPT_DIR/validate_track.py" "$HOOKS_TARGET_DIR/"
    chmod +x "$HOOKS_TARGET_DIR/validate_track.py"
    echo "✓ Installed validate_track.py"
fi

if [ -f "$SCRIPT_DIR/validate_chapter.py" ]; then
    cp "$SCRIPT_DIR/validate_chapter.py" "$HOOKS_TARGET_DIR/"
    chmod +x "$HOOKS_TARGET_DIR/validate_chapter.py"
    echo "✓ Installed validate_chapter.py"
fi

if [ -f "$SCRIPT_DIR/check_version_sync.py" ]; then
    cp "$SCRIPT_DIR/check_version_sync.py" "$HOOKS_TARGET_DIR/"
    chmod +x "$HOOKS_TARGET_DIR/check_version_sync.py"
    echo "✓ Installed check_version_sync.py"
fi

echo ""
echo "Agency system hooks installed successfully!"
