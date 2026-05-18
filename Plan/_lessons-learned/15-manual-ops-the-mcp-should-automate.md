---
lesson_id: 15
slug: manual-ops-the-mcp-should-automate
severity: high
seen_in: [orchestrator-session-2026-05-18, spec-022, spec-011a, jules-research-1-5]
applies_to:
  - agency-mcp
  - jules-mcp
  - orchestrator-patterns
  - mcp-tooling
captured_at: 2026-05-18
---

# Manual orchestration ops the MCP server should automate

Catalogue of operations the orchestrator (me, this session) performed by
hand that the agency-mcp / jules-mcp servers could absorb as first-class
tools. Each is a recurring multi-step ritual; together they consumed a
material slice of session attention.

## 1. Combined watcher arming/re-arming

**What I did manually**: every Jules dispatch required killing the
combined watcher (`pkill -f combined_watcher`), updating
`/tmp/jules-all-sessions.json`, restarting via `nohup python3
jules-plugin/skills/jules/references/combined_watcher.py ...`.

**What the MCP should do**: expose `jules_watch_add(sid)`,
`jules_watch_remove(sid)`, `jules_watch_list()`, and a persistent
watcher daemon owned by the server. `jules_create` should auto-add.
Wake events should arrive as session messages (the existing PR-activity
subscription pattern works for this).

## 2. Branch verification after COMPLETED

**What I did manually**: every COMPLETED required
`mcp__github__list_branches` + visual scan for a matching branch + check
for an open PR.

**What the MCP should do**: include `branch_on_remote: bool`,
`pr_url: str | None`, `silent_fail: bool` in `jules_get` response when
`state == "COMPLETED"`. Bake the §8 verification into the state shape
itself so trusting state alone is safe.

## 3. Silent-fail recovery loop

**What I did manually**: extract patch via
`tools/jules-patch-extract.py <sid>` → probe Jules via `jules_message` →
wait ~5 min → re-check → escalate to local subagent → subagent applies
patch via signed MCP commits → open PR.

**What the MCP should do**: expose `jules_recover(sid, max_probes=2,
on_exhaust="subagent")`. The recovery flow is deterministic and well-
documented (CLAUDE.md §"Jules session state semantics" plus JULES_PROTOCOL
§8); the orchestrator should not need to re-implement it every time.

## 4. Codex review → Jules feedback loop

**What I did manually**: for each merged Jules PR, pull Codex inline
comments via `mcp__github__pull_request_read`, categorise as P0/P1/P2,
post a `@jules` issue comment summarising findings, also send a
`jules_message` to the originating session.

**What the MCP should do**: `jules_notify_pr_feedback(sid, pr_number,
filter="codex")` does both writes in one call. Bonus: auto-detect
when a merged PR has new bot reviews and queue the notify.

## 5. Plan inspection before approval

**What I did manually**: every `AWAITING_PLAN_APPROVAL` required
fetching `jules_activities` → parsing `planGenerated` → manually
checking each step's "affects" coverage against the spec's `affects:`
allow-list before calling `jules_approve`.

**What the MCP should do**: `jules_plan_review(sid, spec_path)` returns
`{steps: [...], in_scope_paths: [...], out_of_scope_paths: [...],
missing_paths: [...]}`. Approval guidance is a 1-call summary, not a
multi-step pagination through raw activities.

## 6. Quota guard pre-fanout

**What I did manually**: `jules_quota(daily_limit=60)` before each
fanout to confirm headroom.

**What the MCP should do**: `jules_create(daily_budget=10)` returns an
error if `remaining_today < 1`. Bulk-fanout helpers should pre-check
and refuse to start if the quota cannot cover the planned batch.

## 7. Protocol preamble injection

**What I did manually**: every dispatch prompt re-pasted the JULES_PROTOCOL
preamble ("Read JULES_PROTOCOL.md before starting. Run gates 1→4. §8
silent-fail rule applies. Branch: Master. ...").

**What the MCP should do**: `jules_create(protocol_preset="agency-system")`
injects the preamble server-side from a versioned template. Updating the
preamble once propagates to all future dispatches without orchestrator
code changes.

## 8. PR title / branch naming convention

**What I did manually**: read `Plan/NNN-<slug>/spec.md` frontmatter,
hand-built `title="Spec NNN — <slug>"` and `alias=spec-NNN-<slug>`.

**What the MCP should do**: `jules_create(spec_path=...)` auto-derives
title + alias + branch + base from the spec frontmatter
(`spec_id`, `slug`, `affects:`, owner, `depends_on:`).

## 9. Patch scope audit

**What I did manually**: every `jules_patch_summary` result was diffed
by eye against the spec's `affects:` allow-list to detect scope creep
(see Spec 022's 60-file vs 5-file initial patch).

**What the MCP should do**: `jules_patch_audit(sid, spec_path)` returns
`{in_scope_files: [...], out_of_scope_files: [...], missing_files: [...]}`.
The orchestrator decides what to do; the audit itself is mechanical.

## 10. Code-mode wrapper auto-discovery

**What I did manually**: had to know that
`from agency_mcp.handlers.jules.lifecycle import jules_create` was the
code-mode-wrapped path, distinct from the raw
`jules_plugin.mcp-server.src.jules_mcp.tools.lifecycle` API.

**What the MCP should do**: code-mode wrappers should be the only
exposed surface once dev-install runs. The "raw" API is an
implementation detail; expose unified `mcp__agency-system__jules_*`
tools and hide the rest.

## 11. Dev-install bootstrap from a non-plugin agent

**What I did manually**: `bash bin/agency-dev-install` failed with
"No virtual environment found" because `uv` defaults to venv mode; I
had to `uv pip install --system -e .` separately.

**What the MCP should do**: `bin/agency-dev-install` should auto-detect
"running outside Claude Code's plugin loader" (no venv, no
`CLAUDE_PLUGIN_ROOT`) and fall back to `--system`, or print a clear
"need to run inside Claude Code OR create a venv first" error. The
fastmcp-style preflight from `bin/jules-bulk` is the right idiom.

## 12. Hotfix-PR composer for Codex findings

**What I did manually**: composed a 200-line subagent prompt
enumerating the 4 Codex P1/P2 findings on PR #73, then dispatched a
general-purpose subagent.

**What the MCP should do**: `jules_hotfix_from_codex(pr_number,
severity_filter="P1")` builds the recovery prompt automatically from
the Codex review comments, dispatches the subagent, returns the hotfix
PR URL.

## 13. PR-activity subscription wiring

**What I did manually**: never explicitly subscribed via
`mcp__github__subscribe_pr_activity` after dispatching Jules sessions;
relied on combined_watcher polling.

**What the MCP should do**: `jules_create(subscribe_pr_activity=True)`
auto-wires the subscription when Jules opens the PR, so review-comment
events arrive without polling.

## 14. Session registry alias auto-derivation

**What I did manually**: passed `alias=spec-NNN-<slug>` explicitly on
every `jules_create`.

**What the MCP should do**: when `spec_path` is provided, alias defaults
to `spec-{spec_id}-{slug}` from frontmatter.

## 15. Multi-PR feedback aggregation

**What I did manually**: for the 6-PR Jules fanout, I dispatched a
single subagent to walk every PR, post `@jules` comments + send
session messages. Conceptually one operation, mechanically 12 writes.

**What the MCP should do**: `jules_notify_batch(pr_numbers,
filter="codex")` accepts a list, dedupes by session, posts all
comments/messages in one transaction.

## How this list becomes a spec

Per `Plan/_lessons-learned/README.md`, this folder feeds
`Plan/099-jules-orchestration-improvements/spec.md`. Each item above
maps to a Done-When line:

- Items 1, 2, 3, 5, 6, 9, 14, 15 → agency-mcp Jules-handler additions.
- Items 4, 12, 13 → cross-cutting (agency-mcp wraps GitHub MCP + Jules MCP).
- Items 7, 8, 10, 11 → agency-mcp dev-install + `jules_create` ergonomics.

A follow-up spec should also capture the **observability** side — the
session-log MCP server outlined in `Plan/_lessons-learned/README.md`
§"Final-TODO" would surface "which of these manual ops did the
orchestrator perform N times this session" without re-reading the
transcript by hand.

## Anti-pattern to encode

The recurring shape is: *the orchestrator does N reads + 1 write to
satisfy a single conceptual operation*. Whenever a CLAUDE.md procedure
reads like a checklist of MCP calls (silent-fail recovery is the
canonical example — 4 numbered steps), that procedure is a candidate
for absorption into a single MCP tool. The MCP server is the right
home for procedural knowledge; CLAUDE.md should be policy, not
procedure.
