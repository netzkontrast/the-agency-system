from fastmcp import FastMCP
try:
    from fastmcp.experimental.transforms.code_mode import CodeMode
    _transforms = [CodeMode()]
except ImportError:
    _transforms = []  # ship without Code Mode if extra is unavailable

from .tools.lifecycle import (
    register_lifecycle_tools,
    jules_create,
    jules_resolve_source,
    jules_list,
    jules_get,
    jules_activities,
    jules_plan,
    jules_approve,
    jules_message,
    jules_stop,
)
from .tools.patches import register_patch_tools
from .tools.bulk import (
    register_bulk_tools,
    jules_status_all,
    jules_approve_awaiting,
    jules_quota,
)
from .tools.aliases import register_alias_tools

# The bulk CLI imports `from jules_mcp import server as mod` and calls
# `mod.jules_*(...)`; the helpers above are re-exported here so the CLI
# does not need to know which sub-module owns each tool.
__all__ = [
    "create_mcp",
    "jules_create",
    "jules_resolve_source",
    "jules_list",
    "jules_get",
    "jules_activities",
    "jules_plan",
    "jules_approve",
    "jules_message",
    "jules_stop",
    "jules_status_all",
    "jules_approve_awaiting",
    "jules_quota",
]

def create_mcp() -> FastMCP:
    mcp = FastMCP("jules-orchestrator", transforms=_transforms)
    register_lifecycle_tools(mcp)
    register_patch_tools(mcp)
    register_bulk_tools(mcp)
    register_alias_tools(mcp)
    return mcp

if __name__ == "__main__":
    create_mcp().run()
