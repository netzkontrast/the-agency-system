---
name: recover
description: Recover a silent-failed Jules session — extract its patch metadata into the ontology and (optionally) apply it locally.
model: claude-opus-4-7
---

# recover

Use this skill when a Jules session sits in local state `SILENT_FAIL`
(its Jules-API state is `COMPLETED` but no branch landed on origin and
no PR was opened). The skill drives the row's two recovery phases —
`recover` (phase 07) and `integrate` (phase 08) — without re-running
dispatch / monitor / verify.

## Inputs

Required:
- `session_id` (string): The Jules session id. The skill expects a
  JulesSession node to already exist in the ontology in state
  `SILENT_FAIL`; if it's in a different state, the recover handler
  rejects with `SESSION_STATE_INVALID`.

Optional:
- `apply` (bool, default `true`): When true, integrate calls
  `jules_patch_apply` to land the diff on the local working tree.
  When false, only patch metadata is captured (a `SessionPatch` node
  is upserted) and integrate finalises without touching files.
- `pr_url` (string): Optional pull-request URL — stamp it onto the
  JulesSession when the patch was landed through a separate path.

## What it runs

| Phase | Verb | What it does |
|---|---|---|
| 07 | `recover`    | Calls `jules_patch_summary` → upserts SessionPatch node + DERIVED_FROM edge → bumps session to `PATCH_EXTRACTED`. |
| 08 | `integrate`  | When `apply=true`: `jules_patch_apply` → bumps to `APPLIED`. When `apply=false`: bookkeeping only. |

## Outputs

A `tool_result` envelope reporting the final state (`APPLIED` on
success), the file list from the patch, line-count totals, and any
captured `git_stderr` if `git apply` failed. The `SessionPatch` node
is reachable from the JulesSession via the `DERIVED_FROM` edge for
downstream auditing.

## Manual fallback

If `jules_patch_apply` consistently fails (e.g. the working tree has
divergent changes), call `recover` with `apply=false` first — the
SessionPatch node will still be created — then land the patch via the
GitHub MCP (`create_branch` + `create_or_update_file` +
`create_pull_request`) per JULES_PROTOCOL §8.
