#!/usr/bin/env python3
"""Respawn bulk-tools and code-mode after they died at plan stage."""
import importlib.util, json, sys
from pathlib import Path

spec = importlib.util.spec_from_file_location("jm", ".claude/mcp/jules-mcp/server.py")
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)

JOURNAL = Path(".claude/journal")
SOURCE = "sources/github/netzkontrast/the-agency-system"
BRANCH = "claude/create-jules-skill-x8QHA"

PROMPT_TEMPLATE = """\
You are working on PR #27 of netzkontrast/the-agency-system, branch
{branch}. Wave 2 sessions wave1-* have already landed on {branch}.

READ FIRST: docs/superpowers/specs/2026-05-16-jules-suite-refactor-design.md

This is a RESPAWN — a previous session with the same brief died at the
plan stage. Plan ONCE, request approval ONCE, then execute. If you
have any plan questions, embed them in the SINGLE plan you submit
rather than asking iteratively.

Wave 1 modules already exist:
  jules-plugin/mcp-server/src/jules_mcp/{{api,source,trim}}.py
  jules-plugin/skills/jules/SKILL.md + references/
  jules-plugin/lib/{{sessions_state,watch_jules}}.py
  jules-plugin/bin/jules-bulk

[BRIEF]
{brief}
[/BRIEF]

When done push to jules/refactor-{alias} and reply with branch +
summary + pytest pass/fail.
"""

SESSIONS = [
    {
        "alias": "wave2-bulk-tools-v2",
        "title": "Jules refactor wave 2: bulk + alias tools (respawn)",
        "brief": """\
Port the bulk tools into two files:

jules-plugin/mcp-server/src/jules_mcp/tools/bulk.py:
  - jules_status_all (paginated; default fields="id,state,title" via trim.apply_list_trim; fields="*" returns full)
  - jules_approve_awaiting (uses status_all)
  - jules_quota

jules-plugin/mcp-server/src/jules_mcp/tools/aliases.py:
  - jules_resolve_alias

aliases.py MUST locate sessions_state via BOTH paths:
  (a) Try `from jules_plugin.lib import sessions_state` first (when
      the package is properly installed)
  (b) Fall back to dynamic load from `${CLAUDE_PLUGIN_ROOT}/lib/sessions_state.py`
      via importlib.util.spec_from_file_location
  (c) Final fallback: relative path `../../lib/sessions_state.py`
      from this file's location

Source: copy logic from .claude/mcp/jules-mcp/server.py — do not invent
behaviour. Imports use the new modular layout (from .api import _request,
JulesAPIError, _paginate; from .trim import apply_list_trim).

Expose `register_bulk_tools(mcp: FastMCP) -> None` and
`register_alias_tools(mcp: FastMCP) -> None`.

tests/test_bulk.py must include:
  - test_status_all_groups_by_state (mock _request, verify by_state output)
  - test_status_all_trim_default (default trim has only id/state/title)
  - test_quota_counts_today_only (multi-day fixture, verify counting)
  - test_approve_awaiting_only_targets_correct_state (mock so the
    only candidate is AWAITING_PLAN_APPROVAL; verify approve called)

Push to jules/refactor-wave2-bulk-tools-v2.
""",
    },
    {
        "alias": "wave2-code-mode-v2",
        "title": "Jules refactor wave 2: server.py + Code Mode (respawn)",
        "brief": """\
Wire the FastMCP server entrypoint at
jules-plugin/mcp-server/src/jules_mcp/server.py.

Required content (replaces the existing 12-line stub):

  from fastmcp import FastMCP
  try:
      from fastmcp.experimental.transforms.code_mode import CodeMode
      _transforms = [CodeMode()]
  except ImportError:
      _transforms = []  # ship without Code Mode if extra is unavailable

  from .tools.lifecycle import register_lifecycle_tools
  from .tools.patches import register_patch_tools
  from .tools.bulk import register_bulk_tools
  from .tools.aliases import register_alias_tools

  def create_mcp() -> FastMCP:
      mcp = FastMCP("jules-orchestrator", transforms=_transforms)
      register_lifecycle_tools(mcp)
      register_patch_tools(mcp)
      register_bulk_tools(mcp)
      register_alias_tools(mcp)
      return mcp

  if __name__ == "__main__":
      create_mcp().run()

server.py MUST call ALL FOUR register_* functions on the FastMCP
instance.

Update pyproject.toml dependency from 'fastmcp==3.3.1' to
'fastmcp[code-mode]>=3.1.0'. If pip fails to resolve the extra,
fall back to plain 'fastmcp>=3.1.0' and document why in the file.

tests/test_smoke_fastmcp.py:
  import asyncio
  from jules_mcp.server import create_mcp

  def test_registers_all_tools():
      async def go():
          mcp = create_mcp()
          tools = await mcp.list_tools()
          return [t.name for t in tools]
      names = asyncio.run(go())
      jules_tools = [n for n in names if n.startswith("jules_")]
      assert len(jules_tools) >= 16, f"only {len(jules_tools)} jules_* tools: {jules_tools}"

If the wave2-bulk-tools-v2 session has not yet landed when you run, its
modules will be missing — in that case stub the imports with TODO
comments rather than failing the wave; we'll wire them in Wave 3.

Push to jules/refactor-wave2-code-mode-v2.
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
