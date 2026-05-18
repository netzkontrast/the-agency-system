from agency_mcp.state.cache import StateCache

_cache: StateCache | None = None

def get_cache() -> StateCache:
    global _cache
    if _cache is None:
        _cache = StateCache()
    return _cache

# Valid states
VALID_STATUSES = ["draft", "in_progress", "review", "done", "archived"]

# Transition rules (current -> allowed next states)
STATUS_TRANSITIONS = {
    "work": {
        "draft": {"in_progress", "archived"},
        "in_progress": {"review", "done", "archived", "draft"},
        "review": {"done", "in_progress", "archived"},
        "done": {"archived"}, # explicitly reject done -> review
        "archived": set() # explicitly reject archived -> draft
    },
    "chapter": {
        "draft": {"in_progress", "archived"},
        "in_progress": {"review", "draft", "archived"},
        "review": {"done", "in_progress", "archived"},
        "done": {"archived", "review"},
        "archived": {"draft"}
    },
    "scene": {
        "draft": {"in_progress", "archived"},
        "in_progress": {"review", "draft", "archived"},
        "review": {"done", "in_progress", "archived"},
        "done": {"archived", "review"},
        "archived": {"draft"}
    }
}

import base64
import json

def encode_cursor(offset: int, limit: int) -> str:
    data = json.dumps({"offset": offset, "limit": limit}).encode("utf-8")
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")

def decode_cursor(cursor: str, default_limit: int = 20) -> dict:
    if not cursor:
        return {"offset": 0, "limit": default_limit}
    try:
        padding = "=" * (4 - (len(cursor) % 4))
        data = base64.urlsafe_b64decode(cursor + padding)
        decoded = json.loads(data.decode("utf-8"))
        # If user didn't specify limit, we might override it with decoded, but the tool signature limit takes precedence
        # unless it was default. We'll handle precedence in the handler.
        return decoded
    except Exception:
        return {"offset": 0, "limit": default_limit}
