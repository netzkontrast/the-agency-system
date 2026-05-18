"""L1 Harness — SKILL.md parsing + dispatch resolver.

Spec: Plan/harness/design.md §3.1
"""
import re
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

class SkillParseError(Exception):
    pass

def load_skill(path: Path | str) -> dict:
    """Parses a SKILL.md file and returns its frontmatter as a dict."""
    p = Path(path)
    if not p.exists():
        raise SkillParseError(f"Skill file not found: {p}")

    content = p.read_text()
    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        raise SkillParseError(f"No YAML frontmatter found in {p}")

    frontmatter_text = match.group(1)

    # Very basic YAML parsing for frontmatter
    data = {}
    for line in frontmatter_text.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            parts = line.split(":", 1)
            key = parts[0].strip()
            value = parts[1].strip()
            # remove quotes
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                value = value[1:-1]

            # handle lists minimally if needed, but for validation simple dict might be enough
            # For now we just return string values, we could use PyYAML but hooks avoid it.
            data[key] = value

    return data

def list_skills() -> list[Path]:
    """Returns all SKILL.md files in the repository skills/ directory."""
    skills_dir = REPO_ROOT / "skills"
    if not skills_dir.exists():
        return []

    return list(skills_dir.rglob("SKILL.md"))

def dispatch_skill(name: str) -> Path | None:
    """
    Returns the path the agency-system resolver would produce for /agency-system:<name>
    e.g. translates lyric-writer -> skills/music/lyric-writer/SKILL.md
    """
    for skill_path in list_skills():
        try:
            data = load_skill(skill_path)
            # The name in the skill typically includes the domain prefix, or we just match the directory
            # For exact match, match the end of the `name:` frontmatter, or the directory name.
            if data.get("name", "").endswith(name) or skill_path.parent.name == name:
                return skill_path
        except SkillParseError:
            continue

    return None
