#!/usr/bin/env bash
# =============================================================================
# Universal Claude Code Web environment installer (v4 — hand-install).
#
# `claude plugin install` proved unreliable in the cloud container (silent
# half-installs, plugins absent from `enabledPlugins` after `install`
# returned 0). This script bypasses the CLI entirely and replicates what
# a successful install puts on disk:
#
#   1.  git-clone each marketplace source to ~/.claude/plugins/marketplaces/<mp>/
#   2.  For each plugin whose `source` is a URL, git-clone it to
#       ~/.claude/plugins/cache/<mp>/<plugin>/<version>/  (Claude's own
#       layout). For `source: "./"` plugins, the marketplace dir IS the
#       plugin dir.
#   3.  Merge entries into:
#         ~/.claude/plugins/known_marketplaces.json
#         ~/.claude/plugins/installed_plugins.json
#         <project>/.claude/settings.json   (enabledPlugins + extraKnownMarketplaces)
#         ~/.claude.json                    (top-level mcpServers for standalone)
#   4.  Provision per-plugin deps (Python venv | system | uvx | npm | none).
#   5.  Optional AIRIS Docker stack (gated by AIRIS_GATEWAY=1).
#   6.  Verify every claim, exit ≠0 on any failure.
#
# Idempotent. Safe to re-run. All JSON writes go through jq with atomic
# temp-file rename so a crash mid-write never leaves a half-merged file.
# =============================================================================
set -euo pipefail

# =============================================================================
# CONFIGURATION
# =============================================================================
# Each row: <mp_source> | <mp_name> | <plugin_name> | <plugin_clone> | <dep_mode> | <dep_source> | <post_install>
#
#   mp_source       Source URL/repo of the marketplace. Used to populate the
#                   marketplace dir at ~/.claude/plugins/marketplaces/<mp_name>/.
#                   Format: GitHub shorthand "owner/repo" OR full URL.
#   mp_name         The `name` field inside the marketplace's marketplace.json.
#                   Must match — Claude uses it as the @-suffix.
#   plugin_name     Plugin name inside marketplace.json.
#   plugin_clone    "inline" if plugin.source is "./" (use marketplace dir);
#                   otherwise the URL to clone the plugin from.
#   dep_mode        venv:<state-dir> | system | uvx | npm | none
#   dep_source      Path inside the plugin dir to requirements.txt or
#                   pyproject.toml (ignored for npm/none/uvx).
#   post_install    Optional bash function name called after dep install.
PLUGINS=(
    "bitwize-music-studio/claude-ai-music-skills | bitwize-music | bitwize-music | inline | venv:bitwize-music | requirements.txt | write_bitwize_config"
    "netzkontrast/the-agency-system | agency-marketplace | agency-system | inline | pyvenv:agency-system | servers/agency-mcp/pyproject.toml | "
    "SuperClaude-Org/SuperClaude_Plugin | superclaude | sc | inline | none | | "
    "obra/superpowers-marketplace | superpowers-marketplace | superpowers | https://github.com/obra/superpowers.git | none | | "
    "obra/superpowers-marketplace | superpowers-marketplace | episodic-memory | https://github.com/obra/episodic-memory.git | npm | | "
    "obra/superpowers-marketplace | superpowers-marketplace | superpowers-developing-for-claude-code | https://github.com/obra/superpowers-developing-for-claude-code.git | none | | "
)

# Standalone MCPs (user-scope, registered into ~/.claude.json top-level mcpServers).
# Format: <name> | <transport> | <command-or-url> | <space-separated-args>
STANDALONE_MCPS=(
    "context7 | stdio | npx | -y @upstash/context7-mcp@latest"
    "sequential-thinking | stdio | npx | -y @modelcontextprotocol/server-sequential-thinking"
)

AIRIS_GATEWAY="${AIRIS_GATEWAY:-0}"
ARTIST_NAME="${ARTIST_NAME:-the-agency-system}"

# =============================================================================
# Helpers
# =============================================================================
log()  { printf '[setup] %s\n' "$*" >&2; }
warn() { printf '[setup] WARN: %s\n' "$*" >&2; }
die()  { printf '[setup] ERROR: %s\n' "$*" >&2; exit 1; }

# Atomic JSON merge: jq filter over existing file (or {}) → temp file → mv.
# Signature: json_merge <path> [--arg KEY VAL]... <filter>
# The LAST positional argument is the jq filter; everything between path
# and filter is passed verbatim to jq (--arg / --argjson pairs).
json_merge() {
    local path="$1"; shift
    local n=$#
    [ "${n}" -ge 1 ] || die "json_merge: filter required"
    local args=( "${@:1:n-1}" )
    local filter="${@:n:1}"
    mkdir -p "$(dirname "${path}")"
    local input='{}'
    [ -f "${path}" ] && input="$(cat "${path}")"
    local tmp; tmp="$(mktemp "${path}.XXXXXX")"
    if printf '%s' "${input}" | jq "${args[@]}" "${filter}" > "${tmp}"; then
        mv -f "${tmp}" "${path}"
    else
        rm -f "${tmp}"
        die "jq merge failed for ${path}"
    fi
}

# =============================================================================
# Phase 0 — repo detection
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
[ -d "${REPO_PATH}/.git" ] || die "REPO_PATH=${REPO_PATH} is not a git repo"
log "HOME=${HOME}  REPO_PATH=${REPO_PATH}"

# Claude config paths.
CLAUDE_PLUGINS_DIR="${HOME}/.claude/plugins"
KNOWN_MP="${CLAUDE_PLUGINS_DIR}/known_marketplaces.json"
INSTALLED_PLUGINS="${CLAUDE_PLUGINS_DIR}/installed_plugins.json"
USER_CLAUDE_JSON="${HOME}/.claude.json"
PROJECT_SETTINGS="${REPO_PATH}/.claude/settings.json"

mkdir -p "${CLAUDE_PLUGINS_DIR}/marketplaces" "${CLAUDE_PLUGINS_DIR}/cache"

# =============================================================================
# Phase 1 — system packages
# =============================================================================
log "Phase 1: system packages"
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq \
    git git-lfs python3 python3-venv python3-pip python3-dev \
    ffmpeg libsndfile1 libpq-dev libsqlite3-dev build-essential pkg-config \
    ca-certificates curl jq nodejs npm \
    || die "core apt-get install failed"

apt-get install -y -qq --no-install-recommends \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 libxkbcommon0 libgbm1 \
    libxcomposite1 libxdamage1 libxfixes3 libxrandr2 2>&1 | tail -1 \
    || warn "some Chromium runtime libs missing (non-fatal)"
apt-get install -y -qq libasound2t64 2>/dev/null \
    || apt-get install -y -qq libasound2 2>/dev/null \
    || warn "libasound not installed (non-fatal)"
git lfs install --skip-repo

# Detect PEP 668.
PIP_BREAK_FLAG=""
ls /usr/lib/python3*/EXTERNALLY-MANAGED >/dev/null 2>&1 \
    && PIP_BREAK_FLAG="--break-system-packages" \
    && log "  PEP 668 active → pip uses ${PIP_BREAK_FLAG}"

# =============================================================================
# Phase 2 — uv bootstrap + python symlink
# =============================================================================
log "Phase 2: uv + python symlink"
if ! command -v uvx >/dev/null 2>&1; then
    curl -LsSf https://astral.sh/uv/install.sh | sh < /dev/null 2>&1 | tail -2
    export PATH="${HOME}/.local/bin:${PATH}"
    if [ -f "${HOME}/.bashrc" ] && ! grep -q '.local/bin' "${HOME}/.bashrc"; then
        printf 'export PATH="%s/.local/bin:$PATH"\n' "${HOME}" >> "${HOME}/.bashrc"
    fi
fi
command -v uvx >/dev/null || die "uv install failed"

# Ensure bare `python` resolves (agency-system MCP calls it directly).
if ! command -v python >/dev/null 2>&1; then
    mkdir -p "${HOME}/.local/bin"
    ln -sf "$(command -v python3)" "${HOME}/.local/bin/python"
    log "  symlinked python → python3"
fi

# =============================================================================
# Phase 3 — hand-install plugins
# =============================================================================
log "Phase 3: hand-installing plugins"

# Convert a source ("owner/repo" or full URL) into a clone URL.
clone_url() {
    local s="$1"
    case "${s}" in
        https://*|http://*|git@*) printf '%s\n' "${s}" ;;
        *) printf 'https://github.com/%s.git\n' "${s}" ;;
    esac
}

# Git-clone (or fast-pull) into a target dir. Idempotent.
clone_or_update() {
    local url="$1" target="$2"
    if [ -d "${target}/.git" ]; then
        log "  ↻ updating ${target}"
        ( cd "${target}" && git fetch --quiet --depth=1 origin HEAD 2>&1 \
            && git reset --quiet --hard FETCH_HEAD ) 2>&1 | tail -1 \
            || warn "    update failed (keeping existing)"
    else
        log "  ⇣ cloning ${url} → ${target}"
        mkdir -p "$(dirname "${target}")"
        rm -rf "${target}"
        git clone --quiet --depth=1 "${url}" "${target}" 2>&1 | tail -2 \
            || die "clone failed: ${url}"
    fi
}

parse_row() {
    local row="${PLUGINS[$1]}"
    IFS='|' read -r R_SRC R_MP R_PLUGIN R_CLONE R_DEPMODE R_DEPSRC R_POST <<<"${row}"
    for v in R_SRC R_MP R_PLUGIN R_CLONE R_DEPMODE R_DEPSRC R_POST; do
        eval "${v}=\$(printf '%s' \"\${${v}}\" | xargs)"
    done
}

# Resolve plugin install dir + read its version from plugin.json.
plugin_install_dir() {
    local mp_name="$1" plugin_name="$2" clone="$3" version="$4"
    if [ "${clone}" = "inline" ]; then
        printf '%s\n' "${CLAUDE_PLUGINS_DIR}/marketplaces/${mp_name}"
    else
        printf '%s\n' "${CLAUDE_PLUGINS_DIR}/cache/${mp_name}/${plugin_name}/${version}"
    fi
}

read_plugin_version() {
    local dir="$1"
    local pj="${dir}/.claude-plugin/plugin.json"
    [ -f "${pj}" ] || { printf '0.0.0\n'; return; }
    jq -r '.version // "0.0.0"' "${pj}"
}

# Process each plugin row.
declare -a INSTALLED_REFS=()
for i in "${!PLUGINS[@]}"; do
    parse_row "$i"
    REF="${R_PLUGIN}@${R_MP}"
    log "${REF}"

    # 3a. Clone marketplace source if not already present.
    MP_DIR="${CLAUDE_PLUGINS_DIR}/marketplaces/${R_MP}"
    MP_URL="$(clone_url "${R_SRC}")"
    clone_or_update "${MP_URL}" "${MP_DIR}"

    # 3b. Resolve plugin dir: inline (= marketplace dir) or remote clone into cache/.
    if [ "${R_CLONE}" = "inline" ]; then
        PLUGIN_DIR="${MP_DIR}"
    else
        # Read plugin version from a tentative clone target so version is stable.
        # We clone first, then learn the version from plugin.json.
        TMP_TARGET="${CLAUDE_PLUGINS_DIR}/cache/${R_MP}/${R_PLUGIN}/__staging"
        clone_or_update "${R_CLONE}" "${TMP_TARGET}"
        VER="$(read_plugin_version "${TMP_TARGET}")"
        FINAL_TARGET="${CLAUDE_PLUGINS_DIR}/cache/${R_MP}/${R_PLUGIN}/${VER}"
        if [ "${TMP_TARGET}" != "${FINAL_TARGET}" ]; then
            mkdir -p "$(dirname "${FINAL_TARGET}")"
            rm -rf "${FINAL_TARGET}"
            mv "${TMP_TARGET}" "${FINAL_TARGET}"
        fi
        PLUGIN_DIR="${FINAL_TARGET}"
    fi
    log "  plugin_dir=${PLUGIN_DIR}"

    # 3c. Update known_marketplaces.json.
    # Schema: {"<mp_name>": {"source": {"source":"github","repo":"owner/repo"} | {"source":"url","url":"..."}, "installLocation": "..."}}
    case "${R_SRC}" in
        https://*|http://*|git@*)
            json_merge "${KNOWN_MP}" \
                --arg name "${R_MP}" --arg url "${R_SRC}" --arg loc "${MP_DIR}" \
                '. + {($name): {"source": {"source": "url", "url": $url}, "installLocation": $loc, "lastUpdated": now | strftime("%Y-%m-%dT%H:%M:%SZ")}}'
            ;;
        *)
            json_merge "${KNOWN_MP}" \
                --arg name "${R_MP}" --arg repo "${R_SRC}" --arg loc "${MP_DIR}" \
                '. + {($name): {"source": {"source": "github", "repo": $repo}, "installLocation": $loc, "lastUpdated": now | strftime("%Y-%m-%dT%H:%M:%SZ")}}'
            ;;
    esac

    # 3d. Update installed_plugins.json.
    # Schema: {"version": 2, "plugins": {"<plugin>@<mp>": [{"scope":"user", "installPath":"...", "version":"...", ...}]}}
    PVER="$(read_plugin_version "${PLUGIN_DIR}")"
    GITSHA="$(git -C "${PLUGIN_DIR}" rev-parse HEAD 2>/dev/null || printf 'unknown')"
    json_merge "${INSTALLED_PLUGINS}" \
        --arg ref "${REF}" --arg path "${PLUGIN_DIR}" --arg ver "${PVER}" \
        --arg sha "${GITSHA}" --arg proj "${REPO_PATH}" \
        '
        .version = 2
        | .plugins //= {}
        | .plugins[$ref] = [
            {
              "scope": "user",
              "installPath": $path,
              "version": $ver,
              "installedAt": (now | strftime("%Y-%m-%dT%H:%M:%SZ")),
              "lastUpdated": (now | strftime("%Y-%m-%dT%H:%M:%SZ")),
              "gitCommitSha": $sha,
              "projectPath": $proj
            }
          ]
        '

    INSTALLED_REFS+=("${REF}|${PLUGIN_DIR}|${R_DEPMODE}|${R_DEPSRC}|${R_POST}|${R_MP}|${R_SRC}")
done

# =============================================================================
# Phase 3.5 — fix the project's own .mcp.json.
#
# Claude scope-precedence rule (per code.claude.com docs): project >
# plugin. The repo ships a project-root .mcp.json that uses
# ${CLAUDE_PLUGIN_ROOT} (a plugin-scope-only variable). In project
# scope that variable doesn't expand → MCP path is broken → project
# entry shadows the now-installed plugin entry → agency-system fails
# to connect even though the plugin is correctly installed.
#
# Rewrite ${CLAUDE_PLUGIN_ROOT} → ${CLAUDE_PROJECT_DIR:-.} so the
# project-scope registration ALSO works (which is the right reference
# for a project-root .mcp.json anyway).
# =============================================================================
PROJECT_MCP="${REPO_PATH}/.mcp.json"
if [ -f "${PROJECT_MCP}" ] && grep -q '\${CLAUDE_PLUGIN_ROOT}' "${PROJECT_MCP}"; then
    log "Phase 3.5: fixing ${PROJECT_MCP} (CLAUDE_PLUGIN_ROOT → CLAUDE_PROJECT_DIR:-.)"
    cp "${PROJECT_MCP}" "${PROJECT_MCP}.bak"
    sed -i 's|\${CLAUDE_PLUGIN_ROOT}|\${CLAUDE_PROJECT_DIR:-.}|g' "${PROJECT_MCP}"
    log "  backup at ${PROJECT_MCP}.bak"
fi

# =============================================================================
# Phase 4 — write project .claude/settings.json (merge enabledPlugins +
#           extraKnownMarketplaces; preserve existing hooks/permissions).
# =============================================================================
log "Phase 4: project settings.json (enabledPlugins + extraKnownMarketplaces)"
mkdir -p "$(dirname "${PROJECT_SETTINGS}")"

# Build the patch in two passes: enabledPlugins additions, then marketplaces.
for entry in "${INSTALLED_REFS[@]}"; do
    IFS='|' read -r REF _ _ _ _ R_MP R_SRC <<<"${entry}"
    # enabledPlugins
    json_merge "${PROJECT_SETTINGS}" --arg ref "${REF}" \
        '
        .enabledPlugins //= {}
        | .enabledPlugins[$ref] = true
        '
    # extraKnownMarketplaces — github vs url source
    case "${R_SRC}" in
        https://*|http://*|git@*)
            json_merge "${PROJECT_SETTINGS}" --arg name "${R_MP}" --arg url "${R_SRC}" \
                '
                .extraKnownMarketplaces //= {}
                | .extraKnownMarketplaces[$name] //= {"source": {"source": "url", "url": $url}}
                '
            ;;
        *)
            json_merge "${PROJECT_SETTINGS}" --arg name "${R_MP}" --arg repo "${R_SRC}" \
                '
                .extraKnownMarketplaces //= {}
                | .extraKnownMarketplaces[$name] //= {"source": {"source": "github", "repo": $repo}}
                '
            ;;
    esac
done

# =============================================================================
# Phase 4b — standalone MCPs (user-scope in ~/.claude.json)
# =============================================================================
log "Phase 4b: standalone MCP servers (user-scope ~/.claude.json)"
for row in "${STANDALONE_MCPS[@]}"; do
    IFS='|' read -r M_NAME M_TRANSPORT M_CMD M_ARGS <<<"${row}"
    M_NAME="$(printf '%s' "${M_NAME}" | xargs)"
    M_TRANSPORT="$(printf '%s' "${M_TRANSPORT}" | xargs)"
    M_CMD="$(printf '%s' "${M_CMD}" | xargs)"
    M_ARGS="$(printf '%s' "${M_ARGS}" | xargs)"
    log "  ${M_NAME} (${M_TRANSPORT})"
    # Per docs: user-scope MCPs go in ~/.claude.json top-level mcpServers.
    if [ "${M_TRANSPORT}" = "http" ]; then
        json_merge "${USER_CLAUDE_JSON}" --arg name "${M_NAME}" --arg url "${M_CMD}" \
            '
            .mcpServers //= {}
            | .mcpServers[$name] = {"type": "http", "url": $url}
            '
    else
        # stdio: build args array from space-separated string.
        # shellcheck disable=SC2206
        ARGS_ARR=( ${M_ARGS} )
        ARGS_JSON="$(printf '%s\n' "${ARGS_ARR[@]}" | jq -R . | jq -s .)"
        json_merge "${USER_CLAUDE_JSON}" --arg name "${M_NAME}" --arg cmd "${M_CMD}" --argjson args "${ARGS_JSON}" \
            '
            .mcpServers //= {}
            | .mcpServers[$name] = {"type": "stdio", "command": $cmd, "args": $args}
            '
    fi
done

# =============================================================================
# Phase 5 — per-plugin dep provisioning
# =============================================================================
log "Phase 5: per-plugin dep provisioning"

provision_venv() {
    local state_name="$1" pdir="$2" depsrc="$3"
    local state_dir="${HOME}/.${state_name}"
    local venv="${state_dir}/venv"
    local depfile="${pdir}/${depsrc}"
    [ -f "${depfile}" ] || { warn "  ${depfile} missing"; return; }
    mkdir -p "${state_dir}"
    [ -x "${venv}/bin/python3" ] || { log "  creating venv ${venv}"; python3 -m venv "${venv}"; }
    "${venv}/bin/pip" install --quiet --upgrade pip wheel setuptools
    log "  pip install -r ${depfile}"
    "${venv}/bin/pip" install --quiet -r "${depfile}" || warn "    pip install failed"
    [ -x "${venv}/bin/playwright" ] && {
        "${venv}/bin/playwright" install chromium >/dev/null 2>&1 \
            || warn "    playwright chromium install failed (non-fatal)"
    }
    python3 -c "import hashlib; print(hashlib.sha256(open('${depfile}','rb').read()).hexdigest())" \
        > "${state_dir}/.setup-complete"
}

provision_system() {
    local pdir="$1" depsrc="$2"
    if [ -n "${depsrc}" ]; then
        local depfile="${pdir}/${depsrc}"
        if [ -f "${depfile}" ]; then
            if [[ "${depsrc}" == *.txt ]]; then
                log "  pip install -r ${depfile} (system)"
                python3 -m pip install --quiet ${PIP_BREAK_FLAG} -r "${depfile}" \
                    || warn "    pip install failed"
            else
                local depdir; depdir="$(dirname "${depfile}")"
                log "  pip install -e ${depdir} (system, editable)"
                python3 -m pip install --quiet ${PIP_BREAK_FLAG} -e "${depdir}" \
                    || warn "    editable install failed"
            fi
        fi
    fi
    # Walk siblings under servers/* (e.g. agency-system has multiple MCP packages).
    if [ -d "${pdir}/servers" ]; then
        local s
        for s in "${pdir}/servers"/*/; do
            [ -f "${s}pyproject.toml" ] || continue
            [ -n "${depsrc}" ] && [ "${pdir}/${depsrc}" = "${s}pyproject.toml" ] && continue
            log "  pip install -e ${s} (sibling MCP)"
            python3 -m pip install --quiet ${PIP_BREAK_FLAG} -e "${s}" \
                || warn "    editable install failed"
        done
    fi
}

provision_pyvenv() {
    # Args: state-dir-name, plugin-dir, dep-source (pyproject.toml path)
    # Creates a dedicated venv, installs the pyproject AND every sibling
    # under <plugin>/servers/*/pyproject.toml editably, then symlinks
    # ~/.local/bin/python → the venv's python3 so plugins whose .mcp.json
    # uses bare `python` (like agency-system) find the right packages.
    # Avoids the Debian PyJWT-RECORD-not-found wall that breaks
    # --break-system-packages installs.
    local state_name="$1" pdir="$2" depsrc="$3"
    local state_dir="${HOME}/.${state_name}"
    local venv="${state_dir}/venv"
    mkdir -p "${state_dir}"
    [ -x "${venv}/bin/python3" ] || { log "  creating venv ${venv}"; python3 -m venv "${venv}"; }
    "${venv}/bin/pip" install --quiet --upgrade pip wheel setuptools

    # Editable install of the primary package.
    if [ -n "${depsrc}" ] && [ -f "${pdir}/${depsrc}" ]; then
        local depdir; depdir="$(dirname "${pdir}/${depsrc}")"
        log "  pip install -e ${depdir} (venv)"
        "${venv}/bin/pip" install --quiet -e "${depdir}" \
            || warn "    editable install failed"
    fi
    # Walk sibling server packages.
    if [ -d "${pdir}/servers" ]; then
        local s
        for s in "${pdir}/servers"/*/; do
            [ -f "${s}pyproject.toml" ] || continue
            [ -n "${depsrc}" ] && [ "${pdir}/${depsrc}" = "${s}pyproject.toml" ] && continue
            log "  pip install -e ${s} (venv sibling)"
            "${venv}/bin/pip" install --quiet -e "${s}" \
                || warn "    editable install failed for ${s}"
        done
    fi

    # Make bare `python` resolve to this venv's python. A symlink doesn't
    # work — Python's venv-detection walks the dir of argv[0] looking for
    # pyvenv.cfg, and the link path (e.g. ~/.local/bin/) has none.
    # A small exec-wrapper preserves the venv interpreter's argv[0], which
    # is what venv detection needs.
    #
    # rm first: a previous run may have left a SYMLINK at this path; a
    # `cat > symlink` writes through and corrupts the link target (the
    # venv python binary).
    mkdir -p "${HOME}/.local/bin"
    rm -f "${HOME}/.local/bin/python"
    cat > "${HOME}/.local/bin/python" <<EOF
#!/usr/bin/env bash
exec "${venv}/bin/python3" "\$@"
EOF
    chmod +x "${HOME}/.local/bin/python"
    log "  wrote python wrapper ${HOME}/.local/bin/python → ${venv}/bin/python3"
}

provision_npm() {
    local pdir="$1"
    if [ ! -f "${pdir}/package.json" ]; then
        warn "  ${pdir}/package.json missing"
        return
    fi
    log "  npm install in ${pdir}"
    ( cd "${pdir}" && npm install --no-audit --no-fund --loglevel=error 2>&1 | tail -2 ) \
        || warn "    npm install reported issues"
}

write_bitwize_config() {
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

for entry in "${INSTALLED_REFS[@]}"; do
    IFS='|' read -r REF PDIR DEPMODE DEPSRC POST _ _ <<<"${entry}"
    log "${REF} → mode=${DEPMODE}"
    case "${DEPMODE}" in
        venv:*)   provision_venv "${DEPMODE#venv:}" "${PDIR}" "${DEPSRC}" ;;
        pyvenv:*) provision_pyvenv "${DEPMODE#pyvenv:}" "${PDIR}" "${DEPSRC}" ;;
        system)   provision_system "${PDIR}" "${DEPSRC}" ;;
        npm)      provision_npm "${PDIR}" ;;
        uvx|none) log "  (no eager install)" ;;
        *)        warn "  unknown dep_mode '${DEPMODE}'" ;;
    esac
    if [ -n "${POST}" ] && declare -F "${POST}" >/dev/null 2>&1; then
        "${POST}"
    fi
done

# =============================================================================
# Phase 6 — optional AIRIS Docker stack
# =============================================================================
if [ "${AIRIS_GATEWAY}" = "1" ]; then
    log "Phase 6: AIRIS Docker stack (AIRIS_GATEWAY=1)"
    if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1 \
       && docker compose version >/dev/null 2>&1; then
        if [ ! -x "${HOME}/.local/bin/airis-gateway" ]; then
            curl -fsSL https://raw.githubusercontent.com/agiletec-inc/airis-mcp-gateway/main/install.sh \
                | bash < /dev/null 2>&1 | tail -3 || warn "  AIRIS install.sh failed"
        fi
        if [ -x "${HOME}/.local/bin/airis-gateway" ]; then
            "${HOME}/.local/bin/airis-gateway" up < /dev/null 2>&1 | tail -2 || true
            json_merge "${USER_CLAUDE_JSON}" \
                '
                .mcpServers //= {}
                | .mcpServers["airis-mcp-gateway"] = {"type": "http", "url": "http://localhost:9400/mcp/"}
                '
        fi
    else
        warn "  docker/compose unavailable — skipping"
    fi
else
    log "Phase 6: AIRIS Docker stack skipped (set AIRIS_GATEWAY=1)"
fi

# =============================================================================
# Phase 7 — verification
# =============================================================================
log "Phase 7: verification"
FAIL=0
fail() { warn "VERIFY: $*"; FAIL=$((FAIL + 1)); }

for entry in "${INSTALLED_REFS[@]}"; do
    IFS='|' read -r REF PDIR DEPMODE _ _ _ _ <<<"${entry}"
    [ -d "${PDIR}" ] || fail "plugin dir missing: ${REF} (${PDIR})"
    [ -f "${PDIR}/.claude-plugin/plugin.json" ] || fail "plugin.json missing: ${REF}"
    jq -e ".enabledPlugins[\"${REF}\"]" "${PROJECT_SETTINGS}" >/dev/null 2>&1 \
        || fail "${REF} not in project enabledPlugins"
    jq -e ".plugins[\"${REF}\"]" "${INSTALLED_PLUGINS}" >/dev/null 2>&1 \
        || fail "${REF} not in installed_plugins.json"
    case "${DEPMODE}" in
        venv:*)
            VPY="${HOME}/.${DEPMODE#venv:}/venv/bin/python3"
            [ -x "${VPY}" ] || fail "venv python missing: ${VPY}"
            ;;
        pyvenv:*)
            VPY="${HOME}/.${DEPMODE#pyvenv:}/venv/bin/python3"
            [ -x "${VPY}" ] || fail "venv python missing: ${VPY}"
            # The venv should be importable; ALSO bare `python` must
            # resolve to it via the ~/.local/bin/python symlink.
            python -c "import agency_mcp" >/dev/null 2>&1 \
                || fail "import agency_mcp failed via bare 'python' (PATH=${PATH})"
            ;;
        system)
            if [ "${REF}" = "agency-system@agency-marketplace" ]; then
                python3 -c "import agency_mcp" >/dev/null 2>&1 \
                    || fail "import agency_mcp failed (system Python)"
            fi
            ;;
        npm)
            [ -d "${PDIR}/node_modules" ] || fail "npm deps not installed: ${REF}"
            ;;
    esac
done

for row in "${STANDALONE_MCPS[@]}"; do
    IFS='|' read -r M_NAME _ _ _ <<<"${row}"
    M_NAME="$(printf '%s' "${M_NAME}" | xargs)"
    jq -e ".mcpServers[\"${M_NAME}\"]" "${USER_CLAUDE_JSON}" >/dev/null 2>&1 \
        || fail "standalone MCP ${M_NAME} not in ~/.claude.json"
done

[ "${FAIL}" -gt 0 ] && die "${FAIL} verification check(s) failed"

log "DONE — restart your Claude Code session to load the new plugins."
log "  Installed:"
for entry in "${INSTALLED_REFS[@]}"; do
    IFS='|' read -r REF _ _ _ _ _ _ <<<"${entry}"
    log "    - ${REF}"
done
log "  Standalone MCPs:"
for row in "${STANDALONE_MCPS[@]}"; do
    IFS='|' read -r M_NAME M_TRANSPORT _ _ <<<"${row}"
    log "    - $(printf '%s' "${M_NAME}" | xargs) (${M_TRANSPORT})"
done
[ "${AIRIS_GATEWAY}" = "1" ] && log "    - airis-mcp-gateway (http :9400)"
