#!/usr/bin/env python3
"""Wave 1 dispatcher for the Jules suite refactor (PR #27)."""
import importlib.util
import json
import os
import sys
from pathlib import Path

spec = importlib.util.spec_from_file_location("jm", ".claude/mcp/jules-mcp/server.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

JOURNAL = Path(".claude/journal")
JOURNAL.mkdir(parents=True, exist_ok=True)

SOURCE = "sources/github/netzkontrast/the-agency-system"
BRANCH = "claude/create-jules-skill-x8QHA"

PROMPT_TEMPLATE = """\
You are working on PR #27 of netzkontrast/the-agency-system, branch
{branch}. Your scope is described under [BRIEF] below.

READ FIRST: docs/superpowers/specs/2026-05-16-jules-suite-refactor-design.md
This is your single source of truth for layout, dependencies, and DoD.

[BRIEF]
{brief}
[/BRIEF]

When done:
1. Push your work to branch jules/refactor-{alias} based on {branch}.
   Do NOT open a pull request and do NOT push to {branch} directly.
2. Reply with the branch name and a 5-line summary of what changed.
3. If you encounter ambiguity, ask via AWAITING_USER_FEEDBACK rather
   than guessing.

Hard constraints:
- Do not delete or modify files outside your scope.
- Do not touch the .claude/journal/ directory (operator-only).
- Do not push to Master or to {branch} directly.
- Do not modify the design spec at
  docs/superpowers/specs/2026-05-16-jules-suite-refactor-design.md.
- If you add Python deps, list them in pyproject.toml only (not requirements.txt).

Style:
- Add ZERO net comments in code unless WHY is non-obvious.
- Follow the existing repo conventions for type hints and module layout.
- Keep imports minimal — stdlib first, then fastmcp.
"""

SESSIONS = [
    {
        "alias": "wave1-plugin-meta",
        "title": "Jules refactor wave 1: plugin metadata + marketplace",
        "brief": """\
Fix the jules-plugin/ scaffold metadata so the plugin is installable:

1. jules-plugin/.claude-plugin/plugin.json: ensure name='jules-orchestrator',
   version='1.0.0', author={'name': 'The Agency System'}, description set.
   Verify the manifest passes `claude plugin validate ./jules-plugin` if the
   command exists; otherwise just confirm JSON schema correctness.

2. jules-plugin/.claude-plugin/marketplace.json: CREATE this file with:
     {
       "name": "jules-orchestrator",
       "owner": { "name": "netzkontrast" },
       "plugins": [ { "name": "jules-orchestrator", "source": "./" } ]
     }

3. jules-plugin/.mcp.json: REPLACE the current ${PWD}-based env with
   ${CLAUDE_PLUGIN_ROOT}-based paths. Example shape:
     {
       "mcpServers": {
         "jules-orchestrator": {
           "type": "stdio",
           "command": "python3",
           "args": ["-m", "jules_mcp.server"],
           "env": {
             "PYTHONPATH": "${CLAUDE_PLUGIN_ROOT}/mcp-server/src"
           }
         }
       }
     }

4. jules-plugin/README.md: REPLACE the 9-line placeholder with a real
   README covering: (a) what the plugin does, (b) install via
   `claude --plugin-dir ./jules-plugin` for local dev and
   `/plugin install jules-orchestrator@<marketplace>` for distribution,
   (c) required env var `JULES_API_KEY`, (d) one-line smoke test
   (call `jules_list` and expect a sessions array), (e) link to
   docs/superpowers/specs/2026-05-16-jules-suite-refactor-design.md.

Out of scope: do NOT touch mcp-server/src/ or skills/ — those are
Wave 1's other sessions. Do not touch the .claude/ directory.

When done push to jules/refactor-wave1-plugin-meta.
""",
    },
    {
        "alias": "wave1-api-helpers",
        "title": "Jules refactor wave 1: API helpers + trim layer",
        "brief": """\
Port the network and helper layer of the Jules MCP server into modular
files under jules-plugin/mcp-server/src/jules_mcp/. Source files to
copy/refactor from:

  Source:  .claude/mcp/jules-mcp/server.py  (current commit on the PR branch)
  Target:  jules-plugin/mcp-server/src/jules_mcp/{api.py, source.py, trim.py}

1. api.py — contains JulesAPIError, _request, _translate_http_error,
   _paginate, _short_id, _api_key, and BASE_URL. NO tool decorators.
   Pure network layer. Unit-testable without an API key.

2. source.py — contains _resolve_github_source and _coerce_source.
   Imports _paginate from api.py.

3. trim.py — NEW module. Exposes:
     apply_fields(obj: dict, fields: str) -> dict
        # When fields == "*" returns obj unchanged.
        # Otherwise returns only the requested top-level keys
        # (comma-separated). Unknown keys are silently skipped.
     apply_summary(activity: dict) -> dict
        # Returns {id, kind, originator, summary} from a full
        # Activity. Move the existing _activity_kind and
        # _summarize_activity_payload logic here.
     apply_list_trim(items: list[dict], fields: str) -> list[dict]
        # Map apply_fields over a list.

4. tests/test_api.py — covers JulesAPIError shape, _short_id round-trip,
   _translate_http_error mappings for 400/401/403/404/405/409/429/5xx.
   Mock urllib.request.urlopen via unittest.mock to test _request without
   network access.

5. tests/test_source.py — covers _coerce_source for: opaque
   'sources/abc-123', shorthand 'owner/repo', full URL
   'https://github.com/owner/repo.git', empty string raises, malformed
   string raises. Mock _resolve_github_source so no network is hit.

6. tests/test_trim.py — covers apply_fields ('*', subset, unknown),
   apply_summary for each canonical activity kind, apply_list_trim.

DO NOT define @mcp.tool() decorators in these files — those belong in
tools/ and are landed by Wave 2 sessions. This wave only delivers the
helpers.

When done push to jules/refactor-wave1-api-helpers.
""",
    },
    {
        "alias": "wave1-skill-split",
        "title": "Jules refactor wave 1: skill body decomposition",
        "brief": """\
Split the current monolithic .claude/skills/jules/SKILL.md (~900 lines)
into a slim main file plus 6 on-demand reference files under the plugin's
skills/ directory.

Source:  .claude/skills/jules/SKILL.md
Targets:
  jules-plugin/skills/jules/SKILL.md
  jules-plugin/skills/jules/references/state-machine.md
  jules-plugin/skills/jules/references/error-normalization.md
  jules-plugin/skills/jules/references/worked-examples.md
  jules-plugin/skills/jules/references/parallel-orchestration.md
  jules-plugin/skills/jules/references/harvest-patterns.md
  jules-plugin/skills/jules/references/caveats.md

Rules:

1. The new main SKILL.md MUST be <= 300 lines (target 250). It contains:
   - frontmatter (name, description, argument-hint, model, allowed-tools)
   - the "Your Task" intro
   - the MCP tool table (16 tools, one row each)
   - the most critical 3-5 gotchas inline (approve-quickly, stop-not-supported,
     branches-not-patches harvest)
   - explicit pointers to references/ files in the form:
       "See @references/state-machine.md for the full lifecycle."

2. Each references/<topic>.md begins with a 2-sentence purpose line so the
   model knows when to load it.

3. The decomposition checklist MUST be preserved: every state mentioned in
   the old SKILL.md must appear in state-machine.md; every error code
   must appear in error-normalization.md; every example must appear in
   worked-examples.md; etc. Produce a checklist appended to your reply.

4. Update the frontmatter `name` from `jules` to `jules-orchestrator:jules`
   only if Claude Code requires the namespace; otherwise leave as `jules`.

5. The frontmatter `argument-hint` reflects the supported actions
   (`stop` is unsupported — note this in the body).

Out of scope: do NOT modify mcp-server/, do NOT touch lib/ or bin/,
do NOT delete the old .claude/skills/jules/SKILL.md (that's Wave 3).

When done push to jules/refactor-wave1-skill-split.
""",
    },
    {
        "alias": "wave1-helpers-port",
        "title": "Jules refactor wave 1: lib + bin helpers port",
        "brief": """\
Port the three companion files into the plugin layout, fixing only the
path-resolution differences that come from running under the plugin
cache rather than the project tree.

Source -> Target:
  .claude/skills/jules/sessions_state.py -> jules-plugin/lib/sessions_state.py
  .claude/skills/jules/watch_jules.py    -> jules-plugin/lib/watch_jules.py
  .claude/skills/jules/jules_bulk.sh     -> jules-plugin/bin/jules-bulk

Required changes:

1. sessions_state.py: REGISTRY_PATH must resolve to
   ${CLAUDE_PLUGIN_DATA}/sessions.json when CLAUDE_PLUGIN_DATA is set;
   otherwise fall back to a temp directory under the user's home.
   Do NOT default to the script's own directory (that lives in the
   install cache and is wiped on plugin upgrade).

2. watch_jules.py: PIDFILE_PATH and the default --log path must resolve
   under ${CLAUDE_PLUGIN_DATA} with the same fallback. The poller logic
   itself stays identical to the current implementation.

3. bin/jules-bulk: the python subprocess invocations that import from
   '../../mcp/jules-mcp/server.py' must be changed to import from
   'jules_mcp' (the plugin's installed package). Compute the import via
   CLAUDE_PLUGIN_ROOT:
       PYTHONPATH="${CLAUDE_PLUGIN_ROOT}/mcp-server/src" python3 - <<EOF
       from jules_mcp import server as mod
       ...
       EOF
   Make the file executable (chmod +x) and add a shebang.

4. Add docstrings ONLY where the path-resolution behaviour differs from
   the old version. Do not add new features.

5. tests/test_sessions_state.py — small smoke test: upsert two entries,
   reload, verify both present. Use tmp_path fixture, set
   CLAUDE_PLUGIN_DATA env var for the test.

Out of scope: tool definitions (Wave 2), code-mode wiring (Wave 2),
references split (Wave 1's skill-split session).

When done push to jules/refactor-wave1-helpers-port.
""",
    },
]


def main() -> int:
    created = []
    errors = []
    for s in SESSIONS:
        prompt = PROMPT_TEMPLATE.format(branch=BRANCH, alias=s["alias"], brief=s["brief"])
        try:
            resp = mod.jules_create.fn(
                prompt=prompt,
                source=SOURCE,
                starting_branch=BRANCH,
                title=s["title"],
                require_plan_approval=True,
                auto_create_pr=False,
                alias=s["alias"],
            ) if hasattr(mod.jules_create, "fn") else mod.jules_create(
                prompt=prompt, source=SOURCE, starting_branch=BRANCH,
                title=s["title"], require_plan_approval=True,
                auto_create_pr=False, alias=s["alias"],
            )
            sid = resp.get("id") or resp.get("name", "").rsplit("/", 1)[-1]
            url = resp.get("url", "") or f"https://jules.google.com/session/{sid}"
            created.append({"alias": s["alias"], "id": sid, "url": url, "state": resp.get("state")})

            jpath = JOURNAL / f"jules-{s['alias']}.jsonl"
            with jpath.open("w") as fh:
                fh.write(json.dumps({
                    "event": "created", "alias": s["alias"], "id": sid,
                    "url": url, "title": s["title"],
                    "prompt_chars": len(prompt),
                }) + "\n")
        except Exception as e:
            errors.append({"alias": s["alias"], "error": str(e)})

    print(json.dumps({"created": created, "errors": errors}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
