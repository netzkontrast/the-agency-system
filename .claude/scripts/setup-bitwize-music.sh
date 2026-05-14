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
CONFIG_FILE="${STATE_DIR}/config.yaml"
SENTINEL="${STATE_DIR}/.setup-complete"
LOG_FILE="${STATE_DIR}/setup.log"
LOCK_FILE="${STATE_DIR}/setup.lock"
KNOWN_MARKETPLACES="${HOME}/.claude/plugins/known_marketplaces.json"
DEFAULT_PLUGIN_DIR="${HOME}/.claude/plugins/marketplaces/bitwize-music"
# The project the hook fires from. The plugin stores album content
# under ${REPO}/music/ when the config is rendered from the template.
# Self-locate from $BASH_SOURCE: the script lives at
# ${REPO}/.claude/scripts/setup-bitwize-music.sh, so the repo root is
# two directories up. This avoids depending on CLAUDE_PROJECT_DIR or
# the hook's working directory. CLAUDE_PROJECT_DIR still wins when set
# so manual runs from outside the repo keep working.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
REPO="${CLAUDE_PROJECT_DIR:-$(cd "${SCRIPT_DIR}/../.." && pwd -P)}"
CONFIG_TEMPLATE="${REPO:+${REPO}/.claude/bitwize-music.config.template.yaml}"

# Locate the plugin on disk. Prefer the installLocation Claude recorded
# in known_marketplaces.json so this keeps working if the marketplace is
# keyed under a different alias or moved to a versioned cache directory.
# Falls back to the default marketplaces path.
resolve_plugin_dir() {
    if [[ -f "${KNOWN_MARKETPLACES}" ]] && command -v python3 >/dev/null 2>&1; then
        local loc
        # Only accept entries whose source repo or marketplace key
        # identifies the bitwize plugin. Without this guard, a co-installed
        # marketplace with a requirements.txt could win arbitrarily.
        loc="$(python3 - "${KNOWN_MARKETPLACES}" <<'PY' 2>/dev/null
import json, os, sys
try:
    data = json.load(open(sys.argv[1]))
except Exception:
    sys.exit(0)
if not isinstance(data, dict):
    sys.exit(0)
for key, entry in data.items():
    if not isinstance(entry, dict):
        continue
    loc = entry.get("installLocation")
    repo = (entry.get("source") or {}).get("repo", "") or ""
    is_bitwize = (
        "claude-ai-music-skills" in repo
        or "bitwize-music" in repo
        or "bitwize-music" in str(key)
    )
    if is_bitwize and loc and os.path.isfile(os.path.join(loc, "requirements.txt")):
        print(loc)
        break
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

# Hash requirements.txt to detect plugin updates. Falls through three
# implementations so it works on Linux (sha256sum), macOS (shasum), and
# anywhere python3 is available — without which we couldn't create the
# venv anyway.
compute_hash() {
    local file="$1"
    if command -v sha256sum >/dev/null 2>&1; then
        sha256sum "${file}" | awk '{print $1}'
    elif command -v shasum >/dev/null 2>&1; then
        shasum -a 256 "${file}" | awk '{print $1}'
    elif command -v python3 >/dev/null 2>&1; then
        python3 -c "
import hashlib, sys
print(hashlib.sha256(open(sys.argv[1], 'rb').read()).hexdigest())
" "${file}"
    fi
}
CURRENT_HASH="$(compute_hash "${REQUIREMENTS}" 2>/dev/null)"

# Render ~/.bitwize-music/config.yaml from the repo's template on first
# run, so album content writes into this repo (content_root = ${REPO})
# rather than $HOME. Existing configs (including ones produced by
# /bitwize-music:configure) are left alone unless the recorded
# content_root no longer matches the current repo — in that case the
# template re-renders so the config tracks the repo's actual location.
# Also creates the audio/ documents/ overrides/ subtrees if missing.
bootstrap_config() {
    [[ -z "${REPO}" ]] && return 0
    [[ -z "${CONFIG_TEMPLATE}" || ! -f "${CONFIG_TEMPLATE}" ]] && return 0

    # python3 drives both the drift probe and the renderer. Without it
    # we can't safely do either — skip the whole bootstrap rather than
    # let a redirection write an empty file over a working config.
    if ! command -v python3 >/dev/null 2>&1; then
        echo "[bitwize-music] WARN: python3 not on PATH; skipping config render" >&2
        return 0
    fi

    mkdir -p "${REPO}/audio" "${REPO}/documents" "${REPO}/overrides"

    if [[ -f "${CONFIG_FILE}" ]]; then
        # Re-render only when the recorded content_root doesn't point at
        # this repo, so a customised config keeps working on the same
        # machine but stops drifting after a clone/checkout to a new path.
        # Pass the repo path through Python so regex metacharacters in
        # the path (.,+,(,[,&,\, …) can't make the check mis-match.
        if REPO="${REPO}" python3 -c '
import os, re, sys
repo = os.environ["REPO"]
pattern = re.compile(r"^[ \t]*content_root:[ \t]*" + re.escape(repo) + r"(\s|$)", re.MULTILINE)
sys.exit(0 if pattern.search(open(sys.argv[1]).read()) else 1)
' "${CONFIG_FILE}"; then
            return 0
        fi
    fi

    mkdir -p "${STATE_DIR}"
    local tmp
    tmp="$(mktemp "${CONFIG_FILE}.XXXXXX")"
    # Render the template by literal string replacement (str.replace, not
    # regex) so characters in the repo path that are special to sed
    # replacements — backslash, ampersand, or the delimiter — can't
    # corrupt the rendered config. Only promote the temp file when the
    # renderer actually succeeded, so a failed python3 call can never
    # leave an empty config in place.
    if REPO="${REPO}" python3 -c '
import os, sys
sys.stdout.write(open(sys.argv[1]).read().replace("${REPO}", os.environ["REPO"]))
' "${CONFIG_TEMPLATE}" > "${tmp}"; then
        mv -f "${tmp}" "${CONFIG_FILE}"
    else
        rm -f "${tmp}"
        echo "[bitwize-music] WARN: failed to render config template; existing ${CONFIG_FILE} (if any) left untouched" >&2
        return 0
    fi
}
bootstrap_config

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
# A held lock means another invocation's worker is still running. If
# `flock` is unavailable (e.g. macOS without util-linux), fall back to a
# best-effort mkdir-based lock: it's not race-proof against very fast
# concurrent SessionStart events, but it's the right behaviour when the
# alternative is "silently never provision". Without any lock at all the
# worst case is two pip installs that step on each other — annoying but
# self-healing on the next session.
LOCK_KIND=""
if command -v flock >/dev/null 2>&1; then
    # Open the lock file first so we can distinguish "couldn't open the
    # lock file" (I/O / permission error) from "another worker holds
    # the lock" (real contention). With set -u alone a failed redirect
    # in `exec` doesn't abort the script, so guard it explicitly.
    if ! exec 9>"${LOCK_FILE}" 2>/dev/null; then
        echo "[bitwize-music] ERROR: cannot open lock file ${LOCK_FILE}" >&2
        exit 1
    fi
    flock -n 9
    flock_rc=$?
    case "${flock_rc}" in
        0)
            LOCK_KIND="flock"
            ;;
        1)
            # Standard flock contention: another worker holds the lock.
            echo "[bitwize-music] setup already running; see ${LOG_FILE}"
            exit 0
            ;;
        *)
            echo "[bitwize-music] ERROR: flock failed (rc=${flock_rc}); see ${LOG_FILE} for details" >&2
            exit 1
            ;;
    esac
else
    # Note: cleanup of the lock directory lives only in the background
    # worker below — never in the parent, since the parent exits as soon
    # as it spawns the worker.
    if mkdir "${LOCK_FILE}.d" 2>/dev/null; then
        LOCK_KIND="mkdir"
    else
        # Owner check: if the recorded pid is alive, bail; otherwise evict.
        owner_pid="$(cat "${LOCK_FILE}.d/pid" 2>/dev/null || true)"
        if [[ -n "${owner_pid}" ]] && kill -0 "${owner_pid}" 2>/dev/null; then
            echo "[bitwize-music] setup already running (pid ${owner_pid}); see ${LOG_FILE}"
            exit 0
        fi
        rm -rf "${LOCK_FILE}.d" 2>/dev/null || true
        if mkdir "${LOCK_FILE}.d" 2>/dev/null; then
            LOCK_KIND="mkdir"
        else
            # Another process won the eviction race; let them run.
            echo "[bitwize-music] setup already running; see ${LOG_FILE}"
            exit 0
        fi
    fi
fi

echo "[bitwize-music] starting MCP server setup in background"
echo "[bitwize-music] progress: tail -f ${LOG_FILE}"

# Spawn the heavy work detached. With flock, FD 9 (and its kernel lock)
# is inherited into the subshell, so the lock survives until the worker
# exits — even on SIGKILL. With the mkdir fallback, the worker records
# its own PID for liveness checks and removes the lock dir on exit.
(
    if [[ "${LOCK_KIND}" == "mkdir" ]]; then
        echo "$BASHPID" > "${LOCK_FILE}.d/pid"
        trap 'rm -rf "${LOCK_FILE}.d"' EXIT
    fi
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
