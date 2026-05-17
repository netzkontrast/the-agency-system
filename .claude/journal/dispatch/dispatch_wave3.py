#!/usr/bin/env python3
"""Wave 3 dispatcher — sequential, runs after Waves 1+2 are integrated."""
import importlib.util, json, sys
from pathlib import Path

spec = importlib.util.spec_from_file_location("jm", ".claude/mcp/jules-mcp/server.py")
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)

JOURNAL = Path(".claude/journal")
SOURCE = "sources/github/netzkontrast/the-agency-system"
BRANCH = "claude/create-jules-skill-x8QHA"

PROMPT_TEMPLATE = """\
You are working on PR #27 of netzkontrast/the-agency-system, branch
{branch}. Wave 3 finalises the cut-over: legacy paths get deleted,
the plugin gets smoke-tested end-to-end, docs get updated.

READ FIRST: docs/superpowers/specs/2026-05-16-jules-suite-refactor-design.md

By now (Wave 3 dispatch), Waves 1 and 2 are already merged on {branch}.
The plugin under jules-plugin/ should be functionally complete:
mcp-server/src/jules_mcp/ has api.py, source.py, trim.py, server.py
with CodeMode opt-in, tools/{lifecycle,patches,bulk,aliases}.py;
skills/jules/SKILL.md is slim with references/; lib/ + bin/ ported.

[BRIEF]
{brief}
[/BRIEF]

When done push to jules/refactor-{alias}. Reply with branch + summary.
Hard constraints unchanged. Do not modify the design spec.
"""

SESSIONS = [
    {
        "alias": "wave3-delete-legacy",
        "title": "Jules refactor wave 3: delete .claude/ legacy paths",
        "brief": """\
Delete the legacy project-private Jules suite now that jules-plugin/
is functional:

1. Remove the entire directory .claude/mcp/jules-mcp/ (server.py and
   any sibling files).
2. Remove the entire directory .claude/skills/jules/ (SKILL.md,
   sessions_state.py, watch_jules.py, jules_bulk.sh, examples/,
   notifications.jsonl if present, sessions.json if present).
3. Update .mcp.json (project root) to remove the "jules" entry. If
   that leaves the mcpServers map empty, leave it as an empty object
   {"mcpServers": {}} rather than deleting the file.
4. Update .claude/settings.json: remove any entries referencing the
   project-local jules MCP server (likely keys: enabledMcpjsonServers
   containing "jules", and any allow-list entries containing
   "mcp__jules"). Preserve everything else exactly.

Out of scope: do NOT touch jules-plugin/, do NOT touch docs/, do NOT
touch the .claude/journal/ directory.

Verification: after deletion, `grep -rn jules-mcp .claude/ .mcp.json
.claude/settings.json` should return nothing. Include that grep
output (empty) in your reply.
""",
    },
    {
        "alias": "wave3-integration-test",
        "title": "Jules refactor wave 3: end-to-end smoke test",
        "brief": """\
Produce a one-page smoke-test transcript proving the plugin works:

1. Run `claude --plugin-dir ./jules-plugin --help` (or equivalent
   verify command if --help is wrong) to confirm Claude Code recognises
   the plugin without errors. Capture stdout+stderr.

2. Boot the MCP server directly:
     JULES_API_KEY=$JULES_API_KEY PYTHONPATH=jules-plugin/mcp-server/src \\
       python3 -m jules_mcp.server &
     server_pid=$!
     sleep 2
     kill $server_pid
   Capture stderr (it should show the FastMCP banner + 'starting
   jules-mcp' log line, no tracebacks).

3. In-process tool registration check:
     python3 -c "
     import asyncio
     from jules_mcp.server import create_mcp
     async def go():
         mcp = create_mcp()
         tools = await mcp.list_tools()
         print(sorted(t.name for t in tools))
     asyncio.run(go())
     "
   Expect to see all 16 jules_* tools.

4. End-to-end API call:
     python3 -c "
     import asyncio
     from jules_mcp.server import create_mcp
     async def go():
         mcp = create_mcp()
         tool = await mcp.get_tool('jules_list')
         r = await tool.run({'page_size': 3})
         print(r)
     asyncio.run(go())
     "
   Expect a JSON-shaped response with a 'sessions' array.

Save the full transcript to jules-plugin/tests/SMOKE.md (markdown,
fenced code blocks per step). Include pass/fail verdict per step at
the top.

If a step fails, document the failure inline and proceed with the
remaining steps. Do not 'fix' bugs in jules-plugin/ as part of this
session — file them in SMOKE.md as known issues for follow-up.
""",
    },
    {
        "alias": "wave3-claude-md-update",
        "title": "Jules refactor wave 3: update CLAUDE.md and changelog",
        "brief": """\
Update the root CLAUDE.md (the file at /home/user/the-agency-system/CLAUDE.md)
to reflect the new plugin-based install path. Specifically:

1. Add a section near "Most important commands & skills" titled
   "Jules orchestration plugin" with:
   - Install command for local dev: `claude --plugin-dir ./jules-plugin`
   - Install for distribution: `/plugin install jules-orchestrator@netzkontrast`
   - One-line summary of what's included (MCP server with 16 tools,
     SKILL.md with references/, lib/ helpers, bin/jules-bulk)
   - Pointer to design spec at
     docs/superpowers/specs/2026-05-16-jules-suite-refactor-design.md

2. Search the rest of CLAUDE.md for any reference to .claude/skills/jules/
   or .claude/mcp/jules-mcp/ and either delete the line or update it
   to point at jules-plugin/.

3. Create jules-plugin/CHANGELOG.md with v1.0.0 release notes:
   - 16 MCP tools (list them)
   - FastMCP Code Mode opt-in (if Wave 2's code-mode session succeeded;
     check jules-plugin/mcp-server/pyproject.toml for fastmcp[code-mode]
     dependency to confirm)
   - Skill split into references/
   - Helpers ported with ${CLAUDE_PLUGIN_DATA}-aware paths
   - Stop action removed (Jules API does not support cancellation)

Out of scope: do NOT touch jules-plugin/skills/, do NOT modify the
design spec, do NOT touch the .claude/journal/ directory.
""",
    },
    {
        "alias": "wave3-final-qa",
        "title": "Jules refactor wave 3: final QA pass",
        "brief": """\
Final quality gate before the refactor is declared done:

1. `pytest jules-plugin/tests/ -x -v` — must pass all tests. Capture
   the pass/fail summary.

2. Verify no remaining imports from the deleted paths:
     grep -rn "from .claude" .
     grep -rn "import sessions_state" .
     grep -rn "from jules_mcp.server" jules-plugin/   # OK only inside tests
     grep -rn ".claude/mcp/jules-mcp" .
     grep -rn ".claude/skills/jules" . | grep -v ".claude/journal"
   All five greps (except the journal-allowed jules-mcp reference)
   should be empty. Capture each result.

3. Verify `.mcp.json` is clean:
     cat .mcp.json
   Should show no "jules" entry (only stuff unrelated to this refactor).

4. Verify the plugin manifest schema:
     python3 -c "
     import json
     m = json.load(open('jules-plugin/.claude-plugin/plugin.json'))
     mkt = json.load(open('jules-plugin/.claude-plugin/marketplace.json'))
     assert 'name' in m and 'version' in m
     assert 'plugins' in mkt
     print('manifest OK:', m['name'], m['version'])
     "

5. Verify token-cost spot check: run jules_list (default trim) and
   measure the JSON response size. Compare against the equivalent
   on commit 8811a2d (untrimmed). Report the percentage reduction.

Produce a one-page QA report at jules-plugin/tests/QA-WAVE3.md with
the results of each step. If anything fails, list it as a blocker.

Out of scope: do NOT fix bugs found during QA — file them in the
report. Do not touch the design spec.
""",
    },
]


def main() -> int:
    created = []; errors = []
    for s in SESSIONS:
        prompt = PROMPT_TEMPLATE.format(branch=BRANCH, alias=s["alias"], brief=s["brief"])
        try:
            fn = getattr(mod.jules_create, "fn", mod.jules_create)
            resp = fn(prompt=prompt, source=SOURCE, starting_branch=BRANCH,
                      title=s["title"], require_plan_approval=True,
                      auto_create_pr=False, alias=s["alias"])
            sid = resp.get("id") or resp.get("name", "").rsplit("/", 1)[-1]
            url = resp.get("url", "") or f"https://jules.google.com/session/{sid}"
            created.append({"alias": s["alias"], "id": sid, "url": url, "state": resp.get("state")})
            jpath = JOURNAL / f"jules-{s['alias']}.jsonl"
            with jpath.open("w") as fh:
                fh.write(json.dumps({"event": "created", "alias": s["alias"], "id": sid,
                                      "url": url, "title": s["title"],
                                      "prompt_chars": len(prompt)}) + "\n")
        except Exception as e:
            errors.append({"alias": s["alias"], "error": str(e)})
    print(json.dumps({"created": created, "errors": errors}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
