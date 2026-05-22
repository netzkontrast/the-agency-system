# Spec 022 dispatch — 2026-05-18

Move 1 of the 2026-05-18 next-session goal: dispatch Spec 022 (dev-mode-install)
to Jules as the single Wave-A enabler that unblocks the downstream batches.

## Session

| Field | Value |
| --- | --- |
| Jules session id | `7141901259275298309` |
| URL | https://jules.google.com/session/7141901259275298309 |
| Title | Spec 022 — Dev-mode plugin install (Wave A enabler) |
| Source | `netzkontrast/the-agency-system` |
| Starting branch | `Master` |
| Alias | `spec-022-dev-mode-install` |
| Require plan approval | true |
| State at dispatch | `IN_PROGRESS` |
| Dispatched at | 2026-05-18T09:12Z |

The prompt body lives at `tools/jules-archive/spec-022-dispatch.prompt.json`
(see Files committed below). It tells Jules to read `Plan/JULES_PROTOCOL.md`
first, run gates 1→4 in order, only touch the spec's `affects:` allow-list,
target `Master` (not `main`), and verify branch publication before declaring
COMPLETED (the §8 silent-fail rule).

## Watcher

Watch via the persisted poller. From a shell with `JULES_API_KEY` set:

```bash
echo '["7141901259275298309"]' > /tmp/jules-spec-022-sessions.json
PYTHONPATH=jules-plugin/mcp-server/src \
  python3 jules-plugin/skills/jules/references/combined_watcher.py \
  /tmp/jules-spec-022-sessions.json /dev/null
```

It exits when the session reaches `AWAITING_PLAN_APPROVAL`,
`AWAITING_USER_FEEDBACK`, `COMPLETED`, `FAILED`, or `CANCELLED`, or after
6 hours.

## Setup gap discovered while dispatching

`bin/jules-bulk` failed cryptically the first time it ran outside a
Claude-Code-managed plugin session:

```
ERROR: Failed to create session. Error: No module named 'fastmcp'
```

…and after a plain `pip install fastmcp`:

```
ImportError: cannot import name 'code_mode' from 'fastmcp.contrib'
```

The fix landed on this branch (`claude/spec-022-dispatch-CtdIJ`):

- `jules-plugin/bin/jules-dev-install` — idempotent bootstrap that
  installs `fastmcp[code-mode]>=3.1.0`, `httpx`, and `PyYAML`, verifies the
  imports the helpers need (`FastMCP`, `CodeMode`, `jules_create`,
  `create_mcp`), and pre-creates `${CLAUDE_PLUGIN_DATA:-$HOME/.jules}`.
- `jules-plugin/bin/jules-bulk` — added a preflight import check that
  aborts with a clear pointer at `bin/jules-dev-install` instead of a
  cryptic `ModuleNotFoundError`.
- `jules-plugin/README.md` and `CLAUDE.md` — documented the local-CLI
  bootstrap flow.

This is orchestrator-side only; it is independent of Spec 022 itself
(which targets the agency-system plugin's own dev install).

## Files committed on this branch

- `jules-plugin/bin/jules-dev-install`
- `jules-plugin/bin/jules-bulk` (preflight check)
- `jules-plugin/README.md` (Local CLI tools section)
- `CLAUDE.md` (Driving the CLI helpers outside Claude Code)
- `Plan/_session-state/2026-05-18-spec-022-dispatch.md` (this file)
- `tools/jules-archive/spec-022-dispatch.prompt.json`

## Next checkpoints

1. Watcher fires on `AWAITING_PLAN_APPROVAL` → approve plan.
2. Watcher fires on `COMPLETED` → verify Jules's PR exists on remote
   (`mcp__github__list_branches`) before trusting state. If the branch is
   missing, use `tools/jules-patch-extract.py 7141901259275298309` to recover
   the patch — never re-dispatch a fresh session for the same work
   (JULES_PROTOCOL §8).
3. Codex bot review must land green before merge.
4. After merge: Move 4 — fan out batch 1 (011a, 014, 098, 103).
