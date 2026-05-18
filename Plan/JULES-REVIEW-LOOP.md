# JULES-REVIEW-LOOP.md

> **Audience:** The orchestrator (a Claude Code session, human, or a wrapping script). NOT for Jules to consume directly. Jules's contract is `JULES_PROTOCOL.md`; this file describes how Jules is *invoked, watched, and reviewed* by something else.

> **Goal:** Drive each phase from `Plan/000-overview.md` to merged through a deterministic, mostly-hands-off loop: dispatch → watch → recover-if-needed → review → iterate → merge. Up to 60 Jules sessions in flight at once. The orchestrator's main context stays small because all heavy work happens in Jules sandboxes or local subagents.

---

## 1. The five primitives

The loop is built from five primitives. Every one of them is already implemented in `servers/agency-mcp/handlers/jules/` (ported from `jules-plugin` per Spec 006) — none of this section requires net-new code; it's a procedure spec, not an implementation spec.

| Primitive | What it does | Backing tool |
|---|---|---|
| **Dispatch** | Create one Jules session per spec, with a focused prompt | `jules_create` (MCP) iterated in Python, or `bin/jules-bulk fanout <file.json>` shell helper |
| **Watch** | Poll all in-flight sessions for state transitions | `jules_status_all` (MCP) — or the Python script in `jules-plugin/lib/watch_jules.py` (re-homed to `bin/watch_jules.py` in Phase 0 cleanup; until that ships, the path is `jules-plugin/lib/watch_jules.py`). The orchestrator's own canonical watcher is a single persistent `Monitor` (see §3). |
| **Recover** | When `state=COMPLETED` but no branch on origin: probe, then run `tools/jules-patch-extract.py <sid>` (writes the patch to `/tmp/jules-patches/{sid}-out{i}.patch` and emits stats only — does NOT return file bodies), then parse that on-disk patch and push via GitHub MCP | `jules_message` → `tools/jules-patch-extract.py` → parse `.patch` → `mcp__github__create_branch` + per-`file_change.op` routing (`create_or_update_file` for add/modify, `delete_file` for delete + rename-source — see §5 `apply_change`) + `create_pull_request` |
| **Review** | Dispatch a Jules session whose entire job is to review an open PR and post comments | `jules_create` with `REVIEW_PROMPT_TEMPLATE` below |
| **Merge** | Close the loop when a review session returns < 1 substantive comment | `mcp__github__merge_pull_request` |

The orchestrator never edits Jules's branches itself except via the recovery path. Reviews land as PR comments, not commits.

---

## 2. The phase loop (canonical)

```
INPUT:  phase_id, list[spec_dir]
OUTPUT: list[merged_pr_url]

# 2.a Dispatch (one fanout per parallel-safe group within the phase)
#     `jules_bulk_fanout` is NOT a single helper — it's either a Python loop
#     over `jules_create` OR a shell call to `bin/jules-bulk fanout <file>`.
#     Both produce the same outcome; we model the Python form here for clarity.
all_sids = []                                       # accumulate across groups
for group in groups_of(spec_dirs):                  # see §2.5 grouping rule
    for spec in group:
        res = jules_create(
            prompt=render_prompt("templates/spec-impl.md.j2", spec=spec, phase=phase_id),
            source="netzkontrast/the-agency-system",
            starting_branch="Master",               # the supported kwarg
            title=f"Spec {spec.id} — {spec.slug}",
            require_plan_approval=True,
            auto_create_pr=True,                    # IMPORTANT: jules_create defaults
                                                    # auto_create_pr=False, which lets
                                                    # sessions complete without ever
                                                    # publishing a branch — the watcher
                                                    # would then misclassify them as
                                                    # silent-fail. Always pass True for
                                                    # implementation sessions; review
                                                    # sessions in §4 also pass True so
                                                    # convergence detection works.
        )
        sid = (res.get("name") or res.get("id") or "").replace("sessions/", "")
        register_session(sid, phase_id, spec.id)    # writes ~/.agency-system/cache/sessions.json
        all_sids.append(sid)

# 2.b Watch (one persistent Monitor; runs until every this-phase session hits
#     a terminal state). `all_sids` carries every group's session, so an early
#     group's completion is not missed.
monitor_watch_jules_sessions(
    all_sids,
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
| `state=IN_PROGRESS → AWAITING_PLAN_APPROVAL` | Check the plan body via `jules_plan(sid)`. If confidence ≥ 0.90 (gate 1 from `JULES_PROTOCOL`), call `jules_approve`. **Escalation channel:** at this state no PR exists yet, so the `@human:` PR-comment path is wrong. Escalate via `jules_message(sid, "@human: plan requires clarification — <text>")` (lands in the session timeline), AND write the same text to `~/.agency-system/cache/orchestrator-escalations/{phase}-{sid}.md` so it survives a session-end. Once the human responds or unblocks the session externally, the orchestrator resumes normally. |
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
        round_started_at = utcnow_iso()                # used to filter §4.2
        review_sid_res = jules_create(
            title=f"Review PR #{pr.number} — round {round + 1}",
            prompt=REVIEW_PROMPT_TEMPLATE.format(
                pr_number=pr.number,                   # template's first-line field
                pr_url=pr.html_url,
                phase=pr.phase_id,
                spec=pr.spec_id,
                spec_path=pr.spec_paths_str,           # e.g. "Plan/104-tool-search-anchor-triad/spec.md"
                                                       # OR for meta-reviews "Plan/000-overview.md + Plan/JULES-REVIEW-LOOP.md"
                round=round + 1,
            ),
            source=pr.head_repo,
            starting_branch=pr.head_branch,            # the branch under review
            require_plan_approval=False,               # review-only sessions can't widen scope
        )
        review_sid = (review_sid_res.get("name") or review_sid_res.get("id") or "").replace("sessions/", "")
        wait_until_completed(review_sid)               # uses §3 watcher
        # `get_review_comments` returns threads (per the MCP schema:
        # "Returns threads with metadata (isResolved, isOutdated, isCollapsed)
        # and their associated comments"). No separate get_review_threads
        # method is needed — the thread metadata is on the same response.
        threads = mcp_github_pull_request_read(
            method="get_review_comments", pullNumber=pr.number,    # camelCase per MCP schema
        )
        substantive = triage(threads, since=round_started_at)  # see §4.2

        if len(substantive) == 0 and review_summary_contains_clean_marker(review_sid, pr):
            return pr                                  # clean; merge

        # Spawn a follow-up Jules session pointing at the same branch
        # with the substantive comments as the fix brief. `jules_create`'s
        # `starting_branch` is the supported kwarg (NOT `existing_branch`);
        # Jules's session will branch from there and push back to it.
        fix_sid_res = jules_create(
            title=f"Fix review feedback for PR #{pr.number} — round {round + 1}",
            prompt=FIX_PROMPT_TEMPLATE.format(
                pr_url=pr.html_url,
                substantive_comments_rendered_as_numbered_list=render_numbered(substantive),
                branch=pr.head_branch,
            ),
            source=pr.head_repo,
            starting_branch=pr.head_branch,            # IMPORTANT: stay on the PR branch
            require_plan_approval=True,
        )
        fix_sid = (fix_sid_res.get("name") or fix_sid_res.get("id") or "").replace("sessions/", "")
        wait_until_completed(fix_sid)
        # Loop continues: next round runs a fresh review against the new commits.

    raise NotConvergedError(f"PR #{pr.number} did not converge in {max_rounds} rounds")
```

### 4.1 The review prompt template (verbatim — paste into Jules)

```markdown
You are the independent reviewer for PR #{pr_number} on `netzkontrast/the-agency-system`.

CONTEXT:
- Phase: {phase} (see Plan/000-overview.md)
- Spec:  {spec} (see {spec_path} — for meta/multi-doc reviews this may list multiple paths, e.g. "Plan/000-overview.md + Plan/JULES-REVIEW-LOOP.md")
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

### 4.2 Triage (substantive vs not — round-scoped, thread-aware)

```python
def triage(threads, since: str):
    """Return ONLY comments produced in the current round AND on threads
    that are still unresolved.

    `get_review_comments` returns threads — each carries `isResolved`,
    `isOutdated`, `isCollapsed` metadata alongside its `.comments` list
    (per the MCP `pull_request_read` schema). Threads marked
    `isResolved=true` were addressed in a prior round and must NOT
    re-count; otherwise the loop would never converge and would always
    escalate at round 5.

    Two filters compose:
    1. Thread filter: thread.isResolved == false
    2. Time filter:   comment.created_at >= round_started_at (`since`)
    """
    out = []
    for thread in threads:
        # MCP responses are JSON dicts, not objects with attributes.
        # Use .get() consistently. Camel-case keys match the schema.
        if thread.get("isResolved", False):
            continue
        for c in thread.get("comments", []):
            if c.get("createdAt", "") < since:
                continue
            severity = severity_prefix(c.get("body", ""))   # see below
            if severity in ("[BLOCKING]", "[SUBSTANTIVE]"):
                out.append(c)
    return out


def severity_prefix(body: str) -> str:
    """Map both Jules-style explicit prefixes and external-bot badges to
    the same three-level severity. External bots (Codex, Copilot) use
    `P0`/`P1`/`P2`/`P3` images; map `P0` and `P1` -> [BLOCKING],
    `P2` -> [SUBSTANTIVE], everything else -> [NIT]. `P0` would otherwise
    fall through and let a release-blocking issue land unaddressed —
    explicit handling is mandatory."""
    if (
        body.startswith("[BLOCKING]")
        or "P0 Badge" in body                       # release-blocker
        or "P1 Badge" in body
    ):
        return "[BLOCKING]"
    if body.startswith("[SUBSTANTIVE]") or "P2 Badge" in body:
        return "[SUBSTANTIVE]"
    return "[NIT]"
```

The orchestrator does NOT triage `[NIT]` comments. They land on the PR for the human author to glance at and resolve later; they do not block merge.

External-bot comments (e.g. Codex, copilot) use their own severity badges (`P1`/`P2`/`P3`). The orchestrator maps `P1 → [BLOCKING]` and `P2 → [SUBSTANTIVE]` at triage time so bot reviews compose with Jules reviews in the same convergence test.

### 4.3 The fix prompt template (verbatim — paste into Jules)

Python `.format()` interpolates `{name}` placeholders, so any literal `{` and `}` in the template body must be doubled to `{{` and `}}` to survive untouched. The render is `FIX_PROMPT_TEMPLATE.format(pr_url=..., branch=..., substantive_comments_rendered_as_numbered_list=...)` — only those three fields are interpolated; the `{{comment_id}}` and `{{short_summary}}` braces below are intentional instructions to Jules and arrive in its prompt as `{comment_id}` / `{short_summary}`.

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
4. Commit with subject: "fix(review): address #{{comment_id}} — {{short_summary}}"
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
def recover_completed_no_branch(sid, *, phase_id, spec_id, recover_onto):
    """Recover a silent-fail session.

    Args:
        sid: the Jules session id whose patch needs recovering.
        phase_id, spec_id: identifiers threaded through the recovery
            PR body and commit messages (caller passes them; NEVER
            reference an outer-scope name).
        recover_onto: where the recovered branch should diverge from.
            - For a freshly-dispatched implementation session, this is
              "Master".
            - For a fix-round silent-fail (a session dispatched in
              §4 with starting_branch=pr.head_branch), this MUST be
              pr.head_branch so the fix lands ON the PR under review
              rather than producing a detached PR. The caller passes
              pr.head_branch in that case.
    """
    # Step 1 — probe (per appendix)
    jules_message(sid, "your state is COMPLETED but I can't find your branch on origin — please publish and reply with PR URL")
    if wait_for_publish(sid, timeout_minutes=10):
        return                                        # Jules pushed; done

    # One more probe
    jules_message(sid, "still no branch — please retry the publication flow")
    if wait_for_publish(sid, timeout_minutes=10):
        return

    # Step 2 — API extraction (deterministic). The script writes the raw
    # patch to /tmp/jules-patches/{sid}-out{i}.patch and emits ONLY stats
    # to stdout — it does not return file bodies. The orchestrator parses
    # the on-disk patch itself.
    #
    # Script output shape (verbatim from tools/jules-patch-extract.py):
    #   {"sid": <id>, "patches": [ {path, size, files, first_files[...]}, ... ]}
    # OR (when there is no output at all on the session):
    #   {"sid": <id>, "patches": 0, "note": "no outputs/gitPatch on session"}
    stats = json.loads(run_command(
        f"PYTHONPATH=servers/agency-mcp/src python3 tools/jules-patch-extract.py {sid}"
    ))
    if not isinstance(stats.get("patches"), list):
        # 0-file patch → genuine empty session, not a silent-fail
        log_to_lessons_learned(sid, phase_id, spec_id, "extractor reports no outputs")
        return

    patch_paths = [p["path"] for p in stats["patches"]]

    # Step 3 — push via GitHub MCP (signed web-flow commits). Parse the
    # unified diff into per-file final-content using a unidiff parser
    # (e.g. `unidiff` lib, or a 30-line stdlib parser). The local
    # `git apply` path is NOT used because the CODESIGN_MCP backend
    # currently rejects locally-signed commits.
    branch = f"jules-recovered/{sid[-8:]}"
    target_branch = branch if recover_onto == "Master" else recover_onto
    if recover_onto == "Master":
        mcp_github_create_branch(branch, from_branch="Master")

    def apply_change(file_change, msg_prefix):
        """Route to the right GitHub MCP tool. `parse_unified_diff` yields
        file_change.op in {"add", "modify", "delete", "rename"}; delete
        and rename's source-side need delete_file because
        create_or_update_file cannot remove files."""
        if file_change.op == "delete":
            mcp_github_delete_file(
                path=file_change.source_path,
                branch=target_branch,
                message=f"{msg_prefix} delete {file_change.source_path}",
            )
        elif file_change.op == "rename":
            # GitHub has no atomic rename; emulate as delete-old + add-new.
            mcp_github_delete_file(
                path=file_change.source_path,
                branch=target_branch,
                message=f"{msg_prefix} rename: delete {file_change.source_path}",
            )
            mcp_github_create_or_update_file(
                path=file_change.target_path,
                content=file_change.final_content,
                branch=target_branch,
                message=f"{msg_prefix} rename: add {file_change.target_path}",
            )
        else:  # "add" or "modify"
            mcp_github_create_or_update_file(
                path=file_change.target_path,
                content=file_change.final_content,
                branch=target_branch,
                message=f"{msg_prefix} {file_change.target_path}",
            )

    msg_prefix = (
        f"feat: recovered Spec {spec_id} (phase {phase_id}) from Jules sid {sid[-8:]}"
        if recover_onto == "Master"
        else f"fix(review): recovered fix commit from sid {sid[-8:]} —"
    )
    # IMPORTANT: each patch in a multi-output session may depend on prior
    # patches. parse_unified_diff therefore takes a *current* base — for the
    # first patch it's `recover_onto`; for every subsequent patch it must be
    # the in-progress branch (target_branch) AS IT EXISTS NOW on origin, so
    # that hunks computed against an earlier patch's output line up. The
    # `tools/jules-patch-extract.py --apply` mode stops on first apply
    # failure for exactly this reason; we replicate that ordering invariant.
    current_base = recover_onto
    for patch_path in patch_paths:                               # iterate ALL outputs, not just out0
        for file_change in parse_unified_diff(patch_path, base_branch=current_base):
            apply_change(file_change, msg_prefix)
        current_base = target_branch                             # subsequent patches see the prior patch's commits

    if recover_onto == "Master":
        # Fresh implementation recovery → open a new PR
        return mcp_github_create_pull_request(
            head=branch,
            base="Master",
            title=f"Spec {spec_id} — recovered via API extraction",
            body=render_recovery_pr_body(sid, stats, phase_id, spec_id),
        )
    else:
        # Fix-round recovery wrote directly onto the open PR's head branch.
        return None
```

`parse_unified_diff(path, base_branch)` is a Phase 0 sub-task (~30 LOC in `tools/lib/unidiff_to_files.py`): walks `--- a/<path>` / `+++ b/<path>` headers, fetches each base blob via `mcp__github__get_file_contents(ref=base_branch)` (the MCP schema uses `ref` for branch/tag/sha selection, not `branch`), applies hunks, and yields `(target_path, final_content)` tuples. The `tools/jules-patch-extract.py` script's `--apply` mode is NOT used for the orchestrator path because its `git apply` commits cannot be signed by the CODESIGN_MCP backend; `--apply` remains useful for local dev inspection only.

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

Jules enforces a **daily** quota (default 100 sessions/day). The orchestrator caps **concurrent** in-flight at 60. Both are tracked via `jules_quota` (MCP), whose return shape is `{daily_limit, used_today, remaining_today, active_today, by_state_today, today_utc, newest_today_id, pages_scanned, truncated}`. **Note: there is no `in_flight_count` field — use `active_today` (non-terminal sessions) for the concurrency cap.**

```python
def gated_dispatch(payload):
    q = jules_quota(daily_limit=100)
    in_flight = q["active_today"]                      # the real concurrent count
    daily_remaining = q["remaining_today"]
    if q.get("truncated"):
        # Pagination cap was hit; be conservative — re-query with max_pages=20
        q = jules_quota(daily_limit=100, max_pages=20)
        in_flight = q["active_today"]
        daily_remaining = q["remaining_today"]
    concurrent_budget = max(0, 60 - in_flight)
    budget = min(concurrent_budget, daily_remaining)
    if len(payload) <= budget:
        return dispatch_each(payload)                  # Python loop over jules_create
    # Split: dispatch the first `budget` entries; queue the remainder
    head = dispatch_each(payload[:budget])
    tail = queued_dispatch(payload[budget:])           # waits for slot in §2.b watcher
    return head + tail
```

The 60-session concurrency ceiling is rarely binding; the typical phase opens 4-10 sessions. Phase 8 is the only phase that could realistically approach it (≤ 10 specs). The **daily** cap is the more likely binding constraint across an active week. Watch for the binding-quota signal in lesson-15.

---

## 8. Idempotency under crashes

The orchestrator can crash and resume mid-phase. Resume guarantees:

| State on disk | After crash, orchestrator does |
|---|---|
| `~/.agency-system/cache/sessions.json` | Re-loads in-flight session list; resumes §2.b watcher (canonical path per 000-overview.md §7) |
| Open PRs without `claude-review-cycle:*` label | Treats as awaiting review; starts §4 loop at round 1 |
| Open PRs with `claude-review-cycle: round-N-started` label, no `…round-N-done` label | Resumes §4 loop at round **N** (the in-flight round whose work hadn't finished) |
| Open PRs with `claude-review-cycle: round-N-done` label | Resumes §4 loop at round **N+1** |
| Closed PRs with `claude-merged` label | Skip; included in §2.f overview update |

The orchestrator writes the `claude-review-cycle: round-N-started` label via `mcp__github__issue_write` (issue API works on PRs) at the **start** of each round, and the `claude-review-cycle: round-N-done` label at the **end** of the round (whether convergent or proceeding to round N+1). The two-label scheme prevents skipping unfinished work after a mid-round crash. A `claude-merged` label is set after §6 succeeds.

---

## 9. Failure modes and escalation

| Symptom | Diagnosis | Action |
|---|---|---|
| Review session itself fails 3 rounds in a row | Review prompt may be ambiguous against the spec | Stop loop; escalate `@human:` |
| Fix session widens PR scope (touches files outside spec.affects:) | Scope creep | Reply on PR: "fix session widened scope to {file}. Please revert and try again with tighter prompt." Restart fix session. |
| Convergence stalls but smoke test passes anyway | Tests may be missing coverage | Add a [SUBSTANTIVE] review comment requesting test addition; continue loop |
| `jules_quota()` reports `remaining_today == 0` or `active_today >= 60` | Hit the daily or concurrency ceiling. (`jules_status_all` has no `quota_exceeded` field — it returns `{by_state, sessions, pages_scanned, truncated}` — so quota pressure must be queried via `jules_quota` per §7.) | Pause fanout; wait for completions; resume |
| `tools/jules-patch-extract.py` returns 0-file patch | Genuine empty session (Jules did nothing) | Mark spec for re-dispatch with revised prompt; log to `_lessons-learned/` |

**Escalation channel depends on session state — see §3 for the contract.** Post-COMPLETED escalations (PR-stage problems) go to `@human:` PR comments; pre-PR escalations (sessions still in `AWAITING_PLAN_APPROVAL` where no PR has been opened yet) go through `jules_message(sid, "@human: …")` plus the durable file at `~/.agency-system/cache/orchestrator-escalations/{phase}-{sid}.md`. Either way the PR thread is the canon once a PR exists; never DMs, never external channels.

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
