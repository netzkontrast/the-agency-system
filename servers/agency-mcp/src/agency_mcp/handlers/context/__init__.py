from fastmcp import FastMCP
import mcp.types as types
import atexit
import datetime
from agency_mcp.handlers.context.anchors import register_context_anchor_tools, _get_manifest, _context_cache, change_log, clear_search_describe_cache
from agency_mcp.handlers.context.resources import register_context_resources, emit_resource_updated
from agency_mcp.lib.codemode.context_watcher import ContextWatcher, ChangeEvent

def register_context_handlers(mcp: FastMCP) -> None:
    register_context_anchor_tools(mcp)
    register_context_resources(mcp)

    manifest = _get_manifest()

    def on_change(event: ChangeEvent):
        # a) invalidate cache
        _context_cache.invalidate(event.id)
        clear_search_describe_cache()

        # b) append to log
        now = datetime.datetime.now(datetime.timezone.utc)
        change_log.append((event, now))

        # c) emit resource updated
        uri = f"context://{event.id.replace(':', '-')}"
        emit_resource_updated(uri, mcp)

    watcher = ContextWatcher(manifest, on_change, mcp=mcp)
    watcher.start()
    atexit.register(watcher.stop)
