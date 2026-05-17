import os
import shutil
from pathlib import Path
from datetime import datetime, timezone
import json

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
    """Normalize input to slug format, enforcing max 64 chars."""
    if "/" in name or "\\" in name or "\0" in name:
        raise ValueError(f"Invalid name: contains path separator or null byte: {name!r}")
    slug = name.lower().replace(" ", "-").replace("_", "-")
    if ".." in slug:
        raise ValueError(f"Invalid name: contains path traversal sequence: {name!r}")

    # Strip any non [a-z0-9-]
    slug = "".join(c for c in slug if c.isalnum() or c == "-")
    return slug[:64]

def _substitute_placeholders(text: str, ctx: dict) -> str:
    for key, val in ctx.items():
        text = text.replace(f"{{{{{key}}}}}", str(val))
    return text

def _get_empty_state() -> dict:
    return {"authors": {}}

async def novel_create_work(
    author: str,
    genre: str,
    slug: str,
    title: str = None,
    logline: str = None,
    dry_run: bool = False
) -> dict:
    """Scaffold a new novel work using templates."""
    try:
        norm_author = _normalize_slug(author)
        norm_genre = _normalize_slug(genre)
        norm_slug = _normalize_slug(slug)
    except ValueError as e:
        return {"ok": False, "warnings": [str(e)]}

    root_dir = PLUGIN_ROOT / "novels"
    work_dir = root_dir / norm_author / "works" / norm_genre / norm_slug

    if work_dir.exists():
        return {"ok": True, "data": {"created": False}, "warnings": ["work already exists"]}

    template_dir = PLUGIN_ROOT / "templates" / "novel"

    # Files and folders
    files_to_copy = [
        "work.md", "premise.md", "cast.md", "dramatica.md",
        "outline.md", "ncp.json", "README.md"
    ]
    subfolders = ["chapters", "scenes", "characters", "world", "revisions", "art", "research"]

    if dry_run:
        diff = []
        for f in files_to_copy:
            diff.append(f"Create file {work_dir / f}")
        for f in subfolders:
            diff.append(f"Create directory {work_dir / f}")

        return {
            "ok": True,
            "data": {
                "would_apply": True,
                "diff": diff
            },
            "warnings": []
        }

    # Real run
    work_dir.mkdir(parents=True, exist_ok=True)

    for folder in subfolders:
        (work_dir / folder).mkdir(exist_ok=True)

    ctx = {
        "author_slug": norm_author,
        "genre_slug": norm_genre,
        "work_slug": norm_slug,
        "work_title": title or norm_slug.replace("-", " ").title(),
        "premise_logline": logline or "(Add logline here)",
        "created": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }

    for f in files_to_copy:
        src = template_dir / f
        dest = work_dir / f
        if src.exists():
            content = src.read_text(encoding="utf-8")
            content = _substitute_placeholders(content, ctx)
            dest.write_text(content, encoding="utf-8")
        else:
            dest.write_text("", encoding="utf-8")

    # Trigger indexer refresh
    from agency_mcp.state.indexers.novel_indexer import NovelIndexer
    indexer = NovelIndexer(cache, root_dir)
    await indexer.rebuild()

    return {"ok": True, "data": {"created": True}, "warnings": []}

async def novel_find_novel(query: str) -> dict:
    """Find works matching a query across state."""
    state = await cache.snapshot()
    novel_state = state.get("novel", _get_empty_state())

    results = []
    query_lower = query.lower()
    for author_slug, author_data in novel_state.get("authors", {}).items():
        for work_slug, work_data in author_data.get("works", {}).items():
            title = work_data.get("work_title", "").lower()
            if query_lower in author_slug or query_lower in work_slug or query_lower in title:
                results.append({
                    "id": f"{author_slug}/{work_data.get('genre', 'unknown')}/{work_slug}",
                    "name": work_data.get("work_title", work_slug),
                    "summary": f"By {author_slug}. Status: {work_data.get('status')}"
                })
                if len(results) >= 20:
                    break
        if len(results) >= 20:
            break

    return {"ok": True, "data": {"results": results, "count": len(results)}, "warnings": []}

async def novel_list_novels(author: str = None) -> dict:
    """List all novels, optionally filtered by author."""
    state = await cache.snapshot()
    novel_state = state.get("novel", _get_empty_state())

    results = []
    authors = [author] if author else list(novel_state.get("authors", {}).keys())

    for author_slug in authors:
        author_data = novel_state.get("authors", {}).get(author_slug, {})
        for work_slug, work_data in author_data.get("works", {}).items():
            results.append({
                "id": f"{author_slug}/{work_data.get('genre', 'unknown')}/{work_slug}",
                "name": work_data.get("work_title", work_slug),
                "summary": f"By {author_slug}. Status: {work_data.get('status')}"
            })
            if len(results) >= 20:
                break
        if len(results) >= 20:
            break

    return {"ok": True, "data": {"results": results, "count": len(results)}, "warnings": []}

async def novel_get_work_full(author: str, slug: str, full: bool = False) -> dict:
    """Get full descriptor and counts for a work."""
    state = await cache.snapshot()
    novel_state = state.get("novel", _get_empty_state())

    author_data = novel_state.get("authors", {}).get(author, {})
    work_data = author_data.get("works", {}).get(slug)

    if not work_data:
        return {"ok": False, "warnings": ["Work not found"]}

    res = {"work": work_data}

    if full:
        # Resolve full lists if requested
        genre = work_data.get("genre")
        work_dir = PLUGIN_ROOT / "novels" / author / "works" / genre / slug

        if work_dir.exists():
            for folder in ["chapters", "scenes", "characters"]:
                f_dir = work_dir / folder
                if f_dir.exists() and f_dir.is_dir():
                    res[folder] = [f.name for f in f_dir.glob("*.md")]

    return {"ok": True, "data": res, "warnings": []}

async def novel_rename_work(author: str, old_slug: str, new_slug: str, dry_run: bool = False) -> dict:
    """Rename a work and update state."""
    state = await cache.snapshot()
    novel_state = state.get("novel", _get_empty_state())

    author_data = novel_state.get("authors", {}).get(author, {})
    work_data = author_data.get("works", {}).get(old_slug)

    if not work_data:
        return {"ok": False, "warnings": ["Work not found"]}

    genre = work_data.get("genre")
    old_dir = PLUGIN_ROOT / "novels" / author / "works" / genre / old_slug
    new_dir = PLUGIN_ROOT / "novels" / author / "works" / genre / new_slug

    if new_dir.exists():
        return {"ok": False, "warnings": ["Target work slug already exists"]}

    if dry_run:
        return {
            "ok": True,
            "data": {"would_apply": True, "diff": [f"Rename directory {old_dir} -> {new_dir}"]},
            "warnings": []
        }

    shutil.move(str(old_dir), str(new_dir))

    # Trigger indexer refresh
    from agency_mcp.state.indexers.novel_indexer import NovelIndexer
    indexer = NovelIndexer(cache, PLUGIN_ROOT / "novels")
    await indexer.rebuild()

    return {"ok": True, "data": {"renamed": True}, "warnings": []}

async def novel_rebuild_state() -> dict:
    """Rebuild the novel index manually."""
    from agency_mcp.state.indexers.novel_indexer import NovelIndexer
    indexer = NovelIndexer(cache, PLUGIN_ROOT / "novels")
    await indexer.rebuild()
    return {"ok": True, "data": {"rebuilt": True}, "warnings": []}

def register(mcp: FastMCP) -> None:
    mcp.tool(tags={"domain:novel"})(novel_create_work)
    mcp.tool(tags={"domain:novel"})(novel_find_novel)
    mcp.tool(tags={"domain:novel"})(novel_list_novels)
    mcp.tool(tags={"domain:novel"})(novel_get_work_full)
    mcp.tool(tags={"domain:novel"})(novel_rename_work)
    mcp.tool(tags={"domain:novel"})(novel_rebuild_state)
