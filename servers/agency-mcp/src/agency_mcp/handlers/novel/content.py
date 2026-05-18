import os
import shutil
from pathlib import Path
from datetime import datetime, timezone

from fastmcp import FastMCP
from .gates import _chapter_create_guard

from agency_mcp.state.cache import StateCache

try:
    from agency_mcp.config import PLUGIN_ROOT
except ImportError:
    PLUGIN_ROOT = Path(".").resolve()

# Mock these for tests
def _get_cache():
    return StateCache()
cache = _get_cache()

def _normalize_slug(name: str) -> str:
    """Normalize input to slug format."""
    if "/" in name or "\\" in name or "\0" in name:
        raise ValueError(f"Invalid name: contains path separator or null byte: {name!r}")
    slug = name.lower().replace(" ", "-").replace("_", "-")
    slug = "".join(c for c in slug if c.isalnum() or c == "-")
    return slug[:64]

def _substitute_placeholders(text: str, ctx: dict) -> str:
    for key, val in ctx.items():
        text = text.replace(f"{{{{{key}}}}}", str(val))
    return text

def _get_empty_state() -> dict:
    return {"authors": {}}

async def _get_work_details(author: str, work_slug: str) -> dict:
    state = await cache.snapshot()
    novel_state = state.get("novel", _get_empty_state())
    author_data = novel_state.get("authors", {}).get(author, {})
    return author_data.get("works", {}).get(work_slug)

async def novel_create_chapter(author: str, work_slug: str, chapter_number: int, title: str, dry_run: bool = False, force: bool = False) -> dict:
    guard = _chapter_create_guard(work_slug, force)
    if not guard["ok"]:
        return guard

    work_data = await _get_work_details(author, work_slug)
    if not work_data:
        return {"ok": False, "warnings": [f"Work not found: {author}/{work_slug}"]}

    genre = work_data.get("genre")
    norm_title = _normalize_slug(title)
    filename = f"ch{chapter_number:02d}-{norm_title}.md"

    work_dir = PLUGIN_ROOT / "novels" / author / "works" / genre / work_slug
    chap_file = work_dir / "chapters" / filename

    if chap_file.exists():
        return {"ok": True, "data": {"created": False}, "warnings": ["chapter already exists"]}

    if dry_run:
        return {"ok": True, "data": {"would_apply": True, "diff": [f"Create file {chap_file}"]}, "warnings": []}

    template = PLUGIN_ROOT / "templates" / "novel" / "chapter.md"
    content = ""
    if template.exists():
        content = template.read_text(encoding="utf-8")

    ctx = {
        "work_title": work_data.get("work_title", work_slug),
        "chapter_title": title,
        "chapter_number": chapter_number
    }

    content = _substitute_placeholders(content, ctx)
    chap_file.parent.mkdir(parents=True, exist_ok=True)
    chap_file.write_text(content, encoding="utf-8")

    return {"ok": True, "data": {"created": True, "path": str(chap_file)}, "warnings": []}

async def novel_create_scene(author: str, work_slug: str, chapter_number: int, scene_number: int, dry_run: bool = False) -> dict:
    work_data = await _get_work_details(author, work_slug)
    if not work_data:
        return {"ok": False, "warnings": [f"Work not found: {author}/{work_slug}"]}

    genre = work_data.get("genre")
    filename = f"ch{chapter_number:02d}-s{scene_number:02d}.md"

    work_dir = PLUGIN_ROOT / "novels" / author / "works" / genre / work_slug
    scene_file = work_dir / "scenes" / filename

    if scene_file.exists():
        return {"ok": True, "data": {"created": False}, "warnings": ["scene already exists"]}

    if dry_run:
        return {"ok": True, "data": {"would_apply": True, "diff": [f"Create file {scene_file}"]}, "warnings": []}

    template = PLUGIN_ROOT / "templates" / "novel" / "scene.md"
    content = ""
    if template.exists():
        content = template.read_text(encoding="utf-8")

    ctx = {
        "scene_number": scene_number,
        "chapter_number": chapter_number
    }

    content = _substitute_placeholders(content, ctx)
    scene_file.parent.mkdir(parents=True, exist_ok=True)
    scene_file.write_text(content, encoding="utf-8")

    return {"ok": True, "data": {"created": True, "path": str(scene_file)}, "warnings": []}

async def novel_get_chapter(author: str, work_slug: str, chapter_slug: str) -> dict:
    work_data = await _get_work_details(author, work_slug)
    if not work_data:
        return {"ok": False, "warnings": [f"Work not found: {author}/{work_slug}"]}
    genre = work_data.get("genre")
    chap_file = PLUGIN_ROOT / "novels" / author / "works" / genre / work_slug / "chapters" / f"{chapter_slug}.md"
    if not chap_file.exists():
        return {"ok": False, "warnings": ["Chapter not found"]}
    return {"ok": True, "data": {"content": chap_file.read_text(encoding="utf-8")}, "warnings": []}

async def novel_list_chapters(author: str, work_slug: str) -> dict:
    work_data = await _get_work_details(author, work_slug)
    if not work_data:
        return {"ok": False, "warnings": [f"Work not found: {author}/{work_slug}"]}
    genre = work_data.get("genre")
    chap_dir = PLUGIN_ROOT / "novels" / author / "works" / genre / work_slug / "chapters"
    chapters = [f.stem for f in chap_dir.glob("*.md")] if chap_dir.exists() else []
    return {"ok": True, "data": {"chapters": sorted(chapters)[:20]}, "warnings": []}

async def novel_get_scene(author: str, work_slug: str, scene_slug: str) -> dict:
    work_data = await _get_work_details(author, work_slug)
    if not work_data:
        return {"ok": False, "warnings": [f"Work not found: {author}/{work_slug}"]}
    genre = work_data.get("genre")
    scene_file = PLUGIN_ROOT / "novels" / author / "works" / genre / work_slug / "scenes" / f"{scene_slug}.md"
    if not scene_file.exists():
        return {"ok": False, "warnings": ["Scene not found"]}
    return {"ok": True, "data": {"content": scene_file.read_text(encoding="utf-8")}, "warnings": []}

async def novel_list_scenes(author: str, work_slug: str) -> dict:
    work_data = await _get_work_details(author, work_slug)
    if not work_data:
        return {"ok": False, "warnings": [f"Work not found: {author}/{work_slug}"]}
    genre = work_data.get("genre")
    scene_dir = PLUGIN_ROOT / "novels" / author / "works" / genre / work_slug / "scenes"
    scenes = [f.stem for f in scene_dir.glob("*.md")] if scene_dir.exists() else []
    return {"ok": True, "data": {"scenes": sorted(scenes)[:20]}, "warnings": []}

async def novel_rename_chapter(author: str, work_slug: str, old_slug: str, new_slug: str, dry_run: bool = False) -> dict:
    work_data = await _get_work_details(author, work_slug)
    if not work_data:
        return {"ok": False, "warnings": [f"Work not found: {author}/{work_slug}"]}
    genre = work_data.get("genre")
    chap_dir = PLUGIN_ROOT / "novels" / author / "works" / genre / work_slug / "chapters"
    old_file = chap_dir / f"{old_slug}.md"
    new_file = chap_dir / f"{new_slug}.md"

    if not old_file.exists():
        return {"ok": False, "warnings": ["Chapter not found"]}
    if new_file.exists():
        return {"ok": False, "warnings": ["Target chapter already exists"]}

    if dry_run:
        return {"ok": True, "data": {"would_apply": True, "diff": [f"Rename {old_file} -> {new_file}"]}, "warnings": []}

    shutil.move(str(old_file), str(new_file))
    return {"ok": True, "data": {"renamed": True}, "warnings": []}

def register(mcp: FastMCP) -> None:
    mcp.tool(tags={"domain:novel"})(novel_create_chapter)
    mcp.tool(tags={"domain:novel"})(novel_create_scene)
    mcp.tool(tags={"domain:novel"})(novel_get_chapter)
    mcp.tool(tags={"domain:novel"})(novel_list_chapters)
    mcp.tool(tags={"domain:novel"})(novel_get_scene)
    mcp.tool(tags={"domain:novel"})(novel_list_scenes)
    mcp.tool(tags={"domain:novel"})(novel_rename_chapter)
