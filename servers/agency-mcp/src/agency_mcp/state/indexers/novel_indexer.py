import asyncio
from pathlib import Path
from datetime import datetime, timezone
import yaml

from agency_mcp.state.cache import StateCache

class NovelIndexer:
    def __init__(self, cache: StateCache, root_dir: Path):
        self.cache = cache
        self.root_dir = root_dir

    def _parse_frontmatter(self, file_path: Path) -> dict:
        content = file_path.read_text(encoding="utf-8")
        if not content.startswith("---\n"):
            return {}

        try:
            _, frontmatter, _ = content.split("---\n", 2)
            # Use yaml for frontmatter parsing
            data = yaml.safe_load(frontmatter)
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    async def rebuild(self) -> None:
        """Walk novels/*/works/*/*/work.md and populate state.json."""
        authors_state = {}

        # Look for novels directory
        if not self.root_dir.exists() or not self.root_dir.is_dir():
            return

        for author_dir in self.root_dir.iterdir():
            if not author_dir.is_dir():
                continue

            author_slug = author_dir.name
            works_dir = author_dir / "works"
            if not works_dir.exists() or not works_dir.is_dir():
                continue

            author_data = {"works": {}}
            authors_state[author_slug] = author_data

            for genre_dir in works_dir.iterdir():
                if not genre_dir.is_dir():
                    continue

                for work_dir in genre_dir.iterdir():
                    if not work_dir.is_dir():
                        continue

                    work_slug = work_dir.name
                    work_file = work_dir / "work.md"

                    if not work_file.exists():
                        continue

                    frontmatter = self._parse_frontmatter(work_file)

                    # Count chapters
                    chapter_count = 0
                    chapters_dir = work_dir / "chapters"
                    if chapters_dir.exists() and chapters_dir.is_dir():
                        chapter_count = sum(1 for _ in chapters_dir.glob("*.md"))

                    # Count scenes
                    scene_count = 0
                    scenes_dir = work_dir / "scenes"
                    if scenes_dir.exists() and scenes_dir.is_dir():
                        scene_count = sum(1 for _ in scenes_dir.glob("*.md"))

                    # Populate state with work info
                    author_data["works"][work_slug] = {
                        "genre": frontmatter.get("genre_slug", genre_dir.name),
                        "created": frontmatter.get("created", ""),
                        "status": frontmatter.get("status", "draft"),
                        "chapter_count": chapter_count,
                        "scene_count": scene_count
                    }

                    if "work_title" in frontmatter:
                        author_data["works"][work_slug]["work_title"] = frontmatter["work_title"]

        # Use cache.write for namespace isolation to only update novel domain
        state = await self.cache.snapshot()
        novel_state = state.get("novel", {})
        novel_state["authors"] = authors_state
        novel_state["_indexed_at"] = datetime.now(timezone.utc).isoformat()
        await self.cache.write("novel", novel_state)
