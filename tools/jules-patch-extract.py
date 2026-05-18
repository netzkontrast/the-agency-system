#!/usr/bin/env python3
"""Extract a Jules session patch + apply it locally, WITHOUT echoing the patch
body into the orchestrator's stdout (and thus into Claude's context).

The full patch is written to /tmp/jules-patches/{sid}-out{i}.patch and never
printed.  Only counts + filenames + sizes are emitted to stdout — kilobytes,
not megabytes.  The patch body itself stays on disk.

Usage:
  python3 /tmp/jules_extract_patch.py <session_id> [--apply] [--branch <name>]

Without --apply: just downloads + emits stats.
With --apply:    downloads, runs `git apply --stat` (filenames only, no diff
                 lines), then `git apply` quietly, leaving uncommitted changes
                 ready for the orchestrator to commit + push.

ENV:
  JULES_API_KEY  required
"""
from __future__ import annotations
import json
import os
import pathlib
import subprocess
import sys
import urllib.request

PATCH_DIR = pathlib.Path("/tmp/jules-patches")
PATCH_DIR.mkdir(parents=True, exist_ok=True)


def fetch_session(sid: str) -> dict:
    key = os.environ["JULES_API_KEY"]
    req = urllib.request.Request(
        f"https://jules.googleapis.com/v1alpha/sessions/{sid}",
        headers={"X-Goog-Api-Key": key},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def save_patches(sid: str, session: dict) -> list[pathlib.Path]:
    """Write each output's unidiff patch to disk. Return paths only."""
    paths: list[pathlib.Path] = []
    for i, output in enumerate(session.get("outputs", [])):
        patch = (
            output.get("changeSet", {}).get("gitPatch", {}).get("unidiffPatch", "")
        )
        if not patch:
            continue
        p = PATCH_DIR / f"{sid}-out{i}.patch"
        p.write_text(patch)
        paths.append(p)
    return paths


def stat_patch(path: pathlib.Path) -> dict:
    """Return a small summary: byte size + file count + first 12 filenames.

    Reads filenames by scanning the patch on disk LINE-BY-LINE and only
    collecting the `diff --git a/X b/X` headers — no diff content ever
    enters Python memory.
    """
    files: list[str] = []
    with path.open() as f:
        for line in f:
            if line.startswith("diff --git "):
                # `diff --git a/PATH b/PATH`
                try:
                    files.append(line.split()[2][2:])  # strip "a/"
                except IndexError:
                    pass
    return {
        "bytes": path.stat().st_size,
        "files": len(files),
        "first_files": files[:12],
        "has_more": len(files) > 12,
    }


def apply_patch(path: pathlib.Path, repo: pathlib.Path) -> dict:
    """Run `git apply --stat` then `git apply` quietly. Return outcome dict.

    Stat output (filenames + insertions/deletions per file) IS printed —
    that is normal git review surface, not diff content.
    """
    # --stat shows filenames + +/- counts only, never the diff body.
    stat_proc = subprocess.run(
        ["git", "apply", "--stat", str(path)],
        cwd=repo,
        capture_output=True,
        text=True,
    )
    apply_proc = subprocess.run(
        ["git", "apply", "--whitespace=nowarn", str(path)],
        cwd=repo,
        capture_output=True,
        text=True,
    )
    return {
        "stat_stdout": stat_proc.stdout,
        "stat_stderr_lines": len(stat_proc.stderr.splitlines()),
        "apply_returncode": apply_proc.returncode,
        # stderr is fine to surface — it is just file-conflict messages,
        # not patch body. Cap at 2 KB to be safe.
        "apply_stderr_preview": apply_proc.stderr[:2000],
    }


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: jules_extract_patch.py <session_id> [--apply] [--branch NAME]", file=sys.stderr)
        return 1
    sid = sys.argv[1]
    do_apply = "--apply" in sys.argv
    branch = None
    if "--branch" in sys.argv:
        branch = sys.argv[sys.argv.index("--branch") + 1]

    session = fetch_session(sid)
    paths = save_patches(sid, session)
    if not paths:
        print(json.dumps({"sid": sid, "patches": 0, "note": "no outputs/gitPatch on session"}))
        return 2

    report = {"sid": sid, "patches": []}
    for p in paths:
        s = stat_patch(p)
        report["patches"].append({"path": str(p), **s})

    if do_apply:
        repo = pathlib.Path("/home/user/the-agency-system")
        if branch:
            subprocess.run(["git", "checkout", "Master"], cwd=repo, check=False, capture_output=True)
            subprocess.run(["git", "pull", "origin", "Master"], cwd=repo, check=False, capture_output=True)
            subprocess.run(
                ["git", "checkout", "-B", branch], cwd=repo, check=False, capture_output=True
            )
        for p in paths:
            outcome = apply_patch(p, repo)
            report["patches"][paths.index(p)]["apply"] = outcome

    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
