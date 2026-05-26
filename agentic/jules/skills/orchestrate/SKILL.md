---
name: orchestrate
description: Run a Jules session through its full lifecycle — dispatch, plan approval, monitor, verify, integrate — driven by the jules-row state machine.
model: claude-opus-4-7
---

# orchestrate

Drive a single Jules-orchestrator session from a task brief all the way
to a terminal state — `APPLIED` (silent-fail recovery path) or
`VERIFIED` (clean-landing path). The skill is the user-facing surface
over the six orchestration phases (03–08) the `jules` row exposes.

## Inputs

Required:
- `prompt` (string): Natural-language task brief sent to Jules.
- `owner` (string): GitHub owner / org. The repo must be connected to
  the Jules account; if not, dispatch will fail with
  `JULES_SOURCE_UNRESOLVED`.
- `repo` (string): Repository name.

Optional:
- `branch` (string, default `"main"`): Starting branch for the session.
- `title` (string): Human-readable session label.
- `auto_approve` (bool, default `true`): When true, the await_plan
  phase calls `jules_approve` automatically. Set false to pause at the
  planning checkpoint and surface the plan to a human reviewer.
- `apply` (bool, default `true`): When true, the integrate phase calls
  `jules_patch_apply` on a silent-failed session. Set false to take
  delivery of the patch metadata only and integrate via a separate
  path (e.g. GitHub MCP).

## What it runs

The skill loops the row's six phases in order, polling between
`await_plan` and `monitor` until the session reaches a terminal label:

| Phase | Verb | Records |
|---|---|---|
| 03 | `dispatch`    | Creates the JulesSession node in state `DISPATCHED`. |
| 04 | `await_plan`  | Watches `AWAITING_PLAN_APPROVAL`; calls `jules_approve`. |
| 05 | `monitor`     | Watches Jules-API state until `COMPLETED`. |
| 06 | `verify`      | JULES_PROTOCOL §8 silent-fail probe; sets `VERIFIED` or `SILENT_FAIL`. |
| 07 | `recover`     | (conditional) Pulls patch metadata into a SessionPatch node. |
| 08 | `integrate`   | Applies the patch (or stamps a PR url) — terminal phase. |

## Outputs

A `tool_result` envelope. `data.session_id` is the Jules numeric id,
`data.state` is the final local label, `data.terminal=true` on success.
On failure the envelope's `error.code` names the precise problem —
see `context/_shared/error_codes.py` for the jules-orchestration
catalogue.

## When to skip

- The user wants only a research probe — call `/jules-research`
  instead.
- The user wants to recover one specific silent-failed session
  without re-running dispatch — call `/jules-recover`.
- Jules quota is exhausted — `mcp__jules_quota` reports `remaining=0`.

## Manual escape hatches

The skill is a convenience composer. Each phase is independently
callable via `mcp__jules_<verb>`, so a session whose orchestrate run
errors mid-flow can be resumed by hand from the JulesSession node's
last recorded state.
