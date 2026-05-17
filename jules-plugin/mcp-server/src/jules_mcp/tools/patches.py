import os
import shutil
import subprocess
import tempfile
from fastmcp import FastMCP

from jules_mcp.api import _paginate, _request, _short_id, JulesAPIError

def _fetch_patch(sid: str, max_pages: int = 5) -> dict:
    """Internal: returns {"patch": str, "base_commit": str, "suggested_commit_message": str}
    or raises RuntimeError.

    Patches live as activity ARTIFACTS, not in `Session.outputs[]` (which
    carries the PR resource, when auto_create_pr is set). Walk activities,
    look for `artifacts[].changeSet.gitPatch.unidiffPatch`, and return the
    newest patch by ``createTime``.
    """
    items, _, _, _ = _paginate(
        f"/v1alpha/sessions/{sid}/activities",
        {"pageSize": 100},
        max_pages=max_pages,
    )
    best: dict | None = None
    best_time = ""
    for a in items:
        artifacts = a.get("artifacts") or []
        for art in artifacts:
            cs = art.get("changeSet") or {}
            gp = cs.get("gitPatch") or {}
            patch = gp.get("unidiffPatch")
            if not patch:
                continue
            ct = a.get("createTime", "")
            if best is None or ct > best_time:
                best = {
                    "patch": patch,
                    "base_commit": gp.get("baseCommitId", ""),
                    "suggested_commit_message": gp.get("suggestedCommitMessage", ""),
                }
                best_time = ct
    if best is not None:
        return best
    # Provide a useful diagnostic by checking session state.
    try:
        s = _request("GET", f"/v1alpha/sessions/{sid}")
        state = s.get("state") or "UNKNOWN"
    except JulesAPIError:
        state = "UNKNOWN"
    raise RuntimeError(
        f"no patch artifact found in activities (session state={state})"
    )


def _parse_diff_header_b_path(line: str) -> str | None:
    """Extract the b-side path from a `diff --git a/X b/Y` header.

    Handles git's two header forms:
      - unquoted:  diff --git a/path/to/file b/path/to/file
      - quoted:    diff --git "a/path with spaces" "b/path with spaces"
    Returns the file path with the `b/` (or `"b/`) prefix stripped, or None
    if the header is malformed.
    """
    body = line[len("diff --git "):].rstrip("\n")
    # Quoted form: both halves are double-quoted, possibly with C-escapes.
    if body.startswith('"'):
        end = 1
        while end < len(body):
            if body[end] == "\\":
                end += 2
                continue
            if body[end] == '"':
                break
            end += 1
        if end >= len(body):
            return None
        b_part = body[end + 1:].lstrip()
        if not b_part.startswith('"'):
            return None
        b_end = 1
        while b_end < len(b_part):
            if b_part[b_end] == "\\":
                b_end += 2
                continue
            if b_part[b_end] == '"':
                break
            b_end += 1
        if b_end >= len(b_part):
            return None
        inner = b_part[1:b_end]
        return inner[2:] if inner.startswith("b/") else inner
    parts = body.split(" ")
    if len(parts) < 2:
        return None
    p = parts[-1]
    return p[2:] if p.startswith("b/") else p


def _parse_diff_metadata(patch: str) -> dict:
    """Count files touched and added/removed lines from a unidiff. Stdlib only."""
    files: list[str] = []
    added = 0
    removed = 0
    for line in patch.splitlines():
        if line.startswith("diff --git "):
            p = _parse_diff_header_b_path(line)
            if p:
                files.append(p)
        elif line.startswith("+") and not line.startswith("+++"):
            added += 1
        elif line.startswith("-") and not line.startswith("---"):
            removed += 1
    return {"files": files, "lines_added": added, "lines_removed": removed}


def jules_patch_summary(session_id: str) -> dict:
    """Token-cheap metadata about a session's patch — files touched and
    line counts. Does NOT return the diff body.

    Use this to decide whether to apply a patch or to display its size
    to a user before deciding next steps.

    Returns:
        {
          "files": ["path1", ...],
          "lines_added": int,
          "lines_removed": int,
          "patch_bytes": int,
          "base_commit": str,
          "suggested_commit_message": str
        }
    """
    sid = _short_id(session_id)
    try:
        data = _fetch_patch(sid)
    except RuntimeError as e:
        return {"error": str(e)}
    meta = _parse_diff_metadata(data["patch"])
    return {
        **meta,
        "patch_bytes": len(data["patch"]),
        "base_commit": data["base_commit"],
        "suggested_commit_message": data["suggested_commit_message"],
    }


def jules_patch_apply(
    session_id: str,
    dry_run: bool = False,
    cwd: str = "",
    only_files: str = "",
    three_way: bool = False,
) -> dict:
    """Apply a session's patch to a local git working tree WITHOUT
    returning the diff body in the response. Token-efficient — only
    metadata flows back through the model.

    The patch is written to a tempfile, fed to `git apply`, then
    deleted. Patch content never enters the tool result.

    Args:
        session_id: The session whose patch to apply.
        dry_run: When True, runs `git apply --check` instead of applying.
            Use this to validate a patch before committing to it.
        cwd: Working directory to apply in. Empty = current process cwd.
            Must be a git working tree.
        only_files: Comma-separated list of file paths. When non-empty,
            the patch is filtered to only these files before applying
            (useful when you want one Jules patch's contribution to a
            shared file but not its other touches).
        three_way: When True, passes `--3way` to git apply for
            conflict-tolerant application.

    Returns:
        {
          "applied": bool,
          "dry_run": bool,
          "files": ["path1", ...],
          "lines_added": int,
          "lines_removed": int,
          "base_commit": str,
          "suggested_commit_message": str,
          "git_stderr": str,           # captured on failure for triage
        }
    """
    sid = _short_id(session_id)
    try:
        data = _fetch_patch(sid)
    except RuntimeError as e:
        return {"error": str(e), "applied": False}

    patch_text = data["patch"]
    meta = _parse_diff_metadata(patch_text)

    if only_files:
        wanted = {f.strip() for f in only_files.split(",") if f.strip()}
        filtered_chunks: list[list[str]] = []
        current: list[str] = []
        keep_current = False
        for line in patch_text.splitlines(keepends=True):
            if line.startswith("diff --git "):
                if current and keep_current:
                    filtered_chunks.append(current)
                current = [line]
                p = _parse_diff_header_b_path(line.rstrip("\n")) or ""
                keep_current = p in wanted
            else:
                current.append(line)
        if current and keep_current:
            filtered_chunks.append(current)
        if not filtered_chunks:
            return {
                "applied": False,
                "dry_run": dry_run,
                "files": [],
                "error": f"none of {sorted(wanted)} matched files in patch",
            }
        patch_text = "".join("".join(c) for c in filtered_chunks)
        meta = _parse_diff_metadata(patch_text)

    tmp = tempfile.NamedTemporaryFile(
        prefix="jules-patch-", suffix=".diff", delete=False, mode="w"
    )
    try:
        tmp.write(patch_text)
        tmp.close()
        cmd = ["git", "apply"]
        if dry_run:
            cmd.append("--check")
        if three_way:
            cmd.append("--3way")
        cmd.append(tmp.name)
        proc = subprocess.run(
            cmd,
            cwd=cwd or None,
            capture_output=True,
            text=True,
            timeout=60,
        )
        applied = proc.returncode == 0
        result = {
            "applied": applied and not dry_run,
            "dry_run": dry_run,
            "files": meta["files"],
            "lines_added": meta["lines_added"],
            "lines_removed": meta["lines_removed"],
            "base_commit": data["base_commit"],
            "suggested_commit_message": data["suggested_commit_message"],
        }
        if not applied:
            # Truncate to keep token cost bounded even on failure
            err = (proc.stderr or proc.stdout or "").strip()
            result["git_stderr"] = err[:800]
            result["applied"] = False
        return result
    finally:
        try:
            os.unlink(tmp.name)
        except Exception:
            pass


def jules_patch(session_id: str, max_bytes: int = 60000) -> dict:
    """Return the unified-diff patch body for a session.

    TOKEN-EXPENSIVE — the diff lands in the model's context. Prefer
    `jules_patch_apply` (applies on disk, returns metadata only) or
    `jules_patch_summary` (metadata only, no body) for routine work.
    Only call this when you need to inspect or transform the patch
    inside the conversation.

    Args:
        max_bytes: Refuse to return diffs larger than this (default 60 KB
            ≈ 15-20K tokens). Set higher only when you've already
            checked `jules_patch_summary` and accepted the cost.

    Returns: {"patch": "<unidiff>", "base_commit": ..., "suggested_commit_message": ...}
    or {"error": "..."} when too large or unavailable.
    """
    sid = _short_id(session_id)
    try:
        data = _fetch_patch(sid)
    except RuntimeError as e:
        return {"error": str(e)}
    if len(data["patch"]) > max_bytes:
        return {
            "error": (
                f"patch is {len(data['patch'])} bytes, exceeds max_bytes={max_bytes}. "
                "Use jules_patch_apply (no body returned) or raise max_bytes."
            )
        }
    return data


def register_patch_tools(mcp: FastMCP) -> None:
    mcp.tool()(jules_patch_summary)
    mcp.tool()(jules_patch_apply)
    mcp.tool()(jules_patch)
