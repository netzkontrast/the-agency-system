from typing import Any
from agency_mcp.state.cache import StateCache

_cache: StateCache | None = None


def _get_cache() -> StateCache:
    global _cache
    if _cache is None:
        _cache = StateCache()
    return _cache


async def shared_get_session() -> dict[str, Any]:
    cache = _get_cache()
    state = await cache.snapshot()
    session_data = state.get("_session", {})
    return {
        "ok": True,
        "data": session_data,
        "warnings": [],
        "artefacts_written": [],
        "next_suggested_tools": [],
    }


async def shared_update_session(patch: dict, dry_run: bool = False) -> dict[str, Any]:
    cache = _get_cache()
    state = await cache.snapshot()
    session_data = state.get("_session", {})

    diff = {}
    for k, v in patch.items():
        if session_data.get(k) != v:
            diff[k] = {"from": session_data.get(k), "to": v}

    if dry_run:
        return {
            "ok": True,
            "data": {"would_apply": True, "diff": diff},
            "warnings": [],
            "artefacts_written": [],
            "next_suggested_tools": [],
        }

    if diff:
        # [Deliberate cache-extension]
        # Since cache.write strictly validates namespaces ["music", "novel", "jules", "agentic"]
        # and _session is a top level key, we write by bypassing cache.write and directly
        # mutating the JSON file using a lock, extending the cache capability intentionally.
        # The spec says "write through StateCache's lock."
        async with cache._lock:
            # We must load, mutate _session, and save
            if cache._is_stale() or cache._state is None:
                cache._load_from_disk()
            if cache._state is None:
                cache._state = {
                    "music": {},
                    "novel": {},
                    "jules": {},
                    "agentic": {},
                    "_version": "1.0.0",
                }

            if "_session" not in cache._state:
                cache._state["_session"] = {}

            for k, v in patch.items():
                cache._state["_session"][k] = v

            cache._write_to_disk()

    return {
        "ok": True,
        "data": {"applied": True, "diff": diff},
        "warnings": [],
        "artefacts_written": [],
        "next_suggested_tools": [],
    }


async def shared_get_pending_verifications() -> dict[str, Any]:
    cache = _get_cache()
    state = await cache.snapshot()
    session_data = state.get("_session", {})
    pending = session_data.get("pending_verifications", [])
    return {
        "ok": True,
        "data": pending,
        "warnings": [],
        "artefacts_written": [],
        "next_suggested_tools": [],
    }
