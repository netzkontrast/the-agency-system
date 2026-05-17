import os
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

def _normalize_slug(name: str) -> str:
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

async def novel_create_character(author: str, work_slug: str, character_name: str, dry_run: bool = False) -> dict:
    work_data = await _get_work_details(author, work_slug)
    if not work_data:
        return {"ok": False, "warnings": [f"Work not found: {author}/{work_slug}"]}

    genre = work_data.get("genre")
    norm_name = _normalize_slug(character_name)
    filename = f"{norm_name}.md"

    work_dir = PLUGIN_ROOT / "novels" / author / "works" / genre / work_slug
    char_file = work_dir / "characters" / filename

    if char_file.exists():
        return {"ok": True, "data": {"created": False}, "warnings": ["character already exists"]}

    if dry_run:
        return {"ok": True, "data": {"would_apply": True, "diff": [f"Create file {char_file}"]}, "warnings": []}

    template = PLUGIN_ROOT / "templates" / "novel" / "character.md"
    content = ""
    if template.exists():
        content = template.read_text(encoding="utf-8")

    ctx = {
        "character_name": character_name
    }

    content = _substitute_placeholders(content, ctx)
    char_file.parent.mkdir(parents=True, exist_ok=True)
    char_file.write_text(content, encoding="utf-8")

    return {"ok": True, "data": {"created": True, "path": str(char_file)}, "warnings": []}

async def novel_get_character(author: str, work_slug: str, character_slug: str) -> dict:
    work_data = await _get_work_details(author, work_slug)
    if not work_data:
        return {"ok": False, "warnings": [f"Work not found: {author}/{work_slug}"]}
    genre = work_data.get("genre")
    char_file = PLUGIN_ROOT / "novels" / author / "works" / genre / work_slug / "characters" / f"{character_slug}.md"
    if not char_file.exists():
        return {"ok": False, "warnings": ["Character not found"]}
    return {"ok": True, "data": {"content": char_file.read_text(encoding="utf-8")}, "warnings": []}

async def novel_list_characters(author: str, work_slug: str) -> dict:
    work_data = await _get_work_details(author, work_slug)
    if not work_data:
        return {"ok": False, "warnings": [f"Work not found: {author}/{work_slug}"]}
    genre = work_data.get("genre")
    char_dir = PLUGIN_ROOT / "novels" / author / "works" / genre / work_slug / "characters"
    chars = [f.stem for f in char_dir.glob("*.md")] if char_dir.exists() else []
    return {"ok": True, "data": {"characters": sorted(chars)[:20]}, "warnings": []}

def register(mcp: FastMCP) -> None:
    mcp.tool(tags={"domain:novel"})(novel_create_character)
    mcp.tool(tags={"domain:novel"})(novel_get_character)
    mcp.tool(tags={"domain:novel"})(novel_list_characters)
