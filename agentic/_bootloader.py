import tomli
from pathlib import Path
from fastmcp import FastMCP
from agentic._harness.cell_loader import discover
from agentic._harness.fastmcp_boot import register_four_verb_contract
from context._hooks.pre_tool_use import validate_envelope_in
from context._hooks.post_tool_use import ingest as ingest_envelope
import sys
import json


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
    """Plugin entrypoint. Builds the server, scans cells, registers everything."""
    version = get_version()
    mcp = FastMCP("agency-system", version=version)

    registry = discover()
    register_four_verb_contract(mcp, registry)

    # Register all dynamically discovered tools with defer_schema=True.
    # Bind t_name/t_func via default args to avoid late-binding closure capture.
    for t_name, t_func in registry.tools.items():
        def _wrapper(*, _t_name=t_name, _t_func=t_func, **kwargs) -> dict:
            pre = validate_envelope_in(_t_name, kwargs)
            if not pre.get("ok", True):
                envelope = {
                    "ok": False,
                    "data": {"error": {"code": "PRE_TOOL_USE_INVALID", "errors": pre.get("errors", [])}},
                    "warnings": [],
                    "next_suggested_tools": [],
                }
            else:
                envelope = _t_func(**kwargs)
            ingest_envelope(_t_name, envelope)
            return envelope

        _wrapper.__name__ = t_name
        _wrapper.__doc__ = f"Deferred tool {t_name}"

        mcp.add_tool(_wrapper, name=t_name, defer_schema=True)

    return mcp


if __name__ == "__main__":
    mcp = boot()

    if "--emit-cold-boot" in sys.argv:
        # We simulate the MCP payload for `tools/list` plus some system prompt if needed.
        # The tools are in mcp._local_provider.list_tools() if we inspect the internals
        # but to run it synchronously we just dump the stored tool schemas.
        tools_list = []
        for t in mcp._tool_handlers.values():
            if hasattr(t, "inputSchema") and t.inputSchema is not None:
                schema = t.inputSchema
            else:
                schema = {"type": "object", "properties": {}}

            tools_list.append(
                {"name": t.name, "description": t.description, "inputSchema": schema}
            )

        payload = json.dumps({"tools": tools_list})
        print(payload)
