from pathlib import Path
from typing import Any


def _safe_resolve(base: Path, subpath: str) -> Path | None:
    try:
        resolved = (base / subpath).resolve()
        if not resolved.is_relative_to(base.resolve()):
            return None
        return resolved
    except Exception:
        return None


def shared_get_reference(path: str) -> dict[str, Any]:
    base_dir = Path("reference")
    resolved = _safe_resolve(base_dir, path)

    if not resolved or not resolved.exists() or not resolved.is_file():
        return {
            "ok": False,
            "data": "",
            "warnings": [f"Reference not found or invalid path: {path}"],
            "artefacts_written": [],
            "next_suggested_tools": [],
        }

    try:
        content = resolved.read_text(encoding="utf-8")
        if len(content) > 8192:  # Cap at 8KB
            content = content[:8192] + "\n...[Truncated, use read_ref for more]"

        return {
            "ok": True,
            "data": content,
            "warnings": [],
            "artefacts_written": [],
            "next_suggested_tools": [],
        }
    except Exception as e:
        return {
            "ok": False,
            "data": "",
            "warnings": [f"Error reading reference: {str(e)}"],
            "artefacts_written": [],
            "next_suggested_tools": [],
        }


def shared_load_override(name: str) -> dict[str, Any]:
    base_dir = Path("overrides")

    # Check .md and .yaml
    for ext in [".md", ".yaml"]:
        resolved = _safe_resolve(base_dir, f"{name}{ext}")
        if resolved and resolved.exists() and resolved.is_file():
            try:
                content = resolved.read_text(encoding="utf-8")
                return {
                    "ok": True,
                    "data": content,
                    "warnings": [],
                    "artefacts_written": [],
                    "next_suggested_tools": [],
                }
            except Exception as e:
                return {
                    "ok": False,
                    "data": "",
                    "warnings": [f"Error reading override: {str(e)}"],
                    "artefacts_written": [],
                    "next_suggested_tools": [],
                }

    return {
        "ok": False,
        "data": "",
        "warnings": [f"Override not found: {name}"],
        "artefacts_written": [],
        "next_suggested_tools": [],
    }
