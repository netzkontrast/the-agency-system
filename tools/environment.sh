#!/usr/bin/env bash
# =============================================================================
# Universal Claude Code Web environment installer (v2).
#
# Paste into Claude Code Web's "Environment setup" bash field on a fresh
# cloud container. Brings the container to a state where every plugin in
# the PLUGINS table below is installed user-scope, every MCP server it
# bundles is reachable, and every runtime dep (Python venvs, system pip,
# uvx) is provisioned.
#
# Designed to be edited: the PLUGINS array near the top is the single
# source of truth. Add a row to install another plugin.
#
# Phases:
#   0. Detect repo path, sanity checks
#   1. System packages (apt)
#   2. uv bootstrap (needed for SuperClaude's airis-mcp-gateway)
#   3. Marketplace registration with on-disk post-condition probe
#   4. Plugin install with on-disk post-condition probe
#   5. Per-plugin Python dep provisioning (venv | system | uvx | none)
#   6. Plugin-specific config files (e.g. bitwize-music config.yaml)
#   7. Verification — assert every plugin and MCP command is reachable
# =============================================================================
set -euo pipefail

# =============================================================================
# CONFIGURATION — single source of truth.
#
# Each row is a pipe-delimited tuple:
#   <source> | <marketplace_name> | <plugin_name> | <dep_mode> | <dep_source> | <post_install>
#
# Fields:
#   source           Marketplace add target. Accepts:
#                      - GitHub shorthand:  "owner/repo"
#                      - Git URL:           "https://host/path.git"
#                      - Local directory:   absolute path or path relative
#                                           to the cloned repo root
#   marketplace_name The `name` field from the marketplace's marketplace.json.
#                    Must match exactly — `claude plugin install` uses it as
#                    the @-suffix.
#   plugin_name      The plugin inside that marketplace to install.
#   dep_mode         How to provision Python deps for this plugin:
#                      venv:<state-dir>  per-plugin venv at ${HOME}/.<state-dir>/venv
#                      system            system Python (PEP-668 aware)
#                      uvx               none; uvx fetches lazily at run time
#                      none              no dependencies
#   dep_source       Path inside the installed plugin dir to requirements.txt
#                    or pyproject.toml. Ignored for dep_mode=uvx|none.
#   post_install     Optional bash function name to invoke after install.
# =============================================================================
PLUGINS=(
    # bitwize-music — Suno music workflow, audio mastering, art direction.
    # MCP server uses absolute venv path: ${HOME}/.bitwize-music/venv/bin/python3
    "bitwize-music-studio/claude-ai-music-skills | bitwize-music | bitwize-music | venv:bitwize-music | requirements.txt | write_bitwize_config"

    # agency-system — orchestrator + unified MCP for music/novel/jules/agentic.
    # MCP server uses bare `python` → deps must be on system Python.
    "netzkontrast/the-agency-system | agency-marketplace | agency-system | system | servers/agency-mcp/pyproject.toml | "

    # SuperClaude — /sc:* slash commands. Its bundled airis-mcp-gateway MCP
    # entry (uvx --from git+...) is broken (the airis repo has no root
    # pyproject.toml). Useful MCPs are registered separately in Phase 4b.
    "SuperClaude-Org/SuperClaude_Plugin | superclaude | sc | uvx | | "

    # superpowers — pure skills + bash hooks, no MCP, no deps.
    "obra/superpowers-marketplace | superpowers-marketplace | superpowers | none | | "

    # episodic-memory — semantic search over past Claude Code sessions.
    # Node-based MCP server, needs `npm install` for native deps
    # (better-sqlite3, sqlite-vec, @huggingface/transformers).
    "obra/superpowers-marketplace | superpowers-marketplace | episodic-memory | npm:. | | "

    # superpowers-developing-for-claude-code — 42-file Claude Code docs
    # corpus + plugin-dev skills. No MCP, no runtime deps.
    "obra/superpowers-marketplace | superpowers-marketplace | superpowers-developing-for-claude-code | none | | "
)

# Standalone MCP servers registered via `claude mcp add` user-scope (not
# bundled inside any plugin). Pipe-delimited rows:
#   <name> | <transport> | <command-or-url> | <args>
# transport: stdio | http
# For stdio: command + space-separated args
# For http: url (args ignored)
STANDALONE_MCPS=(
    # SuperClaude's commands frequently reference Context7 ("library docs")
    # and Sequential-Thinking ("structured reasoning"). Register them as
    # lightweight npx-based MCPs so /sc:* commands have something to call
    # without standing up the AIRIS Docker stack.
    "context7 | stdio | npx | -y @upstash/context7-mcp@latest"
    "sequential-thinking | stdio | npx | -y @modelcontextprotocol/server-sequential-thinking"
)

# Optional: run the full AIRIS MCP Gateway Docker stack (25+ proxied MCPs:
# Serena, Tavily, Magic, Morphllm, mindbase, chrome-devtools, etc.).
# Adds ~5-10 min to setup, occupies port 9400, requires docker compose v2.
# Some upstream MCPs need API keys (TAVILY_API_KEY, TWENTYFIRST_API_KEY).
# Enable by exporting AIRIS_GATEWAY=1 before running this script.
AIRIS_GATEWAY="${AIRIS_GATEWAY:-0}"

# Bitwize-music writes album content under <REPO>/artists/... — the artist
# name is a logical label inside its config.yaml.
ARTIST_NAME="${ARTIST_NAME:-the-agency-system}"

# =============================================================================
# Helpers
# =============================================================================
log()  { printf '[setup] %s\n' "$*" >&2; }
warn() { printf '[setup] WARN: %s\n' "$*" >&2; }
die()  { printf '[setup] ERROR: %s\n' "$*" >&2; exit 1; }

# Run `claude` with stdin closed so any unexpected prompt fails fast
# instead of blocking the script forever.
claude_q() { claude "$@" < /dev/null; }

# =============================================================================
# Phase 0 — Detect cloned repo path.
#
# Setup runs from $HOME on cloud containers, not inside the clone, and
# CLAUDE_PROJECT_DIR isn't injected during environment-setup. Fall through
# four detection strategies.
# =============================================================================
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
log "HOME=${HOME}  REPO_PATH=${REPO_PATH}  ARTIST=${ARTIST_NAME}"

# =============================================================================
# Phase 1 — System packages.
# =============================================================================
log "Phase 1: installing system packages"
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq

# Core packages — must succeed. apt-get install aborts the whole batch on
# the first missing package, so anything that might be renamed across
# distros goes into the best-effort batch below.
apt-get install -y -qq \
    git git-lfs python3 python3-venv python3-pip python3-dev \
    ffmpeg libsndfile1 libpq-dev libsqlite3-dev build-essential pkg-config \
    ca-certificates curl jq nodejs npm \
    || die "core apt-get install failed — see output above"

# Playwright Chromium runtime libs — best-effort. Distro-renamed packages
# (libasound2 → libasound2t64 on Debian 13 / Ubuntu 24.04+) are tried as
# alternates. None of these are fatal — only document-hunter needs them.
apt-get install -y -qq --no-install-recommends \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 libxkbcommon0 libgbm1 \
    libxcomposite1 libxdamage1 libxfixes3 libxrandr2 \
    2>&1 | tail -2 || warn "some Chromium runtime libs missing (non-fatal)"

# libasound has two upstream names depending on Debian/Ubuntu version.
apt-get install -y -qq libasound2t64 2>/dev/null \
    || apt-get install -y -qq libasound2 2>/dev/null \
    || warn "libasound not installed — Playwright audio may not work"

git lfs install --skip-repo

# Detect PEP 668 once; reused by dep_mode=system installs.
PIP_BREAK_FLAG=""
if [ -e "/usr/lib/python3"*"/EXTERNALLY-MANAGED" ] 2>/dev/null \
   || ls /usr/lib/python3*/EXTERNALLY-MANAGED >/dev/null 2>&1; then
    PIP_BREAK_FLAG="--break-system-packages"
    log "  PEP 668 detected → pip will use ${PIP_BREAK_FLAG}"
fi

# =============================================================================
# Phase 2 — uv bootstrap.
#
# SuperClaude's `sc` plugin ships an MCP server whose command is `uvx`.
# Ensure uv is on PATH. Standard install location is ~/.local/bin/.
# =============================================================================
log "Phase 2: ensuring uv/uvx on PATH"
if ! command -v uvx >/dev/null 2>&1; then
    log "  installing uv via astral.sh installer"
    curl -LsSf https://astral.sh/uv/install.sh | sh < /dev/null 2>&1 | tail -3
    export PATH="${HOME}/.local/bin:${PATH}"
    # Persist for future shells / Claude MCP spawns that inherit env.
    if [ -f "${HOME}/.bashrc" ] && ! grep -q '.local/bin' "${HOME}/.bashrc"; then
        printf 'export PATH="%s/.local/bin:$PATH"\n' "${HOME}" >> "${HOME}/.bashrc"
    fi
fi
command -v uvx >/dev/null 2>&1 || die "uv install failed — uvx not on PATH"
log "  uv: $(uv --version 2>/dev/null || echo 'unknown')"

# Ensure bare `python` resolves. agency-system's .mcp.json invokes `python`
# directly; many container images only ship `python3`. Symlink into
# ~/.local/bin/ so it lands ahead of system paths once that dir is in PATH.
if ! command -v python >/dev/null 2>&1; then
    if command -v python3 >/dev/null 2>&1; then
        mkdir -p "${HOME}/.local/bin"
        ln -sf "$(command -v python3)" "${HOME}/.local/bin/python"
        log "  symlinked python → python3"
    else
        die "neither python nor python3 found on PATH"
    fi
fi

# =============================================================================
# Tuple parsing.
#
# bash 3 lacks associative arrays in some envs; we keep the row as a string
# and split on `|` only when iterating.
# =============================================================================
parse_row() {
    # Args: row index. Sets globals R_SOURCE, R_MP, R_PLUGIN, R_DEPMODE,
    # R_DEPSRC, R_POSTINSTALL.
    local row="${PLUGINS[$1]}"
    IFS='|' read -r R_SOURCE R_MP R_PLUGIN R_DEPMODE R_DEPSRC R_POSTINSTALL <<<"${row}"
    # trim each
    R_SOURCE="${R_SOURCE#"${R_SOURCE%%[![:space:]]*}"}"; R_SOURCE="${R_SOURCE%"${R_SOURCE##*[![:space:]]}"}"
    R_MP="${R_MP#"${R_MP%%[![:space:]]*}"}"; R_MP="${R_MP%"${R_MP##*[![:space:]]}"}"
    R_PLUGIN="${R_PLUGIN#"${R_PLUGIN%%[![:space:]]*}"}"; R_PLUGIN="${R_PLUGIN%"${R_PLUGIN##*[![:space:]]}"}"
    R_DEPMODE="${R_DEPMODE#"${R_DEPMODE%%[![:space:]]*}"}"; R_DEPMODE="${R_DEPMODE%"${R_DEPMODE##*[![:space:]]}"}"
    R_DEPSRC="${R_DEPSRC#"${R_DEPSRC%%[![:space:]]*}"}"; R_DEPSRC="${R_DEPSRC%"${R_DEPSRC##*[![:space:]]}"}"
    R_POSTINSTALL="${R_POSTINSTALL#"${R_POSTINSTALL%%[![:space:]]*}"}"; R_POSTINSTALL="${R_POSTINSTALL%"${R_POSTINSTALL##*[![:space:]]}"}"
}

# Resolve a source string for marketplace add. Local paths become absolute
# relative to REPO_PATH. GitHub shorthand and URLs pass through.
resolve_source() {
    local src="$1"
    if [[ "${src}" == /* ]] || [[ "${src}" == "." ]] || [[ "${src}" == ./* ]]; then
        (cd "${REPO_PATH}" && cd "${src}" && pwd -P)
    else
        printf '%s\n' "${src}"
    fi
}

# Path to known_marketplaces.json (Claude tries HOME first; fall back for
# environments where claude wrote to /root or /home/user explicitly).
known_marketplaces_path() {
    local p
    for p in \
        "${HOME}/.claude/plugins/known_marketplaces.json" \
        "/root/.claude/plugins/known_marketplaces.json" \
        "/home/user/.claude/plugins/known_marketplaces.json"; do
        [ -f "${p}" ] && { printf '%s\n' "${p}"; return; }
    done
    return 1
}

installed_plugins_path() {
    local p
    for p in \
        "${HOME}/.claude/plugins/installed_plugins.json" \
        "/root/.claude/plugins/installed_plugins.json" \
        "/home/user/.claude/plugins/installed_plugins.json"; do
        [ -f "${p}" ] && { printf '%s\n' "${p}"; return; }
    done
    return 1
}

marketplace_installed() {
    local name="$1"
    local km
    km="$(known_marketplaces_path)" || return 1
    python3 -c "
import json, sys
try:
    data = json.load(open('${km}'))
except Exception:
    sys.exit(1)
sys.exit(0 if '${name}' in data else 1)
"
}

plugin_installed() {
    local plugin_ref="$1"   # name@marketplace
    local ip
    ip="$(installed_plugins_path)" || return 1
    python3 -c "
import json, sys
try:
    data = json.load(open('${ip}'))
except Exception:
    sys.exit(1)
plugins = data.get('plugins', {})
sys.exit(0 if '${plugin_ref}' in plugins else 1)
"
}

marketplace_install_location() {
    local name="$1"
    local km
    km="$(known_marketplaces_path)" || return 1
    python3 -c "
import json
data = json.load(open('${km}'))
entry = data.get('${name}', {})
print(entry.get('installLocation', ''))
"
}

# =============================================================================
# Phase 3 — Marketplace registration.
# =============================================================================
log "Phase 3: registering marketplaces"
for i in "${!PLUGINS[@]}"; do
    parse_row "$i"
    if marketplace_installed "${R_MP}"; then
        log "  ${R_MP} already registered"
        continue
    fi
    resolved="$(resolve_source "${R_SOURCE}")"
    log "  registering ${R_MP} from ${resolved}"
    claude_q plugin marketplace add "${resolved}" 2>&1 | sed 's/^/[setup]     /' || true
    if ! marketplace_installed "${R_MP}"; then
        die "marketplace ${R_MP} not present in known_marketplaces.json after add. \
Source=${resolved}. Likely cause: marketplace name in marketplace.json does \
not match the declared name, or the CLI prompted for trust on closed stdin."
    fi
done

# =============================================================================
# Phase 4 — Plugin install.
# =============================================================================
log "Phase 4: installing plugins"
for i in "${!PLUGINS[@]}"; do
    parse_row "$i"
    local_ref="${R_PLUGIN}@${R_MP}"
    if plugin_installed "${local_ref}"; then
        log "  ${local_ref} already installed"
        continue
    fi
    log "  installing ${local_ref}"
    claude_q plugin install "${local_ref}" -s user 2>&1 | sed 's/^/[setup]     /' || true
    if ! plugin_installed "${local_ref}"; then
        die "plugin ${local_ref} not present in installed_plugins.json after install. \
Likely cause: trust prompt blocked, or marketplace_name/plugin_name mismatch."
    fi
done

# =============================================================================
# Phase 4b — Standalone MCP server registration (user-scope).
#
# These are MCPs that aren't bundled in any plugin we install. Idempotent:
# checks ~/.claude.json for existing user-scope mcpServers entries.
# =============================================================================
log "Phase 4b: registering standalone MCP servers (user-scope)"

user_mcp_registered() {
    local name="$1"
    local cfg="${HOME}/.claude.json"
    [ -f "${cfg}" ] || return 1
    python3 -c "
import json, sys
try:
    data = json.load(open('${cfg}'))
except Exception:
    sys.exit(1)
sys.exit(0 if '${name}' in data.get('mcpServers', {}) else 1)
"
}

for row in "${STANDALONE_MCPS[@]}"; do
    IFS='|' read -r M_NAME M_TRANSPORT M_CMD M_ARGS <<<"${row}"
    M_NAME="$(printf '%s' "${M_NAME}" | xargs)"
    M_TRANSPORT="$(printf '%s' "${M_TRANSPORT}" | xargs)"
    M_CMD="$(printf '%s' "${M_CMD}" | xargs)"
    M_ARGS="$(printf '%s' "${M_ARGS}" | xargs)"
    if user_mcp_registered "${M_NAME}"; then
        log "  ${M_NAME} already registered"
        continue
    fi
    log "  registering ${M_NAME} (${M_TRANSPORT})"
    if [ "${M_TRANSPORT}" = "http" ]; then
        claude_q mcp add --scope user --transport http "${M_NAME}" "${M_CMD}" \
            2>&1 | sed 's/^/[setup]     /' || warn "    mcp add failed for ${M_NAME}"
    else
        # stdio: claude mcp add <name> <command> [args...]
        # shellcheck disable=SC2086
        claude_q mcp add --scope user "${M_NAME}" "${M_CMD}" ${M_ARGS} \
            2>&1 | sed 's/^/[setup]     /' || warn "    mcp add failed for ${M_NAME}"
    fi
done

# =============================================================================
# Phase 4c — Optional AIRIS MCP Gateway Docker stack.
#
# Heavy: 25+ proxied MCP servers, port 9400, docker compose. Some upstream
# servers require API keys. Gated by AIRIS_GATEWAY=1.
# =============================================================================
if [ "${AIRIS_GATEWAY}" = "1" ]; then
    log "Phase 4c: AIRIS MCP Gateway (AIRIS_GATEWAY=1)"
    if ! command -v docker >/dev/null 2>&1 || ! docker info >/dev/null 2>&1; then
        warn "  docker not available/running — skipping AIRIS stack"
    elif ! docker compose version >/dev/null 2>&1; then
        warn "  docker compose v2 not available — skipping AIRIS stack"
    else
        AIRIS_DIR="${HOME}/.local/share/airis-mcp-gateway"
        if [ ! -x "${HOME}/.local/bin/airis-gateway" ]; then
            log "  running AIRIS install.sh"
            curl -fsSL https://raw.githubusercontent.com/agiletec-inc/airis-mcp-gateway/main/install.sh \
                | bash < /dev/null 2>&1 | tail -5 || warn "    AIRIS install.sh failed"
        else
            log "  AIRIS already installed at ${AIRIS_DIR}"
        fi
        if [ -x "${HOME}/.local/bin/airis-gateway" ]; then
            "${HOME}/.local/bin/airis-gateway" up < /dev/null 2>&1 | tail -3 \
                || warn "    airis-gateway up failed"
            # Register the HTTP MCP endpoint (idempotent).
            if ! user_mcp_registered "airis-mcp-gateway"; then
                claude_q mcp add --scope user --transport http airis-mcp-gateway \
                    "http://localhost:9400/mcp/" 2>&1 | sed 's/^/[setup]     /' \
                    || warn "    mcp add airis-mcp-gateway failed"
            fi
        fi
    fi
else
    log "Phase 4c: AIRIS Docker stack skipped (set AIRIS_GATEWAY=1 to enable)"
fi

# =============================================================================
# Phase 5 — Per-plugin Python dep provisioning.
# =============================================================================
log "Phase 5: provisioning per-plugin dependencies"

# Resolve a plugin's on-disk directory by walking installed_plugins.json.
plugin_dir() {
    local plugin_ref="$1"   # name@marketplace
    local ip
    ip="$(installed_plugins_path)" || return 1
    python3 -c "
import json
data = json.load(open('${ip}'))
entries = data.get('plugins', {}).get('${plugin_ref}', [])
for e in entries:
    p = e.get('installPath') or e.get('install_path')
    if p:
        print(p); break
"
}

provision_venv() {
    # Args: state-dir-name, plugin-dir, dep-source (requirements.txt or pyproject.toml)
    local state_name="$1" pdir="$2" depsrc="$3"
    local state_dir="${HOME}/.${state_name}"
    local venv="${state_dir}/venv"
    local depfile="${pdir}/${depsrc}"
    [ -f "${depfile}" ] || { warn "  ${depfile} missing — skipping venv provisioning"; return; }

    mkdir -p "${state_dir}"
    if [ ! -x "${venv}/bin/python3" ]; then
        log "  creating venv ${venv}"
        python3 -m venv "${venv}"
    fi
    log "  installing ${state_name} deps into ${venv}"
    "${venv}/bin/pip" install --quiet --upgrade pip wheel setuptools
    if [[ "${depsrc}" == *.txt ]]; then
        "${venv}/bin/pip" install --quiet -r "${depfile}" \
            || warn "    pip install failed for ${state_name}"
    else
        "${venv}/bin/pip" install --quiet "${pdir}/$(dirname "${depsrc}")" \
            || warn "    pip install failed for ${state_name}"
    fi
    # Bitwize-music convention: playwright chromium for document-hunter.
    if [ -x "${venv}/bin/playwright" ]; then
        "${venv}/bin/playwright" install chromium >/dev/null 2>&1 \
            || warn "    playwright chromium install failed (non-fatal)"
    fi
    # Sentinel for SessionStart fast-paths in plugins that check it.
    python3 -c "
import hashlib
print(hashlib.sha256(open('${depfile}','rb').read()).hexdigest())
" > "${state_dir}/.setup-complete"
}

provision_system() {
    # Args: plugin-dir, dep-source. Installs into system python so bare
    # `python`/`python3` resolves the package.
    local pdir="$1" depsrc="$2"
    local depfile="${pdir}/${depsrc}"

    if [ -n "${depsrc}" ] && [ -f "${depfile}" ]; then
        if [[ "${depsrc}" == *.txt ]]; then
            log "  pip install -r ${depfile} (system)"
            python3 -m pip install --quiet ${PIP_BREAK_FLAG} -r "${depfile}" \
                || warn "    pip install failed"
        else
            local depdir; depdir="$(dirname "${depfile}")"
            log "  pip install -e ${depdir} (system, editable)"
            python3 -m pip install --quiet ${PIP_BREAK_FLAG} -e "${depdir}" \
                || warn "    editable install failed for ${depdir}"
        fi
    fi

    # Also walk servers/*/pyproject.toml so multi-server plugins
    # (agency-system has agency-mcp + session-log-mcp) get every package.
    if [ -d "${pdir}/servers" ]; then
        local s
        for s in "${pdir}/servers"/*/; do
            [ -f "${s}pyproject.toml" ] || continue
            # Skip the one already installed above to avoid double work.
            if [ -n "${depsrc}" ] && [ "${pdir}/${depsrc}" = "${s}pyproject.toml" ]; then
                continue
            fi
            log "  pip install -e ${s} (system, editable, sibling MCP)"
            python3 -m pip install --quiet ${PIP_BREAK_FLAG} -e "${s}" \
                || warn "    editable install failed for ${s}"
        done
    fi
}

provision_uvx() {
    # No-op. uvx will fetch lazily on first MCP spawn.
    # Optional best-effort warm-up: pre-fetch airis-mcp-gateway so the
    # first /sc: command isn't gated on a 30-second git clone.
    log "  uvx mode — skipping eager install (uvx fetches lazily)"
}

provision_npm() {
    # Args: plugin-dir, subdir (relative to plugin-dir; default ".")
    local pdir="$1" subdir="${2:-.}"
    local target="${pdir}/${subdir}"
    if [ ! -f "${target}/package.json" ]; then
        warn "  ${target}/package.json missing — skipping npm install"
        return
    fi
    log "  npm install in ${target}"
    ( cd "${target}" && npm install --no-audit --no-fund --loglevel=error 2>&1 | tail -3 ) \
        || warn "    npm install reported issues for ${target}"
}

# Plugin-specific post-install hook(s).
# Called by name from the PLUGINS table's last column.
write_bitwize_config() {
    # Bitwize-music expects ${HOME}/.bitwize-music/config.yaml.
    # Regenerated each run so paths track REPO_PATH (not /home/user/...).
    local cfg="${HOME}/.bitwize-music/config.yaml"
    mkdir -p "${HOME}/.bitwize-music"
    log "  writing ${cfg}"
    local tmp; tmp="$(mktemp "${cfg}.XXXXXX")"
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
    mv -f "${tmp}" "${cfg}"
}

# Dispatch per-plugin provisioning.
for i in "${!PLUGINS[@]}"; do
    parse_row "$i"
    local_ref="${R_PLUGIN}@${R_MP}"
    pdir="$(plugin_dir "${local_ref}")"
    if [ -z "${pdir}" ] || [ ! -d "${pdir}" ]; then
        warn "  could not resolve install dir for ${local_ref} — skipping deps"
        continue
    fi
    log "${local_ref} → mode=${R_DEPMODE}  dir=${pdir}"
    case "${R_DEPMODE}" in
        venv:*)
            state_name="${R_DEPMODE#venv:}"
            provision_venv "${state_name}" "${pdir}" "${R_DEPSRC}"
            ;;
        system)
            provision_system "${pdir}" "${R_DEPSRC}"
            ;;
        uvx)
            provision_uvx
            ;;
        npm|npm:*)
            subdir="${R_DEPMODE#npm}"; subdir="${subdir#:}"
            provision_npm "${pdir}" "${subdir:-.}"
            ;;
        none)
            log "  no deps to install"
            ;;
        *)
            warn "  unknown dep_mode '${R_DEPMODE}' — skipping"
            ;;
    esac
done

# =============================================================================
# Phase 6 — Plugin-specific config files.
# =============================================================================
log "Phase 6: plugin-specific config files"
for i in "${!PLUGINS[@]}"; do
    parse_row "$i"
    if [ -n "${R_POSTINSTALL}" ] && declare -F "${R_POSTINSTALL}" >/dev/null 2>&1; then
        log "${R_PLUGIN}@${R_MP} → ${R_POSTINSTALL}"
        "${R_POSTINSTALL}"
    fi
done

# =============================================================================
# Phase 7 — Verification.
#
# Every claim the script needs to be true must be probed here. Any failure
# = non-zero exit with an actionable error message. This is the single
# chokepoint that prevents silent partial-success states.
# =============================================================================
log "Phase 7: verifying installation"
FAIL=0
fail() { warn "VERIFY: $*"; FAIL=$((FAIL + 1)); }

for i in "${!PLUGINS[@]}"; do
    parse_row "$i"
    ref="${R_PLUGIN}@${R_MP}"
    if plugin_installed "${ref}"; then
        log "  ✓ plugin installed: ${ref}"
    else
        fail "plugin missing from installed_plugins.json: ${ref}"
        continue
    fi
    # dep-mode-specific reachability probes
    case "${R_DEPMODE}" in
        venv:*)
            state_name="${R_DEPMODE#venv:}"
            vpy="${HOME}/.${state_name}/venv/bin/python3"
            [ -x "${vpy}" ] && log "  ✓ venv python: ${vpy}" \
                || fail "venv python missing: ${vpy}"
            ;;
        system)
            command -v python >/dev/null 2>&1 && log "  ✓ system python on PATH" \
                || fail "bare 'python' not on PATH (agency-system MCP needs it)"
            if [ "${R_PLUGIN}" = "agency-system" ]; then
                python3 -c "import agency_mcp" >/dev/null 2>&1 \
                    && log "  ✓ import agency_mcp" \
                    || fail "import agency_mcp failed — agency-system MCP will not start"
            fi
            ;;
        uvx)
            command -v uvx >/dev/null 2>&1 && log "  ✓ uvx on PATH" \
                || fail "uvx missing — sc plugin's airis-mcp-gateway needs it"
            ;;
        npm|npm:*)
            command -v node >/dev/null 2>&1 && log "  ✓ node on PATH" \
                || fail "node missing — episodic-memory needs it"
            ;;
    esac
done

# Standalone MCPs (Phase 4b) — check user-scope registration.
for row in "${STANDALONE_MCPS[@]}"; do
    IFS='|' read -r M_NAME _ _ _ <<<"${row}"
    M_NAME="$(printf '%s' "${M_NAME}" | xargs)"
    if user_mcp_registered "${M_NAME}"; then
        log "  ✓ standalone MCP registered: ${M_NAME}"
    else
        fail "standalone MCP not registered in ~/.claude.json: ${M_NAME}"
    fi
done

# AIRIS gateway (if enabled).
if [ "${AIRIS_GATEWAY}" = "1" ]; then
    if user_mcp_registered "airis-mcp-gateway"; then
        log "  ✓ airis-mcp-gateway registered"
    else
        fail "airis-mcp-gateway not registered (AIRIS_GATEWAY=1 but setup failed)"
    fi
fi

if [ "${FAIL}" -gt 0 ]; then
    die "${FAIL} verification check(s) failed — see [setup] WARN lines above"
fi

# =============================================================================
# Done.
# =============================================================================
log "DONE — all checks passed."
log "  REPO_PATH=${REPO_PATH}"
log "  Installed plugins:"
for i in "${!PLUGINS[@]}"; do
    parse_row "$i"
    log "    - ${R_PLUGIN}@${R_MP}  (deps: ${R_DEPMODE})"
done
log "  Standalone MCPs registered:"
for row in "${STANDALONE_MCPS[@]}"; do
    IFS='|' read -r M_NAME M_TRANSPORT _ _ <<<"${row}"
    log "    - $(printf '%s' "${M_NAME}" | xargs)  (${M_TRANSPORT})"
done
[ "${AIRIS_GATEWAY}" = "1" ] && log "    - airis-mcp-gateway (http)"
log "Verify in a new session: claude plugin list  &&  claude mcp list"
