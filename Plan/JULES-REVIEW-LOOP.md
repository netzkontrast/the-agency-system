# JULES-REVIEW-LOOP.md

> **Audience:** The orchestrator (a Claude Code session, human, or a wrapping script). NOT for Jules to consume directly. Jules's contract is `JULES_PROTOCOL.md`; this file describes how Jules is *invoked, watched, and reviewed* by something else.

> **Goal:** Drive each phase from `Plan/000-overview.md` to merged through a deterministic, mostly-hands-off loop: dispatch → watch → recover-if-needed → review → iterate → merge. Up to 60 Jules sessions in flight at once. The orchestrator's main context stays small because all heavy work happens in Jules sandboxes or local subagents.

---

## 1. The five primitives

The loop is built from five primitives. Every one of them is already implemented in `servers/agency-mcp/handlers/jules/` (ported from `jules-plugin` per Spec 006) — none of this section requires net-new code; it's a procedure spec, not an implementation spec.

| Primitive | What it does | Backing tool |
|---|---|---|
| **Dispatch** | Create one Jules session per spec, with a focused prompt | `jules_create` (MCP) or `bin/jules-bulk fanout <file.json>` (CLI) |
| **Watch** | Poll all in-flight sessions for state transitions | `jules_status_all` (MCP) or `bin/watch_jules.py` (CLI) |
| **Recover** | When `state=COMPLETED` but no branch on origin: probe, then API-extract patch, then push via GitHub MCP | `jules_message` → `tools/jules-patch-extract.py` → `mcp__github__create_branch` + `create_or_update_file` + `create_pull_request` |
| **Review** | Dispatch a Jules session whose entire job is to review an open PR and post comments | `jules_create` with `REVIEW_PROMPT_TEMPLATE` below |
| **Merge** | Close the loop when a review session returns < 1 substantive comment | `mcp__github__merge_pull_request` |

The orchestrator never edits Jules's branches itself except via the recovery path. Reviews land as PR comments, not commits.

---

## 2. The phase loop (canonical)

```
INPUT:  phase_id, list[spec_dir]
OUTPUT: list[merged_pr_url]

# 2.a Dispatch (one fanout per parallel-safe group within the phase)
for group in groups_of(spec_dirs):                  # see §2.5 grouping rule
    fanout_payload = [
        {
            "title":  f"Spec {spec.id} — {spec.slug}",
            "prompt": render_prompt("templates/spec-impl.md.j2", spec=spec, phase=phase_id),
            "source": "netzkontrast/the-agency-system",
            "branch_hint": f"jules/agency-{spec.id}-<short-sid>",
        }
        for spec in group
    ]
    sids = jules_bulk_fanout(fanout_payload)        # returns session ids
    register_sessions(sids, phase_id, spec_ids)     # writes ~/.agency-system/sessions.json

# 2.b Watch (one Monitor; runs until all this-phase sessions hit a terminal state)
monitor_watch_jules_sessions(
    sids,
    interval_seconds=180,                           # 3-minute poll cadence
    on_event=handle_event,                          # see §3
)

# 2.c On each session terminal:
#       - state=COMPLETED + branch_on_remote? → open PR (Jules's publication flow already did this) → §4 review
#       - state=COMPLETED + NO branch_on_remote? → §5 recovery → §4 review
#       - state=FAILED                              → log to _lessons-learned/, escalate
#       - state=AWAITING_PLAN_APPROVAL              → jules_approve (auto-approve once confidence ≥ 0.90) OR escalate

# 2.d Review loop per PR (§4)
for pr in opened_prs:
    iterate_review_until_clean(pr, max_rounds=5)

# 2.e Merge each clean PR (§6)
for pr in clean_prs:
    mcp_github_merge_pull_request(pr, merge_method="squash")

# 2.f Update Plan/000-overview.md §2.1 with the new "Done" rows
```

### 2.5 Grouping rule

Within a phase, group specs so that **no two sessions in the same fanout write to the same file**. The dispatch matrices in `Plan/000-overview.md` §9 already encode this; the implementation may further split for safety but never merges across groups that the matrix marks sequential.

---

## 3. Watch event handling

The watcher emits one JSON line per state transition. Routing:

| Event | Action |
|---|---|
| `state=IN_PROGRESS → AWAITING_PLAN_APPROVAL` | Check the plan body. If confidence ≥ 0.90 (gate 1 from `JULES_PROTOCOL`), call `jules_approve`. Else escalate via `@human:` comment on the draft PR. |
| `state=* → COMPLETED` | Wait 60 s (Jules's auto-publication flow may still be in-flight), then check `mcp__github__list_branches`. If branch present → §4. If absent → §5 recovery. |
| `state=* → FAILED` | Read last activity via `jules_activities` (summary_only=true). If retryable (transient API error), restart the same session via `jules_message` with the same prompt. If genuine failure (e.g. spec ambiguity), append to `Plan/_lessons-learned/` and stop. |
| `inactivity for > 2 h while IN_PROGRESS` | Probe with `jules_message`: "status?". One probe only. If no response in 30 min → treat as silent-fail; escalate. |

The watcher itself is persistent (a single `Monitor` invocation for the entire phase), so the orchestrator's main context only sees one notification per terminal event — never the raw API response.

---

## 4. The review loop (the back-and-forth)

This is what the user's goal calls "use Jules to write a review and go back and forth until no relevant feedback surfaces". The loop:

```
def iterate_review_until_clean(pr, max_rounds):
    for round in range(max_rounds):
        sid = jules_create(
            title=f"Review PR #{pr.number} — round {round + 1}",
            prompt=REVIEW_PROMPT_TEMPLATE.format(
                pr_url=pr.html_url,
                phase=pr.phase_id,
                spec=pr.spec_id,
                round=round + 1,
            ),
            source=pr.head_repo,
        )
        wait_until_completed(sid)                      # uses §3 watcher
        comments = mcp_github_pull_request_read(
            method="get_review_comments", pull_number=pr.number,
        )
        substantive = triage(comments)                 # see §4.2

        if len(substantive) == 0:
            return pr                                  # clean; merge

        # Spawn a follow-up Jules session pointing at the same branch
        # with the substantive comments as the fix brief.
        fix_sid = jules_create(
            title=f"Fix review feedback for PR #{pr.number} — round {round + 1}",
            prompt=FIX_PROMPT_TEMPLATE.format(
                pr_url=pr.html_url,
                substantive_comments=substantive,
                branch=pr.head_branch,
            ),
            source=pr.head_repo,
            existing_branch=pr.head_branch,            # IMPORTANT: stay on branch
        )
        wait_until_completed(fix_sid)
        # Loop continues: next round runs a fresh review against the new commits.

    raise NotConvergedError(f"PR #{pr.number} did not converge in {max_rounds} rounds")
```

### 4.1 The review prompt template (verbatim — paste into Jules)

```markdown
You are the independent reviewer for PR #{pr_number} on `netzkontrast/the-agency-system`.

CONTEXT:
- Phase: {phase} (see Plan/000-overview.md)
- Spec:  {spec} (see Plan/{spec}/spec.md)
- Round: {round}/5

YOUR JOB:
1. Read the spec and the PR diff.
2. Run the spec's smoke tests against the PR branch. Paste the last 20 lines.
3. Apply gates 1-4 from JULES_PROTOCOL.md as a REVIEWER (not implementer):
   - Gate 1 (Confidence): did the implementer actually fulfil the spec? Score on the 5-criterion table.
   - Gate 3 (Evidence): is each Done-When line evidence-backed in the PR body?
   - Look for drift: anything implemented OUTSIDE the spec's affects: list?
4. Post one PR review comment per finding. Severity prefix:
   [BLOCKING] = must fix before merge
   [SUBSTANTIVE] = should fix, will be addressed in next round
   [NIT] = cosmetic; reviewer ignores in triage

YOU MUST NOT:
- Push code changes — comment only.
- Approve or request-changes via the GitHub review API — leave that to the orchestrator.
- Comment on style or formatting issues unless they violate JULES_PROTOCOL.md.

YOU MUST:
- Render the gate-1 confidence table in the review summary comment.
- Include a final "no further substantive findings" line ONLY if you have zero [BLOCKING] and zero [SUBSTANTIVE] findings. The orchestrator searches for that line.
```

### 4.2 Triage (substantive vs not)

```python
def triage(comments):
    return [c for c in comments
            if c.body.startswith("[BLOCKING]") or c.body.startswith("[SUBSTANTIVE]")]
```

The orchestrator does NOT triage `[NIT]` comments. They land on the PR for the human author to glance at and resolve later; they do not block merge.

### 4.3 The fix prompt template (verbatim — paste into Jules)

```markdown
You are fixing review feedback on an open PR.

PR: {pr_url}
Branch: {branch} — STAY ON THIS BRANCH; do not create a new one.

FEEDBACK TO ADDRESS:
{substantive_comments_rendered_as_numbered_list}

YOUR JOB:
1. Read each feedback item.
2. For each one, write a failing test that captures the regression (or a missing-evidence test if the feedback is about Gate 3).
3. Apply the fix. Re-run the test until green.
4. Commit with subject: "fix(review): address #{comment_id} — {short_summary}"
5. Push to {branch}. Publish via the standard flow (your runtime's submit/auto-PR tool — the PR already exists, your commit will land on it).
6. Reply to each addressed comment with a one-line note + the commit SHA.

GATES (per JULES_PROTOCOL.md) STILL APPLY. Do not bypass.
```

### 4.4 Convergence stop condition

The loop terminates when:
- A review round returns `len(substantive) == 0`, **and**
- The review session's summary comment contains the verbatim string `"no further substantive findings"`.

Both conditions are required to defend against false-positive empty triage.

If 5 rounds elapse without convergence, the orchestrator escalates: posts `@human: PR #X stuck after 5 review rounds — last review {sid}` and stops loop for that PR.

---

## 5. Recovery (silent-fail path)

When `state=COMPLETED` but no branch lands on origin, follow `JULES_PROTOCOL.md` §8-Appendix verbatim. The orchestrator script:

```python
def recover_completed_no_branch(sid):
    # Step 1 — probe (per appendix)
    jules_message(sid, "your state is COMPLETED but I can't find your branch on origin — please publish and reply with PR URL")
    if wait_for_publish(sid, timeout_minutes=10):
        return                                        # Jules pushed; done

    # One more probe
    jules_message(sid, "still no branch — please retry the publication flow")
    if wait_for_publish(sid, timeout_minutes=10):
        return

    # Step 2 — API extraction (deterministic)
    patch_info = run_command(
        f"PYTHONPATH=servers/agency-mcp/src python3 tools/jules-patch-extract.py {sid}"
    )
    # Note: patch is written to /tmp/jules-patches/{sid}-out0.patch
    # stdout shows only stats — never echo patch body

    # Step 3 — push via GitHub MCP (signed web-flow commits)
    branch = f"jules-recovered/{sid[-8:]}"
    mcp_github_create_branch(branch, from_branch="Master")
    for file in patch_info["files"]:
        mcp_github_create_or_update_file(
            path=file["path"],
            content=file["new_content"],
            branch=branch,
            message=f"feat: recovered Spec {phase_id} from Jules sid {sid[-8:]}",
        )
    pr = mcp_github_create_pull_request(
        head=branch,
        base="Master",
        title=f"Spec {spec_id} — recovered via API extraction",
        body=render_recovery_pr_body(sid, patch_info),
    )
    # Continue to §4 review loop with this PR
```

The recovery path is **NEVER** a re-dispatch of a fresh Jules session for the same work — that wastes a slot of the 60-session quota and risks divergent output. Re-dispatch is reserved for genuine implementation failures.

---

## 6. Merge gate

A PR is merged when ALL of:
- §4.4 convergence (no substantive findings, latest review contains the verbatim string).
- CI green (`tests/smoke/*.py` and any spec-specific CI workflow).
- `## Evidence` section populated per `JULES_PROTOCOL.md` Gate 3.
- For Phase 1+: boot budget assertion passes (`tools/list` payload < 4 KB).

Merge method: `squash` for spec PRs, `merge` for phase-cleanup PRs that include reverts.

---

## 7. Quota management

Jules quota = 60 concurrent sessions. The orchestrator tracks in-flight count via `jules_quota` (MCP). Dispatch gating:

```python
def gated_fanout(payload):
    quota = jules_quota()
    in_flight = quota["in_flight_count"]
    budget = 60 - in_flight
    if len(payload) <= budget:
        return jules_bulk_fanout(payload)
    # Split: fanout the first `budget` entries; queue the remainder
    return (
        jules_bulk_fanout(payload[:budget])
        + queued_fanout(payload[budget:])               # waits for slot in §2.b watcher
    )
```

The 60-session ceiling is rarely binding; the typical phase opens 4-10 sessions. Phase 8 is the only phase that could realistically fill the quota (≤ 10 specs). Watch for the binding-quota signal in lesson-15.

---

## 8. Idempotency under crashes

The orchestrator can crash and resume mid-phase. Resume guarantees:

| State on disk | After crash, orchestrator does |
|---|---|
| `~/.agency-system/sessions.json` | Re-loads in-flight session list; resumes §2.b watcher |
| Open PRs without `claude-review-cycle` label | Treats as awaiting review; restarts §4 loop at round 1 |
| Open PRs with `claude-review-cycle: round-N` label | Resumes §4 loop at round N+1 |
| Closed PRs with `claude-merged` label | Skip; included in §2.f overview update |

The orchestrator writes the `claude-review-cycle: round-N` label via `mcp__github__issue_write` (issue API works on PRs) at the start of each round, and a `claude-merged` label after §6 succeeds.

---

## 9. Failure modes and escalation

| Symptom | Diagnosis | Action |
|---|---|---|
| Review session itself fails 3 rounds in a row | Review prompt may be ambiguous against the spec | Stop loop; escalate `@human:` |
| Fix session widens PR scope (touches files outside spec.affects:) | Scope creep | Reply on PR: "fix session widened scope to {file}. Please revert and try again with tighter prompt." Restart fix session. |
| Convergence stalls but smoke test passes anyway | Tests may be missing coverage | Add a [SUBSTANTIVE] review comment requesting test addition; continue loop |
| `jules_status_all` returns `quota_exceeded` | Hit the 60-session ceiling | Pause fanout; wait for completions; resume |
| `tools/jules-patch-extract.py` returns 0-file patch | Genuine empty session (Jules did nothing) | Mark spec for re-dispatch with revised prompt; log to `_lessons-learned/` |

All escalations are `@human:` PR comments — never DMs, never external channels. The PR thread is the canon.

---

## 10. Observability

Every phase run produces:

- `~/.agency-system/cache/orchestrator-runs/{phase}-{timestamp}.json` — full event log
- `Plan/_lessons-learned/{NN}-{slug}.md` — one entry per phase (reflexion contract)
- Updates to `Plan/000-overview.md` §2.1 — Done table

The cache file is the source of truth for re-running a phase from scratch (eg. after a destructive `git reset`).

---

## 11. First invocation (this PR)

This is the first PR. The orchestration loop is **about to be exercised** on the PR that lands these two files. Concretely:

1. Push branch `claude/check-installed-plugins-1rf3k` to origin.
2. Open PR to `Master` with title "Plan v2 — unified plugin orchestration spec".
3. Dispatch one Jules review session using §4.1 with `spec={meta: 000-overview + JULES-REVIEW-LOOP}`.
4. Iterate per §4 until clean.
5. Merge per §6.

The PR's smoke test is the existence of these two files, the absence of stale references in `Plan/000-overview.md` (e.g. the v1 "PICK ONE PATH" line is gone), and the explicit Done/In-progress/Scaffolded audit lining up with `git ls-files Plan/`.

The success of this very first review-cycle is the validation that Phase 0 can proceed.
