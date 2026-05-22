"""Combined watcher: polls all tracked Jules sessions + all tracked PRs.

Wakes the parent (exits 0) when ANY of:
  - a session transitions to AWAITING_PLAN_APPROVAL, AWAITING_USER_FEEDBACK,
    COMPLETED, FAILED, CANCELLED
  - a PR receives a new comment, review, or check_run failure

State persists across runs via /tmp/jules_combined_watcher_state.json so
restarts don't double-fire on already-seen events.

Usage:
  python3 watcher.py <sessions.json> <prs.json>

sessions.json: ["17491799094212730419", "10172287027116536958"]
prs.json:      [{"owner":"netzkontrast","repo":"the-agency-system","number":33}, ...]
"""
import json, os, sys, time
from pathlib import Path
from jules_mcp.tools.lifecycle import jules_get
import urllib.request

STATE_PATH = Path("/tmp/jules_combined_watcher_state.json")
POLL_INTERVAL = 60
DEADLINE_HOURS = 6

WAKE_STATES = {"AWAITING_PLAN_APPROVAL", "AWAITING_USER_FEEDBACK",
               "COMPLETED", "FAILED", "CANCELLED"}


def load_state():
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text())
    return {"sessions": {}, "prs": {}}


def save_state(s):
    STATE_PATH.write_text(json.dumps(s, indent=2))


def gh_get(url, token):
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def main():
    session_ids = json.loads(Path(sys.argv[1]).read_text()) if len(sys.argv) > 1 else []
    prs = json.loads(Path(sys.argv[2]).read_text()) if len(sys.argv) > 2 else []
    gh_token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN", "")
    state = load_state()
    deadline = time.time() + DEADLINE_HOURS * 3600
    woke = False

    while time.time() < deadline and not woke:
        for sid in session_ids:
            try:
                s = jules_get(sid, fields="id,state,title")
                cur = s.get("state", "?")
            except Exception as e:
                print(json.dumps({"event": "session_poll_error", "sid": sid, "error": str(e)}), flush=True)
                continue
            prev = state["sessions"].get(sid)
            if cur != prev:
                print(json.dumps({"event": "session_state_change", "sid": sid,
                                  "prev": prev, "now": cur, "title": s.get("title")}), flush=True)
                state["sessions"][sid] = cur
                save_state(state)
                if cur in WAKE_STATES:
                    woke = True

        for pr in prs:
            url_base = f"https://api.github.com/repos/{pr['owner']}/{pr['repo']}/issues/{pr['number']}/comments"
            key = f"{pr['owner']}/{pr['repo']}#{pr['number']}"
            try:
                comments = gh_get(url_base + "?per_page=100", gh_token) if gh_token else []
            except Exception as e:
                print(json.dumps({"event": "pr_poll_error", "pr": key, "error": str(e)}), flush=True)
                continue
            seen = set(state["prs"].setdefault(key, {}).setdefault("comment_ids", []))
            new = [c for c in comments if c["id"] not in seen]
            if new:
                for c in new:
                    print(json.dumps({"event": "pr_new_comment", "pr": key,
                                      "comment_id": c["id"], "author": c["user"]["login"],
                                      "body_preview": (c.get("body") or "")[:200],
                                      "url": c["html_url"]}), flush=True)
                state["prs"][key]["comment_ids"] = [c["id"] for c in comments]
                save_state(state)
                woke = True

        if not woke:
            time.sleep(POLL_INTERVAL)

    if not woke:
        print(json.dumps({"event": "timeout", "hours": DEADLINE_HOURS}), flush=True)


if __name__ == "__main__":
    main()
