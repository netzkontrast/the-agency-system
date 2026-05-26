---
phase_id: "06"
entry_verb: "verify"
description: "JULES_PROTOCOL §8 silent-fail probe — sets state to VERIFIED on a clean landing or SILENT_FAIL when a patch sits unsynced."
---

# Phase 06 — Verify

The verify phase is the silent-fail check codified in
`CLAUDE.md`'s JULES_PROTOCOL §8: a Jules session whose API state has
flipped to `COMPLETED` does not automatically mean work landed on
origin. Verify is the local gate that decides which of two paths the
session follows next:

- **Clean landing.** The patch summary reports zero added/removed
  lines — Jules finished with nothing to push. State moves to
  `VERIFIED` with `branch_on_remote=true` and the phase suggests
  `mcp__jules_integrate` as the (no-op) terminal step.
- **Silent-fail.** The patch summary reports nonzero diff. The
  handler cannot confirm origin from inside the row (that lives
  outside the agency-system harness), so it marks
  `state=SILENT_FAIL`, records `patch_bytes` / `patch_files`, and
  suggests `mcp__jules_recover` next.

**Inputs.**
- `session_id` (string, required).
- `require_remote_branch` (bool, default `false`): when true, the
  handler skips the patch heuristic and forces `SILENT_FAIL` — useful
  when the caller wants to drive the JULES_PROTOCOL §8 GitHub-branch
  check explicitly (via GitHub MCP) and write `branch_on_remote=true`
  afterwards.

**Outputs.** Envelope `data.state` carries `VERIFIED` or
`SILENT_FAIL`; `data.branch_on_remote` carries the heuristic verdict
(`null` when `require_remote_branch=true`).

**Gates.** Blocked by `session-completed` (hard-blocking) — verify
only runs after `jules_state=COMPLETED` has been observed.
