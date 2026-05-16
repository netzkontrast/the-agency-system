#!/usr/bin/env python3
"""
Background watcher for Google Jules sessions.

Polls the Jules REST API and emits a notification every time a session
crosses into a state that needs the user's attention — plan approval,
agent questions, completion, failure, or pause. Notifications are
appended as JSON-lines to a log file and mirrored to stderr so they
show up if the watcher is run in the foreground.

Usage:
  watch_jules.py                       # watch every active session
  watch_jules.py --session SESSION_ID  # watch one session, exit on terminal state
  watch_jules.py --interval 15         # base poll interval (default 30s)
  watch_jules.py --log /path/to.jsonl  # override log path

Reads:
  JULES_API_KEY         (required)
  JULES_API_BASE_URL    (optional, defaults to https://jules.googleapis.com)

Stdlib only — no pip install required.
"""

from __future__ import annotations

import argparse
import json
import os
import signal
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

# Ensure sibling imports work
sys.path.insert(0, str(Path(__file__).parent.resolve()))

BASE_URL = os.environ.get("JULES_API_BASE_URL", "https://jules.googleapis.com")
API_KEY = os.environ.get("JULES_API_KEY", "")

NOTIFY_STATES = {
    "AWAITING_PLAN_APPROVAL",
    "AWAITING_USER_FEEDBACK",
    "COMPLETED",
    "FAILED",
    "PAUSED",
}
TERMINAL_STATES = {"COMPLETED", "FAILED"}


def http_get(path: str) -> dict:
    req = urllib.request.Request(
        f"{BASE_URL}{path}",
        headers={"x-goog-api-key": API_KEY},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def emit(log_path: Path, event: dict, quiet_transitions: bool = False, summary_mode: bool = False) -> None:
    """Append one JSON line to the log and mirror a human-readable line to stderr."""
    if quiet_transitions and summary_mode:
        return

    with log_path.open("a") as f:
        f.write(json.dumps(event) + "\n")
    print(
        f"[{event['time']}] session={event['session']} state={event['state']}"
        f" :: {event.get('note', '')}",
        file=sys.stderr,
        flush=True,
    )


def list_sessions(max_pages: int = 10) -> list[dict]:
    """Page through ``sessions.list`` and return every session up to
    ``max_pages * 100`` entries.

    The Jules sessions.list API does not document a sort order, so we
    cannot stop early based on createTime — we must scan every page (or
    hit the max_pages cap, which is a safety brake for huge accounts).
    """
    sessions: list[dict] = []
    page_token: str | None = None
    pages = 0
    while pages < max_pages:
        url = "/v1alpha/sessions?pageSize=100"
        if page_token:
            url += f"&pageToken={page_token}"
        data = http_get(url)
        page_sessions = data.get("sessions", []) or []
        sessions.extend(page_sessions)
        pages += 1
        page_token = data.get("nextPageToken")
        if not page_token:
            break
    return sessions


def get_session(session_id: str) -> dict:
    return http_get(f"/v1alpha/sessions/{session_id}")


def latest_agent_question(session_id: str, max_pages: int = 3) -> str | None:
    """Return the newest agentMessaged text across up to ``max_pages`` of
    activities, picked by ``createTime``. The activities endpoint does not
    document a sort order, so we cannot stop at the first page or the first
    hit and trust that it is current."""
    best_text: str | None = None
    best_time = ""
    token = ""
    pages = 0
    while pages < max_pages:
        path = f"/v1alpha/sessions/{session_id}/activities?pageSize=50"
        if token:
            path += f"&pageToken={token}"
        try:
            data = http_get(path)
        except Exception:
            return best_text
        for act in data.get("activities", []) or []:
            msg = act.get("agentMessaged")
            if not isinstance(msg, (dict, str)):
                continue
            if isinstance(msg, dict):
                text = msg.get("agentMessage") or ""
            else:
                text = msg
            if not text:
                continue
            ct = act.get("createTime", "")
            if ct > best_time:
                best_text = text
                best_time = ct
        token = data.get("nextPageToken") or ""
        pages += 1
        if not token:
            break
    return best_text


def session_id_of(s: dict) -> str:
    return s.get("id") or s.get("name", "").rsplit("/", 1)[-1]


def note_for(state: str, prev: str | None, sid: str) -> str:
    if state == "AWAITING_USER_FEEDBACK":
        q = latest_agent_question(sid)
        return f"Jules asks: {q}" if q else "Jules is waiting for your feedback."
    if state == "AWAITING_PLAN_APPROVAL":
        return "Plan ready — approval required."
    if state == "COMPLETED":
        return "Session completed."
    if state == "FAILED":
        return "Session failed."
    if state == "PAUSED":
        return "Session paused (quota, rate limit, or admin)."
    return f"transition {prev or '(new)'} -> {state}"


def _positive_int(s: str) -> int:
    try:
        v = int(s)
    except ValueError as e:
        raise argparse.ArgumentTypeError(f"not an integer: {s!r}") from e
    if v <= 0:
        raise argparse.ArgumentTypeError(f"must be > 0, got {v}")
    return v


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    p.add_argument("--session", help="Watch only this session id; exit on terminal state.")
    p.add_argument("--interval", type=_positive_int, default=30,
                   help="Base poll interval seconds (>0, default 30).")
    p.add_argument("--max-interval", type=_positive_int, default=300,
                   help="Cap exponential backoff at N seconds (>0, default 300).")
    p.add_argument(
        "--log",
        default=str(Path(os.environ.get("CLAUDE_PLUGIN_DATA", Path.home() / ".jules")) / "notifications.jsonl"),
        help="JSON-lines notification log path.",
    )
    p.add_argument("--quiet-transitions", action="store_true",
                   help="Only log NOTIFY_STATES; suppress intermediate transitions like QUEUED/PLANNING/IN_PROGRESS.")
    p.add_argument("--daemonize", action="store_true", help="Run in background as a daemon.")
    p.add_argument("--stop", action="store_true", help="Stop the running watcher daemon.")
    p.add_argument("--once", action="store_true", help="Do exactly ONE poll across all sessions, then exit cleanly.")
    p.add_argument("--summary", action="store_true", help="Print ONE human-readable summary line to stdout.")
    p.add_argument("--quota-warn", type=int, metavar="N", help="Emit a stderr warning if today's remaining sessions drop below N.")
    args = p.parse_args()
    if args.max_interval < args.interval:
        p.error(
            f"--max-interval ({args.max_interval}) must be >= --interval ({args.interval})"
        )
    return args


"""PIDFILE_PATH resolves to ${CLAUDE_PLUGIN_DATA}/watcher.pid if CLAUDE_PLUGIN_DATA is set;
otherwise it falls back to a .jules directory under the user's home."""
plugin_data_dir = os.environ.get("CLAUDE_PLUGIN_DATA")
if plugin_data_dir:
    PIDFILE_PATH = Path(plugin_data_dir) / "watcher.pid"
else:
    PIDFILE_PATH = Path(os.path.expanduser("~")) / ".jules" / "watcher.pid"
PIDFILE_MARKER = "watch_jules.py"


def _pid_is_watcher(pid: int) -> bool:
    """Best-effort check that ``pid`` belongs to a watch_jules.py process.

    Reads /proc/<pid>/cmdline (Linux) and looks for our script name. On
    platforms without /proc (e.g. macOS) we fall back to assuming the PID
    is ours — a stricter check would require psutil, which we deliberately
    avoid (stdlib-only).
    """
    cmdline_path = Path(f"/proc/{pid}/cmdline")
    if not cmdline_path.exists():
        return True
    try:
        cmdline = cmdline_path.read_bytes().replace(b"\x00", b" ").decode("utf-8", "replace")
    except (OSError, PermissionError):
        return True
    return PIDFILE_MARKER in cmdline


def stop_watcher() -> int:
    pid_file = PIDFILE_PATH
    if not pid_file.exists():
        print("Watcher not running (no pidfile found).", file=sys.stderr)
        return 1

    try:
        pid = int(pid_file.read_text().strip())
    except ValueError:
        print("Invalid pidfile.", file=sys.stderr)
        return 1

    if not _pid_is_watcher(pid):
        print(
            f"Pidfile {pid_file} refers to PID {pid} but it is not a "
            "watch_jules.py process; treating as stale and removing.",
            file=sys.stderr,
        )
        try:
            pid_file.unlink()
        except FileNotFoundError:
            pass
        return 1

    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        print("Watcher not running (process not found).", file=sys.stderr)
        try:
            pid_file.unlink()
        except FileNotFoundError:
            pass
        return 1
    except Exception as e:
        print(f"Failed to send SIGTERM: {e}", file=sys.stderr)
        return 1

    for _ in range(10):
        try:
            current_pid = int(pid_file.read_text().strip())
            if current_pid != pid:
                print("Watcher stopped successfully.", file=sys.stderr)
                return 0
        except FileNotFoundError:
            print("Watcher stopped successfully.", file=sys.stderr)
            return 0
        except Exception:
            pass
        time.sleep(1)

    print("Failed to stop watcher within 10s.", file=sys.stderr)
    return 1


def daemonize_process():
    if os.fork() > 0:
        sys.exit(0)
    os.chdir("/")
    os.setsid()
    os.umask(0)
    if os.fork() > 0:
        sys.exit(0)
    
    sys.stdout.flush()
    sys.stderr.flush()
    with open(os.devnull, "r") as f:
        os.dup2(f.fileno(), sys.stdin.fileno())
    with open(os.devnull, "a+") as f:
        os.dup2(f.fileno(), sys.stdout.fileno())
        os.dup2(f.fileno(), sys.stderr.fileno())


def main() -> int:
    args = parse_args()

    if args.stop:
        return stop_watcher()

    if not API_KEY:
        print("ERROR: JULES_API_KEY is not set in the environment.", file=sys.stderr)
        return 1

    pid_file = PIDFILE_PATH
    log_path = Path(args.log).resolve()

    if args.daemonize:
        if pid_file.exists():
            try:
                existing = int(pid_file.read_text().strip())
            except ValueError:
                existing = -1
            if existing > 0 and _pid_is_watcher(existing):
                try:
                    os.kill(existing, 0)
                    print(
                        f"ERROR: another watcher is already running (pid {existing}). "
                        "Run with --stop first.",
                        file=sys.stderr,
                    )
                    return 1
                except ProcessLookupError:
                    pass
        daemonize_process()
        pid_file.parent.mkdir(parents=True, exist_ok=True)
        pid_file.write_text(f"{os.getpid()}\n")

    log_path.parent.mkdir(parents=True, exist_ok=True)

    last_state: dict[str, str] = {}
    seeded_baseline = False
    interval = args.interval
    stop = False

    def handle_sig(_sig, _frame):
        nonlocal stop
        stop = True

    signal.signal(signal.SIGINT, handle_sig)
    signal.signal(signal.SIGTERM, handle_sig)

    emit(log_path, {
        "time": now_iso(),
        "session": "watcher",
        "state": "STARTED",
        "note": f"watching {'session ' + args.session if args.session else 'all sessions'}; interval={args.interval}s",
    }, args.quiet_transitions, args.summary)

    while not stop:
        changed = False

        try:
            if args.session:
                sessions = [get_session(args.session)]
            else:
                sessions = list_sessions()
        except urllib.error.HTTPError as e:
            emit(log_path, {
                "time": now_iso(),
                "session": "watcher",
                "state": "HTTP_ERROR",
                "note": f"{e.code} {e.reason}",
            }, args.quiet_transitions, args.summary)
            if e.code == 401:
                emit(log_path, {
                    "time": now_iso(),
                    "session": "watcher",
                    "state": "FATAL",
                    "note": "API key rejected. Re-export JULES_API_KEY.",
                }, args.quiet_transitions, args.summary)
                return 2
            if e.code == 404 and args.session:
                emit(log_path, {
                    "time": now_iso(),
                    "session": args.session,
                    "state": "FATAL",
                    "note": "Session not found (404). It may have been deleted, "
                            "or the id is wrong. Exiting --session watch.",
                }, args.quiet_transitions, args.summary)
                return 3
            time.sleep(min(interval * 2, args.max_interval))
            continue
        except Exception as e:
            emit(log_path, {
                "time": now_iso(),
                "session": "watcher",
                "state": "POLL_ERROR",
                "note": str(e),
            }, args.quiet_transitions, args.summary)
            time.sleep(min(interval * 2, args.max_interval))
            continue

        today_prefix = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        today_count = sum(1 for s in sessions if s.get("createTime", "").startswith(today_prefix))
        remaining = 100 - today_count
        
        if args.summary:
            active_states = {}
            for s in sessions:
                state = s.get("state")
                if state not in ("COMPLETED", "FAILED", "STATE_UNSPECIFIED"):
                    active_states[state] = active_states.get(state, 0) + 1
            
            active_total = sum(active_states.values())
            states_str = ", ".join(f"{count} {state}" for state, count in active_states.items())
            details = f" ({states_str})" if states_str else ""
            
            print(f"Jules: {today_count} used today, {remaining} left, {active_total} active{details}", flush=True)

        if args.quota_warn is not None and remaining < args.quota_warn:
            print(f"WARNING: Jules quota running low! {remaining} left today.", file=sys.stderr, flush=True)

        last_agent_msg: dict[str, str] = getattr(main, "_last_agent_msg", {})
        main._last_agent_msg = last_agent_msg  # type: ignore[attr-defined]

        # On first poll (all-sessions mode), seed last_state from terminal
        # historical sessions so we don't fire a notification storm of stale
        # COMPLETED/FAILED events. For --session mode we always want the
        # current state surfaced, so skip the seeding.
        if not seeded_baseline and not args.session:
            for s in sessions:
                state = s.get("state", "STATE_UNSPECIFIED")
                if state in TERMINAL_STATES:
                    last_state[session_id_of(s)] = state
            seeded_baseline = True

        for s in sessions:
            sid = session_id_of(s)
            state = s.get("state", "STATE_UNSPECIFIED")
            prev = last_state.get(sid)

            # When the session sits in AWAITING_USER_FEEDBACK across polls,
            # the state-change check will skip it — but Jules may have posted
            # a *new* agent question in the meantime. Re-emit whenever the
            # newest agent message changes, even at the same state.
            agent_msg_changed = False
            if state == "AWAITING_USER_FEEDBACK":
                current_q = latest_agent_question(sid) or ""
                if current_q and current_q != last_agent_msg.get(sid):
                    agent_msg_changed = True
                    last_agent_msg[sid] = current_q

            if prev == state and not agent_msg_changed:
                continue

            # Intermediate transitions (QUEUED/PLANNING/IN_PROGRESS) under
            # --quiet-transitions are suppressed from the log but still count
            # as activity — otherwise the watcher backs off to --max-interval
            # while sessions are actively progressing and misses the next
            # actionable state by minutes.
            if (
                args.quiet_transitions
                and state not in NOTIFY_STATES
                and prev is not None
                and not agent_msg_changed
            ):
                last_state[sid] = state
                changed = True
                continue

            changed = True
            emit(log_path, {
                "time": now_iso(),
                "session": sid,
                "state": state,
                "title": s.get("title", ""),
                "url": s.get("url", ""),
                "note": note_for(state, prev, sid),
            }, args.quiet_transitions, args.summary)
            last_state[sid] = state

            try:
                import sessions_state
                sessions_state.upsert({"id": sid, "status": state})
            except Exception as e:
                emit(log_path, {
                    "time": now_iso(),
                    "session": sid,
                    "state": "REGISTRY_ERROR",
                    "note": f"registry upsert failed: {e}",
                }, args.quiet_transitions, args.summary)

            if args.session and state in TERMINAL_STATES:
                stop = True

        if args.once:
            break

        interval = args.interval if changed else min(int(interval * 1.5), args.max_interval)

        slept = 0
        while slept < interval and not stop:
            time.sleep(1)
            slept += 1

    emit(log_path, {
        "time": now_iso(),
        "session": "watcher",
        "state": "STOPPED",
        "note": "shutdown received",
    }, args.quiet_transitions, args.summary)

    if args.daemonize and pid_file.exists():
        try:
            if int(pid_file.read_text().strip()) == os.getpid():
                pid_file.unlink()
        except Exception:
            pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
