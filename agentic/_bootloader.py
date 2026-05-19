import tomli
from pathlib import Path
from fastmcp import FastMCP
from agentic._harness.cell_loader import discover
from agentic._harness.fastmcp_boot import register_four_verb_contract
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

    # Register all dynamically discovered tools with defer_schema=True
    for t_name, t_func in registry.tools.items():
        # FastMCP uses the function signature to build schemas or map args.
        # By providing **kwargs and dynamically loading, we defer to the wrapper.
        # We need to construct a wrapper that fastmcp accepts.
        # But we also don't want strict validation on args in the boot loader since the schema is deferred

        # To make FastMCP accept arbitrary args without validation failing at the edge,
        # we accept **kwargs. FastMCP handles **kwargs by mapping JSON parameters to it.
        def _wrapper(**kwargs) -> dict:
            return t_func(**kwargs)

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
