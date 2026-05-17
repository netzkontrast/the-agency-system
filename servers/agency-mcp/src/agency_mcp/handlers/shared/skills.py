from pathlib import Path
from typing import Any
import yaml


def shared_list_skills(domain: str | None = None) -> dict[str, Any]:
    skills_dir = Path("skills")
    target_domains = (
        [domain] if domain else ["music", "novel", "jules", "agentic", "shared"]
    )

    skills = []

    if skills_dir.exists():
        for dom in target_domains:
            dom_dir = skills_dir / dom
            if not dom_dir.exists():
                continue

            for skill_path in dom_dir.rglob("SKILL.md"):
                try:
                    content = skill_path.read_text(encoding="utf-8")
                    frontmatter = {}
                    if content.startswith("---"):
                        parts = content.split("---", 2)
                        if len(parts) >= 3:
                            yaml_content = parts[1]
                            frontmatter = yaml.safe_load(yaml_content) or {}

                    skills.append(
                        {
                            "name": frontmatter.get("slug", skill_path.parent.name),
                            "summary": frontmatter.get("summary", ""),
                            "path": str(skill_path),
                        }
                    )
                except Exception:
                    pass

    # Limit to 20 per overview §2.1.6
    limited_skills = skills[:20]
    next_cursor = "page_2" if len(skills) > 20 else None

    return {
        "ok": True,
        "data": limited_skills,
        "warnings": [],
        "artefacts_written": [],
        "next_cursor": next_cursor,
        "next_suggested_tools": [],
    }


def shared_get_skill(name: str) -> dict[str, Any]:
    skills_dir = Path("skills")
    if skills_dir.exists():
        for skill_path in skills_dir.rglob("SKILL.md"):
            if skill_path.parent.name == name:
                try:
                    content = skill_path.read_text(encoding="utf-8")
                    frontmatter = {}
                    body = content
                    if content.startswith("---"):
                        parts = content.split("---", 2)
                        if len(parts) >= 3:
                            yaml_content = parts[1]
                            frontmatter = yaml.safe_load(yaml_content) or {}
                            body = parts[2].strip()

                    return {
                        "ok": True,
                        "data": {
                            "frontmatter": frontmatter,
                            "body_preview": body[:1000]
                            + ("..." if len(body) > 1000 else ""),
                            "length": len(body),
                        },
                        "warnings": [],
                        "artefacts_written": [],
                        "next_suggested_tools": [],
                    }
                except Exception as e:
                    return {
                        "ok": False,
                        "data": {},
                        "warnings": [f"Error reading skill {name}: {str(e)}"],
                        "artefacts_written": [],
                        "next_suggested_tools": [],
                    }

    return {
        "ok": False,
        "data": {},
        "warnings": [f"Skill {name} not found"],
        "artefacts_written": [],
        "next_suggested_tools": [],
    }


def _render_cheatsheet(domain: str, skills: list, prologue: str) -> str:
    lines = [f"# /agency-system:{domain}-*"]
    if prologue:
        lines.append(prologue)
        lines.append("")

    lines.append("## Skills")
    for s in skills:
        lines.append(f"- **{s.get('name', 'Unknown')}**: {s.get('summary', '')}")

    # very rough token counting
    rough_tokens = sum(len(line.split()) for line in lines)
    if rough_tokens > 2000:
        # truncate
        lines = lines[:50]  # Arbitrary line truncation for safety
        lines.append("… (run shared_list_skills for full list)")

    return "\n".join(lines)


def plugin_help(domain: str) -> dict[str, Any]:
    valid_domains = {"music", "novel", "jules", "agentic", "shared"}
    if domain not in valid_domains:
        return {
            "ok": False,
            "data": "",
            "warnings": [f"unknown domain: {domain}"],
            "artefacts_written": [],
            "next_suggested_tools": [],
        }

    prologue = ""
    prologue_path = Path("reference") / domain / "README.md"
    if prologue_path.exists():
        try:
            prologue = prologue_path.read_text(encoding="utf-8")
        except Exception:
            pass

    skills_result = shared_list_skills(domain)
    skills = skills_result.get("data", [])

    markdown = _render_cheatsheet(domain, skills, prologue)

    return {
        "ok": True,
        "data": markdown,
        "warnings": [],
        "artefacts_written": [],
        "next_suggested_tools": [],
    }
