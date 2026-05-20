---
phase_id: "08"
entry_verb: "integrate"
description: "Terminal phase — apply the patch (when apply=true) or stamp a PR url; session ends in APPLIED or VERIFIED."
---

# Phase 08 — Integrate

The integrate phase is the terminal step of the orchestration
workflow. Two paths arrive here:

- **From `VERIFIED`.** The session landed cleanly; integrate is a
  no-op finaliser. When the caller supplies `pr_url`, that url is
  stamped onto the JulesSession. The session stays in `VERIFIED`.
- **From `PATCH_EXTRACTED`.** Recover staged a patch. When
  `apply=true` (default), the handler calls `jules_patch_apply` —
  the patch is applied to the local working tree without ever
  surfacing the diff bytes through the model. State moves to
  `APPLIED`. When `apply=false`, the handler does only bookkeeping
  (state → `APPLIED`, SessionPatch.applied=null) so the caller can
  land the diff through a separate channel (e.g. GitHub MCP).

**Inputs.**
- `session_id` (string, required).
- `apply` (bool, default `true`).
- `pr_url` (string, optional).

**Outputs.** Envelope `data.state` is `APPLIED` (patch landed locally
or bookkeeping-only) or `VERIFIED` (no patch existed). On failure of
`git apply`, the envelope carries `error.code=PATCH_APPLY_FAILED`
with the captured `git_stderr`.

**Gates.** Blocked by `patch-applied` (hard-blocking) — only sessions
in `PATCH_EXTRACTED` or `VERIFIED` may enter. The gate guards against
calling integrate on a session that hasn't reached either terminal
prerequisite.
