#!/usr/bin/env bash
# Setup script for the bitwize-music plugin MCP server.
#
# Creates ~/.bitwize-music/venv and installs the plugin's Python
# dependencies so the `bitwize-music-mcp` MCP server can start. Designed
# to be invoked from the SessionStart hook in .claude/settings.json.
#
# Idempotent: a sentinel file (~/.bitwize-music/.setup-complete) is
# written once install succeeds, so subsequent runs exit immediately.
# The heavy install is spawned detached in the background on first run
# so it never blocks session start. Progress is logged to
# ~/.bitwize-music/setup.log.

set -u

PLUGIN_DIR="${HOME}/.claude/plugins/marketplaces/bitwize-music"
VENV_DIR="${HOME}/.bitwize-music/venv"
SENTINEL="${HOME}/.bitwize-music/.setup-complete"
LOG_FILE="${HOME}/.bitwize-music/setup.log"
LOCK_FILE="${HOME}/.bitwize-music/setup.lock"

# Fast path: already installed.
if [[ -f "${SENTINEL}" && -x "${VENV_DIR}/bin/python3" ]]; then
    exit 0
fi

# Plugin not on disk (e.g. running outside Claude Code) → nothing to do.
if [[ ! -d "${PLUGIN_DIR}" ]]; then
    exit 0
fi

mkdir -p "${HOME}/.bitwize-music"

# Acquire lock atomically (parent process) before spawning background work.
# noclobber makes the redirect fail if the file already exists.
if ! ( set -o noclobber; echo "pending $$" > "${LOCK_FILE}" ) 2>/dev/null; then
    # Lock exists — check if the recorded PID is still alive.
    pid="$(awk '{print $2}' "${LOCK_FILE}" 2>/dev/null || true)"
    if [[ -n "${pid}" ]] && kill -0 "${pid}" 2>/dev/null; then
        echo "[bitwize-music] setup already running (pid ${pid}); see ${LOG_FILE}"
        exit 0
    fi
    # Stale lock — replace it.
    echo "pending $$" > "${LOCK_FILE}"
fi

echo "[bitwize-music] starting one-time MCP server setup in background"
echo "[bitwize-music] progress: tail -f ${LOG_FILE}"

# Spawn the heavy work detached so session start is not blocked.
(
    echo "running $BASHPID" > "${LOCK_FILE}"
    {
        echo "=== bitwize-music setup started $(date -Iseconds) ==="

        if ! command -v python3 >/dev/null 2>&1; then
            echo "ERROR: python3 not found on PATH"
            rm -f "${LOCK_FILE}"
            exit 1
        fi

        if [[ ! -x "${VENV_DIR}/bin/python3" ]]; then
            echo "Creating venv at ${VENV_DIR}"
            python3 -m venv "${VENV_DIR}" || {
                echo "ERROR: failed to create venv"
                rm -f "${LOCK_FILE}"
                exit 1
            }
        fi

        echo "Upgrading pip"
        "${VENV_DIR}/bin/pip" install --upgrade pip wheel setuptools

        echo "Installing requirements from ${PLUGIN_DIR}/requirements.txt"
        "${VENV_DIR}/bin/pip" install -r "${PLUGIN_DIR}/requirements.txt" || {
            echo "ERROR: pip install failed; see log above"
            rm -f "${LOCK_FILE}"
            exit 1
        }

        # Optional: chromium for document-hunter. Don't fail setup if
        # this step fails (system libs may be missing); the rest of the
        # plugin still works.
        echo "Installing playwright chromium (best-effort)"
        "${VENV_DIR}/bin/playwright" install chromium || \
            echo "WARN: playwright install chromium failed (non-fatal)"

        touch "${SENTINEL}"
        echo "=== bitwize-music setup completed $(date -Iseconds) ==="
        rm -f "${LOCK_FILE}"
    } >>"${LOG_FILE}" 2>&1
) </dev/null >/dev/null 2>&1 &
disown

exit 0
