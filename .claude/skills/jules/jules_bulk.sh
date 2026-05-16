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

Subcommands:
  fanout FILE          FILE is a JSON or YAML list of {alias, title, prompt} entries; creates one session per entry
  dashboard            Prints a compact table of all active sessions: alias | id | state | title
  approve-awaiting     Approves every session currently in AWAITING_PLAN_APPROVAL
  stop-all [--force]   Cancels every non-terminal session; prompts "yes/no" first unless --force given
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

    # Convert YAML to JSON if necessary, or just format JSON
    if command -v yq >/dev/null 2>&1; then
        yq -o=json '.' "$file" > "$temp_json"
    elif command -v python3 >/dev/null 2>&1; then
        python3 -c "import sys, json, yaml; json.dump(yaml.safe_load(sys.stdin), sys.stdout)" < "$file" > "$temp_json"
    else
        echo "ERROR: yq or python3+yaml is required to parse FILE." >&2
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
        
        local payload
        payload=$(jq -n \
            --arg title "$title" \
            --arg prompt "$prompt" \
            --arg branch "$branch" \
            --arg source "$DEFAULT_SOURCE" \
            '{
                title: $title,
                prompt: $prompt,
                requirePlanApproval: true,
                sourceContext: {
                    source: $source,
                    githubRepoContext: {
                        startingBranch: $branch
                    }
                }
            }')
            
        local resp
        resp=$(mktemp)
        local http_code
        http_code=$(curl -sS -o "$resp" -w "%{http_code}" -X POST "$JULES_API_BASE_URL/v1alpha/sessions" \
            -H "x-goog-api-key: $JULES_API_KEY" \
            -H "Content-Type: application/json" \
            -d "$payload")
            
        if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
            local session_name
            session_name=$(jq -r '.name' "$resp")
            local session_id="${session_name#sessions/}"
            echo "Session created: $session_id"
            
            python3 "$DIR/sessions_state.py" register --id "$session_id" --title "$title" --alias "$alias"
        else
            echo "ERROR: Failed to create session ($http_code). Response:" >&2
            cat "$resp" >&2
            echo "" >&2
        fi
        rm -f "$resp"
    done
}

cmd_dashboard() {
    local registry_json
    registry_json=$(python3 "$DIR/sessions_state.py" list --json)

    if [ -z "$registry_json" ] || [ "$registry_json" = "[]" ] || [ "$registry_json" = "null" ]; then
        echo "No sessions in registry."
        return 0
    fi

    local temp_out
    temp_out=$(mktemp)
    trap 'rm -f "$temp_out"' EXIT

    echo "$registry_json" | jq -c '.[]' | while read -r item; do
        local id alias state title temp_resp http_code
        id=$(echo "$item" | jq -r '.id')
        alias=$(echo "$item" | jq -r '.alias')
        
        temp_resp=$(mktemp)
        http_code=$(curl -sS -o "$temp_resp" -w "%{http_code}" "$JULES_API_BASE_URL/v1alpha/sessions/$id" \
            -H "x-goog-api-key: $JULES_API_KEY")
            
        if [ "$http_code" -eq 200 ]; then
            state=$(jq -r '.state' "$temp_resp")
            title=$(jq -r '.title' "$temp_resp")
        else
            state="ERROR_$http_code"
            title="<unknown>"
        fi
        rm -f "$temp_resp"
        
        printf "%s\t%s\t%s\t%s\n" "$alias" "$id" "$state" "$title" >> "$temp_out"
    done

    if [ -s "$temp_out" ]; then
        printf "%s\t%s\t%s\t%s\n" "ALIAS" "ID" "STATE" "TITLE" | column -t -s $'\t'
        echo "--------------------------------------------------------------------------------"
        column -t -s $'\t' "$temp_out"
    fi
}

cmd_approve_awaiting() {
    local registry_json
    registry_json=$(python3 "$DIR/sessions_state.py" list --json)
    
    if [ -z "$registry_json" ] || [ "$registry_json" = "[]" ] || [ "$registry_json" = "null" ]; then
        echo "No sessions in registry."
        return 0
    fi

    local to_approve=$(mktemp)
    trap 'rm -f "$to_approve"' EXIT

    echo "Checking session states..."
    echo "$registry_json" | jq -c '.[]' | while read -r item; do
        local id temp_resp http_code state
        id=$(echo "$item" | jq -r '.id')
        
        temp_resp=$(mktemp)
        http_code=$(curl -sS -o "$temp_resp" -w "%{http_code}" "$JULES_API_BASE_URL/v1alpha/sessions/$id" \
            -H "x-goog-api-key: $JULES_API_KEY")
            
        if [ "$http_code" -eq 200 ]; then
            state=$(jq -r '.state' "$temp_resp")
            if [ "$state" = "AWAITING_PLAN_APPROVAL" ]; then
                echo "$id" >> "$to_approve"
            fi
        fi
        rm -f "$temp_resp"
    done

    if [ ! -s "$to_approve" ]; then
        echo "No sessions are currently AWAITING_PLAN_APPROVAL."
        return 0
    fi

    echo "Approving the following sessions in parallel:"
    cat "$to_approve"

    # Export variables needed by the subshell for xargs
    export JULES_API_KEY
    export JULES_API_BASE_URL

    approve_session() {
        local id="$1"
        local http_code
        http_code=$(curl -sS -o /dev/null -w "%{http_code}" -X POST "$JULES_API_BASE_URL/v1alpha/sessions/$id:approvePlan" \
            -H "x-goog-api-key: $JULES_API_KEY" \
            -H "Content-Type: application/json" \
            -d '{}')
        if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
            echo "Approved: $id"
        else
            echo "Failed to approve: $id (HTTP $http_code)" >&2
        fi
    }
    export -f approve_session

    cat "$to_approve" | xargs -P 4 -I {} bash -c 'approve_session "{}"'
}

cmd_stop_all() {
    local force=false
    if [ "$1" = "--force" ]; then
        force=true
    fi

    local registry_json
    registry_json=$(python3 "$DIR/sessions_state.py" list --json)
    
    if [ -z "$registry_json" ] || [ "$registry_json" = "[]" ] || [ "$registry_json" = "null" ]; then
        echo "No sessions in registry."
        return 0
    fi

    local to_stop=$(mktemp)
    trap 'rm -f "$to_stop"' EXIT

    echo "Finding active sessions..."
    echo "$registry_json" | jq -c '.[]' | while read -r item; do
        local id temp_resp http_code state
        id=$(echo "$item" | jq -r '.id')
        
        temp_resp=$(mktemp)
        http_code=$(curl -sS -o "$temp_resp" -w "%{http_code}" "$JULES_API_BASE_URL/v1alpha/sessions/$id" \
            -H "x-goog-api-key: $JULES_API_KEY")
            
        if [ "$http_code" -eq 200 ]; then
            state=$(jq -r '.state' "$temp_resp")
            # Exclude terminal states. Assuming COMPLETED, FAILED, and potentially deleted/not found.
            if [ "$state" != "COMPLETED" ] && [ "$state" != "FAILED" ] && [ "$state" != "STATE_UNSPECIFIED" ]; then
                echo "$id" >> "$to_stop"
            fi
        fi
        rm -f "$temp_resp"
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
        local http_code
        http_code=$(curl -sS -o /dev/null -w "%{http_code}" -X DELETE "$JULES_API_BASE_URL/v1alpha/sessions/$id" \
            -H "x-goog-api-key: $JULES_API_KEY")
        if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
            echo "Stopped: $id"
        else
            echo "Failed to stop: $id (HTTP $http_code)" >&2
        fi
    done
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
    *)
        usage
        ;;
esac
