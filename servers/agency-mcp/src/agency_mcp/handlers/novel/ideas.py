import uuid
from pathlib import Path
from datetime import datetime, timezone

from fastmcp import FastMCP
from agency_mcp.state.cache import StateCache
from agency_mcp.handlers.novel.work_ops import novel_create_work

try:
    from agency_mcp.config import PLUGIN_ROOT
except ImportError:
    PLUGIN_ROOT = Path(".").resolve()

def _get_cache():
    return StateCache()
cache = _get_cache()

def _get_empty_state() -> dict:
    return {"premise_ideas": {}}

async def _get_novel_state() -> dict:
    state = await cache.snapshot()
    return state.get("novel", _get_empty_state())

async def novel_create_premise_idea(title: str, logline: str, author_hint: str = None) -> dict:
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
    await cache.write("novel", novel_state)
    return {"ok": True, "data": {"id": idea_id}, "warnings": []}

async def novel_list_premise_ideas(status: str = None) -> dict:
    state = await _get_novel_state()
    ideas = state.get("premise_ideas", {})

    results = []
    for idea_id, idea in ideas.items():
        if status and idea.get("status") != status:
            continue
        results.append({
            "id": idea_id,
            "name": idea.get("title"),
            "summary": idea.get("logline", "")[:100] + "..."
        })
        if len(results) >= 20:
            break

    return {"ok": True, "data": {"results": results, "count": len(results)}, "warnings": []}

async def novel_get_premise_idea(idea_id: str) -> dict:
    state = await _get_novel_state()
    ideas = state.get("premise_ideas", {})

    if idea_id not in ideas:
        return {"ok": False, "warnings": ["Idea not found"]}

    return {"ok": True, "data": {"idea": ideas[idea_id]}, "warnings": []}

async def novel_update_premise_idea(idea_id: str, title: str = None, logline: str = None) -> dict:
    state = await _get_novel_state()
    ideas = state.get("premise_ideas", {})

    if idea_id not in ideas:
        return {"ok": False, "warnings": ["Idea not found"]}

    if title:
        ideas[idea_id]["title"] = title
    if logline:
        ideas[idea_id]["logline"] = logline

    ideas[idea_id]["updated"] = datetime.now(timezone.utc).isoformat()

    novel_state = await _get_novel_state()
    novel_state["premise_ideas"] = ideas
    await cache.write("novel", novel_state)
    return {"ok": True, "data": {"updated": True}, "warnings": []}

async def novel_delete_premise_idea(idea_id: str) -> dict:
    state = await _get_novel_state()
    ideas = state.get("premise_ideas", {})

    if idea_id not in ideas:
        return {"ok": False, "warnings": ["Idea not found"]}

    del ideas[idea_id]
    novel_state = await _get_novel_state()
    novel_state["premise_ideas"] = ideas
    await cache.write("novel", novel_state)
    return {"ok": True, "data": {"deleted": True}, "warnings": []}

async def novel_promote_premise(idea_id: str, author: str, genre: str, slug: str) -> dict:
    state = await _get_novel_state()
    ideas = state.get("premise_ideas", {})

    if idea_id not in ideas:
        return {"ok": False, "warnings": ["Idea not found"]}

    idea = ideas[idea_id]

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
    await cache.write("novel", novel_state)

    return {"ok": True, "data": {"promoted": True, "work": idea["promoted_to"]}, "warnings": []}

def register(mcp: FastMCP) -> None:
    mcp.tool(tags={"domain:novel"})(novel_create_premise_idea)
    mcp.tool(tags={"domain:novel"})(novel_list_premise_ideas)
    mcp.tool(tags={"domain:novel"})(novel_get_premise_idea)
    mcp.tool(tags={"domain:novel"})(novel_update_premise_idea)
    mcp.tool(tags={"domain:novel"})(novel_delete_premise_idea)
    mcp.tool(tags={"domain:novel"})(novel_promote_premise)
