import tomli
from pathlib import Path
from fastmcp import FastMCP
from agentic._harness.cell_loader import discover
from agentic._harness.fastmcp_boot import register_four_verb_contract
from context._hooks.pre_tool_use import validate_envelope_in
from context._hooks.post_tool_use import ingest as ingest_envelope
import sys
import json


def make_hooked_wrapper(t_name, t_func):
    """Wrap a tool function so PreToolUse validation fires before the call
    and PostToolUse ingest fires after. Defaults bind t_name/t_func to
    avoid the closure capture-by-reference bug across loop iterations."""

    def _wrapper(*, _t_name=t_name, _t_func=t_func, **kwargs) -> dict:
        validate_envelope_in(_t_name, kwargs)
        envelope = _t_func(**kwargs)
        ingest_envelope(_t_name, envelope)
        return envelope

    _wrapper.__name__ = t_name
    _wrapper.__doc__ = f"Deferred tool {t_name}"
    return _wrapper


def get_version() -> str:
    pyproject_path = Path("pyproject.toml")
    # For tests, we might not have pyproject in the cwd, try servers/agency-mcp/pyproject.toml
    if not pyproject_path.exists():
        pyproject_path = Path("servers/agency-mcp/pyproject.toml")

    if pyproject_path.exists():
        with open(pyproject_path, "rb") as f:
            data = tomli.load(f)
            return data.get("project", {}).get("version", "0.0.1")
    return "0.0.1"


def boot() -> FastMCP:
    """Plugin entrypoint. Builds the server, scans cells, registers everything.

    Per spec 06 §Cold-boot: only the four verbs are registered as FastMCP
    tools. Individual cell tools live in the CellRegistry and are reached via
    ``mcp__call_tool``. PreToolUse / PostToolUse hooks (C5) fire inside the
    registry's ``call_tool`` dispatch so they cover the deferred-discovery
    path uniformly.
    """
    version = get_version()
    mcp = FastMCP("agency-system", version=version)

    registry = discover()
    _wrap_registry_with_hooks(registry)
    register_four_verb_contract(mcp, registry)

    return mcp


def _wrap_registry_with_hooks(registry) -> None:
    """Wrap every tool in the registry through make_hooked_wrapper so the
    PreToolUse / PostToolUse C5 contract fires uniformly via ``mcp__call_tool``.
    """
    for t_name, t_func in list(registry.tools.items()):
        registry.tools[t_name] = make_hooked_wrapper(t_name, t_func)


if __name__ == "__main__":
    mcp = boot()

    if "--emit-cold-boot" in sys.argv:
        # Cold-boot payload simulation. Matches what an MCP client would see
        # on `tools/list` — only the four verbs are pre-registered with
        # FastMCP per spec 06; every cell tool is reached through
        # mcp__call_tool, so it does NOT appear here.
        import asyncio

        tools_response = asyncio.run(mcp._local_provider.list_tools())
        tools_list = []
        for t in tools_response:
            schema = (
                t.inputSchema
                if getattr(t, "inputSchema", None) is not None
                else {"type": "object", "properties": {}}
            )
            tools_list.append(
                {"name": t.name, "description": t.description, "inputSchema": schema}
            )

        payload = json.dumps({"tools": tools_list})
        print(payload)
