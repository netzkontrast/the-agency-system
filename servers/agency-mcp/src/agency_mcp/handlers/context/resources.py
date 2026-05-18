from pathlib import Path
from fastmcp import FastMCP
from agency_mcp.lib.codemode.context_manifest import ContextManifest, load_context_manifest
import mcp.types as types
from mcp.server.lowlevel.server import request_ctx

# Module-level cache
_manifest_cache: ContextManifest | None = None

def _get_manifest() -> ContextManifest:
    global _manifest_cache
    if _manifest_cache is None:
        # Load from default path
        manifest_path = Path(__file__).resolve().parents[2] / "codemode" / "context_manifest.json"
        _manifest_cache = load_context_manifest(str(manifest_path))
    return _manifest_cache

# Track active subscriptions: map of URI to set of active sessions
_subscriptions: dict[str, set] = {}

def _register_mock_session(session):
    # Only for tests
    _subscriptions.setdefault("all", set()).add(session)

def emit_resource_updated(uri: str, mcp: FastMCP) -> None:
    """Emit notifications to all subscribed sessions."""
    import asyncio
    import inspect

    # Send to specific subscribers and fallback mock "all"
    sessions = _subscriptions.get(uri, set()) | _subscriptions.get("all", set())

    for session in sessions:
        if hasattr(session, "send_resource_updated"):
            notification = types.ServerNotification(
                types.ResourceUpdatedNotification(
                    method="notifications/resources/updated",
                    params=types.ResourceUpdatedNotificationParams(uri=uri)
                )
            )
            if inspect.iscoroutinefunction(session.send_notification):
                asyncio.run_coroutine_threadsafe(
                    session.send_notification(notification),
                    session._loop if hasattr(session, "_loop") else asyncio.get_event_loop()
                )
            else:
                session.send_notification(notification)
        elif hasattr(session, "send_notification"): # The mock session uses send_notification
            notification = types.ServerNotification(
                types.ResourceUpdatedNotification(
                    method="notifications/resources/updated",
                    params=types.ResourceUpdatedNotificationParams(uri=uri)
                )
            )
            if inspect.iscoroutinefunction(session.send_notification):
                asyncio.run_coroutine_threadsafe(
                    session.send_notification(notification),
                    session._loop if hasattr(session, "_loop") else asyncio.get_event_loop()
                )
            else:
                session.send_notification(notification)

def register_context_resources(mcp: FastMCP) -> None:
    manifest = _get_manifest()
    
    # 1. We must register subscribe/unsubscribe handlers to track active clients
    @mcp._mcp_server.subscribe_resource()
    async def subscribe_resource(uri: types.AnyUrl):
        uri_str = str(uri)
        session = request_ctx.get().session
        _subscriptions.setdefault(uri_str, set()).add(session)

    @mcp._mcp_server.unsubscribe_resource()
    async def unsubscribe_resource(uri: types.AnyUrl):
        uri_str = str(uri)
        session = request_ctx.get().session
        if uri_str in _subscriptions and session in _subscriptions[uri_str]:
            _subscriptions[uri_str].remove(session)

    # We dynamically register each resource
    for entry in manifest.entries:
        id = entry["id"]
        safe_id = id.replace(":", "-")
        
        mime = entry.get("mime", "text/plain")
        title = entry.get("title", id)
        summary = entry.get("summary", "")
        
        def make_resource_handler(entry_id: str, mapped_id: str):
            @mcp.resource(f"context://{mapped_id}", mime_type=mime, name=title, description=summary)
            def read_resource() -> str:
                m = _get_manifest()
                e = m.get(entry_id)
                if not e:
                    raise ValueError(f"Resource not found: {entry_id}")
                
                file_path = Path(m.repo_root) / e["path"]
                if not file_path.exists():
                    raise ValueError(f"File not found: {e['path']}")
                    
                with open(file_path, "r", encoding="utf-8") as f:
                    return f.read()
            return read_resource
            
        make_resource_handler(id, safe_id)
