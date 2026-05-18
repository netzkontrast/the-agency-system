import os
import re
from pathlib import Path

from fastmcp import FastMCP
from agency_mcp.handlers.novel import _shared

try:
    from agency_mcp.config import PLUGIN_ROOT
except ImportError:
    PLUGIN_ROOT = Path(".").resolve()

# Mock these for tests

def _get_empty_state() -> dict:
    return {"authors": {}}

async def _get_work_details(author: str, work_slug: str) -> dict:
    state = await _shared.get_cache().snapshot()
    novel_state = state.get("novel", _get_empty_state())
    author_data = novel_state.get("authors", {}).get(author, {})
    return author_data.get("works", {}).get(work_slug)

# Valid states
VALID_STATUSES = ["draft", "in_progress", "review", "done", "archived"]

# Transition rules (current -> allowed next states)

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

async def novel_update_work_status(author: str, work_slug: str, status: str, dry_run: bool = False) -> dict:
    from agency_mcp.handlers.novel._shared import VALID_STATUSES, STATUS_TRANSITIONS

    if status not in VALID_STATUSES:
        return {"ok": False, "warnings": [f"Invalid status: {status}"]}

    work_data = await _get_work_details(author, work_slug)
    if not work_data:
        return {"ok": False, "warnings": [f"Work not found: {author}/{work_slug}"]}

    current_status = work_data.get("status", "draft")

    if status not in STATUS_TRANSITIONS["work"].get(current_status, set()):
        return {
            "ok": False,
            "code": "illegal_transition",
            "from": current_status,
            "to": status,
            "warnings": [f"Invalid transition from {current_status} to {status}"]
        }

    genre = work_data.get("genre")
    work_file = PLUGIN_ROOT / "novels" / author / "works" / genre / work_slug / "work.md"

    if dry_run:
        return {
            "ok": True,
            "data": {
                "would_apply": True,
                "diff": [f"Update {work_file} status from {current_status} to {status}"]
            },
            "warnings": []
        }

    if _update_frontmatter_status(work_file, status):
        # Trigger indexer refresh
        from agency_mcp.state.indexers.novel_indexer import NovelIndexer
        indexer = NovelIndexer(_shared.get_cache(), PLUGIN_ROOT / "novels")
        await indexer.rebuild()
        return {"ok": True, "data": {"updated": True, "status": status}, "warnings": []}

    return {"ok": False, "warnings": ["Failed to update work file"]}

def _get_current_status_from_file(file_path: Path) -> str:
    if not file_path.exists():
        return "draft"
    content = file_path.read_text(encoding="utf-8")
    import re
    match = re.search(r"^status:\s*(.+)$", content, flags=re.MULTILINE)
    if match:
        return match.group(1).strip()
    return "draft"

async def novel_update_chapter_status(author: str, work_slug: str, chapter_slug: str, status: str, dry_run: bool = False) -> dict:
    from agency_mcp.handlers.novel._shared import VALID_STATUSES, STATUS_TRANSITIONS

    if status not in VALID_STATUSES:
        return {"ok": False, "warnings": [f"Invalid status: {status}"]}

    work_data = await _get_work_details(author, work_slug)
    if not work_data:
        return {"ok": False, "warnings": [f"Work not found: {author}/{work_slug}"]}

    genre = work_data.get("genre")
    chap_file = PLUGIN_ROOT / "novels" / author / "works" / genre / work_slug / "chapters" / f"{chapter_slug}.md"

    if not chap_file.exists():
        return {"ok": False, "warnings": ["Chapter not found"]}

    current_status = _get_current_status_from_file(chap_file)

    if status not in STATUS_TRANSITIONS["chapter"].get(current_status, set()):
        return {
            "ok": False,
            "code": "illegal_transition",
            "from": current_status,
            "to": status,
            "warnings": [f"Invalid transition from {current_status} to {status}"]
        }

    if dry_run:
        return {
            "ok": True,
            "data": {
                "would_apply": True,
                "diff": [f"Update {chap_file} status from {current_status} to {status}"]
            },
            "warnings": []
        }

    if _update_frontmatter_status(chap_file, status):
        return {"ok": True, "data": {"updated": True, "status": status}, "warnings": []}

    return {"ok": False, "warnings": ["Failed to update chapter"]}

async def novel_update_scene_status(author: str, work_slug: str, scene_slug: str, status: str, dry_run: bool = False) -> dict:
    from agency_mcp.handlers.novel._shared import VALID_STATUSES, STATUS_TRANSITIONS

    if status not in VALID_STATUSES:
        return {"ok": False, "warnings": [f"Invalid status: {status}"]}

    work_data = await _get_work_details(author, work_slug)
    if not work_data:
        return {"ok": False, "warnings": [f"Work not found: {author}/{work_slug}"]}

    genre = work_data.get("genre")
    scene_file = PLUGIN_ROOT / "novels" / author / "works" / genre / work_slug / "scenes" / f"{scene_slug}.md"

    if not scene_file.exists():
        return {"ok": False, "warnings": ["Scene not found"]}

    current_status = _get_current_status_from_file(scene_file)

    if status not in STATUS_TRANSITIONS["scene"].get(current_status, set()):
        return {
            "ok": False,
            "code": "illegal_transition",
            "from": current_status,
            "to": status,
            "warnings": [f"Invalid transition from {current_status} to {status}"]
        }

    if dry_run:
        return {
            "ok": True,
            "data": {
                "would_apply": True,
                "diff": [f"Update {scene_file} status from {current_status} to {status}"]
            },
            "warnings": []
        }

    if _update_frontmatter_status(scene_file, status):
        return {"ok": True, "data": {"updated": True, "status": status}, "warnings": []}

    return {"ok": False, "warnings": ["Failed to update scene"]}

def register(mcp: FastMCP) -> None:
    mcp.tool(tags={"domain:novel"})(novel_update_work_status)
    mcp.tool(tags={"domain:novel"})(novel_update_chapter_status)
    mcp.tool(tags={"domain:novel"})(novel_update_scene_status)
