#!/usr/bin/env bash
# Cloud-container environment setup for the-agency-system.
#
# Paste this into Claude Code's "Environment setup" bash field. It runs
# once when the cloud container is provisioned, before Claude Code
# clones the repo into /home/user/the-agency-system. After this script
# finishes and the repo is checked out, the bitwize-music plugin's 50+
# /bitwize-music:* slash commands and the bitwize-music-mcp MCP
# server's 89 tools are live the moment a session starts.
#
# Approach: use the official `claude plugin` CLI to add the marketplace
# and install the plugin at user scope — that single install registers
# the plugin's own .mcp.json so the bitwize-music-mcp MCP server is
# discovered automatically (no manual `claude mcp add-json` needed).
# This script only has to provision the Python venv the MCP server
# expects and the inlined ~/.bitwize-music/config.yaml.
#
# Repo-side steps (LFS pull, content subtree creation) belong in the
# repo's SessionStart hook, since the repo does not exist yet when this
# script runs. The config.yaml is inlined here for the same reason —
# the template in the repo is unreachable at env-setup time.
#
# In this container Claude Code runs as root, so $HOME=/root is the
# correct target for plugin and venv state. If you ever switch the
# cloud image to run sessions as a non-root user, run this script as
# that user (or set HOME explicitly) so state lands in their home.
#
# Hard-coded for /home/user/the-agency-system. Idempotent — safe to
# re-run after plugin updates.

set -euo pipefail

STATE_DIR="${HOME}/.bitwize-music"
VENV_DIR="${STATE_DIR}/venv"
CONFIG_FILE="${STATE_DIR}/config.yaml"
SENTINEL="${STATE_DIR}/.setup-complete"
MARKETPLACE_SOURCE="bitwize-music-studio/claude-ai-music-skills"
PLUGIN_REF="bitwize-music@bitwize-music"

log() { printf '[setup] %s\n' "$*"; }

# ---- 1. System packages ----------------------------------------------------
# librosa/matchering need libsndfile; the document/audio workflows
# expect ffmpeg; LFS is installed system-wide so the cloud's repo
# checkout (which happens after this script) fetches LFS objects.
log "installing system packages"
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq \
    git git-lfs \
    python3 python3-venv python3-pip \
    ffmpeg libsndfile1 \
    ca-certificates curl jq
git lfs install --skip-repo

# ---- 2. Marketplace + plugin install via the official CLI -----------------
# `claude plugin marketplace add` clones the marketplace into
# ~/.claude/plugins/marketplaces/. `claude plugin install` copies the
# plugin into the versioned cache, marks it enabled in user-scope
# state, AND reads the plugin's .mcp.json so bitwize-music-mcp is
# auto-discovered by `claude mcp list`.
log "registering marketplace + installing plugin"
claude plugin marketplace add "${MARKETPLACE_SOURCE}"
claude plugin install "${PLUGIN_REF}" -s user

# Resolve the marketplace path the CLI cloned to so we can pip-install
# from its requirements.txt.
PLUGIN_DIR="$(python3 -c "
import json, os, sys
p = os.path.expanduser('~/.claude/plugins/known_marketplaces.json')
try:
    print(json.load(open(p))['bitwize-music']['installLocation'])
except Exception as e:
    sys.exit(f'cannot resolve plugin install location: {e}')
")"
REQUIREMENTS="${PLUGIN_DIR}/requirements.txt"

# ---- 3. Python venv + plugin dependencies ---------------------------------
# The plugin's .mcp.json launches the MCP server with
# ${HOME}/.bitwize-music/venv/bin/python3, so the venv must exist at
# exactly that path with the plugin's dependencies installed.
mkdir -p "${STATE_DIR}"
[ -x "${VENV_DIR}/bin/python3" ] || {
    log "creating venv at ${VENV_DIR}"
    python3 -m venv "${VENV_DIR}"
}
log "installing Python dependencies"
"${VENV_DIR}/bin/pip" install --quiet --upgrade pip wheel setuptools
"${VENV_DIR}/bin/pip" install --quiet -r "${REQUIREMENTS}"

# Playwright browser used by document-hunter. Non-fatal if it fails
# (e.g. missing system libs) — the rest of the plugin still works.
log "installing playwright chromium (best-effort)"
"${VENV_DIR}/bin/playwright" install chromium \
    || log "WARN: playwright chromium install failed (non-fatal)"

# ---- 4. Inlined ~/.bitwize-music/config.yaml ------------------------------
# Preserve any existing file so a re-run doesn't blow away edits or
# `/bitwize-music:configure` output. Write through a temp file so a
# transient failure can't truncate a working config.
if [ ! -f "${CONFIG_FILE}" ]; then
    log "writing ${CONFIG_FILE}"
    tmp="$(mktemp "${CONFIG_FILE}.XXXXXX")"
    cat >"${tmp}" <<'YAML'
# bitwize-music configuration for the-agency-system.
# Inlined by cloud-environment-setup.sh. To change settings, run
# /bitwize-music:configure inside Claude Code, or edit this file
# directly. Re-running the env-setup script leaves this file untouched.

artist:
  name: the-agency-system

paths:
  # content_root is the repo root, so the plugin writes albums to
  # /home/user/the-agency-system/artists/<artist>/albums/<genre>/<slug>/.
  # Audio, documents, and overrides live in named subdirectories.
  content_root: /home/user/the-agency-system
  audio_root: /home/user/the-agency-system/audio
  documents_root: /home/user/the-agency-system/documents
  overrides: /home/user/the-agency-system/overrides
  ideas_file: /home/user/the-agency-system/IDEAS.md

generation:
  service: suno
  require_suno_link_for_final: true
  max_lyric_words: 800

database:
  enabled: false
YAML
    mv -f "${tmp}" "${CONFIG_FILE}"
else
    log "${CONFIG_FILE} already exists — leaving in place"
fi

# ---- 5. SessionStart sentinel ---------------------------------------------
# The repo's SessionStart hook fast-paths (skips pip install) when this
# file holds the current requirements.txt sha256.
python3 -c "
import hashlib
print(hashlib.sha256(open('${REQUIREMENTS}', 'rb').read()).hexdigest())
" > "${SENTINEL}"

log "DONE"
log "  marketplace: ${PLUGIN_DIR}"
log "  venv:        ${VENV_DIR}"
log "  config:      ${CONFIG_FILE}"
log ""
log "Verify with:"
log "  claude plugin list"
log "  claude mcp list"
