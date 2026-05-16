# REFACTOR_DESIGN.md

## A. Findings Summary

* **FastMCP**: FastMCP uses a decorator-based approach (`@mcp.tool()`) and supports both async and sync tools. The canonical way to structure it is to instantiate `FastMCP("name")` and attach tools. We can split tools across multiple modules and import them into the main server file to keep it organized. 
* **Skills**: Based on Claude Code documentation, skills are `.md` files equipped with YAML frontmatter (`argument-hint`, `model`, `allowed-tools`). The current `SKILL.md` works but is unnecessarily long, acting as both doctrine and API documentation. It should be stripped down to core directives, relying on the MCP tools for actual execution.
* **Plugins**: Claude Code plugins are standalone directories with a specific structure: `.claude-plugin/plugin.json`, `commands/`, `skills/`, `agents/`, `hooks/`, and an `.mcp.json`. Plugins bundle tools, commands, and skills together, making them shareable and cohesive.
* **MCP Protocol**: The MCP protocol specifies a structured JSON-RPC lifecycle for tool calls. FastMCP abstracts this, but understanding the robust error handling and capability negotiation helps us design clean tool boundaries (e.g., returning structured metadata instead of giant diffs).

## B. Proposed Architecture

The entire suite will be repackaged into a standard Claude Code Plugin directory called `jules-plugin`.

```text
jules-plugin/
├── .claude-plugin/
│   └── plugin.json          # NEW: Plugin metadata and configuration
├── commands/
│   └── jules-bulk.sh        # MOVED & RENAME: from jules_bulk.sh. Bulk operation facade.
├── tools/                   # NEW: Generic runtime tools (shipped with plugin)
│   ├── researcher/
│   │   ├── research.py      # MOVED & GENERALIZED: from .claude/skills/jules/research.py
│   │   ├── requirements.txt # NEW: explicit dependencies for the research tool
│   │   └── cache/           # MOVED: Preserved durable research artifacts
├── skills/
│   └── jules.md             # MOVED & REWRITE: from SKILL.md. Tight doctrine doc.
├── mcp-server/              # NEW: Python package for the FastMCP server and utilities
│   ├── pyproject.toml       # NEW: Defines dependencies (fastmcp, etc.)
│   ├── src/
│   │   ├── jules_mcp/
│   │   │   ├── __init__.py
│   │   │   ├── server.py    # MOVED & REWRITE: Main FastMCP instantiation.
│   │   │   ├── state.py     # MOVED & REWRITE: from sessions_state.py (local JSON registry)
│   │   │   ├── watcher.py   # MOVED & REWRITE: from watch_jules.py (background polling)
│   │   │   └── tools/       # NEW: Split 15+ tools into logical modules
│   │   │       ├── lifecycle.py  # create, stop, start_watcher, stop_watcher
│   │   │       ├── info.py       # list, get, status_all, activities
│   │   │       ├── actions.py    # plan, approve, message
│   │   │       └── patch.py      # patch, patch_summary, patch_apply
├── .mcp.json                # NEW: Points Claude to the local mcp-server
├── README.md                # NEW: Documentation for the plugin
└── tests/                   # NEW: Test suite for the MCP server and state logic
```

## C. Plugin Shape Decision

**Decision:** A **single plugin** located at the repository root (`jules-plugin/`).
**Justification:** The official Anthropic plugin repository examples (e.g., `plugin-dev`, `code-review`) demonstrate that a single plugin folder should contain all related components (skills, commands, MCP configs). Creating separate plugins for the skill and the MCP server would break cohesion and complicate installation. The watcher script will remain a standalone utility within the package, capable of being started/stopped via new MCP tools (`jules_start_watcher`, `jules_stop_watcher`).

`plugin.json`:
```json
{
  "name": "jules-orchestrator",
  "description": "Complete suite for orchestrating Jules asynchronous coding sessions.",
  "version": "1.0.0",
  "author": {
    "name": "The Agency System"
  }
}
```

## D. MCP Server Structure

The MCP server currently has 15 tools in one ~800 line `server.py` file. I propose splitting this into a module-based structure using FastMCP's ability to attach tools. 

`server.py` will act as the entry point:
```python
from fastmcp import FastMCP
from .tools.lifecycle import register_lifecycle_tools
from .tools.info import register_info_tools
from .tools.actions import register_action_tools
from .tools.patch import register_patch_tools

mcp = FastMCP("jules")

register_lifecycle_tools(mcp)
register_info_tools(mcp)
register_action_tools(mcp)
register_patch_tools(mcp)
```

## E. Skill Rewrite Plan

The current `SKILL.md` (~900 lines) will be drastically reduced. A fresh reader should grok it in 10 minutes.
1. **Introduction:** What Jules is and when to use it (async coding agent).
2. **Core Directive:** "ALWAYS use the `mcp__jules__*` tools. Never use raw curl."
3. **Tool Overview:** A bulleted list of the tools with one-line descriptions. Remove the verbose curl examples and manual API payload docs since the MCP server abstracts this.
4. **Lifecycle & Quota:** Doctrine on how to spawn, when to approve (`jules_approve`), and the strict 100/day quota (`jules_quota`).
5. **Fan-out/Parallelism:** Brief rules on how to orchestrate parallel sessions.

## F. Test Strategy

* **Framework:** `pytest` for the Python MCP server and state logic.
* **Layout:** `jules-plugin/tests/` with `test_state.py`, `test_tools_lifecycle.py`, etc.
* **Mocking:** All HTTP calls to `https://jules.googleapis.com` will be mocked using `responses` or `unittest.mock`. `JULES_API_KEY` presence will be mocked.
* **Smoke Tests:** A shell script `test_smoke.sh` that stands up the MCP server locally and pings it using FastMCP's CLI/inspector, ensuring no runtime import errors.
* **Execution:** Users can run `pytest jules-plugin/tests` and `./jules-plugin/tests/test_smoke.sh`.

## G. Migration Plan

1. Create the new `jules-plugin/` directory structure.
2. Copy/Refactor files into the new structure step-by-step.
3. Update `.claude/settings.json` and the root `.mcp.json` to point to the new plugin path to seamlessly transition.
4. Run tests against the new plugin structure.
5. Once verified, delete the old `.claude/skills/jules/` and `.claude/mcp/jules-mcp/` directories.

## H. Risk Register

1. **Missing `JULES_API_KEY` in plugin env:** *Mitigation:* Ensure the plugin's `.mcp.json` clearly defines the `JULES_API_KEY` environment variable requirement.
2. **Relative pathing breaks:** *Mitigation:* Use strict `__file__` based absolute path resolution for state JSON files and logs.
3. **FastMCP version mismatches:** *Mitigation:* Explicitly pin the required `fastmcp` version in `pyproject.toml`.
4. **Breaking existing callers during transition:** *Mitigation:* Keep the old files intact until the very last step of the migration, only pointing Claude to the new plugin once it's fully ready.

## I. Open Question: Sub-session Creation

**Answer:** No. A Jules session **cannot** create new Jules sessions autonomously because it does not have access to the `JULES_API_KEY` inside the sandbox environment. The orchestrator operating on the host machine holds the key and must spawn the sessions.

---

## J. Publish-as-Workflow
Publishing intermediate work to the remote branch must be a routine step at the end of each phase. After completing a phase, the work will be committed and pushed to a remote branch (e.g., `jules/plugin-refactor-<sessionId>`). The orchestrator integrates incrementally by fetching and cherry-picking. Work will not pile up on the VM.

## K. Research Artifacts Policy
Only the generalized research tool itself and the durable research *results* (the cache and index) will be preserved. Any intermediate scratch files or test scripts will be dropped. The cache serves as the durable artifact that the design doc references.

## L. Generalize the Research Tool
`research.py` will be shipped as part of the plugin payload (`jules-plugin/tools/researcher/research.py`) for use by humans and future agents. It will be topic-agnostic, with a configurable cache location via arguments or environment variables, acting as a general-purpose robust fetcher and indexer.

## M. Improve the Tool with Dependencies
The generalized research tool will use the following pinned dependencies (in `requirements.txt`) to vastly improve output quality:
* `httpx`: Provides modern, async-capable HTTP fetching with proper redirect handling and timeouts.
* `trafilatura`: Excellent for extracting core article content from HTML, automatically stripping away navigation, footers, and noise.
* `markdownify`: Converts the cleaned HTML into readable Markdown, which is much denser and easier for LLMs to read than raw HTML or basic text extraction.
* `rich`: Provides clear, formatted terminal output for listing and summarizing the index.

## N. Strict Token-Efficiency Policy
Every tool (MCP, CLI, bash) will default to returning the **smallest** representation that answers the caller's question (summaries, counts, IDs). 
* Opt-in flags (`--full`, `max_bytes=N`) will be required to get full content.
* Large payload tools (`jules_patch`, `jules_activities`) will have a corresponding metadata-only `_summary` version. 
* Every MCP tool docstring will document its expected worst-case response size.
