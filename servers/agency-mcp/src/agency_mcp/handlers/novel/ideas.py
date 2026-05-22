import uuid
from pathlib import Path
from datetime import datetime, timezone

from fastmcp import FastMCP
from agency_mcp.handlers.novel import _shared
from agency_mcp.handlers.novel.work_ops import novel_create_work

try:
    from agency_mcp.config import PLUGIN_ROOT
except ImportError:
    PLUGIN_ROOT = Path(".").resolve()


def _get_empty_state() -> dict:
    return {"premise_ideas": {}}

async def _get_novel_state() -> dict:
    state = await _shared.get_cache().snapshot()
    return state.get("novel", _get_empty_state())

async def novel_create_premise_idea(title: str, logline: str, author_hint: str = None, dry_run: bool = False) -> dict:
    if dry_run:
        return {
            "ok": True,
            "data": {
                "would_apply": True,
                "diff": [{"op": "add", "path": "/premise_ideas/new_id", "value": {"title": title, "logline": logline}}]
            },
            "warnings": []
        }

    state = await _get_novel_state()
    ideas = state.get("premise_ideas", {})

    idea_id = str(uuid.uuid4())
    ideas[idea_id] = {
        "title": title,
        "logline": logline,
        "author_hint": author_hint,
        "status": "draft",
        "created": datetime.now(timezone.utc).isoformat()
    }

    novel_state = await _get_novel_state()
    novel_state["premise_ideas"] = ideas
    await _shared.get_cache().write("novel", novel_state)
    return {"ok": True, "data": {"id": idea_id}, "warnings": []}

async def novel_list_premise_ideas(status: str = None, limit: int = None, cursor: str = None) -> dict:
    from agency_mcp.handlers.novel._shared import decode_cursor, encode_cursor

    state = await _get_novel_state()
    ideas = state.get("premise_ideas", {})

    all_results = []
    for idea_id, idea in ideas.items():
        if status and idea.get("status") != status:
            continue
        all_results.append({
            "id": idea_id,
            "name": idea.get("title"),
            "summary": idea.get("logline", "")[:100] + "..."
        })

    c_data = decode_cursor(cursor, default_limit=20)
    offset = c_data["offset"]
    effective_limit = limit if limit is not None else c_data["limit"]

    paginated = all_results[offset : offset + effective_limit]

    next_cursor = None
    if offset + effective_limit < len(all_results):
        next_cursor = encode_cursor(offset + effective_limit, effective_limit)

    return {"ok": True, "data": {"items": paginated, "count": len(paginated), "next_cursor": next_cursor}, "warnings": []}

async def novel_get_premise_idea(idea_id: str) -> dict:
    state = await _get_novel_state()
    ideas = state.get("premise_ideas", {})

    if idea_id not in ideas:
        return {"ok": False, "warnings": ["Idea not found"]}

    return {"ok": True, "data": {"idea": ideas[idea_id]}, "warnings": []}

async def novel_update_premise_idea(idea_id: str, title: str = None, logline: str = None, dry_run: bool = False) -> dict:
    state = await _get_novel_state()
    ideas = state.get("premise_ideas", {})

    if idea_id not in ideas:
        return {"ok": False, "warnings": ["Idea not found"]}

    if dry_run:
        diffs = []
        if title:
            diffs.append({"op": "replace", "path": f"/premise_ideas/{idea_id}/title", "value": title})
        if logline:
            diffs.append({"op": "replace", "path": f"/premise_ideas/{idea_id}/logline", "value": logline})
        return {
            "ok": True,
            "data": {"would_apply": True, "diff": diffs},
            "warnings": []
        }

    if title:
        ideas[idea_id]["title"] = title
    if logline:
        ideas[idea_id]["logline"] = logline

    ideas[idea_id]["updated"] = datetime.now(timezone.utc).isoformat()

    novel_state = await _get_novel_state()
    novel_state["premise_ideas"] = ideas
    await _shared.get_cache().write("novel", novel_state)
    return {"ok": True, "data": {"updated": True}, "warnings": []}

async def novel_delete_premise_idea(idea_id: str, dry_run: bool = False) -> dict:
    state = await _get_novel_state()
    ideas = state.get("premise_ideas", {})

    if idea_id not in ideas:
        return {"ok": False, "warnings": ["Idea not found"]}

    if dry_run:
        return {
            "ok": True,
            "data": {
                "would_apply": True,
                "diff": [{"op": "remove", "path": f"/premise_ideas/{idea_id}"}]
            },
            "warnings": []
        }

    del ideas[idea_id]
    novel_state = await _get_novel_state()
    novel_state["premise_ideas"] = ideas
    await _shared.get_cache().write("novel", novel_state)
    return {"ok": True, "data": {"deleted": True}, "warnings": []}

async def novel_promote_premise(idea_id: str, author: str, genre: str, slug: str, dry_run: bool = False) -> dict:
    state = await _get_novel_state()
    ideas = state.get("premise_ideas", {})

    if idea_id not in ideas:
        return {"ok": False, "warnings": ["Idea not found"]}

    idea = ideas[idea_id]

    if dry_run:
        return {
            "ok": True,
            "data": {
                "would_apply": True,
                "diff": [
                    {"op": "replace", "path": f"/premise_ideas/{idea_id}/status", "value": "promoted"},
                    {"op": "replace", "path": f"/premise_ideas/{idea_id}/promoted_to", "value": f"{author}/{genre}/{slug}"},
                    f"Create work {author}/{genre}/{slug}"
                ]
            },
            "warnings": []
        }

    # Call create work
    res = await novel_create_work(
        author=author,
        genre=genre,
        slug=slug,
        title=idea.get("title"),
        logline=idea.get("logline"),
        dry_run=False
    )

    if not res.get("ok"):
        return res

    # Update status
    idea["status"] = "promoted"
    idea["promoted_to"] = f"{author}/{genre}/{slug}"

    novel_state = await _get_novel_state()
    novel_state["premise_ideas"] = ideas
    await _shared.get_cache().write("novel", novel_state)

    return {"ok": True, "data": {"promoted": True, "work": idea["promoted_to"]}, "warnings": []}

def register(mcp: FastMCP) -> None:
    mcp.tool(tags={"domain:novel"})(novel_create_premise_idea)
    mcp.tool(tags={"domain:novel"})(novel_list_premise_ideas)
    mcp.tool(tags={"domain:novel"})(novel_get_premise_idea)
    mcp.tool(tags={"domain:novel"})(novel_update_premise_idea)
    mcp.tool(tags={"domain:novel"})(novel_delete_premise_idea)
    mcp.tool(tags={"domain:novel"})(novel_promote_premise)
