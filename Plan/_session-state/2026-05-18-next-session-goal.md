---
type: session-goal
authored: 2026-05-18
for_session: next (post-handoff)
prev_session_handoff: Plan/_session-state/2026-05-18-orchestration-handoff.md
---

# /goal — next orchestration session

Continue the the-agency-system unified-plugin refactor. Master is at the
session-handoff commit (15 specs done / 30 ready in Plan/). Start by
reading `Plan/_session-state/2026-05-18-orchestration-handoff.md` — it has
the dependency graph, the 5-command startup script, and the 6 hardest
lessons from the previous session.

## Primary objective

Ship Wave B + Wave C to land the unified Claude Code plugin at v1.0:

- **Wave B remaining:** 011a (novel hardening), 014 (gates+revision),
  015 (28+10 novel skills), 021 (prompt-builder family)
- **Wave C:** 016 (agentic 32-tool surface), 017 (hooks port+extend),
  018 (overrides+config migration), 020 (bitwize-music deprecation+docs)
- **One cross-cutting decision:** Context Mode path — adopt
  `mksglu/context-mode` via Spec 108, OR build-from-scratch via Specs
  111+112+113. Mutually exclusive; pick one before dispatching either.

**Pre-requisite spec for this session:** 022 dev-mode-install — must
land first so the orchestrator can actually USE the plugin under
development (skills + MCP server in dev-mode) instead of waiting for a
final marketplace install. See `Plan/022-dev-mode-install/spec.md`.

"Done" for this session = bitwize-music plugin can be uninstalled
without breaking any music workflow, AND a fresh Claude Code session
boots into agency-system at ≤500 token context cost, AND the
orchestrator can load the in-progress plugin via `claude --plugin-dir`
within 5 minutes of session start.

## Secondary objectives (parallelizable, dispatch as quota allows)

- Spec 098 — Wave A hardening (Codex P1 cleanup across merged work)
- Specs 103-107 — token-efficiency layer (view=/fields= projection,
  anchor triad, TOON serializer, GitHub-MCP subagent wrappers,
  cache-breakpoint ordering)
- Specs 114-121 — token-optimizer-inspired hook-layer compression

## Orchestrator discipline (from yesterday's lessons)

1. **Verify before trust.** Jules auto-PR has silent-fail modes. On every
   Jules COMPLETED state, run `git ls-remote origin | grep <sid>` BEFORE
   trusting it. If missing, recover via
   `tools/jules-patch-extract.py <sid>` — never re-dispatch a fresh
   session on the same spec for the same work.
2. **2 silent-fails → switch.** Don't burn a third Jules slot. Spawn a
   local subagent + apply the API-extracted patch instead.
3. **Patches > 2 KB never `head`/`grep`/`cat`-ed.** Always go through the
   extractor script which writes to `/tmp/jules-patches/` and emits only
   `{bytes, files, first_files[]}` stats.
4. **Wrap every `mcp__github__pull_request_read` in a focused subagent.**
   Main thread never pages through PR bodies. Spec 106 documents the
   permanent fix; until it ships, wrap manually.
5. **Wait for Codex review before merging non-trivial PRs.** Yesterday it
   caught 7 P1s that the spec-writing subagent missed.
6. **Always rebase before publish.** Stale merge-base = phantom-files in
   the diff. `git rebase origin/Master` then `git push --force-with-lease`.

## Recommended first moves (in order)

1. **Dispatch Spec 022 (dev-mode install) FIRST** — single Jules session,
   small scope, unblocks everything else. Once 022 lands on Master, you
   can boot the in-progress plugin via:
   ```bash
   claude --plugin-dir /path/to/the-agency-system
   ```
   This is the dev-install pathway — no marketplace round-trip needed.
2. While 022 is running, invoke `sc-spec-panel` against the 31 ready
   specs in Plan/ to surface architectural drift, stale references,
   BCP-14 violations. Capture findings as a single review comment that
   can be triaged into spec-patches.
3. Once 022 has merged, parallel-dispatch the **first fanout batch**:
   - **011a** (novel hardening — depends on 011 ✅)
   - **014** (novel gates+revision — critical-path step)
   - **098** (Wave A hardening — Codex P1 cleanup, orthogonal)
   - **103** (token-eff: view/fields projection — depends on 008 ✅)
4. Invoke `skill-creator` to formalize three operational patterns from
   yesterday's lessons-learned into reusable Skills under
   `skills/agentic/`:
   - `jules-orchestrator-discipline` (the 6-rule list above)
   - `silent-fail-recovery` (the §8 patch-extraction flow)
   - `context-safe-patch-handling` (extractor script + never-echo rule)
5. Read both Context Mode spec heads (`Plan/108-…/spec.md` vs the
   `Plan/111-/112-/113-` chain) and **make the path decision** before
   any downstream context-mode work.

## Critical path to v1.0 (5 sessions)

```
022 ⭐ (enabler, dispatch alone first)
        │
        └── 014 → 015 → 020 (v1.0 cutover)
                   │
                   └── 021 (parallel)

        Parallel from session start:
        - 016 → 020
        - 017 → 020
        - 018 → 020
        - 011a (no downstream blocker)
        - 098 (hardening)
        - 103-107 (token-eff)
```

After Session 3 (estimate): bitwize-music uninstallable, agency-system
v1.0 shipped. Remaining 24+ specs become continuous improvement.

## Decisions deferred to your judgment

- Context Mode path (108 vs 111-113). Read both spec heads + decide.
- Whether to keep the refactor branch `claude/agency-plugin-refactor-PgMQ4`
  alive or delete it (currently identical to Master).
- Whether to revive PR #23 (Soul.md framework, queued since 2026-05-15)
  in this session or defer until after v1.0 ships.
- Quota: yesterday burned ~15 Jules sessions including silent-fails.
  Budget Wave B+C completion at ~10-15 healthy Jules sessions plus
  3-5 local subagent fallbacks. Pace accordingly.

## Out of scope

- Music side production work (artists/, audio/, documents/) — unchanged.
- bitwize-music plugin itself — owned by Spec 020 at the cutover.
- Any new feature not enumerated in the 30 ready specs. New ideas →
  draft a spec under Plan/, do not implement inline.

## Recovered tooling

Watcher pattern: `/tmp/jules_combined_watcher.py` exists but is
container-ephemeral. Respawn it after dispatching the first Jules
session. Heartbeat mode was tried and reverted (token cost > benefit).
For polling, the watcher's internal-loop mode (sleep 60s, exits on
real events) is enough.

Patch extractor: `tools/jules-patch-extract.py` is the canonical
recovery path. Document is in `Plan/JULES_PROTOCOL.md §8`.

Patch archive: `tools/jules-archive/` holds 5 forensic patches from
yesterday's silent-fail sessions. Read-only audit trail.
