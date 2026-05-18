import os
from pathlib import Path
from typing import Any

from fastmcp import FastMCP
from .gates import _resolve_work_dir, _read_frontmatter, _read_json

def novel_build_promo_pack(work_id: str, kinds: list[str] = None) -> dict:
    if kinds is None:
        kinds = ["blurb", "logline", "jacket_flap", "press_kit"]

    work_dir = _resolve_work_dir(work_id)
    if not work_dir:
        return {"ok": False, "warnings": ["Work not found"]}

    readme_path = work_dir / "README.md"
    cast_path = work_dir / "cast.md"
    ncp_path = work_dir / ".ncp.json"

    fm = _read_frontmatter(readme_path)
    theme = ""
    ncp = _read_json(ncp_path)
    theme = fm.get("theme", ncp.get("theme", ""))

    cast_text = ""
    if cast_path.exists():
        cast_text = cast_path.read_text(encoding="utf-8")

    data = {}

    ctx = {
        "logline": fm.get("logline", "A compelling story."),
        "theme": theme,
        "genre": fm.get("genre", "fiction"),
        "target_reader": fm.get("target_reader", "general audience"),
        "comp_titles": str(fm.get("comp_titles", "other great books")),
        "cast_preview": cast_text[:100] + "..." if len(cast_text) > 100 else cast_text
    }

    if "blurb" in kinds:
        data["blurb"] = f"**{ctx['logline']}**\n\nIn this {ctx['genre']} novel for {ctx['target_reader']}, we explore {ctx['theme']}. Fans of {ctx['comp_titles']} will love this."

    if "logline" in kinds:
        data["logline"] = f"{ctx['logline']}"

    if "jacket_flap" in kinds:
        data["jacket_flap"] = f"## Jacket Flap\n\n{ctx['logline']}\n\n{ctx['cast_preview']}\n\nAn unforgettable journey into {ctx['theme']}."

    if "press_kit" in kinds:
        data["press_kit"] = f"# Press Kit\n\n**Genre**: {ctx['genre']}\n**Target**: {ctx['target_reader']}\n**Comps**: {ctx['comp_titles']}\n\n## Logline\n{ctx['logline']}\n\n## Theme\n{ctx['theme']}"

    return {"ok": True, "data": data}

def novel_get_promo_content(work_id: str, kind: str) -> dict:
    res = novel_build_promo_pack(work_id, [kind])
    if not res["ok"]:
        return res
    if kind not in res["data"]:
        return {"ok": False, "warnings": [f"Kind '{kind}' not generated"]}
    return {"ok": True, "data": {"content": res["data"][kind]}}

def novel_update_promo_field(work_id: str, kind: str, field: str, value: str, dry_run: bool = False) -> dict:
    work_dir = _resolve_work_dir(work_id)
    if not work_dir:
        return {"ok": False, "warnings": ["Work not found"]}

    readme_path = work_dir / "README.md"
    if not readme_path.exists():
        return {"ok": False, "warnings": ["Missing README.md"]}

    if dry_run:
        return {
            "ok": True,
            "data": {
                "would_apply": True,
                "diff": [f"Update field '{field}' in {readme_path} to '{value}'"]
            },
            "warnings": []
        }

    try:
        with open(readme_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        new_lines = []
        in_fm = False
        updated = False
        if lines and lines[0].strip() == "---\n":
            new_lines.append(lines[0])
            in_fm = True
            for i in range(1, len(lines)):
                line = lines[i]
                if line.strip() == "---":
                    in_fm = False
                    if not updated:
                        new_lines.append(f'{field}: "{value}"\n')
                        updated = True
                    new_lines.append(line)
                    continue

                if in_fm and ":" in line:
                    k, v = line.split(":", 1)
                    if k.strip() == field:
                        new_lines.append(f'{field}: "{value}"\n')
                        updated = True
                        continue

                new_lines.append(line)

        with open(readme_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

        return {"ok": True, "data": {"updated": True, "field": field, "value": value}}
    except Exception as e:
        return {"ok": False, "warnings": [str(e)]}

def register(mcp: FastMCP) -> None:
    mcp.tool(tags={"domain:novel"})(novel_build_promo_pack)
    mcp.tool(tags={"domain:novel"})(novel_get_promo_content)
    mcp.tool(tags={"domain:novel"})(novel_update_promo_field)
