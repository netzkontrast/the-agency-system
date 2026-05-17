import os
import re
from pathlib import Path

from fastmcp import FastMCP
from agency_mcp.state.cache import StateCache

try:
    from agency_mcp.config import PLUGIN_ROOT
except ImportError:
    PLUGIN_ROOT = Path(".").resolve()

# Mock these for tests
def _get_cache():
    return StateCache()
cache = _get_cache()

def _get_empty_state() -> dict:
    return {"authors": {}}

async def _get_work_details(author: str, work_slug: str) -> dict:
    state = await cache.snapshot()
    novel_state = state.get("novel", _get_empty_state())
    author_data = novel_state.get("authors", {}).get(author, {})
    return author_data.get("works", {}).get(work_slug)

# Valid states
VALID_STATUSES = ["draft", "in_progress", "review", "done", "archived"]

# Transition rules (current -> allowed next states)
STATUS_TRANSITIONS = {
    "draft": ["in_progress", "archived"],
    "in_progress": ["review", "draft", "archived"],
    "review": ["done", "in_progress", "archived"],
    "done": ["archived", "review"],
    "archived": ["draft"]
}

def _update_frontmatter_status(file_path: Path, new_status: str) -> bool:
    if not file_path.exists():
        return False

    content = file_path.read_text(encoding="utf-8")
    if not content.startswith("---\n"):
        return False

    # Simple regex to replace status line in frontmatter
    new_content = re.sub(r"^status:.*$", f"status: {new_status}", content, flags=re.MULTILINE)

    if new_content == content and "status:" not in content.split("---\n", 2)[1]:
        # Need to inject status if missing
        parts = content.split("---\n", 2)
        parts[1] = parts[1] + f"status: {new_status}\n"
        new_content = "---\n" + parts[1] + "---\n" + parts[2]

    file_path.write_text(new_content, encoding="utf-8")
    return True

async def novel_update_work_status(author: str, work_slug: str, status: str) -> dict:
    if status not in VALID_STATUSES:
        return {"ok": False, "warnings": [f"Invalid status: {status}"]}

    work_data = await _get_work_details(author, work_slug)
    if not work_data:
        return {"ok": False, "warnings": [f"Work not found: {author}/{work_slug}"]}

    current_status = work_data.get("status", "draft")

    if status not in STATUS_TRANSITIONS.get(current_status, []):
        return {"ok": False, "warnings": [f"Invalid transition from {current_status} to {status}"]}

    genre = work_data.get("genre")
    work_file = PLUGIN_ROOT / "novels" / author / "works" / genre / work_slug / "work.md"

    if _update_frontmatter_status(work_file, status):
        # Trigger indexer refresh
        from agency_mcp.state.indexers.novel_indexer import NovelIndexer
        indexer = NovelIndexer(cache, PLUGIN_ROOT / "novels")
        await indexer.rebuild()
        return {"ok": True, "data": {"updated": True, "status": status}, "warnings": []}

    return {"ok": False, "warnings": ["Failed to update work file"]}

async def novel_update_chapter_status(author: str, work_slug: str, chapter_slug: str, status: str) -> dict:
    if status not in VALID_STATUSES:
        return {"ok": False, "warnings": [f"Invalid status: {status}"]}

    work_data = await _get_work_details(author, work_slug)
    if not work_data:
        return {"ok": False, "warnings": [f"Work not found: {author}/{work_slug}"]}

    genre = work_data.get("genre")
    chap_file = PLUGIN_ROOT / "novels" / author / "works" / genre / work_slug / "chapters" / f"{chapter_slug}.md"

    # We do not strictly validate transitions for sub-entities if they don't have tracked state in cache
    # But we update it in the file.
    if _update_frontmatter_status(chap_file, status):
        return {"ok": True, "data": {"updated": True, "status": status}, "warnings": []}

    return {"ok": False, "warnings": ["Chapter not found or failed to update"]}

async def novel_update_scene_status(author: str, work_slug: str, scene_slug: str, status: str) -> dict:
    if status not in VALID_STATUSES:
        return {"ok": False, "warnings": [f"Invalid status: {status}"]}

    work_data = await _get_work_details(author, work_slug)
    if not work_data:
        return {"ok": False, "warnings": [f"Work not found: {author}/{work_slug}"]}

    genre = work_data.get("genre")
    scene_file = PLUGIN_ROOT / "novels" / author / "works" / genre / work_slug / "scenes" / f"{scene_slug}.md"

    if _update_frontmatter_status(scene_file, status):
        return {"ok": True, "data": {"updated": True, "status": status}, "warnings": []}

    return {"ok": False, "warnings": ["Scene not found or failed to update"]}

def register(mcp: FastMCP) -> None:
    mcp.tool(tags={"domain:novel"})(novel_update_work_status)
    mcp.tool(tags={"domain:novel"})(novel_update_chapter_status)
    mcp.tool(tags={"domain:novel"})(novel_update_scene_status)
