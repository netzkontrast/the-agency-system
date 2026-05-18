---
name: context-safe-patch-handling
description: >
  Never echo a Jules patch body into the orchestrator's context — always
  route through `tools/jules-patch-extract.py` which writes the patch to
  `/tmp/jules-patches/` and emits only stats. Use when the user or
  context mentions "large patch", "Jules patch", "patch > 2 KB",
  "extract patch", "/tmp/jules-patches/", or "context-safe", or
  whenever you are about to read, grep, or apply a patch produced by
  a remote coding agent.
---

## The rule (one sentence)

`cat`, `head`, `grep`, and `Read` are FORBIDDEN against any file under
`/tmp/jules-patches/` or any patch artefact larger than ~2 KB — route
through `tools/jules-patch-extract.py` and consume only its JSON stats.

## Why this exists

Jules patches routinely span tens to hundreds of KB. Pulling one into
the orchestrator's context window — even via a one-line `head` — burns
thousands of tokens on diff content the LLM does not need to reason
about. The orchestrator's job is to decide *whether* to apply, not to
re-derive the diff. On 2026-05-17, a single `cat` of a 47 KB patch cost
~12 K tokens and degraded subsequent decisions for the rest of the
session.

The extractor solves this once: it writes the patch to disk, reads
filenames by line-scanning (no diff content ever enters Python
memory), and emits a compact JSON summary. The body stays on disk
where `git apply` can reach it without the LLM ever seeing it.

## The extractor — real CLI surface

Source: `tools/jules-patch-extract.py`. Read its docstring (lines 1–26)
for the contract.

### Required env

| Variable | Purpose |
|---|---|
| `JULES_API_KEY` | Required for all invocations. Used in `X-Goog-Api-Key` header against `https://jules.googleapis.com/v1alpha/sessions/{sid}`. |
| `AGENCY_REPO_ROOT` | Optional. Overrides repo-root auto-detection when `--apply` is used. |

### Positional + flags

```
python3 tools/jules-patch-extract.py <session_id> [--apply] [--branch NAME] [--repo PATH]
```

| Token | Meaning |
|---|---|
| `<session_id>` | The Jules session ID (positional, required). |
| `--apply` | After saving the patch to disk, run `git apply --stat` then `git apply --whitespace=nowarn` against the resolved repo. Without `--apply` the script only saves + emits stats. |
| `--branch NAME` | (Only with `--apply`.) Before applying, runs `git checkout Master`, `git pull origin Master`, `git checkout -B NAME`. Fails fast on any base-prep error — never swallowed. |
| `--repo PATH` | Override repo root. Priority order: `--repo` > `$AGENCY_REPO_ROOT` > `git rev-parse --show-toplevel`. |

### Output shape (JSON to stdout)

```json
{
  "sid": "<session_id>",
  "patches": [
    {
      "path": "/tmp/jules-patches/<sid>-out0.patch",
      "bytes": 12345,
      "files": 7,
      "first_files": ["path/a.py", "path/b.md", "..."],
      "has_more": false,
      "apply": {                       // only when --apply is used
        "stat_stdout": "...",          // filenames + +/- counts ONLY
        "stat_stderr_lines": 0,
        "apply_returncode": 0,
        "apply_stderr_preview": ""     // capped at 2 KB
      }
    }
  ],
  "skipped_after_failure": {           // present only if apply failed mid-batch
    "count": 2,
    "note": "Subsequent patches were not applied because an earlier patch failed; resolve the failure and re-run."
  }
}
```

Exit codes:
- `0` — success (or no `--apply`).
- `1` — usage error, repo-root unresolved, base-branch prep failed, or
  `git apply` failed.
- `2` — session has no `outputs[].gitPatch.unidiffPatch` to extract.

## Usage patterns

### Stats-only inspection (decide whether to apply)

```bash
python3 tools/jules-patch-extract.py <sid>
```

Returns the JSON above without touching the working tree. Use this
before deciding whether the patch is worth applying — file count and
first 12 filenames are enough for that judgment.

### Apply to a fresh branch off Master

```bash
AGENCY_REPO_ROOT=$(pwd) python3 tools/jules-patch-extract.py <sid> \
  --apply --branch claude/<spec-slug>-recovered-<sid-short>
```

Branches off the current `origin/Master`, applies the patch, leaves
uncommitted changes ready for `git commit`.

### Apply in-place on the current branch

```bash
AGENCY_REPO_ROOT=$(pwd) python3 tools/jules-patch-extract.py <sid> --apply
```

No branch prep — applies to wherever HEAD currently points. Use only
when you have already prepared the branch by hand.

## What NOT to do

| Forbidden | Why |
|---|---|
| `cat /tmp/jules-patches/<sid>-out0.patch` | Pulls the entire diff into context. Use the extractor's `first_files` instead. |
| `head -n 200 <patch>` | Still pulls hundreds of diff lines — same problem at smaller scale. |
| `grep <pattern> <patch>` | Even matched lines bring surrounding hunk headers and file paths into context. If you need to know whether a file is touched, check `first_files[]` (capped at 12) or run the extractor without `--apply` and inspect the JSON. |
| `Read` tool against a patch file | Same as `cat`. The `Read` tool returns content into context. |
| Echoing `git diff` output for an applied patch into context | Apply, then commit. Do not read the diff back — `git apply --stat` already printed the structural summary you need. |
| Inventing `--verbose` / `--json` / `--out` flags | The extractor's only flags are `--apply`, `--branch`, `--repo`. Do not assume others exist. |

## Red flags

| Symptom | Action |
|---|---|
| About to use `Read` / `cat` / `head` / `grep` on `/tmp/jules-patches/...` | Stop. Re-run the extractor without `--apply` and use its JSON. |
| Patch file is > 2 KB and you want to "just peek" | Stop. The `first_files[]` + `bytes` + `files` summary is the peek. |
| Extractor returned `has_more: true` and you want the full file list | Acceptable to re-run with a small Python one-liner that only emits filenames (the extractor's `stat_patch` function does exactly this in-process). Do NOT `grep ^diff` against the patch from the main thread. |
| Need to verify a specific file is in the patch | Pipe the extractor's stdout through `jq` for `.patches[].first_files[]` containing the target. If `has_more`, do the check in a subagent so the patch body never reaches the main context. |
| `apply_returncode != 0` and curious about the failure | Read `apply_stderr_preview` (capped at 2 KB by design). Do not read the patch to "see what conflicted" — re-run with a subagent if forensic detail is required. |

## References

- `tools/jules-patch-extract.py` — the canonical implementation.
  Docstring at top of file is authoritative.
- `Plan/JULES_PROTOCOL.md §8` — recovery flow that drives most
  invocations of the extractor.
- `skills/agentic/silent-fail-recovery/SKILL.md` — the runbook that
  calls into this skill.
- `skills/agentic/jules-orchestrator-discipline/SKILL.md` — rule 3
  ("patches > 2 KB never `head`/`grep`/`cat`-ed") is enforced here.
