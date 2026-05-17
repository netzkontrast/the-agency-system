#!/usr/bin/env python3
"""One-off: dispatch a Jules session to add workflow learnings to references/."""
import importlib.util, json, sys
from pathlib import Path

spec = importlib.util.spec_from_file_location("jm", ".claude/mcp/jules-mcp/server.py")
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)

JOURNAL = Path(".claude/journal")
SOURCE = "sources/github/netzkontrast/the-agency-system"
BRANCH = "claude/create-jules-skill-x8QHA"
ALIAS = "wave3-workflow-learnings"
TITLE = "Jules refactor wave 3: workflow learnings → references/"

PROMPT = f"""\
You are working on PR #27 of netzkontrast/the-agency-system, branch
{BRANCH}. Add real-world workflow learnings from the refactor session
itself to the new skill's references/ directory.

READ FIRST:
- docs/superpowers/specs/2026-05-16-jules-suite-refactor-design.md
- jules-plugin/skills/jules/references/caveats.md
- jules-plugin/skills/jules/references/state-machine.md
- jules-plugin/skills/jules/references/parallel-orchestration.md

These learnings come from orchestrating ~18 Jules sessions for this
refactor (PR #27, Waves 1-3). They're not in the original SKILL.md
because they only surfaced under real fan-out load.

Single-plan, single-execution — DO NOT iterate on plan approval.

[TASK]
Add three sets of additions, append-only, to existing reference files.
Do not delete or reword existing content unless explicitly noted.

1. jules-plugin/skills/jules/references/caveats.md — append a new H2
   section "Empirically observed traps (from PR #27 refactor)" with
   these subsections, written as numbered list:

   a) **COMPLETED without artifacts ≠ dead.** A session can show state
      COMPLETED with no patch artifact and no PR output, yet still be
      paused waiting on a UI gate (e.g. a "Create PR?" prompt). Do NOT
      assume the work is lost. Recovery: send a jules_message asking the
      agent to continue ("Please continue and complete the brief…"); the
      state will transition to AWAITING_USER_FEEDBACK and the work
      resumes. Only respawn if a nudge produces no transition within
      ~10 minutes.

   b) **jules_message during plan-approval can kill the session.** When
      a session is in AWAITING_PLAN_APPROVAL and you want to request
      changes, sending jules_message instead of jules_approve sometimes
      causes the session to interpret the message as a stop signal and
      transition to COMPLETED with no plan and no work. Safer pattern:
      if the plan is acceptable, jules_approve; if not, jules_message
      with the change request AND then verify the next state is
      PLANNING (re-plan in progress), not COMPLETED.

   c) **Patch artifacts are retrievable while state is IN_PROGRESS.**
      jules_patch_summary and jules_patch_apply walk activities[]
      artifacts; they do not require the session to be COMPLETED. If a
      session is stuck IN_PROGRESS for >30 minutes but the latest
      progressUpdated activity shows artifacts written, fetch and
      integrate the patch immediately — don't wait for COMPLETED.

   d) **Watcher liveness is not free.** watch_jules.py is a separate
      process; if it dies, state transitions stop being written to
      notifications.jsonl and any monitor that tails the log goes
      silent. Verify with `ps -p $(cat .claude/skills/jules/watcher.pid)`
      or `claude/journal` log lines before assuming a session is
      stalled. Restart with --daemonize.

2. jules-plugin/skills/jules/references/state-machine.md — find the
   COMPLETED state row (or add one if missing) and add a clarifying
   sub-bullet:

   - COMPLETED with patch artifact OR Session.outputs[].pullRequest → real terminal success
   - COMPLETED with NEITHER → session is paused on a UI gate; recovery is
     a continuation jules_message, not a respawn (see caveats: "COMPLETED
     without artifacts ≠ dead")

3. jules-plugin/skills/jules/references/parallel-orchestration.md —
   append a new H2 section "Fan-out reliability checklist (from PR #27
   refactor experience)" with these numbered items:

   1. Before dispatching a fan-out, verify the watcher daemon is alive
      (ps -p $(cat .claude/skills/jules/watcher.pid)). A dead watcher
      means silent failures.

   2. Each session prompt should include the exact branch name and the
      EXACT shape of the expected reply (5-line summary + pytest verdict).
      Vague prompts trigger more clarifying questions per session, which
      multiplies under fan-out.

   3. Wave-based dispatch (groups of 3-6 sessions with no inter-wave
      dependencies) integrates better than single-session-per-task
      because review cycles batch across the wave instead of context
      thrashing one at a time.

   4. When integrating multiple Jules patches that touch overlapping
      files, use jules_patch_apply with only_files= to apply just the
      in-scope subset. Letting two sessions both rewrite tools/lifecycle.py
      via blind `git apply` lets the second one silently overwrite the
      first.

   5. Quota cost of fan-out is len(unique_sessions), not retries. A
      respawn or a fresh continuation each burns one slot of the
      per-account daily quota. Budget 1.3x the expected session count
      for safety (correction loops + stalled-session respawns).

   6. The plan-approval gate is your cheapest steering point. Spend the
      time to read each plan before approve/correct rather than batching
      blindly — the cost of a misaligned implementation is much higher
      than the cost of one extra review pass.

When done push to jules/refactor-wave3-workflow-learnings and reply with
branch name, files modified, and a 3-line confirmation that the
appended sections compile cleanly (no broken markdown).

Hard constraints:
- Do NOT touch jules-plugin/skills/jules/SKILL.md (slim main file)
- Do NOT touch the design spec
- Do NOT touch the .claude/journal/ directory
- Do NOT touch any code (tools/*, lib/*, tests/*) — references only
"""


def main() -> int:
    fn = getattr(mod.jules_create, "fn", mod.jules_create)
    resp = fn(prompt=PROMPT, source=SOURCE, starting_branch=BRANCH,
              title=TITLE, require_plan_approval=True,
              auto_create_pr=False, alias=ALIAS)
    sid = resp.get("id") or resp.get("name", "").rsplit("/", 1)[-1]
    url = resp.get("url", "") or f"https://jules.google.com/session/{sid}"
    print(json.dumps({"alias": ALIAS, "id": sid, "url": url}, indent=2))
    jpath = JOURNAL / f"jules-{ALIAS}.jsonl"
    with jpath.open("w") as fh:
        fh.write(json.dumps({"event": "created", "alias": ALIAS, "id": sid,
                              "url": url, "title": TITLE,
                              "prompt_chars": len(PROMPT)}) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
