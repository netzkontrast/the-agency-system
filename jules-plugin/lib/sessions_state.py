import argparse
import datetime
import fcntl
import json
import os
import sys

"""REGISTRY_PATH resolves to ${CLAUDE_PLUGIN_DATA}/sessions.json if CLAUDE_PLUGIN_DATA is set;
otherwise it falls back to a .jules directory under the user's home."""
plugin_data_dir = os.environ.get("CLAUDE_PLUGIN_DATA")
if plugin_data_dir:
    REGISTRY_PATH = os.path.join(plugin_data_dir, "sessions.json")
else:
    REGISTRY_PATH = os.path.join(os.path.expanduser("~"), ".jules", "sessions.json")


def load():
    if not os.path.exists(os.path.dirname(REGISTRY_PATH)):
        os.makedirs(os.path.dirname(REGISTRY_PATH), exist_ok=True)
    if not os.path.exists(REGISTRY_PATH):

        return []
    try:
        with open(REGISTRY_PATH, 'r') as f:
            fcntl.flock(f, fcntl.LOCK_SH)
            try:
                data = json.load(f)
                return data.get("sessions", [])
            except json.JSONDecodeError:
                return []
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)
    except FileNotFoundError:
        return []

def save(entries):
    data = {"sessions": entries}
    with open(REGISTRY_PATH, 'a+') as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            f.seek(0)
            f.truncate()
            json.dump(data, f, indent=2)
            f.write('\n')
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)

def upsert(entry):
    with open(REGISTRY_PATH, 'a+') as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            f.seek(0)
            try:
                content = f.read()
                if not content:
                    entries = []
                else:
                    data = json.loads(content)
                    entries = data.get("sessions", [])
            except json.JSONDecodeError:
                entries = []
            
            idx = -1
            for i, e in enumerate(entries):
                if e.get("id") == entry.get("id"):
                    idx = i
                    break
            
            now = datetime.datetime.now(datetime.timezone.utc).isoformat()
            # replace +00:00 with Z if any, or just use it as is.
            if now.endswith("+00:00"):
                now = now[:-6] + "Z"
            
            if idx >= 0:
                entries[idx].update(entry)
                entries[idx]["updated_at"] = now
            else:
                if "created_at" not in entry:
                    entry["created_at"] = now
                entry["updated_at"] = now
                entries.append(entry)
            
            f.seek(0)
            f.truncate()
            json.dump({"sessions": entries}, f, indent=2)
            f.write('\n')
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)

def resolve(id_or_alias):
    for e in load():
        if e.get("id") == id_or_alias or e.get("alias") == id_or_alias:
            return e.get("id")
    return None

def find(predicate):
    return [e for e in load() if predicate(e)]


def register_session(id, title="", source="", branch="", alias=None, url="", status=None):
    """Python API for callers (e.g. the MCP server) to upsert a session
    without going through the CLI. Idempotent: re-registering the same id
    updates the existing entry rather than duplicating it. Safe under
    concurrent writers — uses the same fcntl flock as the CLI path."""
    entry = {"id": id}
    if title: entry["title"] = title
    if source: entry["source"] = source
    if branch: entry["branch"] = branch
    if alias: entry["alias"] = alias
    if url: entry["url"] = url
    if status: entry["status"] = status
    upsert(entry)
    matches = find(lambda x: x.get("id") == id)
    return matches[0] if matches else entry


def main():
    parser = argparse.ArgumentParser(description="Jules sessions registry")
    subparsers = parser.add_subparsers(dest="command")
    subparsers.required = True

    # register
    parser_reg = subparsers.add_parser("register", help="Register a new session")
    parser_reg.add_argument("--id", required=True)
    parser_reg.add_argument("--title", required=True)
    parser_reg.add_argument("--alias")
    parser_reg.add_argument("--source")
    parser_reg.add_argument("--branch")
    parser_reg.add_argument("--url")

    # list
    parser_list = subparsers.add_parser("list", help="List sessions")
    parser_list.add_argument("--json", action="store_true")

    # get
    parser_get = subparsers.add_parser("get", help="Get a session")
    parser_get.add_argument("id_or_alias")

    # update
    parser_upd = subparsers.add_parser("update", help="Update session status")
    parser_upd.add_argument("id_or_alias")
    parser_upd.add_argument("--status", required=True)

    # forget
    parser_for = subparsers.add_parser("forget", help="Remove a session")
    parser_for.add_argument("id_or_alias")

    # resolve
    parser_res = subparsers.add_parser("resolve", help="Resolve alias or id to canonical id")
    parser_res.add_argument("id_or_alias")

    args = parser.parse_args()

    if args.command == "register":
        entry = {"id": args.id, "title": args.title}
        if args.alias: entry["alias"] = args.alias
        if args.source: entry["source"] = args.source
        if args.branch: entry["branch"] = args.branch
        if args.url: entry["url"] = args.url
        upsert(entry)
        print(f"Registered session {args.id}")

    elif args.command == "list":
        entries = load()
        if args.json:
            print(json.dumps({"sessions": entries}, indent=2))
        else:
            for e in entries:
                alias_str = f" [{e['alias']}]" if e.get("alias") else ""
                status_str = f" - {e['status']}" if e.get("status") else ""
                print(f"{e['id']}{alias_str}: {e.get('title', '')}{status_str}")

    elif args.command == "get":
        session_id = resolve(args.id_or_alias)
        if not session_id:
            print(f"Session not found: {args.id_or_alias}", file=sys.stderr)
            sys.exit(1)
        res = find(lambda x: x.get("id") == session_id)
        if res:
            print(json.dumps(res[0], indent=2))

    elif args.command == "update":
        session_id = resolve(args.id_or_alias)
        if not session_id:
            print(f"Session not found: {args.id_or_alias}", file=sys.stderr)
            sys.exit(1)
        upsert({"id": session_id, "status": args.status})
        print(f"Updated session {session_id} status to {args.status}")

    elif args.command == "forget":
        session_id = resolve(args.id_or_alias)
        if not session_id:
            print(f"Session not found: {args.id_or_alias}", file=sys.stderr)
            sys.exit(1)
        
        with open(REGISTRY_PATH, 'a+') as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            try:
                f.seek(0)
                content = f.read()
                if not content:
                    entries = []
                else:
                    try:
                        data = json.loads(content)
                        entries = data.get("sessions", [])
                    except json.JSONDecodeError:
                        entries = []
                
                new_entries = [e for e in entries if e.get("id") != session_id]
                
                f.seek(0)
                f.truncate()
                json.dump({"sessions": new_entries}, f, indent=2)
                f.write('\n')
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)
        print(f"Forgot session {session_id}")

    elif args.command == "resolve":
        session_id = resolve(args.id_or_alias)
        if not session_id:
            print(f"Session not found: {args.id_or_alias}", file=sys.stderr)
            sys.exit(1)
        print(session_id)

if __name__ == "__main__":
    main()
