# Jules Suite Refactor — Design + Implementation Plan

**Status:** Approved (user direction in the goal hook).
**Branch:** `claude/create-jules-skill-x8QHA` (PR #27).
**Date:** 2026-05-16.

---

## Goal

Replace the current `.claude/`-resident Jules suite (a tightly-coupled
~2,000-line skill + 1,000-line MCP server) with a **self-contained,
installable Claude Code plugin** at `jules-plugin/`, optimised primarily
for **token efficiency**, secondarily for distribution and discoverability.

Success criteria:

1. `claude --plugin-dir ./jules-plugin` boots and registers all 16 tools
   plus the `/jules-orchestrator:jules` skill.
2. `/plugin install jules-orchestrator@<source>` works against a future
   marketplace, with no project-local `.claude/jules/` required.
3. Common Jules workflows (status check, plan review, approve, harvest
   patch) consume **<30%** of the tokens they do today on a per-turn
   basis. Stretch: <10% for multi-tool workflows via Code Mode.
4. Old `.claude/jules/` + `.claude/mcp/jules-mcp/` directories are
   deleted (full cut-over, no shims).

---

## Token-efficiency strategy (the three knobs)

### 1. FastMCP Code Mode — biggest single win

Server side, one line:

```python
from fastmcp import FastMCP
from fastmcp.experimental.transforms.code_mode import CodeMode

mcp = FastMCP("jules-orchestrator", transforms=[CodeMode()])
```

Install dependency: `fastmcp[code-mode]>=3.1`. Replaces the
"one tool call per action" pattern with a model-written Python snippet
that batches calls inside a sandbox. Benchmarked savings:
**150K → 2K tokens (~98%)** for multi-tool workflows.

Existing `@mcp.tool()` decorations need **zero changes**. The 16 tools
keep their signatures.

### 2. SKILL.md decomposition

Main `SKILL.md` shrinks to ~250 lines: task description, tool table,
critical gotchas. Everything else moves to `references/<topic>.md`
files that the model loads on demand via `Read` only when it actually
hits the topic:

| Reference file | Source (current SKILL.md) | Loaded when |
|---|---|---|
| `state-machine.md` | lines 195–375 | model sees an unfamiliar state |
| `error-normalization.md` | lines 539–555 | a tool returns an HTTP error |
| `worked-examples.md` | lines 558–622 | first session of a project |
| `parallel-orchestration.md` | lines 705–815 | fan-out request |
| `harvest-patterns.md` | lines 820–913 | session reaches COMPLETED |
| `caveats.md` | lines 935–966 | recovery from a known trap |

Saves an estimated **~9,500 tokens** off the always-loaded skill body.

### 3. Per-tool result trimming + opt-in verbosity

Current tools return raw upstream JSON or 500-char string blobs. Trim:

- `jules_list`/`jules_status_all` default to `fields="id,state,title"`;
  pass `fields="*"` for the full record.
- `jules_activities` defaults to `summary_only=True` (returns
  `{id, kind, summary}`); pass `summary_only=False` for full payloads.
- `jules_get` drops `has_outputs`, returns only what the caller asked
  for via a `fields` argument.
- `jules_plan` returns `{steps: [{title}]}` by default;
  `include_descriptions=True` adds the descriptions.

Expected savings: another **40–60%** off routine status checks.

---

## Architecture

### Plugin layout (post-refactor)

```
jules-plugin/
├── .claude-plugin/
│   ├── plugin.json                       # name, version, deps
│   └── marketplace.json                  # for distribution
├── .mcp.json                             # uses ${CLAUDE_PLUGIN_ROOT}
├── README.md                             # install + smoke test
├── mcp-server/
│   ├── pyproject.toml                    # fastmcp[code-mode]>=3.1
│   └── src/jules_mcp/
│       ├── __init__.py                   # package marker
│       ├── server.py                     # FastMCP entry + Code Mode opt-in
│       ├── api.py                        # _request, JulesAPIError, _paginate
│       ├── source.py                     # _coerce_source, _resolve_github_source
│       ├── trim.py                       # fields/summary helpers
│       └── tools/
│           ├── __init__.py
│           ├── lifecycle.py              # create, get, list, activities, plan, approve, message, stop, resolve_source
│           ├── patches.py                # patch, patch_apply, patch_summary
│           ├── bulk.py                   # status_all, approve_awaiting, quota
│           └── aliases.py                # resolve_alias
├── skills/jules/
│   ├── SKILL.md                          # ~250 lines (task + tool table)
│   └── references/
│       ├── state-machine.md
│       ├── error-normalization.md
│       ├── worked-examples.md
│       ├── parallel-orchestration.md
│       ├── harvest-patterns.md
│       └── caveats.md
├── bin/jules-bulk                        # fanout / dashboard / approve-awaiting
├── lib/sessions_state.py                 # alias registry (unchanged behaviour)
├── lib/watch_jules.py                    # background poller (unchanged behaviour)
├── hooks/                                # empty for v1; reserved
└── tests/
    ├── test_api.py                       # _request, JulesAPIError
    ├── test_source.py                    # _coerce_source variants
    ├── test_trim.py                      # fields/summary helpers
    ├── test_activity_kind.py             # kind detector + summarizer
    ├── test_patch_parse.py               # diff metadata + quoted paths
    └── test_smoke_fastmcp.py             # FastMCP registers all tools
```

### Deletions

- `.claude/mcp/jules-mcp/` — gone
- `.claude/skills/jules/` — gone
- `.mcp.json` — `jules` entry removed (project uses the plugin's `.mcp.json`)
- `.claude/settings.json` — `enabledMcpjsonServers: ["jules"]` removed

### Backward compatibility

None. Per user direction: full cut-over. PR description must explain
that anyone consuming the old paths re-installs via the plugin.

---

## Jules orchestration plan

13 Jules sessions across 3 sequential waves. Each session pushes to its
own branch `jules/refactor-<slug>` (per the harvest-via-branches doctrine
in the current skill). After each wave I:

1. Fetch every branch.
2. Run a subagent to review the diff against the wave's spec.
3. If the diff is good: integrate to the PR branch (`claude/create-jules-skill-x8QHA`).
4. If not: one correction round via `jules_message`, re-review, integrate.

### Wave 1 — Foundation (parallel, 4 sessions)

| Alias | Brief |
|---|---|
| `wave1-plugin-meta` | Fix `jules-plugin/.claude-plugin/plugin.json`, write `marketplace.json`, fix `.mcp.json` to use `${CLAUDE_PLUGIN_ROOT}`, write a real `README.md` with install + smoke instructions. No code yet. |
| `wave1-api-helpers` | Port `_request`, `JulesAPIError`, `_paginate`, `_coerce_source`, `_resolve_github_source`, plus a new `lib/trim.py` with `apply_fields()` and `apply_summary()` helpers. Land in `jules-plugin/mcp-server/src/jules_mcp/{api,source,trim}.py`. Unit tests in `tests/test_api.py`, `tests/test_source.py`, `tests/test_trim.py`. |
| `wave1-skill-split` | Move `.claude/skills/jules/SKILL.md` into `jules-plugin/skills/jules/SKILL.md` (slimmed to ~250 lines) plus 6 reference files under `references/`. Update SKILL.md to point at references via `@references/<topic>.md` notation. |
| `wave1-helpers-port` | Port `sessions_state.py` and `watch_jules.py` to `jules-plugin/lib/`. Port `jules_bulk.sh` to `jules-plugin/bin/jules-bulk` (handle the `${CLAUDE_PLUGIN_ROOT}` path resolution). |

### Wave 2 — Tools + Code Mode (parallel, 5 sessions)

| Alias | Brief |
|---|---|
| `wave2-lifecycle-tools` | Port lifecycle tools (`jules_create`, `_get`, `_list`, `_activities`, `_plan`, `_approve`, `_message`, `_stop`, `_resolve_source`) into `tools/lifecycle.py`. Apply trim helpers — every list-style tool defaults to compact output, opt-in verbosity. |
| `wave2-patch-tools` | Port patch tools (`_patch`, `_patch_apply`, `_patch_summary`, `_fetch_patch`, `_parse_diff_metadata`, `_parse_diff_header_b_path`) into `tools/patches.py`. Keep the existing token-cost guards (`max_bytes`, no body in summary/apply). |
| `wave2-bulk-tools` | Port bulk tools (`_status_all`, `_approve_awaiting`, `_quota`, `_resolve_alias`) into `tools/bulk.py` + `tools/aliases.py`. Defaults to trimmed output. |
| `wave2-code-mode` | Wire `FastMCP("jules-orchestrator", transforms=[CodeMode()])` in `server.py`. Add the `fastmcp[code-mode]>=3.1` dep in `pyproject.toml`. Verify all 16 tools still register via the in-process `Client`. |
| `wave2-tests` | Author `tests/test_activity_kind.py`, `tests/test_patch_parse.py`, `tests/test_smoke_fastmcp.py`. Tests must run with `pytest` from `jules-plugin/` and pass without an API key (mock the network). |

### Wave 3 — Cut-over + smoke (sequential, 4 sessions)

| Alias | Brief |
|---|---|
| `wave3-delete-legacy` | Delete `.claude/mcp/jules-mcp/` and `.claude/skills/jules/` from the repo. Update `.mcp.json` (project root) to remove the `jules` entry. Update `.claude/settings.json` to remove Jules-specific allowlists. |
| `wave3-integration-test` | End-to-end smoke: install plugin via `claude --plugin-dir ./jules-plugin`, run `jules_list`, `jules_resolve_source(owner='netzkontrast', repo='the-agency-system')`, verify the FastMCP server boots and serves the tool list. Capture transcript to `jules-plugin/tests/SMOKE.md`. |
| `wave3-claude-md-update` | Update root `CLAUDE.md` to point users at `/plugin install jules-orchestrator` and to mention the Code Mode workflow. Cross-link to the plugin README. |
| `wave3-final-qa` | Run all `pytest` tests, verify nothing imports from the deleted `.claude/jules/` paths, verify `.mcp.json` is clean. Produce a one-page changelog as `jules-plugin/CHANGELOG.md` for the v1 release. |

Total: 13 sessions across 3 waves (well under the 30-session budget).

### Per-session prompt template

Every Jules `create` call uses this prompt skeleton (each `[BRIEF]` is
the per-session task above plus the spec snippet for the relevant
directory). The template encodes the harvest-via-branch doctrine and
sets review expectations:

```
You are working on PR #27 of netzkontrast/the-agency-system, branch
claude/create-jules-skill-x8QHA. Your scope is described under [BRIEF]
below. Read docs/superpowers/specs/2026-05-16-jules-suite-refactor-design.md
for the full design.

[BRIEF]
<inserted per-session>
[/BRIEF]

When done:
1. Push your work to a branch named jules/refactor-<alias> from the PR
   branch above. Do NOT open a pull request.
2. Reply with the branch name and a 5-line summary of what changed.
3. If you encounter ambiguity, ask via the AWAITING_USER_FEEDBACK
   channel rather than guessing.

Constraints:
- Do not delete files outside your scope.
- Do not touch the .claude/journal/ directory.
- Do not push to main/Master or the PR branch directly.
- Run `pytest jules-plugin/tests/ -x` before declaring done; include
  the pass/fail summary in your reply.
```

### Review loop (per session)

When a session reaches `AWAITING_PLAN_APPROVAL`:

1. Fetch the plan via `jules_plan`.
2. Run a subagent to evaluate the plan against the spec; return
   approve/request-changes/reject in <200 words.
3. If approve → `jules_approve`. If request-changes → `jules_message`
   with the diff between plan and spec. If reject → `jules_stop`
   (which is now a no-op; the session continues but our integration
   never picks it up).

When a session reaches `COMPLETED`:

1. Fetch the branch with `git fetch origin jules/refactor-<alias>`.
2. Run a subagent to review the diff (<300 words: pass/fail + specific
   issues + cherry-pick recommendation).
3. If pass → cherry-pick or merge to PR branch.
4. If fail → one correction round via `jules_message` with the review,
   wait for re-completion, re-review.
5. Pipe Jules's reply at every step to
   `.claude/journal/jules-<alias>.jsonl` for the post-mortem.

### Context hygiene

- **Never read Jules's full activity log into the main session.** Use
  `jules_activities(summary_only=True, page_size=5)` and let subagents
  fetch detail.
- **Plan review, diff review, and integration testing run in subagents.**
  The main session only sees their summaries.
- **Journal everything.** Each session has its own `.jsonl` log;
  research and design decisions go in dated markdown.

---

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| Code Mode sandbox restrictions break a tool that needs filesystem (e.g. `jules_patch_apply`) | Tool falls back to classical invocation; Code Mode only optimises the read-only / stateless tools |
| Jules sessions drift from the spec during the AWAITING_PLAN_APPROVAL gate timeout | Set a strict 10-minute SLA on plan review; if missed, the session is abandoned and respawned with a sharper brief |
| Two Wave 2 sessions touch the same file (e.g. both define `_request`) | Wave 1 lands first and merges to PR branch before Wave 2 dispatches; Wave 2 sessions are scoped to disjoint files |
| Marketplace.json format wrong, blocks distribution | Wave 3 final-qa explicitly runs `claude plugin validate ./jules-plugin` |
| Quota burn — 13 sessions in one day | Pre-check `jules_quota`; if remaining < 20, defer Wave 3 to next UTC day |
| The split SKILL.md loses behaviour that lived in the prose | Wave 1 skill-split session must produce a checklist proving every state/error/example from the old SKILL.md is preserved somewhere in references/ |

---

## Definition of done

1. `pytest jules-plugin/tests/ -x` passes.
2. `claude --plugin-dir ./jules-plugin` boots cleanly.
3. `claude mcp list` shows `plugin:jules-orchestrator:jules-orchestrator` as connected when invoked with `JULES_API_KEY` in env.
4. The 16 tools register and respond correctly to a real API call (verified by a one-shot `jules_list`).
5. `.claude/mcp/jules-mcp/` and `.claude/skills/jules/` no longer exist.
6. The PR description on #27 explains the refactor and points reviewers at this spec.
7. Token-cost spot check: a status-check workflow (`jules_list` → `jules_get` → `jules_plan`) executed end-to-end consumes <30% of the tokens it does on `8811a2d`.
