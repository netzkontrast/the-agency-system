from typing import Any
from ._shared import _short_id

_ACTIVITY_META_KEYS = {
    "name", "id", "createTime", "updateTime", "originator",
    "description", "artifacts",
}

_ACTIVITY_KINDS = {
    "agentMessaged", "userMessaged", "planGenerated", "planApproved",
    "progressUpdated", "sessionCompleted", "sessionFailed",
}

def apply_fields(obj: dict, fields: str) -> dict:
    if fields == "*":
        return obj
    wanted = {f.strip() for f in fields.split(",") if f.strip()}
    if not wanted:
        return obj
    return {k: v for k, v in obj.items() if k in wanted}

def apply_list_trim(items: list[dict], fields: str) -> list[dict]:
    return [apply_fields(item, fields) for item in items]

def _activity_kind(a: dict) -> str:
    """Pick the activity's event kind, preferring known oneof members over
    arbitrary metadata fields. Falls back to the first unknown key only when
    no canonical kind matches."""
    for k in _ACTIVITY_KINDS:
        if k in a:
            return k
    for k in a.keys():
        if k not in _ACTIVITY_META_KEYS:
            return k
    return "unknown"

def _summarize_activity_payload(kind: str, payload: Any, activity: dict | None = None) -> str:
    if kind == "planGenerated" and isinstance(payload, dict):
        plan = payload.get("plan") or {}
        steps = plan.get("steps") or []
        if not steps:
            return "(empty plan)"
        return "; ".join(f"{s.get('title', '?')}" for s in steps[:6])
    if kind == "agentMessaged" and isinstance(payload, dict):
        text = payload.get("agentMessage") or ""
        return (text[:300] + "…") if len(text) > 300 else text
    if kind == "userMessaged" and isinstance(payload, dict):
        text = payload.get("userMessage") or ""
        return (text[:300] + "…") if len(text) > 300 else text
    if kind == "sessionFailed" and isinstance(payload, dict):
        return payload.get("reason") or "(no reason given)"
    if kind == "sessionCompleted":
        return "session completed"
    if kind == "planApproved":
        return "plan approved"
    if kind == "progressUpdated" and isinstance(payload, dict):
        title = payload.get("title") or ""
        desc = payload.get("description") or ""
        return f"{title}: {desc}".strip(": ") if (title or desc) else "progress"
    if activity is not None:
        arts = activity.get("artifacts")
        if arts and isinstance(arts, list):
            return f"artifacts updated: {len(arts)} paths"
    return "(unrecognized activity shape)"

def apply_summary(activity: dict) -> dict:
    kind = _activity_kind(activity)
    summary = _summarize_activity_payload(kind, activity.get(kind), activity)

    return {
        "id": _short_id(activity.get("name", activity.get("id", ""))),
        "originator": activity.get("originator"),
        "kind": kind,
        "summary": summary,
    }
