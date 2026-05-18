from pathlib import Path
from typing import Any

from agency_mcp.state.cache import StateCache
from agency_mcp.lib.codemode.projection import apply_view

_cache: StateCache | None = None


def _get_cache() -> StateCache:
    global _cache
    if _cache is None:
        _cache = StateCache()
    return _cache


def _walk_dict(data: dict, query: str, path_prefix: str, hits: list, namespace: str):
    query_lower = query.lower()
    for k, v in data.items():
        curr_path = f"{path_prefix}.{k}" if path_prefix else k
        if isinstance(v, str) and query_lower in v.lower():
            hits.append(
                {
                    "namespace": namespace,
                    "path": curr_path,
                    "summary": v[:100] + ("..." if len(v) > 100 else ""),
                }
            )
        elif isinstance(v, dict):
            _walk_dict(v, query, curr_path, hits, namespace)
        elif isinstance(v, list):
            for i, item in enumerate(v):
                if isinstance(item, str) and query_lower in item.lower():
                    hits.append(
                        {
                            "namespace": namespace,
                            "path": f"{curr_path}[{i}]",
                            "summary": item[:100] + ("..." if len(item) > 100 else ""),
                        }
                    )
                elif isinstance(item, dict):
                    _walk_dict(item, query, f"{curr_path}[{i}]", hits, namespace)


def _search_files(
    base_dir: Path,
    query: str,
    max_depth: int,
    current_depth: int,
    hits: list,
    namespace: str,
    ext: str,
):
    if not base_dir.exists() or current_depth > max_depth:
        return
    query_lower = query.lower()
    for item in base_dir.iterdir():
        if item.is_dir():
            _search_files(
                item, query, max_depth, current_depth + 1, hits, namespace, ext
            )
        elif item.is_file() and item.name.endswith(ext):
            try:
                content = item.read_text(encoding="utf-8")
                if query_lower in item.name.lower() or query_lower in content.lower():
                    hits.append(
                        {
                            "namespace": namespace,
                            "path": str(item.relative_to(Path.cwd())),
                            "summary": f"Found match in {item.name}",
                        }
                    )
            except Exception:
                pass


@apply_view
async def shared_search(
    query: str, namespaces: list[str] | None = None, full: bool = False
) -> dict[str, Any]:
    if not query:
        return {
            "ok": True,
            "data": [],
            "warnings": ["empty query"],
            "artefacts_written": [],
            "next_suggested_tools": [],
        }

    target_namespaces = namespaces or ["music", "novel", "jules", "agentic"]
    hits = []

    # 1. Search state.json via Cache
    cache = _get_cache()
    state = await cache.snapshot()
    for ns in target_namespaces:
        if ns in state:
            _walk_dict(state[ns], query, "", hits, ns)

    # 2. Walk reference/ for .md files
    ref_dir = Path("reference")
    if ref_dir.exists():
        _search_files(
            ref_dir,
            query,
            max_depth=4,
            current_depth=0,
            hits=hits,
            namespace="reference",
            ext=".md",
        )

    # 3. Walk skills/*/SKILL.md frontmatter
    skills_dir = Path("skills")
    if skills_dir.exists():
        _search_files(
            skills_dir,
            query,
            max_depth=4,
            current_depth=0,
            hits=hits,
            namespace="skills",
            ext="SKILL.md",
        )

    limit = 200 if full else 20
    limited_hits = hits[:limit]

    return {
        "ok": True,
        "data": limited_hits,
        "warnings": [],
        "artefacts_written": [],
        "next_suggested_tools": [],
    }
