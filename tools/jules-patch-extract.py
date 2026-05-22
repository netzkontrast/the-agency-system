#!/usr/bin/env python3
"""Extract a Jules session patch + apply it locally, WITHOUT echoing the patch
body into the orchestrator's stdout (and thus into Claude's context).

The full patch is written to /tmp/jules-patches/{sid}-out{i}.patch and never
printed.  Only counts + filenames + sizes are emitted to stdout — kilobytes,
not megabytes.  The patch body itself stays on disk.

Usage:
  python3 /tmp/jules_extract_patch.py <session_id> [--apply] [--branch <name>] [--repo <path>]

Without --apply: just downloads + emits stats.
With --apply:    downloads, runs `git apply --stat` (filenames only, no diff
                 lines), then `git apply` quietly, leaving uncommitted changes
                 ready for the orchestrator to commit + push.

Repo root resolution (when --apply is used):
  1. --repo CLI arg, if given.
  2. $AGENCY_REPO_ROOT environment variable, if set.
  3. `git rev-parse --show-toplevel` from current working directory.
  Failure at step 3 (not inside a git repo) -> JSON error + exit 1.

ENV:
  JULES_API_KEY        required
  AGENCY_REPO_ROOT     optional, overrides auto-detection
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


def resolve_repo_root(cli_repo: str | None) -> pathlib.Path:
    """Resolve repo root via --repo > $AGENCY_REPO_ROOT > git rev-parse.

    On failure (not in a repo and no override), print JSON error + exit 1.
    """
    if cli_repo:
        return pathlib.Path(cli_repo)
    env_root = os.environ.get("AGENCY_REPO_ROOT")
    if env_root:
        return pathlib.Path(env_root)
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        )
        return pathlib.Path(result.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        stderr = getattr(e, "stderr", "") or ""
        print(json.dumps({
            "error": "repo_root_unresolved",
            "detail": (
                "Could not determine repo root. Pass --repo <path>, set "
                "$AGENCY_REPO_ROOT, or run from inside a git working tree."
            ),
            "git_stderr": stderr[:500],
        }))
        sys.exit(1)


def main() -> int:
    if len(sys.argv) < 2:
        print(
            "usage: jules_extract_patch.py <session_id> [--apply] "
            "[--branch NAME] [--repo PATH]",
            file=sys.stderr,
        )
        return 1
    sid = sys.argv[1]
    do_apply = "--apply" in sys.argv

    branch = None
    if "--branch" in sys.argv:
        try:
            branch = sys.argv[sys.argv.index("--branch") + 1]
            if branch.startswith("--"):
                raise IndexError
        except IndexError:
            print(
                "usage: jules_extract_patch.py <session_id> [--apply] "
                "[--branch NAME] [--repo PATH]\n"
                "error: --branch requires a value",
                file=sys.stderr,
            )
            return 1

    cli_repo = None
    if "--repo" in sys.argv:
        try:
            cli_repo = sys.argv[sys.argv.index("--repo") + 1]
            if cli_repo.startswith("--"):
                raise IndexError
        except IndexError:
            print(
                "usage: jules_extract_patch.py <session_id> [--apply] "
                "[--branch NAME] [--repo PATH]\n"
                "error: --repo requires a value",
                file=sys.stderr,
            )
            return 1

    session = fetch_session(sid)
    paths = save_patches(sid, session)
    if not paths:
        print(json.dumps({"sid": sid, "patches": 0, "note": "no outputs/gitPatch on session"}))
        return 2

    report = {"sid": sid, "patches": []}
    for p in paths:
        s = stat_patch(p)
        report["patches"].append({"path": str(p), **s})

    apply_failed = False
    if do_apply:
        repo = resolve_repo_root(cli_repo)
        if branch:
            # Fail fast on base-branch prep errors -- swallowing these
            # silently is how Jules silent-fail bugs slip past review.
            for cmd in (
                ["git", "checkout", "Master"],
                ["git", "pull", "origin", "Master"],
                ["git", "checkout", "-B", branch],
            ):
                proc = subprocess.run(cmd, cwd=repo, capture_output=True, text=True)
                if proc.returncode != 0:
                    print(json.dumps({
                        "error": "base_branch_prep_failed",
                        "command": cmd,
                        "returncode": proc.returncode,
                        "stderr": proc.stderr[:500],
                    }))
                    return 1
        for idx, p in enumerate(paths):
            outcome = apply_patch(p, repo)
            report["patches"][idx]["apply"] = outcome
            if outcome["apply_returncode"] != 0:
                apply_failed = True
                # Stop on first apply failure -- subsequent patches likely
                # depend on earlier ones, and continuing produces a mess.
                skipped = len(paths) - idx - 1
                if skipped > 0:
                    report["skipped_after_failure"] = {
                        "count": skipped,
                        "note": (
                            "Subsequent patches were not applied because an "
                            "earlier patch failed; resolve the failure and "
                            "re-run."
                        ),
                    }
                break

    print(json.dumps(report, indent=2))
    return 1 if apply_failed else 0


if __name__ == "__main__":
    sys.exit(main())
