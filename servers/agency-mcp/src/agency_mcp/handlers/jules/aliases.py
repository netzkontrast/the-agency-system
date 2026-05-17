import os
import importlib.util
from fastmcp import FastMCP

def _load_sessions_state():
    """Locate sessions_state via BOTH paths:
    (a) Try `from jules_plugin.lib import sessions_state` first
    (b) Fall back to dynamic load from `${CLAUDE_PLUGIN_ROOT}/lib/sessions_state.py`
    (c) Final fallback: relative path `../../lib/sessions_state.py`
    """
    try:
        from jules_plugin.lib import sessions_state
        return sessions_state
    except ImportError:
        pass

    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if plugin_root:
        path = os.path.join(plugin_root, "lib", "sessions_state.py")
        if os.path.exists(path):
            spec = importlib.util.spec_from_file_location("sessions_state", path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                return module

    # Final fallback
    this_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(this_dir, "..", "..", "..", "..", "lib", "sessions_state.py")
    if os.path.exists(path):
        spec = importlib.util.spec_from_file_location("sessions_state", path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module

    return None

def jules_resolve_alias(name_or_id: str) -> dict:
    """Resolve a session alias or id to its canonical session id.

    Args:
        name_or_id: The alias or id to resolve.

    Returns: {"id": "..."} on success, {"error": "..."} on failure.
    """
    sessions_state = _load_sessions_state()
    if sessions_state is None:
        return {"error": "sessions_state is unavailable"}

    resolved = sessions_state.resolve(name_or_id)
    if resolved:
        return {"id": resolved}
    return {"error": f"Session alias or id not found: {name_or_id}"}

def register_alias_tools(mcp: FastMCP) -> None:
    mcp.tool(tags={"domain:jules"})(jules_resolve_alias)
