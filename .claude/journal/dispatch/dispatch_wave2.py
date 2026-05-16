#!/usr/bin/env python3
"""Wave 2 dispatcher — depends on Wave 1 being merged to PR branch first."""
import importlib.util, json, sys
from pathlib import Path

spec = importlib.util.spec_from_file_location("jm", ".claude/mcp/jules-mcp/server.py")
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)

JOURNAL = Path(".claude/journal")
SOURCE = "sources/github/netzkontrast/the-agency-system"
BRANCH = "claude/create-jules-skill-x8QHA"

PROMPT_TEMPLATE = """\
You are working on PR #27 of netzkontrast/the-agency-system, branch
{branch}. Your scope is described under [BRIEF] below.

READ FIRST: docs/superpowers/specs/2026-05-16-jules-suite-refactor-design.md
Wave 1 of this plan is already merged on {branch}. Your work builds on
the foundation it laid:
  - jules-plugin/mcp-server/src/jules_mcp/api.py    (network + JulesAPIError)
  - jules-plugin/mcp-server/src/jules_mcp/source.py (_coerce_source helpers)
  - jules-plugin/mcp-server/src/jules_mcp/trim.py   (apply_fields, apply_summary)
  - jules-plugin/skills/jules/SKILL.md (slim) + references/
  - jules-plugin/lib/* and jules-plugin/bin/jules-bulk

[BRIEF]
{brief}
[/BRIEF]

When done:
1. Push your work to branch jules/refactor-{alias} based on {branch}.
2. Reply with the branch name and a 5-line summary.
3. Run `pytest jules-plugin/tests/ -x` and include pass/fail in your reply.

Hard constraints unchanged from Wave 1 brief. Do not modify the design
spec. Do not push to {branch} directly.
"""

SESSIONS = [
    {
        "alias": "wave2-lifecycle-tools",
        "title": "Jules refactor wave 2: lifecycle tools + trimming",
        "brief": """\
Port the 9 lifecycle tools from .claude/mcp/jules-mcp/server.py into
jules-plugin/mcp-server/src/jules_mcp/tools/lifecycle.py.

Tools: jules_create, jules_get, jules_list, jules_activities, jules_plan,
jules_approve, jules_message, jules_stop, jules_resolve_source.

Apply per-tool trimming using the helpers in jules_mcp.trim:

- jules_list(page_size=20, page_token="", fields="id,state,title"):
  default returns only those 3 keys per session; fields="*" returns all.
- jules_get(session_id, fields="id,state,title"): same pattern.
- jules_activities(session_id, page_size=10, only_kinds="", page_token="",
  summary_only=True): summary_only=True returns {id,kind,originator,summary}
  via apply_summary; False returns the full activity dict.
- jules_plan(session_id, max_pages=5, include_descriptions=False): the
  description field on each step is omitted unless include_descriptions=True.
- jules_create, jules_approve, jules_message, jules_stop, jules_resolve_source:
  unchanged signatures and behaviour from current code.

Register each tool via @mcp.tool() on a FastMCP instance passed in (do NOT
construct the FastMCP instance here — Wave 2's code-mode session owns
server.py). Expose a function `register_lifecycle_tools(mcp: FastMCP) -> None`
that decorates each function and returns nothing.

Imports come from .api, .source, .trim — NOT from the deleted .claude/
paths and NOT from server.py.

tests/test_lifecycle_trim.py — verify jules_list default vs fields='*',
jules_get default vs fields='*', jules_activities summary_only on/off,
jules_plan include_descriptions on/off. Mock _request via unittest.mock.

Push to jules/refactor-wave2-lifecycle-tools.
""",
    },
    {
        "alias": "wave2-patch-tools",
        "title": "Jules refactor wave 2: patch tools",
        "brief": """\
Port the 4 patch-related functions from .claude/mcp/jules-mcp/server.py
into jules-plugin/mcp-server/src/jules_mcp/tools/patches.py:

Tools and helpers:
  - jules_patch_summary, jules_patch_apply, jules_patch (the @mcp.tool entries)
  - _fetch_patch, _parse_diff_metadata, _parse_diff_header_b_path (helpers)

Preserve the existing token-cost guards:
  - jules_patch_summary returns metadata only, never the diff body
  - jules_patch_apply applies on disk, returns metadata only
  - jules_patch defaults max_bytes=60000 and refuses oversize diffs

Expose `register_patch_tools(mcp: FastMCP) -> None`.

tests/test_patch_parse.py — covers _parse_diff_header_b_path with
quoted and unquoted forms, _parse_diff_metadata across multi-file diffs,
and only_files filtering inside jules_patch_apply.

Imports from .api (for _request), no imports from server.py.

Push to jules/refactor-wave2-patch-tools.
""",
    },
    {
        "alias": "wave2-bulk-tools",
        "title": "Jules refactor wave 2: bulk + alias tools",
        "brief": """\
Port the bulk tools into two files:

jules-plugin/mcp-server/src/jules_mcp/tools/bulk.py:
  - jules_status_all (paginated, with trim)
  - jules_approve_awaiting (uses status_all)
  - jules_quota

jules-plugin/mcp-server/src/jules_mcp/tools/aliases.py:
  - jules_resolve_alias (depends on lib/sessions_state.py — import via
    `from jules_plugin import sessions_state` if that works, else load
    the module from CLAUDE_PLUGIN_ROOT/lib/sessions_state.py at runtime)

Apply trim helpers to jules_status_all (default fields="id,state,title").

Expose `register_bulk_tools(mcp: FastMCP) -> None` and
`register_alias_tools(mcp: FastMCP) -> None`.

tests/test_bulk.py — smoke test that jules_status_all groups by state
and that jules_quota correctly computes used_today/remaining when sessions
span multiple UTC days. Mock _request.

Push to jules/refactor-wave2-bulk-tools.
""",
    },
    {
        "alias": "wave2-code-mode",
        "title": "Jules refactor wave 2: server.py + Code Mode",
        "brief": """\
Wire the FastMCP server entrypoint at
jules-plugin/mcp-server/src/jules_mcp/server.py.

Required content (this replaces the existing 12-line stub):

  from fastmcp import FastMCP
  from fastmcp.experimental.transforms.code_mode import CodeMode
  from .tools.lifecycle import register_lifecycle_tools
  from .tools.patches import register_patch_tools
  from .tools.bulk import register_bulk_tools
  from .tools.aliases import register_alias_tools

  def create_mcp() -> FastMCP:
      mcp = FastMCP("jules-orchestrator", transforms=[CodeMode()])
      register_lifecycle_tools(mcp)
      register_patch_tools(mcp)
      register_bulk_tools(mcp)
      register_alias_tools(mcp)
      return mcp

  if __name__ == "__main__":
      create_mcp().run()

If the CodeMode import path is different in the installed fastmcp
version (it may live at fastmcp.transforms.code_mode in a later
release), find the correct import via:
  python3 -c "import fastmcp; print([m for m in dir(fastmcp) if 'transform' in m.lower() or 'code' in m.lower()])"
  python3 -c "from fastmcp.experimental.transforms.code_mode import CodeMode"
Use whichever works.

Update jules-plugin/mcp-server/pyproject.toml to depend on
'fastmcp[code-mode]>=3.1.0' (with the extras).

Add tests/test_smoke_fastmcp.py:
  import asyncio
  from jules_mcp.server import create_mcp
  async def go():
      mcp = create_mcp()
      tools = await mcp.list_tools()
      names = sorted(t.name for t in tools)
      assert "jules_create" in names
      assert "jules_resolve_source" in names
      # Code Mode should expose its meta-tools too:
      assert any(t.name in ("execute","search","get_schema") for t in tools)
      return names
  def test_registers_all_tools():
      names = asyncio.run(go())
      assert len(names) >= 16  # 16 jules tools + code mode meta-tools

If installing fastmcp[code-mode] fails (e.g. the extras don't exist on
this pypi version yet), document the failure in your reply and proceed
WITHOUT the CodeMode transform — keep the registration code commented
out with a TODO. Either way the regular tools must register and the
smoke test must pass on the standard tool list.

Push to jules/refactor-wave2-code-mode.
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
