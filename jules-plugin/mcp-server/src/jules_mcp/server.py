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
