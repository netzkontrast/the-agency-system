#!/bin/bash
set -eo pipefail

if [ -z "$JULES_API_KEY" ]; then
    echo "ERROR: JULES_API_KEY is not set." >&2
    exit 1
fi

JULES_API_BASE_URL="${JULES_API_BASE_URL:-https://jules.googleapis.com}"
DEFAULT_SOURCE="${JULES_DEFAULT_SOURCE:-sources/github/netzkontrast/the-agency-system}"
DEFAULT_BRANCH="$(git branch --show-current 2>/dev/null || echo 'main')"

# Base directory for the script to find sessions_state.py
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

usage() {
    cat << 'USAGE'
Usage: jules_bulk.sh <subcommand> [args...]

This script is a thin facade over the MCP server's Python tools (jules-mcp/server.py).

Subcommands:
  fanout FILE          FILE is a JSON or YAML list of {alias, title, prompt} entries; creates one session per entry
  dashboard            Prints a compact table of all active sessions: alias | id | state | title
  approve-awaiting     Approves every session currently in AWAITING_PLAN_APPROVAL
  stop-all [--force]   Cancels every non-terminal session; prompts "yes/no" first unless --force given
  quota                Prints the Jules daily session quota usage
USAGE
    exit 1
}

cmd_fanout() {
    local file="$1"
    if [ -z "$file" ] || [ ! -f "$file" ]; then
        echo "ERROR: fanout requires a valid FILE argument." >&2
        usage
    fi

    local temp_json
    temp_json=$(mktemp)
    trap 'rm -f "$temp_json"' EXIT

    # Accept JSON directly; otherwise convert YAML to JSON via Python (always available).
    if jq -e . "$file" >/dev/null 2>&1; then
        cp "$file" "$temp_json"
    elif command -v python3 >/dev/null 2>&1; then
        python3 -c "import sys, json, yaml; json.dump(yaml.safe_load(open(sys.argv[1])), sys.stdout)" \
            "$file" > "$temp_json" || {
                echo "ERROR: could not parse $file as JSON or YAML." >&2; exit 1; }
    else
        echo "ERROR: python3 with PyYAML required for YAML input." >&2
        exit 1
    fi

    jq -c '.[]' "$temp_json" | while read -r entry; do
        local alias title prompt branch
        alias=$(echo "$entry" | jq -r '.alias // empty')
        title=$(echo "$entry" | jq -r '.title // empty')
        prompt=$(echo "$entry" | jq -r '.prompt // empty')
        branch=$(echo "$entry" | jq -r '.branch // empty')

        if [ -z "$alias" ] || [ -z "$title" ] || [ -z "$prompt" ]; then
            echo "WARN: Skipping entry with missing alias, title, or prompt: $entry" >&2
            continue
        fi
        
        if [ -z "$branch" ]; then
            branch="$DEFAULT_BRANCH"
        fi

        echo "Creating session for alias: $alias ..."
        
        export JULES_TEMP_PROMPT="$prompt"
        export JULES_TEMP_TITLE="$title"
        export JULES_TEMP_BRANCH="$branch"
        export JULES_TEMP_SOURCE="$DEFAULT_SOURCE"
        export SCRIPT_DIR="$DIR"

        local resp
        resp=$(python3 - <<'PY'
import importlib.util, json, os
server_path = os.path.abspath(os.path.join(os.environ.get('SCRIPT_DIR', '.'), '..', '..', 'mcp', 'jules-mcp', 'server.py'))
spec = importlib.util.spec_from_file_location('jm', server_path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
try:
    res = mod.jules_create(
        prompt=os.environ['JULES_TEMP_PROMPT'],
        source=os.environ['JULES_TEMP_SOURCE'],
        starting_branch=os.environ['JULES_TEMP_BRANCH'],
        title=os.environ.get('JULES_TEMP_TITLE', ''),
        require_plan_approval=True
    )
    print(json.dumps({"ok": True, "res": res}))
except Exception as e:
    print(json.dumps({"ok": False, "err": str(e)}))
PY
        )
        
        local ok=$(echo "$resp" | jq -r '.ok')
        if [ "$ok" = "true" ]; then
            local session_id
            session_id=$(echo "$resp" | jq -r '.res.name // .res.id // empty' | sed 's|^sessions/||')
            echo "Session created: $session_id"
            
            python3 "$DIR/sessions_state.py" register --id "$session_id" --title "$title" --alias "$alias"
        else
            local err=$(echo "$resp" | jq -r '.err // "Unknown error"')
            echo "ERROR: Failed to create session. Error: $err" >&2
        fi
    done
}

cmd_dashboard() {
    local registry_json
    registry_json=$(python3 "$DIR/sessions_state.py" list --json)

    if [ -z "$registry_json" ] || [ "$registry_json" = "[]" ] || [ "$registry_json" = "null" ] || [ "$registry_json" = '{"sessions": []}' ]; then
        echo "No sessions in registry."
        return 0
    fi

    local temp_out
    temp_out=$(mktemp)
    trap 'rm -f "$temp_out"' EXIT

    export SCRIPT_DIR="$DIR"
    local all_sessions_json
    all_sessions_json=$(python3 - <<'PY'
import importlib.util, json, os
server_path = os.path.abspath(os.path.join(os.environ.get('SCRIPT_DIR', '.'), '..', '..', 'mcp', 'jules-mcp', 'server.py'))
spec = importlib.util.spec_from_file_location('jm', server_path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
try:
    print(json.dumps(mod.jules_status_all()))
except Exception as e:
    print(json.dumps({"error": str(e)}))
PY
    )

    # sessions_state.py list --json emits {"sessions": [...]}; tolerate bare arrays too.
    echo "$registry_json" | jq -c 'if type=="array" then .[] else .sessions[]? end' | while read -r item; do
        local id alias state title
        id=$(echo "$item" | jq -r '.id')
        alias=$(echo "$item" | jq -r '.alias')
        
        # Look up session info from bulk status JSON
        local match
        match=$(echo "$all_sessions_json" | jq -c --arg id "$id" '.sessions[]? | select(.id == $id)')
        
        if [ -n "$match" ]; then
            state=$(echo "$match" | jq -r '.state // "STATE_UNSPECIFIED"')
            title=$(echo "$match" | jq -r '.title // "<unknown>"')
        else
            state="UNKNOWN"
            title="<not found>"
        fi
        
        printf "%s\t%s\t%s\t%s\n" "$alias" "$id" "$state" "$title" >> "$temp_out"
    done

    if [ -s "$temp_out" ]; then
        {
            printf "%s\t%s\t%s\t%s\n" "ALIAS" "ID" "STATE" "TITLE"
            cat "$temp_out"
        } | awk -F'\t' '
            { for (i=1;i<=NF;i++){ if(length($i)>w[i]) w[i]=length($i); rows[NR,i]=$i; cols=NF } }
            END {
                for (r=1;r<=NR;r++){
                    line=""
                    for (i=1;i<=cols;i++){
                        sep = (i==cols ? "" : "  ")
                        line = line sprintf("%-*s%s", w[i], rows[r,i], sep)
                    }
                    print line
                    if (r==1) {
                        sepline=""
                        for (i=1;i<=cols;i++){ for(j=0;j<w[i];j++) sepline=sepline"-"; if(i<cols) sepline=sepline"  " }
                        print sepline
                    }
                }
            }'
    fi
}

cmd_approve_awaiting() {
    echo "Checking session states and approving..."
    export SCRIPT_DIR="$DIR"
    local resp
    resp=$(python3 - <<'PY'
import importlib.util, json, os
server_path = os.path.abspath(os.path.join(os.environ.get('SCRIPT_DIR', '.'), '..', '..', 'mcp', 'jules-mcp', 'server.py'))
spec = importlib.util.spec_from_file_location('jm', server_path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
try:
    print(json.dumps(mod.jules_approve_awaiting()))
except Exception as e:
    print(json.dumps({"error": str(e)}))
PY
    )

    local err
    err=$(echo "$resp" | jq -r '.error // empty')
    if [ -n "$err" ]; then
        echo "ERROR: Failed to run approve-awaiting. Error: $err" >&2
        return 1
    fi

    local approved_count skipped_count errors_count
    approved_count=$(echo "$resp" | jq -r '.approved | length')
    skipped_count=$(echo "$resp" | jq -r '.skipped | length')
    errors_count=$(echo "$resp" | jq -r '.errors | length')

    if [ "$approved_count" -eq 0 ] && [ "$errors_count" -eq 0 ]; then
        echo "No sessions are currently AWAITING_PLAN_APPROVAL."
        return 0
    fi

    if [ "$approved_count" -gt 0 ]; then
        echo "Approved the following sessions:"
        echo "$resp" | jq -r '.approved[]'
    fi

    if [ "$errors_count" -gt 0 ]; then
        echo "Failed to approve the following sessions:" >&2
        echo "$resp" | jq -r '.errors[] | "\(.id): \(.error)"' >&2
    fi
}

cmd_stop_all() {
    local force=false
    if [ "$1" = "--force" ]; then
        force=true
    fi

    local registry_json
    registry_json=$(python3 "$DIR/sessions_state.py" list --json)
    
    if [ -z "$registry_json" ] || [ "$registry_json" = "[]" ] || [ "$registry_json" = "null" ] || [ "$registry_json" = '{"sessions": []}' ]; then
        echo "No sessions in registry."
        return 0
    fi

    local to_stop=$(mktemp)
    trap 'rm -f "$to_stop"' EXIT

    echo "Finding active sessions..."
    export SCRIPT_DIR="$DIR"
    local all_sessions_json
    all_sessions_json=$(python3 - <<'PY'
import importlib.util, json, os
server_path = os.path.abspath(os.path.join(os.environ.get('SCRIPT_DIR', '.'), '..', '..', 'mcp', 'jules-mcp', 'server.py'))
spec = importlib.util.spec_from_file_location('jm', server_path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
try:
    print(json.dumps(mod.jules_status_all()))
except Exception as e:
    print(json.dumps({"error": str(e)}))
PY
    )

    # sessions_state.py list --json emits {"sessions": [...]}; tolerate bare arrays too.
    echo "$registry_json" | jq -c 'if type=="array" then .[] else .sessions[]? end' | while read -r item; do
        local id state
        id=$(echo "$item" | jq -r '.id')
        
        # Look up session info from bulk status JSON
        local match
        match=$(echo "$all_sessions_json" | jq -c --arg id "$id" '.sessions[]? | select(.id == $id)')
        
        if [ -n "$match" ]; then
            state=$(echo "$match" | jq -r '.state // "STATE_UNSPECIFIED"')
            # Exclude terminal states. Assuming COMPLETED, FAILED, and potentially deleted/not found.
            if [ "$state" != "COMPLETED" ] && [ "$state" != "FAILED" ] && [ "$state" != "STATE_UNSPECIFIED" ]; then
                echo "$id" >> "$to_stop"
            fi
        fi
    done

    if [ ! -s "$to_stop" ]; then
        echo "No active sessions found to stop."
        return 0
    fi

    echo "The following active sessions will be stopped:"
    cat "$to_stop"
    echo ""

    if [ "$force" != "true" ]; then
        read -p "Are you sure you want to stop all these sessions? (yes/no): " confirm
        if [ "$confirm" != "yes" ]; then
            echo "Operation cancelled."
            return 0
        fi
    fi

    cat "$to_stop" | while read -r id; do
        export JULES_TEMP_ID="$id"
        local stop_resp
        stop_resp=$(python3 - <<'PY'
import importlib.util, json, os
server_path = os.path.abspath(os.path.join(os.environ.get('SCRIPT_DIR', '.'), '..', '..', 'mcp', 'jules-mcp', 'server.py'))
spec = importlib.util.spec_from_file_location('jm', server_path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
try:
    res = mod.jules_stop(session_id=os.environ['JULES_TEMP_ID'])
    print(json.dumps({"ok": True, "res": res}))
except Exception as e:
    print(json.dumps({"ok": False, "err": str(e)}))
PY
        )
        local ok=$(echo "$stop_resp" | jq -r '.ok')
        if [ "$ok" = "true" ]; then
            echo "Stopped: $id"
        else
            local err=$(echo "$stop_resp" | jq -r '.err // "Unknown error"')
            echo "Failed to stop: $id (Error: $err)" >&2
        fi
    done
}

cmd_quota() {
    export SCRIPT_DIR="$DIR"
    local resp
    resp=$(python3 - <<'PY'
import importlib.util, json, os
server_path = os.path.abspath(os.path.join(os.environ.get('SCRIPT_DIR', '.'), '..', '..', 'mcp', 'jules-mcp', 'server.py'))
spec = importlib.util.spec_from_file_location('jm', server_path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
try:
    print(json.dumps(mod.jules_quota()))
except Exception as e:
    print(json.dumps({"error": str(e)}))
PY
    )
    
    local err
    err=$(echo "$resp" | jq -r '.error // empty')
    if [ -n "$err" ]; then
        echo "ERROR: Failed to fetch quota. Error: $err" >&2
        return 1
    fi

    local used remaining active
    used=$(echo "$resp" | jq -r '.used_today // 0')
    remaining=$(echo "$resp" | jq -r '.remaining_today // 0')
    active=$(echo "$resp" | jq -r '.active_today // 0')

    echo "Jules quota: $used/100 used, $remaining left, $active active"
}

case "$1" in
    fanout)
        shift
        cmd_fanout "$@"
        ;;
    dashboard)
        cmd_dashboard
        ;;
    approve-awaiting)
        cmd_approve_awaiting
        ;;
    stop-all)
        shift
        cmd_stop_all "$@"
        ;;
    quota)
        cmd_quota
        ;;
    *)
        usage
        ;;
esac
