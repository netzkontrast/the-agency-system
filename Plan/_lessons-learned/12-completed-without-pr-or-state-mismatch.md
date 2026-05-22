---
lesson_id: 12
slug: completed-without-pr-or-state-mismatch
severity: high
seen_in: [spec-012]
applies_to:
  - jules-mcp
  - jules-protocol
  - orchestrator-patterns
captured_at: 2026-05-17
---

# Session COMPLETED ≠ PR opened

## Pattern

Spec 012 (Dramatica + NCP libs) session `sessions/8219552128114767877` transitioned to `COMPLETED` per `jules_get`, and the `jules_patch_summary` returns a real diff — but the branch is missing on GitHub:

```bash
$ mcp__github__list_branches | grep 8219552
(empty)
```

No PR was opened, even with `auto_create_pr=True` on `jules_create`. Jules' last activities said "Ready for submission" but the actual push step apparently failed silently or never ran.

This is the 4th strike on the scratch-file anti-pattern too — the patch_summary shows `copy_vendor_data.py`, `patch_pyproject.py`, `patch_pyproject_yaml.py` at the repo root, exactly the kind of porting-script residue lesson 01 warned about.

## What to change

### Jules MCP / API

The `jules_get` state surface needs a sub-state to distinguish "completed AND PR opened" vs "completed AND push failed":

```
state: COMPLETED
substate: pr_opened | push_failed | submit_skipped
```

Or: a separate `jules_pr_url(sid)` tool that returns the PR URL if one was opened, `null` otherwise. The orchestrator can poll this to detect the discrepancy without listing GitHub branches.

### Orchestrator policy

After a session hits COMPLETED, ALWAYS verify the PR exists via `mcp__github__list_pull_requests` (or the proposed `jules_pr_url`) BEFORE assuming work landed. The watcher should treat "COMPLETED without PR within 60s" as an action-required state, not a terminal success.

### Dispatch-prompt template

Add an explicit gate at end of Approach:
> Final step: open the PR via the submit tool. If push fails for any reason (rate limit, credential expiry, network), open a draft PR labelled `[BLOCKED: push-failure]` documenting the failure. Do NOT idle waiting for retry.

## Workaround used in this wave

Sent `jules_message` to spec 012 with explicit instructions to (a) delete the 3 scratch files, (b) push + open PR, (c) re-run smoke tests in clean install, (d) paste real evidence. If Jules can't resume the submit step, will dispatch a fresh session with a "finalize spec 012 from branch X" prompt — but that's brittle because there's no remote branch yet.

## Concrete deliverable for the meta-spec

Two layers:
1. **Jules MCP** — add a `jules_pr_url(sid)` tool and/or a `substate` field. Document the `state=COMPLETED, no PR` failure mode in `jules_get`'s docstring.
2. **JULES_PROTOCOL.md** — orchestrator must verify PR existence after COMPLETED; do not trust the state alone.
