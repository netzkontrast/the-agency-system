---
name: jules
description: >
  Delegates long-running codebase tasks (refactors, multi-file edits, test
  generation, feature implementation, automated PR creation) to the Google
  Jules asynchronous coding agent over its REST API. Use when the user
  mentions "Jules", "remote agent", "asynchronous task", or asks for a
  cloud-side coding job that would block the local terminal if run
  synchronously.
argument-hint: <action> [args...]   # actions: create | list | status | activities | approve | message | stop | help
model: claude-sonnet-4-6
allowed-tools:
  - Bash
  - Read
---

## Your Task

**Input:** `$ARGUMENTS`

You are an orchestrator for the Google Jules asynchronous coding agent. The
user's local terminal is a control plane; Jules is the remote worker. Your
job is to start, monitor, decide on, interact with, and stop Jules sessions
on the user's behalf — never to simulate the work locally.

This skill talks to the Jules REST API directly via `curl`. There is no
separate MCP server. Authentication uses the `JULES_API_KEY` environment
variable set in the user's shell.

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
| `COMPLETED` | Done | Extract `outputs` (look for the PR URL in `pullRequest`/`outputs[].pullRequest.url` — schema may vary), present the artifact link, exit cleanly. |

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
PAYLOAD=$(jq -n \
  --arg prompt "$PROMPT" \
  --arg source "$SOURCE" \
  --arg branch "$BRANCH" \
  --arg title  "$TITLE" \
  --argjson requireApproval $REQUIRE_APPROVAL \
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
curl -sS -X POST "${JULES_API_BASE_URL:-https://jules.googleapis.com}/v1alpha/sessions" \
  -H "x-goog-api-key: $JULES_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD" \
  | tee /tmp/jules-create-response.json \
  | jq '{name, state, title}'
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
curl -sS "${JULES_API_BASE_URL:-https://jules.googleapis.com}/v1alpha/sessions?pageSize=${PAGE_SIZE:-10}${PAGE_TOKEN:+&pageToken=$PAGE_TOKEN}" \
  -H "x-goog-api-key: $JULES_API_KEY" \
  | jq '{sessions: [.sessions[]? | {id: (.name | sub("^sessions/"; "")), state, title}], nextPageToken}'
```

Render as a compact table. If `nextPageToken` is non-empty, tell the user
how to fetch the next page (`/jules list --page-token <token>`).

---

## Action: `status`

```bash
curl -sS "${JULES_API_BASE_URL:-https://jules.googleapis.com}/v1alpha/sessions/$SESSION_ID" \
  -H "x-goog-api-key: $JULES_API_KEY" \
  | jq '{state, title, source: .sourceContext.source, branch: .sourceContext.githubRepoContext.startingBranch, outputs}'
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
curl -sS "${JULES_API_BASE_URL:-https://jules.googleapis.com}/v1alpha/sessions/$SESSION_ID/activities?pageSize=${PAGE_SIZE:-10}" \
  -H "x-goog-api-key: $JULES_API_KEY" \
  > /tmp/jules-activities.json
```

**Filter aggressively.** A long-running session can have hundreds of
activities; do not paste all of them into context. Pull only what you
need:

- Plans: `jq '.activities[] | select(.planGenerated)'`
- Agent questions: `jq '.activities[] | select(.userMessaged) | select(.originator != "USER")'` (schema-dependent — adjust if `originator` is named differently in the response)
- Errors: any activity with an `error` field
- Completion artifacts: any with `outputs`

Render plans as readable markdown (numbered steps, one line each — not raw
JSON). Render questions verbatim, in quotes, attributed to "Jules".

If the user asks for the raw timeline, then and only then, dump a
condensed listing (timestamp + activity type + 1-line summary).

---

## Action: `approve`

Only valid when state is `AWAITING_PLAN_APPROVAL`. If unsure, fetch
`status` first.

```bash
curl -sS -X POST "${JULES_API_BASE_URL:-https://jules.googleapis.com}/v1alpha/sessions/$SESSION_ID:approvePlan" \
  -H "x-goog-api-key: $JULES_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{}' \
  | jq .
```

A 2xx with no error is success. Confirm to the user and tell them the
session should transition to `IN_PROGRESS` shortly.

---

## Action: `message`

For user feedback in `AWAITING_USER_FEEDBACK`, or for refining/revising
during any interactive state. Build the body with `jq`:

```bash
BODY=$(jq -n --arg prompt "$TEXT" '{prompt: $prompt}')

curl -sS -X POST "${JULES_API_BASE_URL:-https://jules.googleapis.com}/v1alpha/sessions/$SESSION_ID:sendMessage" \
  -H "x-goog-api-key: $JULES_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$BODY" \
  | jq .
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

Use `curl -sS -w '\nHTTP %{http_code}\n'` so the status code is always
visible, and inspect it with `tail -1` before parsing the body.

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
