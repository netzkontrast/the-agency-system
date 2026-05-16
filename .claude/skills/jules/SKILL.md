---
name: jules
description: >
  Delegates long-running codebase tasks (refactors, multi-file edits, test
  generation, feature implementation, automated PR creation) to the Google
  Jules asynchronous coding agent. Supports fan-out parallel orchestration
  across many concurrent sessions. Use when the user mentions "Jules",
  "remote agent", "asynchronous task", asks for a cloud-side coding job
  that would block the local terminal, or asks for parallel work.
argument-hint: <action> [args...]   # actions: create | list | status | activities | approve | message | stop | fanout | dashboard | help
model: claude-sonnet-4-6
allowed-tools:
  - Bash
  - Read
  - mcp__jules
---

## Your Task

**Input:** `$ARGUMENTS`

You are an orchestrator for the Google Jules asynchronous coding agent. The
user's local terminal is a control plane; Jules is the remote worker. Your
job is to start, monitor, decide on, interact with, and stop Jules sessions
on the user's behalf — never to simulate the work locally.

## Preferred path: MCP tools (`mcp__jules__*`)

When the `jules` MCP server is connected, **always prefer its tools over
raw `curl`** — they are reliable, structured, and the model sees them in
every turn so they cannot be silently missed (the watcher+log-tail
pipeline is fragile; tool calls are not).

| Tool | What it does |
|---|---|
| `jules_create` | Start a new session. |
| `jules_list` | List sessions on the account (trimmed). |
| `jules_get` | Live state of one session. |
| `jules_activities` | Filtered activity timeline. |
| `jules_plan` | Render the latest planGenerated as steps. |
| `jules_approve` | Approve a plan — **call promptly or the session times out.** |
| `jules_message` | Send user feedback to a session. |
| `jules_stop` | Delete a session (destructive). |
| `jules_patch_summary` | Token-cheap: files touched, line counts, suggested commit msg. NO diff body. |
| `jules_patch_apply` | Token-cheap: apply the patch on disk (or `--dry_run`) and return metadata only. NO diff body. **Preferred harvest path.** |
| `jules_patch` | Token-EXPENSIVE: returns the full unidiff in the response. Only call when you need to inspect or transform the diff in-context; defaults to refusing > 60 KB. |
| `jules_status_all` | Bulk: state of every session grouped by state. |
| `jules_approve_awaiting` | Bulk: approve every session currently awaiting approval (filter by title substring for safety). |
| `jules_quota` | How many sessions remain on today's quota (default 100/UTC day). Call before fan-out. |

When the MCP tools are unavailable (server not yet started, no permission),
fall back to the raw `curl` recipes documented below — they remain the
authoritative reference for the on-wire format.

## Companion tooling

| Path | What it is |
|---|---|
| `.claude/mcp/jules-mcp/server.py` | The FastMCP server exposing the tools above. |
| `.claude/skills/jules/watch_jules.py` | Background watcher that polls and writes a JSON-lines log on every state transition. Supports `--daemonize`, `--stop`, and writes the latest state into the local session registry. |
| `.claude/skills/jules/sessions_state.py` | Local session registry — maps short aliases to session ids, holds last-known state. CLI: `register | list | get | update | forget | resolve`. |
| `.claude/skills/jules/jules_bulk.sh` | Bash helper for `fanout` (parallel create), `dashboard` (table view), `approve-awaiting`, `stop-all`. |
| `.claude/skills/jules/notifications.jsonl` | Watcher's event log (gitignored). |
| `.claude/skills/jules/sessions.json` | Registry persistence (gitignored). |
| `.claude/skills/jules/examples/fanout-tasks.json` | Sample input for `fanout`. |

The MCP server reads `JULES_API_KEY` from the environment on every tool
call. The skill and helpers do the same. None of these cache the key.

---

## Quota and Session Economics

**Jules enforces a per-account daily session quota — currently 100
sessions / UTC day.** Every `jules_create` call burns one slot;
stopping or finalizing a session does NOT return its slot. The
remaining budget for the day is queryable:

```python
jules_quota()  # returns used_today, remaining_today, active_today, by_state_today
```

`active_today` is the count of non-terminal sessions you started
today — they are still alive and **still able to do useful work for
you**. A running session is not a leak; it's a worker you have on
retainer.

### Conservation principles (mandatory before fan-out)

1. **Call `jules_quota` before any fan-out of 3+ sessions.** If
   remaining is tight, batch the work — or extend an existing
   session instead of spawning new ones.
2. **`jules_message` is free — but it does NOT deliver new patch
   artifacts.** A session's `outputs[].gitPatch` is set ONCE, when
   the first piece of work completes, and does NOT update when
   subsequent work happens via follow-up messages. Subsequent work
   IS performed (Jules commits to its own copy of your branch in
   its VM), but the unified-diff artifact stays the original. So:
   - Use `jules_message` for: clarifications, revising a plan
     before approval, answering agent questions, sending
     "finalize" messages, requesting summaries / reviews of work
     already done.
   - Do NOT use `jules_message` for: independent follow-up work
     that needs its own deliverable patch. For that, create a
     fresh session — yes, it burns a slot, but it's the only way
     to get a clean unidiff artifact back.

   If you must extract follow-up work from an existing session,
   the only paths are (a) ask the session to inline the diff in
   an `agentMessaged` text reply (token-expensive — pulls the
   diff into your context), or (b) ask it to create a PR
   (separate Jules-side branch and PR per session, messy to
   integrate).
3. **Don't `jules_stop` a session that can still produce value.**
   Stopping does not reclaim the slot for today. The only good
   reasons to stop a session are: it's clearly off-track and a
   message can't redirect it, OR it's blocking another session that
   needs the same exclusive resource. "Tidiness" is not a reason —
   leave them alive until the day rolls over (UTC midnight).
4. **Pass `auto_create_pr=True` for fire-and-forget work.** That way
   the session finalizes itself when done instead of pausing in the
   web UI asking whether to open a PR (the second COMPLETED-state
   trap documented below). Each pending PR-approval prompt is a slot
   you're effectively holding open without intent.
5. **Use aliases to reuse sessions across tasks.** A session aliased
   `refactor-auth` can be reactivated tomorrow with new instructions
   via `jules_message` — it's a long-running agent on retainer, not
   a single-use ticket. The local registry (`sessions_state.py`) is
   built for this; refer to sessions by alias instead of throwing
   them away.

### When to spawn vs. when to reuse

| Situation | Right move |
|---|---|
| Clarifying question / plan revision / agent question / finalize-please | `jules_message` (free — same session) |
| **New work that needs its own patch deliverable** | `jules_create` (burns a slot — required, see principle #2) |
| Genuinely independent parallel work (no shared context, no shared files) | `jules_create` — burns a slot but produces real concurrency |
| The earlier session is failed/stuck and won't recover | Stop it (slot already lost) and create one fresh |
| Quota is below 10 and the work isn't urgent | Defer until UTC midnight; warn the user |

The MCP tool `jules_status_all` plus `jules_quota` together give you
the full economic picture: what slots you've burned, which are still
working for you, and how many you have left for the rest of the day.

---

## Hard Prerequisite: `JULES_API_KEY`

**Before any other action**, verify the key is present:

```bash
if [ -z "${JULES_API_KEY:-}" ]; then
  echo "ERROR: JULES_API_KEY is not set."
  echo "Run: export JULES_API_KEY=\"your-api-key-here\""
  echo "Then re-invoke this skill."
  exit 1
fi
```

If the key is missing, **stop immediately**. Do not fabricate a key, do not
prompt for it inline (it would land in chat logs), do not try to read it
from a file. Tell the user to `export JULES_API_KEY="…"` in the same
shell that launched Claude Code, then restart the session so the env var
is inherited.

If a request returns HTTP `401`, treat it as an invalid key — surface the
exact API error and ask the user to re-export.

---

## API Surface

| Action | HTTP | Path |
|---|---|---|
| Create session | `POST` | `/v1alpha/sessions` |
| List sessions | `GET` | `/v1alpha/sessions?pageSize=N&pageToken=…` |
| Get session | `GET` | `/v1alpha/sessions/{id}` |
| List activities | `GET` | `/v1alpha/sessions/{id}/activities?pageSize=N&pageToken=…` |
| Approve plan | `POST` | `/v1alpha/sessions/{id}:approvePlan` (empty body `{}`) |
| Send message | `POST` | `/v1alpha/sessions/{id}:sendMessage` (body `{"prompt":"…"}`) |
| Delete session | `DELETE` | `/v1alpha/sessions/{id}` |

**Base URL:** `https://jules.googleapis.com` (override with
`JULES_API_BASE_URL` if the user has set one).

**Authentication:** every request sends `x-goog-api-key: $JULES_API_KEY`.
For JSON bodies also send `Content-Type: application/json`.

**Always** request structured output by piping `curl` through `jq`. Never
paste raw HTTP response blobs back to the user — extract the relevant
fields.

---

## The Cognitive Loop: Session State Machine

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
| `COMPLETED` | **Ambiguous — the field lies in two distinct ways.** (1) `state=COMPLETED + outputs is null/empty` means the plan-approval gate timed out and Jules abandoned the session; treat as `AWAITING_PLAN_APPROVAL` and approve fast. (2) `state=COMPLETED + has_outputs=True` may still mean Jules is paused in the web UI asking whether to create a Pull Request for the patch it produced; the `state` field has flipped but the session is not finalized. The `sessionCompleted` activity does NOT distinguish the two — it appears in both. The only reliable resolutions are: (a) set `automationMode=AUTO_CREATE_PR` at create time so Jules opens the PR itself without asking; or (b) after harvesting the patch via `jules_patch`, send `jules_message(session_id, "no PR needed, patch applied locally")` to finalize the session. | If outputs is empty, approve the plan. If outputs is present but Jules might be waiting on PR-creation, either set automation mode up front or send a finalize message after harvest. |

**Never simulate a blocking poll loop.** The terminal is interactive; do
not freeze it. The pattern is: do *one* status check, report, hand control
back to the user. The user explicitly asks "check Jules" / "status?" to
trigger the next check. The only exception is *immediately* after
`create`, where one status check confirms `QUEUED` before yielding.

---

## Action: Argument Parsing

Parse `$ARGUMENTS` as `<action> [args...]`. Supported actions:

| Form | Behavior |
|---|---|
| `create <prompt>` | Create a session in the current repo, current branch. |
| `create --source <sources/…> --branch <branch> [--title T] [--auto-pr] [--no-approval] <prompt>` | Explicit form. |
| `list [--page-size N] [--page-token T]` | List sessions. Default page size 10. |
| `status <sessionId>` | Get session state and key fields. |
| `activities <sessionId> [--page-size N]` | List activities (default page size 10, filter for high-signal types). |
| `approve <sessionId>` | Approve the pending plan. |
| `message <sessionId> <text>` | Send conversational feedback / answer an agent question. |
| `stop <sessionId>` | Cancel and delete the session. **Confirm first.** |
| `help` | Print this usage table. |

If `$ARGUMENTS` is empty or `help`, print the table and exit.

If the user's natural-language request maps to one of these but they
didn't use the literal action verb (e.g. "ask Jules to refactor the auth
module"), translate it: that's `create` with the prompt being everything
after "Jules to" / "Jules:".

---

## Action: `create`

### 1. Resolve repository context

If `--source` is missing, infer it from the local git remote:

```bash
REMOTE_URL=$(git remote get-url origin 2>/dev/null) || true
# Examples that must work:
#   git@github.com:org/repo.git
#   https://github.com/org/repo.git
#   https://github.com/org/repo
# Result: sources/github/org/repo
```

Extract `org/repo` with a regex that strips `.git`, the URL scheme, and the
host. If the remote is missing, has multiple plausible matches, or is not
GitHub, **ask the user** for an explicit `--source` rather than guessing.

If `--branch` is missing, use `git branch --show-current`. Refuse to
proceed if it returns empty (detached HEAD) — ask the user to specify.

### 2. Build the payload

The API expects a deeply nested object. Construct it with `jq` (never
hand-concatenate JSON):

```bash
# Callers must set REQUIRE_APPROVAL to a literal 'true' or 'false'.
REQUIRE_APPROVAL="${REQUIRE_APPROVAL:-true}"

PAYLOAD=$(jq -n \
  --arg prompt "$PROMPT" \
  --arg source "$SOURCE" \
  --arg branch "$BRANCH" \
  --arg title  "$TITLE" \
  --argjson requireApproval "$REQUIRE_APPROVAL" \
  --arg automation "$AUTOMATION_MODE" \
  '{
    prompt: $prompt,
    sourceContext: {
      source: $source,
      githubRepoContext: { startingBranch: $branch }
    },
    title: ($title // empty),
    requirePlanApproval: $requireApproval,
    automationMode: ($automation // empty)
  } | with_entries(select(.value != null and .value != ""))')
```

Defaults:
- `requirePlanApproval: true` — **always default to true.** Only set false
  if the user passed `--no-approval` *and* you have surfaced a one-line
  warning that the agent will modify the codebase without their review.
- `automationMode`: omit unless `--auto-pr` was passed (then
  `AUTO_CREATE_PR`).

### 3. Call the API

```bash
TMP=$(mktemp /tmp/jules-create-XXXXXX.json)
curl -sS -o "$TMP" -w "%{http_code}" -X POST "${JULES_API_BASE_URL:-https://jules.googleapis.com}/v1alpha/sessions" \
  -H "x-goog-api-key: $JULES_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD"

jq '{name, state, title}' "$TMP"

rm -f "$TMP"
```

Extract the session ID from `name` (format: `sessions/{id}`). Echo the
**short** ID for the user:

```
Jules session created.
  ID:     <id>
  State:  QUEUED
  Title:  <title or "(untitled)">
  Source: <sources/...>
  Branch: <branch>

Run "/jules status <id>" any time to check progress, or "/jules stop <id>"
to cancel.
```

Then do **one** follow-up `status` call to confirm the state has
transitioned past `STATE_UNSPECIFIED`. Yield.

---

## Action: `list`

```bash
TMP=$(mktemp /tmp/jules-list-XXXXXX.json)
curl -sS -o "$TMP" -w "%{http_code}" "${JULES_API_BASE_URL:-https://jules.googleapis.com}/v1alpha/sessions?pageSize=${PAGE_SIZE:-10}${PAGE_TOKEN:+&pageToken=$PAGE_TOKEN}" \
  -H "x-goog-api-key: $JULES_API_KEY"

jq '{sessions: [.sessions[]? | {id: (.name | sub("^sessions/"; "")), state, title}], nextPageToken}' "$TMP"

rm -f "$TMP"
```

Render as a compact table. If `nextPageToken` is non-empty, tell the user
how to fetch the next page (`/jules list --page-token <token>`).

---

## Action: `status`

```bash
TMP=$(mktemp /tmp/jules-status-XXXXXX.json)
curl -sS -o "$TMP" -w "%{http_code}" "${JULES_API_BASE_URL:-https://jules.googleapis.com}/v1alpha/sessions/$SESSION_ID" \
  -H "x-goog-api-key: $JULES_API_KEY"

jq '{state, title, source: .sourceContext.source, branch: .sourceContext.githubRepoContext.startingBranch, outputs}' "$TMP"

rm -f "$TMP"
```

Then **act on the state** per the decision matrix above. Don't just print
the state and stop — interpret it:

- If `AWAITING_PLAN_APPROVAL`: chain straight into `activities`, find the
  plan, render it, ask for approval.
- If `AWAITING_USER_FEEDBACK`: chain straight into `activities`, find the
  question, surface it, await reply.
- If `COMPLETED`: extract output artifacts, present PR URL.
- Any other state: report and yield.

---

## Action: `activities`

```bash
TMP=$(mktemp /tmp/jules-activities-XXXXXX.json)
curl -sS "${JULES_API_BASE_URL:-https://jules.googleapis.com}/v1alpha/sessions/$SESSION_ID/activities?pageSize=${PAGE_SIZE:-10}" \
  -H "x-goog-api-key: $JULES_API_KEY" \
  > "$TMP"
```

**Filter aggressively.** A long-running session can have hundreds of
activities; do not paste all of them into context. Pull only what you
need:

- Plans: `jq '.activities[] | select(.planGenerated)' "$TMP"`
- Agent questions: `jq '.activities[] | select(.userMessaged) | select(.originator != "USER")' "$TMP"` (schema-dependent — adjust if `originator` is named differently in the response)
- Errors: any activity with an `error` field
- Completion artifacts: any with `outputs`

Render plans as readable markdown (numbered steps, one line each — not raw
JSON). Render questions verbatim, in quotes, attributed to "Jules".

If the user asks for the raw timeline, then and only then, dump a
condensed listing (timestamp + activity type + 1-line summary).

Remember to clean up:
```bash
rm -f "$TMP"
```

---

## Action: `approve`

Only valid when state is `AWAITING_PLAN_APPROVAL`. If unsure, fetch
`status` first.

```bash
TMP=$(mktemp /tmp/jules-approve-XXXXXX.json)
curl -sS -o "$TMP" -w "%{http_code}" -X POST "${JULES_API_BASE_URL:-https://jules.googleapis.com}/v1alpha/sessions/$SESSION_ID:approvePlan" \
  -H "x-goog-api-key: $JULES_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{}'

jq . "$TMP"

rm -f "$TMP"
```

A 2xx with no error is success. Confirm to the user and tell them the
session should transition to `IN_PROGRESS` shortly.

---

## Action: `message`

For user feedback in `AWAITING_USER_FEEDBACK`, or for refining/revising
during any interactive state. Build the body with `jq`:

```bash
BODY=$(jq -n --arg prompt "$TEXT" '{prompt: $prompt}')

TMP=$(mktemp /tmp/jules-message-XXXXXX.json)
curl -sS -o "$TMP" -w "%{http_code}" -X POST "${JULES_API_BASE_URL:-https://jules.googleapis.com}/v1alpha/sessions/$SESSION_ID:sendMessage" \
  -H "x-goog-api-key: $JULES_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$BODY"

jq . "$TMP"

rm -f "$TMP"
```

Confirm dispatch. Note that the session state will likely move back to
`PLANNING` or `IN_PROGRESS` depending on how Jules digests the feedback.

---

## Action: `stop`

**Destructive.** Cancels and deletes the session on Google's side. Always
confirm with the user *before* the DELETE call unless they used clearly
unambiguous language ("cancel that task", "stop Jules", "kill session
abc123"):

```bash
curl -sS -X DELETE "${JULES_API_BASE_URL:-https://jules.googleapis.com}/v1alpha/sessions/$SESSION_ID" \
  -H "x-goog-api-key: $JULES_API_KEY" \
  -w "HTTP %{http_code}\n"
```

A 2xx (often 200 with empty body, or 204) is success. Tell the user the
session is destroyed and any in-flight work is discarded.

---

## Error Normalisation

Trap HTTP errors and translate, don't dump:

| HTTP | Meaning | What to tell the user |
|---|---|---|
| `400` | Malformed payload | Echo the API's error message; check `--source` / `--branch` formats. |
| `401` | Invalid `JULES_API_KEY` | "Jules rejected the API key. Re-export `JULES_API_KEY` and try again." |
| `403` | No access to the source | "Jules cannot access `<source>`. Make sure the GitHub repo is connected via the Jules GitHub app." |
| `404` | Unknown session | "No session `<id>` found. Use `/jules list` to see active sessions." |
| `409` | Illegal state transition | E.g. approving a session that isn't awaiting approval. Run `/jules status` first. |
| `429` | Quota exceeded | Stop polling. Tell the user to wait or check their billing/quota in the Jules console. |
| `5xx` | Server error | Retryable. Suggest waiting a minute. Do not auto-retry more than once. |

Use `curl -sS -o "$TMP" -w "%{http_code}"` so the status code is emitted,
and inspect it. Then parse the body from the tempfile with `jq < "$TMP"`.

---

## Worked Examples

**Create:**
```
User: /jules create refactor the auth middleware to use JWT and cover it with integration tests
Skill:
  Detected source: sources/github/netzkontrast/the-agency-system
  Detected branch: claude/create-jules-skill-x8QHA
  Plan approval: REQUIRED (default)

  Created. ID: 7f3a91c2-…  State: QUEUED
  → Polled once: state is now PLANNING.
  Run "/jules status 7f3a91c2-…" in a minute to check progress.
```

**Status with plan ready:**
```
User: /jules status 7f3a91c2-…
Skill:
  State: AWAITING_PLAN_APPROVAL

  Jules has drafted this plan:
    1. Replace cookie-session middleware with jsonwebtoken in src/auth/
    2. Add JWT secret env var (JWT_SECRET) with dotenv fallback
    3. Add tests/integration/auth.spec.ts covering login + refresh
    4. Update README env-var section

  Approve, request changes, or cancel?
```

**Agent asks a question:**
```
User: /jules status 7f3a91c2-…
Skill:
  State: AWAITING_USER_FEEDBACK
  Jules asks: "The auth module currently has no mock interface. Should I
  add one in tests/mocks/, or wire the integration tests directly against
  the real middleware?"
  Reply with: /jules message 7f3a91c2-… <your answer>
```

**Completed:**
```
User: /jules status 7f3a91c2-…
Skill:
  State: COMPLETED
  Jules opened a pull request:
    https://github.com/netzkontrast/the-agency-system/pull/42
```

---

## Behavioural Acceptance (Gherkin — for reference, not for execution)

These are the contracts this skill must satisfy. Use them as guard rails
when in doubt about what to do:

```gherkin
Feature: API key gate
  Scenario: Missing key
    Given JULES_API_KEY is unset
    When the user invokes any action
    Then the skill exits with an instruction to export the variable
    And no HTTP request is made.

Feature: Plan approval circuit breaker
  Scenario: Session reaches AWAITING_PLAN_APPROVAL
    Given a session was created with requirePlanApproval=true
    When the skill checks status
    Then it fetches the planGenerated activity
    And renders the plan as readable markdown
    And asks the user to approve, revise, or cancel
    And does not proceed without an explicit decision.

Feature: Bidirectional feedback
  Scenario: Jules requests clarification
    Given a session is in AWAITING_USER_FEEDBACK
    When the skill checks status
    Then it surfaces the agent's question verbatim
    And the user's reply is dispatched via sendMessage.

Feature: Destructive cancel requires confirmation
  Scenario: User says "stop"
    Given an active session
    When the user issues an unambiguous cancel ("stop", "cancel", "kill")
    Then the skill calls DELETE on the session
    Otherwise it confirms first.

Feature: No tight polling
  Scenario: Session is QUEUED, PLANNING, or IN_PROGRESS
    Then the skill performs at most one status check per user request
    And does not loop in the terminal.
```

---

## Background Watcher (`watch_jules.py`)

A companion Python script (`watch_jules.py`, stdlib only — no install)
polls Jules sessions and writes a JSON-lines notification any time a
session crosses into a state that needs your attention
(`AWAITING_PLAN_APPROVAL`, `AWAITING_USER_FEEDBACK`, `COMPLETED`,
`FAILED`, `PAUSED`). For `AWAITING_USER_FEEDBACK` it also fetches and
embeds the agent's question text.

```bash
# Watch every active session (Ctrl-C to stop)
python3 .claude/skills/jules/watch_jules.py

# Watch one session and exit when it terminates
python3 .claude/skills/jules/watch_jules.py --session 5740936444374394996

# Suppress noisy intermediate transitions (QUEUED/PLANNING/IN_PROGRESS)
python3 .claude/skills/jules/watch_jules.py --quiet-transitions

# Custom interval / log location
python3 .claude/skills/jules/watch_jules.py --interval 15 --log /tmp/jules.jsonl
```

The default log lives at `.claude/skills/jules/notifications.jsonl` (in
`.gitignore`). The watcher uses exponential backoff: it polls every
30s when something is happening, then stretches up to 5 min during
quiet periods to stay under Jules' rate limits. SIGINT/SIGTERM stop
it cleanly.

To check what changed without re-running the watcher, just `tail` the log:

```bash
tail -f .claude/skills/jules/notifications.jsonl | jq -c '{time, session, state, note}'
```

## Parallel Orchestration

You can run **many Jules sessions in parallel**. This is the canonical
flow for fan-out work (e.g. apply the same change across N tracks,
review N PRs, generate N test files):

### 1. Fan out

Provide a JSON or YAML file with one entry per task (see
`.claude/skills/jules/examples/fanout-tasks.json`). Each entry has
`{alias, title, prompt}` and optionally `{branch, source}`.

**Every prompt should include the branch convention** so harvest
goes through git, not patches:

> "When done, push your work to branch `jules/<alias>` on the source
> repository. Do NOT open a pull request."

This makes the alias the link between the local registry and the
remote branch — `jules_resolve_alias("auth-fix")` returns the
session id, and `origin/jules/auth-fix` holds the work.

Then:

```bash
JULES_DEFAULT_SOURCE="sources/github/<org>/<repo>" \
  ./.claude/skills/jules/jules_bulk.sh fanout tasks.json
```

Each entry creates one session and registers it in `sessions.json` with
its alias so you can refer to it by name (`auth-fix`) instead of the
19-digit id.

Equivalently in MCP: call `jules_create` once per task in a single
turn. The Jules API accepts concurrent session creation; rate limits
apply per account.

### 2. Watch all of them at once

```bash
python3 .claude/skills/jules/watch_jules.py --daemonize
```

The watcher polls every session, writes one JSON line per state
transition to `notifications.jsonl`, and pushes the latest state into
the registry so `dashboard` always has fresh data.

### 3. Use the dashboard to triage

```bash
./.claude/skills/jules/jules_bulk.sh dashboard
```

Lists every active session in a compact table: alias | id | state |
title. Sessions in `AWAITING_PLAN_APPROVAL` are highlighted — those are
the ones blocking on you.

For an in-context check during a chat turn, call `jules_status_all`
(one API request, all sessions grouped by state).

### 4. Review the plan FIRST, then approve (do not auto-approve)

**The plan-approval gate is your cheapest review point. Do not
bypass it.** A misaligned plan caught at the AWAITING_PLAN_APPROVAL
stage costs one `jules_message` to redirect; the same misalignment
caught after the patch lands costs a re-spawn (a slot) and a full
fresh planning cycle.

The workflow for every fan-out:

1. Wait for each session to reach `AWAITING_PLAN_APPROVAL` (watch
   `jules_status_all` periodically, or run the watcher daemon).
2. For each one, call `jules_plan(session_id)` and READ THE STEPS.
   Check: are the right files in scope? Are the wrong files
   excluded? Is the plan over-engineered? Under-scoped?
3. If the plan is good, call `jules_approve(session_id)` —
   manually, one at a time.
4. If the plan needs refinement, call `jules_message(session_id,
   "<specific feedback>")`. The session will replan; loop back to
   step 1.
5. **Bulk-approve (`jules_approve_awaiting`) is for the case where
   you have ALREADY individually reviewed each plan and they are
   all good.** It is not for "auto-approve everything that's
   waiting" — that pattern wastes the review opportunity.

Auto-approving drivers (`while AWAITING: approve()`) are an
antipattern: they remove your cheapest course-correction lever and
guarantee you'll integrate work you didn't actually want. Only use
them when you've explicitly decided this batch doesn't warrant
review (e.g. a known-safe templated fan-out you've validated
before).

When you have N plans waiting AND you have already inspected them
in the dashboard or via `jules_plan`, you can batch-approve:

```bash
./.claude/skills/jules/jules_bulk.sh approve-awaiting
```

Or in MCP:

```
jules_approve_awaiting(only_titles_contain="lyric-review")
```

The `only_titles_contain` filter is your safety net — restrict the
bulk-approve to a known prefix so a stray unrelated session can't be
swept in.

### 5. Harvest patches via `jules_patch_apply` (canonical)

The integrator-via-PR pattern is conceptually appealing but
**empirically unreliable on this account**: setting
`auto_create_pr=True` is silently ignored (the response shows
`automationMode: None`, no branch is pushed, no PR is opened —
verified on session `4878612101900714069`). Prompt-level
instructions to push or open PRs also fail or hallucinate
completion. The working harvest path is patches:

```python
jules_patch_summary(session_id)         # metadata only — files, line counts
jules_patch_apply(session_id, dry_run=True)   # validate cleanly
jules_patch_apply(session_id)           # apply on disk, token-cheap
```

The full unidiff is written to a tempfile, fed to `git apply`, and
discarded. Only metadata (`{applied, files, lines_added,
lines_removed, base_commit, suggested_commit_message}`) flows back
through the model — ~200 bytes vs. a diff that can be tens of KB.
This works reliably even when PR / branch publishing does not.

**The integrator-via-PR pattern remains valid in principle.** When
you confirm it works on your account (i.e. setting
`auto_create_pr=True` actually publishes a branch and opens a PR),
use it — it's strictly better than patches (richer audit trail,
multi-iteration history, cherry-pick granularity). The patch path
is the *fallback* when the publish path is unavailable. Probe with
one session before relying on either.

**The instruction template for `jules_create`:**

> "When done, make your work retrievable on the remote — your
> choice of mechanism: push to a branch named `jules/<slug>` if
> your tooling supports it, otherwise a draft PR or a regular
> PR from such a branch. Reply with the exact branch name and
> PR URL (if any). The PR is for integration, not necessarily
> for merging."

Equivalent in code: `jules_create(..., auto_create_pr=True)` is
the most reliable signal, but for some setups the prompt-level
instruction works too. When in doubt, set the flag AND include the
prompt sentence.

**The integrator flow once the branch lands:**

```
git fetch origin
git branch -r | grep jules/                                   # discover
git log --oneline <my-branch>..origin/jules/<slug>            # what's there
git diff <my-branch>...origin/jules/<slug> --stat             # scope
git diff <my-branch>...origin/jules/<slug> -- path/to/file    # only when needed
gh pr view <pr-number>                                        # PR body & metadata, if a PR was opened
```

**Then integrate at the granularity you want:**

```
git cherry-pick <commit-on-jules-branch>                # one commit
git checkout origin/jules/<slug> -- path/to/file        # one file
git merge --no-ff origin/jules/<slug>                   # the whole branch
```

If a PR was opened, **close it without merging** when you've
cherry-picked what you wanted — the closed PR is the audit
record. If no PR was opened, the branch itself is the record;
delete it from the remote once integrated, or leave it as a
historical reference.

**Why this beats both raw patches and "no PR please":**

- Zero token cost for diff inspection (git output never enters the
  model's context).
- Works with Jules's actual capabilities — no instructions Jules
  interprets the wrong way (the "don't open a PR" framing reliably
  causes some sessions to conflate it with "don't push").
- Real git history per session: blame, log, bisect, cherry-pick
  all work normally.
- The PR (when one exists) is metadata you can comment on / link
  to — useful for multi-orchestrator coordination.
- Multiple iterations on the same session push additional commits
  to the same branch — defuses the "outputs[].gitPatch is set
  only once" trap from principle #2 above.

**When to fall back to patches:**

- The target repo doesn't accept Jules's push or PR scope (rare).
- You need to transform the diff in-context before applying
  (e.g. strip unrelated changes). Use `jules_patch_summary` first,
  then `jules_patch` with explicit `max_bytes` if truly necessary.
- `jules_patch_apply(session_id, dry_run=True)` is still the
  preferred way to land a unified-diff locally when the integrator
  pattern doesn't apply.

**Two `COMPLETED` traps you must defuse:**

1. **`COMPLETED` with empty `outputs` = abandoned.** The plan-approval
   gate timed out before you approved. Use `jules_get` to check
   `has_outputs` before treating any session as a deliverable.
2. **`COMPLETED` with `has_outputs=True` may still be waiting on a
   "Create PR?" UI prompt.** The patch is real and harvestable, but
   the session is not finalized — it's sitting in the Jules web UI
   asking the human whether to open a PR. To finalize cleanly when
   you've already applied the patch locally:

   ```python
   jules_message(session_id, "Patch applied locally — no PR needed. Finalize.")
   ```

   To avoid the trap entirely on a fresh session, pass
   `auto_create_pr=True` at create time and let Jules open the PR
   without asking. Choose your default based on whether you want
   patches piped into your branch (current default) or independent
   PRs (auto mode).

### Caveats for parallel work

- **Approve quickly.** The Jules backend appears to discard sessions
  that sit in `AWAITING_PLAN_APPROVAL` for too long — they end up in
  `COMPLETED` state with empty `outputs`. **Treat `COMPLETED + empty
  outputs` as `AWAITING_PLAN_APPROVAL`**: fetch the plan and approve,
  or the work is lost.
- **Scope tasks to disjoint files.** Parallel sessions branch from the
  same base commit, so patches that touch the same file will conflict
  on apply.
- **Use aliases.** 19-digit ids are unusable in conversation; aliases
  scale to dozens of sessions without confusion.
- **Watch out for stale `list` responses.** `jules_list` can show a
  session as `IN_PROGRESS` for a few seconds after `jules_get` reports
  the real state. Use `jules_get` (per-session) as the authoritative
  state, not `jules_list`.
- **No more than 4 concurrent approves.** `jules_bulk.sh
  approve-awaiting` uses `xargs -P 4`. Higher concurrency risks 429s.

## What This Skill Does NOT Do

- **Does not edit local files.** Jules works on its own VM and pushes to
  the user's GitHub via the Jules GitHub app. The skill never modifies the
  local working tree on the user's behalf as part of a Jules session.
- **Does not commit or push.** The output is a Jules-generated PR URL.
- **Does not poll in the background.** Each status check is initiated by
  a fresh user prompt.
- **Does not cache the API key.** It is read live from `JULES_API_KEY`
  every invocation.
- **Does not retry destructive failures automatically.** A failed
  `approve`, `message`, or `stop` is reported, not silently re-attempted.
