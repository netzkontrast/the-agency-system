#!/usr/bin/env bash
# Setup script for the bitwize-music plugin MCP server.
#
# Creates ~/.bitwize-music/venv and installs the plugin's Python
# dependencies so the `bitwize-music-mcp` MCP server can start.
# Invoked from the SessionStart hook in .claude/settings.json.
#
# Idempotent: the sentinel (~/.bitwize-music/.setup-complete) records
# the sha256 of requirements.txt at install time, so subsequent runs
# exit immediately when the manifest is unchanged but re-provision
# automatically after a plugin update. The install runs detached so
# session start is never blocked. Progress goes to
# ~/.bitwize-music/setup.log.
#
# Concurrency is guarded by an OS-level flock on ~/.bitwize-music/setup.lock.
# The lock is held by the open file descriptor (FD 9) inherited into the
# background worker; when the worker exits — for any reason, including
# SIGKILL — the kernel releases the lock. No PID files, no stale-lock
# windows.

set -u

STATE_DIR="${HOME}/.bitwize-music"
VENV_DIR="${STATE_DIR}/venv"
SENTINEL="${STATE_DIR}/.setup-complete"
LOG_FILE="${STATE_DIR}/setup.log"
LOCK_FILE="${STATE_DIR}/setup.lock"
KNOWN_MARKETPLACES="${HOME}/.claude/plugins/known_marketplaces.json"
DEFAULT_PLUGIN_DIR="${HOME}/.claude/plugins/marketplaces/bitwize-music"

# Locate the plugin on disk. Prefer the installLocation Claude recorded
# in known_marketplaces.json so this keeps working if the marketplace is
# keyed under a different alias or moved to a versioned cache directory.
# Falls back to the default marketplaces path.
resolve_plugin_dir() {
    if [[ -f "${KNOWN_MARKETPLACES}" ]] && command -v python3 >/dev/null 2>&1; then
        local loc
        loc="$(python3 - "${KNOWN_MARKETPLACES}" <<'PY' 2>/dev/null
import json, os, sys
try:
    data = json.load(open(sys.argv[1]))
except Exception:
    sys.exit(0)
candidates = []
if isinstance(data, dict):
    # Prefer an entry whose source repo matches the plugin.
    for entry in data.values():
        if not isinstance(entry, dict):
            continue
        loc = entry.get("installLocation")
        repo = (entry.get("source") or {}).get("repo", "")
        if loc and os.path.isfile(os.path.join(loc, "requirements.txt")):
            score = 1 if "claude-ai-music-skills" in repo else 0
            candidates.append((score, loc))
candidates.sort(reverse=True)
if candidates:
    print(candidates[0][1])
PY
        )"
        if [[ -n "${loc}" ]]; then
            echo "${loc}"
            return 0
        fi
    fi
    echo "${DEFAULT_PLUGIN_DIR}"
}

PLUGIN_DIR="$(resolve_plugin_dir)"
REQUIREMENTS="${PLUGIN_DIR}/requirements.txt"

# Plugin not on disk yet (e.g. running outside Claude Code) → nothing to do.
if [[ ! -f "${REQUIREMENTS}" ]]; then
    exit 0
fi

CURRENT_HASH="$(sha256sum "${REQUIREMENTS}" 2>/dev/null | awk '{print $1}')"

# Fast path: sentinel records the same hash → already provisioned for
# this requirements.txt. A plugin update changes the hash and forces
# re-provision automatically.
if [[ -n "${CURRENT_HASH}" && -f "${SENTINEL}" && -x "${VENV_DIR}/bin/python3" ]]; then
    if [[ "$(cat "${SENTINEL}" 2>/dev/null)" == "${CURRENT_HASH}" ]]; then
        exit 0
    fi
fi

mkdir -p "${STATE_DIR}"

# Open the lock file and acquire an exclusive non-blocking flock on FD 9.
# A held lock means another invocation's worker is still running.
exec 9>"${LOCK_FILE}"
if ! flock -n 9; then
    echo "[bitwize-music] setup already running; see ${LOG_FILE}"
    exit 0
fi

echo "[bitwize-music] starting MCP server setup in background"
echo "[bitwize-music] progress: tail -f ${LOG_FILE}"

# Spawn the heavy work detached. FD 9 (with the flock) is inherited into
# the subshell, so the kernel keeps the lock held until the worker exits.
# When the parent process exits its FD 9 also closes, but the worker's
# inherited descriptor keeps the lock alive — and when the worker dies
# the kernel releases it, no matter how the worker terminates.
(
    {
        echo "=== bitwize-music setup started $(date -Iseconds) ==="
        echo "PLUGIN_DIR=${PLUGIN_DIR}"
        echo "requirements.txt sha256=${CURRENT_HASH}"

        if ! command -v python3 >/dev/null 2>&1; then
            echo "ERROR: python3 not found on PATH"
            exit 1
        fi

        if [[ ! -x "${VENV_DIR}/bin/python3" ]]; then
            echo "Creating venv at ${VENV_DIR}"
            python3 -m venv "${VENV_DIR}" || { echo "ERROR: venv creation failed"; exit 1; }
        fi

        echo "Upgrading pip / wheel / setuptools"
        "${VENV_DIR}/bin/pip" install --upgrade pip wheel setuptools

        echo "Installing requirements from ${REQUIREMENTS}"
        "${VENV_DIR}/bin/pip" install -r "${REQUIREMENTS}" || { echo "ERROR: pip install failed"; exit 1; }

        # Best-effort browser install for document-hunter. Don't fail
        # setup if system libs are missing — the rest of the plugin
        # still works without it.
        echo "Installing playwright chromium (best-effort)"
        "${VENV_DIR}/bin/playwright" install chromium || \
            echo "WARN: playwright install chromium failed (non-fatal)"

        # Write sentinel atomically so a partially-written file is
        # never observed by the fast path.
        tmp="$(mktemp "${SENTINEL}.XXXXXX")"
        echo "${CURRENT_HASH}" > "${tmp}"
        mv -f "${tmp}" "${SENTINEL}"

        echo "=== bitwize-music setup completed $(date -Iseconds) ==="
    } >>"${LOG_FILE}" 2>&1
) </dev/null >/dev/null 2>&1 &
disown

exit 0
