This file documents the Jules session state machine. Load this when you need to understand the lifecycle of a session or what actions are permitted in a given state.


Every status check (`get session`) returns a `state` enum. Your decision
matrix:

| State | What it means | Your next action |
|---|---|---|
| `STATE_UNSPECIFIED` | Backend can't determine state — transient/init failure | Report and ask user whether to retry. |
| `QUEUED` | Accepted, waiting for compute | Tell the user it is queued; do not poll in a tight loop. Yield. |
| `PLANNING` | Cloning repo, analysing, drafting plan | Same — report progress, yield to the prompt. |
| `AWAITING_PLAN_APPROVAL` | **Circuit breaker tripped** — plan ready, needs human OK | Immediately call `list activities`, find the `planGenerated` event, render the plan as readable markdown, and ask the user "Approve this plan, request changes, or cancel?". |
| `AWAITING_USER_FEEDBACK` | Jules has a question and is blocked | Call `list activities`, find the latest `userMessaged` from the agent, surface the question verbatim, await the user's reply, then send via `sendMessage`. |
| `IN_PROGRESS` | Writing code, running tests, committing | Report status; yield. Do not poll continuously. |
| `PAUSED` | Suspended (quota, rate limit, admin) | Surface any accompanying message; stop polling; let the user decide. |
| `FAILED` | Terminal error | Pull recent activities for diagnostics, summarise the failure, close out the local task tracking. |
| `COMPLETED` | **Ambiguous — the field lies in two distinct ways.** (1) `state=COMPLETED + outputs is null/empty` means the plan-approval gate timed out and Jules abandoned the session; treat as `AWAITING_PLAN_APPROVAL` and approve fast. (2) `state=COMPLETED + has_outputs=True` may still mean Jules is paused in the web UI asking whether to create a Pull Request for the patch it produced; the `state` field has flipped but the session is not finalized. The `sessionCompleted` activity does NOT distinguish the two — it appears in both. The only reliable resolutions are: (a) set `automationMode=AUTO_CREATE_PR` at create time so Jules opens the PR itself without asking; or (b) after harvesting the patch via `jules_patch`, send `jules_message(session_id, "no PR needed, patch applied locally")` to finalize the session.<br><br><ul><li>COMPLETED with patch artifact OR Session.outputs[].pullRequest → real terminal success</li><li>COMPLETED with NEITHER → session is paused on a UI gate; recovery is a continuation jules_message, not a respawn (see caveats: "COMPLETED without artifacts ≠ dead")</li></ul> | If outputs is empty, approve the plan. If outputs is present but Jules might be waiting on PR-creation, either set automation mode up front or send a finalize message after harvest. |

**Never simulate a blocking poll loop.** The terminal is interactive; do
not freeze it. The pattern is: do *one* status check, report, hand control
back to the user. The user explicitly asks "check Jules" / "status?" to
trigger the next check. The only exception is *immediately* after
`create`, where one status check confirms `QUEUED` before yielding.

---
