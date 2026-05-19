#!/usr/bin/env bash
# =============================================================================
# Universal Claude Code Web environment installer.
#
# Configurable at the top: list any number of plugin sources (GitHub repos,
# Git URLs, or local paths). The script registers each as a marketplace,
# auto-discovers the plugins they define, installs them, auto-registers
# the MCP servers their `.mcp.json` declares, and provisions Python
# dependencies it finds (`requirements.txt` at plugin root, or
# `pyproject.toml` files under `servers/*/`).
#
# Idempotent. Safe to re-run. Designed for Anthropic's cloud containers,
# but works on any Linux box with apt-get + python3 + the `claude` CLI.
#
# Paste into Claude Code's "Environment setup" bash field, or invoke
# directly with `bash tools/environment.sh`.
# =============================================================================
set -euo pipefail

# =============================================================================
# CONFIGURATION — edit these arrays to change what gets installed.
# =============================================================================

# Plugin sources. Each entry becomes a marketplace.
#
# Source forms (per `claude plugin marketplace add`):
#   - GitHub shorthand:  "owner/repo"
#   - Git URL:           "https://host/path.git" or "git@host:path.git"
#   - Local directory:   absolute path, or path relative to REPO_PATH
#                        (e.g. "." installs the current repo as a plugin)
#
# Optional filter: append `|plugin1,plugin2` to install only specific
# plugins from that marketplace's marketplace.json. Omit the suffix to
# install every plugin the marketplace declares.
PLUGIN_SOURCES=(
    # bitwize-music studio plugin (music creation skills + MCP)
    "bitwize-music-studio/claude-ai-music-skills"

    # obra/superpowers marketplace — install ONLY the superpowers plugin
    # (deliberately skipping private-journal-mcp).
    "obra/superpowers-marketplace|superpowers"

    # The local repo itself, installed as a plugin from its marketplace.json.
    # Registers the `agency-marketplace` and installs `agency-system`,
    # which auto-loads the agency-mcp MCP server via the repo's .mcp.json.
    "."
)

# Bitwize-music writes album content under <REPO>/artists/... The artist
# name is just a logical label inside its config.yaml.
ARTIST_NAME="${ARTIST_NAME:-the-agency-system}"

# =============================================================================
# Helpers
# =============================================================================
log()  { printf '[setup] %s\n' "$*"; }
warn() { printf '[setup] WARN: %s\n' "$*" >&2; }
die()  { printf '[setup] ERROR: %s\n' "$*" >&2; exit 1; }

# =============================================================================
# 1. Locate the cloned repo.
# =============================================================================
# Setup runs from $HOME on Claude's cloud containers, not inside the clone.
# CLAUDE_PROJECT_DIR is not injected during environment setup, so we fall
# back through several detection strategies.
detect_repo_path() {
    if [ -n "${CLAUDE_PROJECT_DIR:-}" ] && [ -d "${CLAUDE_PROJECT_DIR}/.git" ]; then
        printf '%s\n' "${CLAUDE_PROJECT_DIR}"; return
    fi
    local top
    top="$(git -C "$(pwd)" rev-parse --show-toplevel 2>/dev/null || true)"
    if [ -n "${top}" ]; then printf '%s\n' "${top}"; return; fi
    local search="${HOME}"
    [ "${HOME}" != "/home/user" ] && [ -d /home/user ] && search="${search} /home/user"
    # shellcheck disable=SC2086
    local found
    found="$(find ${search} -maxdepth 2 -name .git -type d -printf '%h\n' 2>/dev/null | head -1)"
    if [ -n "${found}" ]; then printf '%s\n' "${found}"; return; fi
    pwd
}

REPO_PATH="$(detect_repo_path)"
[ -d "${REPO_PATH}/.git" ] || die "REPO_PATH=${REPO_PATH} is not a git repo. Check the clone path."

REPO_NAME="$(basename "${REPO_PATH}")"
log "HOME=${HOME}  REPO_PATH=${REPO_PATH}  ARTIST=${ARTIST_NAME}"

# =============================================================================
# 2. System packages (apt). Quiet, idempotent.
# =============================================================================
log "installing system packages"
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq \
    git git-lfs python3 python3-venv python3-pip python3-dev \
    ffmpeg libsndfile1 build-essential pkg-config \
    ca-certificates curl jq
git lfs install --skip-repo

# Detect whether system pip refuses to install (PEP 668 on Debian 12+).
PIP_BREAK_FLAG=""
if python3 -m pip install --dry-run pip 2>&1 | grep -q "externally-managed-environment"; then
    PIP_BREAK_FLAG="--break-system-packages"
fi

# =============================================================================
# 3. Source helpers: parse a PLUGIN_SOURCES entry into (source, filter).
# =============================================================================
parse_source() {
    local raw="$1"
    local src filter
    if [[ "${raw}" == *"|"* ]]; then
        src="${raw%%|*}"
        filter="${raw#*|}"
    else
        src="${raw}"
        filter=""
    fi
    printf '%s\t%s\n' "${src}" "${filter}"
}

# Resolve a source string to an installable form. Local paths (".", "./x"
# or "/abs/path") are resolved absolute so `claude` doesn't get confused
# by its own working directory.
resolve_source() {
    local src="$1"
    if [[ "${src}" == /* ]] || [[ "${src}" == "." ]] || [[ "${src}" == ./* ]]; then
        # Local path. Make absolute relative to REPO_PATH.
        (cd "${REPO_PATH}" && cd "${src}" && pwd -P)
    else
        printf '%s\n' "${src}"
    fi
}

# Read marketplace.json for a local source (or accept marketplace name
# inferred later for remote sources via known_marketplaces.json).
read_local_marketplace_name() {
    local path="$1"
    local mp="${path}/.claude-plugin/marketplace.json"
    [ -f "${mp}" ] || return 1
    python3 -c "import json,sys; print(json.load(open('${mp}'))['name'])"
}

# After a marketplace is registered, look up its installed location and
# its declared plugins from known_marketplaces.json.
known_marketplaces_path() {
    local candidates=(
        "${HOME}/.claude/plugins/known_marketplaces.json"
        "/root/.claude/plugins/known_marketplaces.json"
        "/home/user/.claude/plugins/known_marketplaces.json"
    )
    local p
    for p in "${candidates[@]}"; do
        [ -f "${p}" ] && { printf '%s\n' "${p}"; return; }
    done
    return 1
}

list_marketplace_plugins() {
    # Args: marketplace-name. Prints plugin names, one per line.
    local mp_name="$1"
    local km
    km="$(known_marketplaces_path)" || return 1
    python3 - "${km}" "${mp_name}" <<'PY'
import json, sys
km_path, mp_name = sys.argv[1], sys.argv[2]
with open(km_path) as f:
    data = json.load(f)
entry = data.get(mp_name)
if not entry:
    sys.exit(0)
loc = entry.get("installLocation")
if not loc:
    sys.exit(0)
import os
mp = os.path.join(loc, ".claude-plugin", "marketplace.json")
if not os.path.isfile(mp):
    sys.exit(0)
with open(mp) as f:
    mpdata = json.load(f)
for p in mpdata.get("plugins", []):
    name = p.get("name")
    if name:
        print(name)
PY
}

marketplace_install_location() {
    local mp_name="$1"
    local km
    km="$(known_marketplaces_path)" || return 1
    python3 -c "
import json, sys
data = json.load(open('${km}'))
entry = data.get('${mp_name}')
print(entry['installLocation'] if entry else '')
" 2>/dev/null
}

# Check whether a plugin is already installed for the user scope.
plugin_already_installed() {
    local plugin_ref="$1"   # name@marketplace
    if claude plugin list --json 2>/dev/null \
        | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(1)
ref = '${plugin_ref}'
name, _, mp = ref.partition('@')
items = data if isinstance(data, list) else data.get('plugins', [])
for it in items:
    if it.get('name') == name and (not mp or it.get('marketplace') == mp):
        sys.exit(0)
sys.exit(1)
" 2>/dev/null; then
        return 0
    fi
    return 1
}

# =============================================================================
# 4. Register marketplaces and install plugins.
# =============================================================================
# Tracks marketplace-name → install-location pairs we've handled, so we
# can run plugin-specific provisioning (Python deps, config) afterwards.
INSTALLED_MARKETPLACES=()
INSTALLED_PLUGINS=()

register_and_install() {
    local raw="$1"
    local parsed src filter
    parsed="$(parse_source "${raw}")"
    src="$(printf '%s' "${parsed}" | cut -f1)"
    filter="$(printf '%s' "${parsed}" | cut -f2)"

    local resolved
    resolved="$(resolve_source "${src}")"
    log "registering marketplace from: ${resolved}${filter:+ (filter: ${filter})}"

    # Register marketplace (idempotent — `claude` returns non-zero if
    # already known, which we treat as success).
    claude plugin marketplace add "${resolved}" 2>&1 \
        | sed 's/^/[setup]   /' \
        || log "  marketplace already registered or non-fatal warning"

    # Determine the marketplace's logical name.
    local mp_name=""
    if [ -d "${resolved}" ]; then
        mp_name="$(read_local_marketplace_name "${resolved}" || true)"
    fi
    # Fall back: probe known_marketplaces.json by install location.
    if [ -z "${mp_name}" ]; then
        local km
        km="$(known_marketplaces_path)" || return 0
        mp_name="$(python3 - "${km}" "${resolved}" "${src}" <<'PY' 2>/dev/null
import json, sys
km, resolved, src = sys.argv[1], sys.argv[2], sys.argv[3]
with open(km) as f:
    data = json.load(f)
# Try to match by source repo or install location
for name, entry in data.items():
    srcobj = entry.get("source") or {}
    repo = srcobj.get("repo", "")
    if repo == src or entry.get("installLocation") == resolved:
        print(name); break
    # Last segment fallback (e.g. obra/superpowers-marketplace → name often equals repo basename)
    if src and src.endswith(name):
        print(name); break
PY
)"
    fi
    [ -n "${mp_name}" ] || { warn "could not resolve marketplace name for ${src} — skipping plugin install"; return 0; }

    log "  marketplace name: ${mp_name}"

    # Determine which plugins to install: either the explicit filter list,
    # or all plugins declared in the marketplace.json.
    local plugins_to_install=()
    if [ -n "${filter}" ]; then
        IFS=',' read -r -a plugins_to_install <<<"${filter}"
    else
        mapfile -t plugins_to_install < <(list_marketplace_plugins "${mp_name}" || true)
    fi
    if [ "${#plugins_to_install[@]}" -eq 0 ]; then
        warn "  no plugins discovered for marketplace ${mp_name}"
        return 0
    fi

    local p ref
    for p in "${plugins_to_install[@]}"; do
        p="${p// /}"   # trim whitespace
        [ -z "${p}" ] && continue
        ref="${p}@${mp_name}"
        if plugin_already_installed "${ref}"; then
            log "  plugin ${ref} already installed"
        else
            log "  installing plugin ${ref}"
            claude plugin install "${ref}" -s user 2>&1 \
                | sed 's/^/[setup]     /' \
                || warn "    plugin install reported non-zero (may be already installed)"
        fi
        INSTALLED_PLUGINS+=("${ref}")
    done

    INSTALLED_MARKETPLACES+=("${mp_name}")
}

for entry in "${PLUGIN_SOURCES[@]}"; do
    register_and_install "${entry}"
done

# =============================================================================
# 5. Provision Python dependencies for installed plugins.
#
# Two conventions are auto-detected, in order:
#   a) <plugin>/requirements.txt        → installed into a per-plugin venv
#      at ${HOME}/.<plugin>/venv and a sentinel is written. This matches
#      the bitwize-music convention.
#   b) <plugin>/servers/*/pyproject.toml → installed editably into the
#      SYSTEM python (`pip3 install -e .`), because the corresponding
#      .mcp.json typically uses bare `python`/`python3` as the command,
#      which Claude Code resolves via PATH.
# =============================================================================

# State dir for bitwize-music (referenced by its SessionStart hook).
BITWIZE_STATE_DIR="${HOME}/.bitwize-music"
mkdir -p "${BITWIZE_STATE_DIR}"

install_plugin_python_deps() {
    local mp_name="$1"
    local plugin_dir
    plugin_dir="$(marketplace_install_location "${mp_name}")"
    [ -n "${plugin_dir}" ] && [ -d "${plugin_dir}" ] || return 0

    # Walk every plugin in this marketplace and provision its deps.
    local pjson="${plugin_dir}/.claude-plugin/marketplace.json"
    if [ ! -f "${pjson}" ]; then
        return 0
    fi
    local plugin_paths
    plugin_paths="$(python3 - "${plugin_dir}" "${pjson}" <<'PY' 2>/dev/null
import json, os, sys
plugin_dir, mp_path = sys.argv[1], sys.argv[2]
with open(mp_path) as f:
    mp = json.load(f)
for entry in mp.get("plugins", []):
    source = entry.get("source", "./")
    name = entry.get("name", "unknown")
    path = os.path.normpath(os.path.join(plugin_dir, source))
    print(f"{name}\t{path}")
PY
)"

    while IFS=$'\t' read -r pname ppath; do
        [ -n "${ppath}" ] && [ -d "${ppath}" ] || continue

        # (a) Plugin-root requirements.txt → per-plugin venv.
        if [ -f "${ppath}/requirements.txt" ]; then
            local state_dir="${HOME}/.${pname}"
            local venv="${state_dir}/venv"
            mkdir -p "${state_dir}"
            if [ ! -x "${venv}/bin/python3" ]; then
                log "creating venv ${venv}"
                python3 -m venv "${venv}"
            fi
            log "installing ${pname} requirements into ${venv}"
            "${venv}/bin/pip" install --quiet --upgrade pip wheel setuptools
            "${venv}/bin/pip" install --quiet -r "${ppath}/requirements.txt" \
                || warn "  pip install failed for ${pname}"
            # Optional playwright bootstrap (bitwize-music convention).
            if [ -x "${venv}/bin/playwright" ]; then
                "${venv}/bin/playwright" install chromium >/dev/null 2>&1 \
                    || warn "  playwright chromium install failed (non-fatal)"
            fi
            # Sentinel for SessionStart fast-paths.
            python3 -c "
import hashlib
print(hashlib.sha256(open('${ppath}/requirements.txt','rb').read()).hexdigest())
" > "${state_dir}/.setup-complete"
        fi

        # (b) MCP-server subprojects with pyproject.toml → system Python
        # editable install. Common pattern in this repo: servers/<name>/.
        if [ -d "${ppath}/servers" ]; then
            local server
            for server in "${ppath}/servers"/*/; do
                [ -f "${server}/pyproject.toml" ] || continue
                log "installing MCP server deps from ${server} into system python"
                python3 -m pip install --quiet ${PIP_BREAK_FLAG} -e "${server}" \
                    || warn "  editable install failed for ${server}"
            done
        fi
    done <<<"${plugin_paths}"
}

# De-duplicate marketplaces before walking deps.
uniq_marketplaces=()
seen=""
for mp in "${INSTALLED_MARKETPLACES[@]}"; do
    case "${seen}" in *"|${mp}|"*) continue;; esac
    seen="${seen}|${mp}|"
    uniq_marketplaces+=("${mp}")
done

for mp in "${uniq_marketplaces[@]}"; do
    install_plugin_python_deps "${mp}"
done

# =============================================================================
# 6. Plugin-specific config files.
#
# bitwize-music expects ${HOME}/.bitwize-music/config.yaml. We always
# regenerate it so the paths match the currently-cloned repo (which is
# never guaranteed to be /home/user/the-agency-system).
# =============================================================================
BITWIZE_CONFIG="${BITWIZE_STATE_DIR}/config.yaml"
if printf '%s\n' "${INSTALLED_PLUGINS[@]}" | grep -q "^bitwize-music@"; then
    log "writing ${BITWIZE_CONFIG}"
    tmp="$(mktemp "${BITWIZE_CONFIG}.XXXXXX")"
    cat >"${tmp}" <<YAML
artist:
  name: ${ARTIST_NAME}
paths:
  content_root: ${REPO_PATH}
  audio_root: ${REPO_PATH}/audio
  documents_root: ${REPO_PATH}/documents
  overrides: ${REPO_PATH}/overrides
  ideas_file: ${REPO_PATH}/IDEAS.md
generation:
  service: suno
  require_suno_link_for_final: true
  max_lyric_words: 800
database:
  enabled: false
YAML
    mv -f "${tmp}" "${BITWIZE_CONFIG}"
fi

# =============================================================================
# 7. Done.
# =============================================================================
log "DONE — verify with: claude plugin list && claude mcp list"
log "  REPO_PATH=${REPO_PATH}"
log "  Installed plugins:"
for p in "${INSTALLED_PLUGINS[@]}"; do
    log "    - ${p}"
done
