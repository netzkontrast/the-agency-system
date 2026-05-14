#!/usr/bin/env bash
# Cloud-container environment setup for the-agency-system.
#
# Paste this into Claude Code's "Environment setup" bash field. It runs
# once when the cloud container is provisioned, before any Claude Code
# session starts, and leaves the bitwize-music plugin + its
# bitwize-music-mcp MCP server fully wired up so the 50+
# /bitwize-music:* slash commands and 89 MCP tools are live on session
# start.
#
# Hard-coded for /home/user/the-agency-system. Idempotent — safe to
# re-run after updates.

set -euo pipefail

REPO_DIR="/home/user/the-agency-system"
STATE_DIR="${HOME}/.bitwize-music"
VENV_DIR="${STATE_DIR}/venv"
PLUGINS_DIR="${HOME}/.claude/plugins"
PLUGIN_DIR="${PLUGINS_DIR}/marketplaces/bitwize-music"
PLUGIN_REPO="https://github.com/bitwize-music-studio/claude-ai-music-skills.git"
MCP_SERVER_ENTRY="${PLUGIN_DIR}/servers/bitwize-music-server/run.py"

log() { printf '[setup] %s\n' "$*"; }

# ---- 1. System packages ----------------------------------------------------
# librosa/matchering need libsndfile; the document/audio workflows
# expect ffmpeg; LFS is required for audio/ and documents/.
log "installing system packages"
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq \
    git git-lfs \
    python3 python3-venv python3-pip \
    ffmpeg libsndfile1 \
    ca-certificates curl jq

# ---- 2. git-lfs ------------------------------------------------------------
git lfs install --skip-repo
if [ -d "${REPO_DIR}/.git" ]; then
    log "pulling LFS objects in ${REPO_DIR}"
    git -C "${REPO_DIR}" lfs install --local
    git -C "${REPO_DIR}" lfs pull || true
fi

# ---- 3. Clone / refresh the plugin marketplace -----------------------------
mkdir -p "${PLUGINS_DIR}/marketplaces"
if [ ! -d "${PLUGIN_DIR}/.git" ]; then
    log "cloning bitwize-music plugin"
    git clone --depth 1 "${PLUGIN_REPO}" "${PLUGIN_DIR}"
else
    log "refreshing bitwize-music plugin"
    git -C "${PLUGIN_DIR}" pull --ff-only || true
fi

# ---- 4. Register the plugin as known + installed + enabled at user scope --
# This makes Claude Code load the plugin's skills (the /bitwize-music:*
# slash commands) on session start.
log "registering plugin in user-level Claude Code state"
PLUGIN_DIR="${PLUGIN_DIR}" python3 <<'PY'
import json, os, datetime

home       = os.path.expanduser("~")
plugin_dir = os.environ["PLUGIN_DIR"]
ts         = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")

def load(path, default):
    try:
        return json.load(open(path)) if os.path.exists(path) else default
    except Exception:
        return default

def dump(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(data, open(path, "w"), indent=2)

# known_marketplaces.json
km_path = f"{home}/.claude/plugins/known_marketplaces.json"
km = load(km_path, {})
if not isinstance(km, dict):
    km = {}
km["bitwize-music"] = {
    "source": {"source": "github",
               "repo":   "bitwize-music-studio/claude-ai-music-skills"},
    "installLocation": plugin_dir,
    "lastUpdated":     ts,
}
dump(km_path, km)

# installed_plugins.json
ip_path = f"{home}/.claude/plugins/installed_plugins.json"
ip = load(ip_path, {"version": 2, "plugins": {}})
if not isinstance(ip, dict):
    ip = {"version": 2, "plugins": {}}
ip.setdefault("version", 2)
plugins = ip.setdefault("plugins", {})
if not isinstance(plugins, dict):
    plugins = ip["plugins"] = {}
plugins["bitwize-music@bitwize-music"] = {
    "marketplace":     "bitwize-music",
    "name":            "bitwize-music",
    "installLocation": plugin_dir,
}
dump(ip_path, ip)

# User-level settings.json — extra belt for the cloud session loader.
st_path = f"{home}/.claude/settings.json"
st = load(st_path, {})
if not isinstance(st, dict):
    st = {}
st.setdefault("extraKnownMarketplaces", {})["bitwize-music"] = {
    "source": {"source": "github",
               "repo":   "bitwize-music-studio/claude-ai-music-skills"},
}
st.setdefault("enabledPlugins", {})["bitwize-music@bitwize-music"] = True
dump(st_path, st)
PY

# ---- 5. Provision the Python venv + install plugin dependencies -----------
mkdir -p "${STATE_DIR}"
if [ ! -x "${VENV_DIR}/bin/python3" ]; then
    log "creating venv at ${VENV_DIR}"
    python3 -m venv "${VENV_DIR}"
fi
log "installing Python dependencies"
"${VENV_DIR}/bin/pip" install --quiet --upgrade pip wheel setuptools
"${VENV_DIR}/bin/pip" install --quiet -r "${PLUGIN_DIR}/requirements.txt"

# Playwright browser used by document-hunter. Non-fatal if it fails
# (e.g. missing system libs) — the rest of the plugin still works.
log "installing playwright chromium (best-effort)"
"${VENV_DIR}/bin/playwright" install chromium \
    || log "WARN: playwright chromium install failed (non-fatal)"

# ---- 6. Render ~/.bitwize-music/config.yaml -------------------------------
# Substitute the ${REPO} placeholder in the template with this repo's
# absolute path. Literal string replace (not sed) so path characters
# can't corrupt the rendered config.
CONFIG_TEMPLATE="${REPO_DIR}/.claude/bitwize-music.config.template.yaml"
CONFIG_FILE="${STATE_DIR}/config.yaml"
if [ -f "${CONFIG_TEMPLATE}" ]; then
    log "rendering ${CONFIG_FILE}"
    REPO="${REPO_DIR}" python3 -c '
import os, sys
sys.stdout.write(open(sys.argv[1]).read().replace("${REPO}", os.environ["REPO"]))
' "${CONFIG_TEMPLATE}" > "${CONFIG_FILE}"
fi

# ---- 7. Record the SessionStart sentinel ----------------------------------
# The repo's SessionStart hook fast-paths when this file holds the
# current requirements.txt sha256, so pip install never re-runs.
python3 -c "
import hashlib
print(hashlib.sha256(open('${PLUGIN_DIR}/requirements.txt', 'rb').read()).hexdigest())
" > "${STATE_DIR}/.setup-complete"

# ---- 8. Ensure repo content subtrees exist --------------------------------
mkdir -p "${REPO_DIR}/audio" "${REPO_DIR}/documents" "${REPO_DIR}/overrides"

# ---- 9. Register bitwize-music-mcp at user scope --------------------------
# Use the claude CLI when available (canonical), fall back to writing
# ~/.claude.json directly.
log "registering bitwize-music-mcp at user scope"
MCP_JSON=$(python3 -c "
import json
print(json.dumps({
    'type':    'stdio',
    'command': '${VENV_DIR}/bin/python3',
    'args':    ['${MCP_SERVER_ENTRY}'],
}))
")

CLAUDE_BIN="$(command -v claude || true)"
if [ -z "${CLAUDE_BIN}" ] && [ -x /opt/node22/bin/claude ]; then
    CLAUDE_BIN=/opt/node22/bin/claude
fi

if [ -n "${CLAUDE_BIN}" ]; then
    "${CLAUDE_BIN}" mcp remove   bitwize-music-mcp -s user 2>/dev/null || true
    "${CLAUDE_BIN}" mcp add-json bitwize-music-mcp -s user "${MCP_JSON}"
else
    log "claude CLI not found; writing ~/.claude.json directly"
    MCP_JSON="${MCP_JSON}" python3 <<'PY'
import json, os
p = os.path.expanduser("~/.claude.json")
data = json.load(open(p)) if os.path.exists(p) else {}
if not isinstance(data, dict):
    data = {}
data.setdefault("mcpServers", {})["bitwize-music-mcp"] = json.loads(
    os.environ["MCP_JSON"]
)
json.dump(data, open(p, "w"), indent=2)
PY
fi

log "DONE"
log "  plugin: ${PLUGIN_DIR}"
log "  venv:   ${VENV_DIR}"
log "  config: ${CONFIG_FILE}"
log "  mcp:    ${VENV_DIR}/bin/python3 ${MCP_SERVER_ENTRY}"
